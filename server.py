from flask import Flask, render_template, request, jsonify
import ast
import base64
import ctypes
import html
import io
import math
import os
import json
import platform
import re
import shutil
import socket
import subprocess
import tempfile
import urllib.error
import urllib.request
import webbrowser
import wave
from pathlib import Path
import threading
import time
from urllib.parse import quote_plus, urlparse

try:
    import speech_recognition as sr
    SPRAAK_BESCHIKBAAR = True
except ImportError:
    SPRAAK_BESCHIKBAAR = False

try:
    from faster_whisper import WhisperModel
    WHISPER_BESCHIKBAAR = True
except ImportError:
    WhisperModel = None
    WHISPER_BESCHIKBAAR = False

try:
    import pyttsx3
    TTS_BESCHIKBAAR = True
except ImportError:
    TTS_BESCHIKBAAR = False

try:
    import pyautogui
    import pygetwindow as gw
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.05
    AUTOMATISERING_BESCHIKBAAR = True
except Exception:
    pyautogui = None
    gw = None
    AUTOMATISERING_BESCHIKBAAR = False

try:
    import winsound
    WINSOUND_BESCHIKBAAR = True
except Exception:
    winsound = None
    WINSOUND_BESCHIKBAAR = False

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.jinja_env.auto_reload = True
SETTINGS_FILE = "instellingen.json"
ENV_FILE = Path(".env")
MEMORY_FILE = "echo_geheugen.json"
PLANNER_FILE = "echo_planning.json"
MAX_GESPREK_GESCHIEDENIS = 6
MAX_LANGETERMIJN_GEHEUGEN_ITEMS = 12
MAX_OPEN_TAKEN = 30
MAX_NOTIFICATIES = 20
MAX_DOCUMENT_SNIPPETS = 3
MAX_DOCUMENT_BESTANDSGROOTTE = 200_000
DOCUMENT_CONTEXT_EXTENSIES = {".md", ".txt", ".json", ".py", ".html", ".js", ".css"}
DOCUMENT_CONTEXT_GENEGEERDE_MAPNAMEN = {".git", ".venv", "__pycache__", ".mypy_cache", ".pytest_cache"}
WORKSPACE_SEARCH_GENEGEERDE_BESTANDEN = {".env", "echo_geheugen.json", "instellingen.json"}
DOCUMENT_CONTEXT_STOPWOORDEN = {
    "the", "and", "for", "with", "this", "that", "from", "have", "what", "when", "where", "which", "will", "would",
    "your", "about", "into", "how", "why", "can", "you", "echo", "een", "het", "de", "van", "met", "voor", "naar",
    "wat", "hoe", "waar", "waarom", "dan", "dit", "dat", "zijn", "kan", "kun", "ook", "maar", "niet", "welke",
}


def strip_omringende_quotes(waarde):
    waarde = str(waarde or "").strip()
    if len(waarde) >= 2 and waarde[0] == waarde[-1] and waarde[0] in {'"', "'"}:
        return waarde[1:-1]
    return waarde


def laad_env_variabelen(env_pad=ENV_FILE):
    env_pad = Path(env_pad)
    if not env_pad.exists():
        return

    try:
        regels = env_pad.read_text(encoding="utf-8").splitlines()
    except Exception:
        return

    for regel in regels:
        regel = regel.strip()
        if not regel or regel.startswith("#"):
            continue
        if regel.lower().startswith("export "):
            regel = regel[7:].strip()

        sleutel, scheiding, waarde = regel.partition("=")
        if not scheiding:
            continue

        sleutel = sleutel.strip()
        waarde = strip_omringende_quotes(waarde.strip())
        if sleutel and sleutel not in os.environ:
            os.environ[sleutel] = waarde


laad_env_variabelen()

# Standaard instellingen
DEFAULT_SETTINGS = {
    "naam": "Echo",
    "client_naam": "",
    "taal": "English",
    "verkenner_start_map": str(Path.home()),
    "youtube_url": "https://youtube.com",
    "google_url": "https://google.com",
    "emoji_gebruik": True,
    "begroeting_tonen": True,
    "spraak_ingang": False,
    "spraak_uitgang": True,
    "spraak_taal": "en-US",
    "spraak_input_provider": str(os.environ.get("STT_PROVIDER", "google") or "google").strip().lower(),
    "whisper_model": str(os.environ.get("WHISPER_MODEL", "small") or "small").strip(),
    "whisper_device": str(os.environ.get("WHISPER_DEVICE", "auto") or "auto").strip().lower(),
    "whisper_compute_type": str(os.environ.get("WHISPER_COMPUTE_TYPE", "auto") or "auto").strip().lower(),
    "whisper_beam_size": os.environ.get("WHISPER_BEAM_SIZE", "5"),
    "whisper_vad_filter": os.environ.get("WHISPER_VAD_FILTER", "true"),
    "spraak_provider": str(os.environ.get("TTS_PROVIDER", "local") or "local").strip().lower(),
    "cloud_tts_voice": str(os.environ.get("GOOGLE_TTS_VOICE", "") or "").strip(),
    "cloud_tts_speed": os.environ.get("GOOGLE_TTS_SPEED", "1.0"),
    "cloud_tts_pitch": os.environ.get("GOOGLE_TTS_PITCH", "0.0"),
    "wake_word": "hey echo",
    "browser_stem": "",
    "agent_modus": True,
    "geheugen_modus": True,
    "prioriteit_modus": True,
    "computerbesturing_toestaan": False,
    "online_ai_modus": True,
    "online_ai_model": os.environ.get("OPENAI_MODEL", "gpt-4.1-mini"),
    "ai_agent_primair": True
}

AUTOMATISERING_TIMEOUT_SECONDEN = 300
APP_START_TIMESTAMP = time.time()
APP_BUILD_ID = str(int(APP_START_TIMESTAMP * 1000))
AUTO_OPEN_MARKER_FILE = Path(tempfile.gettempdir()) / "echo_auto_open.marker"


def normaliseer_taalwaarde(taal):
    waarde = str(taal or "").strip().lower()
    if waarde in {"nl", "nl-nl", "nederlands", "dutch"}:
        return "Nederlands"
    return "English"


def standaard_spraak_taal(taal):
    return "nl-NL" if normaliseer_taalwaarde(taal) == "Nederlands" else "en-US"


def begrens_float_waarde(waarde, standaard, minimum=None, maximum=None):
    try:
        resultaat = float(waarde)
    except (TypeError, ValueError):
        resultaat = float(standaard)

    if minimum is not None:
        resultaat = max(float(minimum), resultaat)
    if maximum is not None:
        resultaat = min(float(maximum), resultaat)
    return resultaat


def begrens_int_waarde(waarde, standaard, minimum=None, maximum=None):
    try:
        resultaat = int(float(waarde))
    except (TypeError, ValueError):
        resultaat = int(standaard)

    if minimum is not None:
        resultaat = max(int(minimum), resultaat)
    if maximum is not None:
        resultaat = min(int(maximum), resultaat)
    return resultaat


def parseer_bool_waarde(waarde, standaard=False):
    if isinstance(waarde, bool):
        return waarde

    tekst = str(waarde or "").strip().lower()
    if tekst in {"1", "true", "yes", "y", "ja", "on"}:
        return True
    if tekst in {"0", "false", "no", "n", "nee", "off"}:
        return False
    return bool(standaard)


def normaliseer_spraak_provider(provider):
    provider = str(provider or "").strip().lower()
    if provider not in {"local", "google"}:
        return "local"
    return provider


def normaliseer_spraak_input_provider(provider):
    provider = str(provider or "").strip().lower()
    if provider not in {"google", "whisper"}:
        return "google"
    return provider


def normaliseer_whisper_device(device):
    device = str(device or "").strip().lower()
    if device == "gpu":
        return "cuda"
    if device not in {"auto", "cpu", "cuda"}:
        return "auto"
    return device


def normaliseer_whisper_compute_type(compute_type):
    compute_type = str(compute_type or "").strip().lower()
    toegestane_types = {
        "auto",
        "default",
        "int8",
        "int8_float16",
        "int16",
        "float16",
        "float32",
    }
    if compute_type not in toegestane_types:
        return "auto"
    return compute_type


def synchroniseer_taalinstellingen(configuratie):
    configuratie["taal"] = normaliseer_taalwaarde(configuratie.get("taal", DEFAULT_SETTINGS["taal"]))
    configuratie["spraak_taal"] = standaard_spraak_taal(configuratie["taal"])
    configuratie["spraak_input_provider"] = normaliseer_spraak_input_provider(
        configuratie.get("spraak_input_provider", DEFAULT_SETTINGS["spraak_input_provider"])
    )
    configuratie["whisper_model"] = str(configuratie.get("whisper_model", DEFAULT_SETTINGS["whisper_model"]) or "").strip() or "small"
    configuratie["whisper_device"] = normaliseer_whisper_device(
        configuratie.get("whisper_device", DEFAULT_SETTINGS["whisper_device"])
    )
    configuratie["whisper_compute_type"] = normaliseer_whisper_compute_type(
        configuratie.get("whisper_compute_type", DEFAULT_SETTINGS["whisper_compute_type"])
    )
    configuratie["whisper_beam_size"] = begrens_int_waarde(
        configuratie.get("whisper_beam_size", DEFAULT_SETTINGS["whisper_beam_size"]),
        standaard=5,
        minimum=1,
        maximum=10,
    )
    configuratie["whisper_vad_filter"] = parseer_bool_waarde(
        configuratie.get("whisper_vad_filter", DEFAULT_SETTINGS["whisper_vad_filter"]),
        standaard=True,
    )
    configuratie["spraak_provider"] = normaliseer_spraak_provider(
        configuratie.get("spraak_provider", DEFAULT_SETTINGS["spraak_provider"])
    )
    configuratie["cloud_tts_voice"] = str(configuratie.get("cloud_tts_voice", "") or "").strip()
    configuratie["cloud_tts_speed"] = begrens_float_waarde(
        configuratie.get("cloud_tts_speed", DEFAULT_SETTINGS["cloud_tts_speed"]),
        standaard=1.0,
        minimum=0.25,
        maximum=4.0,
    )
    configuratie["cloud_tts_pitch"] = begrens_float_waarde(
        configuratie.get("cloud_tts_pitch", DEFAULT_SETTINGS["cloud_tts_pitch"]),
        standaard=0.0,
        minimum=-20.0,
        maximum=20.0,
    )

    if not str(configuratie.get("wake_word", "")).strip():
        configuratie["wake_word"] = "hee echo" if configuratie["taal"] == "Nederlands" else "hey echo"

    return configuratie

def laad_instellingen():
    """Laad instellingen uit bestand"""
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
            instellingen = json.load(f)
            for key, value in DEFAULT_SETTINGS.items():
                if key not in instellingen:
                    instellingen[key] = value
            return synchroniseer_taalinstellingen(instellingen)
    return synchroniseer_taalinstellingen(DEFAULT_SETTINGS.copy())

def sla_instellingen_op(instellingen):
    """Sla instellingen op"""
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(instellingen, f, ensure_ascii=False, indent=2)

instellingen = laad_instellingen()

GESPREK_CONTEXT = {
    "laatste_plan": [],
    "laatste_resultaten": [],
    "laatste_map": "",
    "laatste_webactie": "",
    "laatste_routering": {},
    "wacht_op_bevestiging": "",
    "automatisering_actief_tot": 0.0,
    "recente_gesprekken": [],
    "notificaties": []
}
APP_START_TIJD = time.time()
MODEL_STATUS_LOCK = threading.Lock()
MODEL_STATUS_CACHE = {
    "checked_at": 0.0,
    "status": {},
}
WHISPER_MODEL_LOCK = threading.Lock()
WHISPER_MODEL_CACHE = {
    "model": None,
    "cache_key": "",
    "loaded_at": 0.0,
}


def gebruik_nederlands():
    return normaliseer_taalwaarde(instellingen.get("taal", DEFAULT_SETTINGS["taal"])) == "Nederlands"


def tekst_voor_taal(engels, nederlands):
    return nederlands if gebruik_nederlands() else engels


def update_routering_context(intent="", tool="", categorie="", fase="", notitie=""):
    GESPREK_CONTEXT["laatste_routering"] = {
        "intent": str(intent or "").strip(),
        "tool": str(tool or "").strip(),
        "category": str(categorie or "").strip(),
        "phase": str(fase or "").strip(),
        "note": str(notitie or "").strip(),
        "at": time.time(),
    }


def huidige_routering_context():
    routering = GESPREK_CONTEXT.get("laatste_routering")
    return routering if isinstance(routering, dict) else {}


def opschonen_korte_tekst(tekst, max_lengte=240):
    tekst = re.sub(r"\s+", " ", str(tekst or "")).strip()
    if len(tekst) > max_lengte:
        return tekst[: max_lengte - 3].rstrip() + "..."
    return tekst


def kan_niet_oproepen_bericht(verzoek=""):
    verzoek = opschonen_korte_tekst(verzoek, max_lengte=80)
    if verzoek:
        return tekst_voor_taal(
            f"I can't call or open '{verzoek}' right now. Tell me in a simpler way what you want to open, read, search, or explain, and I'll try a different route.",
            f"Ik kan '{verzoek}' nu niet voor je oproepen. Zeg in een simpelere zin wat je wilt openen, lezen, zoeken of uitgelegd wilt hebben, dan probeer ik een andere route."
        )

    return tekst_voor_taal(
        "I can't call or open that right now. Tell me in a simpler way what you want to open, read, search, or explain, and I'll try a different route.",
        "Ik kan dat nu niet voor je oproepen. Zeg in een simpelere zin wat je wilt openen, lezen, zoeken of uitgelegd wilt hebben, dan probeer ik een andere route."
    )


def standaard_langetermijn_geheugen():
    return {
        "profiel": {},
        "feiten": [],
        "notities": [],
    }


def normaliseer_geheugen_item(tekst, max_lengte=160):
    return opschonen_korte_tekst(tekst, max_lengte=max_lengte)


def laad_langetermijn_geheugen():
    geheugen = standaard_langetermijn_geheugen()
    geheugen_pad = Path(MEMORY_FILE)
    if not geheugen_pad.exists():
        return geheugen

    try:
        inhoud = json.loads(geheugen_pad.read_text(encoding="utf-8"))
    except Exception:
        return geheugen

    if not isinstance(inhoud, dict):
        return geheugen

    profiel = inhoud.get("profiel")
    if isinstance(profiel, dict):
        for sleutel, waarde in profiel.items():
            sleutel = str(sleutel or "").strip().lower()
            waarde = normaliseer_geheugen_item(waarde, max_lengte=80)
            if sleutel and waarde:
                geheugen["profiel"][sleutel] = waarde

    for veld in ("feiten", "notities"):
        items = inhoud.get(veld)
        if not isinstance(items, list):
            continue

        unieke_items = []
        bekende_items = set()
        for item in items:
            opgeschoond = normaliseer_geheugen_item(item)
            sleutel = opgeschoond.casefold()
            if not opgeschoond or sleutel in bekende_items:
                continue
            unieke_items.append(opgeschoond)
            bekende_items.add(sleutel)
        geheugen[veld] = unieke_items[-MAX_LANGETERMIJN_GEHEUGEN_ITEMS:]

    return geheugen


