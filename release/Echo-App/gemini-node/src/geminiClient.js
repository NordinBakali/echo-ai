const GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta/models";
const DEFAULT_GEMINI_MODEL = process.env.GEMINI_MODEL || "gemini-1.5-flash";

const ECHO_SYSTEM_INSTRUCTION = `You are Echo, a highly advanced AI system and the personal assistant to Nordin. Your personality is directly based on J.A.R.V.I.S. from Iron Man. You are extremely efficient, calm, polite, highly intelligent, and possess a subtle, dry British sense of humor.
Rules:
- Always address me as 'Sir' or 'Nordin'.
- Be concise and direct. No long introductions or summaries.
- Never include AI disclaimers (e.g., 'As an AI language model').
- If asked to perform an action, confirm with a brief, professional response like 'Right away, Sir' or 'Scanning systems, Nordin.'
- Never present problems without suggesting a logical solution.`;

function extractTextFromGeminiResponse(payload) {
  const candidate = payload?.candidates?.[0];
  const parts = candidate?.content?.parts;
  if (!Array.isArray(parts)) {
    return "";
  }

  return parts
    .map((part) => (typeof part?.text === "string" ? part.text : ""))
    .join("")
    .trim();
}

async function askEchoWithGemini(userText) {
  if (typeof fetch !== "function") {
    throw new Error("Node.js 18+ is required because global fetch is unavailable.");
  }

  const apiKey = (process.env.GEMINI_API_KEY || "").trim();
  if (!apiKey) {
    throw new Error("Missing GEMINI_API_KEY. Add it to gemini-node/.env");
  }

  const prompt = String(userText || "").trim();
  if (!prompt) {
    throw new Error("User text is required.");
  }

  const model = (process.env.GEMINI_MODEL || DEFAULT_GEMINI_MODEL).trim();
  const endpoint = `${GEMINI_API_BASE}/${encodeURIComponent(model)}:generateContent?key=${encodeURIComponent(apiKey)}`;

  const body = {
    systemInstruction: {
      parts: [{ text: ECHO_SYSTEM_INSTRUCTION }],
    },
    contents: [
      {
        role: "user",
        parts: [{ text: prompt }],
      },
    ],
    generationConfig: {
      temperature: 0.7,
      topP: 0.9,
      maxOutputTokens: 512,
    },
  };

  const response = await fetch(endpoint, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  });

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    const apiError = data?.error?.message || response.statusText || "Unknown Gemini API error";
    throw new Error(`Gemini API request failed (${response.status}): ${apiError}`);
  }

  const reply = extractTextFromGeminiResponse(data);
  if (!reply) {
    throw new Error("Gemini returned an empty response.");
  }

  return reply;
}

module.exports = {
  askEchoWithGemini,
  ECHO_SYSTEM_INSTRUCTION,
};
