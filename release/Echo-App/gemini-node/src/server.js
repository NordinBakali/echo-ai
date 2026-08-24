const cors = require("cors");
const dotenv = require("dotenv");
const express = require("express");

dotenv.config();

const { askEchoWithGemini } = require("./geminiClient");
const { listPremiumVoices, synthesizePremiumSpeech } = require("./ttsClient");

const app = express();
const port = Number(process.env.PORT || 8787);

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

  if (!text) {
    res.status(400).json({ error: "text is required" });
    return;
  }

  if (text.length > 4000) {
    res.status(400).json({ error: "text is too long (max 4000 chars)" });
    return;
  }

  try {
    const { audioBuffer, resolvedVoiceId } = await synthesizePremiumSpeech({ text, voiceId });
    res.setHeader("Content-Type", "audio/mpeg");
    res.setHeader("Cache-Control", "no-store");
    res.setHeader("X-Echo-Voice-Id", resolvedVoiceId);
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