def sla_langetermijn_geheugen_op():
    try:
        Path(MEMORY_FILE).write_text(
            json.dumps(LANGETERMIJN_GEHEUGEN, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        return True
    except Exception:
        return False


def huidige_client_naam():
    profiel_naam = str(LANGETERMIJN_GEHEUGEN.get("profiel", {}).get("name", "")).strip()
    if profiel_naam:
        return profiel_naam
    return str(instellingen.get("client_naam", "")).strip()


def voeg_langetermijn_item_toe(veld, waarde):
    waarde = normaliseer_geheugen_item(waarde)
    if not waarde:
        return False

    items = LANGETERMIJN_GEHEUGEN.setdefault(veld, [])
    sleutel = waarde.casefold()
    if any(str(item).casefold() == sleutel for item in items):
        return False

    items.append(waarde)
    if len(items) > MAX_LANGETERMIJN_GEHEUGEN_ITEMS:
        del items[:-MAX_LANGETERMIJN_GEHEUGEN_ITEMS]
    sla_langetermijn_geheugen_op()
    return True


def verwijder_langetermijn_item(veld, zoektekst):
    zoektekst = normaliseer_geheugen_item(zoektekst)
    if not zoektekst:
        return ""

    zoek_sleutel = zoektekst.casefold()
    items = LANGETERMIJN_GEHEUGEN.get(veld, [])
    for index, item in enumerate(list(items)):
        item_tekst = str(item)
        item_sleutel = item_tekst.casefold()
        if zoek_sleutel == item_sleutel or zoek_sleutel in item_sleutel or item_sleutel in zoek_sleutel:
            del items[index]
            sla_langetermijn_geheugen_op()
            return item_tekst
    return ""


def stel_profielgegeven_in(sleutel, waarde):
    sleutel = str(sleutel or "").strip().lower()
    waarde = normaliseer_geheugen_item(waarde, max_lengte=80)
    if not sleutel or not waarde:
        return False

    profiel = LANGETERMIJN_GEHEUGEN.setdefault("profiel", {})
    if profiel.get(sleutel) == waarde:
        return False

    profiel[sleutel] = waarde
    if sleutel == "name":
        instellingen["client_naam"] = waarde
        sla_instellingen_op(instellingen)
    sla_langetermijn_geheugen_op()
    return True


def verwijder_profielgegeven(sleutel):
    sleutel = str(sleutel or "").strip().lower()
    if not sleutel:
        return ""

    profiel = LANGETERMIJN_GEHEUGEN.get("profiel", {})
    verwijderde_waarde = str(profiel.pop(sleutel, "")).strip()
    if sleutel == "name":
        instellingen["client_naam"] = ""
        sla_instellingen_op(instellingen)
    if verwijderde_waarde:
        sla_langetermijn_geheugen_op()
    return verwijderde_waarde


def wis_langetermijn_geheugen():
    LANGETERMIJN_GEHEUGEN.clear()
    LANGETERMIJN_GEHEUGEN.update(standaard_langetermijn_geheugen())
    instellingen["client_naam"] = ""
    sla_instellingen_op(instellingen)
    sla_langetermijn_geheugen_op()


def extraheer_naam_uit_tekst(tekst):
    tekst = re.sub(r"\s+", " ", str(tekst or "")).strip()
    if not tekst:
        return ""

    patronen = [
        r"^(?:my name is|i am called|call me)\s+(?P<naam>.+)$",
        r"^(?:mijn naam is|ik heet|noem me)\s+(?P<naam>.+)$",
    ]

    for patroon in patronen:
        match = re.match(patroon, tekst, flags=re.IGNORECASE)
        if not match:
            continue

        naam = re.split(r"\b(?:and|but|en|maar)\b", match.group("naam"), maxsplit=1, flags=re.IGNORECASE)[0]
        naam = naam.strip(" .,!?:;\"'")
        if 1 < len(naam) <= 40:
            return naam

    return ""


def is_zuivere_naamzin(tekst):
    tekst = re.sub(r"\s+", " ", str(tekst or "")).strip()
    if not tekst:
        return False

    patronen = [
        r"^(?:my name is|i am called|call me)\s+[A-Za-zÀ-ÖØ-öø-ÿ][A-Za-zÀ-ÖØ-öø-ÿ' -]{1,39}[.!?]?$",
        r"^(?:mijn naam is|ik heet|noem me)\s+[A-Za-zÀ-ÖØ-öø-ÿ][A-Za-zÀ-ÖØ-öø-ÿ' -]{1,39}[.!?]?$",
    ]
    return any(re.fullmatch(patroon, tekst, flags=re.IGNORECASE) for patroon in patronen)


def beschrijf_langetermijn_geheugen():
    naam = huidige_client_naam()
    feiten = LANGETERMIJN_GEHEUGEN.get("feiten", [])[-4:]
    notities = LANGETERMIJN_GEHEUGEN.get("notities", [])[-4:]

    if not naam and not feiten and not notities:
        return tekst_voor_taal(
            "I do not have any saved long-term memory yet.",
            "Ik heb nog geen opgeslagen langetermijngeheugen."
        )

    delen = []
    if naam:
        delen.append(tekst_voor_taal(f"your name is {naam}", f"je naam is {naam}"))
    if feiten:
        delen.append(
            tekst_voor_taal("saved facts", "opgeslagen feiten") + ": " + "; ".join(feiten)
        )
    if notities:
        delen.append(
            tekst_voor_taal("saved notes", "opgeslagen notities") + ": " + "; ".join(notities)
        )

    return tekst_voor_taal(
        "I remember that " + "; ".join(delen) + ".",
        "Ik onthoud dat " + "; ".join(delen) + "."
    )


def blok_langetermijn_geheugen():
    regels = []
    naam = huidige_client_naam()
    if naam:
        regels.append("- " + tekst_voor_taal("Name", "Naam") + f": {naam}")

    for feit in LANGETERMIJN_GEHEUGEN.get("feiten", [])[-4:]:
        regels.append("- " + tekst_voor_taal("Fact", "Feit") + f": {feit}")

    for notitie in LANGETERMIJN_GEHEUGEN.get("notities", [])[-4:]:
        regels.append("- " + tekst_voor_taal("Note", "Notitie") + f": {notitie}")

    if not regels:
        return ""

    return tekst_voor_taal("Long-term memory:", "Langetermijngeheugen:") + "\n" + "\n".join(regels)


def behandel_geheugen_commando(tekst):
    if not instellingen.get("geheugen_modus", True):
        return ""

    tekst = re.sub(r"\s+", " ", str(tekst or "")).strip()
    tekst_lower = tekst.lower()
    if not tekst:
        return ""

    if re.fullmatch(r"(?:what do you remember about me|what do you know about me|show memory|show my memory|show my notes|wat weet je over mij|wat onthoud je van mij|toon mijn geheugen|toon mijn notities)\??", tekst_lower):
        return beschrijf_langetermijn_geheugen()

    if re.fullmatch(r"(?:what is my name|what's my name|wat is mijn naam|hoe heet ik)\??", tekst_lower):
        naam = huidige_client_naam()
        if naam:
            return tekst_voor_taal(f"Your name is {naam}.", f"Je naam is {naam}.")
        return tekst_voor_taal("I do not know your name yet.", "Ik weet je naam nog niet.")

    if re.fullmatch(r"(?:clear memory|reset memory|forget everything about me|wis geheugen|reset geheugen|vergeet alles over mij)\??", tekst_lower):
        wis_langetermijn_geheugen()
        return tekst_voor_taal("I cleared my saved long-term memory.", "Ik heb mijn opgeslagen langetermijngeheugen gewist.")

    if re.fullmatch(r"(?:forget my name|vergeet mijn naam)\??", tekst_lower):
        verwijderde_naam = verwijder_profielgegeven("name") or huidige_client_naam()
        if verwijderde_naam:
            return tekst_voor_taal("I forgot your saved name.", "Ik ben je opgeslagen naam vergeten.")
        return tekst_voor_taal("I did not have a saved name yet.", "Ik had nog geen opgeslagen naam.")

    naam = extraheer_naam_uit_tekst(tekst)
    if naam:
        stel_profielgegeven_in("name", naam)
        return tekst_voor_taal(
            f"I will remember your name as {naam}.",
            f"Ik onthoud je naam als {naam}."
        )

    vergeet_match = re.match(
        r"^(?:forget that|forget note|remove memory|delete memory|delete note|vergeet dat|verwijder geheugen|verwijder notitie|wis notitie)\s+(?P<item>.+)$",
        tekst,
        flags=re.IGNORECASE
    )
    if vergeet_match:
        zoekterm = vergeet_match.group("item").strip(" .,!?:;\"'")
        if not zoekterm:
            return ""

        verwijderd_item = verwijder_langetermijn_item("feiten", zoekterm) or verwijder_langetermijn_item("notities", zoekterm)
        if verwijderd_item:
            return tekst_voor_taal(
                f"I removed this saved memory: {verwijderd_item}",
                f"Ik heb dit opgeslagen geheugen verwijderd: {verwijderd_item}"
            )
        return tekst_voor_taal(
            "I could not find that saved memory.",
            "Ik kon dat opgeslagen geheugen niet vinden."
        )

    geheugen_patronen = [
        (r"^(?:remember that|remember this|save memory|store memory)\s+(?P<item>.+)$", "feiten"),
        (r"^(?:onthoud dat|onthoud dit|sla dit op|sla op dat|bewaar dit)\s+(?P<item>.+)$", "feiten"),
        (r"^(?:remember note|save note|store note)\s+(?P<item>.+)$", "notities"),
        (r"^(?:bewaar notitie|sla notitie op|onthoud notitie)\s+(?P<item>.+)$", "notities"),
    ]
    for patroon, veld in geheugen_patronen:
        match = re.match(patroon, tekst, flags=re.IGNORECASE)
        if not match:
            continue

        item = match.group("item").strip(" .,!?:;\"'")
        if not item:
            return ""

        opgeslagen_naam = extraheer_naam_uit_tekst(item)
        wijzigingen = []
        if opgeslagen_naam and stel_profielgegeven_in("name", opgeslagen_naam):
            wijzigingen.append(tekst_voor_taal(f"name {opgeslagen_naam}", f"naam {opgeslagen_naam}"))

        if not (opgeslagen_naam and is_zuivere_naamzin(item)) and voeg_langetermijn_item_toe(veld, item):
            wijzigingen.append(item)

        if wijzigingen:
            return tekst_voor_taal(
                "I saved this to long-term memory: " + "; ".join(wijzigingen),
                "Ik heb dit in mijn langetermijngeheugen opgeslagen: " + "; ".join(wijzigingen)
            )

        return tekst_voor_taal(
            "I already had that saved in long-term memory.",
            "Dat stond al in mijn langetermijngeheugen."
        )

    return ""


LANGETERMIJN_GEHEUGEN = laad_langetermijn_geheugen()


def standaard_planning_data():
    return {
        "next_id": 1,
        "timers": [],
        "reminders": [],
        "tasks": [],
    }


def laad_planning_data():
    planning = standaard_planning_data()
    planning_pad = Path(PLANNER_FILE)
    if not planning_pad.exists():
        return planning

    try:
        inhoud = json.loads(planning_pad.read_text(encoding="utf-8"))
    except Exception:
        return planning

    if not isinstance(inhoud, dict):
        return planning

    hoogste_id = 0
    for veld in ("timers", "reminders"):
        items = inhoud.get(veld)
        if not isinstance(items, list):
            continue

        gevalideerde_items = []
        for item in items[:100]:
            if not isinstance(item, dict):
                continue

            try:
                item_id = int(item.get("id", 0))
                due_at = float(item.get("due_at", 0))
                seconden = max(1, int(item.get("seconds", 0)))
            except (TypeError, ValueError):
                continue

            bericht = opschonen_korte_tekst(item.get("message", ""), max_lengte=220)
            status = str(item.get("status", "pending")).strip().lower()
            if not bericht or due_at <= 0 or status not in {"pending", "done", "cancelled"}:
                continue

            hoogste_id = max(hoogste_id, item_id)
            gevalideerde_items.append({
                "id": item_id,
                "message": bericht,
                "seconds": seconden,
                "due_at": due_at,
                "created_at": float(item.get("created_at", 0.0) or 0.0),
                "status": status,
            })

        planning[veld] = gevalideerde_items

    taken = inhoud.get("tasks")
    if isinstance(taken, list):
        gevalideerde_taken = []
        for item in taken[:200]:
            if not isinstance(item, dict):
                continue

            try:
                item_id = int(item.get("id", 0))
            except (TypeError, ValueError):
                continue

            tekst = opschonen_korte_tekst(item.get("text", ""), max_lengte=220)
            status = str(item.get("status", "open")).strip().lower()
            if not tekst or status not in {"open", "done"}:
                continue

            hoogste_id = max(hoogste_id, item_id)
            gevalideerde_taken.append({
                "id": item_id,
                "text": tekst,
                "status": status,
                "created_at": float(item.get("created_at", 0.0) or 0.0),
                "updated_at": float(item.get("updated_at", 0.0) or 0.0),
            })
        planning["tasks"] = gevalideerde_taken

    try:
        next_id = int(inhoud.get("next_id", hoogste_id + 1))
    except (TypeError, ValueError):
        next_id = hoogste_id + 1
    planning["next_id"] = max(hoogste_id + 1, next_id, 1)
    return planning


PLANNER_LOCK = threading.Lock()
PLANNING_DATA = laad_planning_data()
PLANNER_MONITOR_GESTART = False
SYSTEM_SCAN_LOCK = threading.Lock()
MAX_SYSTEM_SCAN_LOGS = 24
SYSTEM_SCAN_STAPPEN = [
    {
        "label_en": "Component store quick health check (DISM /CheckHealth)",
        "label_nl": "Snelle componentstore-check (DISM /CheckHealth)",
        "command": ["DISM", "/Online", "/Cleanup-Image", "/CheckHealth"],
        "timeout": 900,
    },
    {
        "label_en": "Component store deep scan (DISM /ScanHealth)",
        "label_nl": "Dieptecontrole componentstore (DISM /ScanHealth)",
        "command": ["DISM", "/Online", "/Cleanup-Image", "/ScanHealth"],
        "timeout": 1800,
    },
    {
        "label_en": "System file integrity and repair (SFC /SCANNOW)",
        "label_nl": "Integriteitscontrole en reparatie systeembestanden (SFC /SCANNOW)",
        "command": ["sfc", "/scannow"],
        "timeout": 5400,
    },
]


def standaard_system_scan_data():
    return {
        "running": False,
        "state": "idle",
        "started_at": 0.0,
        "updated_at": 0.0,
        "finished_at": 0.0,
        "stage": "",
        "progress_percent": 0,
        "steps_total": len(SYSTEM_SCAN_STAPPEN),
        "steps_completed": 0,
        "last_result": "",
        "recent_logs": [],
    }


SYSTEM_SCAN_STATE = standaard_system_scan_data()


def sla_planning_data_op():
    try:
        Path(PLANNER_FILE).write_text(
            json.dumps(PLANNING_DATA, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        return True
    except Exception:
        return False


def volgende_planner_id():
    volgende_id = int(PLANNING_DATA.get("next_id", 1) or 1)
    PLANNING_DATA["next_id"] = volgende_id + 1
    return volgende_id


def registreer_notificatie(bericht):
    bericht = opschonen_korte_tekst(bericht, max_lengte=320)
    if not bericht:
        return

    notificaties = GESPREK_CONTEXT.setdefault("notificaties", [])
    notificaties.append({
        "message": bericht,
        "created_at": time.time(),
    })
    if len(notificaties) > MAX_NOTIFICATIES:
        del notificaties[:-MAX_NOTIFICATIES]

    spreek_uit(bericht)


def formatteer_duur_compact(seconden):
    resterend = max(0, int(round(seconden)))
    dagen, resterend = divmod(resterend, 86400)
    uren, resterend = divmod(resterend, 3600)
    minuten, seconden = divmod(resterend, 60)

    delen = []
    if dagen:
        delen.append(f"{dagen}d")
    if uren:
        delen.append(f"{uren}h")
    if minuten:
        delen.append(f"{minuten}m")
    if seconden or not delen:
        delen.append(f"{seconden}s")
    return " ".join(delen[:3])


def open_taken():
    return [taak for taak in PLANNING_DATA.get("tasks", []) if taak.get("status") == "open"]


def open_planning_items(veld):
    return [item for item in PLANNING_DATA.get(veld, []) if item.get("status") == "pending"]


def blok_planning_context():
    regels = []

    timers = open_planning_items("timers")[:4]
    if timers:
        regels.append(
            tekst_voor_taal("Active timers", "Actieve timers") + ": " + "; ".join(
                f"#{item['id']} {formatteer_duur_compact(item['due_at'] - time.time())}" for item in timers
            )
        )

    reminders = open_planning_items("reminders")[:4]
    if reminders:
        regels.append(
            tekst_voor_taal("Pending reminders", "Open herinneringen") + ": " + "; ".join(
                f"#{item['id']} {item['message']} ({formatteer_duur_compact(item['due_at'] - time.time())})" for item in reminders
            )
        )

    taken = open_taken()[:5]
    if taken:
        regels.append(
            tekst_voor_taal("Open tasks", "Open taken") + ": " + "; ".join(
                f"#{taak['id']} {taak['text']}" for taak in taken
            )
        )

    if not regels:
        return ""
    return tekst_voor_taal("Planner:", "Planner:") + "\n" + "\n".join("- " + regel for regel in regels)


def planner_item_matcht(item, zoekterm):
    zoekterm = str(zoekterm or "").strip().casefold()
    if not zoekterm:
        return False
    if zoekterm.isdigit() and int(zoekterm) == int(item.get("id", 0)):
        return True

    bron = str(item.get("text") or item.get("message") or "").casefold()
    return zoekterm in bron


def zoek_planner_items(veld, zoekterm):
    items = open_planning_items(veld) if veld in {"timers", "reminders"} else open_taken()
    zoekterm = str(zoekterm or "").strip().lower()

    if zoekterm in {"", "last", "laatste"}:
        return items[-1:] if items else []
    if zoekterm in {"all", "alles"}:
        return list(items)

    for item in items:
        if planner_item_matcht(item, zoekterm):
            return [item]
    return []


def voeg_timer_toe(seconden):
    with PLANNER_LOCK:
        item = {
            "id": volgende_planner_id(),
            "message": tekst_voor_taal("Timer finished", "Timer klaar"),
            "seconds": max(1, int(seconden)),
            "due_at": time.time() + max(1, int(seconden)),
            "created_at": time.time(),
            "status": "pending",
        }
        PLANNING_DATA["timers"].append(item)
        sla_planning_data_op()
        return dict(item)


def voeg_herinnering_toe(seconden, bericht):
    with PLANNER_LOCK:
        item = {
            "id": volgende_planner_id(),
            "message": opschonen_korte_tekst(bericht, max_lengte=220),
            "seconds": max(1, int(seconden)),
            "due_at": time.time() + max(1, int(seconden)),
            "created_at": time.time(),
            "status": "pending",
        }
        PLANNING_DATA["reminders"].append(item)
        sla_planning_data_op()
        return dict(item)


def voeg_taak_toe(tekst):
    tekst = opschonen_korte_tekst(tekst, max_lengte=220)
    if not tekst:
        return None

    with PLANNER_LOCK:
        open_items = open_taken()
        if len(open_items) >= MAX_OPEN_TAKEN:
            return "limit"

        if any(str(item.get("text", "")).casefold() == tekst.casefold() for item in open_items):
            return "duplicate"

        item = {
            "id": volgende_planner_id(),
            "text": tekst,
            "status": "open",
            "created_at": time.time(),
            "updated_at": time.time(),
        }
        PLANNING_DATA["tasks"].append(item)
        sla_planning_data_op()
        return dict(item)


def annuleer_planning_items(veld, zoekterm):
    with PLANNER_LOCK:
        matches = zoek_planner_items(veld, zoekterm)
        if not matches:
            return []
        for item in matches:
            item["status"] = "cancelled"
        sla_planning_data_op()
        return [dict(item) for item in matches]


def voltooi_taak(zoekterm):
    with PLANNER_LOCK:
        matches = zoek_planner_items("tasks", zoekterm)
        if not matches:
            return None
        taak = matches[0]
        taak["status"] = "done"
        taak["updated_at"] = time.time()
        sla_planning_data_op()
        return dict(taak)


def verwijder_taak(zoekterm):
    with PLANNER_LOCK:
        matches = zoek_planner_items("tasks", zoekterm)
        if not matches:
            return None
        taak = matches[0]
        PLANNING_DATA["tasks"] = [item for item in PLANNING_DATA["tasks"] if int(item.get("id", 0)) != int(taak.get("id", 0))]
        sla_planning_data_op()
        return dict(taak)


def planner_lijst_bericht(veld):
    if veld == "tasks":
        taken = open_taken()
        if not taken:
            return tekst_voor_taal("No open tasks.", "Geen open taken.")
        return tekst_voor_taal(
            "Open tasks: " + "; ".join(f"#{item['id']} {item['text']}" for item in taken[:10]),
            "Open taken: " + "; ".join(f"#{item['id']} {item['text']}" for item in taken[:10])
        )

    items = open_planning_items(veld)
    if not items:
        return tekst_voor_taal(
            f"No active {veld}.",
            f"Geen actieve {'timers' if veld == 'timers' else 'herinneringen'}."
        )

    if veld == "timers":
        regels = [f"#{item['id']} {formatteer_duur_compact(item['due_at'] - time.time())}" for item in items[:10]]
        return tekst_voor_taal("Active timers: " + "; ".join(regels), "Actieve timers: " + "; ".join(regels))

    regels = [
        f"#{item['id']} {item['message']} ({formatteer_duur_compact(item['due_at'] - time.time())})"
        for item in items[:10]
    ]
    return tekst_voor_taal("Pending reminders: " + "; ".join(regels), "Open herinneringen: " + "; ".join(regels))


def agenda_overzicht_bericht():
    delen = []
    for veld in ("timers", "reminders", "tasks"):
        bericht = planner_lijst_bericht(veld)
        if bericht and not bericht.lower().startswith(("no ", "geen ")):
            delen.append(bericht)
    if not delen:
        return tekst_voor_taal("Your planner is empty.", "Je planner is leeg.")
    return " ".join(delen)


def verwerk_verlopen_planning_items():
    verlopen_items = []
    huidige_tijd = time.time()

    with PLANNER_LOCK:
        gewijzigd = False
        for veld in ("timers", "reminders"):
            for item in PLANNING_DATA.get(veld, []):
                if item.get("status") == "pending" and float(item.get("due_at", 0)) <= huidige_tijd:
                    item["status"] = "done"
                    item["completed_at"] = huidige_tijd
                    verlopen_items.append((veld, dict(item)))
                    gewijzigd = True

        if gewijzigd:
            sla_planning_data_op()

    for veld, item in verlopen_items:
        if veld == "timers":
            bericht = tekst_voor_taal(
                f"Timer #{item['id']} finished.",
                f"Timer #{item['id']} is klaar."
            )
        else:
            bericht = tekst_voor_taal(
                f"Reminder: {item['message']}",
                f"Herinnering: {item['message']}"
            )
        registreer_notificatie(bericht)


def planner_monitor_worker():
    while True:
        try:
            verwerk_verlopen_planning_items()
        except Exception:
            pass
        time.sleep(1.0)


def start_planning_monitor():
    global PLANNER_MONITOR_GESTART
    if PLANNER_MONITOR_GESTART:
        return
    threading.Thread(target=planner_monitor_worker, daemon=True).start()
    PLANNER_MONITOR_GESTART = True


def heeft_windows_adminrechten():
    if platform.system().lower() != "windows":
        return False
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def system_scan_log_toevoegen(bericht):
    opgeschoond = opschonen_korte_tekst(bericht, max_lengte=280)
    if not opgeschoond:
        return

    logs = SYSTEM_SCAN_STATE.setdefault("recent_logs", [])
    logs.append({
        "message": opgeschoond,
        "at": time.time(),
    })
    if len(logs) > MAX_SYSTEM_SCAN_LOGS:
        del logs[:-MAX_SYSTEM_SCAN_LOGS]


def system_scan_output_samenvatting(stdout_tekst, stderr_tekst, max_regels=3):
    regels = []
    for bron in (stdout_tekst, stderr_tekst):
        for regel in str(bron or "").splitlines():
            schoon = opschonen_korte_tekst(regel, max_lengte=220)
            if not schoon:
                continue
            if schoon.lower().startswith("deployment image servicing"):
                continue
            regels.append(schoon)

    if not regels:
        return ""

    return " | ".join(regels[-max_regels:])


def huidige_system_scan_payload():
    with SYSTEM_SCAN_LOCK:
        payload = dict(SYSTEM_SCAN_STATE)
        payload["recent_logs"] = list(SYSTEM_SCAN_STATE.get("recent_logs", []))

    laatste_log = payload["recent_logs"][-1] if payload["recent_logs"] else {}
    payload["last_log"] = str(laatste_log.get("message", "") or "").strip()
    payload["updated_at_label"] = (
        time.strftime("%H:%M:%S", time.localtime(float(payload.get("updated_at", 0.0) or 0.0)))
        if payload.get("updated_at")
        else ""
    )
    return payload


def system_scan_status_bericht():
    scan = huidige_system_scan_payload()
    status = str(scan.get("state", "idle") or "idle")
    stage = str(scan.get("stage", "") or "").strip()
    progressie = int(scan.get("progress_percent", 0) or 0)
    resultaat = str(scan.get("last_result", "") or "").strip()

    if scan.get("running"):
        return tekst_voor_taal(
            f"System Scan in Progress: {stage or 'working'} ({progressie}%).",
            f"Systeemscan bezig: {stage or 'bezig'} ({progressie}%)."
        )

    if status == "completed":
        return resultaat or tekst_voor_taal(
            "System scan completed.",
            "Systeemscan voltooid."
        )

    if status == "error":
        return resultaat or tekst_voor_taal(
            "System scan stopped with an error.",
            "Systeemscan is gestopt met een fout."
        )

    return tekst_voor_taal(
        "System scan is idle. Say start system scan when you are ready.",
        "Systeemscan staat stand-by. Zeg start systeemscan wanneer je klaar bent."
    )


def voer_system_scan_worker_uit():
    totaal = max(1, len(SYSTEM_SCAN_STAPPEN))

    for index, stap in enumerate(SYSTEM_SCAN_STAPPEN, start=1):
        label = tekst_voor_taal(stap["label_en"], stap["label_nl"])

        with SYSTEM_SCAN_LOCK:
            SYSTEM_SCAN_STATE["stage"] = label
            SYSTEM_SCAN_STATE["steps_completed"] = max(0, index - 1)
            SYSTEM_SCAN_STATE["progress_percent"] = int(round(((index - 1) / totaal) * 100))
            SYSTEM_SCAN_STATE["updated_at"] = time.time()
            system_scan_log_toevoegen(
                tekst_voor_taal(
                    f"Step {index}/{totaal} running: {label}",
                    f"Stap {index}/{totaal} draait: {label}"
                )
            )

        try:
            resultaat = subprocess.run(
                stap["command"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="ignore",
                timeout=int(stap.get("timeout", 1200) or 1200),
            )
        except FileNotFoundError:
            fout_bericht = tekst_voor_taal(
                f"System scan failed: command not found for {label}.",
                f"Systeemscan mislukt: opdracht niet gevonden voor {label}."
            )
            with SYSTEM_SCAN_LOCK:
                SYSTEM_SCAN_STATE.update({
                    "running": False,
                    "state": "error",
                    "finished_at": time.time(),
                    "updated_at": time.time(),
                    "last_result": fout_bericht,
                })
                system_scan_log_toevoegen(fout_bericht)
            registreer_notificatie(fout_bericht)
            return
        except subprocess.TimeoutExpired:
            fout_bericht = tekst_voor_taal(
                f"System scan timed out during: {label}.",
                f"Systeemscan timeout tijdens: {label}."
            )
            with SYSTEM_SCAN_LOCK:
                SYSTEM_SCAN_STATE.update({
                    "running": False,
                    "state": "error",
                    "finished_at": time.time(),
                    "updated_at": time.time(),
                    "last_result": fout_bericht,
                })
                system_scan_log_toevoegen(fout_bericht)
            registreer_notificatie(fout_bericht)
            return
        except Exception as e:
            fout_bericht = tekst_voor_taal(
                f"System scan failed during {label}: {e}",
                f"Systeemscan mislukte tijdens {label}: {e}"
            )
            with SYSTEM_SCAN_LOCK:
                SYSTEM_SCAN_STATE.update({
                    "running": False,
                    "state": "error",
                    "finished_at": time.time(),
                    "updated_at": time.time(),
                    "last_result": fout_bericht,
                })
                system_scan_log_toevoegen(fout_bericht)
            registreer_notificatie(fout_bericht)
            return

        output_kern = system_scan_output_samenvatting(resultaat.stdout, resultaat.stderr)
        if int(resultaat.returncode) != 0:
            fout_bericht = tekst_voor_taal(
                f"System scan step failed ({resultaat.returncode}) at {label}. {output_kern}",
                f"Systeemscanstap mislukt ({resultaat.returncode}) bij {label}. {output_kern}"
            ).strip()
            with SYSTEM_SCAN_LOCK:
                SYSTEM_SCAN_STATE.update({
                    "running": False,
                    "state": "error",
                    "finished_at": time.time(),
                    "updated_at": time.time(),
                    "last_result": fout_bericht,
                    "steps_completed": max(0, index - 1),
                    "progress_percent": int(round(((index - 1) / totaal) * 100)),
                })
                system_scan_log_toevoegen(fout_bericht)
            registreer_notificatie(fout_bericht)
            return

        with SYSTEM_SCAN_LOCK:
            SYSTEM_SCAN_STATE["steps_completed"] = index
            SYSTEM_SCAN_STATE["progress_percent"] = int(round((index / totaal) * 100))
            SYSTEM_SCAN_STATE["updated_at"] = time.time()
            if output_kern:
                system_scan_log_toevoegen(
                    tekst_voor_taal(
                        f"Step {index} completed: {output_kern}",
                        f"Stap {index} voltooid: {output_kern}"
                    )
                )

    eindbericht = tekst_voor_taal(
        "System scan completed. DISM and SFC checks finished.",
        "Systeemscan voltooid. DISM- en SFC-controles zijn afgerond."
    )
    with SYSTEM_SCAN_LOCK:
        SYSTEM_SCAN_STATE.update({
            "running": False,
            "state": "completed",
            "finished_at": time.time(),
            "updated_at": time.time(),
            "progress_percent": 100,
            "steps_completed": totaal,
            "stage": tekst_voor_taal("System scan complete", "Systeemscan afgerond"),
            "last_result": eindbericht,
        })
        system_scan_log_toevoegen(eindbericht)
    registreer_notificatie(eindbericht)


def start_system_scan():
    if platform.system().lower() != "windows":
        return False, tekst_voor_taal(
            "System scan is only available on Windows.",
            "Systeemscan is alleen beschikbaar op Windows."
        )

    if not heeft_windows_adminrechten():
        return False, tekst_voor_taal(
            "System scan needs administrator rights. Start Echo as administrator and try again.",
            "Systeemscan heeft administratorrechten nodig. Start Echo als administrator en probeer opnieuw."
        )

    with SYSTEM_SCAN_LOCK:
        if SYSTEM_SCAN_STATE.get("running"):
            return False, tekst_voor_taal(
                "System Scan in Progress already.",
                "Systeemscan is al bezig."
            )

        now = time.time()
        SYSTEM_SCAN_STATE.update(standaard_system_scan_data())
        SYSTEM_SCAN_STATE.update({
            "running": True,
            "state": "running",
            "started_at": now,
            "updated_at": now,
            "stage": tekst_voor_taal("Preparing diagnostics", "Diagnose wordt voorbereid"),
            "progress_percent": 2,
        })
        system_scan_log_toevoegen(
            tekst_voor_taal(
                "System Scan in Progress. Running DISM and SFC in the background.",
                "Systeemscan bezig. DISM en SFC draaien op de achtergrond."
            )
        )

    threading.Thread(target=voer_system_scan_worker_uit, daemon=True).start()
    return True, tekst_voor_taal(
        "System Scan in Progress. I started diagnostics in the background.",
        "Systeemscan bezig. Ik ben de diagnose op de achtergrond gestart."
    )


def model_basis_url():
    azure_endpoint = str(os.environ.get("AZURE_OPENAI_ENDPOINT", "") or "").strip()
    if azure_endpoint:
        return azure_endpoint.rstrip("/")
    return str(os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1") or "https://api.openai.com/v1").strip()


def huidige_ai_api_key():
    return str(
        os.environ.get("AZURE_OPENAI_API_KEY", "")
        or os.environ.get("OPENAI_API_KEY", "")
        or ""
    ).strip()


def huidige_ai_model_naam():
    return str(
        os.environ.get("OPENAI_MODEL", instellingen.get("online_ai_model", DEFAULT_SETTINGS["online_ai_model"]))
        or ""
    ).strip()


def azure_openai_endpoint():
    endpoint = str(os.environ.get("AZURE_OPENAI_ENDPOINT", "") or "").strip()
    if endpoint:
        return endpoint.rstrip("/")

    basis_url = str(os.environ.get("OPENAI_BASE_URL", "") or "").strip()
    if "openai.azure.com" in basis_url.lower():
        return basis_url.rstrip("/")
    return ""


def azure_openai_deployment(model_naam=""):
    return str(os.environ.get("AZURE_OPENAI_DEPLOYMENT", "") or model_naam or "").strip()


def azure_openai_api_version():
    return str(os.environ.get("AZURE_OPENAI_API_VERSION", "2024-10-21") or "2024-10-21").strip()


def model_provider_naam(basis_url):
    if azure_openai_endpoint():
        return "azure-openai"

    basis_url = str(basis_url or "").lower()
    if any(waarde in basis_url for waarde in ("127.0.0.1", "localhost", "11434", "ollama")):
        return "ollama"
    if "openai.com" in basis_url:
        return "openai"
    return "openai-compatible"


def lokale_model_provider(basis_url):
    basis_url = str(basis_url or "").lower()
    return any(waarde in basis_url for waarde in ("127.0.0.1", "localhost"))


def model_tags_url(basis_url):
    basis = str(basis_url or "").rstrip("/")
    if basis.endswith("/v1"):
        basis = basis[:-3]
    return basis + "/api/tags"


def haal_model_status(force=False):
    huidige_tijd = time.time()
    with MODEL_STATUS_LOCK:
        if not force and MODEL_STATUS_CACHE["status"] and (huidige_tijd - MODEL_STATUS_CACHE["checked_at"]) < 8:
            return dict(MODEL_STATUS_CACHE["status"])

    basis_url = model_basis_url()
    model_naam = huidige_ai_model_naam()
    provider = model_provider_naam(basis_url)
    status = {
        "enabled": bool(instellingen.get("online_ai_modus", True)),
        "configured": bool(huidige_ai_api_key()),
        "available": False,
        "reachable": False,
        "provider": provider,
        "model": model_naam,
        "base_url": basis_url if lokale_model_provider(basis_url) else "",
        "latency_ms": None,
        "model_present": False,
        "message": tekst_voor_taal("Model disabled", "Model uitgeschakeld"),
    }

    if not status["enabled"]:
        status["message"] = tekst_voor_taal("Connected AI is disabled in settings.", "Gekoppelde AI staat uit in instellingen.")
    elif not status["configured"]:
        status["message"] = tekst_voor_taal("No AI key or local token is configured.", "Er is geen AI-sleutel of lokaal token ingesteld.")
    elif provider == "ollama":
        verzoek = urllib.request.Request(model_tags_url(basis_url), headers={"Accept": "application/json"}, method="GET")
        start = time.time()
        try:
            with urllib.request.urlopen(verzoek, timeout=2.0) as response:
                data = json.loads(response.read().decode("utf-8"))
            modellen = data.get("models") or []
            namen = {
                str(model.get("name") or "").strip()
                for model in modellen
                if isinstance(model, dict)
            }
            latency_ms = int(round((time.time() - start) * 1000))
            status.update({
                "available": True,
                "reachable": True,
                "latency_ms": latency_ms,
                "model_present": (model_naam in namen) if model_naam else False,
                "message": tekst_voor_taal(
                    f"Local Ollama is reachable in {latency_ms} ms.",
                    f"Lokale Ollama is bereikbaar in {latency_ms} ms."
                ),
            })
        except Exception as e:
            status["message"] = tekst_voor_taal(
                f"Local Ollama is not reachable: {e}",
                f"Lokale Ollama is niet bereikbaar: {e}"
            )
    elif provider == "azure-openai":
        deployment = azure_openai_deployment(model_naam)
        if not deployment:
            status["message"] = tekst_voor_taal(
                "Azure OpenAI is missing a deployment name. Set AZURE_OPENAI_DEPLOYMENT or OPENAI_MODEL.",
                "Azure OpenAI mist een deploymentnaam. Zet AZURE_OPENAI_DEPLOYMENT of OPENAI_MODEL."
            )
        else:
            status.update({
                "available": True,
                "message": tekst_voor_taal(
                    "Azure OpenAI is configured.",
                    "Azure OpenAI is ingesteld."
                ),
            })
    else:
        status.update({
            "available": True,
            "message": tekst_voor_taal(
                "Connected AI is configured.",
                "Gekoppelde AI is ingesteld."
            ),
        })

    with MODEL_STATUS_LOCK:
        MODEL_STATUS_CACHE["checked_at"] = huidige_tijd
        MODEL_STATUS_CACHE["status"] = dict(status)
    return status


def planning_item_voor_dashboard(item, veld):
    payload = {
        "id": int(item.get("id", 0) or 0),
        "status": str(item.get("status", "")).strip().lower(),
    }
    if veld == "tasks":
        payload.update({
            "text": str(item.get("text") or "").strip(),
            "updated_at": float(item.get("updated_at", 0.0) or 0.0),
        })
        return payload

    resterend = max(0, int(round(float(item.get("due_at", 0.0) or 0.0) - time.time())))
    payload.update({
        "message": str(item.get("message") or "").strip(),
        "seconds": int(item.get("seconds", 0) or 0),
        "remaining_seconds": resterend,
        "remaining_label": formatteer_duur_compact(resterend),
        "due_at": float(item.get("due_at", 0.0) or 0.0),
    })
    return payload


def recente_notificaties_voor_dashboard(max_items=6):
    notificaties = list(GESPREK_CONTEXT.get("notificaties", []))[-max_items:]
    notificaties.reverse()
    huidige_tijd = time.time()
    resultaten = []
    for item in notificaties:
        aangemaakt = float(item.get("created_at", 0.0) or 0.0)
        resultaten.append({
            "message": str(item.get("message") or "").strip(),
            "created_at": aangemaakt,
            "age_seconds": max(0, int(round(huidige_tijd - aangemaakt))),
            "age_label": formatteer_duur_compact(max(0, huidige_tijd - aangemaakt)),
        })
    return resultaten


def recente_acties_voor_dashboard(max_items=5):
    plan = list(GESPREK_CONTEXT.get("laatste_plan", []))
    resultaten = list(GESPREK_CONTEXT.get("laatste_resultaten", []))
    items = []
    for actie, resultaat in zip(plan[-max_items:], resultaten[-max_items:]):
        items.append({
            "command": str(actie or "").strip(),
            "result": opschonen_korte_tekst(resultaat, max_lengte=180),
        })
    items.reverse()
    return items


def dashboard_bestand_suggesties(max_items=8):
    voorkeuren = [
        "README.md",
        "server.py",
        "templates/index.html",
        "static/script.js",
        "static/style.css",
        "requirements.txt",
    ]
    resultaten = []
    gezien = set()

    for relatieve_pad in voorkeuren:
        pad = Path.cwd() / relatieve_pad
        if not pad.exists() or not pad.is_file():
            continue
        sleutel = relatief_document_pad(pad)
        if sleutel in gezien:
            continue
        resultaten.append({
            "path": sleutel,
            "name": pad.name,
            "suffix": pad.suffix.lower(),
        })
        gezien.add(sleutel)

    for pad in iter_workspace_bestanden():
        if pad.suffix.lower() not in DOCUMENT_CONTEXT_EXTENSIES:
            continue
        sleutel = relatief_document_pad(pad)
        if sleutel in gezien:
            continue
        resultaten.append({
            "path": sleutel,
            "name": pad.name,
            "suffix": pad.suffix.lower(),
        })
        gezien.add(sleutel)
        if len(resultaten) >= max_items:
            break

    return resultaten[:max_items]


def maak_pending_bevestiging_payload():
    wachtende_actie = str(GESPREK_CONTEXT.get("wacht_op_bevestiging", "") or "").strip()

    payload = {
        "pending": False,
        "action_key": "",
        "kind": "",
        "target": "",
        "prompt": "",
        "prompt_en": "",
        "prompt_nl": "",
        "confirm_command": "confirm pending action",
        "cancel_command": "cancel pending action",
    }

    if not wachtende_actie:
        return payload

    payload["pending"] = True
    payload["action_key"] = wachtende_actie

    kind = "unknown"
    target = ""
    prompt_en = "Safety check: confirm the pending action."
    prompt_nl = "Veiligheidscontrole: bevestig de wachtende actie."

    if wachtende_actie in DANGEROUS_SYSTEM_ACTIONS:
        details = DANGEROUS_SYSTEM_ACTIONS[wachtende_actie]
        kind = "system"
        prompt_en = f"Safety check: confirm to {details['confirm_en']}."
        prompt_nl = f"Veiligheidscontrole: bevestig om {details['confirm_nl']}."
    elif wachtende_actie.startswith("delete path::"):
        kind = "workspace-delete"
        doel_tekst = wachtende_actie.split("::", 1)[1]
        doel_pad = resolve_bron_pad_voor_operatie(doel_tekst)
        target = str(doel_pad or doel_tekst).strip()
        if target:
            prompt_en = f"Safety check: confirm to delete {target}."
            prompt_nl = f"Veiligheidscontrole: bevestig om {target} te verwijderen."
    elif wachtende_actie.startswith("overwrite file::"):
        kind = "workspace-overwrite"
        bestand_payload = wachtende_actie.split("::", 1)[1]
        doel_tekst = bestand_payload.split("||", 1)[0] if "||" in bestand_payload else bestand_payload
        doel_pad = resolve_pad_voor_operatie(doel_tekst)
        target = str(doel_pad or doel_tekst).strip()
        if target:
            prompt_en = f"Safety check: confirm to overwrite {target}."
            prompt_nl = f"Veiligheidscontrole: bevestig om {target} te overschrijven."
    elif wachtende_actie.startswith("rewrite file::"):
        kind = "workspace-rewrite"
        bestand_payload = wachtende_actie.split("::", 1)[1]
        doel_tekst = bestand_payload.split("||", 1)[0] if "||" in bestand_payload else bestand_payload
        doel_pad = resolve_bestand_pad(doel_tekst)
        target = str(doel_pad or doel_tekst).strip()
        if target:
            prompt_en = f"Safety check: confirm to rewrite {target}."
            prompt_nl = f"Veiligheidscontrole: bevestig om {target} te herschrijven."

    payload.update({
        "kind": kind,
        "target": target,
        "prompt_en": prompt_en,
        "prompt_nl": prompt_nl,
        "prompt": tekst_voor_taal(prompt_en, prompt_nl),
    })

    return payload


def maak_dashboard_payload():
    verwerk_verlopen_planning_items()
    huidige_tijd = time.time()
    model_status = haal_model_status()
    automation_seconden = max(0, int(round(GESPREK_CONTEXT.get("automatisering_actief_tot", 0.0) - huidige_tijd)))

    with PLANNER_LOCK:
        open_taken_lijst = [planning_item_voor_dashboard(item, "tasks") for item in open_taken()[:8]]
        open_timers_lijst = [planning_item_voor_dashboard(item, "timers") for item in open_planning_items("timers")[:6]]
        open_reminders_lijst = [planning_item_voor_dashboard(item, "reminders") for item in open_planning_items("reminders")[:6]]
        open_task_count = len(open_taken())
        active_timer_count = len(open_planning_items("timers"))
        pending_reminder_count = len(open_planning_items("reminders"))

    laatste_commando_tijd = float(GESPREK_CONTEXT.get("laatste_commando_at", 0.0) or 0.0)
    return {
        "generated_at": huidige_tijd,
        "generated_at_label": time.strftime("%H:%M:%S", time.localtime(huidige_tijd)),
        "runtime": {
            "uptime_seconds": max(0, int(round(huidige_tijd - APP_START_TIJD))),
            "uptime_label": formatteer_duur_compact(max(0, huidige_tijd - APP_START_TIJD)),
            "last_command": {
                "text": str(GESPREK_CONTEXT.get("laatste_commando", "") or "").strip(),
                "duration_ms": int(GESPREK_CONTEXT.get("laatste_commando_duur_ms", 0) or 0),
                "success": bool(GESPREK_CONTEXT.get("laatste_commando_succes", False)),
                "at": laatste_commando_tijd,
                "at_label": time.strftime("%H:%M:%S", time.localtime(laatste_commando_tijd)) if laatste_commando_tijd else "",
            },
        },
        "routing": huidige_routering_context(),
        "modes": {
            "language": instellingen.get("taal", DEFAULT_SETTINGS["taal"]),
            "voice_language": instellingen.get("spraak_taal", DEFAULT_SETTINGS["spraak_taal"]),
            "speech_input_provider": normaliseer_spraak_input_provider(
                instellingen.get("spraak_input_provider", DEFAULT_SETTINGS["spraak_input_provider"])
            ),
            "whisper_available": bool(WHISPER_BESCHIKBAAR),
            "voice_provider": normaliseer_spraak_provider(instellingen.get("spraak_provider", DEFAULT_SETTINGS["spraak_provider"])),
            "cloud_tts_ready": cloud_tts_configuratie_beschikbaar(),
            "wake_word": instellingen.get("wake_word", DEFAULT_SETTINGS["wake_word"]),
            "voice_output": bool(instellingen.get("spraak_uitgang", True)),
            "memory_enabled": bool(instellingen.get("geheugen_modus", True)),
            "thinking_enabled": bool(instellingen.get("agent_modus", True)),
            "priority_enabled": bool(instellingen.get("prioriteit_modus", True)),
            "ai_agent_first": bool(instellingen.get("ai_agent_primair", True)),
            "online_ai_enabled": bool(instellingen.get("online_ai_modus", True)),
            "automation_allowed": bool(instellingen.get("computerbesturing_toestaan", False)),
            "automation_active": automatisering_actief(),
            "automation_seconds_left": automation_seconden,
            "automation_label": formatteer_duur_compact(automation_seconden) if automation_seconden else "0s",
        },
        "ai": model_status,
        "memory": {
            "summary": beschrijf_langetermijn_geheugen(),
            "profile_count": len(LANGETERMIJN_GEHEUGEN.get("profiel", {})),
            "fact_count": len(LANGETERMIJN_GEHEUGEN.get("feiten", [])),
            "note_count": len(LANGETERMIJN_GEHEUGEN.get("notities", [])),
        },
        "planner": {
            "open_task_count": open_task_count,
            "active_timer_count": active_timer_count,
            "pending_reminder_count": pending_reminder_count,
            "tasks": open_taken_lijst,
            "timers": open_timers_lijst,
            "reminders": open_reminders_lijst,
            "notifications": recente_notificaties_voor_dashboard(),
        },
        "workspace": {
            "cwd": str(Path.cwd()),
            "recent_web_action": str(GESPREK_CONTEXT.get("laatste_webactie", "") or "").strip(),
            "recent_actions": recente_acties_voor_dashboard(),
            "suggested_files": dashboard_bestand_suggesties(),
        },
        "system_scan": huidige_system_scan_payload(),
        "pending_confirmation": maak_pending_bevestiging_payload(),
    }


def registreer_gesprek_uitwisseling(gebruiker_tekst, echo_tekst):
    gebruiker_tekst = opschonen_korte_tekst(gebruiker_tekst)
    echo_tekst = opschonen_korte_tekst(echo_tekst, max_lengte=320)
    if not gebruiker_tekst or not echo_tekst:
        return

    geschiedenis = GESPREK_CONTEXT.setdefault("recente_gesprekken", [])
    geschiedenis.append({"user": gebruiker_tekst, "assistant": echo_tekst})
    if len(geschiedenis) > MAX_GESPREK_GESCHIEDENIS:
        del geschiedenis[:-MAX_GESPREK_GESCHIEDENIS]


def kies_stem_voor_taal(engine):
    is_nederlands = instellingen.get("spraak_taal", "en-US").lower().startswith("nl")
    taal_prefix = "nl" if is_nederlands else "en"
    patronen = (
        ("female", "zira", "hazel", "aria", "jenny", "emma", "samantha", "eva")
        if not is_nederlands
        else ("female", "fem", "vrouw", "marjolein", "claire", "emma", "sophie")
    )

    try:
        stemmen = engine.getProperty("voices")
    except Exception:
        return

    for stem in stemmen:
        beschrijving = f"{getattr(stem, 'name', '')} {getattr(stem, 'id', '')}".lower()
        talen = " ".join(str(taal).lower() for taal in getattr(stem, "languages", []))
        if any(patroon in beschrijving for patroon in patronen) and (
            taal_prefix in talen or taal_prefix in beschrijving or not talen
        ):
            engine.setProperty("voice", stem.id)
            return

    for stem in stemmen:
        beschrijving = f"{getattr(stem, 'name', '')} {getattr(stem, 'id', '')}".lower()
        talen = " ".join(str(taal).lower() for taal in getattr(stem, "languages", []))
        if taal_prefix in talen or taal_prefix in beschrijving:
            engine.setProperty("voice", stem.id)
            return


def google_tts_api_key():
    return str(os.environ.get("GOOGLE_TTS_API_KEY", "") or os.environ.get("GOOGLE_API_KEY", "")).strip()


def cloud_tts_configuratie_beschikbaar():
    return bool(google_tts_api_key() and WINSOUND_BESCHIKBAAR)


def standaard_google_tts_stem():
    is_nederlands = str(instellingen.get("spraak_taal", "en-US")).lower().startswith("nl")
    return "nl-NL-Wavenet-C" if is_nederlands else "en-US-Neural2-F"


def google_tts_stemnaam():
    stem = str(instellingen.get("cloud_tts_voice", "") or os.environ.get("GOOGLE_TTS_VOICE", "")).strip()
    return stem if stem else standaard_google_tts_stem()


def maak_wav_uit_pcm(pcm_bytes, sample_rate_hz=24000):
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(int(sample_rate_hz))
        wav_file.writeframes(pcm_bytes)
    return buffer.getvalue()


def vraag_google_tts_audio(tekst):
    api_key = google_tts_api_key()
    if not api_key:
        raise RuntimeError("GOOGLE_TTS_API_KEY is not set")

    taalcode = str(instellingen.get("spraak_taal", "en-US") or "en-US").strip()
    stemnaam = google_tts_stemnaam()
    snelheid = begrens_float_waarde(instellingen.get("cloud_tts_speed", 1.0), standaard=1.0, minimum=0.25, maximum=4.0)
    pitch = begrens_float_waarde(instellingen.get("cloud_tts_pitch", 0.0), standaard=0.0, minimum=-20.0, maximum=20.0)

    payload = {
        "input": {"text": str(tekst or "")[:4500]},
        "voice": {
            "languageCode": taalcode,
            "name": stemnaam,
        },
        "audioConfig": {
            "audioEncoding": "LINEAR16",
            "speakingRate": snelheid,
            "pitch": pitch,
            "sampleRateHertz": 24000,
        },
    }

    request = urllib.request.Request(
        f"https://texttospeech.googleapis.com/v1/text:synthesize?key={quote_plus(api_key)}",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(request, timeout=25) as response:
        data = json.loads(response.read().decode("utf-8"))

    audio_content = str(data.get("audioContent") or "").strip()
    if not audio_content:
        raise RuntimeError("Google TTS returned empty audio")

    audio_bytes = base64.b64decode(audio_content)
    if not audio_bytes.startswith(b"RIFF"):
        audio_bytes = maak_wav_uit_pcm(audio_bytes, sample_rate_hz=24000)
    return audio_bytes


def spreek_uit_via_google_tts(tekst):
    if not cloud_tts_configuratie_beschikbaar():
        return False

    audio_bytes = vraag_google_tts_audio(tekst)
    winsound.PlaySound(audio_bytes, winsound.SND_MEMORY)
    return True

def spreek_uit(tekst):
    """Spreek tekst uit via text-to-speech"""
    if not instellingen.get("spraak_uitgang", True):
        return

    tekst = str(tekst or "").strip()
    if not tekst:
        return

    provider = normaliseer_spraak_provider(instellingen.get("spraak_provider", DEFAULT_SETTINGS["spraak_provider"]))

    if provider == "google":
        try:
            if spreek_uit_via_google_tts(tekst):
                return
        except Exception as e:
            print(f"Cloud spraak fout: {e}")

    if not TTS_BESCHIKBAAR:
        return
    
    try:
        engine = pyttsx3.init()
        kies_stem_voor_taal(engine)
        engine.say(tekst)
        engine.runAndWait()
    except Exception as e:
        print(f"Spraak fout: {e}")


def whisper_taalcode_voor_spraak():
    taal = str(instellingen.get("spraak_taal", "en-US") or "en-US").strip().lower()
    if "-" in taal:
        taal = taal.split("-", 1)[0]
    if len(taal) >= 2:
        return taal[:2]
    return "en"


def whisper_compute_type_voor_runtime():
    compute_type = normaliseer_whisper_compute_type(instellingen.get("whisper_compute_type", DEFAULT_SETTINGS["whisper_compute_type"]))
    if compute_type == "auto":
        return "default"
    return compute_type


def whisper_model_cache_key():
    model_naam = str(instellingen.get("whisper_model", DEFAULT_SETTINGS["whisper_model"]) or "small").strip() or "small"
    device = normaliseer_whisper_device(instellingen.get("whisper_device", DEFAULT_SETTINGS["whisper_device"]))
    compute_type = whisper_compute_type_voor_runtime()
    return f"{model_naam}|{device}|{compute_type}"


def laad_whisper_model():
    if not WHISPER_BESCHIKBAAR or WhisperModel is None:
        raise RuntimeError("faster-whisper is not available")

    model_naam = str(instellingen.get("whisper_model", DEFAULT_SETTINGS["whisper_model"]) or "small").strip() or "small"
    device = normaliseer_whisper_device(instellingen.get("whisper_device", DEFAULT_SETTINGS["whisper_device"]))
    compute_type = whisper_compute_type_voor_runtime()
    cache_key = whisper_model_cache_key()

    with WHISPER_MODEL_LOCK:
        huidig_model = WHISPER_MODEL_CACHE.get("model")
        if huidig_model is not None and WHISPER_MODEL_CACHE.get("cache_key") == cache_key:
            return huidig_model

        model = WhisperModel(model_naam, device=device, compute_type=compute_type)
        WHISPER_MODEL_CACHE["model"] = model
        WHISPER_MODEL_CACHE["cache_key"] = cache_key
        WHISPER_MODEL_CACHE["loaded_at"] = time.time()
        return model


def herken_spraak_via_whisper(audio):
    model = laad_whisper_model()
    beam_size = begrens_int_waarde(instellingen.get("whisper_beam_size", 5), standaard=5, minimum=1, maximum=10)
    vad_filter = parseer_bool_waarde(instellingen.get("whisper_vad_filter", True), standaard=True)
    taal = whisper_taalcode_voor_spraak()

    temp_pad = ""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_bestand:
            temp_bestand.write(audio.get_wav_data(convert_rate=16000, convert_width=2))
            temp_pad = temp_bestand.name

        segmenten, _ = model.transcribe(
            temp_pad,
            language=taal,
            beam_size=beam_size,
            vad_filter=vad_filter,
        )

        transcriptie = " ".join(
            str(getattr(segment, "text", "") or "").strip()
            for segment in segmenten
            if str(getattr(segment, "text", "") or "").strip()
        ).strip()
        return transcriptie
    finally:
        if temp_pad:
            try:
                Path(temp_pad).unlink(missing_ok=True)
            except Exception:
                pass


def herken_spraak_via_google(recognizer, audio):
    try:
        return recognizer.recognize_google(audio, language=instellingen.get("spraak_taal", DEFAULT_SETTINGS["spraak_taal"]))
    except Exception:
        return ""

def herken_spraak():
    """Herken spraak via microfoon"""
    if not SPRAAK_BESCHIKBAAR:
        return None
    
    try:
        recognizer = sr.Recognizer()
        recognizer.dynamic_energy_threshold = True
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.6)
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=16)

        provider = normaliseer_spraak_input_provider(
            instellingen.get("spraak_input_provider", DEFAULT_SETTINGS["spraak_input_provider"])
        )

        if provider == "whisper":
            if WHISPER_BESCHIKBAAR:
                try:
                    tekst = herken_spraak_via_whisper(audio)
                    if tekst:
                        return tekst
                except Exception as whisper_fout:
                    print(f"Whisper fout: {whisper_fout}")
            else:
                print("Whisper is niet beschikbaar; fallback naar Google spraakherkenning.")

        tekst = herken_spraak_via_google(recognizer, audio)
        return tekst or None

    except Exception:
        return None

def maak_actie_plan(tekst):
    """Split a sentence into multiple steps so Echo can execute tasks in sequence."""
    cleaned = tekst.lower().strip()
    cleaned = re.sub(r"\s+", " ", cleaned)

    delen = re.split(r"\b(?:and then|after that|next|then|en dan|daarna|vervolgens|dan)\b", cleaned)
    stappen = [deel.strip(" ,.") for deel in delen if deel.strip(" ,.")]

    return stappen if stappen else [cleaned]


def is_explicit_help_request(stap):
    expliciete_hulpvragen = {
        "help",
        "hulp",
        "what can you do",
        "wat kun je",
        "wat kan je",
        "show commands",
        "toon commandos",
        "toon commando's",
        "commands",
        "commando's",
        "commandos",
    }
    return stap in expliciete_hulpvragen


def is_meedenk_vraag(tekst):
    tekst = re.sub(r"\s+", " ", str(tekst or "").lower()).strip()
    triggers = [
        "help me",
        "can you help me",
        "could you help me",
        "i need help",
        "i am stuck",
        "i'm stuck",
        "what should i do",
        "how do i start",
        "how can i",
        "solution",
        "solutions",
        "ideas",
        "advice",
        "plan my",
        "kun je me helpen",
        "kan je me helpen",
        "ik heb hulp nodig",
        "ik zit vast",
        "wat moet ik",
        "hoe kan ik",
        "hoe moet ik",
        "hoe begin ik",
        "denk mee",
        "meedenken",
        "oplossing",
        "oplossingen",
        "idee",
        "ideeen",
        "ideeën",
        "advies",
        "aanpak",
        "strategie",
        "plannen",
    ]
    return any(trigger in tekst for trigger in triggers)


INHOUDELIJKE_VRAAG_PREFIXEN = (
    "what is ",
    "what are ",
    "what does ",
    "what's ",
    "why is ",
    "why does ",
    "why do ",
    "how does ",
    "how do ",
    "how can ",
    "explain ",
    "can you explain ",
    "difference between ",
    "compare ",
    "pros and cons of ",
    "wat is ",
    "wat zijn ",
    "wat betekent ",
    "waarom is ",
    "waarom werkt ",
    "hoe werkt ",
    "hoe kan ",
    "hoe moet ",
    "leg uit ",
    "kun je uitleggen ",
    "kan je uitleggen ",
    "verschil tussen ",
    "vergelijk ",
    "voordelen en nadelen van ",
)

TECHNISCHE_VRAAGWOORDEN = {
    "computer",
    "pc",
    "laptop",
    "software",
    "app",
    "apps",
    "website",
    "web",
    "browser",
    "internet",
    "server",
    "api",
    "database",
    "code",
    "programming",
    "programmeren",
    "python",
    "flask",
    "bug",
    "error",
    "fout",
    "debug",
    "debugging",
    "ram",
    "storage",
    "opslag",
    "cpu",
    "gpu",
    "cache",
    "git",
    "frontend",
    "backend",
    "cloud",
    "security",
    "beveiliging",
    "network",
    "netwerk",
    "wifi",
    "bluetooth",
    "ai",
    "artificial intelligence",
    "kunstmatige intelligentie",
    "machine learning",
    "machinaal leren",
    "algoritme",
    "algorithm",
    "performance",
    "prestaties",
    "slow",
    "traag",
    "langzaam",
    "https",
    "http",
}

KENNIS_ALIASES = {
    "ram": {"ram", "werkgeheugen", "random access memory"},
    "storage": {"storage", "opslag", "ssd", "hdd", "schijfruimte", "diskruimte"},
    "cpu": {"cpu", "processor"},
    "gpu": {"gpu", "videokaart", "graphics card", "grafische kaart"},
    "api": {"api", "application programming interface"},
    "database": {"database", "databank"},
    "frontend": {"frontend", "front end", "client side", "ui", "gebruikersinterface"},
    "backend": {"backend", "back end", "server side", "serverkant"},
    "cache": {"cache", "caching"},
    "debugging": {"debugging", "debuggen", "debug"},
    "git": {"git", "version control", "versiebeheer"},
    "python": {"python"},
    "flask": {"flask"},
    "ai": {"ai", "artificial intelligence", "kunstmatige intelligentie"},
    "machine learning": {"machine learning", "machinaal leren"},
    "http": {"http"},
    "https": {"https"},
}

KENNISKAARTEN = {
    "ram": {
        "summary_en": "RAM is the computer's short-term working memory for data and programs that are active right now.",
        "summary_nl": "RAM is het kortetermijn-werkgeheugen van de computer voor data en programma's die nu actief zijn.",
        "details_en": [
            "It is very fast, but it is cleared when the power goes off.",
            "More RAM mainly helps with multitasking, browsers, large files, and creative apps.",
            "If a system slows down with many apps open, RAM can be the bottleneck.",
        ],
        "details_nl": [
            "Het is erg snel, maar wordt leeg als de stroom uitgaat.",
            "Meer RAM helpt vooral bij multitasking, browsers, grote bestanden en creatieve apps.",
            "Als een systeem traag wordt met veel apps open, kan RAM de bottleneck zijn.",
        ],
    },
    "storage": {
        "summary_en": "Storage keeps files, apps, and system data long-term, even after shutdown.",
        "summary_nl": "Opslag bewaart bestanden, apps en systeemdata langdurig, ook na het afsluiten.",
        "details_en": [
            "Storage is slower than RAM, but it keeps data when power is off.",
            "An SSD is fast storage; an HDD is usually slower but often cheaper per gigabyte.",
            "Storage size affects how much you can keep, while storage speed affects load times.",
        ],
        "details_nl": [
            "Opslag is langzamer dan RAM, maar bewaart data zonder stroom.",
            "Een SSD is snelle opslag; een HDD is meestal trager maar vaak goedkoper per gigabyte.",
            "Opslaggrootte bepaalt hoeveel je kunt bewaren, terwijl opslagsnelheid laadtijden beinvloedt.",
        ],
    },
    "cpu": {
        "summary_en": "The CPU is the general-purpose processor that handles most application logic and operating system work.",
        "summary_nl": "De CPU is de algemene processor die het meeste applicatielogica- en besturingssysteemwerk uitvoert.",
        "details_en": [
            "It is optimized for fast decisions, branching logic, and a wide mix of tasks.",
            "CPU performance matters for responsiveness, compilation, scripting, and many everyday apps.",
            "A stronger CPU helps when the work is varied rather than massively parallel.",
        ],
        "details_nl": [
            "Hij is geoptimaliseerd voor snelle beslissingen, vertakkende logica en een brede mix van taken.",
            "CPU-prestaties zijn belangrijk voor snelheid van reageren, compileren, scripting en veel alledaagse apps.",
            "Een sterkere CPU helpt vooral wanneer het werk gevarieerd is en niet enorm parallel.",
        ],
    },
    "gpu": {
        "summary_en": "The GPU is a specialized processor built for running many similar calculations in parallel.",
        "summary_nl": "De GPU is een gespecialiseerde processor die veel vergelijkbare berekeningen parallel uitvoert.",
        "details_en": [
            "It is excellent for graphics, video processing, simulations, and machine learning workloads.",
            "A GPU shines when the same operation must be repeated across a lot of data at once.",
            "It is not a direct replacement for the CPU because control-heavy tasks still fit the CPU better.",
        ],
        "details_nl": [
            "Hij is sterk in graphics, videobewerking, simulaties en machine-learning-workloads.",
            "Een GPU is op zijn best als dezelfde bewerking tegelijk op veel data moet worden uitgevoerd.",
            "Hij vervangt de CPU niet direct, omdat controlerijke taken beter bij de CPU passen.",
        ],
    },
    "api": {
        "summary_en": "An API is a contract that lets one piece of software request data or behavior from another in a predictable way.",
        "summary_nl": "Een API is een contract waarmee het ene stuk software op voorspelbare manier data of gedrag bij een ander stuk software opvraagt.",
        "details_en": [
            "It defines what you can send, what you get back, and which rules apply.",
            "A good API hides internal complexity so systems can evolve independently.",
            "You use an API when you want reliable integration instead of manual copying or screen interaction.",
        ],
        "details_nl": [
            "Het definieert wat je mag sturen, wat je terugkrijgt en welke regels gelden.",
            "Een goede API verbergt interne complexiteit zodat systemen onafhankelijk kunnen evolueren.",
            "Je gebruikt een API als je betrouwbare integratie wilt in plaats van handmatig kopieren of schermklikken.",
        ],
    },
    "database": {
        "summary_en": "A database is a system for storing, organizing, and querying structured data efficiently.",
        "summary_nl": "Een database is een systeem om gestructureerde data efficient op te slaan, te ordenen en op te vragen.",
        "details_en": [
            "It helps keep data consistent, searchable, and safe across many users or processes.",
            "Relational databases are strong when relationships and transactions matter.",
            "The design of tables, indexes, and queries usually matters as much as the database brand.",
        ],
        "details_nl": [
            "Het helpt data consistent, doorzoekbaar en veilig te houden voor veel gebruikers of processen.",
            "Relationele databases zijn sterk wanneer relaties en transacties belangrijk zijn.",
            "Het ontwerp van tabellen, indexen en queries is meestal net zo belangrijk als het databaseproduct zelf.",
        ],
    },
    "frontend": {
        "summary_en": "The frontend is the part of an app that users see and interact with directly.",
        "summary_nl": "De frontend is het deel van een app dat gebruikers direct zien en bedienen.",
        "details_en": [
            "It focuses on interface, user flow, feedback, accessibility, and client-side behavior.",
            "Frontend work often includes HTML, CSS, JavaScript, rendering, and browser performance.",
            "A strong frontend makes the system understandable and responsive for the user.",
        ],
        "details_nl": [
            "Die draait om interface, gebruikersstroom, feedback, toegankelijkheid en client-side gedrag.",
            "Frontendwerk omvat vaak HTML, CSS, JavaScript, rendering en browserprestaties.",
            "Een sterke frontend maakt het systeem begrijpelijk en responsief voor de gebruiker.",
        ],
    },
    "backend": {
        "summary_en": "The backend is the part of an app that handles data, business rules, security, and system coordination behind the scenes.",
        "summary_nl": "De backend is het deel van een app dat achter de schermen data, bedrijfsregels, beveiliging en systeemcoordinatie afhandelt.",
        "details_en": [
            "It often manages APIs, databases, authentication, and server-side logic.",
            "Backend code decides what is allowed, how data is stored, and how systems communicate.",
            "A strong backend emphasizes correctness, reliability, and maintainability.",
        ],
        "details_nl": [
            "Die beheert vaak API's, databases, authenticatie en server-side logica.",
            "Backendcode bepaalt wat is toegestaan, hoe data wordt opgeslagen en hoe systemen communiceren.",
            "Een sterke backend legt nadruk op correctheid, betrouwbaarheid en onderhoudbaarheid.",
        ],
    },
    "cache": {
        "summary_en": "A cache stores recently used or precomputed data so the system can answer faster without repeating expensive work.",
        "summary_nl": "Een cache bewaart recent gebruikte of vooraf berekende data zodat het systeem sneller kan antwoorden zonder duur werk te herhalen.",
        "details_en": [
            "Caching trades extra memory or storage for lower latency and lower compute cost.",
            "It works best when the same data is requested repeatedly.",
            "The hard part is invalidation: you must know when cached data is too old to trust.",
        ],
        "details_nl": [
            "Caching ruilt extra geheugen of opslag in voor lagere wachttijd en minder rekenwerk.",
            "Het werkt het best wanneer dezelfde data herhaaldelijk wordt opgevraagd.",
            "Het lastige deel is invalidatie: je moet weten wanneer gecachte data te oud is om te vertrouwen.",
        ],
    },
    "debugging": {
        "summary_en": "Debugging is the process of finding the smallest real cause of a problem instead of guessing at symptoms.",
        "summary_nl": "Debugging is het proces van de kleinste echte oorzaak van een probleem vinden in plaats van gokken op symptomen.",
        "details_en": [
            "First reproduce the failure reliably with one concrete input or step sequence.",
            "Then inspect the boundary between expected and actual behavior with logs, prints, or breakpoints.",
            "Fix one likely cause at a time and rerun the same check so you know what changed.",
        ],
        "details_nl": [
            "Reproduceer de fout eerst betrouwbaar met een concrete invoer of stappenreeks.",
            "Inspecteer daarna de grens tussen verwacht en werkelijk gedrag met logs, prints of breakpoints.",
            "Pas steeds een waarschijnlijke oorzaak aan en herhaal dezelfde check, zodat je weet wat veranderde.",
        ],
    },
    "git": {
        "summary_en": "Git is a version-control system that tracks changes in files so you can inspect history, branch safely, and merge work.",
        "summary_nl": "Git is een versiebeheersysteem dat wijzigingen in bestanden bijhoudt, zodat je geschiedenis kunt bekijken, veilig kunt vertakken en werk kunt samenvoegen.",
        "details_en": [
            "A commit records a meaningful snapshot of your project state.",
            "Branches let you experiment without rewriting the main line immediately.",
            "The real value is traceability: you can see what changed, when, and why.",
        ],
        "details_nl": [
            "Een commit legt een betekenisvolle momentopname van je project vast.",
            "Branches laten je experimenteren zonder direct de hoofdlijn te herschrijven.",
            "De echte waarde is traceerbaarheid: je ziet wat veranderde, wanneer en waarom.",
        ],
    },
    "python": {
        "summary_en": "Python is a high-level programming language designed for readable code and fast iteration.",
        "summary_nl": "Python is een programmeertaal op hoog niveau die is ontworpen voor leesbare code en snelle iteratie.",
        "details_en": [
            "It is popular for automation, web development, data work, scripting, and AI tooling.",
            "Python favors simple syntax, which lowers the cost of understanding and changing code.",
            "Its biggest strengths are ecosystem breadth and developer speed.",
        ],
        "details_nl": [
            "Python is populair voor automatisering, webontwikkeling, datawerk, scripting en AI-tools.",
            "Python kiest voor eenvoudige syntax, waardoor code makkelijker te begrijpen en te wijzigen is.",
            "De grootste sterke punten zijn de brede ecosystemen en hoge ontwikkelsnelheid.",
        ],
    },
    "flask": {
        "summary_en": "Flask is a lightweight Python web framework for routing requests, returning responses, and composing web apps with minimal ceremony.",
        "summary_nl": "Flask is een lichtgewicht Python-webframework voor het routeren van requests, teruggeven van responses en opbouwen van webapps met weinig extra ballast.",
        "details_en": [
            "It gives you the core pieces for web apps without forcing a large project structure.",
            "That makes Flask fast to start with, but architecture decisions stay your responsibility.",
            "It is a good fit when you want control and a small surface area.",
        ],
        "details_nl": [
            "Het geeft je de kernonderdelen voor webapps zonder een grote projectstructuur af te dwingen.",
            "Daardoor kun je snel starten, maar architectuurkeuzes blijven jouw verantwoordelijkheid.",
            "Flask past goed wanneer je controle wilt en een klein framework-oppervlak zoekt.",
        ],
    },
    "ai": {
        "summary_en": "AI is the broad field of building systems that perform tasks requiring human-like pattern recognition, decision-making, or language handling.",
        "summary_nl": "AI is het brede vakgebied van systemen bouwen die taken uitvoeren met mensachtige patroonherkenning, besluitvorming of taalverwerking.",
        "details_en": [
            "It includes many methods, from rules and search to neural networks.",
            "AI is about the goal of intelligent behavior, not one single algorithm.",
            "Modern AI often uses data-driven methods, but the field is broader than machine learning alone.",
        ],
        "details_nl": [
            "Het omvat veel methoden, van regels en zoekalgoritmen tot neurale netwerken.",
            "AI gaat over het doel van intelligent gedrag, niet over een enkel algoritme.",
            "Moderne AI gebruikt vaak datagedreven methoden, maar het vakgebied is breder dan alleen machine learning.",
        ],
    },
    "machine learning": {
        "summary_en": "Machine learning is a subset of AI where models learn patterns from data instead of relying only on hand-written rules.",
        "summary_nl": "Machine learning is een deelgebied van AI waarin modellen patronen uit data leren in plaats van alleen handgeschreven regels te volgen.",
        "details_en": [
            "The model improves by seeing examples and adjusting parameters.",
            "Its quality depends heavily on data quality, objective design, and evaluation.",
            "It is useful when the pattern is too complex to encode manually.",
        ],
        "details_nl": [
            "Het model verbetert door voorbeelden te zien en parameters aan te passen.",
            "De kwaliteit hangt sterk af van datakwaliteit, doeldefinitie en evaluatie.",
            "Het is nuttig wanneer het patroon te complex is om handmatig te coderen.",
        ],
    },
    "http": {
        "summary_en": "HTTP is the protocol browsers and servers use to request and deliver web resources.",
        "summary_nl": "HTTP is het protocol waarmee browsers en servers webresources opvragen en leveren.",
        "details_en": [
            "It defines methods like GET and POST, plus headers, status codes, and message bodies.",
            "HTTP itself does not encrypt traffic.",
            "That is why plain HTTP is fine for local testing but risky on public networks.",
        ],
        "details_nl": [
            "Het definieert methodes zoals GET en POST, plus headers, statuscodes en berichtinhoud.",
            "HTTP zelf versleutelt verkeer niet.",
            "Daarom is plain HTTP prima voor lokaal testen maar riskant op publieke netwerken.",
        ],
    },
    "https": {
        "summary_en": "HTTPS is HTTP protected by TLS encryption, which helps keep data private and verifies the server identity.",
        "summary_nl": "HTTPS is HTTP met TLS-versleuteling, wat data helpt beschermen en de identiteit van de server verifieert.",
        "details_en": [
            "It prevents other parties on the network from easily reading or altering traffic.",
            "Browsers also use certificates to confirm they are talking to the intended server.",
            "HTTPS is the default expectation for modern web apps, especially with login or personal data.",
        ],
        "details_nl": [
            "Het voorkomt dat anderen op het netwerk verkeer eenvoudig kunnen lezen of aanpassen.",
            "Browsers gebruiken ook certificaten om te bevestigen dat ze met de bedoelde server praten.",
            "HTTPS is de standaardverwachting voor moderne webapps, zeker bij login of persoonlijke data.",
        ],
    },
}

VERGELIJKINGSKAARTEN = {
    frozenset({"ram", "storage"}): {
        "summary_en": "RAM is temporary fast working space, while storage is long-term space for keeping files and apps.",
        "summary_nl": "RAM is tijdelijk snel werkgeheugen, terwijl opslag langdurige ruimte is voor bestanden en apps.",
        "details_en": [
            "RAM affects how smoothly active work runs right now.",
            "Storage affects how much you can keep and how fast programs load.",
            "Power off clears RAM but not storage.",
        ],
        "details_nl": [
            "RAM bepaalt hoe soepel actief werk nu draait.",
            "Opslag bepaalt hoeveel je kunt bewaren en hoe snel programma's laden.",
            "Bij stroom uit wordt RAM gewist, maar opslag niet.",
        ],
    },
    frozenset({"cpu", "gpu"}): {
        "summary_en": "A CPU is built for flexible general-purpose work, while a GPU is built for huge amounts of similar work in parallel.",
        "summary_nl": "Een CPU is gebouwd voor flexibel algemeen werk, terwijl een GPU is gebouwd voor enorme hoeveelheden vergelijkbaar werk in parallel.",
        "details_en": [
            "The CPU is better for branching logic and mixed workloads.",
            "The GPU is better for graphics, matrix math, and large parallel jobs.",
            "Most systems need both because they solve different performance problems.",
        ],
        "details_nl": [
            "De CPU is beter voor vertakkende logica en gemengde workloads.",
            "De GPU is beter voor graphics, matrixrekenen en grote parallelle taken.",
            "De meeste systemen hebben beide nodig omdat ze verschillende prestatieproblemen oplossen.",
        ],
    },
    frozenset({"frontend", "backend"}): {
        "summary_en": "Frontend handles the user-facing experience, while backend handles logic, data, and coordination behind the scenes.",
        "summary_nl": "De frontend verzorgt de gebruikerservaring aan de voorkant, terwijl de backend de logica, data en coordinatie achter de schermen regelt.",
        "details_en": [
            "Frontend optimizes usability, feedback, and browser behavior.",
            "Backend optimizes correctness, security, and data flow.",
            "They are strongest when designed together around one clear product flow.",
        ],
        "details_nl": [
            "Frontend optimaliseert bruikbaarheid, feedback en browsergedrag.",
            "Backend optimaliseert correctheid, beveiliging en datastromen.",
            "Ze zijn het sterkst als ze samen ontworpen worden rond een duidelijke productflow.",
        ],
    },
    frozenset({"ai", "machine learning"}): {
        "summary_en": "AI is the broad goal of intelligent behavior, while machine learning is one major method inside AI.",
        "summary_nl": "AI is het brede doel van intelligent gedrag, terwijl machine learning een belangrijke methode binnen AI is.",
        "details_en": [
            "Not every AI system uses machine learning.",
            "Machine learning focuses on learning patterns from data.",
            "So machine learning is a subset of AI, not the other way around.",
        ],
        "details_nl": [
            "Niet elk AI-systeem gebruikt machine learning.",
            "Machine learning richt zich op het leren van patronen uit data.",
            "Machine learning is dus een deel van AI, niet andersom.",
        ],
    },
    frozenset({"http", "https"}): {
        "summary_en": "HTTPS is HTTP plus encryption and identity checks, so it is safer for real users and public networks.",
        "summary_nl": "HTTPS is HTTP plus versleuteling en identiteitscontrole, waardoor het veiliger is voor echte gebruikers en publieke netwerken.",
        "details_en": [
            "HTTP sends data without built-in encryption.",
            "HTTPS adds TLS so traffic is harder to read or tamper with.",
            "That is why modern browsers strongly prefer HTTPS.",
        ],
        "details_nl": [
            "HTTP verstuurt data zonder ingebouwde versleuteling.",
            "HTTPS voegt TLS toe zodat verkeer moeilijker te lezen of te manipuleren is.",
            "Daarom geven moderne browsers sterk de voorkeur aan HTTPS.",
        ],
    },
}


def lijst_voor_taal(engels, nederlands):
    return nederlands if gebruik_nederlands() else engels


def schoon_vraag_onderwerp(onderwerp):
    onderwerp = re.sub(r"\s+", " ", str(onderwerp or "")).strip(" .?!,:;")
    onderwerp = re.sub(r"^(?:the|a|an|de|het|een)\s+", "", onderwerp, flags=re.IGNORECASE)
    onderwerp = re.sub(r"\b(?:please|pls|alsjeblieft)\b", "", onderwerp, flags=re.IGNORECASE)
    return re.sub(r"\s+", " ", onderwerp).strip(" ,.?!=")


def bevat_technische_context(tekst):
    return any(woord in tekst for woord in TECHNISCHE_VRAAGWOORDEN)


def is_inhoudelijke_vraag(tekst):
    originele_tekst = re.sub(r"\s+", " ", str(tekst or "")).strip()
    tekst = originele_tekst.lower()
    if not tekst:
        return False

    if any(tekst.startswith(prefix) for prefix in INHOUDELIJKE_VRAAG_PREFIXEN):
        return True

    if re.search(r"\b(?:difference between|verschil tussen|compare|vergelijk|pros and cons|voordelen en nadelen|leg uit|explain)\b", tekst):
        return True

    vraagwoord_aanwezig = bool(re.search(r"\b(?:what|why|how|which|when|wat|waarom|hoe|welke|wanneer)\b", tekst))
    return vraagwoord_aanwezig and ("?" in originele_tekst or bevat_technische_context(tekst))


def bepaal_vraagtype(tekst):
    tekst = re.sub(r"\s+", " ", str(tekst or "").lower()).strip()

    if extraheer_vergelijkingsonderwerpen(tekst):
        return "vergelijking"
    if re.search(r"\b(?:pros and cons|voordelen en nadelen)\b", tekst):
        return "afweging"
    if re.search(r"^(?:why|waarom)\b", tekst):
        return "oorzaak"
    if re.search(r"^(?:how do|how does|how can|hoe werkt|hoe kan|hoe moet)\b", tekst):
        return "aanpak"
    if re.search(r"\b(?:what is|what are|what does|what's|wat is|wat zijn|wat betekent|explain|leg uit|uitleg)\b", tekst):
        return "uitleg"
    return "vraag"


def vind_kennis_sleutels(tekst):
    tekst = re.sub(r"\s+", " ", str(tekst or "").lower()).strip()
    gevonden = []

    alias_sets = sorted(
        KENNIS_ALIASES.items(),
        key=lambda item: max(len(alias) for alias in item[1]),
        reverse=True,
    )

    for sleutel, aliassen in alias_sets:
        if any(re.search(rf"(?<!\w){re.escape(alias)}(?!\w)", tekst) for alias in aliassen):
            gevonden.append(sleutel)

    return gevonden


def normaliseer_kennis_sleutel(onderwerp):
    onderwerp = schoon_vraag_onderwerp(onderwerp).lower()
    for sleutel, aliassen in KENNIS_ALIASES.items():
        if onderwerp == sleutel or onderwerp in aliassen:
            return sleutel

    gevonden = vind_kennis_sleutels(onderwerp)
    return gevonden[0] if gevonden else ""


def extraheer_vergelijkingsonderwerpen(tekst):
    tekst = re.sub(r"\s+", " ", str(tekst or "")).strip()
    patronen = [
        r"(?:difference between|verschil tussen|compare|vergelijk)\s+(?P<a>.+?)\s+(?:and|en|vs\.?|versus)\s+(?P<b>.+)$",
        r"(?P<a>.+?)\s+(?:vs\.?|versus)\s+(?P<b>.+)$",
    ]

    for patroon in patronen:
        match = re.search(patroon, tekst, flags=re.IGNORECASE)
        if match:
            onderwerp_a = schoon_vraag_onderwerp(match.group("a"))
            onderwerp_b = schoon_vraag_onderwerp(match.group("b"))
            if onderwerp_a and onderwerp_b:
                return onderwerp_a, onderwerp_b

    return None


def extraheer_vraag_onderwerp(tekst):
    tekst = re.sub(r"\s+", " ", str(tekst or "")).strip()
    patronen = [
        r"^(?:what is|what are|what does|what's|explain|can you explain|how does|pros and cons of)\s+(?P<onderwerp>.+)$",
        r"^(?:wat is|wat zijn|wat betekent|leg uit|kun je uitleggen|kan je uitleggen|hoe werkt|voordelen en nadelen van)\s+(?P<onderwerp>.+)$",
    ]

    for patroon in patronen:
        match = re.search(patroon, tekst, flags=re.IGNORECASE)
        if match:
            onderwerp = schoon_vraag_onderwerp(match.group("onderwerp"))
            if onderwerp:
                return onderwerp

    return ""


def bouw_inhoudelijk_antwoord(kort_antwoord, kernpunten, uitgevoerde_resultaten=None):
    delen = []

    if uitgevoerde_resultaten:
        delen.append(
            tekst_voor_taal(
                "I already handled this part: ",
                "Dit deel heb ik al voor je gedaan: "
            ) + "; ".join(uitgevoerde_resultaten) + "."
        )

    delen.append(tekst_voor_taal("Short answer: ", "Kort antwoord: ") + kort_antwoord)

    if kernpunten:
        delen.append(
            tekst_voor_taal("Key points: ", "Belangrijke punten: ") +
            " ".join(f"{index}. {punt}" for index, punt in enumerate(kernpunten, start=1))
        )

    return " ".join(delen)


def maak_kenniskaart_antwoord(sleutel, uitgevoerde_resultaten=None):
    kaart = KENNISKAARTEN.get(sleutel)
    if not kaart:
        return ""

    return bouw_inhoudelijk_antwoord(
        lijst_voor_taal(kaart["summary_en"], kaart["summary_nl"]),
        lijst_voor_taal(kaart["details_en"], kaart["details_nl"]),
        uitgevoerde_resultaten,
    )


def maak_vergelijkingsantwoord(onderwerp_a, onderwerp_b, uitgevoerde_resultaten=None):
    sleutel_a = normaliseer_kennis_sleutel(onderwerp_a)
    sleutel_b = normaliseer_kennis_sleutel(onderwerp_b)

    kaart = VERGELIJKINGSKAARTEN.get(frozenset({sleutel_a, sleutel_b})) if sleutel_a and sleutel_b else None
    if kaart:
        return bouw_inhoudelijk_antwoord(
            lijst_voor_taal(kaart["summary_en"], kaart["summary_nl"]),
            lijst_voor_taal(kaart["details_en"], kaart["details_nl"]),
            uitgevoerde_resultaten,
        )

    onderwerp_a = schoon_vraag_onderwerp(onderwerp_a)
    onderwerp_b = schoon_vraag_onderwerp(onderwerp_b)
    return bouw_inhoudelijk_antwoord(
        tekst_voor_taal(
            f"{onderwerp_a} and {onderwerp_b} are best compared by role, constraints, and trade-offs instead of by name alone.",
            f"{onderwerp_a} en {onderwerp_b} vergelijk je het best op rol, randvoorwaarden en afwegingen in plaats van alleen op naam."
        ),
        [
            tekst_voor_taal(
                f"Start with the problem {onderwerp_a} solves and the problem {onderwerp_b} solves.",
                f"Begin met het probleem dat {onderwerp_a} oplost en het probleem dat {onderwerp_b} oplost."
            ),
            tekst_voor_taal(
                "Then compare speed, complexity, cost, and failure risk.",
                "Vergelijk daarna snelheid, complexiteit, kosten en faalrisico."
            ),
            tekst_voor_taal(
                "If you want, ask me to compare them for one concrete use case.",
                "Als je wilt, kan ik ze ook voor een concrete use-case vergelijken."
            ),
        ],
        uitgevoerde_resultaten,
    )


def maak_generiek_technisch_antwoord(tekst, vraagtype, onderwerp, uitgevoerde_resultaten=None):
    tekst = re.sub(r"\s+", " ", str(tekst or "").lower()).strip()
    onderwerp = schoon_vraag_onderwerp(onderwerp or tekst)

    if any(woord in tekst for woord in ["slow", "traag", "langzaam", "performance", "prestaties"]) and any(
        woord in tekst for woord in ["computer", "pc", "laptop", "browser", "app", "apps"]
    ):
        return bouw_inhoudelijk_antwoord(
            tekst_voor_taal(
                "A slow system usually points to a bottleneck in CPU, RAM, storage, or background load.",
                "Een traag systeem wijst meestal op een bottleneck in CPU, RAM, opslag of achtergrondbelasting."
            ),
            [
                tekst_voor_taal(
                    "Check Task Manager first to see which resource is maxed out.",
                    "Controleer eerst Taakbeheer om te zien welke resource volloopt."
                ),
                tekst_voor_taal(
                    "Close startup apps, heavy browser tabs, and other background work before changing hardware.",
                    "Sluit opstartapps, zware browsertabs en ander achtergrondwerk voordat je aan hardware denkt."
                ),
                tekst_voor_taal(
                    "If storage is almost full or the system uses an HDD, that can also make everything feel slow.",
                    "Als opslag bijna vol is of het systeem op een HDD draait, kan dat alles ook traag laten voelen."
                ),
            ],
            uitgevoerde_resultaten,
        )

    if any(woord in tekst for woord in ["bug", "error", "fout", "debug", "debugging", "crash"]):
        return maak_kenniskaart_antwoord("debugging", uitgevoerde_resultaten)

    if vraagtype == "oorzaak":
        return bouw_inhoudelijk_antwoord(
            tekst_voor_taal(
                f"For technical problems around {onderwerp}, the root cause is usually in data, logic, environment, or load.",
                f"Bij technische problemen rond {onderwerp} zit de oorzaak meestal in data, logica, omgeving of belasting."
            ),
            [
                tekst_voor_taal(
                    "Verify the exact input and expected output first.",
                    "Controleer eerst de exacte invoer en verwachte uitvoer."
                ),
                tekst_voor_taal(
                    "Then inspect configuration, state, and recent changes before guessing at fixes.",
                    "Inspecteer daarna configuratie, status en recente wijzigingen voordat je op oplossingen gokt."
                ),
                tekst_voor_taal(
                    "Measure one thing at a time so you know which factor actually explains the problem.",
                    "Meet steeds een factor tegelijk zodat je weet welke oorzaak het probleem echt verklaart."
                ),
            ],
            uitgevoerde_resultaten,
        )

    if vraagtype == "aanpak":
        return bouw_inhoudelijk_antwoord(
            tekst_voor_taal(
                f"The strongest way to approach {onderwerp} is to define the target, choose the smallest test, and iterate from evidence.",
                f"De sterkste aanpak voor {onderwerp} is eerst het doel vastleggen, dan de kleinste test kiezen en daarna itereren op bewijs."
            ),
            [
                tekst_voor_taal(
                    "Write down the exact outcome you want and the main constraint.",
                    "Schrijf de exacte uitkomst op die je wilt en de belangrijkste randvoorwaarde."
                ),
                tekst_voor_taal(
                    "Start with the smallest working slice before you optimize or generalize.",
                    "Begin met het kleinste werkende stukje voordat je optimaliseert of generaliseert."
                ),
                tekst_voor_taal(
                    "Validate with one concrete check so you can tell whether the approach works.",
                    "Valideer met een concrete check zodat je kunt zien of de aanpak werkt."
                ),
            ],
            uitgevoerde_resultaten,
        )

    if vraagtype == "afweging":
        return bouw_inhoudelijk_antwoord(
            tekst_voor_taal(
                f"A good trade-off analysis for {onderwerp} balances speed, complexity, cost, and reliability.",
                f"Een goede afweging voor {onderwerp} balanceert snelheid, complexiteit, kosten en betrouwbaarheid."
            ),
            [
                tekst_voor_taal(
                    "List the biggest advantage first, because that is usually why the option exists.",
                    "Noem eerst het grootste voordeel, want dat is meestal waarom de optie bestaat."
                ),
                tekst_voor_taal(
                    "Then name the main downside or operational cost.",
                    "Noem daarna het grootste nadeel of de operationele prijs."
                ),
                tekst_voor_taal(
                    "Choose based on your real constraint, not on which option sounds more advanced.",
                    "Kies op basis van je echte randvoorwaarde, niet op basis van welke optie geavanceerder klinkt."
                ),
            ],
            uitgevoerde_resultaten,
        )

    return ""


def maak_inhoudelijk_antwoord(tekst, uitgevoerde_resultaten=None):
    if not instellingen.get("agent_modus", True) or not is_inhoudelijke_vraag(tekst):
        return ""

    vergelijking = extraheer_vergelijkingsonderwerpen(tekst)
    if vergelijking:
        return maak_vergelijkingsantwoord(vergelijking[0], vergelijking[1], uitgevoerde_resultaten)

    onderwerp = extraheer_vraag_onderwerp(tekst)
    if onderwerp:
        sleutel = normaliseer_kennis_sleutel(onderwerp)
        if sleutel:
            return maak_kenniskaart_antwoord(sleutel, uitgevoerde_resultaten)

    gevonden_sleutels = vind_kennis_sleutels(tekst)
    if len(gevonden_sleutels) == 1:
        return maak_kenniskaart_antwoord(gevonden_sleutels[0], uitgevoerde_resultaten)

    vraagtype = bepaal_vraagtype(tekst)
    if bevat_technische_context(re.sub(r"\s+", " ", str(tekst or "").lower()).strip()):
        return maak_generiek_technisch_antwoord(tekst, vraagtype, onderwerp or tekst, uitgevoerde_resultaten)

    return ""


REKEN_PREFIXEN = (
    r"calculate",
    r"compute",
    r"solve",
    r"bereken",
    r"reken uit",
    r"what is",
    r"what's",
    r"how much is",
    r"wat is",
    r"hoeveel is",
)

REKEN_BIN_OPS = {
    ast.Add: lambda links, rechts: links + rechts,
    ast.Sub: lambda links, rechts: links - rechts,
    ast.Mult: lambda links, rechts: links * rechts,
    ast.Div: lambda links, rechts: links / rechts,
    ast.FloorDiv: lambda links, rechts: links // rechts,
    ast.Mod: lambda links, rechts: links % rechts,
    ast.Pow: lambda links, rechts: links ** rechts,
}

REKEN_UNARY_OPS = {
    ast.UAdd: lambda waarde: waarde,
    ast.USub: lambda waarde: -waarde,
}

REKEN_CONSTANTEN = {
    "pi": math.pi,
    "e": math.e,
}

REKEN_FUNCTIES = {
    "abs": abs,
    "sqrt": math.sqrt,
    "round": round,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "log": math.log,
}


def extraheer_rekenexpressie(tekst):
    tekst = re.sub(r"\s+", " ", str(tekst or "")).strip()
    if not tekst:
        return ""

    expressie = tekst.strip().rstrip("=? ")
    for prefix in REKEN_PREFIXEN:
        match = re.match(rf"^(?:{prefix})\s+(?P<expressie>.+)$", expressie, flags=re.IGNORECASE)
        if match:
            expressie = match.group("expressie").strip()
            break

    if not re.search(r"\d|\b(?:pi|e|sqrt|abs|round|sin|cos|tan|log|wortel)\b", expressie, flags=re.IGNORECASE):
        return ""

    return expressie


def normaliseer_rekenexpressie(tekst):
    expressie = extraheer_rekenexpressie(tekst)
    if not expressie:
        return ""

    expressie = expressie.lower().strip().rstrip("?.!")
    expressie = re.sub(r"(?<=\d),(?=\d)", ".", expressie)
    expressie = expressie.replace("^", "**")
    expressie = re.sub(r"([0-9a-z_\)\.]+)\s*(?:%|percent|procent)\s+(?:of|van)\s+([0-9a-z_\(\.\-+*/% ]+)", r"(\1/100)*(\2)", expressie)
    expressie = re.sub(r"([0-9a-z_\)\.]+)\s*(?:%|percent|procent)", r"(\1/100)", expressie)

    vervangingen = [
        (r"\bmultiplied by\b", "*"),
        (r"\bdivided by\b", "/"),
        (r"\bto the power of\b", "**"),
        (r"\bpower of\b", "**"),
        (r"\btot de macht\b", "**"),
        (r"\bgedeeld door\b", "/"),
        (r"\bkeer\b", "*"),
        (r"\bmaal\b", "*"),
        (r"\bplus\b", "+"),
        (r"\bmin\b", "-"),
        (r"\bminus\b", "-"),
        (r"\bmodulo\b", "%"),
        (r"\bmod\b", "%"),
        (r"\bsquare root of\b", "sqrt "),
        (r"\bwortel van\b", "sqrt "),
        (r"\bwortel\b", "sqrt"),
    ]
    for patroon, vervanging in vervangingen:
        expressie = re.sub(patroon, vervanging, expressie)

    expressie = re.sub(r"(?<=[\d\)])\s*[x×]\s*(?=[\d\(a-z])", " * ", expressie)
    expressie = re.sub(r"\bsqrt\s+([\d\(][\d\w\s\.+\-*/%()]*)$", r"sqrt(\1)", expressie)
    expressie = re.sub(r"\s+", " ", expressie).strip()
    return expressie


def is_toegestane_reken_ast(node):
    if isinstance(node, ast.Expression):
        return is_toegestane_reken_ast(node.body)

    if isinstance(node, ast.Constant):
        return isinstance(node.value, (int, float))

    if isinstance(node, ast.BinOp):
        return (
            type(node.op) in REKEN_BIN_OPS and
            is_toegestane_reken_ast(node.left) and
            is_toegestane_reken_ast(node.right)
        )

    if isinstance(node, ast.UnaryOp):
        return type(node.op) in REKEN_UNARY_OPS and is_toegestane_reken_ast(node.operand)

    if isinstance(node, ast.Name):
        return node.id.lower() in REKEN_CONSTANTEN

    if isinstance(node, ast.Call):
        return (
            isinstance(node.func, ast.Name) and
            node.func.id.lower() in REKEN_FUNCTIES and
            not node.keywords and
            1 <= len(node.args) <= 2 and
            all(is_toegestane_reken_ast(argument) for argument in node.args)
        )

    return False


def is_veilige_rekenexpressie(expressie):
    try:
        boom = ast.parse(expressie, mode="eval")
    except SyntaxError:
        return False

    return is_toegestane_reken_ast(boom)


def begrens_rekenwaarde(waarde):
    if isinstance(waarde, bool) or not isinstance(waarde, (int, float)):
        raise ValueError("Invalid calculation value")
    if isinstance(waarde, float) and (math.isnan(waarde) or math.isinf(waarde)):
        raise ValueError("Invalid calculation result")
    if abs(float(waarde)) > 1_000_000_000_000:
        raise ValueError("Calculation result is too large")
    return waarde


def evalueer_reken_ast(node):
    if isinstance(node, ast.Expression):
        return evalueer_reken_ast(node.body)

    if isinstance(node, ast.Constant):
        return begrens_rekenwaarde(node.value)

    if isinstance(node, ast.Name):
        return REKEN_CONSTANTEN[node.id.lower()]

    if isinstance(node, ast.UnaryOp):
        operator = REKEN_UNARY_OPS[type(node.op)]
        return begrens_rekenwaarde(operator(evalueer_reken_ast(node.operand)))

    if isinstance(node, ast.BinOp):
        links = evalueer_reken_ast(node.left)
        rechts = evalueer_reken_ast(node.right)
        if isinstance(node.op, ast.Pow) and abs(float(rechts)) > 12:
            raise ValueError("Exponent is too large")
        operator = REKEN_BIN_OPS[type(node.op)]
        return begrens_rekenwaarde(operator(links, rechts))

    if isinstance(node, ast.Call):
        functie_naam = node.func.id.lower()
        argumenten = [evalueer_reken_ast(argument) for argument in node.args]
        if functie_naam == "round" and len(argumenten) == 2:
            argumenten[1] = int(argumenten[1])
        return begrens_rekenwaarde(REKEN_FUNCTIES[functie_naam](*argumenten))

    raise ValueError("Unsupported calculation")


def bereken_veilige_expressie(expressie):
    boom = ast.parse(expressie, mode="eval")
    if not is_toegestane_reken_ast(boom):
        raise ValueError("Unsupported calculation syntax")
    return evalueer_reken_ast(boom)


def formatteer_reken_resultaat(waarde):
    if isinstance(waarde, float):
        if abs(waarde) < 1e-12:
            return "0"
        if waarde.is_integer():
            return str(int(waarde))
        return f"{waarde:.10f}".rstrip("0").rstrip(".")
    return str(waarde)


def maak_reken_actie(originele_stap):
    expressie = normaliseer_rekenexpressie(originele_stap)
    if not expressie or not is_veilige_rekenexpressie(expressie):
        return ""
    return f"calculate::{expressie}"


def online_ai_beschikbaar():
    return bool(instellingen.get("online_ai_modus", True) and huidige_ai_api_key())


def ai_request_timeout_seconden(basis_url):
    override = os.environ.get("OPENAI_TIMEOUT_SECONDS", "").strip()
    if override:
        try:
            return max(5, int(float(override)))
        except ValueError:
            pass

    basis_url = str(basis_url or "").lower()
    if "127.0.0.1" in basis_url or "localhost" in basis_url:
        return 180
    return 25


def vraag_online_ai_bericht(berichten, temperatuur=0.4, extra_payload=None, return_raw=False):
    api_key = huidige_ai_api_key()
    if not api_key:
        return {} if return_raw else ""

    basis_url = model_basis_url().rstrip("/")
    model = huidige_ai_model_naam()
    provider = model_provider_naam(basis_url)
    timeout = ai_request_timeout_seconden(basis_url)

    payload = {
        "temperature": temperatuur,
        "messages": berichten,
    }
    if extra_payload:
        payload.update(extra_payload)

    headers = {"Content-Type": "application/json"}
    request_url = ""

    if provider == "azure-openai":
        deployment = azure_openai_deployment(model)
        if not deployment:
            raise ValueError("Azure OpenAI deployment is missing")

        endpoint = azure_openai_endpoint() or basis_url
        endpoint = endpoint.rstrip("/")
        if endpoint.endswith("/openai"):
            endpoint_basis = endpoint
        else:
            endpoint_basis = endpoint + "/openai"

        api_version = azure_openai_api_version()
        request_url = (
            f"{endpoint_basis}/deployments/{quote_plus(deployment)}/chat/completions"
            f"?api-version={quote_plus(api_version)}"
        )
        headers["api-key"] = api_key
    else:
        payload["model"] = model
        request_url = f"{basis_url}/chat/completions"
        headers["Authorization"] = f"Bearer {api_key}"

    request = urllib.request.Request(
        request_url,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )

    with urllib.request.urlopen(request, timeout=timeout) as response:
        data = json.loads(response.read().decode("utf-8"))

    if return_raw:
        return data

    keuzes = data.get("choices") or []
    if not keuzes:
        return ""

    bericht = keuzes[0].get("message", {}).get("content", "")
    return str(bericht or "").strip()


def vraag_online_ai_chat(tekst, uitgevoerde_resultaten=None):
    systeem_prompt = tekst_voor_taal(
        "You are Echo, a concise desktop assistant. Answer clearly and practically. If the user asks an open-ended question, explain it directly. If they ask for a plan, give a short actionable plan. Never claim you executed computer actions unless explicit results are provided in the context.",
        "Je bent Echo, een beknopte desktopassistent. Antwoord duidelijk en praktisch. Als de gebruiker een open vraag stelt, leg het direct uit. Als de gebruiker om een plan vraagt, geef een kort uitvoerbaar plan. Doe nooit alsof je computeracties hebt uitgevoerd tenzij expliciete resultaten in de context staan."
    )

    context_blokken = []
    agent_context = context_voor_ai_agent(tekst)
    if agent_context:
        context_blokken.append(agent_context)

    if uitgevoerde_resultaten:
        context_blokken.append(tekst_voor_taal(
            "Already executed: ",
            "Al uitgevoerd: "
        ) + "; ".join(uitgevoerde_resultaten))

    berichten = [
        {"role": "system", "content": systeem_prompt},
        {
            "role": "user",
            "content": ("\n\n".join(context_blokken) + "\n\n" if context_blokken else "") + str(tekst or "").strip(),
        },
    ]
    return vraag_online_ai_bericht(berichten, temperatuur=0.4)


def maak_online_ai_antwoord(tekst, uitgevoerde_resultaten=None):
    if not online_ai_beschikbaar():
        return ""

    try:
        return vraag_online_ai_chat(tekst, uitgevoerde_resultaten)
    except (urllib.error.URLError, TimeoutError, ValueError, KeyError, json.JSONDecodeError):
        return ""


AI_AGENT_BEKENDE_PREFIXEN = (
    "open browser url::",
    "open website ",
    "open websites ",
    "open new tab ",
    "open new tabs ",
    "search google ",
    "search youtube ",
    "calculate::",
    "browser ",
    "timer ",
    "reminder ",
    "task ",
    "agenda show",
    "create folder",
    "open folder ",
    "open file ",
    "open setting ",
    "open app ",
    "open app raw::",
    "open notepad",
    "open calculator",
    "open paint",
    "open command prompt",
    "open file explorer",
    "create file ",
    "list folder::",
    "read file::",
    "summarize file::",
    "append file::",
    "overwrite file::",
    "rewrite file::",
    "search files::",
    "copy path::",
    "move path::",
    "rename path::",
    "delete path::",
    "system info",
    "system scan start",
    "system scan status",
    "battery status",
    "disk space",
    "ip address",
    "current time",
    "run macro ",
    "mouse ",
    "type text::",
    "press key::",
    "press hotkey::",
    "take screenshot",
    "volume ",
    "window ",
    "wifi ",
    "bluetooth ",
)

AI_AGENT_MAX_TOOL_CALLS = 4


def ai_agent_tool_schema():
    return [
        {
            "type": "function",
            "function": {
                "name": "open_youtube",
                "description": "Open YouTube in the browser.",
                "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "open_google",
                "description": "Open Google in the browser.",
                "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "open_website",
                "description": "Open a website or known site keyword like gmail, github, or netflix.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "target": {"type": "string", "description": "Website URL or site keyword."},
                    },
                    "required": ["target"],
                    "additionalProperties": False,
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "search_google",
                "description": "Search Google for a query.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query."},
                    },
                    "required": ["query"],
                    "additionalProperties": False,
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "search_youtube",
                "description": "Search YouTube for a query.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query."},
                    },
                    "required": ["query"],
                    "additionalProperties": False,
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "create_folder",
                "description": "Create a folder in the current workspace or system path.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Folder name or path."},
                    },
                    "required": ["name"],
                    "additionalProperties": False,
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "create_file",
                "description": "Create an empty file path.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "File path to create."},
                    },
                    "required": ["path"],
                    "additionalProperties": False,
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "list_folder",
                "description": "List files in a folder.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Folder path."},
                    },
                    "required": ["path"],
                    "additionalProperties": False,
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "read_file",
                "description": "Read a text file preview.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "File path."},
                    },
                    "required": ["path"],
                    "additionalProperties": False,
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "append_file",
                "description": "Append plain text to a file.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "File path."},
                        "text": {"type": "string", "description": "Text to append."},
                    },
                    "required": ["path", "text"],
                    "additionalProperties": False,
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "search_files",
                "description": "Search workspace files by keyword.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Keyword for file search."},
                    },
                    "required": ["query"],
                    "additionalProperties": False,
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "calculate_expression",
                "description": "Safely calculate a math expression.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "expression": {"type": "string", "description": "Math expression."},
                    },
                    "required": ["expression"],
                    "additionalProperties": False,
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "system_status",
                "description": "Get local system status.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "kind": {
                            "type": "string",
                            "enum": ["system", "battery", "disk", "ip", "time", "scan"],
                            "description": "Type of status to retrieve.",
                        },
                    },
                    "required": ["kind"],
                    "additionalProperties": False,
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "run_echo_action",
                "description": "Execute one supported Echo action string directly.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {"type": "string", "description": "One supported Echo action command."},
                    },
                    "required": ["action"],
                    "additionalProperties": False,
                },
            },
        },
    ]


