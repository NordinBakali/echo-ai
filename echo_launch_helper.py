import argparse
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
import webbrowser
from pathlib import Path


def runtime_url(port):
    return f"http://127.0.0.1:{int(port)}/api/runtime-version"


def get_echo_runtime_url(port, timeout_seconds=0.7):
    url = runtime_url(port)
    try:
        with urllib.request.urlopen(url, timeout=timeout_seconds) as response:
            if getattr(response, "status", 200) != 200:
                return ""
            payload_raw = response.read().decode("utf-8", errors="ignore")
        payload = json.loads(payload_raw)
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ValueError, OSError):
        return ""

    if isinstance(payload, dict) and ("build_id" in payload or "started_at" in payload):
        return url
    return ""


def find_running_echo(preferred_port, port_span):
    start_port = max(1024, int(preferred_port))
    end_port = min(65535, start_port + max(0, int(port_span)))

    for port in range(start_port, end_port + 1):
        url = get_echo_runtime_url(port)
        if url:
            return port, url

    return None, ""


def browser_executable_candidates():
    program_files = Path(os.environ.get("ProgramFiles", ""))
    program_files_x86 = Path(os.environ.get("ProgramFiles(x86)", ""))
    local_appdata = Path(os.environ.get("LocalAppData", ""))

    candidates = [
        program_files_x86 / "Microsoft/Edge/Application/msedge.exe",
        program_files / "Microsoft/Edge/Application/msedge.exe",
        local_appdata / "Microsoft/Edge/Application/msedge.exe",
        program_files_x86 / "Google/Chrome/Application/chrome.exe",
        program_files / "Google/Chrome/Application/chrome.exe",
        local_appdata / "Google/Chrome/Application/chrome.exe",
    ]

    unique_paths = []
    seen = set()
    for candidate in candidates:
        candidate_str = str(candidate)
        if not candidate_str or candidate_str in seen:
            continue
        seen.add(candidate_str)
        unique_paths.append(candidate)
    return unique_paths


def open_url_in_app_window(url):
    for browser_path in browser_executable_candidates():
        if browser_path.exists():
            try:
                subprocess.Popen(
                    [str(browser_path), f"--app={url}", "--new-window"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                return True
            except Exception:
                continue

    for browser_command in ("msedge", "chrome"):
        try:
            subprocess.Popen(
                [browser_command, f"--app={url}", "--new-window"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return True
        except Exception:
            continue

    return False


def open_echo_interface(url, window_mode="app"):
    mode = str(window_mode or "app").strip().lower()
    if mode == "app" and open_url_in_app_window(url):
        return True

    webbrowser.open(url)
    return True


def parse_args(argv):
    parser = argparse.ArgumentParser(description="Echo launcher pre-check helper")
    parser.add_argument("--preferred-port", type=int, default=5000)
    parser.add_argument("--port-span", type=int, default=10)
    parser.add_argument("--window-mode", default="app")
    parser.add_argument("--reopen-if-running", action="store_true")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv if argv is not None else sys.argv[1:])
    running_port, running_url = find_running_echo(args.preferred_port, args.port_span)

    if running_url:
        print(f"[Echo] Existing runtime detected on port {running_port}: {running_url}")
        if args.reopen_if_running:
            app_url = running_url.replace("/api/runtime-version", "")
            print(f"[Echo] Reopening existing app window: {app_url}")
            open_echo_interface(app_url, args.window_mode)
        return 10

    print("[Echo] No running Echo runtime detected.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
