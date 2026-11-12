"""Explicitly approved, local process and Windows power-profile actions."""

import ctypes
from ctypes import wintypes
from collections.abc import Callable
import math
import os
import re
import subprocess
import sys
import time

import psutil


PROFILES = ("normal", "streaming", "security", "gaming", "heavy_work")
GUID = re.compile(r"[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}")
COOLING = "94d3a615-a899-4ac5-ae2b-e4d8f634367f"
PROCESSOR = "54533251-82be-4824-96c1-47b60b740d00"
PROTECTED = {
    "system", "registry", "secure system", "idle", "init", "systemd", "sshd",
    "python", "python3", "python.exe", "pythonw.exe", "node.exe", "node",
    "code.exe", "code", "explorer.exe", "cmd.exe", "powershell.exe", "pwsh.exe",
    "conhost.exe", "dwm.exe", "winlogon.exe", "csrss.exe", "lsass.exe",
    "services.exe", "svchost.exe", "smss.exe", "msmpeng.exe", "nissrv.exe",
    "securityhealthservice.exe", "msmpengcp.exe", "sense.exe",
    "msedge.exe", "msedgewebview2.exe", "chrome.exe", "firefox.exe",
}


class ResourceError(Exception):
    pass


def command(args: list[str], timeout: int = 15) -> str:
    try:
        result = subprocess.run(args, capture_output=True, text=True, encoding="utf-8",
                                errors="replace", timeout=timeout, check=False,
                                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ResourceError(f"System command unavailable: {args[0]} ({exc})") from exc
    if result.returncode:
        raise ResourceError(f"{args[0]} failed: {(result.stderr or result.stdout).strip()[:300]}")
    return result.stdout


def memory_status() -> dict:
    memory = psutil.virtual_memory()
    return {"total": memory.total, "available": memory.available, "percent": memory.percent}


def foreground_protection() -> tuple[set[int], set[str]]:
    if sys.platform != "win32":
        raise ResourceError("Automatic load protection requires Windows foreground-app detection.")
    user32 = ctypes.WinDLL("user32", use_last_error=True)
    user32.OpenInputDesktop.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    user32.OpenInputDesktop.restype = wintypes.HANDLE
    user32.GetUserObjectInformationW.argtypes = [wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD, ctypes.POINTER(wintypes.DWORD)]
    user32.CloseDesktop.argtypes = [wintypes.HANDLE]
    user32.GetForegroundWindow.restype = wintypes.HWND
    user32.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
    desktop = user32.OpenInputDesktop(0, False, 1)
    if not desktop:
        raise ResourceError("The unlocked Windows desktop could not be verified.")
    try:
        name, needed = ctypes.create_unicode_buffer(256), wintypes.DWORD()
        if not user32.GetUserObjectInformationW(desktop, 2, name, ctypes.sizeof(name), ctypes.byref(needed)) or name.value != "Default":
            raise ResourceError("Automatic load protection is paused on a locked or unavailable desktop.")
        pid = wintypes.DWORD()
        window = user32.GetForegroundWindow()
        if not window or not user32.GetWindowThreadProcessId(window, ctypes.byref(pid)) or not pid.value:
            raise ResourceError("The foreground application could not be identified. No app was stopped.")
        active = psutil.Process(pid.value)
        ancestors = active.parents()
        family = [active, *active.children(recursive=True)]
        for parent in ancestors:
            if parent.name().lower() in PROTECTED or parent.username() != active.username():
                break
            family.extend([parent, *parent.children(recursive=True)])
        paths = set()
        for process in family:
            path = process.exe()
            if not path or not os.path.isabs(path):
                raise ResourceError("The foreground application's executable could not be verified. No app was stopped.")
            paths.add(normalized_path(path))
        if not active.is_running() or user32.GetForegroundWindow() != window:
            raise ResourceError("The foreground application changed during verification. No app was stopped.")
        return {process.pid for process in [*family, *ancestors]}, paths
    except (psutil.Error, OSError) as exc:
        raise ResourceError("The foreground application's identity could not be verified. No app was stopped.") from exc
    finally:
        user32.CloseDesktop(desktop)


def load_sample(previous: dict, now: float) -> tuple[dict, dict]:
    cpu, memory = psutil.cpu_percent(interval=None), memory_status()
    if any(not isinstance(value, (int, float)) or not math.isfinite(value) or not 0 <= value <= 100
           for value in (cpu, memory["percent"])):
        raise ResourceError("CPU or RAM usage could not be measured.")
    inventory = processes()
    candidates, current = [], {}
    cores = max(1, psutil.cpu_count() or 1)
    inaccessible = inventory["inaccessible"]
    for item in inventory["items"]:
        try:
            process = psutil.Process(item["pid"])
            if process.create_time() != item["created"]:
                continue
            times = process.cpu_times()
            used = times.user + times.system
            identity = (item["pid"], item["created"])
            current[identity] = (used, now)
            prior = previous.get(identity)
            load = max(0.0, (used - prior[0]) / (now - prior[1]) / cores * 100) if prior and now > prior[1] else 0.0
            candidates.append({**item, "cpu": load})
        except psutil.NoSuchProcess:
            continue
        except (psutil.AccessDenied, OSError):
            inaccessible += 1
    return {"cpu": cpu, "ram": memory["percent"], "candidates": candidates, "inaccessible": inaccessible}, current


def local_pressure_speech(dutch: bool, check_only: bool = False) -> None:
    if sys.platform != "win32":
        raise ResourceError("Local spoken load notifications require Windows.")
    message = ("Echo heeft een goedgekeurde achtergrondapp gestopt wegens hoge belasting."
               if dutch else "Echo stopped an approved background application because of high system load.")
    script = (
        "$ErrorActionPreference='Stop'; Add-Type -AssemblyName System.Speech; "
        "$voice=New-Object System.Speech.Synthesis.SpeechSynthesizer; "
        "try { if ($voice.GetInstalledVoices().Count -eq 0) { throw 'No local Windows voices installed' }; "
        + ("" if check_only else f"$voice.Speak('{message}'); ")
        + "} finally { $voice.Dispose() }"
    )
    command(["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", script], timeout=20)


def normalized_path(value: str) -> str:
    return os.path.normcase(os.path.realpath(value))


def protected_pids() -> set[int]:
    own = psutil.Process()
    return {0, 1, own.pid, *(p.pid for p in own.parents()), *(p.pid for p in own.children(recursive=True))}


def session_id(pid: int) -> int:
    value = ctypes.c_ulong()
    if not ctypes.windll.kernel32.ProcessIdToSessionId(pid, ctypes.byref(value)):
        raise OSError("The Windows process session could not be verified.")
    return value.value


def eligible(process, protected: set[int], owner: str) -> bool:
    if process.pid in protected or owner.lower() in {"root", "nt authority\\system"}:
        return False
    name = process.name().lower()
    if name in PROTECTED or any(word in name for word in ("antivirus", "defender", "security", "sentinel", "crowdstrike", "sophos")):
        return False
    if process.username() != owner:
        return False
    raw_executable = process.exe()
    if not raw_executable or name.startswith("python"):
        return False
    executable = normalized_path(raw_executable)
    if any(word in executable.lower() for word in ("defender", "sophos", "crowdstrike", "sentinel", "kaspersky",
                                                   "bitdefender", "avast", "eset", "malwarebytes", "mcafee", "norton")):
        return False
    if not os.path.isabs(executable) or executable == normalized_path(sys.executable):
        return False
    if sys.platform == "win32":
        if session_id(process.pid) != session_id(os.getpid()):
            return False
        system = normalized_path(os.environ.get("SystemRoot", r"C:\Windows"))
        if executable == system or executable.startswith(system + os.sep):
            return False
    return True


def processes() -> dict:
    owner = psutil.Process().username()
    protected = protected_pids()
    items, inaccessible = [], 0
    for process in psutil.process_iter():
        try:
            if eligible(process, protected, owner):
                items.append({
                    "pid": process.pid, "created": process.create_time(),
                    "exe": normalized_path(process.exe()), "name": process.name(),
                    "memory": process.memory_info().rss,
                })
        except psutil.NoSuchProcess:
            continue
        except (psutil.AccessDenied, OSError):
            inaccessible += 1
    return {"items": sorted(items, key=lambda p: p["memory"], reverse=True), "inaccessible": inaccessible}


def active_scheme() -> str:
    match = GUID.search(command(["powercfg.exe", "/getactivescheme"]))
    if not match:
        raise ResourceError("Windows returned no active power-scheme GUID.")
    return match.group().lower()


def cooling_index(scheme: str) -> int | None:
    output = command(["powercfg.exe", "/qh", scheme, PROCESSOR])
    start = output.lower().find(COOLING)
    if start < 0:
        return None
    section = output[start + len(COOLING):]
    following = GUID.search(section)
    if following:
        section = section[:following.start()]
    values = re.findall(r"0x([0-9a-fA-F]+)", section)
    if len(values) < 2:
        raise ResourceError("Windows cooling-policy values could not be read.")
    return int(values[-2], 16)


def power_capabilities() -> dict:
    if sys.platform != "win32":
        return {"supported": False, "plans": [], "active": "", "active_cooling": False,
                "note": "Windows powercfg is unavailable; direct fan RPM control is not supported."}
    output = command(["powercfg.exe", "/list"])
    plans = []
    for line in output.splitlines():
        match = GUID.search(line)
        if match:
            plans.append({"id": match.group().lower(), "name": line[match.end():].strip(" ()*")})
    active = active_scheme()
    return {"supported": True, "plans": plans, "active": active,
            "active_cooling": cooling_index(active) is not None,
            "note": "Active cooling on AC power is a Windows policy, not a fan-speed guarantee. Direct RPM control requires manufacturer support."}


def validate_policy(data: object, previous: dict) -> dict:
    if not isinstance(data, dict) or set(data) != {"apps", "power_plan", "active_cooling"}:
        raise ResourceError("Invalid resource policy.")
    apps, plan, cooling = data["apps"], data["power_plan"], data["active_cooling"]
    if not isinstance(apps, list) or len(apps) > 20 or any(not isinstance(path, str) for path in apps):
        raise ResourceError("Select at most 20 applications.")
    known = {item["exe"] for item in processes()["items"]} | set(previous.get("apps", []))
    if any(path not in known for path in apps):
        raise ResourceError("An application is not in the local, eligible process list. Refresh and select again.")
    if type(cooling) is not bool or not isinstance(plan, str):
        raise ResourceError("Invalid power settings.")
    if plan or cooling:
        capabilities = power_capabilities()
        if not capabilities["supported"]:
            raise ResourceError("Power and cooling policies require Windows.")
        if plan and plan not in {item["id"] for item in capabilities["plans"]}:
            raise ResourceError("The selected power plan is unavailable.")
        if cooling and cooling_index(plan or capabilities["active"]) is None:
            raise ResourceError("Active cooling is not exposed by this hardware.")
    return {"apps": sorted(set(apps)), "power_plan": plan, "active_cooling": cooling}


def prepare(profile: str, policy: dict) -> dict:
    if profile not in PROFILES:
        raise ResourceError("Unknown profile.")
    selected = [item for item in processes()["items"] if item["exe"] in policy.get("apps", [])]
    return {"profile": profile, "processes": selected, "policy": policy, "created": time.time(),
            "memory": memory_status(), "estimated_process_memory": sum(item["memory"] for item in selected)}


def check_recovery(recovery: object) -> None:
    if (
        not isinstance(recovery, dict) or not isinstance(recovery.get("active"), str)
        or not GUID.fullmatch(recovery["active"]) or not isinstance(recovery.get("cooling"), dict)
        or any(not isinstance(scheme, str) or not GUID.fullmatch(scheme)
               or type(index) is not int or index not in (0, 1)
               for scheme, index in recovery["cooling"].items())
    ):
        raise ResourceError("Saved power recovery data is invalid. No settings were changed.")


def apply_power(policy: dict, store) -> None:
    if not policy["power_plan"] and not policy["active_cooling"]:
        return
    capabilities = power_capabilities()
    target = policy["power_plan"] or capabilities["active"]
    if target not in {p["id"] for p in capabilities["plans"]}:
        raise ResourceError("Power plan disappeared. No processes were terminated.")
    recovery = store.get("power_recovery", None)
    if recovery is None:
        recovery = {"active": capabilities["active"], "cooling": {}}
    check_recovery(recovery)
    if policy["active_cooling"]:
        old_index = cooling_index(target)
        if old_index is None:
            raise ResourceError("Cooling is unsupported. No processes were terminated.")
        recovery["cooling"].setdefault(target, old_index)
    store.set("power_recovery", recovery)
    if policy["active_cooling"]:
        command(["powercfg.exe", "/setacvalueindex", target, PROCESSOR, COOLING, "1"])
    command(["powercfg.exe", "/setactive", target])
    if active_scheme() != target or (policy["active_cooling"] and cooling_index(target) != 1):
        raise ResourceError("Power-setting verification failed. Use Restore power settings.")


def restore_power(store) -> None:
    recovery = store.get("power_recovery", None)
    if recovery is None:
        raise ResourceError("There are no saved power settings to restore.")
    check_recovery(recovery)
    for scheme, index in recovery.get("cooling", {}).items():
        command(["powercfg.exe", "/setacvalueindex", scheme, PROCESSOR, COOLING, str(index)])
        if cooling_index(scheme) != index:
            raise ResourceError("Cooling-policy restoration could not be verified.")
    command(["powercfg.exe", "/setactive", recovery["active"]])
    if active_scheme() != recovery["active"]:
        raise ResourceError("Power-plan restoration could not be verified.")
    store.set("power_recovery", None)


def execute(plan: dict, store, *, guard: Callable[[psutil.Process], bool] | None = None) -> dict:
    if time.time() - plan["created"] > 30:
        raise ResourceError("The preview expired. Preview the current processes again.")
    policy = store.get("policies", {}).get(plan["profile"], {})
    if policy != plan["policy"]:
        raise ResourceError("The policy changed. Preview again.")
    if plan.get("pressure"):
        if guard is None:
            raise ResourceError("Automatic load actions require a live foreground and permission guard.")
    else:
        apply_power(policy, store)
    owner, protected = psutil.Process().username(), protected_pids()
    results, requested = [], []
    for item in plan["processes"]:
        result = {"pid": item["pid"], "name": item["name"]}
        try:
            process = psutil.Process(item["pid"])
            if (
                process.create_time() != item["created"]
                or normalized_path(process.exe()) != item["exe"]
                or item["exe"] not in policy["apps"] or not eligible(process, protected, owner)
            ):
                result["status"] = "skipped_identity_or_protection"
            elif guard is not None and not guard(process):
                result["status"] = "skipped_foreground_or_permission"
            else:
                process.terminate()
                requested.append((process, result))
                result["status"] = "termination_requested"
        except psutil.NoSuchProcess:
            result["status"] = "already_exited"
        except (psutil.AccessDenied, OSError) as exc:
            result.update(status="error", error=str(exc)[:200])
        results.append(result)
    if requested:
        gone, _alive = psutil.wait_procs([process for process, _result in requested], timeout=3)
        gone_ids = {process.pid for process in gone}
        for process, result in requested:
            result["status"] = "terminated" if process.pid in gone_ids else "still_running"
    memory = memory_status()
    partial = any(item["status"] not in {"terminated", "already_exited"} for item in results)
    return {"status": "partial" if partial else "completed", "processes": results, "memory": memory,
            "available_change": memory["available"] - plan["memory"]["available"]}