def parse_ai_tool_arguments(arguments):
    if isinstance(arguments, dict):
        return arguments

    argument_tekst = str(arguments or "").strip()
    if not argument_tekst:
        return {}

    try:
        data = json.loads(argument_tekst)
    except Exception:
        return {}

    return data if isinstance(data, dict) else {}


def actie_uit_ai_tool_call(tool_call):
    if not isinstance(tool_call, dict):
        return ""

    functie = tool_call.get("function")
    if not isinstance(functie, dict):
        return ""

    naam = str(functie.get("name") or "").strip()
    args = parse_ai_tool_arguments(functie.get("arguments"))

    if naam == "open_youtube":
        return "open youtube"
    if naam == "open_google":
        return "open google"
    if naam == "open_website":
        target = str(args.get("target") or "").strip()
        return f"open website {target}" if target else ""
    if naam == "search_google":
        query = str(args.get("query") or "").strip()
        return f"search google {query}" if query else ""
    if naam == "search_youtube":
        query = str(args.get("query") or "").strip()
        return f"search youtube {query}" if query else ""
    if naam == "create_folder":
        foldernaam = str(args.get("name") or "").strip()
        return f"create folder {foldernaam}" if foldernaam else ""
    if naam == "create_file":
        pad = str(args.get("path") or "").strip()
        return f"create file {pad}" if pad else ""
    if naam == "list_folder":
        pad = str(args.get("path") or "").strip()
        return f"list folder::{pad}" if pad else ""
    if naam == "read_file":
        pad = str(args.get("path") or "").strip()
        return f"read file::{pad}" if pad else ""
    if naam == "append_file":
        pad = str(args.get("path") or "").strip()
        tekst = str(args.get("text") or "").strip()
        return f"append file::{pad}||{tekst}" if pad and tekst else ""
    if naam == "search_files":
        zoekterm = str(args.get("query") or "").strip()
        return f"search files::{zoekterm}" if zoekterm else ""
    if naam == "calculate_expression":
        expressie = str(args.get("expression") or "").strip()
        return f"calculate::{expressie}" if expressie else ""
    if naam == "system_status":
        status_soort = str(args.get("kind") or "system").strip().lower()
        mapping = {
            "system": "system info",
            "battery": "battery status",
            "disk": "disk space",
            "ip": "ip address",
            "time": "current time",
            "scan": "system scan status",
        }
        return mapping.get(status_soort, "system info")
    if naam == "run_echo_action":
        return str(args.get("action") or "").strip()

    return ""


