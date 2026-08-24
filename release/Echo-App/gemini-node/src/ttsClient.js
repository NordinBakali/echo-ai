const ELEVENLABS_API_BASE = "https://api.elevenlabs.io/v1";
const DEFAULT_MODEL_ID = (process.env.ELEVENLABS_MODEL_ID || "eleven_multilingual_v2").trim();
const VOICE_CACHE_MS = 5 * 60 * 1000;

let voiceCache = {
  loadedAt: 0,
  voices: [],
};

function readElevenLabsApiKey() {
  const apiKey = String(process.env.ELEVENLABS_API_KEY || "").trim();
  if (!apiKey) {
    throw new Error("Missing ELEVENLABS_API_KEY in gemini-node/.env");
  }
  return apiKey;
}

function normalizeVoice(voice) {
  return {
    id: String(voice?.voice_id || "").trim(),
    name: String(voice?.name || "").trim(),
    labels: voice?.labels || {},
    previewUrl: String(voice?.preview_url || "").trim(),
    category: String(voice?.category || "").trim(),
    description: String(voice?.description || "").trim(),
  };
}

function voiceScoreForJarvis(voice) {
  const labelText = `${voice.name} ${voice.category} ${voice.description} ${JSON.stringify(voice.labels || {})}`.toLowerCase();
  let score = 0;

  if (/male|man/.test(labelText)) score += 30;
  if (/british|uk|england/.test(labelText)) score += 26;
  if (/narration|conversational|calm|professional|confident|assistant/.test(labelText)) score += 20;
  if (/deep|clear|smooth|warm/.test(labelText)) score += 14;
  if (/adam|antoni|josh|sam|george|daniel|callum/.test(labelText)) score += 8;
  if (/child|cartoon|anime|character/.test(labelText)) score -= 24;

  return score;
}

async function fetchVoicesFromApi() {
  const apiKey = readElevenLabsApiKey();
  const response = await fetch(`${ELEVENLABS_API_BASE}/voices`, {
    method: "GET",
    headers: {
      "xi-api-key": apiKey,
      Accept: "application/json",
    },
  });

  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const message = data?.detail?.message || data?.detail || response.statusText || "Unknown ElevenLabs error";
    throw new Error(`ElevenLabs voices request failed (${response.status}): ${message}`);
  }

  const voices = Array.isArray(data?.voices)
    ? data.voices.map(normalizeVoice).filter((voice) => Boolean(voice.id))
    : [];

  voiceCache = {
    loadedAt: Date.now(),
    voices,
  };

  return voices;
}

async function listPremiumVoices() {
  const isCacheFresh = Date.now() - voiceCache.loadedAt < VOICE_CACHE_MS;
  if (isCacheFresh && voiceCache.voices.length) {
    return voiceCache.voices;
  }

  return fetchVoicesFromApi();
}

async function resolveVoiceId(requestedVoiceId) {
  const requested = String(requestedVoiceId || "").trim();
  if (requested) {
    return requested;
  }

  const envVoiceId = String(process.env.ELEVENLABS_DEFAULT_VOICE_ID || "").trim();
  if (envVoiceId) {
    return envVoiceId;
  }

  const voices = await listPremiumVoices();
  if (!voices.length) {
    throw new Error("No ElevenLabs voices available for synthesis.");
  }

  const ranked = [...voices].sort((a, b) => voiceScoreForJarvis(b) - voiceScoreForJarvis(a));
  return ranked[0].id;
}

async function synthesizePremiumSpeech({ text, voiceId }) {
  const prompt = String(text || "").trim();
  if (!prompt) {
    throw new Error("text is required for TTS");
  }

  const apiKey = readElevenLabsApiKey();
  const resolvedVoiceId = await resolveVoiceId(voiceId);

  const stability = Number(process.env.ELEVENLABS_STABILITY || 0.34);
  const similarityBoost = Number(process.env.ELEVENLABS_SIMILARITY_BOOST || 0.82);
  const style = Number(process.env.ELEVENLABS_STYLE || 0.28);

  const body = {
    text: prompt,
    model_id: DEFAULT_MODEL_ID,
    voice_settings: {
      stability: Number.isFinite(stability) ? stability : 0.34,
      similarity_boost: Number.isFinite(similarityBoost) ? similarityBoost : 0.82,
      style: Number.isFinite(style) ? style : 0.28,
      use_speaker_boost: true,
    },
  };

  const response = await fetch(
    `${ELEVENLABS_API_BASE}/text-to-speech/${encodeURIComponent(resolvedVoiceId)}/stream?output_format=mp3_44100_128`,
    {
      method: "POST",
      headers: {
        "xi-api-key": apiKey,
        "Content-Type": "application/json",
        Accept: "audio/mpeg",
      },
      body: JSON.stringify(body),
    }
  );

  if (!response.ok) {
    const errorText = await response.text().catch(() => "");
    throw new Error(`ElevenLabs TTS failed (${response.status}): ${errorText || response.statusText}`);
  }

  const audioBuffer = Buffer.from(await response.arrayBuffer());
  if (!audioBuffer.length) {
    throw new Error("ElevenLabs returned empty audio output.");
  }

  return {
    audioBuffer,
    resolvedVoiceId,
  };
}

module.exports = {
  listPremiumVoices,
  synthesizePremiumSpeech,
};
