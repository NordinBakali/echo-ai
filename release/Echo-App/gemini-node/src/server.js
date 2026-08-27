const cors = require("cors");
const dotenv = require("dotenv");
const express = require("express");

dotenv.config();

const { askEchoWithGemini, planDeviceActionWithGemini } = require("./geminiClient");
const { executeDeviceAction, getDeviceControlCapabilities } = require("./deviceControl");
const { listPremiumVoices, synthesizePremiumSpeech } = require("./ttsClient");

const app = express();
const port = Number(process.env.PORT || 8787);

function normalizeLanguage(input) {
  const raw = String(input || "").trim().toLowerCase();
  if (!raw) {
    return "nl-NL";
  }

  if (raw.includes("nederlands") || raw.includes("dutch") || raw.startsWith("nl")) {
    return "nl-NL";
  }

  if (raw.startsWith("en") || raw.includes("english")) {
    return "en-US";
  }

  return raw;
}

function textForLanguage(language, english, dutch) {
  const normalized = normalizeLanguage(language);
  return normalized.startsWith("nl") ? String(dutch || "") : String(english || "");
}

function parseAllowedOrigins() {
  const raw = (process.env.CORS_ORIGIN || "").trim();
  if (!raw) {
    return ["http://127.0.0.1:5000", "http://localhost:5000"];
  }

  return raw
    .split(",")
    .map((origin) => origin.trim())
    .filter(Boolean);
}

const allowedOrigins = parseAllowedOrigins();

app.use(
  cors({
    origin(origin, callback) {
      if (!origin) {
        callback(null, true);
        return;
      }

      if (allowedOrigins.includes(origin)) {
        callback(null, true);
        return;
      }

      callback(new Error("Origin not allowed by CORS."));
    },
  })
);

app.use(express.json({ limit: "1mb" }));

app.get("/health", (_req, res) => {
  res.json({ status: "ok", service: "echo-gemini-bridge" });
});

app.get("/api/device/capabilities", (_req, res) => {
  res.json({
    status: "ok",
    ...getDeviceControlCapabilities(),
  });
});

app.post("/api/device/execute", async (req, res) => {
  const text = String(req.body?.text || "").trim();
  const confirm = Boolean(req.body?.confirm);
  const dryRun = Boolean(req.body?.dryRun);
  const language = normalizeLanguage(req.body?.language);

  if (!text) {
    res.status(400).json({ error: textForLanguage(language, "text is required", "tekst is verplicht") });
    return;
  }

  if (text.length > 4000) {
    res.status(400).json({
      error: textForLanguage(language, "text is too long (max 4000 chars)", "tekst is te lang (max 4000 tekens)"),
    });
    return;
  }

  try {
    const plan = await planDeviceActionWithGemini(text);

    if (plan.action === "none") {
      res.json({
        handled: false,
        status: "ignored",
        plan,
        message: textForLanguage(language, "No local computer action needed.", "Geen lokale computeractie nodig."),
      });
      return;
    }

    const confirmationFromText = /\b(confirm|confirmed|bevestig|bevestigd)\b/i.test(text);
    const needsConfirmation = Boolean(plan.requiresConfirmation) && !confirm && !confirmationFromText;

    if (needsConfirmation) {
      const confirmationMessage = textForLanguage(
        language,
        "Confirmation required for this system action.",
        "Veiligheidscontrole: bevestig deze systeemactie."
      );
      res.json({
        handled: true,
        status: "confirmation_required",
        requiresConfirmation: true,
        plan,
        message: `${confirmationMessage} ${textForLanguage(
          language,
          'Repeat the command with "confirm" to continue.',
          'Herhaal de opdracht met "bevestig" om door te gaan.'
        )}`,
      });
      return;
    }

    if (dryRun) {
      res.json({
        handled: true,
        status: "planned",
        dryRun: true,
        plan,
        message: textForLanguage(language, `Planned action: ${plan.action}`, `Geplande actie: ${plan.action}`),
      });
      return;
    }

    const result = await executeDeviceAction(plan, { language });

    res.json({
      handled: true,
      status: "success",
      plan,
      result,
      message: result.message,
    });
  } catch (error) {
    res.status(500).json({
      handled: true,
      status: "error",
      error: "Device action failed",
      message: error instanceof Error ? error.message : "Unknown device action error",
    });
  }
});

app.post("/api/echo", async (req, res) => {
  const text = String(req.body?.text || "").trim();

  if (!text) {
    res.status(400).json({ error: "text is required" });
    return;
  }

  if (text.length > 4000) {
    res.status(400).json({ error: "text is too long (max 4000 chars)" });
    return;
  }

  try {
    const reply = await askEchoWithGemini(text);
    res.json({ reply });
  } catch (error) {
    res.status(500).json({
      error: "Gemini request failed",
      message: error instanceof Error ? error.message : "Unknown error",
    });
  }
});

app.get("/api/tts/voices", async (_req, res) => {
  try {
    const voices = await listPremiumVoices();
    res.json({ voices });
  } catch (error) {
    res.status(500).json({
      error: "TTS voices request failed",
      message: error instanceof Error ? error.message : "Unknown error",
    });
  }
});

app.post("/api/tts/speak", async (req, res) => {
  const text = String(req.body?.text || "").trim();
  const voiceId = String(req.body?.voiceId || "").trim();
  const profile = String(req.body?.profile || "status").trim().toLowerCase();

  if (!text) {
    res.status(400).json({ error: "text is required" });
    return;
  }

  if (text.length > 4000) {
    res.status(400).json({ error: "text is too long (max 4000 chars)" });
    return;
  }

  try {
    const { audioBuffer, resolvedVoiceId, resolvedProfile } = await synthesizePremiumSpeech({ text, voiceId, profile });
    res.setHeader("Content-Type", "audio/mpeg");
    res.setHeader("Cache-Control", "no-store");
    res.setHeader("X-Echo-Voice-Id", resolvedVoiceId);
    res.setHeader("X-Echo-Voice-Profile", resolvedProfile);
    res.send(audioBuffer);
  } catch (error) {
    res.status(500).json({
      error: "TTS synthesis failed",
      message: error instanceof Error ? error.message : "Unknown error",
    });
  }
});

app.listen(port, () => {
  console.log(`[Echo Gemini Bridge] Listening on http://127.0.0.1:${port}`);
});