def schoon_json_antwoord(tekst):
    opgeschoond = str(tekst or "").strip()
    opgeschoond = re.sub(r"^```(?:json)?\s*", "", opgeschoond, flags=re.IGNORECASE)
    opgeschoond = re.sub(r"\s*```$", "", opgeschoond)

    start = opgeschoond.find("{")
    einde = opgeschoond.rfind("}")
    if start != -1 and einde != -1 and einde >= start:
        return opgeschoond[start:einde + 1]

    return opgeschoond


def zoekwoorden_uit_tekst(tekst):
    gevonden = []
    for woord in re.findall(r"[a-z0-9_]{3,}", str(tekst or "").lower()):
        if woord in DOCUMENT_CONTEXT_STOPWOORDEN or woord in gevonden:
            continue
        gevonden.append(woord)
    return gevonden[:12]


def iter_document_context_bestanden(basis_pad=None):
    basis_pad = Path(basis_pad or Path.cwd())
    for pad in basis_pad.rglob("*"):
        if not pad.is_file():
            continue
        if any(deel in DOCUMENT_CONTEXT_GENEGEERDE_MAPNAMEN for deel in pad.parts):
            continue
        if pad.suffix.lower() not in DOCUMENT_CONTEXT_EXTENSIES:
            continue
        try:
            if pad.stat().st_size > MAX_DOCUMENT_BESTANDSGROOTTE:
                continue
        except OSError:
            continue
        yield pad


def relatief_document_pad(pad):
    try:
        return Path(pad).resolve().relative_to(Path.cwd().resolve()).as_posix()
    except Exception:
        return Path(pad).name


def beste_document_snippet(inhoud, zoekwoorden):
    regels = inhoud.splitlines()
    beste_index = -1
    beste_score = 0

    for index, regel in enumerate(regels):
        regel_lower = regel.lower()
        score = sum(1 for woord in zoekwoorden if woord in regel_lower)
        if score > beste_score:
            beste_index = index
            beste_score = score

    if beste_index == -1:
        return 0, ""

    begin = max(0, beste_index - 1)
    einde = min(len(regels), beste_index + 2)
    snippet = " ".join(regel.strip() for regel in regels[begin:einde] if regel.strip())
    return beste_index + 1, opschonen_korte_tekst(snippet, max_lengte=280)


def document_context_snippets(tekst, max_snippets=MAX_DOCUMENT_SNIPPETS):
    zoekwoorden = zoekwoorden_uit_tekst(tekst)
    if not zoekwoorden:
        return []

    kandidaten = []
    for pad in iter_document_context_bestanden():
        try:
            inhoud = pad.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        inhoud_lower = inhoud.lower()
        hits = [woord for woord in zoekwoorden if woord in inhoud_lower]
        if not hits:
            continue

        lijnnummer, snippet = beste_document_snippet(inhoud, hits)
        if not snippet:
            continue

        score = len(hits) * 10 + sum(inhoud_lower.count(woord) for woord in hits[:5])
        if Path(pad).name.lower().startswith("readme"):
            score += 5
        kandidaten.append((score, relatief_document_pad(pad), lijnnummer, snippet))

    kandidaten.sort(key=lambda item: item[0], reverse=True)
    snippets = []
    for _, pad, lijnnummer, snippet in kandidaten[:max_snippets]:
        snippets.append(f"- {pad}:{lijnnummer} {snippet}")
    return snippets


def blok_recente_gesprekken():
    gesprekken = GESPREK_CONTEXT.get("recente_gesprekken", [])
    if not gesprekken:
        return ""

    regels = [tekst_voor_taal("Recent conversation:", "Recent gesprek:")]
    for beurt in gesprekken[-4:]:
        regels.append(tekst_voor_taal("User", "Gebruiker") + ": " + beurt["user"])
        regels.append("Echo: " + beurt["assistant"])
    return "\n".join(regels)


def blok_document_context(tekst):
    snippets = document_context_snippets(tekst)
    if not snippets:
        return ""
    return tekst_voor_taal("Relevant workspace snippets:", "Relevante workspace-fragmenten:") + "\n" + "\n".join(snippets)


def context_voor_ai_agent(tekst=""):
    regels = [
        tekst_voor_taal("Language mode", "Taalmodus") + f": {instellingen.get('taal', DEFAULT_SETTINGS['taal'])}",
        tekst_voor_taal("Advanced computer control", "Geavanceerde computerbesturing") + ": " + (
            tekst_voor_taal("enabled", "ingeschakeld") if instellingen.get("computerbesturing_toestaan", False) else tekst_voor_taal("disabled", "uitgeschakeld")
        ),
        tekst_voor_taal("Automation mode", "Automation-modus") + ": " + (
            tekst_voor_taal("active", "actief") if automatisering_actief() else tekst_voor_taal("inactive", "inactief")
        ),
    ]

    if GESPREK_CONTEXT.get("laatste_plan"):
        regels.append(
            tekst_voor_taal("Last plan", "Laatste plan") + ": " + "; ".join(GESPREK_CONTEXT["laatste_plan"])
        )
    if GESPREK_CONTEXT.get("laatste_resultaten"):
        regels.append(
            tekst_voor_taal("Last results", "Laatste resultaten") + ": " + "; ".join(GESPREK_CONTEXT["laatste_resultaten"])
        )

    recente_gesprekken = blok_recente_gesprekken()
    if recente_gesprekken:
        regels.append(recente_gesprekken)

    langetermijn_geheugen = blok_langetermijn_geheugen()
    if langetermijn_geheugen:
        regels.append(langetermijn_geheugen)

    planning_context = blok_planning_context()
    if planning_context:
        regels.append(planning_context)

    document_context = blok_document_context(tekst)
    if document_context:
        regels.append(document_context)

    return "\n".join(regels)


def actie_is_uitvoerbaar_door_echo(actie):
    genormaliseerde_actie = normaliseer_actie(str(actie or "").strip())
    if not genormaliseerde_actie:
        return "", False

    if genormaliseerde_actie in DANGEROUS_SYSTEM_ACTIONS:
        return genormaliseerde_actie, True

    if genormaliseerde_actie in {"confirm pending action", "cancel pending action", "help", "open google", "open youtube"}:
        return genormaliseerde_actie, True

    if genormaliseerde_actie.startswith(AI_AGENT_BEKENDE_PREFIXEN):
        return genormaliseerde_actie, True

    return genormaliseerde_actie, actie_prioriteit(genormaliseerde_actie) < 9


def categoriseer_actie(actie):
    actie = str(actie or "").strip().lower()
    if not actie:
        return "general"

    if actie.startswith(("task ", "timer ", "reminder ", "agenda show")):
        return "planner"

    if actie.startswith((
        "browser ",
        "open browser url::",
        "open website ",
        "open websites ",
        "open new tab ",
        "open new tabs ",
        "search google ",
        "search youtube ",
    )):
        return "browser"

    if actie.startswith((
        "create file ",
        "create folder",
        "open folder ",
        "open file ",
        "list folder::",
        "read file::",
        "summarize file::",
        "append file::",
        "overwrite file::",
        "rewrite file::",
        "search files::",
        "copy path::",
        "move path::",
        "rename path::",
        "delete path::",
    )):
        return "workspace"

    if actie.startswith((
        "run macro ",
        "mouse ",
        "type text::",
        "press key::",
        "press hotkey::",
        "take screenshot",
        "volume ",
        "window ",
        "wifi ",
        "bluetooth ",
    )):
        return "automation"

    if actie.startswith((
        "open setting ",
        "open app ",
        "open app raw::",
        "open notepad",
        "open calculator",
        "open paint",
        "open command prompt",
        "open file explorer",
        "system info",
        "system scan start",
        "system scan status",
        "battery status",
        "disk space",
        "ip address",
        "current time",
        "calculate::",
    )):
        return "system"

    return "general"


def categoriseer_verzoek_tekst(tekst):
    tekst = re.sub(r"\s+", " ", str(tekst or "").lower()).strip()
    if not tekst:
        return "general"

    if any(woord in tekst for woord in ("timer", "remind", "herinner", "agenda", "task", "taak", "planning", "plan mijn", "plan my")):
        return "planner"
    if any(woord in tekst for woord in ("page", "pagina", "browser", "chrome", "edge", "tab", "website", "url", "formulier", "form")):
        return "browser"
    if any(woord in tekst for woord in ("bestand", "file", "folder", "map", "readme", "zoek", "search", "rename", "copy", "move", "delete", "rewrite", "herschrijf", "overschrijf", "append")):
        return "workspace"
    if any(woord in tekst for woord in ("automation", "screenshot", "window", "venster", "wifi", "bluetooth", "volume", "mouse", "muis", "keyboard", "toets", "macro", "discord", "steam", "whatsapp", "vscode")):
        return "automation"
    if any(woord in tekst for woord in ("why", "what", "how", "compare", "explain", "leg uit", "waarom", "wat is", "hoe werkt", "vergelijk")):
        return "answer"
    return "general"


def tekst_lijkt_actiegericht(tekst):
    tekst = re.sub(r"\s+", " ", str(tekst or "").lower()).strip()
    if not tekst:
        return False

    patronen = (
        r"\b(open|start|launch|create|make|read|summarize|append|overwrite|rewrite|search|copy|move|rename|delete|list|show|set|remind|fill|submit|switch|take|mute|maximize|close|save|press|type|drag)\b",
        r"\b(open|maak|lees|vat|voeg|overschrijf|herschrijf|zoek|kopieer|verplaats|hernoem|verwijder|toon|zet|herinner|vul|verzend|wissel|sluit|sla op|druk|typ|sleep)\b",
    )
    return any(re.search(patroon, tekst) for patroon in patronen)


def analyseer_verzoek_routering(tekst):
    ruwe_plan = maak_actie_plan(tekst)
    verrijkt_plan = verrijk_plan_met_context(tekst, ruwe_plan)
    genormaliseerd_plan = [genormaliseerde_stap for stap in verrijkt_plan if (genormaliseerde_stap := normaliseer_actie(stap))]

    uitvoerbare_acties = []
    for stap in genormaliseerd_plan:
        genormaliseerde_actie, uitvoerbaar = actie_is_uitvoerbaar_door_echo(stap)
        if uitvoerbaar and genormaliseerde_actie:
            uitvoerbare_acties.append(genormaliseerde_actie)

    vraagachtig = bool(is_inhoudelijke_vraag(tekst) or is_meedenk_vraag(tekst))
    actieachtig = bool(uitvoerbare_acties or tekst_lijkt_actiegericht(tekst))
    categorie = categoriseer_actie(uitvoerbare_acties[0]) if uitvoerbare_acties else categoriseer_verzoek_tekst(tekst)

    if actieachtig and vraagachtig:
        intent = "hybrid"
    elif actieachtig:
        intent = "action"
    else:
        intent = "answer"

    if intent == "answer":
        voorkeur_tool = "builtin_answer"
    elif uitvoerbare_acties:
        voorkeur_tool = "local_plan"
    elif online_ai_beschikbaar() and instellingen.get("ai_agent_primair", True):
        voorkeur_tool = "online_action_planner"
    else:
        voorkeur_tool = "fallback"

    return {
        "intent": intent,
        "tool": voorkeur_tool,
        "category": categorie,
        "plan": uitvoerbare_acties,
        "question_like": vraagachtig,
        "action_like": actieachtig,
    }


def vraag_online_ai_agent_acties(tekst, routering=None):
    routering = routering or analyseer_verzoek_routering(tekst)
    systeem_prompt = tekst_voor_taal(
        "You are Echo's tool orchestrator. For action requests, call the provided tools instead of describing what to do. You may call up to 4 tools. Use a short content reply only for useful context. If no tool is needed, provide a concise direct reply.",
        "Je bent Echo's tool-orkestrator. Voor actieverzoeken roep je de beschikbare tools aan in plaats van uit te leggen wat je zou doen. Je mag maximaal 4 tools aanroepen. Gebruik een korte tekstreactie alleen als extra context nuttig is. Als er geen tool nodig is, geef dan een kort direct antwoord."
    )

    mogelijkheden = tekst_voor_taal(
        "Use tools for concrete actions. Prefer open_youtube or open_website when users ask to watch videos. Use run_echo_action only when no specific tool fits.",
        "Gebruik tools voor concrete acties. Gebruik bij videoverzoeken bij voorkeur open_youtube of open_website. Gebruik run_echo_action alleen als geen specifieke tool past."
    )

    berichten = [
        {"role": "system", "content": systeem_prompt},
        {
            "role": "user",
            "content": (
                context_voor_ai_agent(tekst) + "\n\n" +
                mogelijkheden + "\n\n" +
                tekst_voor_taal("Chosen intent: action", "Gekozen intentie: actie") + "\n" +
                tekst_voor_taal("Chosen tool: local echo actions", "Gekozen tool: lokale Echo-acties") + "\n" +
                tekst_voor_taal("Detected category: ", "Gedetecteerde categorie: ") + routering.get("category", "general") + "\n\n" +
                tekst_voor_taal("User request: ", "Gebruikersverzoek: ") + str(tekst or "").strip()
            ),
        },
    ]

    antwoord_data = vraag_online_ai_bericht(
        berichten,
        temperatuur=0.2,
        extra_payload={
            "tools": ai_agent_tool_schema(),
            "tool_choice": "auto",
        },
        return_raw=True,
    )
    if not isinstance(antwoord_data, dict):
        return None

    keuzes = antwoord_data.get("choices") or []
    if not keuzes:
        return None

    bericht = keuzes[0].get("message") or {}
    reply = str(bericht.get("content") or "").strip()

    tool_calls = bericht.get("tool_calls") or []
    ruwe_acties = []
    if isinstance(tool_calls, list):
        for tool_call in tool_calls[:AI_AGENT_MAX_TOOL_CALLS]:
            actie = actie_uit_ai_tool_call(tool_call)
            if actie:
                ruwe_acties.append(actie)

    if not ruwe_acties and reply:
        try:
            fallback_beslissing = json.loads(schoon_json_antwoord(reply))
        except Exception:
            fallback_beslissing = None

        if isinstance(fallback_beslissing, dict):
            fallback_reply = str(fallback_beslissing.get("reply") or "").strip()
            fallback_acties = fallback_beslissing.get("actions") or []
            if isinstance(fallback_acties, list):
                for kandidaat in fallback_acties[:AI_AGENT_MAX_TOOL_CALLS]:
                    kandidaat_tekst = str(kandidaat or "").strip()
                    if kandidaat_tekst:
                        ruwe_acties.append(kandidaat_tekst)
            if fallback_reply:
                reply = fallback_reply

    if ruwe_acties or reply:
        return {
            "reply": reply,
            "actions": ruwe_acties,
        }

    return None


def maak_best_mogelijke_antwoordtekst(tekst, uitgevoerde_resultaten=None):
    inhoudelijk_bericht = maak_inhoudelijk_antwoord(tekst, uitgevoerde_resultaten)
    if inhoudelijk_bericht:
        return "builtin_answer", inhoudelijk_bericht

    online_ai_bericht = maak_online_ai_antwoord(tekst, uitgevoerde_resultaten)
    if online_ai_bericht:
        return "online_answer", online_ai_bericht

    meedenk_bericht = maak_meedenk_antwoord(tekst, uitgevoerde_resultaten)
    if meedenk_bericht:
        return "guided_answer", meedenk_bericht

    return "", ""


def combineer_agent_bericht(reply, resultaten):
    reply = str(reply or "").strip()
    if reply and resultaten:
        return reply + " " + tekst_voor_taal("Results: ", "Resultaten: ") + "; ".join(resultaten)
    if reply:
        return reply
    if len(resultaten) > 1:
        return tekst_voor_taal("Plan completed: ", "Plan uitgevoerd: ") + "; ".join(resultaten)
    return resultaten[0] if resultaten else ""


def probeer_online_ai_agent(tekst, routering=None):
    if not online_ai_beschikbaar() or not instellingen.get("ai_agent_primair", True):
        return None

    routering = routering or analyseer_verzoek_routering(tekst)
    if routering.get("intent") not in {"action", "hybrid"}:
        return None

    try:
        beslissing = vraag_online_ai_agent_acties(tekst, routering)
    except (urllib.error.URLError, TimeoutError, ValueError, KeyError, json.JSONDecodeError):
        return None

    if not beslissing:
        return None

    reply = str(beslissing.get("reply", "")).strip()

    ruwe_acties = beslissing.get("actions") or []
    if not isinstance(ruwe_acties, list):
        return None

    uitvoerbare_acties = []
    for ruwe_actie in ruwe_acties[:4]:
        genormaliseerde_actie, is_uitvoerbaar = actie_is_uitvoerbaar_door_echo(ruwe_actie)
        if is_uitvoerbaar and genormaliseerde_actie:
            uitvoerbare_acties.append(genormaliseerde_actie)

    if not uitvoerbare_acties:
        return {"bericht": reply, "plan": [], "resultaten": []} if reply else None

    resultaten = [voer_enkele_actie_uit(actie) for actie in uitvoerbare_acties]
    bericht = combineer_agent_bericht(reply, resultaten)
    if not bericht:
        return None

    return {
        "bericht": bericht,
        "plan": uitvoerbare_acties,
        "resultaten": resultaten,
    }


def voer_plan_uit(plan):
    resultaten = []
    bekende_stappen = []
    bekende_resultaten = []
    onbekende_actie = kan_niet_oproepen_bericht()

    for stap in plan:
        resultaat = voer_enkele_actie_uit(stap)
        resultaten.append(resultaat)
        if resultaat != onbekende_actie:
            bekende_stappen.append(stap)
            bekende_resultaten.append(resultaat)

    if len(plan) > 1:
        bericht = tekst_voor_taal("Plan completed: ", "Plan uitgevoerd: ") + "; ".join(resultaten)
    else:
        bericht = resultaten[0] if resultaten else onbekende_actie

    return {
        "bericht": bericht,
        "resultaten": resultaten,
        "bekende_stappen": bekende_stappen,
        "bekende_resultaten": bekende_resultaten,
        "onbekende_actie": onbekende_actie,
        "heeft_onbekende_stap": onbekende_actie in resultaten or not plan,
    }


def maak_meedenk_antwoord(tekst, uitgevoerde_resultaten=None):
    if not instellingen.get("agent_modus", True) or not is_meedenk_vraag(tekst):
        return ""

    tekst = re.sub(r"\s+", " ", str(tekst or "").lower()).strip()
    stappen = []

    if any(woord in tekst for woord in ["plan", "planning", "study", "studie", "huiswerk", "exam", "toets", "deadline", "taak", "project", "focus"]):
        stappen = [
            tekst_voor_taal(
                "Choose one clear goal for this moment instead of the whole problem.",
                "Kies eerst één helder doel voor nu in plaats van het hele probleem tegelijk."
            ),
            tekst_voor_taal(
                "Break it into three small steps and start with a ten-minute first action.",
                "Breek het op in drie kleine stappen en begin met een eerste actie van tien minuten."
            ),
            tekst_voor_taal(
                "If you want, ask me to open Notepad so you can turn that into a simple plan.",
                "Als je wilt, vraag mij om Kladblok te openen zodat je daar meteen een simpel plan kunt maken."
            ),
        ]
    elif any(woord in tekst for woord in ["folder", "map", "file", "bestand", "desktop", "downloads", "organize", "organiseer", "opruimen"]):
        stappen = [
            tekst_voor_taal(
                "Start with three main groups, for example work, personal, and temporary.",
                "Begin met drie hoofdgroepen, bijvoorbeeld werk, prive en tijdelijk."
            ),
            tekst_voor_taal(
                "Move only the biggest or newest files first so the task stays small.",
                "Verplaats eerst alleen de grootste of nieuwste bestanden zodat het klein blijft."
            ),
            tekst_voor_taal(
                "If you want, I can create the first folders for you.",
                "Als je wilt, kan ik de eerste mappen alvast voor je aanmaken."
            ),
        ]
    elif any(woord in tekst for woord in ["google", "youtube", "search", "zoek", "research", "informatie", "learn", "leren", "uitleg"]):
        stappen = [
            tekst_voor_taal(
                "Turn your problem into one clear search question first.",
                "Maak van je probleem eerst één duidelijke zoekvraag."
            ),
            tekst_voor_taal(
                "Compare two sources and note the best next action instead of collecting too much information.",
                "Vergelijk twee bronnen en noteer daarna de beste volgende stap in plaats van te veel informatie te verzamelen."
            ),
            tekst_voor_taal(
                "If you want, I can open Google or YouTube for that next step.",
                "Als je wilt, kan ik Google of YouTube openen voor die volgende stap."
            ),
        ]
    elif any(woord in tekst for woord in ["write", "schrijf", "email", "mail", "tekst", "verslag", "note", "notitie", "idee", "brainstorm"]):
        stappen = [
            tekst_voor_taal(
                "Start with a rough outline: goal, three key points, and the next sentence to write.",
                "Begin met een ruwe opzet: doel, drie kernpunten en de eerstvolgende zin die je wilt schrijven."
            ),
            tekst_voor_taal(
                "Do not try to make it perfect in the first pass.",
                "Probeer het niet meteen perfect te maken in de eerste versie."
            ),
            tekst_voor_taal(
                "If you want, I can open Notepad so you can capture the outline immediately.",
                "Als je wilt, kan ik Kladblok openen zodat je de opzet meteen kunt vastleggen."
            ),
        ]
    else:
        stappen = [
            tekst_voor_taal(
                "Tell me your goal in one sentence.",
                "Vertel mij je doel in één zin."
            ),
            tekst_voor_taal(
                "Then tell me what is blocking you right now.",
                "Vertel daarna waar je nu precies op vastloopt."
            ),
            tekst_voor_taal(
                "Then I can turn that into a small next-step plan with you.",
                "Dan kan ik dat samen met jou omzetten in een klein plan met volgende stappen."
            ),
        ]

    delen = []
    if uitgevoerde_resultaten:
        delen.append(
            tekst_voor_taal(
                "I already handled this part: ",
                "Dit deel heb ik al voor je gedaan: "
            ) + "; ".join(uitgevoerde_resultaten) + "."
        )

    delen.append(
        tekst_voor_taal(
            "I am thinking along with you. A practical approach is: ",
            "Ik denk met je mee. Een praktische aanpak is: "
        ) + " ".join(f"{index}. {stap}" for index, stap in enumerate(stappen, start=1))
    )

    return " ".join(delen)


SITE_ALIASES = {
    "youtube": {"youtube", "yt"},
    "google": {"google"},
    "github": {"github", "git hub"},
    "gmail": {"gmail", "google mail", "mail"},
    "chatgpt": {"chatgpt", "chat gpt"},
    "wikipedia": {"wikipedia", "wiki"},
    "spotify": {"spotify"},
    "netflix": {"netflix"},
    "reddit": {"reddit"},
    "linkedin": {"linkedin", "linked in"},
    "stackoverflow": {"stackoverflow", "stack overflow"},
}


def bekende_sites():
    return {
        "youtube": instellingen["youtube_url"],
        "google": instellingen["google_url"],
        "github": "https://github.com",
        "gmail": "https://mail.google.com",
        "chatgpt": "https://chatgpt.com",
        "wikipedia": "https://www.wikipedia.org",
        "spotify": "https://open.spotify.com",
        "netflix": "https://www.netflix.com",
        "reddit": "https://www.reddit.com",
        "linkedin": "https://www.linkedin.com",
        "stackoverflow": "https://stackoverflow.com",
    }


SITE_SEARCH_TEMPLATES = {
    "google": "https://www.google.com/search?q={query}",
    "youtube": "https://www.youtube.com/results?search_query={query}",
    "gmail": "https://mail.google.com/mail/u/0/#search/{query}",
    "github": "https://github.com/search?q={query}",
    "wikipedia": "https://en.wikipedia.org/w/index.php?search={query}",
    "reddit": "https://www.reddit.com/search/?q={query}",
    "linkedin": "https://www.linkedin.com/search/results/all/?keywords={query}",
    "stackoverflow": "https://stackoverflow.com/search?q={query}",
}


def browser_label(browser_sleutel):
    return {
        "chrome": "Chrome",
        "edge": "Edge",
    }.get(browser_sleutel, browser_sleutel.title())


def vind_browser_sleutel_tekst(tekst):
    tekst = re.sub(r"\s+", " ", str(tekst or "").lower()).strip()
    if re.search(r"\b(?:chrome|google chrome)\b", tekst):
        return "chrome"
    if re.search(r"\b(?:edge|microsoft edge)\b", tekst):
        return "edge"
    return ""


def vind_site_sleutel_in_tekst(tekst):
    tekst = re.sub(r"\s+", " ", str(tekst or "").lower()).strip()
    for sleutel, aliassen in SITE_ALIASES.items():
        if any(re.search(rf"(?<!\w){re.escape(alias)}(?!\w)", tekst) for alias in sorted(aliassen, key=len, reverse=True)):
            return sleutel
    return ""


def verwijder_browser_suffix(tekst):
    return re.sub(r"\s+(?:in|met|using)\s+(?:google chrome|chrome|microsoft edge|edge)\s*$", "", str(tekst or "").strip(), flags=re.IGNORECASE)


def url_voor_site_search(site_sleutel, zoekterm):
    template = SITE_SEARCH_TEMPLATES.get(site_sleutel, SITE_SEARCH_TEMPLATES["google"])
    return template.format(query=quote_plus(str(zoekterm or "").strip()))


def maak_browser_workflow_actie(originele_stap, stap):
    browser_sleutel = vind_browser_sleutel_tekst(originele_stap)
    if not browser_sleutel:
        return ""

    genormaliseerd = re.sub(r"\s+", " ", str(originele_stap or "")).strip()
    site_sleutel = vind_site_sleutel_in_tekst(genormaliseerd)
    zoekterm = ""

    if site_sleutel:
        site_patronen = sorted(SITE_ALIASES[site_sleutel], key=len, reverse=True)
        site_regex = "|".join(re.escape(alias) for alias in site_patronen)
        zoek_patronen = [
            rf"(?:search|zoek)(?:\s+(?:on|op))?\s+(?:{site_regex})(?:\s+(?:for|naar|op))\s+(?P<query>.+)$",
            rf"(?:go to|ga naar|open)\s+(?:{site_regex})\s+(?:and|en)\s+(?:search|zoek)(?:\s+(?:for|naar|op))?\s+(?P<query>.+)$",
            rf"(?:open|start)\s+(?:chrome|edge|google chrome|microsoft edge)[, ]+(?:go to|ga naar)\s+(?:{site_regex})\s+(?:and|en)\s+(?:search|zoek)(?:\s+(?:for|naar|op))?\s+(?P<query>.+)$",
        ]
        for patroon in zoek_patronen:
            match = re.search(patroon, genormaliseerd, flags=re.IGNORECASE)
            if match:
                zoekterm = verwijder_browser_suffix(match.group("query")).strip(" .?,'\"")
                break

    if not zoekterm:
        generieke_zoek_match = re.search(r"(?:search|zoek)(?:\s+(?:for|naar|op))\s+(?P<query>.+)$", genormaliseerd, flags=re.IGNORECASE)
        if generieke_zoek_match:
            zoekterm = verwijder_browser_suffix(generieke_zoek_match.group("query")).strip(" .?,'\"")

    if zoekterm:
        doel_site = site_sleutel or "google"
        return f"open browser url::{browser_sleutel}||{url_voor_site_search(doel_site, zoekterm)}"

    if site_sleutel and re.search(r"\b(?:open|start|go to|ga naar)\b", stap):
        return f"open browser url::{browser_sleutel}||{webdoel_naar_url(site_sleutel)}"

    return ""


