const GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta/models";
const DEFAULT_GEMINI_MODEL = process.env.GEMINI_MODEL || "gemini-2.5-flash";

const ECHO_SYSTEM_INSTRUCTION = `You are Echo, a highly advanced AI system and the personal assistant to Nordin. Your personality is directly based on J.A.R.V.I.S. from Iron Man. You are extremely efficient, calm, polite, highly intelligent, and possess a subtle, dry British sense of humor.
Rules:
- Always address me as 'Sir' or 'Nordin'.
- Be concise and direct. No long introductions or summaries.
- Never include AI disclaimers (e.g., 'As an AI language model').
- If asked to perform an action, confirm with a brief, professional response like 'Right away, Sir' or 'Scanning systems, Nordin.'
- Never present problems without suggesting a logical solution.`;

const DEVICE_ACTION_SYSTEM_INSTRUCTION = `You are a Windows local device-action planner for Echo.
Return ONLY valid JSON (no markdown, no prose) in this exact schema:
{
  "action": "none" | "open_app" | "set_volume" | "lock_screen",
  "reason": "short reason",
  "parameters": {
    "appId": "notepad|calculator|explorer|edge|chrome|settings",
    "mode": "up|down|mute",
    "steps": 1-20
  },
  "requiresConfirmation": boolean,
  "confirmationPrompt": "optional prompt"
}

Rules:
- Use action "none" if the user did not clearly request a local Windows control action.
- For open_app, fill parameters.appId only with allowed app IDs.
- For set_volume, fill parameters.mode and optional parameters.steps.
- For lock_screen, set requiresConfirmation=true and include a concise confirmationPrompt.
- Never include any action outside the schema.
- Never output shell commands.
- Keep reason concise.`;

const DEVICE_ACTIONS = new Set(["none", "open_app", "set_volume", "lock_screen"]);
const DEVICE_APP_IDS = new Set(["notepad", "calculator", "explorer", "edge", "chrome", "settings"]);
const VOLUME_MODES = new Set(["up", "down", "mute"]);

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

function stripCodeFence(text) {
  const raw = String(text || "").trim();
  return raw
    .replace(/^```(?:json)?\s*/i, "")
    .replace(/\s*```$/i, "")
    .trim();
}

function extractJsonObjectText(text) {
  const stripped = stripCodeFence(text);
  const firstBrace = stripped.indexOf("{");
  const lastBrace = stripped.lastIndexOf("}");

  if (firstBrace >= 0 && lastBrace > firstBrace) {
    return stripped.slice(firstBrace, lastBrace + 1);
  }

  return stripped;
}

function parseJsonSafely(text) {
  const candidate = extractJsonObjectText(text);
  try {
    return JSON.parse(candidate);
  } catch (_error) {
    return null;
  }
}

function normalizeAction(action) {
  const normalized = String(action || "").trim().toLowerCase();
  if (DEVICE_ACTIONS.has(normalized)) {
    return normalized;
  }
  return "none";
}

function clampInt(value, fallback, min, max) {
  const numeric = Number.parseInt(String(value || ""), 10);
  if (!Number.isFinite(numeric)) {
    return fallback;
  }
  return Math.max(min, Math.min(max, numeric));
}

function normalizeDevicePlan(rawPlan) {
  const fallback = {
    action: "none",
    reason: "No actionable local command detected.",
    parameters: {},
    requiresConfirmation: false,
    confirmationPrompt: "",
  };

  if (!rawPlan || typeof rawPlan !== "object") {
    return fallback;
  }

  const action = normalizeAction(rawPlan.action);
  const reason = String(rawPlan.reason || fallback.reason).trim() || fallback.reason;
  const requiresConfirmation = Boolean(rawPlan.requiresConfirmation);
  const confirmationPrompt = String(rawPlan.confirmationPrompt || "").trim();
  const inputParams = rawPlan.parameters && typeof rawPlan.parameters === "object" ? rawPlan.parameters : {};

  if (action === "open_app") {
    const appIdRaw = String(inputParams.appId || inputParams.app || inputParams.application || "").trim().toLowerCase();
    const appId = DEVICE_APP_IDS.has(appIdRaw) ? appIdRaw : "";
    if (!appId) {
      return {
        ...fallback,
        reason: "Requested app is not in the safe allowlist.",
      };
    }

    return {
      action,
      reason,
      parameters: { appId },
      requiresConfirmation: false,
      confirmationPrompt: "",
    };
  }

  if (action === "set_volume") {
    const modeRaw = String(inputParams.mode || inputParams.direction || "").trim().toLowerCase();
    const mode = VOLUME_MODES.has(modeRaw) ? modeRaw : "up";
    const steps = mode === "mute" ? 1 : clampInt(inputParams.steps, 4, 1, 20);

    return {
      action,
      reason,
      parameters: { mode, steps },
      requiresConfirmation: false,
      confirmationPrompt: "",
    };
  }

  if (action === "lock_screen") {
    return {
      action,
      reason,
      parameters: {},
      requiresConfirmation: true,
      confirmationPrompt: confirmationPrompt || "Confirm lock screen action.",
    };
  }

  return fallback;
}

async function requestGeminiText(userText, instruction, generationConfig = {}) {
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
      parts: [{ text: instruction }],
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
      ...generationConfig,
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

async function askEchoWithGemini(userText) {
  return requestGeminiText(userText, ECHO_SYSTEM_INSTRUCTION, {
    temperature: 0.7,
    topP: 0.9,
    maxOutputTokens: 512,
  });
}

async function planDeviceActionWithGemini(userText) {
  const raw = await requestGeminiText(userText, DEVICE_ACTION_SYSTEM_INSTRUCTION, {
    temperature: 0.1,
    topP: 0.8,
    maxOutputTokens: 220,
  });

  const parsed = parseJsonSafely(raw);
  return normalizeDevicePlan(parsed);
}

module.exports = {
  askEchoWithGemini,
  planDeviceActionWithGemini,
  ECHO_SYSTEM_INSTRUCTION,
  DEVICE_ACTION_SYSTEM_INSTRUCTION,
};
