# 🤖 AI Assistent - Web Interface

Je AI assistent wordt nu in een mooie HTML interface uitgevoerd!

## Installatie

### Stap 1: Flask installeren
```powershell
pip install flask
```

### Stap 2: Server starten
```powershell
cd c:\Users\nordi\Desktop\ai
python server.py
```

De browser gaat automatisch openen op **http://localhost:5000**

## App-modus (zonder URL typen)

### One-click starten
```powershell
cd c:\Users\nordi\Desktop\ai
Start-Echo-App.bat
```

Dit start Echo in app-venster modus, zet auto-reload aan, en opent automatisch bij wijzigingen.

### Desktop-icoon maken
```powershell
powershell -ExecutionPolicy Bypass -File .\Install-Echo-Desktop-Shortcut.ps1
```

Dit maakt `Echo App.lnk` op je bureaublad.

## GitHub auto-sync

### Eenmalig syncen
```powershell
Sync-GitHub.bat -RepoUrl https://github.com/<user>/<repo>.git
```

### Doorlopend auto-syncen bij wijzigingen
```powershell
powershell -ExecutionPolicy Bypass -File .\Sync-GitHub.ps1 -RepoUrl https://github.com/<user>/<repo>.git -Watch
```

> Als `git` niet geinstalleerd is, installeer eerst Git voor Windows.

## Portable zip maken

```powershell
powershell -ExecutionPolicy Bypass -File .\Build-Echo-App-Zip.ps1
```

Daarna staat je uitpakbare app-package hier:

- `release\Echo-App-Portable.zip`

## Hoe het werkt

- ✍️ **Typ commando's** - Voer commando's in via het invoerveld
- 🎤 **Spraak** - Klik op de knop en spreek je commando in
- ⚙️ **Instellingen** - Pas je voorkeuren aan via het instellingenmenu
- 💬 **Live chat** - Zie alle communicatie in het chatvenster

## Beschikbare commando's

- `open youtube` - Opent YouTube
- `open google` - Opent Google
- `maak map` - Maakt een nieuwe map
- `open kladblok` - Opent Kladblok
- `open verkenner` - Opent Verkenner
- `bereken 12*(8+3)` - Rekent veilige expressies uit
- `open chrome and go to gmail and search for invoice` - Browser-workflow in een specifieke browser
- `create file notes.txt` - Maakt een leeg bestand aan
- `list files in templates` - Toont de inhoud van een map
- `read README.md` - Laat een preview van een tekstbestand zien
- `summarize README.md` - Vat een tekstbestand samen
- `append hello world to notes.txt` - Voegt tekst toe aan een bestand en maakt het zonodig aan
- `overwrite notes.txt with hello` - Overschrijft een tekstbestand, met bevestiging als het al bestaat
- `rewrite README.md to be shorter` - Laat Echo een tekstbestand herschrijven met de lokale AI, na bevestiging
- `search files for ollama` - Zoekt in de workspace naar bestandsnamen en tekstmatches
- `copy README.md to demo123/README.md` - Kopieert een bestand of map
- `move test.txt to demo123/` - Verplaatst een bestand of map
- `rename old.txt to new.txt` - Hernoemt een bestand of map
- `delete test.txt` - Verwijdert een bestand of map na bevestiging
- `system info`, `battery status`, `disk space`, `ip address`, `current time` - Geeft lokale systeeminformatie
- `remember that my name is Nordin` - Slaat je naam of een feit op in langetermijngeheugen
- `save note buy milk` - Slaat een korte notitie op
- `what do you remember about me` - Laat Echo zijn opgeslagen langetermijngeheugen samenvatten
- `add task buy milk`, `show tasks`, `set timer for 5 minutes`, `remind me in 10 minutes to stretch`, `show agenda` - Planner, timers en herinneringen
- `read this page`, `summarize this page`, `summarize https://example.com` - Leest of vat webpagina's samen
- `fill form with Jan, jan@example.com, hallo`, `submit form` - Vult browserformulieren in via automation-modus
- `switch window`, `next tab`, `copy`, `paste`, `save` - Extra computerbesturing

## Instellingen (in HTML)

- 📝 **Naam** - Verander de naam van je AI
- 🔗 **URL's** - Stel YouTube en Google URL in
- 😊 **Emoji's** - Zet emoji's aan/uit
- 🔊 **Spraak** - Text-to-speech aan/uit

## Extra features

- **Spraakherkenning** (optioneel)
  ```powershell
  pip install SpeechRecognition pyttsx3 pyaudio
  ```

- **Haarscherpe lokale spraakherkenning met Whisper (GPU-ready)**
  Echo ondersteunt nu ook lokale Whisper-herkenning via `faster-whisper`, met automatische fallback naar de bestaande Google-herkenning als Whisper niet beschikbaar is.

  Zet in `.env`:
  ```env
  STT_PROVIDER=whisper
  WHISPER_MODEL=small
  WHISPER_DEVICE=auto
  WHISPER_COMPUTE_TYPE=auto
  WHISPER_BEAM_SIZE=5
  WHISPER_VAD_FILTER=true
  ```

  Praktische tips:
  - Gebruik `WHISPER_DEVICE=cuda` voor NVIDIA GPU-versnelling.
  - Start met `WHISPER_MODEL=small` of `medium` voor goede balans tussen snelheid en kwaliteit.
  - Laat `WHISPER_VAD_FILTER=true` aan voor betere robuustheid bij achtergrondgeluid.

