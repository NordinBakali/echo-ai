import json
import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

try:
    import msvcrt
except ImportError:
    msvcrt = None

try:
    import pyaudiowpatch as pyaudio
    sys.modules.setdefault("pyaudio", pyaudio)
except ImportError:
    pass

try:
    import speech_recognition as sr
except ImportError:
    sr = None

from echo_launch_helper import find_running_echo, open_echo_interface

BASE_DIR = Path(__file__).resolve().parent
SETTINGS_FILE = BASE_DIR / "instellingen.json"
LOCK_FILE = Path(tempfile.gettempdir()) / "echo_wake_listener.lock"
DEFAULT_WAKE_WORD = "wake up"
FALLBACK_WAKE_WORDS = {
    "wake up",
    "wake app",
    "wake echo",
    "word wakker",
    "wakker worden",
    "hey echo",
    "hee echo",
    "hey eko",
    "hey eco",
}
COOLDOWN_SECONDS = 6.0
STOP_FILE = Path(tempfile.gettempdir()) / "echo_wake_listener.stop"
LOG_FILE = Path(tempfile.gettempdir()) / "echo_wake_listener.log"


def normalize_text(text):
    value = str(text or "").strip().lower()
    value = re.sub(r"[^a-z0-9\s]", " ", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value


def load_wake_word():
    try:
        payload = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
    except Exception:
        return DEFAULT_WAKE_WORD

    wake_word = normalize_text(payload.get("wake_word", ""))
    return wake_word or DEFAULT_WAKE_WORD


def wake_word_variants():
    configured = load_wake_word()
    variants = set(FALLBACK_WAKE_WORDS)
    variants.add(configured)
    if configured.startswith("hey "):
        variants.add(configured.replace("hey ", "hee ", 1))
    if configured.startswith("hee "):
        variants.add(configured.replace("hee ", "hey ", 1))
    return sorted(normalize_text(item) for item in variants if normalize_text(item))


def contains_wake_word(spoken_text, variants):
    spoken = normalize_text(spoken_text)
    for variant in variants:
        if spoken == variant or spoken.startswith(variant + " "):
            return True
    return False


def recognize_text(recognizer, audio):
    for language_code in ("en-US", "nl-NL"):
        try:
            return recognizer.recognize_google(audio, language=language_code)
        except sr.UnknownValueError:
            continue
        except sr.RequestError as exc:
            print(f"[Echo] Speech recognition unavailable: {exc}", flush=True)
            return ""
    return ""


def log_listener_message(message):
    try:
        with LOG_FILE.open("a", encoding="utf-8") as log_handle:
            log_handle.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {message}\n")
    except OSError:
        pass


def echo_window_visible():
    script = (
        "$targets = @('msedge','chrome'); "
        "$procs = Get-Process -Name $targets -ErrorAction SilentlyContinue | "
        "Where-Object { $_.MainWindowHandle -ne 0 -and $_.MainWindowTitle }; "
        "if ($procs | Where-Object { $_.MainWindowTitle -match '(?i)echo' }) { exit 0 } else { exit 1 }"
    )
    result = subprocess.run(
        ["powershell", "-NoProfile", "-Command", script],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="ignore",
    )
    return result.returncode == 0


def launch_echo_app():
    vbs_launcher = BASE_DIR / "Echo-App.vbs"
    batch_launcher = BASE_DIR / "Start-Echo-App.bat"

    if vbs_launcher.exists():
        subprocess.Popen(
            ["wscript.exe", str(vbs_launcher)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return

    if batch_launcher.exists():
        subprocess.Popen(
            [str(batch_launcher)],
            cwd=str(BASE_DIR),
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return

    raise FileNotFoundError("Could not find Echo launcher files")


def acquire_listener_lock():
    handle = open(LOCK_FILE, "a+", encoding="utf-8")
    handle.seek(0)
    existing = handle.read(1)
    if not existing:
        handle.seek(0)
        handle.write("1")
        handle.flush()

    if msvcrt is None:
        return handle

    try:
        handle.seek(0)
        msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
    except OSError:
        handle.close()
        return None

    return handle


def run_wake_listener():
    if sr is None:
        print("[Echo] SpeechRecognition is not installed. Cannot start wake listener.")
        return 1

    lock_handle = acquire_listener_lock()
    if lock_handle is None:
        print("[Echo] Wake listener is already running.")
        return 0

    recognizer = sr.Recognizer()
    recognizer.dynamic_energy_threshold = True
    recognizer.pause_threshold = 0.6

    preferred_port = int(os.environ.get("ECHO_PORT", "5000") or "5000")
    port_span = int(os.environ.get("ECHO_PORT_SPAN", "10") or "10")
    window_mode = str(os.environ.get("ECHO_WINDOW_MODE", "app") or "app")

    variants = wake_word_variants()
    cooldown_until = 0.0

    microphone_name = str(os.environ.get("ECHO_MICROPHONE", "") or "").strip()
    microphone_index = None
    if microphone_name:
        microphone_names = sr.Microphone.list_microphone_names()
        microphone_index = next(
            (index for index, name in enumerate(microphone_names) if microphone_name.lower() in name.lower()),
            None,
        )
        if microphone_index is None:
            message = f"Microphone not found: {microphone_name}"
            print(f"[Echo] {message}", flush=True)
            log_listener_message(message)
            return 1

    print(f"[Echo] Wake listener active. Say: {load_wake_word()}", flush=True)
    log_listener_message("Wake listener active")

    try:
        STOP_FILE.unlink(missing_ok=True)
        while not STOP_FILE.exists():
            try:
                with sr.Microphone(device_index=microphone_index) as source:
                    recognizer.adjust_for_ambient_noise(source, duration=0.7)
                    while not STOP_FILE.exists():
                        try:
                            audio = recognizer.listen(source, timeout=2, phrase_time_limit=4)
                        except sr.WaitTimeoutError:
                            continue

                        spoken_text = recognize_text(recognizer, audio)
                        if not spoken_text or not contains_wake_word(spoken_text, variants):
                            continue

                        now = time.time()
                        if now < cooldown_until:
                            continue

                        variants = wake_word_variants()
                        running_port, running_url = find_running_echo(preferred_port, port_span)

                        if running_url:
                            if echo_window_visible():
                                print("[Echo] Wake word detected, app already open.", flush=True)
                            else:
                                open_echo_interface(running_url.replace("/api/runtime-version", ""), window_mode)
                                print(f"[Echo] Wake word detected, reopened app window on port {running_port}.", flush=True)
                        else:
                            launch_echo_app()
                            print("[Echo] Wake word detected, launched Echo.", flush=True)

                        log_listener_message("Wake word detected")
                        cooldown_until = now + COOLDOWN_SECONDS
            except (OSError, AttributeError) as exc:
                message = f"Microphone unavailable: {exc}"
                print(f"[Echo] {message}. Retrying in 5 seconds.", flush=True)
                log_listener_message(message)
                time.sleep(5)

        print("[Echo] Wake listener stopped by Echo command.", flush=True)
    except KeyboardInterrupt:
        print("[Echo] Wake listener stopped.")
    except Exception as exc:
        print(f"[Echo] Wake listener error: {exc}", flush=True)
        log_listener_message(f"Wake listener error: {exc}")
        return 1
    finally:
        try:
            if msvcrt is not None and lock_handle:
                lock_handle.seek(0)
                msvcrt.locking(lock_handle.fileno(), msvcrt.LK_UNLCK, 1)
        except OSError:
            pass
        try:
            lock_handle.close()
        except Exception:
            pass

    return 0


if __name__ == "__main__":
    raise SystemExit(run_wake_listener())
