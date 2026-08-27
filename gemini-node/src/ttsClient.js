const ELEVENLABS_API_BASE = "https://api.elevenlabs.io/v1";
const DEFAULT_MODEL_ID = (process.env.ELEVENLABS_MODEL_ID || "eleven_multilingual_v2").trim();
const VOICE_CACHE_MS = 5 * 60 * 1000;

let voiceCache = {
  loadedAt: 0,
  voices: [],
};

const VOICE_PROFILE_KEYS = new Set(["status", "confirmation", "warning"]);

const PROFILE_VOICE_ENV_KEYS = {
  status: "ELEVENLABS_STATUS_VOICE_ID",
  confirmation: "ELEVENLABS_CONFIRMATION_VOICE_ID",
  warning: "ELEVENLABS_WARNING_VOICE_ID",
};

const PROFILE_VOICE_SETTINGS = {
  status: {
    stability: 0.44,
    similarityBoost: 0.84,
    style: 0.24,
    useSpeakerBoost: true,
  },
  confirmation: {
    stability: 0.6,
    similarityBoost: 0.88,
    style: 0.14,
    useSpeakerBoost: true,
  },
  warning: {
    stability: 0.3,
    similarityBoost: 0.82,
    style: 0.4,
    useSpeakerBoost: true,
  },
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

function normalizeVoiceProfile(profile) {
  const key = String(profile || "").trim().toLowerCase();
  if (VOICE_PROFILE_KEYS.has(key)) {
    return key;
  }
  return "status";
}

function voiceScoreForProfile(voice, profile = "status") {
  const normalizedProfile = normalizeVoiceProfile(profile);
  const labelText = `${voice.name} ${voice.category} ${voice.description} ${JSON.stringify(voice.labels || {})}`.toLowerCase();
  let score = 0;

  if (/male|man/.test(labelText)) score += 30;
  if (/british|uk|england/.test(labelText)) score += 26;
  if (/narration|conversational|calm|professional|confident|assistant/.test(labelText)) score += 20;
  if (/deep|clear|smooth|warm/.test(labelText)) score += 14;
  if (/adam|antoni|josh|sam|george|daniel|callum/.test(labelText)) score += 8;
  if (/child|cartoon|anime|character/.test(labelText)) score -= 24;

  if (normalizedProfile === "status") {
    if (/calm|neutral|assistant|professional|conversational|narration/.test(labelText)) score += 20;
    if (/dramatic|shout|angry/.test(labelText)) score -= 16;
  }

  if (normalizedProfile === "confirmation") {
    if (/clear|confident|professional|guide|assistant/.test(labelText)) score += 24;
    if (/aggressive|rough/.test(labelText)) score -= 12;
  }

  if (normalizedProfile === "warning") {
    if (/deep|authority|serious|command|broadcast/.test(labelText)) score += 28;
    if (/soft|cute|child|anime/.test(labelText)) score -= 28;
  }

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

function resolveProfileEnvVoiceId(profile) {
  const key = PROFILE_VOICE_ENV_KEYS[normalizeVoiceProfile(profile)];
  if (!key) {
    return "";
  }
  return String(process.env[key] || "").trim();
}

async function resolveVoiceId(requestedVoiceId, profile = "status") {
  const requested = String(requestedVoiceId || "").trim();
  if (requested) {
    return requested;
  }

  const profileVoiceId = resolveProfileEnvVoiceId(profile);
  if (profileVoiceId) {
    return profileVoiceId;
  }

  const envVoiceId = String(process.env.ELEVENLABS_DEFAULT_VOICE_ID || "").trim();
  if (envVoiceId) {
    return envVoiceId;
  }

  const voices = await listPremiumVoices();
  if (!voices.length) {
    throw new Error("No ElevenLabs voices available for synthesis.");
  }

  const ranked = [...voices].sort((a, b) => voiceScoreForProfile(b, profile) - voiceScoreForProfile(a, profile));
  return ranked[0].id;
}

function parseBoundedSetting(value, fallback, min, max) {
  const numeric = Number(value);
  if (!Number.isFinite(numeric)) {
    return fallback;
  }
  return Math.max(min, Math.min(max, numeric));
}

function resolveProfileVoiceSettings(profile) {
  const normalizedProfile = normalizeVoiceProfile(profile);
  const defaults = PROFILE_VOICE_SETTINGS[normalizedProfile] || PROFILE_VOICE_SETTINGS.status;
  const envPrefix = normalizedProfile.toUpperCase();

  const stability = parseBoundedSetting(
    process.env[`ELEVENLABS_${envPrefix}_STABILITY`] ?? process.env.ELEVENLABS_STABILITY,
    defaults.stability,
    0,
    1
  );
  const similarityBoost = parseBoundedSetting(
    process.env[`ELEVENLABS_${envPrefix}_SIMILARITY_BOOST`] ?? process.env.ELEVENLABS_SIMILARITY_BOOST,
    defaults.similarityBoost,
    0,
    1
  );
  const style = parseBoundedSetting(
    process.env[`ELEVENLABS_${envPrefix}_STYLE`] ?? process.env.ELEVENLABS_STYLE,
    defaults.style,
    0,
    1
  );

  return {
    stability,
    similarity_boost: similarityBoost,
    style,
    use_speaker_boost: defaults.useSpeakerBoost !== false,
  };
}

async function synthesizePremiumSpeech({ text, voiceId, profile }) {
  const prompt = String(text || "").trim();
  if (!prompt) {
    throw new Error("text is required for TTS");
  }

  const apiKey = readElevenLabsApiKey();
  const resolvedProfile = normalizeVoiceProfile(profile);
  const resolvedVoiceId = await resolveVoiceId(voiceId, resolvedProfile);
  const voiceSettings = resolveProfileVoiceSettings(resolvedProfile);

  const body = {
    text: prompt,
    model_id: DEFAULT_MODEL_ID,
    voice_settings: voiceSettings,
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
    resolvedProfile,
  };
}

module.exports = {
  listPremiumVoices,
  synthesizePremiumSpeech,
};
