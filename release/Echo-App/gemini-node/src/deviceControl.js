const { execFile } = require("child_process");

const COMMAND_TIMEOUT_MS = Number.parseInt(process.env.DEVICE_COMMAND_TIMEOUT_MS || "12000", 10);
const MAX_OUTPUT_BUFFER = 64 * 1024;

const APP_COMMANDS = {
  notepad: {
    label: "Notepad",
    file: "notepad.exe",
    args: [],
  },
  calculator: {
    label: "Calculator",
    file: "calc.exe",
    args: [],
  },
  explorer: {
    label: "File Explorer",
    file: "explorer.exe",
    args: [],
  },
  edge: {
    label: "Microsoft Edge",
    file: "cmd.exe",
    args: ["/c", "start", "", "microsoft-edge:"],
  },
  chrome: {
    label: "Google Chrome",
    file: "cmd.exe",
    args: ["/c", "start", "", "chrome"],
  },
  settings: {
    label: "Windows Settings",
    file: "cmd.exe",
    args: ["/c", "start", "", "ms-settings:"],
  },
};

const APP_ALIASES = {
  calc: "calculator",
  calculator: "calculator",
  rekenmachine: "calculator",
  notepad: "notepad",
  kladblok: "notepad",
  explorer: "explorer",
  verkenner: "explorer",
  edge: "edge",
  "microsoft edge": "edge",
  chrome: "chrome",
  "google chrome": "chrome",
  settings: "settings",
  "windows settings": "settings",
  instellingen: "settings",
};

const ALLOWED_ACTIONS = ["open_app", "set_volume", "lock_screen"];
const VOLUME_MODES = new Set(["up", "down", "mute"]);

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

function clampInt(value, fallback, min, max) {
  const number = Number.parseInt(String(value || ""), 10);
  if (!Number.isFinite(number)) {
    return fallback;
  }
  return Math.max(min, Math.min(max, number));
}

function normalizeAppId(input) {
  const key = String(input || "")
    .trim()
    .toLowerCase()
    .replace(/[_-]+/g, " ")
    .replace(/\s+/g, " ");

  if (!key) {
    return "";
  }

  return APP_ALIASES[key] || key;
}

function runCommand(file, args, timeoutMs = COMMAND_TIMEOUT_MS) {
  return new Promise((resolve, reject) => {
    execFile(
      file,
      args,
      {
        windowsHide: true,
        timeout: Number.isFinite(timeoutMs) ? timeoutMs : 12000,
        maxBuffer: MAX_OUTPUT_BUFFER,
      },
      (error, stdout, stderr) => {
        if (error) {
          reject(
            new Error(
              `Command failed: ${file} ${args.join(" ")} | ${error.message} | ${String(stderr || "").trim()}`
            )
          );
          return;
        }

        resolve({
          stdout: String(stdout || "").trim(),
          stderr: String(stderr || "").trim(),
        });
      }
    );
  });
}

function buildVolumeCommand(mode, steps, language) {
  const normalizedMode = String(mode || "").trim().toLowerCase();
  if (!VOLUME_MODES.has(normalizedMode)) {
    return null;
  }

  if (normalizedMode === "mute") {
    return {
      file: "powershell.exe",
      args: [
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-Command",
        "$shell=New-Object -ComObject WScript.Shell; $shell.SendKeys([char]173)",
      ],
      message: textForLanguage(language, "Toggled mute.", "Geluid gedempt of hervat."),
      mode: "mute",
      steps: 1,
    };
  }

  const safeSteps = clampInt(steps, 4, 1, 20);
  const keyCode = normalizedMode === "up" ? 175 : 174;
  const directionLabel = normalizedMode === "up" ? "up" : "down";
  const command = `$shell=New-Object -ComObject WScript.Shell; 1..${safeSteps} | ForEach-Object { $shell.SendKeys([char]${keyCode}) }`;

  return {
    file: "powershell.exe",
    args: ["-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", command],
    message: textForLanguage(
      language,
      `Adjusted system volume ${directionLabel} (${safeSteps} step${safeSteps === 1 ? "" : "s"}).`,
      `Systeemvolume ${directionLabel === "up" ? "omhoog" : "omlaag"} aangepast (${safeSteps} stap${safeSteps === 1 ? "" : "pen"}).`
    ),
    mode: normalizedMode,
    steps: safeSteps,
  };
}

async function executeDeviceAction(actionPlan, options = {}) {
  const language = normalizeLanguage(options.language || actionPlan?.language);
  const action = String(actionPlan?.action || "").trim().toLowerCase();
  const parameters = actionPlan?.parameters && typeof actionPlan.parameters === "object" ? actionPlan.parameters : {};

  if (!ALLOWED_ACTIONS.includes(action)) {
    throw new Error(textForLanguage(language, `Unsupported device action: ${action || "unknown"}`, `Niet-ondersteunde apparaatactie: ${action || "onbekend"}`));
  }

  if (action === "open_app") {
    const appId = normalizeAppId(parameters.appId || parameters.app || parameters.application);
    const command = APP_COMMANDS[appId];

    if (!command) {
      throw new Error(textForLanguage(language, `App '${String(parameters.appId || "").trim()}' is not allowed.`, `App '${String(parameters.appId || "").trim()}' is niet toegestaan.`));
    }

    await runCommand(command.file, command.args);

    return {
      action,
      message: textForLanguage(language, `Opened ${command.label}.`, `${command.label} geopend.`),
      details: {
        appId,
      },
    };
  }

  if (action === "set_volume") {
    const command = buildVolumeCommand(parameters.mode, parameters.steps, language);
    if (!command) {
      throw new Error(textForLanguage(language, "Volume mode is invalid. Use up, down, or mute.", "Volume-modus is ongeldig. Gebruik up, down of mute."));
    }

    await runCommand(command.file, command.args);

    return {
      action,
      message: command.message,
      details: {
        mode: command.mode,
        steps: command.steps,
      },
    };
  }

  if (action === "lock_screen") {
    await runCommand("rundll32.exe", ["user32.dll,LockWorkStation"]);

    return {
      action,
      message: textForLanguage(language, "Screen locked.", "Scherm vergrendeld."),
      details: {},
    };
  }

  throw new Error(textForLanguage(language, `Unhandled device action: ${action}`, `Onverwerkte apparaatactie: ${action}`));
}

function getDeviceControlCapabilities() {
  return {
    actions: ALLOWED_ACTIONS,
    apps: Object.keys(APP_COMMANDS),
    volumeModes: Array.from(VOLUME_MODES),
    requiresConfirmationFor: ["lock_screen"],
  };
}

module.exports = {
  executeDeviceAction,
  getDeviceControlCapabilities,
};
