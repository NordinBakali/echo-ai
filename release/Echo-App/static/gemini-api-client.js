async function askEchoWithGemini(userText, endpoint = "http://127.0.0.1:8787/api/echo") {
  const text = String(userText || "").trim();
  if (!text) {
    throw new Error("User text is required.");
  }

  const response = await fetch(endpoint, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ text }),
  });

  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    const message = payload?.message || payload?.error || "Unknown request error";
    throw new Error(message);
  }

  const reply = String(payload?.reply || "").trim();
  if (!reply) {
    throw new Error("Echo returned an empty response.");
  }

  return reply;
}

async function sendEchoDeviceCommand(userText, options = {}) {
  const text = String(userText || "").trim();
  if (!text) {
    throw new Error("User text is required.");
  }

  const endpoint = String(options.endpoint || "http://127.0.0.1:8787/api/device/execute").trim();
  const body = {
    text,
    confirm: Boolean(options.confirm),
    dryRun: Boolean(options.dryRun),
  };

  const response = await fetch(endpoint, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  });

  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    const message = payload?.message || payload?.error || "Unknown request error";
    throw new Error(message);
  }

  return payload;
}

window.askEchoWithGemini = askEchoWithGemini;
window.sendEchoDeviceCommand = sendEchoDeviceCommand;