- **Spraakuitgang** (text-to-speech)
  Zet aan in Instellingen > Spraak uitgang

- **Natuurlijkere stem via Cloud TTS (Google)**
  Voor een menselijkere stem kun je Google Cloud Text-to-Speech gebruiken. Echo blijft automatisch terugvallen op de lokale pyttsx3-stem als Cloud TTS niet beschikbaar is.

  Voeg dit toe aan `.env`:
  ```env
  TTS_PROVIDER=google
  GOOGLE_TTS_API_KEY=jouw_google_tts_api_key
  GOOGLE_TTS_VOICE=en-US-Neural2-F
  GOOGLE_TTS_SPEED=1.0
  GOOGLE_TTS_PITCH=0.0
  ```

  Voor Nederlands kun je bijvoorbeeld gebruiken:
  ```env
  GOOGLE_TTS_VOICE=nl-NL-Wavenet-C
  ```

- **Online AI-antwoorden** (optioneel)
  Echo leest nu automatisch een lokaal `.env`-bestand in bij het opstarten. De snelste route is:
  ```powershell
  Copy-Item .env.example .env
  # vul daarna je echte key in in .env
  python server.py
  ```
  Of zet de variabelen direct in je terminal:
  ```powershell
  $env:OPENAI_API_KEY = "jouw_api_key"
  $env:OPENAI_MODEL = "gpt-4.1-mini"
  python server.py
  ```
  Optioneel kun je ook `OPENAI_BASE_URL` zetten als je een andere OpenAI-compatibele provider gebruikt.

- **Lokale AI met Ollama**
  Dit project werkt nu ook direct met `Ollama` via dezelfde OpenAI-compatibele route. Een praktische lokale config is:
  ```env
  OPENAI_API_KEY=ollama
  OPENAI_BASE_URL=http://127.0.0.1:11434/v1
  OPENAI_MODEL=qwen2.5:3b
  OPENAI_TIMEOUT_SECONDS=180
  ```
  Daarna start je gewoon opnieuw:
  ```powershell
  python server.py
  ```
  Op jouw machine is `qwen2.5:3b` nu lokaal ingericht als standaardmodel.

- **Geheugen + documentcontext**
  Echo stuurt nu recent gesprek, opgeslagen langetermijngeheugen en relevante snippets uit je workspace mee naar het model. Daardoor kan hij consistenter reageren en beter verwijzen naar lokale projectcontext zoals `README.md`, instellingen en codebestanden.
  Je kunt expliciet dingen opslaan met commando's zoals `remember that ...`, `save note ...`, `what do you remember about me` en `clear memory`.
  Het langetermijngeheugen wordt automatisch bewaard in `echo_geheugen.json`.

- **Planner + notificaties**
  Echo kan nu taken, timers en herinneringen bewaren in `echo_planning.json`. Voorbeelden: `add task buy milk`, `show tasks`, `set timer for 5 minutes`, `remind me in 10 minutes to stretch` en `show agenda`.

- **Browser lezen + formulieren invullen**
  Met automation-modus en geavanceerde computerbesturing kan Echo de huidige tab-URL lezen, een webpagina lokaal ophalen en samenvatten, en formulierwaarden invullen. Voorbeelden: `read this page`, `summarize this page`, `summarize https://example.com`, `fill form with Jan, jan@example.com, hallo` en `submit form`.

- **Workspace-tools + systeeminfo**
  Echo kan nu ook mapinhoud tonen, tekstbestanden previewen of samenvatten, tekst toevoegen aan bestanden, bestanden overschrijven of met AI herschrijven, door de workspace zoeken en korte lokale systeeminformatie geven. Bij workspace-zoeken worden gevoelige lokale bestanden zoals `.env` niet meegenomen.

## Bestanden

- `server.py` - Flask webserver
- `templates/index.html` - HTML interface
- `ai.py` - Originele terminal versie (nog steeds beschikbaar)
- `instellingen.json` - Je opgeslagen instellingen
- `echo_geheugen.json` - Automatisch aangemaakt langetermijngeheugen
- `echo_planning.json` - Automatisch aangemaakte plannerdata voor taken, timers en herinneringen

## Problemen?

- **Browser opent niet** - Ga naar http://localhost:5000
- **Geen spraak** - Installeer: `pip install SpeechRecognition pyttsx3 pyaudio`
- **Microfoon werkt niet** - Controleer je audioapparatuur
- **Online AI reageert niet** - Controleer of `OPENAI_API_KEY` gezet is in dezelfde terminal waarin je de server start
- **Online AI reageert niet met `.env`** - Controleer of `.env` naast `server.py` staat en een geldige `OPENAI_API_KEY` bevat
- **Cloud stem klinkt niet** - Controleer `TTS_PROVIDER=google`, een geldige `GOOGLE_TTS_API_KEY`, en dat je op Windows draait (de huidige cloud-afspeelroute gebruikt `winsound`)
- **Whisper luistert niet lokaal** - Controleer `STT_PROVIDER=whisper`, of `faster-whisper` is geïnstalleerd, en zet `WHISPER_DEVICE=cuda` als je GPU wilt gebruiken

Veel plezier! 🎉