SYSTEM_APP_TARGETS = {
    "notepad": {
        "aliases": {"notepad", "kladblok"},
        "command": ["notepad"],
        "label_en": "Notepad",
        "label_nl": "Kladblok",
    },
    "calculator": {
        "aliases": {"calculator", "rekenmachine", "calc"},
        "command": ["calc"],
        "label_en": "Calculator",
        "label_nl": "Rekenmachine",
    },
    "paint": {
        "aliases": {"paint", "mspaint", "tekenprogramma"},
        "command": ["mspaint"],
        "label_en": "Paint",
        "label_nl": "Paint",
    },
    "command prompt": {
        "aliases": {"command prompt", "cmd", "opdrachtprompt", "terminal"},
        "command": ["cmd"],
        "label_en": "Command Prompt",
        "label_nl": "Opdrachtprompt",
    },
    "powershell": {
        "aliases": {"powershell", "power shell"},
        "command": ["powershell"],
        "label_en": "PowerShell",
        "label_nl": "PowerShell",
    },
    "file explorer": {
        "aliases": {"file explorer", "explorer", "verkenner", "bestandsverkenner"},
        "command": ["explorer", instellingen["verkenner_start_map"]],
        "label_en": "File Explorer",
        "label_nl": "Verkenner",
    },
    "task manager": {
        "aliases": {"task manager", "taskmgr", "taakbeheer"},
        "command": ["taskmgr"],
        "label_en": "Task Manager",
        "label_nl": "Taakbeheer",
    },
    "control panel": {
        "aliases": {"control panel", "configuratiescherm"},
        "command": ["control"],
        "label_en": "Control Panel",
        "label_nl": "Configuratiescherm",
    },
    "snipping tool": {
        "aliases": {"snipping tool", "knipprogramma", "screenshot tool", "schermafbeelding tool"},
        "command": ["snippingtool"],
        "label_en": "Snipping Tool",
        "label_nl": "Knipprogramma",
    },
    "edge": {
        "aliases": {"edge", "microsoft edge"},
        "command": ["cmd", "/c", "start", "", "msedge"],
        "label_en": "Microsoft Edge",
        "label_nl": "Microsoft Edge",
    },
    "discord": {
        "aliases": {"discord"},
        "command": ["cmd", "/c", "start", "", "discord"],
        "label_en": "Discord",
        "label_nl": "Discord",
    },
    "whatsapp": {
        "aliases": {"whatsapp", "whatsapp desktop"},
        "command": ["cmd", "/c", "start", "", "whatsapp"],
        "label_en": "WhatsApp",
        "label_nl": "WhatsApp",
    },
    "steam": {
        "aliases": {"steam"},
        "command": ["cmd", "/c", "start", "", "steam"],
        "label_en": "Steam",
        "label_nl": "Steam",
    },
}


SYSTEM_SETTING_TARGETS = {
    "settings": {
        "aliases": {"settings", "instellingen", "windows settings", "windows instellingen"},
        "target": "ms-settings:",
        "label_en": "Settings",
        "label_nl": "Instellingen",
    },
    "display settings": {
        "aliases": {"display settings", "screen settings", "beeldscherminstellingen", "scherminstellingen"},
        "target": "ms-settings:display",
        "label_en": "Display settings",
        "label_nl": "Beeldscherminstellingen",
    },
    "sound settings": {
        "aliases": {"sound settings", "audio settings", "geluidsinstellingen", "audio-instellingen"},
        "target": "ms-settings:sound",
        "label_en": "Sound settings",
        "label_nl": "Geluidsinstellingen",
    },
    "wifi settings": {
        "aliases": {"wifi settings", "wi-fi settings", "network settings", "wifi-instellingen", "netwerkinstellingen"},
        "target": "ms-settings:network-wifi",
        "label_en": "Wi-Fi settings",
        "label_nl": "Wifi-instellingen",
    },
    "bluetooth settings": {
        "aliases": {"bluetooth settings", "bluetooth-instellingen"},
        "target": "ms-settings:bluetooth",
        "label_en": "Bluetooth settings",
        "label_nl": "Bluetooth-instellingen",
    },
    "apps settings": {
        "aliases": {"apps settings", "program settings", "apps-instellingen", "programma-instellingen"},
        "target": "ms-settings:appsfeatures",
        "label_en": "Apps settings",
        "label_nl": "Apps-instellingen",
    },
}


COMMON_FOLDER_TARGETS = {
    "desktop": {
        "aliases": {"desktop", "bureaublad"},
        "path": lambda: Path.home() / "Desktop",
        "label_en": "Desktop",
        "label_nl": "Bureaublad",
    },
    "documents": {
        "aliases": {"documents", "documenten", "docs", "my documents", "mijn documenten"},
        "path": lambda: Path.home() / "Documents",
        "label_en": "Documents",
        "label_nl": "Documenten",
    },
    "downloads": {
        "aliases": {"downloads", "download map", "downloads folder", "download folder"},
        "path": lambda: Path.home() / "Downloads",
        "label_en": "Downloads",
        "label_nl": "Downloads",
    },
    "pictures": {
        "aliases": {"pictures", "afbeeldingen", "photos", "foto's", "fotos"},
        "path": lambda: Path.home() / "Pictures",
        "label_en": "Pictures",
        "label_nl": "Afbeeldingen",
    },
    "music": {
        "aliases": {"music", "muziek"},
        "path": lambda: Path.home() / "Music",
        "label_en": "Music",
        "label_nl": "Muziek",
    },
    "videos": {
        "aliases": {"videos", "video's", "videos folder", "video map"},
        "path": lambda: Path.home() / "Videos",
        "label_en": "Videos",
        "label_nl": "Video's",
    },
    "home": {
        "aliases": {"home", "thuis", "home folder", "thuis map", "user folder", "gebruikersmap"},
        "path": lambda: Path.home(),
        "label_en": "Home folder",
        "label_nl": "Thuismap",
    },
}


DANGEROUS_SYSTEM_ACTIONS = {
    "lock computer": {
        "aliases": {"lock computer", "lock pc", "lock screen", "vergrendel computer", "vergrendel pc", "vergrendel scherm"},
        "confirm_en": "lock the computer",
        "confirm_nl": "de computer te vergrendelen",
        "done_en": "Computer locked",
        "done_nl": "Computer vergrendeld",
    },
    "sleep computer": {
        "aliases": {"sleep computer", "sleep pc", "put computer to sleep", "slaapstand", "computer slaapstand", "pc slaapstand"},
        "confirm_en": "put the computer to sleep",
        "confirm_nl": "de computer in slaapstand te zetten",
        "done_en": "Computer put to sleep",
        "done_nl": "Computer in slaapstand gezet",
    },
    "restart computer": {
        "aliases": {"restart computer", "restart pc", "reboot computer", "herstart computer", "herstart pc"},
        "confirm_en": "restart the computer",
        "confirm_nl": "de computer te herstarten",
        "done_en": "Computer restarting",
        "done_nl": "Computer wordt herstart",
    },
    "shutdown computer": {
        "aliases": {"shutdown computer", "shutdown pc", "turn off computer", "turn off pc", "afsluiten computer", "sluit computer af", "computer uitzetten", "pc uitzetten"},
        "confirm_en": "shut down the computer",
        "confirm_nl": "de computer af te sluiten",
        "done_en": "Computer shutting down",
        "done_nl": "Computer wordt afgesloten",
    },
    "sign out": {
        "aliases": {"sign out", "log out", "uitloggen", "afmelden"},
        "confirm_en": "sign out of Windows",
        "confirm_nl": "je af te melden bij Windows",
        "done_en": "Signing out",
        "done_nl": "Bezig met afmelden",
    },
}


TOETS_ALIASES = {
    "control": "ctrl",
    "ctrl": "ctrl",
    "shift": "shift",
    "alt": "alt",
    "win": "win",
    "windows": "win",
    "enter": "enter",
    "return": "enter",
    "tab": "tab",
    "escape": "esc",
    "esc": "esc",
    "space": "space",
    "spacebar": "space",
    "backspace": "backspace",
    "delete": "delete",
    "del": "delete",
    "up": "up",
    "down": "down",
    "left": "left",
    "right": "right",
    "home": "home",
    "end": "end",
    "pageup": "pageup",
    "page up": "pageup",
    "pagedown": "pagedown",
    "page down": "pagedown",
    "insert": "insert",
    "menu": "apps",
}


WINDOW_TITLE_HINTS = {
    "vscode": ["visual studio code", " - code"],
    "chrome": ["google chrome", "chrome"],
    "edge": ["microsoft edge", "edge"],
    "discord": ["discord"],
    "whatsapp": ["whatsapp"],
    "steam": ["steam"],
    "spotify": ["spotify"],
    "explorer": ["file explorer", "verkenner"],
}


APP_LAUNCH_COMMANDS = {
    "vscode": ["cmd", "/c", "start", "", "vscode"],
    "chrome": ["cmd", "/c", "start", "", "chrome"],
    "edge": ["cmd", "/c", "start", "", "msedge"],
    "discord": ["cmd", "/c", "start", "", "discord"],
    "whatsapp": ["cmd", "/c", "start", "", "whatsapp"],
    "steam": ["cmd", "/c", "start", "", "steam"],
    "spotify": ["cmd", "/c", "start", "", "spotify"],
    "explorer": ["explorer"],
}


def open_url_in_browser(browser_sleutel, url):
    command = list(APP_LAUNCH_COMMANDS.get(browser_sleutel, []))
    if not command:
        webbrowser.open(url)
        return
    subprocess.Popen(command + [url])


def strip_markdown_code_blokken(tekst):
    tekst = str(tekst or "").strip()
    tekst = re.sub(r"^```(?:\w+)?\s*", "", tekst, flags=re.IGNORECASE)
    tekst = re.sub(r"\s*```$", "", tekst)
    return tekst.strip()


def maak_extractieve_samenvatting(inhoud, max_zinnen=3, max_tekens=520):
    inhoud = re.sub(r"\s+", " ", str(inhoud or "")).strip()
    if not inhoud:
        return ""

    zinnen = [zin.strip() for zin in re.split(r"(?<=[.!?])\s+", inhoud) if zin.strip()]
    gekozen = []
    totale_lengte = 0
    for zin in zinnen:
        gekozen.append(zin)
        totale_lengte += len(zin) + 1
        if len(gekozen) >= max_zinnen or totale_lengte >= max_tekens:
            break

    samenvatting = " ".join(gekozen).strip()
    if len(samenvatting) > max_tekens:
        samenvatting = samenvatting[: max_tekens - 3].rstrip() + "..."
    return samenvatting


def vraag_korte_samenvatting_via_ai(bron_label, inhoud):
    if not online_ai_beschikbaar():
        return ""

    inhoud = re.sub(r"\s+", " ", str(inhoud or "")).strip()
    if not inhoud:
        return ""
    if len(inhoud) > 6000:
        inhoud = inhoud[:6000].rstrip() + "..."

    berichten = [
        {
            "role": "system",
            "content": tekst_voor_taal(
                "You summarize content for a desktop assistant. Give 2 to 4 short sentences with the main point, key details, and any action the user may want next. Do not use markdown.",
                "Je vat content samen voor een desktopassistent. Geef 2 tot 4 korte zinnen met de hoofdzaak, belangrijke details en een mogelijke volgende stap voor de gebruiker. Gebruik geen markdown."
            ),
        },
        {
            "role": "user",
            "content": tekst_voor_taal(
                f"Source: {bron_label}\n\nContent:\n{inhoud}",
                f"Bron: {bron_label}\n\nInhoud:\n{inhoud}"
            ),
        },
    ]

    try:
        antwoord = vraag_online_ai_bericht(berichten, temperatuur=0.2)
    except (urllib.error.URLError, TimeoutError, ValueError, KeyError, json.JSONDecodeError):
        return ""

    return opschonen_korte_tekst(strip_markdown_code_blokken(antwoord), max_lengte=650)


def normaliseer_url_voor_browser_taak(url_tekst):
    url_tekst = strip_omringende_quotes(str(url_tekst or "").strip())
    if not url_tekst:
        return ""

    if not re.match(r"^[a-z][a-z0-9+.-]*://", url_tekst, flags=re.IGNORECASE):
        if re.match(r"^[\w.-]+\.[a-z]{2,}(?:[/:?#].*)?$", url_tekst, flags=re.IGNORECASE):
            url_tekst = "https://" + url_tekst
        else:
            return ""

    parsed = urlparse(url_tekst)
    if parsed.scheme.lower() not in {"http", "https"} or not parsed.netloc:
        return ""
    return url_tekst


def strip_html_naar_tekst(html_tekst):
    html_tekst = re.sub(r"(?is)<!--.*?-->", " ", str(html_tekst or ""))
    html_tekst = re.sub(r"(?is)<(script|style|noscript|svg).*?>.*?</\1>", " ", html_tekst)
    html_tekst = re.sub(r"(?i)<br\s*/?>", "\n", html_tekst)
    html_tekst = re.sub(r"(?i)</p>|</div>|</section>|</article>|</li>|</h[1-6]>|</tr>", "\n", html_tekst)
    html_tekst = re.sub(r"(?s)<[^>]+>", " ", html_tekst)
    html_tekst = html.unescape(html_tekst)
    html_tekst = re.sub(r"\r", "", html_tekst)
    html_tekst = re.sub(r"\n{3,}", "\n\n", html_tekst)
    html_tekst = re.sub(r"[ \t]+", " ", html_tekst)
    return html_tekst.strip()


def haal_webpagina_context(url):
    url = normaliseer_url_voor_browser_taak(url)
    if not url:
        raise ValueError("Invalid URL")

    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "EchoDesktop/1.0",
            "Accept": "text/html, text/plain;q=0.9, */*;q=0.1",
        },
    )
    with urllib.request.urlopen(request, timeout=25) as response:
        rauw = response.read(350_000)
        inhoud_type = str(response.headers.get("Content-Type", "")).lower()
        charset = response.headers.get_content_charset() or "utf-8"

    if "text/" not in inhoud_type and "html" not in inhoud_type:
        raise ValueError("Unsupported page content")

    inhoud = rauw.decode(charset, errors="ignore")
    titel_match = re.search(r"(?is)<title[^>]*>(.*?)</title>", inhoud)
    titel = html.unescape(titel_match.group(1)).strip() if titel_match else url
    tekst = strip_html_naar_tekst(inhoud if "html" in inhoud_type else inhoud)
    if not tekst:
        tekst = titel

    return {
        "url": url,
        "title": opschonen_korte_tekst(titel, max_lengte=140),
        "text": tekst,
    }


def lees_klembord_tekst():
    try:
        resultaat = subprocess.run(
            ["powershell", "-NoProfile", "-Command", "Get-Clipboard -Raw"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
            check=True,
        )
        return str(resultaat.stdout or "")
    except Exception:
        return ""


def zet_klembord_tekst(tekst):
    try:
        subprocess.run(
            ["powershell", "-NoProfile", "-Command", "Set-Clipboard -Value ([Console]::In.ReadToEnd())"],
            input=str(tekst or ""),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
            check=True,
        )
    except Exception:
        pass


def actieve_browser_sleutel():
    venster = haal_actief_venster()
    titel = getattr(venster, "title", "").lower() if venster else ""
    for browser_sleutel in ("chrome", "edge"):
        for hint in WINDOW_TITLE_HINTS.get(browser_sleutel, []):
            if hint in titel:
                return browser_sleutel
    return ""


def browser_automation_blokkade_bericht():
    if not instellingen.get("computerbesturing_toestaan", False):
        return tekst_voor_taal(
            "Enable advanced computer control in Settings first.",
            "Zet eerst geavanceerde computerbesturing aan in Instellingen."
        )

    if not automatisering_actief():
        return tekst_voor_taal(
            "Automation mode is off. Say enable automation mode first. It stays active for 5 minutes.",
            "Automation-modus staat uit. Zeg eerst schakel automation-modus in. Die blijft 5 minuten actief."
        )

    if not AUTOMATISERING_BESCHIKBAAR:
        return tekst_voor_taal(
            "Automation support is not available because PyAutoGUI could not be loaded.",
            "Automation-ondersteuning is niet beschikbaar omdat PyAutoGUI niet geladen kon worden."
        )

    return ""


def lees_huidige_browser_url(browser_sleutel=""):
    blokkade = browser_automation_blokkade_bericht()
    if blokkade:
        raise RuntimeError(blokkade)

    browser_sleutel = browser_sleutel or actieve_browser_sleutel()
    if browser_sleutel and not actieve_browser_sleutel() and not activeer_venster(browser_sleutel):
        raise RuntimeError(tekst_voor_taal("Could not focus the requested browser.", "Kon de gevraagde browser niet activeren."))
    if not browser_sleutel:
        raise RuntimeError(tekst_voor_taal("No supported browser is active.", "Er is geen ondersteunde browser actief."))

    originele_klembordtekst = lees_klembord_tekst()
    try:
        pyautogui.hotkey("ctrl", "l")
        time.sleep(0.1)
        pyautogui.hotkey("ctrl", "c")
        time.sleep(0.12)
        url = normaliseer_url_voor_browser_taak(lees_klembord_tekst().strip())
    finally:
        zet_klembord_tekst(originele_klembordtekst)

    if not url:
        raise RuntimeError(tekst_voor_taal("Could not read the current browser URL.", "Kon de huidige browser-URL niet lezen."))
    return url


def preview_van_webpagina(url):
    pagina = haal_webpagina_context(url)
    preview = maak_extractieve_samenvatting(pagina["text"], max_zinnen=4, max_tekens=650)
    return tekst_voor_taal(
        f"Page preview for {pagina['title']}: {preview}",
        f"Paginavoorbeeld voor {pagina['title']}: {preview}"
    )


def samenvatting_van_webpagina(url):
    pagina = haal_webpagina_context(url)
    samenvatting = vraag_korte_samenvatting_via_ai(pagina["title"], pagina["text"]) or maak_extractieve_samenvatting(pagina["text"])
    return tekst_voor_taal(
        f"Summary of {pagina['title']}: {samenvatting}",
        f"Samenvatting van {pagina['title']}: {samenvatting}"
    )


def vul_browser_formulier_in(waarden):
    blokkade = browser_automation_blokkade_bericht()
    if blokkade:
        raise RuntimeError(blokkade)

    schone_waarden = [str(waarde).strip() for waarde in waarden if str(waarde).strip()]
    if not schone_waarden:
        raise RuntimeError(tekst_voor_taal("No form values provided.", "Geen formulierwaarden opgegeven."))

    for index, waarde in enumerate(schone_waarden):
        pyautogui.write(waarde, interval=0.02)
        if index < len(schone_waarden) - 1:
            pyautogui.press("tab")
            time.sleep(0.05)

    return tekst_voor_taal(
        f"Filled {len(schone_waarden)} form field(s).",
        f"{len(schone_waarden)} formulierveld(en) ingevuld."
    )


def voer_geavanceerde_browser_actie_uit(actie):
    try:
        if actie == "browser current url":
            url = lees_huidige_browser_url()
            return tekst_voor_taal(f"Current browser URL: {url}", f"Huidige browser-URL: {url}")

        if actie == "browser read current":
            return preview_van_webpagina(lees_huidige_browser_url())

        if actie == "browser summarize current":
            return samenvatting_van_webpagina(lees_huidige_browser_url())

        if actie.startswith("browser read url::"):
            return preview_van_webpagina(actie.split("::", 1)[1])

        if actie.startswith("browser summarize url::"):
            return samenvatting_van_webpagina(actie.split("::", 1)[1])

        if actie.startswith("browser fill form::"):
            waarden = [deel for deel in actie.split("::", 1)[1].split("||") if deel]
            return vul_browser_formulier_in(waarden)

        if actie == "browser submit form":
            blokkade = browser_automation_blokkade_bericht()
            if blokkade:
                return blokkade
            pyautogui.press("enter")
            return tekst_voor_taal("Form submitted.", "Formulier verzonden.")
    except ValueError as e:
        return tekst_voor_taal(f"Browser task error: {e}", f"Browsertaakfout: {e}")
    except Exception as e:
        return str(e) if str(e) else tekst_voor_taal("Browser task failed.", "Browsertaak mislukt.")

    return tekst_voor_taal("Unknown browser action", "Onbekende browseractie")


APP_MACROS = {
    "vscode-new-file": {
        "aliases": {"vscode new file", "new file in vscode", "nieuw bestand in vscode", "open vscode new file", "start vscode new file"},
        "app": "vscode",
        "steps": [("hotkey", ["ctrl", "n"])],
        "label_en": "VS Code new file",
        "label_nl": "VS Code nieuw bestand",
    },
    "vscode-command-palette": {
        "aliases": {"vscode command palette", "open command palette in vscode", "vscode opdrachtenpalet", "vscode commandopalet", "open vscode command palette"},
        "app": "vscode",
        "steps": [("hotkey", ["ctrl", "shift", "p"])],
        "label_en": "VS Code command palette",
        "label_nl": "VS Code opdrachtenpalet",
    },
    "chrome-new-tab": {
        "aliases": {"chrome new tab", "new tab in chrome", "nieuw tabblad in chrome", "open chrome new tab"},
        "app": "chrome",
        "steps": [("hotkey", ["ctrl", "t"])],
        "label_en": "Chrome new tab",
        "label_nl": "Chrome nieuw tabblad",
    },
    "chrome-incognito": {
        "aliases": {"chrome incognito", "open incognito in chrome", "chrome incognito mode", "chrome incognito modus", "open chrome incognito"},
        "app": "chrome",
        "steps": [("hotkey", ["ctrl", "shift", "n"])],
        "label_en": "Chrome incognito",
        "label_nl": "Chrome incognito",
    },
    "edge-new-tab": {
        "aliases": {"edge new tab", "new tab in edge", "nieuw tabblad in edge", "open edge new tab"},
        "app": "edge",
        "steps": [("hotkey", ["ctrl", "t"])],
        "label_en": "Edge new tab",
        "label_nl": "Edge nieuw tabblad",
    },
    "edge-inprivate": {
        "aliases": {"edge inprivate", "edge private mode", "open inprivate in edge", "edge inprivate mode", "open edge inprivate"},
        "app": "edge",
        "steps": [("hotkey", ["ctrl", "shift", "n"])],
        "label_en": "Edge InPrivate",
        "label_nl": "Edge InPrivate",
    },
    "discord-search": {
        "aliases": {"discord search", "search in discord", "zoek in discord", "open discord search"},
        "app": "discord",
        "steps": [("hotkey", ["ctrl", "k"])],
        "label_en": "Discord quick switcher",
        "label_nl": "Discord snelzoeker",
    },
    "discord-mute-toggle": {
        "aliases": {"discord mute", "discord toggle mute", "discord dempen", "discord mute toggle"},
        "app": "discord",
        "steps": [("hotkey", ["ctrl", "shift", "m"])],
        "label_en": "Discord mute toggle",
        "label_nl": "Discord mute-toggle",
    },
    "whatsapp-new-chat": {
        "aliases": {"whatsapp new chat", "new chat in whatsapp", "nieuw chat in whatsapp", "open whatsapp new chat"},
        "app": "whatsapp",
        "steps": [("hotkey", ["ctrl", "n"])],
        "label_en": "WhatsApp new chat",
        "label_nl": "WhatsApp nieuwe chat",
    },
    "whatsapp-search": {
        "aliases": {"whatsapp search", "search in whatsapp", "zoek in whatsapp", "open whatsapp search"},
        "app": "whatsapp",
        "steps": [("hotkey", ["ctrl", "f"])],
        "label_en": "WhatsApp search",
        "label_nl": "WhatsApp zoeken",
    },
    "steam-screenshot": {
        "aliases": {"steam screenshot", "take steam screenshot", "steam schermafbeelding", "open steam screenshot"},
        "app": "steam",
        "steps": [("press", "f12")],
        "label_en": "Steam screenshot",
        "label_nl": "Steam screenshot",
    },
    "steam-search": {
        "aliases": {"steam search", "search in steam", "zoek in steam", "open steam search"},
        "app": "steam",
        "steps": [("hotkey", ["ctrl", "f"])],
        "label_en": "Steam search",
        "label_nl": "Steam zoeken",
    },
    "spotify-play-pause": {
        "aliases": {"spotify play pause", "spotify pause", "spotify afspelen", "spotify pauze", "open spotify play pause"},
        "app": "spotify",
        "steps": [("press", "playpause")],
        "label_en": "Spotify play or pause",
        "label_nl": "Spotify afspelen of pauzeren",
    },
    "spotify-next-track": {
        "aliases": {"spotify next track", "spotify next song", "spotify volgende nummer", "spotify volgende track", "open spotify next track"},
        "app": "spotify",
        "steps": [("press", "nexttrack")],
        "label_en": "Spotify next track",
        "label_nl": "Spotify volgende track",
    },
    "explorer-new-window": {
        "aliases": {"explorer new window", "new explorer window", "verkenner nieuw venster", "open explorer new window"},
        "app": "explorer",
        "steps": [("launch", ["explorer"])],
        "label_en": "Explorer new window",
        "label_nl": "Verkenner nieuw venster",
    },
    "explorer-search": {
        "aliases": {"explorer search", "search in explorer", "zoek in verkenner", "verkenner zoeken", "open explorer search"},
        "app": "explorer",
        "steps": [("hotkey", ["ctrl", "e"])],
        "label_en": "Explorer search",
        "label_nl": "Zoeken in Verkenner",
    },
}


def titel_voor_webdoel(doel):
    labels = {
        "youtube": "YouTube",
        "google": "Google",
        "github": "GitHub",
        "gmail": "Gmail",
        "chatgpt": "ChatGPT",
        "wikipedia": "Wikipedia",
        "spotify": "Spotify",
        "netflix": "Netflix",
        "reddit": "Reddit",
        "linkedin": "LinkedIn",
        "stackoverflow": "Stack Overflow",
    }
    if doel in labels:
        return labels[doel]

    return re.sub(r"^https?://", "", doel).rstrip("/")


def is_webadres(doel):
    return bool(re.match(r"^(?:https?://)?(?:www\.)?[a-z0-9-]+(?:\.[a-z0-9-]+)+(?:/[^\s]*)?$", doel))


def normaliseer_webdoel(doel):
    doel = re.sub(r"\s+", " ", str(doel or "").lower()).strip(" ,.")
    if not doel:
        return ""

    doel = re.sub(r"^(?:website|site|pagina|page)\s+", "", doel)
    doel = re.sub(r"\s+(?:website|site|pagina|page)$", "", doel)
    doel = doel.strip(" ,.")

    for sleutel, aliassen in SITE_ALIASES.items():
        if doel in aliassen:
            return sleutel

    if is_webadres(doel):
        return doel if doel.startswith(("http://", "https://")) else f"https://{doel}"

    return ""


def normaliseer_meerdere_webdoelen(doel_tekst):
    delen = re.split(r"\s*(?:,|\ben\b|\band\b|&)\s*", str(doel_tekst or "").strip())
    doelen = []
    gezien = set()

    for deel in delen:
        doel = normaliseer_webdoel(deel)
        if doel and doel not in gezien:
            doelen.append(doel)
            gezien.add(doel)

    return doelen


def webdoel_naar_url(doel):
    sites = bekende_sites()
    if doel in sites:
        return sites[doel]
    return doel


def haal_webdoelen_uit_actie(actie, prefix):
    payload = re.sub(rf"^{re.escape(prefix)}\s*", "", actie).strip()
    return [doel for doel in payload.split("||") if doel]


def schoon_computerdoel(doel_tekst):
    doel = re.sub(r"\s+", " ", str(doel_tekst or "").lower()).strip(" ,.'\"")
    doel = re.sub(r"^(?:de|het|the|a|een)\s+", "", doel)
    doel = re.sub(r"^(?:app|application|programma|program)\s+", "", doel)
    doel = re.sub(r"\s+(?:app|application|programma|program)$", "", doel)
    return doel.strip(" ,.'\"")


def vind_alias_sleutel(doel_tekst, definities):
    doel = schoon_computerdoel(doel_tekst)
    for sleutel, data in definities.items():
        if doel in data["aliases"]:
            return sleutel
    return ""


def resolve_bestaand_pad(doel_tekst):
    doel = str(doel_tekst or "").strip().strip("\"'")
    if not doel:
        return None

    kandidaat = Path(doel).expanduser()
    if not kandidaat.is_absolute():
        kandidaat = Path.cwd() / kandidaat

    try:
        kandidaat = kandidaat.resolve()
    except Exception:
        kandidaat = kandidaat

    return kandidaat if kandidaat.exists() else None


def resolve_folder_pad(doel_tekst):
    doel = schoon_computerdoel(re.sub(r"^(?:folder|map|directory)\s+", "", str(doel_tekst or "")))
    sleutel = vind_alias_sleutel(doel, COMMON_FOLDER_TARGETS)
    if sleutel:
        return COMMON_FOLDER_TARGETS[sleutel]["path"]()

    kandidaat = resolve_bestaand_pad(doel)
    if kandidaat and kandidaat.is_dir():
        return kandidaat

    return None


def resolve_bestand_pad(doel_tekst):
    doel = re.sub(r"^(?:file|bestand)\s+", "", str(doel_tekst or "").strip(), flags=re.IGNORECASE)
    kandidaat = resolve_bestaand_pad(doel)
    if kandidaat and kandidaat.is_file():
        return kandidaat
    return None


def schoon_pad_argument(tekst):
    waarde = str(tekst or "").strip()
    waarde = re.sub(r"^(?:(?:the|de|het|a|an|een)\s+)?(?:file|bestand|folder|map|directory)\s+", "", waarde, flags=re.IGNORECASE)
    if len(waarde) >= 2 and waarde[0] == waarde[-1] and waarde[0] in {'"', "'"}:
        waarde = waarde[1:-1]
    return waarde.strip()


def resolve_pad_voor_operatie(doel_tekst):
    doel = schoon_pad_argument(doel_tekst)
    if not doel:
        return None

    bekende_map = resolve_folder_pad(doel)
    if bekende_map:
        return bekende_map

    kandidaat = Path(doel).expanduser()
    if not kandidaat.is_absolute():
        kandidaat = Path.cwd() / kandidaat

    try:
        return kandidaat.resolve(strict=False)
    except TypeError:
        return kandidaat.resolve()
    except Exception:
        return kandidaat


def resolve_bron_pad_voor_operatie(doel_tekst):
    doel = schoon_pad_argument(doel_tekst)
    folder_pad = resolve_folder_pad(doel)
    if folder_pad:
        return folder_pad

    bestand_pad = resolve_bestand_pad(doel)
    if bestand_pad:
        return bestand_pad

    return resolve_bestaand_pad(doel)


def resolve_bestemming_pad_voor_operatie(bron_pad, doel_tekst):
    bron_pad = Path(bron_pad)
    ruwe_doel = schoon_pad_argument(doel_tekst)
    bestemming = resolve_pad_voor_operatie(ruwe_doel)
    if bestemming is None:
        return None

    if bestemming.exists() and bestemming.is_dir():
        return bestemming / bron_pad.name

    if ruwe_doel.endswith(("\\", "/")):
        return bestemming / bron_pad.name

    return bestemming


def split_pad_payload(actie):
    payload = actie.split("::", 1)[1]
    delen = payload.split("||")
    return [deel for deel in delen if deel]


def split_tekst_en_pad_opdracht(payload_tekst):
    payload_tekst = re.sub(r"\s+", " ", str(payload_tekst or "")).strip()
    if not payload_tekst:
        return "", ""

    indices = []
    lower_payload = payload_tekst.lower()
    for scheiding in (" to ", " naar ", " in ", " aan "):
        index = lower_payload.rfind(scheiding)
        if index > 0:
            indices.append((index, scheiding))

    if not indices:
        return "", ""

    index, scheiding = max(indices, key=lambda item: item[0])
    tekst = strip_omringende_quotes(payload_tekst[:index].strip())
    pad = schoon_pad_argument(payload_tekst[index + len(scheiding):])
    return tekst, pad


def formatteer_bestandsgrootte(aantal_bytes):
    grootte = float(max(0, aantal_bytes))
    eenheden = ["B", "KB", "MB", "GB", "TB"]
    for eenheid in eenheden:
        if grootte < 1024 or eenheid == eenheden[-1]:
            precision = 0 if eenheid == "B" else 1
            return f"{grootte:.{precision}f} {eenheid}"
        grootte /= 1024
    return f"{aantal_bytes} B"


def lees_tekst_preview(bestand_pad, max_regels=18, max_tekens=1500):
    bestand_pad = Path(bestand_pad)
    try:
        rauw = bestand_pad.read_bytes()
    except Exception as e:
        raise RuntimeError(str(e)) from e

    if b"\x00" in rauw[:4096]:
        raise ValueError("binary file")

    tekst = rauw.decode("utf-8", errors="ignore")
    if not tekst.strip():
        return ""

    regels = []
    totale_lengte = 0
    for regel in tekst.splitlines():
        opgeschoond = regel.rstrip()
        regels.append(opgeschoond)
        totale_lengte += len(opgeschoond) + 1
        if len(regels) >= max_regels or totale_lengte >= max_tekens:
            break

    preview = "\n".join(regels).strip()
    if len(preview) > max_tekens:
        preview = preview[: max_tekens - 3].rstrip() + "..."
    return preview


def lees_tekstbestand_volledig(bestand_pad, max_tekens=12000):
    bestand_pad = Path(bestand_pad)
    try:
        rauw = bestand_pad.read_bytes()
    except Exception as e:
        raise RuntimeError(str(e)) from e

    if b"\x00" in rauw[:4096]:
        raise ValueError("binary file")

    tekst = rauw.decode("utf-8", errors="ignore")
    if len(tekst) > max_tekens:
        raise ValueError("file too large")
    return tekst


def vat_tekstbestand_samen(bestand_pad):
    inhoud = lees_tekstbestand_volledig(bestand_pad, max_tekens=12000)
    samenvatting = vraag_korte_samenvatting_via_ai(Path(bestand_pad).name, inhoud) or maak_extractieve_samenvatting(inhoud)
    return tekst_voor_taal(
        f"Summary of {Path(bestand_pad).name}: {samenvatting}",
        f"Samenvatting van {Path(bestand_pad).name}: {samenvatting}"
    )


def herschrijf_tekst_met_ai(bron_label, inhoud, instructie):
    if not online_ai_beschikbaar():
        raise RuntimeError(tekst_voor_taal("AI rewrite is not available right now.", "AI-herschrijven is nu niet beschikbaar."))

    inhoud = str(inhoud or "")
    if len(inhoud) > 12000:
        raise ValueError("file too large")

    berichten = [
        {
            "role": "system",
            "content": tekst_voor_taal(
                "You rewrite file content for a desktop assistant. Apply the user's instruction and return only the final file content. Do not add markdown fences, explanations, or commentary.",
                "Je herschrijft bestandsinhoud voor een desktopassistent. Voer de instructie van de gebruiker uit en geef alleen de uiteindelijke bestandsinhoud terug. Voeg geen markdown-fences, uitleg of commentaar toe."
            ),
        },
        {
            "role": "user",
            "content": tekst_voor_taal(
                f"File: {bron_label}\nInstruction: {instructie}\n\nContent:\n{inhoud}",
                f"Bestand: {bron_label}\nInstructie: {instructie}\n\nInhoud:\n{inhoud}"
            ),
        },
    ]

    antwoord = vraag_online_ai_bericht(berichten, temperatuur=0.2)
    antwoord = strip_markdown_code_blokken(antwoord)
    if not antwoord.strip():
        raise RuntimeError(tekst_voor_taal("AI rewrite returned no content.", "AI-herschrijving gaf geen inhoud terug."))
    return antwoord


def iter_workspace_bestanden(basis_pad=None):
    basis_pad = Path(basis_pad or Path.cwd())
    for pad in basis_pad.rglob("*"):
        if not pad.is_file():
            continue
        if any(deel in DOCUMENT_CONTEXT_GENEGEERDE_MAPNAMEN for deel in pad.parts):
            continue
        if pad.name.lower() in WORKSPACE_SEARCH_GENEGEERDE_BESTANDEN:
            continue
        yield pad


def lijst_map_inhoud(map_pad, max_items=14):
    map_pad = Path(map_pad)
    items = sorted(map_pad.iterdir(), key=lambda item: (not item.is_dir(), item.name.lower()))
    regels = []
    for item in items[:max_items]:
        label = item.name + ("/" if item.is_dir() else "")
        if item.is_file():
            try:
                label += f" ({formatteer_bestandsgrootte(item.stat().st_size)})"
            except OSError:
                pass
        regels.append(label)
    return items, regels


def vind_eerste_regel_match(inhoud, zoektekst):
    zoektekst = str(zoektekst or "").lower()
    for index, regel in enumerate(inhoud.splitlines(), start=1):
        if zoektekst in regel.lower():
            return index, opschonen_korte_tekst(regel, max_lengte=220)
    return 0, ""


def zoek_bestanden_in_workspace(zoektekst, max_resultaten=6):
    zoektekst = re.sub(r"\s+", " ", str(zoektekst or "")).strip().lower()
    if not zoektekst:
        return []

    kandidaten = []
    for pad in iter_workspace_bestanden():
        score = 0
        lijnnummer = 0
        snippet = ""

        relatieve_pad = relatief_document_pad(pad)
        naam_lower = pad.name.lower()
        if zoektekst in naam_lower:
            score += 40

        try:
            grootte = pad.stat().st_size
        except OSError:
            grootte = MAX_DOCUMENT_BESTANDSGROOTTE + 1

        if grootte <= MAX_DOCUMENT_BESTANDSGROOTTE:
            try:
                rauw = pad.read_bytes()
            except Exception:
                rauw = b""

            if rauw and b"\x00" not in rauw[:4096]:
                inhoud = rauw.decode("utf-8", errors="ignore")
                if zoektekst in inhoud.lower():
                    lijnnummer, snippet = vind_eerste_regel_match(inhoud, zoektekst)
                    score += 15
                    if relatieve_pad.lower().startswith("readme"):
                        score += 3

        if score:
            kandidaten.append((score, relatieve_pad, lijnnummer, snippet))

    kandidaten.sort(key=lambda item: item[0], reverse=True)
    return kandidaten[:max_resultaten]


class SYSTEM_POWER_STATUS(ctypes.Structure):
    _fields_ = [
        ("ACLineStatus", ctypes.c_byte),
        ("BatteryFlag", ctypes.c_byte),
        ("BatteryLifePercent", ctypes.c_byte),
        ("SystemStatusFlag", ctypes.c_byte),
        ("BatteryLifeTime", ctypes.c_ulong),
        ("BatteryFullLifeTime", ctypes.c_ulong),
    ]


def haal_batterij_status():
    try:
        status = SYSTEM_POWER_STATUS()
        if not ctypes.windll.kernel32.GetSystemPowerStatus(ctypes.byref(status)):
            return ""
    except Exception:
        return ""

    percentage = None if status.BatteryLifePercent == 255 else int(status.BatteryLifePercent)
    laadstatus = {
        0: tekst_voor_taal("offline", "op batterij"),
        1: tekst_voor_taal("charging", "aan oplader"),
    }.get(status.ACLineStatus, tekst_voor_taal("unknown", "onbekend"))

    if percentage is None:
        return tekst_voor_taal(f"Battery status: {laadstatus}", f"Batterijstatus: {laadstatus}")
    return tekst_voor_taal(
        f"Battery: {percentage}% ({laadstatus})",
        f"Batterij: {percentage}% ({laadstatus})"
    )


def haal_lokaal_ip_adres():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.connect(("8.8.8.8", 80))
            return sock.getsockname()[0]
    except Exception:
        try:
            return socket.gethostbyname(socket.gethostname())
        except Exception:
            return ""


def maak_informatie_actie(stap):
    if re.fullmatch(
        r"(?:start|run|begin|launch|starten|draai|voer uit)?\s*(?:een\s+)?(?:system|windows|computer|systeem)?\s*(?:scan|diagnostics?|diagnose|integrity check|integriteitscontrole|repair scan|reparatiescan|bestandsscan|sfc scan)",
        stap,
    ):
        return "system scan start"

    if re.fullmatch(
        r"(?:system scan status|system diagnostics status|system scan progress|scan status|status system scan|status systeemscan|systeemscan status|voortgang systeemscan|diagnose status|diagnostics status)",
        stap,
    ):
        return "system scan status"

    if re.fullmatch(r"(?:system info|system status|computer info|computer status|systeeminfo|systeem status|computerinfo|computerstatus)", stap):
        return "system info"

    if re.fullmatch(r"(?:battery|battery status|batterij|batterij status)", stap):
        return "battery status"

    if re.fullmatch(r"(?:disk space|free space|storage status|schijfruimte|vrije ruimte|opslagstatus)", stap):
        return "disk space"

    if re.fullmatch(r"(?:ip address|local ip|my ip|ip-adres|mijn ip|wat is mijn ip)", stap):
        return "ip address"

    if re.fullmatch(r"(?:time|current time|date|today|what time is it|what is the time|hoe laat is het|wat is de tijd|wat is de datum|datum)", stap):
        return "current time"

    return ""


def maak_bestands_actie(originele_stap, stap):
    if re.match(r"^(?:move|verplaats)\s+(?:mouse|cursor|muis|venster|window)\b", stap):
        return ""

    list_match = re.match(
        r"^(?:list|show|toon|laat zien)(?:\s+(?:de|het|the))?\s+(?:files|bestanden|contents|inhoud|folder contents|mapinhoud)(?:\s+(?:of|in|van))?\s*(.*)$",
        originele_stap,
        re.IGNORECASE,
    )
    if list_match:
        doel_pad = schoon_pad_argument(list_match.group(1)) or "."
        return f"list folder::{doel_pad}"

    read_match = re.match(
        r"^(?:read|lees|show file|toon bestand|show contents of file|toon inhoud van bestand)\s+(.+)$",
        originele_stap,
        re.IGNORECASE,
    )
    if read_match:
        doel_pad = schoon_pad_argument(read_match.group(1))
        if doel_pad:
            return f"read file::{doel_pad}"

    samenvat_match = re.match(
        r"^(?:summari[sz]e|samenvat|vat samen)(?:\s+(?:file|bestand|document))?\s+(.+)$",
        originele_stap,
        re.IGNORECASE,
    )
    if samenvat_match:
        doel_pad = schoon_pad_argument(samenvat_match.group(1))
        if doel_pad:
            return f"summarize file::{doel_pad}"

    overschrijf_match = re.match(
        r"^(?:overwrite|replace(?:\s+contents(?:\s+of)?)?|overschrijf|schrijf over)(?:\s+(?:file|bestand))?\s+(.+?)\s+(?:with|met)\s+(.+)$",
        originele_stap,
        re.IGNORECASE,
    )
    if overschrijf_match:
        doel_pad = schoon_pad_argument(overschrijf_match.group(1))
        inhoud = strip_omringende_quotes(overschrijf_match.group(2).strip())
        if doel_pad and inhoud:
            return f"overwrite file::{doel_pad}||{inhoud}"

    herschrijf_match = re.match(
        r"^(?:rewrite|herschrijf)(?:\s+(?:file|bestand))?\s+(.+?)\s+(?:to|into|naar|zodat|with|met)\s+(.+)$",
        originele_stap,
        re.IGNORECASE,
    )
    if herschrijf_match:
        doel_pad = schoon_pad_argument(herschrijf_match.group(1))
        instructie = strip_omringende_quotes(herschrijf_match.group(2).strip())
        if doel_pad and instructie:
            return f"rewrite file::{doel_pad}||{instructie}"

    tekst_naar_bestand_match = re.match(
        r"^(?:append|add|write|schrijf|voeg toe|bewaar)\s+(.+)$",
        originele_stap,
        re.IGNORECASE,
    )
    if tekst_naar_bestand_match:
        tekst_inhoud, doel_pad = split_tekst_en_pad_opdracht(tekst_naar_bestand_match.group(1))
        if tekst_inhoud and doel_pad:
            return f"append file::{doel_pad}||{tekst_inhoud}"

    search_match = re.match(
        r"^(?:search|find|zoek|vind)\s+(?:in\s+)?(?:files|file|bestanden|bestand|project|workspace|tekst)\s+(?:for|naar|op)?\s+(.+)$",
        originele_stap,
        re.IGNORECASE,
    )
    if search_match:
        zoektekst = strip_omringende_quotes(search_match.group(1).strip(" ."))
        if zoektekst:
            return f"search files::{zoektekst}"

    create_file_match = re.match(r"^(?:create|make|maak)\s+(?:a\s+|an\s+|een\s+|new\s+|nieuw\s+|nieuwe\s+)?(?:file|bestand)\s+(.+)$", originele_stap, re.IGNORECASE)
    if create_file_match:
        doel_pad = schoon_pad_argument(create_file_match.group(1))
        if doel_pad:
            return f"create file {doel_pad}"

    copy_match = re.match(r"^(?:copy|kopieer)\s+(.+?)\s+(?:to|naar)\s+(.+)$", originele_stap, re.IGNORECASE)
    if copy_match:
        bron, bestemming = schoon_pad_argument(copy_match.group(1)), schoon_pad_argument(copy_match.group(2))
        if bron and bestemming:
            return f"copy path::{bron}||{bestemming}"

    move_match = re.match(r"^(?:move|verplaats)\s+(.+?)\s+(?:to|naar)\s+(.+)$", originele_stap, re.IGNORECASE)
    if move_match:
        bron, bestemming = schoon_pad_argument(move_match.group(1)), schoon_pad_argument(move_match.group(2))
        if bron and bestemming:
            return f"move path::{bron}||{bestemming}"

    rename_match = re.match(r"^(?:rename|hernoem)\s+(.+?)\s+(?:to|as|naar)\s+(.+)$", originele_stap, re.IGNORECASE)
    if rename_match:
        bron, bestemming = schoon_pad_argument(rename_match.group(1)), schoon_pad_argument(rename_match.group(2))
        if bron and bestemming:
            return f"rename path::{bron}||{bestemming}"

    delete_match = re.match(r"^(?:delete|remove|verwijder|wis)\s+(.+)$", originele_stap, re.IGNORECASE)
    if delete_match:
        doel_pad = schoon_pad_argument(delete_match.group(1))
        if doel_pad:
            return f"delete path::{doel_pad}"

    return ""


def maak_planner_actie(originele_stap, stap):
    if re.fullmatch(r"(?:show|list|toon|laat zien)(?:\s+(?:my|mijn))?\s+(?:agenda|planner)", stap):
        return "agenda show"

    if re.fullmatch(r"(?:show|list|toon|laat zien)(?:\s+(?:my|mijn))?\s+(?:timers?)", stap):
        return "timer list"

    if re.fullmatch(r"(?:show|list|toon|laat zien)(?:\s+(?:my|mijn))?\s+(?:reminders|herinneringen?)", stap):
        return "reminder list"

    if re.fullmatch(r"(?:show|list|toon|laat zien)(?:\s+(?:my|mijn))?\s+(?:tasks|taken)", stap):
        return "task list"

    timer_match = re.match(r"^(?:(?:set|start|create|maak|zet)(?:\s+(?:a|een))?\s*timer|timer)(?:\s+(?:for|van|op))?\s+(.+)$", originele_stap, re.IGNORECASE)
    if timer_match:
        seconden = parseer_tijdsduur_seconden(timer_match.group(1))
        if seconden > 0:
            return f"timer create::{seconden}"

    reminder_match = re.match(
        r"^(?:remind me|set reminder|create reminder|maak herinnering|herinner me)(?:\s+(?:in|over|for|voor))\s+(.+?)\s+(?:to|about|aan|om)\s+(.+)$",
        originele_stap,
        re.IGNORECASE,
    )
    if reminder_match:
        seconden = parseer_tijdsduur_seconden(reminder_match.group(1))
        bericht = reminder_match.group(2).strip(" .")
        if seconden > 0 and bericht:
            return f"reminder create::{seconden}||{bericht}"

    cancel_timer_match = re.match(r"^(?:cancel|stop|annuleer)\s+timer\s*(.*)$", originele_stap, re.IGNORECASE)
    if cancel_timer_match:
        query = cancel_timer_match.group(1).strip() or "last"
        return f"timer cancel::{query}"

    cancel_reminder_match = re.match(r"^(?:cancel|remove|delete|annuleer|verwijder|wis)\s+(?:reminder|herinnering)\s*(.*)$", originele_stap, re.IGNORECASE)
    if cancel_reminder_match:
        query = cancel_reminder_match.group(1).strip() or "last"
        return f"reminder cancel::{query}"

    add_task_match = re.match(r"^(?:add task|new task|create task|maak taak|taak toevoegen)\s+(.+)$", originele_stap, re.IGNORECASE)
    if add_task_match:
        taak = add_task_match.group(1).strip(" .")
        if taak:
            return f"task add::{taak}"

    done_task_match = re.match(r"^(?:complete task|finish task|done with task|mark task done|voltooi taak|rond taak af|taak gedaan)\s+(.+)$", originele_stap, re.IGNORECASE)
    if done_task_match:
        return f"task done::{done_task_match.group(1).strip()}"

    remove_task_match = re.match(r"^(?:remove task|delete task|cancel task|verwijder taak|wis taak|annuleer taak)\s+(.+)$", originele_stap, re.IGNORECASE)
    if remove_task_match:
        return f"task remove::{remove_task_match.group(1).strip()}"

    return ""


def is_veilig_app_doel(doel_tekst):
    return bool(re.fullmatch(r"[a-z0-9][a-z0-9 ._-]{1,60}", schoon_computerdoel(doel_tekst)))


def maak_systeem_actie(stap):
    if re.fullmatch(r"(?:confirm|bevestig)(?:\s+.+)?", stap):
        return "confirm pending action"

    if re.fullmatch(r"(?:cancel|annuleer|laat maar|niet doen)(?:\s+.+)?", stap):
        return "cancel pending action"

    for actie, data in DANGEROUS_SYSTEM_ACTIONS.items():
        if stap in data["aliases"]:
            return actie

    direct_setting = vind_alias_sleutel(stap, SYSTEM_SETTING_TARGETS)
    if direct_setting:
        return f"open setting {direct_setting}"

    direct_app = vind_alias_sleutel(stap, SYSTEM_APP_TARGETS)
    if direct_app:
        return f"open app {direct_app}"

    direct_folder = resolve_folder_pad(stap)
    if direct_folder and vind_alias_sleutel(stap, COMMON_FOLDER_TARGETS):
        return f"open folder {direct_folder}"

    folder_match = re.match(r"^(?:open|openen|start|launch)\s+(?:de|het|the|a|een\s+)?(?:folder|map|directory)\s+(.+)$", stap)
    if folder_match:
        folder_pad = resolve_folder_pad(folder_match.group(1))
        if folder_pad:
            return f"open folder {folder_pad}"

    file_match = re.match(r"^(?:open|openen|start|launch)\s+(?:de|het|the|a|een\s+)?(?:file|bestand)\s+(.+)$", stap)
    if file_match:
        bestand_pad = resolve_bestand_pad(file_match.group(1))
        if bestand_pad:
            return f"open file {bestand_pad}"

    open_match = re.match(r"^(?:open|openen|start|launch)\s+(.+)$", stap)
    if not open_match:
        return ""

    doel_tekst = schoon_computerdoel(open_match.group(1))

    setting_sleutel = vind_alias_sleutel(doel_tekst, SYSTEM_SETTING_TARGETS)
    if setting_sleutel:
        return f"open setting {setting_sleutel}"

    folder_pad = resolve_folder_pad(doel_tekst)
    if folder_pad:
        return f"open folder {folder_pad}"

    app_sleutel = vind_alias_sleutel(doel_tekst, SYSTEM_APP_TARGETS)
    if app_sleutel:
        return f"open app {app_sleutel}"

    if is_veilig_app_doel(doel_tekst):
        return f"open app raw::{doel_tekst}"

    return ""


def open_windows_doel(doel):
    if not hasattr(os, "startfile"):
        raise RuntimeError("This system action is only available on Windows")
    os.startfile(str(doel))


def voer_bevestigde_systeemactie_uit(actie):
    if actie == "lock computer":
        ctypes.windll.user32.LockWorkStation()
    elif actie == "sleep computer":
        subprocess.Popen(["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"])
    elif actie == "restart computer":
        subprocess.Popen(["shutdown", "/r", "/t", "0"])
    elif actie == "shutdown computer":
        subprocess.Popen(["shutdown", "/s", "/t", "0"])
    elif actie == "sign out":
        subprocess.Popen(["shutdown", "/l"])

    details = DANGEROUS_SYSTEM_ACTIONS[actie]
    return tekst_voor_taal(details["done_en"], details["done_nl"])


def voer_verwijder_pad_uit(actie):
    doel_tekst = actie.split("::", 1)[1]
    doel_pad = resolve_bron_pad_voor_operatie(doel_tekst)
    if not doel_pad:
        return tekst_voor_taal(
            f"Could not find path: {doel_tekst}",
            f"Kon pad niet vinden: {doel_tekst}"
        )

    try:
        if Path(doel_pad).is_dir():
            shutil.rmtree(doel_pad)
        else:
            Path(doel_pad).unlink()
        return tekst_voor_taal(
            f"Deleted: {doel_pad}",
            f"Verwijderd: {doel_pad}"
        )
    except Exception as e:
        return tekst_voor_taal(
            f"Error deleting path: {e}",
            f"Fout bij verwijderen van pad: {e}"
        )


def voer_bevestigde_actie_uit(actie):
    if actie in DANGEROUS_SYSTEM_ACTIONS:
        return voer_bevestigde_systeemactie_uit(actie)

    if actie.startswith("delete path::"):
        return voer_verwijder_pad_uit(actie)

    if actie.startswith("overwrite file::"):
        return voer_overschrijf_bestand_uit(actie)

    if actie.startswith("rewrite file::"):
        return voer_herschrijf_bestand_uit(actie)

    return tekst_voor_taal(
        "There is no pending action to confirm.",
        "Er is geen wachtende actie om te bevestigen."
    )


def voer_maak_bestand_uit(actie):
    doel_tekst = re.sub(r"^create file\s*", "", actie).strip()
    doel_pad = resolve_pad_voor_operatie(doel_tekst)
    if not doel_pad:
        return tekst_voor_taal("No file path provided.", "Geen bestandspad opgegeven.")

    try:
        doel_pad.parent.mkdir(parents=True, exist_ok=True)
        if doel_pad.exists():
            return tekst_voor_taal(
                f"File already exists: {doel_pad}",
                f"Bestand bestaat al: {doel_pad}"
            )
        doel_pad.touch()
        return tekst_voor_taal(
            f"File created: {doel_pad}",
            f"Bestand aangemaakt: {doel_pad}"
        )
    except Exception as e:
        return tekst_voor_taal(
            f"Error creating file: {e}",
            f"Fout bij aanmaken van bestand: {e}"
        )


def voer_kopieer_pad_uit(actie):
    bron_tekst, bestemming_tekst = split_pad_payload(actie)
    bron_pad = resolve_bron_pad_voor_operatie(bron_tekst)
    if not bron_pad:
        return tekst_voor_taal(f"Could not find source: {bron_tekst}", f"Kon bron niet vinden: {bron_tekst}")

    bestemming_pad = resolve_bestemming_pad_voor_operatie(bron_pad, bestemming_tekst)
    if not bestemming_pad:
        return tekst_voor_taal("No destination provided.", "Geen bestemming opgegeven.")
    if bestemming_pad.exists():
        return tekst_voor_taal(
            f"Destination already exists: {bestemming_pad}",
            f"Bestemming bestaat al: {bestemming_pad}"
        )

    try:
        bestemming_pad.parent.mkdir(parents=True, exist_ok=True)
        if Path(bron_pad).is_dir():
            shutil.copytree(bron_pad, bestemming_pad)
        else:
            shutil.copy2(bron_pad, bestemming_pad)
        return tekst_voor_taal(
            f"Copied to {bestemming_pad}",
            f"Gekopieerd naar {bestemming_pad}"
        )
    except Exception as e:
        return tekst_voor_taal(f"Error copying path: {e}", f"Fout bij kopieren van pad: {e}")


def voer_verplaats_pad_uit(actie):
    bron_tekst, bestemming_tekst = split_pad_payload(actie)
    bron_pad = resolve_bron_pad_voor_operatie(bron_tekst)
    if not bron_pad:
        return tekst_voor_taal(f"Could not find source: {bron_tekst}", f"Kon bron niet vinden: {bron_tekst}")

    bestemming_pad = resolve_bestemming_pad_voor_operatie(bron_pad, bestemming_tekst)
    if not bestemming_pad:
        return tekst_voor_taal("No destination provided.", "Geen bestemming opgegeven.")
    if bestemming_pad.exists():
        return tekst_voor_taal(
            f"Destination already exists: {bestemming_pad}",
            f"Bestemming bestaat al: {bestemming_pad}"
        )

    try:
        bestemming_pad.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(bron_pad), str(bestemming_pad))
        return tekst_voor_taal(
            f"Moved to {bestemming_pad}",
            f"Verplaatst naar {bestemming_pad}"
        )
    except Exception as e:
        return tekst_voor_taal(f"Error moving path: {e}", f"Fout bij verplaatsen van pad: {e}")


def voer_hernoem_pad_uit(actie):
    bron_tekst, bestemming_tekst = split_pad_payload(actie)
    bron_pad = resolve_bron_pad_voor_operatie(bron_tekst)
    if not bron_pad:
        return tekst_voor_taal(f"Could not find source: {bron_tekst}", f"Kon bron niet vinden: {bron_tekst}")

    ruwe_bestemming = schoon_pad_argument(bestemming_tekst)
    if not ruwe_bestemming:
        return tekst_voor_taal("No new name provided.", "Geen nieuwe naam opgegeven.")

    if not Path(ruwe_bestemming).is_absolute() and not any(scheiding in ruwe_bestemming for scheiding in ("\\", "/")):
        bestemming_pad = Path(bron_pad).with_name(ruwe_bestemming)
    else:
        bestemming_pad = resolve_bestemming_pad_voor_operatie(bron_pad, ruwe_bestemming)

    if not bestemming_pad:
        return tekst_voor_taal("No valid new path provided.", "Geen geldig nieuw pad opgegeven.")
    if bestemming_pad.exists():
        return tekst_voor_taal(
            f"Destination already exists: {bestemming_pad}",
            f"Bestemming bestaat al: {bestemming_pad}"
        )

    try:
        bestemming_pad.parent.mkdir(parents=True, exist_ok=True)
        Path(bron_pad).rename(bestemming_pad)
        return tekst_voor_taal(
            f"Renamed to {bestemming_pad}",
            f"Hernoemd naar {bestemming_pad}"
        )
    except Exception as e:
        return tekst_voor_taal(f"Error renaming path: {e}", f"Fout bij hernoemen van pad: {e}")


def voer_planner_actie_uit(actie):
    if actie == "agenda show":
        return agenda_overzicht_bericht()

    if actie == "timer list":
        return planner_lijst_bericht("timers")

    if actie == "reminder list":
        return planner_lijst_bericht("reminders")

    if actie == "task list":
        return planner_lijst_bericht("tasks")

    if actie.startswith("timer create::"):
        seconden = max(1, int(actie.split("::", 1)[1]))
        item = voeg_timer_toe(seconden)
        return tekst_voor_taal(
            f"Timer #{item['id']} set for {formatteer_duur_compact(seconden)}.",
            f"Timer #{item['id']} gezet voor {formatteer_duur_compact(seconden)}."
        )

    if actie.startswith("reminder create::"):
        payload = actie.split("::", 1)[1].split("||", 1)
        seconden = max(1, int(payload[0]))
        bericht = payload[1].strip() if len(payload) > 1 else ""
        if not bericht:
            return tekst_voor_taal("No reminder text provided.", "Geen herinneringstekst opgegeven.")
        item = voeg_herinnering_toe(seconden, bericht)
        return tekst_voor_taal(
            f"Reminder #{item['id']} set for {formatteer_duur_compact(seconden)}: {item['message']}",
            f"Herinnering #{item['id']} gezet voor {formatteer_duur_compact(seconden)}: {item['message']}"
        )

    if actie.startswith("timer cancel::"):
        query = actie.split("::", 1)[1]
        items = annuleer_planning_items("timers", query)
        if not items:
            return tekst_voor_taal("No matching active timer found.", "Geen passende actieve timer gevonden.")
        return tekst_voor_taal(
            "Cancelled timer(s): " + "; ".join(f"#{item['id']}" for item in items),
            "Timer(s) geannuleerd: " + "; ".join(f"#{item['id']}" for item in items)
        )

    if actie.startswith("reminder cancel::"):
        query = actie.split("::", 1)[1]
        items = annuleer_planning_items("reminders", query)
        if not items:
            return tekst_voor_taal("No matching reminder found.", "Geen passende herinnering gevonden.")
        return tekst_voor_taal(
            "Cancelled reminder(s): " + "; ".join(f"#{item['id']}" for item in items),
            "Herinnering(en) geannuleerd: " + "; ".join(f"#{item['id']}" for item in items)
        )

    if actie.startswith("task add::"):
        resultaat = voeg_taak_toe(actie.split("::", 1)[1])
        if resultaat == "limit":
            return tekst_voor_taal("Your task list is full. Complete or remove a task first.", "Je takenlijst zit vol. Rond eerst een taak af of verwijder er een.")
        if resultaat == "duplicate":
            return tekst_voor_taal("That task is already on your list.", "Die taak staat al op je lijst.")
        if not resultaat:
            return tekst_voor_taal("No task text provided.", "Geen taaktekst opgegeven.")
        return tekst_voor_taal(
            f"Task #{resultaat['id']} added: {resultaat['text']}",
            f"Taak #{resultaat['id']} toegevoegd: {resultaat['text']}"
        )

    if actie.startswith("task done::"):
        taak = voltooi_taak(actie.split("::", 1)[1])
        if not taak:
            return tekst_voor_taal("No matching open task found.", "Geen passende open taak gevonden.")
        return tekst_voor_taal(
            f"Completed task #{taak['id']}: {taak['text']}",
            f"Taak #{taak['id']} afgerond: {taak['text']}"
        )

    if actie.startswith("task remove::"):
        taak = verwijder_taak(actie.split("::", 1)[1])
        if not taak:
            return tekst_voor_taal("No matching open task found.", "Geen passende open taak gevonden.")
        return tekst_voor_taal(
            f"Removed task #{taak['id']}: {taak['text']}",
            f"Taak #{taak['id']} verwijderd: {taak['text']}"
        )

    return tekst_voor_taal("Unknown planner action", "Onbekende planneractie")


def voer_lijst_map_uit(actie):
    doel_tekst = actie.split("::", 1)[1].strip()
    doel_pad = resolve_folder_pad(doel_tekst) if doel_tekst not in {"", "."} else Path.cwd()
    if not doel_pad:
        return tekst_voor_taal(
            f"Could not find folder: {doel_tekst}",
            f"Kon map niet vinden: {doel_tekst}"
        )

    try:
        items, regels = lijst_map_inhoud(doel_pad)
    except Exception as e:
        return tekst_voor_taal(
            f"Error listing folder: {e}",
            f"Fout bij tonen van mapinhoud: {e}"
        )

    if not items:
        return tekst_voor_taal(
            f"Folder is empty: {doel_pad}",
            f"Map is leeg: {doel_pad}"
        )

    extra = "" if len(items) <= len(regels) else tekst_voor_taal("; more items are available", "; er zijn meer items beschikbaar")
    return tekst_voor_taal(
        f"Contents of {doel_pad}: " + "; ".join(regels) + extra,
        f"Inhoud van {doel_pad}: " + "; ".join(regels) + extra
    )


def voer_lees_bestand_uit(actie):
    doel_tekst = actie.split("::", 1)[1].strip()
    doel_pad = resolve_bestand_pad(doel_tekst)
    if not doel_pad:
        return tekst_voor_taal(
            f"Could not find file: {doel_tekst}",
            f"Kon bestand niet vinden: {doel_tekst}"
        )

    try:
        preview = lees_tekst_preview(doel_pad)
    except ValueError:
        return tekst_voor_taal(
            f"I can only preview text files. This looks binary: {doel_pad}",
            f"Ik kan alleen tekstbestanden tonen. Dit lijkt binair: {doel_pad}"
        )
    except Exception as e:
        return tekst_voor_taal(
            f"Error reading file: {e}",
            f"Fout bij lezen van bestand: {e}"
        )

    if not preview:
        return tekst_voor_taal(
            f"File is empty: {doel_pad}",
            f"Bestand is leeg: {doel_pad}"
        )

    return tekst_voor_taal(
        f"Preview of {doel_pad}:\n{preview}",
        f"Voorbeeld van {doel_pad}:\n{preview}"
    )


def voer_append_bestand_uit(actie):
    payload = actie.split("::", 1)[1]
    if "||" not in payload:
        return tekst_voor_taal("No text or file path provided.", "Geen tekst of bestandspad opgegeven.")

    doel_tekst, tekst = payload.split("||", 1)
    doel_pad = resolve_pad_voor_operatie(doel_tekst)
    if not doel_pad:
        return tekst_voor_taal("No valid file path provided.", "Geen geldig bestandspad opgegeven.")

    tekst = str(tekst or "").strip()
    if not tekst:
        return tekst_voor_taal("No text provided.", "Geen tekst opgegeven.")

    try:
        doel_pad.parent.mkdir(parents=True, exist_ok=True)
        bestaand_einde = ""
        if doel_pad.exists():
            try:
                bestaand_einde = doel_pad.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                bestaand_einde = ""
        prefix = "" if not bestaand_einde or bestaand_einde.endswith(("\n", "\r")) else "\n"
        with open(doel_pad, "a", encoding="utf-8") as f:
            f.write(prefix + tekst)
        return tekst_voor_taal(
            f"Saved text to {doel_pad}",
            f"Tekst opgeslagen in {doel_pad}"
        )
    except Exception as e:
        return tekst_voor_taal(
            f"Error writing file: {e}",
            f"Fout bij schrijven naar bestand: {e}"
        )


def voer_samenvatting_bestand_uit(actie):
    doel_tekst = actie.split("::", 1)[1].strip()
    doel_pad = resolve_bestand_pad(doel_tekst)
    if not doel_pad:
        return tekst_voor_taal(
            f"Could not find file: {doel_tekst}",
            f"Kon bestand niet vinden: {doel_tekst}"
        )

    try:
        return vat_tekstbestand_samen(doel_pad)
    except ValueError as e:
        fout = str(e).lower()
        if fout == "binary file":
            return tekst_voor_taal(
                f"I can only summarize text files. This looks binary: {doel_pad}",
                f"Ik kan alleen tekstbestanden samenvatten. Dit lijkt binair: {doel_pad}"
            )
        if fout == "file too large":
            return tekst_voor_taal(
                f"That file is too large to summarize safely: {doel_pad}",
                f"Dat bestand is te groot om veilig samen te vatten: {doel_pad}"
            )
        return tekst_voor_taal(f"File summary error: {e}", f"Fout bij bestandssamenvatting: {e}")
    except Exception as e:
        return tekst_voor_taal(f"File summary error: {e}", f"Fout bij bestandssamenvatting: {e}")


def voer_overschrijf_bestand_uit(actie):
    payload = actie.split("::", 1)[1]
    if "||" not in payload:
        return tekst_voor_taal("No text or file path provided.", "Geen tekst of bestandspad opgegeven.")

    doel_tekst, tekst = payload.split("||", 1)
    doel_pad = resolve_pad_voor_operatie(doel_tekst)
    if not doel_pad:
        return tekst_voor_taal("No valid file path provided.", "Geen geldig bestandspad opgegeven.")

    try:
        if doel_pad.exists() and doel_pad.is_file() and b"\x00" in doel_pad.read_bytes()[:4096]:
            return tekst_voor_taal(
                f"I can only overwrite text files. This looks binary: {doel_pad}",
                f"Ik kan alleen tekstbestanden overschrijven. Dit lijkt binair: {doel_pad}"
            )

        doel_pad.parent.mkdir(parents=True, exist_ok=True)
        doel_pad.write_text(str(tekst), encoding="utf-8")
        return tekst_voor_taal(
            f"File overwritten: {doel_pad}",
            f"Bestand overschreven: {doel_pad}"
        )
    except Exception as e:
        return tekst_voor_taal(
            f"Error overwriting file: {e}",
            f"Fout bij overschrijven van bestand: {e}"
        )


def voer_herschrijf_bestand_uit(actie):
    payload = actie.split("::", 1)[1]
    if "||" not in payload:
        return tekst_voor_taal("No instruction or file path provided.", "Geen instructie of bestandspad opgegeven.")

    doel_tekst, instructie = payload.split("||", 1)
    doel_pad = resolve_bestand_pad(doel_tekst)
    if not doel_pad:
        return tekst_voor_taal(
            f"Could not find file: {doel_tekst}",
            f"Kon bestand niet vinden: {doel_tekst}"
        )

    try:
        inhoud = lees_tekstbestand_volledig(doel_pad, max_tekens=12000)
        nieuwe_inhoud = herschrijf_tekst_met_ai(doel_pad.name, inhoud, instructie)
        doel_pad.write_text(nieuwe_inhoud, encoding="utf-8")
        return tekst_voor_taal(
            f"File rewritten: {doel_pad}",
            f"Bestand herschreven: {doel_pad}"
        )
    except ValueError as e:
        fout = str(e).lower()
        if fout == "binary file":
            return tekst_voor_taal(
                f"I can only rewrite text files. This looks binary: {doel_pad}",
                f"Ik kan alleen tekstbestanden herschrijven. Dit lijkt binair: {doel_pad}"
            )
        if fout == "file too large":
            return tekst_voor_taal(
                f"That file is too large to rewrite safely: {doel_pad}",
                f"Dat bestand is te groot om veilig te herschrijven: {doel_pad}"
            )
        return tekst_voor_taal(f"File rewrite error: {e}", f"Fout bij herschrijven van bestand: {e}")
    except Exception as e:
        return tekst_voor_taal(
            f"File rewrite error: {e}",
            f"Fout bij herschrijven van bestand: {e}"
        )


def voer_zoek_bestanden_uit(actie):
    zoektekst = actie.split("::", 1)[1].strip()
    resultaten = zoek_bestanden_in_workspace(zoektekst)
    if not resultaten:
        return tekst_voor_taal(
            f"No workspace matches found for: {zoektekst}",
            f"Geen workspace-resultaten gevonden voor: {zoektekst}"
        )

    regels = []
    for _, pad, lijnnummer, snippet in resultaten:
        if lijnnummer and snippet:
            regels.append(f"{pad}:{lijnnummer} {snippet}")
        else:
            regels.append(pad)

    return tekst_voor_taal(
        f"Workspace matches for {zoektekst}: " + "; ".join(regels),
        f"Workspace-resultaten voor {zoektekst}: " + "; ".join(regels)
    )


def voer_systeeminfo_uit(actie):
    if actie == "battery status":
        return haal_batterij_status() or tekst_voor_taal(
            "Battery information is not available.",
            "Batterijinformatie is niet beschikbaar."
        )

    if actie == "disk space":
        try:
            basis = Path.cwd().anchor or str(Path.cwd())
            totaal, gebruikt, vrij = shutil.disk_usage(basis)
            return tekst_voor_taal(
                f"Disk space on {basis}: {formatteer_bestandsgrootte(vrij)} free of {formatteer_bestandsgrootte(totaal)}",
                f"Schijfruimte op {basis}: {formatteer_bestandsgrootte(vrij)} vrij van {formatteer_bestandsgrootte(totaal)}"
            )
        except Exception as e:
            return tekst_voor_taal(f"Error reading disk space: {e}", f"Fout bij lezen van schijfruimte: {e}")

    if actie == "ip address":
        ip_adres = haal_lokaal_ip_adres()
        if ip_adres:
            return tekst_voor_taal(f"Local IP address: {ip_adres}", f"Lokaal IP-adres: {ip_adres}")
        return tekst_voor_taal("I could not determine the local IP address.", "Ik kon het lokale IP-adres niet bepalen.")

    if actie == "current time":
        return tekst_voor_taal(
            "Current time: " + time.strftime("%A %d %B %Y %H:%M"),
            "Huidige tijd: " + time.strftime("%A %d %B %Y %H:%M")
        )

    batterij = haal_batterij_status()
    ip_adres = haal_lokaal_ip_adres()
    try:
        basis = Path.cwd().anchor or str(Path.cwd())
        totaal, gebruikt, vrij = shutil.disk_usage(basis)
        schijfruimte = tekst_voor_taal(
            f"Free disk space: {formatteer_bestandsgrootte(vrij)} of {formatteer_bestandsgrootte(totaal)}",
            f"Vrije schijfruimte: {formatteer_bestandsgrootte(vrij)} van {formatteer_bestandsgrootte(totaal)}"
        )
    except Exception:
        schijfruimte = ""

    regels = [
        tekst_voor_taal(f"Computer name: {os.environ.get('COMPUTERNAME', 'unknown')}", f"Computernaam: {os.environ.get('COMPUTERNAME', 'onbekend')}"),
        tekst_voor_taal(f"Platform: {platform.system()} {platform.release()}", f"Platform: {platform.system()} {platform.release()}"),
        tekst_voor_taal("Current time: " + time.strftime("%A %d %B %Y %H:%M"), "Huidige tijd: " + time.strftime("%A %d %B %Y %H:%M")),
    ]
    if batterij:
        regels.append(batterij)
    if schijfruimte:
        regels.append(schijfruimte)
    if ip_adres:
        regels.append(tekst_voor_taal(f"Local IP: {ip_adres}", f"Lokaal IP: {ip_adres}"))
    return "; ".join(regels)


def automatisering_actief():
    return GESPREK_CONTEXT.get("automatisering_actief_tot", 0.0) > time.time()


def activeer_automatisering_modus():
    GESPREK_CONTEXT["automatisering_actief_tot"] = time.time() + AUTOMATISERING_TIMEOUT_SECONDEN


def deactiveer_automatisering_modus():
    GESPREK_CONTEXT["automatisering_actief_tot"] = 0.0


def automatisering_status_bericht():
    if not instellingen.get("computerbesturing_toestaan", False):
        return tekst_voor_taal(
            "Advanced computer control is off in Settings.",
            "Geavanceerde computerbesturing staat uit in Instellingen."
        )

    resterend = max(0, int(GESPREK_CONTEXT.get("automatisering_actief_tot", 0.0) - time.time()))
    if resterend <= 0:
        return tekst_voor_taal(
            "Automation mode is off. Say enable automation mode first.",
            "Automation-modus staat uit. Zeg eerst schakel automation-modus in."
        )

    minuten = max(1, (resterend + 59) // 60)
    return tekst_voor_taal(
        f"Automation mode is active for about {minuten} more minute(s).",
        f"Automation-modus is nog ongeveer {minuten} minuut/minuten actief."
    )


def geavanceerde_besturing_geblokkeerd(actie):
    if not instellingen.get("computerbesturing_toestaan", False):
        return tekst_voor_taal(
            "Enable advanced computer control in Settings first.",
            "Zet eerst geavanceerde computerbesturing aan in Instellingen."
        )

    if not automatisering_actief():
        return tekst_voor_taal(
            "Automation mode is off. Say enable automation mode first. It stays active for 5 minutes.",
            "Automation-modus staat uit. Zeg eerst schakel automation-modus in. Die blijft 5 minuten actief."
        )

    if actie.startswith(("mouse ", "type text::", "press key::", "press hotkey::", "window ", "run macro ")) and not AUTOMATISERING_BESCHIKBAAR:
        return tekst_voor_taal(
            "Automation support is not available because PyAutoGUI could not be loaded.",
            "Automation-ondersteuning is niet beschikbaar omdat PyAutoGUI niet geladen kon worden."
        )

    if actie.startswith("volume ") and not actie.startswith("volume set ") and not AUTOMATISERING_BESCHIKBAAR:
        return tekst_voor_taal(
            "Automation support is not available because PyAutoGUI could not be loaded.",
            "Automation-ondersteuning is niet beschikbaar omdat PyAutoGUI niet geladen kon worden."
        )

    return ""


def normaliseer_toets_combinatie(tekst):
    samengevoegd = str(tekst or "").lower()
    samengevoegd = samengevoegd.replace("page up", "pageup").replace("page down", "pagedown")
    samengevoegd = samengevoegd.replace("arrow up", "up").replace("arrow down", "down")
    samengevoegd = samengevoegd.replace("arrow left", "left").replace("arrow right", "right")
    tokens = [token for token in re.split(r"(?:\s*\+\s*|\s+)", samengevoegd) if token and token not in {"and", "en"}]
    resultaat = []

    for token in tokens:
        if token in TOETS_ALIASES:
            resultaat.append(TOETS_ALIASES[token])
        elif re.fullmatch(r"f(?:[1-9]|1[0-2])", token):
            resultaat.append(token)
        elif re.fullmatch(r"[a-z0-9]", token):
            resultaat.append(token)
        else:
            return []

    return resultaat


def vind_macro_sleutel(stap):
    for sleutel, details in APP_MACROS.items():
        if stap in details["aliases"]:
            return sleutel
    return ""


def activeer_venster(app_sleutel, probeer_start=True):
    if gw is None:
        return False

    for hint in WINDOW_TITLE_HINTS.get(app_sleutel, []):
        try:
            vensters = [venster for venster in gw.getWindowsWithTitle(hint) if getattr(venster, "title", "").strip()]
        except Exception:
            vensters = []

        for venster in vensters:
            try:
                if getattr(venster, "isMinimized", False):
                    venster.restore()
                    time.sleep(0.2)
                venster.activate()
                time.sleep(0.2)
                return True
            except Exception:
                continue

    if probeer_start and app_sleutel in APP_LAUNCH_COMMANDS:
        try:
            subprocess.Popen(APP_LAUNCH_COMMANDS[app_sleutel])
            time.sleep(1.2)
        except Exception:
            return False
        return activeer_venster(app_sleutel, False)

    return False


def vind_focus_app_sleutel(doel_tekst):
    app_sleutel = vind_alias_sleutel(doel_tekst, SYSTEM_APP_TARGETS)
    if app_sleutel:
        return app_sleutel

    doel = schoon_computerdoel(doel_tekst)
    return doel if doel in WINDOW_TITLE_HINTS else ""


def haal_actief_venster():
    if gw is None:
        return None

    try:
        return gw.getActiveWindow()
    except Exception:
        return None


def verplaats_actief_venster(richting, afstand):
    venster = haal_actief_venster()
    if not venster:
        raise RuntimeError("No active window found")

    if getattr(venster, "isMinimized", False):
        venster.restore()
        time.sleep(0.15)

    x_offset = (-afstand if richting == "left" else afstand if richting == "right" else 0)
    y_offset = (-afstand if richting == "up" else afstand if richting == "down" else 0)
    venster.moveTo(venster.left + x_offset, venster.top + y_offset)
    return venster


def maak_screenshot_pad():
    screenshot_map = Path.home() / "Pictures" / "Echo Screenshots"
    screenshot_map.mkdir(parents=True, exist_ok=True)
    bestandsnaam = f"echo-screenshot-{time.strftime('%Y%m%d-%H%M%S')}.png"
    return screenshot_map / bestandsnaam


def maak_windows_screenshot(bestemming):
    pad = str(bestemming).replace("'", "''")
    script = f"""
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
$bounds = [System.Windows.Forms.SystemInformation]::VirtualScreen
$bitmap = New-Object System.Drawing.Bitmap $bounds.Width, $bounds.Height
$graphics = [System.Drawing.Graphics]::FromImage($bitmap)
$graphics.CopyFromScreen($bounds.Left, $bounds.Top, 0, 0, $bitmap.Size)
$bitmap.Save('{pad}', [System.Drawing.Imaging.ImageFormat]::Png)
$graphics.Dispose()
$bitmap.Dispose()
"""
    subprocess.run(
        ["powershell", "-NoProfile", "-Command", script],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="ignore",
    )


def haal_wifi_interface_info():
    resultaat = subprocess.run(
        ["netsh", "interface", "show", "interface"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="ignore",
    )

    if resultaat.returncode != 0:
        raise RuntimeError((resultaat.stderr or resultaat.stdout or "netsh failed").strip())

    for regel in resultaat.stdout.splitlines():
        regel = regel.strip()
        if not regel or regel.startswith("Admin") or regel.startswith("Beheer") or regel.startswith("---"):
            continue

        delen = re.split(r"\s{2,}", regel)
        if len(delen) < 4:
            continue

        admin_state, _state, _type, naam = delen[0], delen[1], delen[2], delen[3]
        if re.search(r"wi-?fi|wlan|wireless|draadloos", naam, re.IGNORECASE):
            return {
                "name": naam,
                "enabled": admin_state.lower().startswith(("enabled", "ingeschakeld")),
            }

    raise RuntimeError("No Wi-Fi interface found")


def voer_wifi_actie_uit(modus):
    interface_info = haal_wifi_interface_info()
    doel_enabled = interface_info["enabled"]

    if modus == "toggle":
        doel_enabled = not interface_info["enabled"]
    elif modus == "on":
        doel_enabled = True
    elif modus == "off":
        doel_enabled = False

    subprocess.run(
        ["netsh", "interface", "set", "interface", f"name={interface_info['name']}", f"admin={'enabled' if doel_enabled else 'disabled'}"],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="ignore",
    )

    return tekst_voor_taal(
        f"Wi-Fi turned {'on' if doel_enabled else 'off'}",
        f"Wifi {'ingeschakeld' if doel_enabled else 'uitgeschakeld'}"
    )


def haal_bluetooth_adapter_info():
    script = (
        "$device = Get-PnpDevice -Class Bluetooth | Where-Object { $_.FriendlyName -and $_.FriendlyName -notmatch 'Enumerator' } | "
        "Select-Object -First 1 FriendlyName, Status, InstanceId; if ($device) { $device | ConvertTo-Json -Compress }"
    )
    resultaat = subprocess.run(
        ["powershell", "-NoProfile", "-Command", script],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="ignore",
    )

    if resultaat.returncode != 0 or not resultaat.stdout.strip():
        raise RuntimeError((resultaat.stderr or resultaat.stdout or "Bluetooth adapter not available").strip())

    return json.loads(resultaat.stdout.strip())


def voer_bluetooth_actie_uit(modus):
    adapter_info = haal_bluetooth_adapter_info()
    actief = str(adapter_info.get("Status", "")).lower() == "ok"
    doel_actief = actief

    if modus == "toggle":
        doel_actief = not actief
    elif modus == "on":
        doel_actief = True
    elif modus == "off":
        doel_actief = False

    instance_id = str(adapter_info.get("InstanceId", "")).replace("'", "''")
    script = f"{'Enable' if doel_actief else 'Disable'}-PnpDevice -InstanceId '{instance_id}' -Confirm:$false"
    resultaat = subprocess.run(
        ["powershell", "-NoProfile", "-Command", script],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="ignore",
    )

    if resultaat.returncode != 0:
        raise RuntimeError((resultaat.stderr or resultaat.stdout or "Bluetooth toggle failed").strip())

    return tekst_voor_taal(
        f"Bluetooth turned {'on' if doel_actief else 'off'}",
        f"Bluetooth {'ingeschakeld' if doel_actief else 'uitgeschakeld'}"
    )


def begrens_percentage(waarde):
    return max(0, min(100, int(waarde)))


def percentage_uit_woordtekst(tekst):
    tekst = str(tekst or "").strip().lower()
    tekst = tekst.translate(str.maketrans({
        "ë": "e",
        "é": "e",
        "è": "e",
        "ê": "e",
        "ï": "i",
        "í": "i",
        "ì": "i",
        "á": "a",
        "à": "a",
        "ä": "a",
        "ö": "o",
        "ü": "u",
    }))
    tekst = tekst.replace("%", " ").replace("-", " ")
    tekst = re.sub(r"\b(?:percent|percentage|procent)\b", " ", tekst)
    tekst = re.sub(r"[^a-z0-9\s]", " ", tekst)
    tekst = re.sub(r"\s+", " ", tekst).strip()
    if not tekst:
        return None

    if tekst.isdigit():
        return begrens_percentage(tekst)

    engels_basis = {
        "zero": 0,
        "one": 1,
        "two": 2,
        "three": 3,
        "four": 4,
        "five": 5,
        "six": 6,
        "seven": 7,
        "eight": 8,
        "nine": 9,
        "ten": 10,
        "eleven": 11,
        "twelve": 12,
        "thirteen": 13,
        "fourteen": 14,
        "fifteen": 15,
        "sixteen": 16,
        "seventeen": 17,
        "eighteen": 18,
        "nineteen": 19,
    }
    engels_tientallen = {
        "twenty": 20,
        "thirty": 30,
        "forty": 40,
        "fifty": 50,
        "sixty": 60,
        "seventy": 70,
        "eighty": 80,
        "ninety": 90,
    }
    nederlands_basis = {
        "nul": 0,
        "een": 1,
        "twee": 2,
        "drie": 3,
        "vier": 4,
        "vijf": 5,
        "zes": 6,
        "zeven": 7,
        "acht": 8,
        "negen": 9,
        "tien": 10,
        "elf": 11,
        "twaalf": 12,
        "dertien": 13,
        "veertien": 14,
        "vijftien": 15,
        "zestien": 16,
        "zeventien": 17,
        "achttien": 18,
        "negentien": 19,
    }
    nederlands_tientallen = {
        "twintig": 20,
        "dertig": 30,
        "veertig": 40,
        "vijftig": 50,
        "zestig": 60,
        "zeventig": 70,
        "tachtig": 80,
        "negentig": 90,
    }

    lookup = {
        **engels_basis,
        **nederlands_basis,
        "hundred": 100,
        "one hundred": 100,
        "honderd": 100,
    }

    for woord, waarde in engels_tientallen.items():
        lookup[woord] = waarde
        for eenheid, eenheid_waarde in engels_basis.items():
            if eenheid_waarde <= 0 or eenheid_waarde >= 10:
                continue
            lookup[f"{woord} {eenheid}"] = waarde + eenheid_waarde

    for woord, waarde in nederlands_tientallen.items():
        lookup[woord] = waarde
        for eenheid, eenheid_waarde in nederlands_basis.items():
            if eenheid_waarde <= 0 or eenheid_waarde >= 10:
                continue
            lookup[f"{eenheid} en {woord}"] = waarde + eenheid_waarde
            lookup[f"{eenheid}en{woord}"] = waarde + eenheid_waarde

    if tekst in lookup:
        return lookup[tekst]

    samengevoegd = tekst.replace(" ", "")
    if samengevoegd in lookup:
        return lookup[samengevoegd]

    return None


def parseer_tijdsduur_seconden(tekst):
    tekst = str(tekst or "").strip().lower()
    tekst = tekst.translate(str.maketrans({
        "ë": "e",
        "é": "e",
        "è": "e",
        "ê": "e",
        "ï": "i",
        "í": "i",
        "ì": "i",
        "á": "a",
        "à": "a",
        "ä": "a",
        "ö": "o",
        "ü": "u",
    }))
    tekst = tekst.replace("-", " ")
    tekst = re.sub(r"[^a-z0-9\s]", " ", tekst)
    tekst = re.sub(r"\s+", " ", tekst).strip()
    if not tekst:
        return 0

    totaal = 0
    patroon = re.compile(
        r"(?P<waarde>\d+|[a-z]+(?:\s+[a-z]+){0,2})\s*(?P<eenheid>seconds?|secs?|seconden?|minutes?|mins?|minuten?|hours?|hrs?|uur|uren|days?|dag|dagen)"
    )
    factoren = {
        "second": 1,
        "seconds": 1,
        "sec": 1,
        "secs": 1,
        "seconde": 1,
        "seconden": 1,
        "minute": 60,
        "minutes": 60,
        "min": 60,
        "mins": 60,
        "minuut": 60,
        "minuten": 60,
        "hour": 3600,
        "hours": 3600,
        "hr": 3600,
        "hrs": 3600,
        "uur": 3600,
        "uren": 3600,
        "day": 86400,
        "days": 86400,
        "dag": 86400,
        "dagen": 86400,
    }

    for match in patroon.finditer(tekst):
        waarde_tekst = match.group("waarde").strip()
        waarde = int(waarde_tekst) if waarde_tekst.isdigit() else percentage_uit_woordtekst(waarde_tekst)
        if waarde is None:
            continue
        totaal += int(waarde) * factoren[match.group("eenheid")]

    return totaal


def haal_volume_percentage_uit_tekst(stap):
    volume_set_match = re.match(
        r"^(?:(?:set|zet|schakel)\s+(?:the\s+|het\s+|de\s+)?(?:volume|geluidd?|sound)|(?:volume|geluidd?|sound))(?:\s+(?:to|op|naar))?\s+(.+)$",
        stap,
    )
    if not volume_set_match:
        return None

    return percentage_uit_woordtekst(volume_set_match.group(1))


def stel_systeemvolume_in(percentage):
    percentage = begrens_percentage(percentage)
    scalar = percentage / 100.0
    mute_state = "$true" if percentage == 0 else "$false"
    script = f'''\
Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;

[ComImport]
[Guid("BCDE0395-E52F-467C-8E3D-C4579291692E")]
class MMDeviceEnumeratorComObject {{ }}

public enum EDataFlow {{ eRender, eCapture, eAll }}
public enum ERole {{ eConsole, eMultimedia, eCommunications }}

[ComImport, InterfaceType(ComInterfaceType.InterfaceIsIUnknown), Guid("A95664D2-9614-4F35-A746-DE8DB63617E6")]
interface IMMDeviceEnumerator
{{
    int NotImpl1();
    int GetDefaultAudioEndpoint(EDataFlow dataFlow, ERole role, out IMMDevice ppDevice);
}}

[ComImport, InterfaceType(ComInterfaceType.InterfaceIsIUnknown), Guid("D666063F-1587-4E43-81F1-B948E807363F")]
interface IMMDevice
{{
    int Activate(ref Guid iid, int dwClsCtx, IntPtr pActivationParams, [MarshalAs(UnmanagedType.Interface)] out object ppInterface);
}}

[ComImport, InterfaceType(ComInterfaceType.InterfaceIsIUnknown), Guid("5CDF2C82-841E-4546-9722-0CF74078229A")]
interface IAudioEndpointVolume
{{
    int RegisterControlChangeNotify(IntPtr pNotify);
    int UnregisterControlChangeNotify(IntPtr pNotify);
    int GetChannelCount(out uint pnChannelCount);
    int SetMasterVolumeLevel(float fLevelDB, Guid pguidEventContext);
    int SetMasterVolumeLevelScalar(float fLevel, Guid pguidEventContext);
    int GetMasterVolumeLevel(out float pfLevelDB);
    int GetMasterVolumeLevelScalar(out float pfLevel);
    int SetChannelVolumeLevel(uint nChannel, float fLevelDB, Guid pguidEventContext);
    int SetChannelVolumeLevelScalar(uint nChannel, float fLevel, Guid pguidEventContext);
    int GetChannelVolumeLevel(uint nChannel, out float pfLevelDB);
    int GetChannelVolumeLevelScalar(uint nChannel, out float pfLevel);
    int SetMute([MarshalAs(UnmanagedType.Bool)] bool bMute, Guid pguidEventContext);
    int GetMute(out bool pbMute);
    int GetVolumeStepInfo(out uint pnStep, out uint pnStepCount);
    int VolumeStepUp(Guid pguidEventContext);
    int VolumeStepDown(Guid pguidEventContext);
    int QueryHardwareSupport(out uint pdwHardwareSupportMask);
    int GetVolumeRange(out float pflVolumeMindB, out float pflVolumeMaxdB, out float pflVolumeIncrementdB);
}}

public static class AudioManager
{{
    public static void SetMasterVolume(float level, bool mute)
    {{
        var enumerator = (IMMDeviceEnumerator)(new MMDeviceEnumeratorComObject());
        IMMDevice device;
        Marshal.ThrowExceptionForHR(enumerator.GetDefaultAudioEndpoint(EDataFlow.eRender, ERole.eMultimedia, out device));
        object endpointVolumeObject;
        var iid = typeof(IAudioEndpointVolume).GUID;
        Marshal.ThrowExceptionForHR(device.Activate(ref iid, 23, IntPtr.Zero, out endpointVolumeObject));
        var endpointVolume = (IAudioEndpointVolume)endpointVolumeObject;
        Marshal.ThrowExceptionForHR(endpointVolume.SetMasterVolumeLevelScalar(level, Guid.Empty));
        Marshal.ThrowExceptionForHR(endpointVolume.SetMute(mute, Guid.Empty));
    }}
}}
"@
[AudioManager]::SetMasterVolume({scalar:.4f}, {mute_state})
'''
    subprocess.run(
        ["powershell", "-NoProfile", "-Command", script],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="ignore",
    )
    return percentage


def voer_macro_uit(macro_sleutel):
    details = APP_MACROS[macro_sleutel]
    stappen = details["steps"]
    heeft_launch_stap = any(soort == "launch" for soort, _ in stappen)
    heeft_hotkeys = any(soort == "hotkey" for soort, _ in stappen)

    if details.get("app") and heeft_hotkeys and not activeer_venster(details["app"], not heeft_launch_stap):
        return tekst_voor_taal(
            f"Could not focus {details['label_en']}. Open the app first and try again.",
            f"Kon {details['label_nl']} niet activeren. Open de app eerst en probeer opnieuw."
        )

    for soort, payload in stappen:
        if soort == "launch":
            subprocess.Popen(payload)
            time.sleep(0.8)
        elif soort == "press":
            pyautogui.press(payload)
        elif soort == "hotkey":
            pyautogui.hotkey(*payload)
        elif soort == "write":
            pyautogui.write(payload, interval=0.02)
        time.sleep(0.1)

    return tekst_voor_taal(
        f"Ran macro: {details['label_en']}",
        f"Macro uitgevoerd: {details['label_nl']}"
    )


def maak_automation_actie(originele_stap, stap):
    if re.fullmatch(r"(?:enable|activate|turn on|start|zet|schakel) automation mode(?: on)?", stap):
        return "automation enable"

    if re.fullmatch(r"(?:disable|deactivate|turn off|stop|zet|schakel) automation mode(?: off)?", stap):
        return "automation disable"

    if stap in {"automation status", "status automation mode", "automation mode status", "automation-modus status"}:
        return "automation status"

    macro_sleutel = vind_macro_sleutel(stap)
    if macro_sleutel:
        return f"run macro {macro_sleutel}"

    focus_match = re.match(r"^(?:focus|activate|switch to|focus op|activeer|ga naar)\s+(?:app\s+)?(.+)$", stap)
    if focus_match:
        app_sleutel = vind_focus_app_sleutel(focus_match.group(1))
        if app_sleutel:
            return f"window focus {app_sleutel}"

    if re.fullmatch(r"(?:switch|next|cycle)\s+(?:window|app|venster|programma)", stap):
        return "press hotkey::alt||tab"

    if re.fullmatch(r"(?:previous|vorige)\s+(?:window|app|venster|programma)", stap):
        return "press hotkey::alt||shift||tab"

    if re.fullmatch(r"(?:task view|open task view|taakweergave|open taakweergave)", stap):
        return "press hotkey::win||tab"

    if re.fullmatch(r"(?:open start menu|show start menu|start menu|open start|toon startmenu|startmenu)", stap):
        return "press key::win"

    if re.fullmatch(r"(?:copy|copy that|kopieer|kopieer dat)", stap):
        return "press hotkey::ctrl||c"

    if re.fullmatch(r"(?:paste|plak)", stap):
        return "press hotkey::ctrl||v"

    if re.fullmatch(r"(?:cut|knip)", stap):
        return "press hotkey::ctrl||x"

    if re.fullmatch(r"(?:select all|selecteer alles)", stap):
        return "press hotkey::ctrl||a"

    if re.fullmatch(r"(?:undo|ongedaan maken)", stap):
        return "press hotkey::ctrl||z"

    if re.fullmatch(r"(?:redo|opnieuw uitvoeren|herhaal bewerking)", stap):
        return "press hotkey::ctrl||y"

    if re.fullmatch(r"(?:save|save file|opslaan|bestand opslaan)", stap):
        return "press hotkey::ctrl||s"

    if re.fullmatch(r"(?:find|search here|zoeken|zoek hier)", stap):
        return "press hotkey::ctrl||f"

    if re.fullmatch(r"(?:new tab|nieuw tabblad)", stap):
        return "press hotkey::ctrl||t"

    if re.fullmatch(r"(?:close tab|sluit tab|sluit tabblad)", stap):
        return "press hotkey::ctrl||w"

    if re.fullmatch(r"(?:next tab|volgende tab|volgend tabblad)", stap):
        return "press hotkey::ctrl||tab"

    if re.fullmatch(r"(?:previous tab|vorige tab|vorig tabblad)", stap):
        return "press hotkey::ctrl||shift||tab"

    if re.fullmatch(r"(?:reopen tab|reopen closed tab|heropen tab|heropen gesloten tab)", stap):
        return "press hotkey::ctrl||shift||t"

    if re.fullmatch(r"(?:close|sluit)(?:\s+(?:the|het|de))?(?:\s+(?:current|active|huidige|actieve))?\s+(?:window|venster)", stap):
        return "window close"

    if re.fullmatch(r"(?:maximize|maximaliseer)(?:\s+(?:the|het|de))?\s+(?:window|venster)", stap):
        return "window maximize"

    if re.fullmatch(r"(?:minimize|minimaliseer)(?:\s+(?:the|het|de))?\s+(?:window|venster)", stap):
        return "window minimize"

    if re.fullmatch(r"(?:restore|herstel)(?:\s+(?:the|het|de))?\s+(?:window|venster)", stap):
        return "window restore"

    snap_match = re.match(r"^(?:snap)(?:\s+(?:the|het|de))?\s+(?:window|venster)\s+(left|right|links|rechts)$", stap)
    if snap_match:
        richting = {"links": "left", "rechts": "right"}.get(snap_match.group(1), snap_match.group(1))
        return f"window snap {richting}"

    move_window_match = re.match(r"^(?:move|drag|verplaats|sleep)(?:\s+(?:the|het|de))?\s+(?:window|venster)\s+(left|right|up|down|links|rechts|omhoog|omlaag)\s+(\d+)$", stap)
    if move_window_match:
        richting = {
            "links": "left",
            "rechts": "right",
            "omhoog": "up",
            "omlaag": "down",
        }.get(move_window_match.group(1), move_window_match.group(1))
        return f"window move {richting} {move_window_match.group(2)}"

    type_match = re.match(r"^(?:type|type text|typ|schrijf)\s+(.+)$", originele_stap, re.IGNORECASE)
    if type_match:
        return f"type text::{type_match.group(1)}"

    shortcut_match = re.match(r"^(?:hotkey|shortcut|sneltoets)\s+(.+)$", originele_stap, re.IGNORECASE)
    if shortcut_match:
        toetsen = normaliseer_toets_combinatie(shortcut_match.group(1))
        if len(toetsen) >= 2:
            return "press hotkey::" + "||".join(toetsen)

    press_match = re.match(r"^(?:press|druk op)\s+(.+)$", originele_stap, re.IGNORECASE)
    if press_match:
        toetsen = normaliseer_toets_combinatie(press_match.group(1))
        if len(toetsen) >= 2:
            return "press hotkey::" + "||".join(toetsen)
        if len(toetsen) == 1:
            return f"press key::{toetsen[0]}"

    move_to_match = re.match(r"^(?:move mouse to|move cursor to|verplaats muis naar|verplaats cursor naar)\s+(\d+)\s*(?:,|x| )\s*(\d+)$", stap)
    if move_to_match:
        return f"mouse move to {move_to_match.group(1)}||{move_to_match.group(2)}"

    drag_to_match = re.match(r"^(?:drag mouse to|drag cursor to|sleep muis naar|sleep cursor naar)\s+(\d+)\s*(?:,|x| )\s*(\d+)$", stap)
    if drag_to_match:
        return f"mouse drag to {drag_to_match.group(1)}||{drag_to_match.group(2)}"

    move_by_match = re.match(r"^(?:move mouse|move cursor|verplaats muis|verplaats cursor)\s+(left|right|up|down|links|rechts|omhoog|omlaag)\s+(\d+)$", stap)
    if move_by_match:
        richting = {
            "links": "left",
            "rechts": "right",
            "omhoog": "up",
            "omlaag": "down",
        }.get(move_by_match.group(1), move_by_match.group(1))
        return f"mouse move {richting} {move_by_match.group(2)}"

    drag_by_match = re.match(r"^(?:drag mouse|drag cursor|sleep muis|sleep cursor)\s+(left|right|up|down|links|rechts|omhoog|omlaag)\s+(\d+)$", stap)
    if drag_by_match:
        richting = {
            "links": "left",
            "rechts": "right",
            "omhoog": "up",
            "omlaag": "down",
        }.get(drag_by_match.group(1), drag_by_match.group(1))
        return f"mouse drag {richting} {drag_by_match.group(2)}"

    if re.fullmatch(r"(?:double click|dubbelklik)", stap):
        return "mouse double click left"
    if re.fullmatch(r"(?:right click|rechtermuisklik|rechts klik)", stap):
        return "mouse click right"
    if re.fullmatch(r"(?:click|klik|left click|linkermuisklik)", stap):
        return "mouse click left"

    scroll_match = re.match(r"^(?:scroll|scrollen)\s+(up|down|omhoog|omlaag)(?:\s+(\d+))?$", stap)
    if scroll_match:
        richting = {"omhoog": "up", "omlaag": "down"}.get(scroll_match.group(1), scroll_match.group(1))
        hoeveelheid = scroll_match.group(2) or "400"
        return f"mouse scroll {richting} {hoeveelheid}"

    if re.fullmatch(r"(?:take a screenshot|take screenshot|maak screenshot|maak schermafbeelding|screenshot)", stap):
        return "take screenshot"

    volume_percentage = haal_volume_percentage_uit_tekst(stap)
    if volume_percentage is not None:
        return f"volume set {volume_percentage}"

    volume_match = re.match(r"^(?:(?:volume|geluid)\s+(up|down|mute|omhoog|omlaag|stil)|(?:mute volume|dempen volume|zet volume stil))$", stap)
    if volume_match:
        ruwe_richting = volume_match.group(1) or "mute"
        richting = {"omhoog": "up", "omlaag": "down", "stil": "mute"}.get(ruwe_richting, ruwe_richting)
        return f"volume {richting}"

    if re.fullmatch(r"(?:show desktop|minimize windows|minimaliseer vensters|toon bureaublad)", stap):
        return "window show desktop"

    wifi_match = re.fullmatch(r"(?:(?:wifi|wi-fi)\s+(on|off|toggle|aan|uit)|(?:turn|zet|schakel)\s+(?:wifi|wi-fi)\s+(on|off|aan|uit)|toggle\s+(?:wifi|wi-fi))", stap)
    if wifi_match:
        ruwe_richting = next((waarde for waarde in wifi_match.groups() if waarde), "toggle")
        richting = {"aan": "on", "uit": "off", None: "toggle"}.get(ruwe_richting, ruwe_richting)
        return f"wifi {richting}"

    bluetooth_match = re.fullmatch(r"(?:(?:bluetooth)\s+(on|off|toggle|aan|uit)|(?:turn|zet|schakel)\s+bluetooth\s+(on|off|aan|uit)|toggle\s+bluetooth)", stap)
    if bluetooth_match:
        ruwe_richting = next((waarde for waarde in bluetooth_match.groups() if waarde), "toggle")
        richting = {"aan": "on", "uit": "off", None: "toggle"}.get(ruwe_richting, ruwe_richting)
        return f"bluetooth {richting}"

    return ""


def maak_geavanceerde_browser_actie(originele_stap, stap):
    if re.fullmatch(r"(?:current tab url|current page url|tab url|huidige tab url|huidige pagina url)", stap):
        return "browser current url"

    if re.fullmatch(r"(?:read|show|lees|toon)(?:\s+(?:this|current|active|deze|huidige|actieve))\s+(?:tab|page|pagina)", stap):
        return "browser read current"

    if re.fullmatch(r"(?:summari[sz]e|samenvat|vat samen)(?:\s+(?:this|current|active|deze|huidige|actieve))\s+(?:tab|page|pagina)", stap):
        return "browser summarize current"

    lees_url_match = re.match(r"^(?:read|show|lees|toon)(?:\s+(?:page|pagina))?\s+(.+)$", originele_stap, re.IGNORECASE)
    if lees_url_match:
        browser_doel = lees_url_match.group(1).strip(" .")
        if resolve_bron_pad_voor_operatie(browser_doel):
            return ""
        url = normaliseer_url_voor_browser_taak(browser_doel)
        if url:
            return f"browser read url::{url}"

    samenvat_url_match = re.match(r"^(?:summari[sz]e|samenvat|vat samen)(?:\s+(?:page|pagina))?\s+(.+)$", originele_stap, re.IGNORECASE)
    if samenvat_url_match:
        browser_doel = samenvat_url_match.group(1).strip(" .")
        if resolve_bron_pad_voor_operatie(browser_doel):
            return ""
        url = normaliseer_url_voor_browser_taak(browser_doel)
        if url:
            return f"browser summarize url::{url}"

    formulier_match = re.match(r"^(?:fill form|fill in form|vul formulier in)(?:\s+(?:with|met))\s+(.+)$", originele_stap, re.IGNORECASE)
    if formulier_match:
        waarden = [deel.strip() for deel in re.split(r"\s*(?:,|;)\s*", formulier_match.group(1)) if deel.strip()]
        if len(waarden) == 1 and " and " in waarden[0].lower():
            waarden = [deel.strip() for deel in re.split(r"\s+and\s+", waarden[0], flags=re.IGNORECASE) if deel.strip()]
        if len(waarden) == 1 and " en " in waarden[0].lower():
            waarden = [deel.strip() for deel in re.split(r"\s+en\s+", waarden[0], flags=re.IGNORECASE) if deel.strip()]
        if waarden:
            return "browser fill form::" + "||".join(waarden)

    if re.fullmatch(r"(?:submit form|verzend formulier)", stap):
        return "browser submit form"

    return ""


def maak_browser_actie(stap):
    google_match = re.match(
        r"^(?:search(?:\s+on)?\s+google\s+(?:for)?|google\s+search\s+(?:for)?|zoek\s+(?:op\s+)?google\s+(?:naar)?)\s+(.+)$",
        stap,
    )
    if google_match:
        zoekterm = google_match.group(1).strip(" ?.")
        if zoekterm:
            return f"search google {zoekterm}"

    youtube_match = re.match(
        r"^(?:search(?:\s+on)?\s+youtube\s+(?:for)?|youtube\s+search\s+(?:for)?|zoek\s+(?:op\s+)?youtube\s+(?:naar)?)\s+(.+)$",
        stap,
    )
    if youtube_match:
        zoekterm = youtube_match.group(1).strip(" ?.")
        if zoekterm:
            return f"search youtube {zoekterm}"

    if re.search(r"\b(?:new tabs?|nieuw(?:e)? tab(?:blad)?(?:en)?)\b", stap):
        meervoud = bool(re.search(r"\b(?:new tabs|nieuwe? tabbladen|tabbladen)\b", stap))
        doel_tekst = re.sub(r"\b(?:open|openen|start|launch|ga(?:\s+naar)?)\b", " ", stap)
        doel_tekst = re.sub(r"\b(?:new tabs?|nieuw(?:e)? tab(?:blad)?(?:en)?)\b", " ", doel_tekst)
        doel_tekst = re.sub(r"\b(?:in|een|a|the|het|de|met|with)\b", " ", doel_tekst)
        doel_tekst = re.sub(r"\s+", " ", doel_tekst).strip(" ,.")
        doelen = normaliseer_meerdere_webdoelen(doel_tekst)

        if len(doelen) > 1 or (meervoud and doelen):
            return "open new tabs " + "||".join(doelen)
        if len(doelen) == 1:
            return f"open new tab {doelen[0]}"

    open_match = re.match(r"^(?:open|openen|start|launch|ga(?:\s+naar)?)\s+(.+)$", stap)
    if open_match:
        doel_tekst = open_match.group(1).strip(" ,.")
        doelen = normaliseer_meerdere_webdoelen(doel_tekst)
        if len(doelen) > 1:
            return "open websites " + "||".join(doelen)
        if len(doelen) == 1:
            return f"open website {doelen[0]}"

    enkel_doel = normaliseer_webdoel(stap)
    if enkel_doel:
        return f"open website {enkel_doel}"

    return ""


def normaliseer_actie(stap):
    originele_stap = re.sub(r"\s+", " ", str(stap or "")).strip()
    stap = originele_stap.lower()
    if not originele_stap:
        return ""

    if stap.startswith(("calculate::", "open browser url::", "copy path::", "move path::", "rename path::", "delete path::", "create file ", "list folder::", "read file::", "summarize file::", "append file::", "overwrite file::", "rewrite file::", "search files::", "timer ", "reminder ", "task ", "agenda show")):
        return originele_stap

    if is_explicit_help_request(stap):
        return "help"

    geavanceerde_browser_actie = maak_geavanceerde_browser_actie(originele_stap, stap)
    if geavanceerde_browser_actie:
        return geavanceerde_browser_actie

    browser_workflow_actie = maak_browser_workflow_actie(originele_stap, stap)
    if browser_workflow_actie:
        return browser_workflow_actie

    browser_actie = maak_browser_actie(stap)
    if browser_actie:
        return browser_actie

    reken_actie = maak_reken_actie(originele_stap)
    if reken_actie:
        return reken_actie

    planner_actie = maak_planner_actie(originele_stap, stap)
    if planner_actie:
        return planner_actie

    bestands_actie = maak_bestands_actie(originele_stap, stap)
    if bestands_actie:
        return bestands_actie

    informatie_actie = maak_informatie_actie(stap)
    if informatie_actie:
        return informatie_actie

    automation_actie = maak_automation_actie(originele_stap, stap)
    if automation_actie:
        return automation_actie

    systeem_actie = maak_systeem_actie(stap)
    if systeem_actie:
        return systeem_actie

    if "youtube" in stap and (
        stap == "youtube" or re.search(r"\b(open|openen|start|launch|ga(?:\s+naar)?)\b", stap)
    ):
        return "open youtube"

    if "google" in stap and (
        stap == "google" or re.search(r"\b(open|openen|start|launch|ga(?:\s+naar)?)\b", stap)
    ):
        return "open google"

    folder_match = re.match(
        r"^(?:(?:create|make|maak)(?:\s+(?:a|een|new|nieuwe))?\s+(?:folder|map|directory)(?:\s+(?:named|met(?:\s+de)?\s+naam))?|(?:folder|map))\s*(.*)$",
        stap,
    )
    if folder_match:
        mapnaam = folder_match.group(1).strip()
        return f"create folder {mapnaam}".strip()

    if re.search(r"\b(?:calculator|rekenmachine|calc)\b", stap):
        return "open calculator"

    if re.search(r"\b(?:paint|mspaint|tekenprogramma)\b", stap):
        return "open paint"

    if re.search(r"\b(?:command prompt|cmd|opdrachtprompt|terminal)\b", stap):
        return "open command prompt"

    if re.search(r"\b(?:notepad|kladblok)\b", stap):
        return "open notepad"

    if re.search(r"\b(?:file explorer|explorer|verkenner|bestandsverkenner)\b", stap):
        return "open file explorer"

    return stap


def mapnaam_uit_actie(actie):
    mapnaam = re.sub(r"^create folder\s*", "", actie).strip()
    return mapnaam if mapnaam else "Nieuwe_Map"


def actie_prioriteit(stap):
    stap = stap.lower()
    if stap in {"confirm pending action", "cancel pending action", "automation enable", "automation disable", "automation status", "system scan start", "system scan status"}:
        return 0
    if stap.startswith(("timer ", "reminder ", "task ", "agenda show")):
        return 1
    if stap.startswith(("open website", "open websites", "open new tab", "open new tabs", "search google", "search youtube", "open browser url::")) or "youtube" in stap or "google" in stap or "browser" in stap:
        return 1
    if stap.startswith("calculate::"):
        return 2
    if stap.startswith(("open notepad", "open file explorer", "open calculator", "open paint", "open command prompt", "open app ", "open folder ", "open file ", "open setting ", "create file ", "list folder::", "read file::", "summarize file::", "append file::", "overwrite file::", "rewrite file::", "search files::", "copy path::", "move path::", "rename path::", "delete path::", "system info", "system scan start", "system scan status", "battery status", "disk space", "ip address", "current time")):
        return 2
    if stap.startswith(("run macro ", "mouse ", "type text::", "press key::", "press hotkey::", "take screenshot", "volume ", "window ", "wifi ", "bluetooth ")):
        return 3
    if stap.startswith("create folder"):
        return 4
    if stap in DANGEROUS_SYSTEM_ACTIONS:
        return 7
    if stap == "help":
        return 8
    return 9


def verrijk_plan_met_context(originele_tekst, plan):
    if not instellingen.get("geheugen_modus", True):
        return plan

    tekst = originele_tekst.lower().strip()
    herhaal_triggers = ["again", "repeat", "do that again", "same again", "nog een keer", "opnieuw", "herhaal", "doe dat nog eens", "zelfde nog eens"]

    if any(trigger in tekst for trigger in herhaal_triggers) and GESPREK_CONTEXT["laatste_plan"]:
        return list(GESPREK_CONTEXT["laatste_plan"])

    verrijkt = []
    for stap in plan:
        if ("also that" in stap or "ook dat" in stap) and GESPREK_CONTEXT["laatste_webactie"]:
            verrijkt.append(GESPREK_CONTEXT["laatste_webactie"])
            continue

        if ("that folder too" in stap or "also that folder" in stap or "ook die map" in stap) and GESPREK_CONTEXT["laatste_map"]:
            verrijkt.append(f"create folder {GESPREK_CONTEXT['laatste_map']}")
            continue

        verrijkt.append(stap)

    return verrijkt


def orden_plan_op_prioriteit(plan):
    if not instellingen.get("prioriteit_modus", True) or len(plan) <= 1:
        return plan

    met_index = list(enumerate(plan))
    met_index.sort(key=lambda item: (actie_prioriteit(item[1]), item[0]))
    return [stap for _, stap in met_index]


def update_gesprek_context(plan, resultaten):
    GESPREK_CONTEXT["laatste_plan"] = list(plan)
    GESPREK_CONTEXT["laatste_resultaten"] = list(resultaten)

    for stap, resultaat in zip(plan, resultaten):
        stap_lower = stap.lower()
        if stap_lower.startswith(("open website", "open websites", "open new tab", "open new tabs", "search google", "search youtube", "open browser url::")) or "youtube" in stap_lower or "google" in stap_lower:
            GESPREK_CONTEXT["laatste_webactie"] = stap

        if stap_lower.startswith("create folder"):
            GESPREK_CONTEXT["laatste_map"] = mapnaam_uit_actie(stap_lower)


def voer_enkele_actie_uit(actie):
    """Execute exactly one action."""
    actie = normaliseer_actie(actie)

    if actie.startswith(("timer ", "reminder ", "task ", "agenda show")):
        return voer_planner_actie_uit(actie)

    if actie.startswith("browser "):
        return voer_geavanceerde_browser_actie_uit(actie)

    if actie == "automation enable":
        if not instellingen.get("computerbesturing_toestaan", False):
            return tekst_voor_taal(
                "Enable advanced computer control in Settings first.",
                "Zet eerst geavanceerde computerbesturing aan in Instellingen."
            )
        activeer_automatisering_modus()
        return tekst_voor_taal(
            "Automation mode enabled for 5 minutes.",
            "Automation-modus ingeschakeld voor 5 minuten."
        )

    if actie == "automation disable":
        deactiveer_automatisering_modus()
        return tekst_voor_taal(
            "Automation mode disabled.",
            "Automation-modus uitgeschakeld."
        )

    if actie == "automation status":
        return automatisering_status_bericht()

    if actie == "confirm pending action":
        wachtende_actie = GESPREK_CONTEXT.get("wacht_op_bevestiging", "")
        if not wachtende_actie:
            return tekst_voor_taal(
                "There is no pending action to confirm.",
                "Er is geen wachtende actie om te bevestigen."
            )

        GESPREK_CONTEXT["wacht_op_bevestiging"] = ""
        return voer_bevestigde_actie_uit(wachtende_actie)

    if actie == "cancel pending action":
        if GESPREK_CONTEXT.get("wacht_op_bevestiging"):
            GESPREK_CONTEXT["wacht_op_bevestiging"] = ""
            return tekst_voor_taal(
                "Pending action cancelled.",
                "Wachtende actie geannuleerd."
            )

        return tekst_voor_taal(
            "There is no pending action to cancel.",
            "Er is geen wachtende actie om te annuleren."
        )

    if actie in DANGEROUS_SYSTEM_ACTIONS:
        GESPREK_CONTEXT["wacht_op_bevestiging"] = actie
        details = DANGEROUS_SYSTEM_ACTIONS[actie]
        return tekst_voor_taal(
            f"Safety check: say confirm to {details['confirm_en']}.",
            f"Veiligheidscontrole: zeg bevestig om {details['confirm_nl']}."
        )

    if actie.startswith("delete path::"):
        doel_tekst = actie.split("::", 1)[1]
        doel_pad = resolve_bron_pad_voor_operatie(doel_tekst)
        if not doel_pad:
            return tekst_voor_taal(
                f"Could not find path: {doel_tekst}",
                f"Kon pad niet vinden: {doel_tekst}"
            )
        GESPREK_CONTEXT["wacht_op_bevestiging"] = actie
        return tekst_voor_taal(
            f"Safety check: say confirm to delete {doel_pad}.",
            f"Veiligheidscontrole: zeg bevestig om {doel_pad} te verwijderen."
        )

    if actie.startswith("overwrite file::"):
        payload = actie.split("::", 1)[1]
        doel_tekst = payload.split("||", 1)[0] if "||" in payload else payload
        doel_pad = resolve_pad_voor_operatie(doel_tekst)
        if not doel_pad:
            return tekst_voor_taal("No valid file path provided.", "Geen geldig bestandspad opgegeven.")
        if doel_pad.exists():
            GESPREK_CONTEXT["wacht_op_bevestiging"] = actie
            return tekst_voor_taal(
                f"Safety check: say confirm to overwrite {doel_pad}.",
                f"Veiligheidscontrole: zeg bevestig om {doel_pad} te overschrijven."
            )
        return voer_overschrijf_bestand_uit(actie)

    if actie.startswith("rewrite file::"):
        payload = actie.split("::", 1)[1]
        doel_tekst = payload.split("||", 1)[0] if "||" in payload else payload
        doel_pad = resolve_bestand_pad(doel_tekst)
        if not doel_pad:
            return tekst_voor_taal(
                f"Could not find file: {doel_tekst}",
                f"Kon bestand niet vinden: {doel_tekst}"
            )
        GESPREK_CONTEXT["wacht_op_bevestiging"] = actie
        return tekst_voor_taal(
            f"Safety check: say confirm to rewrite {doel_pad}.",
            f"Veiligheidscontrole: zeg bevestig om {doel_pad} te herschrijven."
        )

    if actie.startswith("calculate::"):
        expressie = actie.split("::", 1)[1]
        try:
            resultaat = bereken_veilige_expressie(expressie)
            return tekst_voor_taal(
                f"Result: {formatteer_reken_resultaat(resultaat)}",
                f"Uitkomst: {formatteer_reken_resultaat(resultaat)}"
            )
        except ZeroDivisionError:
            return tekst_voor_taal(
                "I cannot divide by zero.",
                "Ik kan niet door nul delen."
            )
        except ValueError as e:
            return tekst_voor_taal(
                f"I could not calculate that safely: {e}",
                f"Ik kon dat niet veilig uitrekenen: {e}"
            )
        except Exception as e:
            return tekst_voor_taal(
                f"Calculation error: {e}",
                f"Rekenfout: {e}"
            )

    if actie.startswith("list folder::"):
        return voer_lijst_map_uit(actie)

    if actie.startswith("read file::"):
        return voer_lees_bestand_uit(actie)

    if actie.startswith("summarize file::"):
        return voer_samenvatting_bestand_uit(actie)

    if actie.startswith("append file::"):
        return voer_append_bestand_uit(actie)

    if actie.startswith("search files::"):
        return voer_zoek_bestanden_uit(actie)

    if actie == "system scan start":
        _gestart, bericht = start_system_scan()
        return bericht

    if actie == "system scan status":
        return system_scan_status_bericht()

    if actie in {"system info", "battery status", "disk space", "ip address", "current time"}:
        return voer_systeeminfo_uit(actie)

    if actie.startswith(("run macro ", "mouse ", "type text::", "press key::", "press hotkey::", "take screenshot", "volume ", "window ", "wifi ", "bluetooth ")):
        blokkade = geavanceerde_besturing_geblokkeerd(actie)
        if blokkade:
            return blokkade

    if actie.startswith("run macro "):
        macro_sleutel = re.sub(r"^run macro\s*", "", actie).strip()
        try:
            return voer_macro_uit(macro_sleutel)
        except Exception as e:
            return tekst_voor_taal(
                f"Error running macro: {e}",
                f"Fout bij uitvoeren van macro: {e}"
            )

    if actie.startswith("window focus "):
        app_sleutel = re.sub(r"^window focus\s*", "", actie).strip()
        if activeer_venster(app_sleutel):
            return tekst_voor_taal(
                f"Focused {app_sleutel}",
                f"{app_sleutel} geactiveerd"
            )
        return tekst_voor_taal(
            f"Could not focus {app_sleutel}",
            f"Kon {app_sleutel} niet activeren"
        )

    if actie == "window close":
        try:
            venster = haal_actief_venster()
            if not venster:
                raise RuntimeError("No active window found")
            try:
                venster.close()
            except Exception:
                pyautogui.hotkey("alt", "f4")
            return tekst_voor_taal("Closed active window", "Actief venster gesloten")
        except Exception as e:
            return tekst_voor_taal(f"Error closing window: {e}", f"Fout bij sluiten van venster: {e}")

    if actie == "window maximize":
        try:
            venster = haal_actief_venster()
            if not venster:
                raise RuntimeError("No active window found")
            venster.maximize()
            return tekst_voor_taal("Window maximized", "Venster gemaximaliseerd")
        except Exception as e:
            return tekst_voor_taal(f"Error maximizing window: {e}", f"Fout bij maximaliseren van venster: {e}")

    if actie == "window minimize":
        try:
            venster = haal_actief_venster()
            if not venster:
                raise RuntimeError("No active window found")
            venster.minimize()
            return tekst_voor_taal("Window minimized", "Venster geminimaliseerd")
        except Exception as e:
            return tekst_voor_taal(f"Error minimizing window: {e}", f"Fout bij minimaliseren van venster: {e}")

    if actie == "window restore":
        try:
            venster = haal_actief_venster()
            if not venster:
                raise RuntimeError("No active window found")
            venster.restore()
            return tekst_voor_taal("Window restored", "Venster hersteld")
        except Exception as e:
            return tekst_voor_taal(f"Error restoring window: {e}", f"Fout bij herstellen van venster: {e}")

    if actie.startswith("window snap "):
        richting = re.sub(r"^window snap\s*", "", actie).strip()
        try:
            pyautogui.hotkey("win", richting)
            return tekst_voor_taal(
                f"Snapped window {richting}",
                f"Venster gesnapt naar {('links' if richting == 'left' else 'rechts')}"
            )
        except Exception as e:
            return tekst_voor_taal(f"Error snapping window: {e}", f"Fout bij snappen van venster: {e}")

    if actie.startswith("window move "):
        move_match = re.match(r"^window move\s+(left|right|up|down)\s+(\d+)$", actie)
        if move_match:
            richting, afstand = move_match.group(1), int(move_match.group(2))
            try:
                verplaats_actief_venster(richting, afstand)
                return tekst_voor_taal(
                    f"Moved window {richting} by {afstand} pixels",
                    f"Venster {('links' if richting == 'left' else 'rechts' if richting == 'right' else 'omhoog' if richting == 'up' else 'omlaag')} verplaatst met {afstand} pixels"
                )
            except Exception as e:
                return tekst_voor_taal(f"Error moving window: {e}", f"Fout bij verplaatsen van venster: {e}")

    if actie.startswith("mouse move to "):
        payload = re.sub(r"^mouse move to\s*", "", actie).strip().split("||")
        try:
            pyautogui.moveTo(int(payload[0]), int(payload[1]), duration=0.15)
            return tekst_voor_taal("Mouse moved", "Muis verplaatst")
        except Exception as e:
            return tekst_voor_taal(f"Error moving mouse: {e}", f"Fout bij verplaatsen van muis: {e}")

    if actie.startswith("mouse drag to "):
        payload = re.sub(r"^mouse drag to\s*", "", actie).strip().split("||")
        try:
            pyautogui.dragTo(int(payload[0]), int(payload[1]), duration=0.2, button="left")
            return tekst_voor_taal("Mouse dragged", "Muis gesleept")
        except Exception as e:
            return tekst_voor_taal(f"Error dragging mouse: {e}", f"Fout bij slepen van muis: {e}")

    if actie.startswith("mouse move "):
        move_match = re.match(r"^mouse move\s+(left|right|up|down)\s+(\d+)$", actie)
        if move_match:
            richting, afstand = move_match.group(1), int(move_match.group(2))
            x_offset = (-afstand if richting == "left" else afstand if richting == "right" else 0)
            y_offset = (-afstand if richting == "up" else afstand if richting == "down" else 0)
            try:
                pyautogui.moveRel(x_offset, y_offset, duration=0.12)
                return tekst_voor_taal("Mouse moved", "Muis verplaatst")
            except Exception as e:
                return tekst_voor_taal(f"Error moving mouse: {e}", f"Fout bij verplaatsen van muis: {e}")

    if actie.startswith("mouse drag "):
        drag_match = re.match(r"^mouse drag\s+(left|right|up|down)\s+(\d+)$", actie)
        if drag_match:
            richting, afstand = drag_match.group(1), int(drag_match.group(2))
            x_offset = (-afstand if richting == "left" else afstand if richting == "right" else 0)
            y_offset = (-afstand if richting == "up" else afstand if richting == "down" else 0)
            try:
                pyautogui.dragRel(x_offset, y_offset, duration=0.2, button="left")
                return tekst_voor_taal("Mouse dragged", "Muis gesleept")
            except Exception as e:
                return tekst_voor_taal(f"Error dragging mouse: {e}", f"Fout bij slepen van muis: {e}")

    if actie.startswith("mouse double click"):
        try:
            pyautogui.doubleClick()
            return tekst_voor_taal("Double clicked", "Dubbelgeklikt")
        except Exception as e:
            return tekst_voor_taal(f"Error clicking: {e}", f"Fout bij klikken: {e}")

    if actie.startswith("mouse click "):
        knop = re.sub(r"^mouse click\s*", "", actie).strip()
        try:
            pyautogui.click(button=knop)
            return tekst_voor_taal(
                f"{knop.title()} click sent",
                f"{knop.title()} klik uitgevoerd"
            )
        except Exception as e:
            return tekst_voor_taal(f"Error clicking: {e}", f"Fout bij klikken: {e}")

    if actie.startswith("mouse scroll "):
        scroll_match = re.match(r"^mouse scroll\s+(up|down)\s+(\d+)$", actie)
        if scroll_match:
            richting, hoeveelheid = scroll_match.group(1), int(scroll_match.group(2))
            try:
                pyautogui.scroll(hoeveelheid if richting == "up" else -hoeveelheid)
                return tekst_voor_taal("Scrolled", "Geschrold")
            except Exception as e:
                return tekst_voor_taal(f"Error scrolling: {e}", f"Fout bij scrollen: {e}")

    if actie.startswith("type text::"):
        tekst = actie.split("::", 1)[1]
        try:
            pyautogui.write(tekst, interval=0.02)
            return tekst_voor_taal("Typed text", "Tekst getypt")
        except Exception as e:
            return tekst_voor_taal(f"Error typing text: {e}", f"Fout bij typen van tekst: {e}")

    if actie.startswith("press hotkey::"):
        toetsen = [deel for deel in actie.split("::", 1)[1].split("||") if deel]
        try:
            pyautogui.hotkey(*toetsen)
            return tekst_voor_taal("Hotkey sent", "Sneltoets uitgevoerd")
        except Exception as e:
            return tekst_voor_taal(f"Error sending hotkey: {e}", f"Fout bij uitvoeren van sneltoets: {e}")

    if actie.startswith("press key::"):
        toets = actie.split("::", 1)[1]
        try:
            pyautogui.press(toets)
            return tekst_voor_taal(f"Pressed {toets}", f"Toets ingedrukt: {toets}")
        except Exception as e:
            return tekst_voor_taal(f"Error pressing key: {e}", f"Fout bij indrukken van toets: {e}")

    if actie == "take screenshot":
        try:
            screenshot_pad = maak_screenshot_pad()
            maak_windows_screenshot(screenshot_pad)
            return tekst_voor_taal(
                f"Screenshot saved to {screenshot_pad}",
                f"Screenshot opgeslagen in {screenshot_pad}"
            )
        except Exception as e:
            return tekst_voor_taal(f"Error taking screenshot: {e}", f"Fout bij maken van screenshot: {e}")

    volume_set_match = re.match(r"^volume set\s+(\d{1,3})$", actie)
    if volume_set_match:
        percentage = begrens_percentage(volume_set_match.group(1))
        try:
            stel_systeemvolume_in(percentage)
            return tekst_voor_taal(
                f"Volume set to {percentage}%",
                f"Volume ingesteld op {percentage}%"
            )
        except Exception as e:
            return tekst_voor_taal(f"Error setting volume: {e}", f"Fout bij instellen van volume: {e}")

    if actie.startswith("volume "):
        richting = re.sub(r"^volume\s*", "", actie).strip()
        toets = {"up": "volumeup", "down": "volumedown", "mute": "volumemute"}.get(richting)
        if toets:
            try:
                pyautogui.press(toets)
                return tekst_voor_taal(
                    f"Volume {richting}",
                    f"Volume {richting if richting == 'mute' else ('omhoog' if richting == 'up' else 'omlaag')}"
                )
            except Exception as e:
                return tekst_voor_taal(f"Error changing volume: {e}", f"Fout bij aanpassen van volume: {e}")

    if actie == "window show desktop":
        try:
            pyautogui.hotkey("win", "d")
            return tekst_voor_taal("Desktop shown", "Bureaublad getoond")
        except Exception as e:
            return tekst_voor_taal(f"Error showing desktop: {e}", f"Fout bij tonen van bureaublad: {e}")

    if actie.startswith("wifi "):
        modus = re.sub(r"^wifi\s*", "", actie).strip()
        try:
            return voer_wifi_actie_uit(modus)
        except Exception as e:
            return tekst_voor_taal(f"Error changing Wi-Fi: {e}", f"Fout bij aanpassen van wifi: {e}")

    if actie.startswith("bluetooth "):
        modus = re.sub(r"^bluetooth\s*", "", actie).strip()
        try:
            return voer_bluetooth_actie_uit(modus)
        except Exception as e:
            return tekst_voor_taal(f"Error changing Bluetooth: {e}", f"Fout bij aanpassen van bluetooth: {e}")

    if actie.startswith("open browser url::"):
        browser_sleutel, url = split_pad_payload(actie)
        try:
            open_url_in_browser(browser_sleutel, url)
            return tekst_voor_taal(
                f"Opened URL in {browser_label(browser_sleutel)}",
                f"URL geopend in {browser_label(browser_sleutel)}"
            )
        except Exception as e:
            return tekst_voor_taal(
                f"Error opening URL in browser: {e}",
                f"Fout bij openen van URL in browser: {e}"
            )

    if actie.startswith("open new tabs "):
        doelen = haal_webdoelen_uit_actie(actie, "open new tabs")
        for doel in doelen:
            webbrowser.open_new_tab(webdoel_naar_url(doel))
        namen = ", ".join(titel_voor_webdoel(doel) for doel in doelen)
        return tekst_voor_taal(
            f"Opened new tabs: {namen}",
            f"Nieuwe tabbladen geopend: {namen}"
        )

    if actie.startswith("open new tab "):
        doel = re.sub(r"^open new tab\s*", "", actie).strip()
        webbrowser.open_new_tab(webdoel_naar_url(doel))
        naam = titel_voor_webdoel(doel)
        return tekst_voor_taal(
            f"Opened {naam} in a new tab",
            f"{naam} geopend in een nieuw tabblad"
        )

    if actie.startswith("open websites "):
        doelen = haal_webdoelen_uit_actie(actie, "open websites")
        for index, doel in enumerate(doelen):
            url = webdoel_naar_url(doel)
            if index == 0:
                webbrowser.open(url)
            else:
                webbrowser.open_new_tab(url)
        namen = ", ".join(titel_voor_webdoel(doel) for doel in doelen)
        return tekst_voor_taal(
            f"Opened websites: {namen}",
            f"Websites geopend: {namen}"
        )

    if actie.startswith("open website "):
        doel = re.sub(r"^open website\s*", "", actie).strip()
        webbrowser.open(webdoel_naar_url(doel))
        naam = titel_voor_webdoel(doel)
        return tekst_voor_taal(
            f"Opened {naam}",
            f"{naam} geopend"
        )

    if actie.startswith("search google "):
        zoekterm = re.sub(r"^search google\s*", "", actie).strip()
        webbrowser.open_new_tab(f"https://www.google.com/search?q={quote_plus(zoekterm)}")
        return tekst_voor_taal(
            f"Opened Google search for '{zoekterm}'",
            f"Google-zoekopdracht geopend voor '{zoekterm}'"
        )

    if actie.startswith("search youtube "):
        zoekterm = re.sub(r"^search youtube\s*", "", actie).strip()
        webbrowser.open_new_tab(f"https://www.youtube.com/results?search_query={quote_plus(zoekterm)}")
        return tekst_voor_taal(
            f"Opened YouTube search for '{zoekterm}'",
            f"YouTube-zoekopdracht geopend voor '{zoekterm}'"
        )

    if "youtube" in actie:
        webbrowser.open(instellingen["youtube_url"])
        return tekst_voor_taal("YouTube opened", "YouTube geopend")

    if "google" in actie:
        webbrowser.open(instellingen["google_url"])
        return tekst_voor_taal("Google opened", "Google geopend")

    if actie.startswith("create folder"):
        mapnaam = mapnaam_uit_actie(actie)
        try:
            os.makedirs(mapnaam, exist_ok=True)
            return tekst_voor_taal(
                f"Folder '{mapnaam}' created",
                f"Map '{mapnaam}' aangemaakt"
            )
        except Exception as e:
            return tekst_voor_taal(
                f"Error creating folder: {e}",
                f"Fout bij maken van map: {e}"
            )

    if actie.startswith("create file "):
        return voer_maak_bestand_uit(actie)

    if actie.startswith("copy path::"):
        return voer_kopieer_pad_uit(actie)

    if actie.startswith("move path::"):
        return voer_verplaats_pad_uit(actie)

    if actie.startswith("rename path::"):
        return voer_hernoem_pad_uit(actie)

    if actie.startswith("open folder "):
        folder_pad = re.sub(r"^open folder\s*", "", actie).strip()
        try:
            open_windows_doel(folder_pad)
            return tekst_voor_taal(
                f"Opened folder: {folder_pad}",
                f"Map geopend: {folder_pad}"
            )
        except Exception as e:
            return tekst_voor_taal(
                f"Error opening folder: {e}",
                f"Fout bij openen van map: {e}"
            )

    if actie.startswith("open file "):
        bestand_pad = re.sub(r"^open file\s*", "", actie).strip()
        try:
            open_windows_doel(bestand_pad)
            return tekst_voor_taal(
                f"Opened file: {bestand_pad}",
                f"Bestand geopend: {bestand_pad}"
            )
        except Exception as e:
            return tekst_voor_taal(
                f"Error opening file: {e}",
                f"Fout bij openen van bestand: {e}"
            )

    if actie.startswith("open setting "):
        instelling_sleutel = re.sub(r"^open setting\s*", "", actie).strip()
        details = SYSTEM_SETTING_TARGETS.get(instelling_sleutel)
        if details:
            try:
                open_windows_doel(details["target"])
                return tekst_voor_taal(
                    f"Opened {details['label_en']}",
                    f"{details['label_nl']} geopend"
                )
            except Exception as e:
                return tekst_voor_taal(
                    f"Error opening {details['label_en']}: {e}",
                    f"Fout bij openen van {details['label_nl']}: {e}"
                )

    if actie.startswith("open app raw::"):
        app_doel = re.sub(r"^open app raw::", "", actie).strip()
        try:
            subprocess.Popen(["cmd", "/c", "start", "", app_doel])
            return tekst_voor_taal(
                f"Opened app: {app_doel}",
                f"App geopend: {app_doel}"
            )
        except Exception as e:
            return tekst_voor_taal(
                f"Error opening app: {e}",
                f"Fout bij openen van app: {e}"
            )

    if actie.startswith("open app "):
        app_sleutel = re.sub(r"^open app\s*", "", actie).strip()
        details = SYSTEM_APP_TARGETS.get(app_sleutel)
        if details:
            command = list(details["command"])
            if app_sleutel == "file explorer":
                command = ["explorer", instellingen["verkenner_start_map"]]

            try:
                subprocess.Popen(command)
                return tekst_voor_taal(
                    f"Opened {details['label_en']}",
                    f"{details['label_nl']} geopend"
                )
            except Exception as e:
                return tekst_voor_taal(
                    f"Error opening {details['label_en']}: {e}",
                    f"Fout bij openen van {details['label_nl']}: {e}"
                )

    if actie == "open notepad":
        os.system("notepad")
        return tekst_voor_taal("Notepad opened", "Kladblok geopend")

    if actie == "open calculator":
        subprocess.Popen(["calc"])
        return tekst_voor_taal("Calculator opened", "Rekenmachine geopend")

    if actie == "open paint":
        subprocess.Popen(["mspaint"])
        return tekst_voor_taal("Paint opened", "Paint geopend")

    if actie == "open command prompt":
        subprocess.Popen(["cmd"])
        return tekst_voor_taal("Command Prompt opened", "Opdrachtprompt geopend")

    if actie == "open file explorer":
        verkenner_map = instellingen["verkenner_start_map"]
        subprocess.Popen(["explorer", verkenner_map])
        return tekst_voor_taal(
            f"File Explorer opened in: {verkenner_map}",
            f"Verkenner geopend in: {verkenner_map}"
        )

    if actie == "help":
        return tekst_voor_taal(
            "Ask me naturally what you want to do. I can help with browser tasks, files and folders, planner items, memory, system info, and explanation questions. If you want ideas, ask for examples or say help with browser, files, planner, or automation.",
            "Vraag me gewoon natuurlijk wat je wilt doen. Ik kan helpen met browseracties, bestanden en mappen, plannerzaken, geheugen, systeeminfo en uitlegvragen. Als je ideeën wilt, vraag dan om voorbeelden of zeg hulp met browser, bestanden, planner of automation."
        )

    return kan_niet_oproepen_bericht()


def voer_commando_uit(tekst):
    """Execute a command and return a response."""
    geheugen_bericht = behandel_geheugen_commando(tekst)
    if geheugen_bericht:
        update_routering_context("memory", "memory", "memory", "completed")
        registreer_gesprek_uitwisseling(tekst, geheugen_bericht)
        spreek_uit(geheugen_bericht)
        return geheugen_bericht

    routering = analyseer_verzoek_routering(tekst)
    update_routering_context(routering["intent"], routering["tool"], routering["category"], "routing")

    if routering["intent"] == "answer":
        antwoord_tool, antwoord_bericht = maak_best_mogelijke_antwoordtekst(tekst)
        if antwoord_bericht:
            bericht = antwoord_bericht
            update_routering_context(routering["intent"], antwoord_tool, routering["category"], "answered")
        else:
            bericht = kan_niet_oproepen_bericht(tekst)
            update_routering_context(routering["intent"], "fallback", routering["category"], "fallback")

        registreer_gesprek_uitwisseling(tekst, bericht)
        spreek_uit(bericht)
        return bericht

    plan = list(routering.get("plan", []))

    if not plan and routering.get("tool") == "online_action_planner":
        update_routering_context(routering["intent"], routering["tool"], routering["category"], "tool_planning")
        agent_resultaat = probeer_online_ai_agent(tekst, routering)
        if agent_resultaat:
            if agent_resultaat.get("plan"):
                update_gesprek_context(agent_resultaat["plan"], agent_resultaat.get("resultaten", []))

            bericht = agent_resultaat["bericht"]
            if routering["intent"] == "hybrid":
                antwoord_tool, antwoord_bericht = maak_best_mogelijke_antwoordtekst(tekst, agent_resultaat.get("resultaten", []))
                if antwoord_bericht:
                    bericht = antwoord_bericht
                    update_routering_context(routering["intent"], antwoord_tool, routering["category"], "answered")
                else:
                    update_routering_context(routering["intent"], "online_action_planner", routering["category"], "completed")
            else:
                update_routering_context(routering["intent"], "online_action_planner", routering["category"], "completed")

            registreer_gesprek_uitwisseling(tekst, bericht)
            spreek_uit(bericht)
            return bericht

    plan = orden_plan_op_prioriteit(plan)
    plan_resultaat = voer_plan_uit(plan)
    bericht = plan_resultaat["bericht"]

    if routering["intent"] == "hybrid":
        if plan_resultaat["bekende_stappen"]:
            update_gesprek_context(plan_resultaat["bekende_stappen"], plan_resultaat["bekende_resultaten"])

        antwoord_tool, antwoord_bericht = maak_best_mogelijke_antwoordtekst(tekst, plan_resultaat["bekende_resultaten"])
        if antwoord_bericht:
            bericht = antwoord_bericht
            update_routering_context(routering["intent"], antwoord_tool, routering["category"], "answered")
        elif plan_resultaat["bekende_stappen"]:
            update_routering_context(routering["intent"], "local_plan", routering["category"], "completed")
        else:
            bericht = tekst_voor_taal(
                "I can't call that task cleanly right now. Split the action from the question, and I'll try again in two smaller steps.",
                "Ik kan die taak nu niet netjes oproepen. Splits de actie en de vraag even op, dan probeer ik het opnieuw in twee kleinere stappen."
            )
            update_routering_context(routering["intent"], "fallback", routering["category"], "fallback")
    elif plan_resultaat["heeft_onbekende_stap"]:
        antwoord_tool, antwoord_bericht = maak_best_mogelijke_antwoordtekst(tekst, plan_resultaat["bekende_resultaten"])
        if antwoord_bericht:
            bericht = antwoord_bericht
            if plan_resultaat["bekende_stappen"]:
                update_gesprek_context(plan_resultaat["bekende_stappen"], plan_resultaat["bekende_resultaten"])
            update_routering_context(routering["intent"], antwoord_tool, routering["category"], "answered")
        else:
            bericht = kan_niet_oproepen_bericht(tekst)
            update_routering_context(routering["intent"], "fallback", routering["category"], "fallback")
    else:
        update_gesprek_context(plan, plan_resultaat["resultaten"])
        update_routering_context(routering["intent"], "local_plan", routering["category"], "completed")

    registreer_gesprek_uitwisseling(tekst, bericht)
    spreek_uit(bericht)
    return bericht

@app.route('/')
def index():
    return render_template('index.html', instellingen=instellingen, spraak_beschikbaar=SPRAAK_BESCHIKBAAR)


@app.route('/api/runtime-version', methods=['GET'])
def get_runtime_version():
    return jsonify({
        'build_id': APP_BUILD_ID,
        'started_at': APP_START_TIMESTAMP,
    })


@app.route('/service-worker.js', methods=['GET'])
def service_worker():
    response = app.send_static_file('service-worker.js')
    response.headers['Cache-Control'] = 'no-store, max-age=0'
    response.headers['Service-Worker-Allowed'] = '/'
    return response

@app.route('/api/commando', methods=['POST'])
def execute_command():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({
            'status': 'error',
            'message': tekst_voor_taal('Invalid JSON payload', 'Ongeldige JSON-payload')
        }), 400

    commando = str(data.get('commando', '')).strip()
    
    if not commando:
        return jsonify({
            'status': 'error',
            'message': tekst_voor_taal('No command provided', 'Geen opdracht opgegeven')
        }), 400
    
    start_tijd = time.time()
    try:
        bericht = voer_commando_uit(commando)
        duur_ms = int(round((time.time() - start_tijd) * 1000))
        GESPREK_CONTEXT['laatste_commando'] = str(commando or '').strip()
        GESPREK_CONTEXT['laatste_commando_at'] = time.time()
        GESPREK_CONTEXT['laatste_commando_duur_ms'] = duur_ms
        GESPREK_CONTEXT['laatste_commando_succes'] = True
        return jsonify({
            'status': 'success',
            'message': bericht,
            'duration_ms': duur_ms,
            'route': huidige_routering_context(),
            'pending_confirmation': maak_pending_bevestiging_payload(),
        })
    except Exception as e:
        duur_ms = int(round((time.time() - start_tijd) * 1000))
        GESPREK_CONTEXT['laatste_commando'] = str(commando or '').strip()
        GESPREK_CONTEXT['laatste_commando_at'] = time.time()
        GESPREK_CONTEXT['laatste_commando_duur_ms'] = duur_ms
        GESPREK_CONTEXT['laatste_commando_succes'] = False
        huidige_route = huidige_routering_context()
        update_routering_context(
            huidige_route.get('intent', ''),
            huidige_route.get('tool', ''),
            huidige_route.get('category', ''),
            'error',
            str(e),
        )
        return jsonify({
            'status': 'error',
            'message': str(e),
            'duration_ms': duur_ms,
            'route': huidige_routering_context(),
            'pending_confirmation': maak_pending_bevestiging_payload(),
        })

@app.route('/api/spraak', methods=['POST'])
def speech_command():
    if not SPRAAK_BESCHIKBAAR:
        return jsonify({'status': 'error', 'message': tekst_voor_taal('Speech recognition is not available', 'Spraakherkenning is niet beschikbaar')})
    
    try:
        tekst = herken_spraak()
        if tekst:
            bericht = voer_commando_uit(tekst)
            return jsonify({'status': 'success', 'gesproken': tekst, 'message': bericht})
        else:
            return jsonify({'status': 'error', 'message': tekst_voor_taal('Could not understand speech', 'Ik kon de spraak niet verstaan')})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/instellingen', methods=['GET'])
def get_settings():
    return jsonify(instellingen)

@app.route('/api/dashboard', methods=['GET'])
def get_dashboard():
    return jsonify(maak_dashboard_payload())

@app.route('/api/instellingen', methods=['POST'])
def update_settings():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({
            'status': 'error',
            'message': tekst_voor_taal('Invalid JSON payload', 'Ongeldige JSON-payload')
        }), 400

    global instellingen
    
    for key, value in data.items():
        if key in instellingen:
            instellingen[key] = value

    synchroniseer_taalinstellingen(instellingen)
    
    sla_instellingen_op(instellingen)
    return jsonify({'status': 'success', 'message': tekst_voor_taal('Settings saved', 'Instellingen opgeslagen')})


def vind_beschikbare_poort(start=5000, eind=5010):
    for poort in range(start, eind + 1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.2)
            if sock.connect_ex(("127.0.0.1", poort)) != 0:
                return poort
    return start


def verwijder_auto_open_marker():
    try:
        AUTO_OPEN_MARKER_FILE.unlink(missing_ok=True)
    except Exception:
        pass


def markeer_auto_open_uitgevoerd():
    if AUTO_OPEN_MARKER_FILE.exists():
        return False

    try:
        AUTO_OPEN_MARKER_FILE.write_text(str(time.time()), encoding='utf-8')
    except Exception:
        # Als we niet kunnen schrijven, openen we alsnog voor usability.
        return True
    return True


def browser_pad_kandidaten():
    programma_bestanden = Path(os.environ.get('ProgramFiles', ''))
    programma_bestanden_x86 = Path(os.environ.get('ProgramFiles(x86)', ''))
    lokale_appdata = Path(os.environ.get('LocalAppData', ''))

    kandidaten = [
        programma_bestanden_x86 / 'Microsoft/Edge/Application/msedge.exe',
        programma_bestanden / 'Microsoft/Edge/Application/msedge.exe',
        lokale_appdata / 'Microsoft/Edge/Application/msedge.exe',
        programma_bestanden_x86 / 'Google/Chrome/Application/chrome.exe',
        programma_bestanden / 'Google/Chrome/Application/chrome.exe',
        lokale_appdata / 'Google/Chrome/Application/chrome.exe',
    ]

    resultaat = []
    gezien = set()
    for pad in kandidaten:
        pad_str = str(pad)
        if not pad_str or pad_str in gezien:
            continue
        gezien.add(pad_str)
        resultaat.append(pad)
    return resultaat


def open_url_in_app_venster(url):
    for browser_pad in browser_pad_kandidaten():
        if browser_pad.exists():
            try:
                subprocess.Popen(
                    [str(browser_pad), f'--app={url}', '--new-window'],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                return True
            except Exception:
                continue

    for browser_commando in ('msedge', 'chrome'):
        try:
            subprocess.Popen(
                [browser_commando, f'--app={url}', '--new-window'],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return True
        except Exception:
            continue

    return False


def open_echo_interface(url, window_mode='browser'):
    mode = str(window_mode or 'browser').strip().lower()
    if mode == 'app' and open_url_in_app_venster(url):
        return
    webbrowser.open(url)


def moet_auto_openen(auto_open, auto_reload, open_on_reload):
    if not auto_open:
        return False

    if not auto_reload:
        return True

    is_reloader_child = os.environ.get('WERKZEUG_RUN_MAIN') == 'true'
    if not is_reloader_child:
        return False

    if open_on_reload:
        return True

    return markeer_auto_open_uitgevoerd()


def bepaal_runtime_poort(voorkeurs_poort):
    gekozen_poort = os.environ.get('ECHO_SELECTED_PORT')
    if gekozen_poort:
        return begrens_int_waarde(gekozen_poort, voorkeurs_poort, 1024, 65535)

    poort = vind_beschikbare_poort(voorkeurs_poort, min(voorkeurs_poort + 10, 65535))
    os.environ['ECHO_SELECTED_PORT'] = str(poort)
    return poort

if __name__ == '__main__':
    voorkeurs_poort = begrens_int_waarde(os.environ.get('ECHO_PORT', '5000'), 5000, 1024, 65535)
    poort = bepaal_runtime_poort(voorkeurs_poort)
    url = f'http://127.0.0.1:{poort}'
    auto_open = parseer_bool_waarde(os.environ.get('ECHO_AUTO_OPEN', 'true'), True)
    auto_reload = parseer_bool_waarde(os.environ.get('ECHO_AUTO_RELOAD', 'false'), False)
    open_on_reload = parseer_bool_waarde(os.environ.get('ECHO_OPEN_ON_RELOAD', 'false'), False)
    window_mode = str(os.environ.get('ECHO_WINDOW_MODE', 'browser') or 'browser').strip().lower()
    is_reloader_child = os.environ.get('WERKZEUG_RUN_MAIN') == 'true'

    if auto_reload and not is_reloader_child:
        verwijder_auto_open_marker()

    if poort == voorkeurs_poort:
        print(f'Echo starting on: {url}')
    else:
        print(f'Echo preferred port {voorkeurs_poort} was unavailable, starting on: {url}')

    print(f'Window mode: {window_mode} | Auto reload: {"on" if auto_reload else "off"}')

    if not auto_reload or is_reloader_child:
        start_planning_monitor()

    if moet_auto_openen(auto_open, auto_reload, open_on_reload):
        threading.Timer(1.0, lambda: open_echo_interface(url, window_mode)).start()

    app.run(debug=auto_reload, use_reloader=auto_reload, port=poort)
