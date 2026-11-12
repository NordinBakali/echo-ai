# 🤖 AI Assistent - Web Interface

Je AI assistent wordt nu in een mooie HTML interface uitgevoerd!

## Installatie

### Stap 1: Benodigde pakketten installeren
```powershell
pip install -r requirements.txt
python -m playwright install chromium
```

### Stap 2: Server starten
```powershell
cd "c:\Users\nordi\Desktop\echo ai\echo-ai"
python server.py
```

De browser gaat automatisch openen op **http://localhost:5000**

### Testen op je telefoon (zelfde wifi)
Echo start nu standaard met LAN-toegang zodat je ook op je telefoon kunt testen.

1. Start Echo normaal.
2. Kijk in de terminal naar de regel **Phone test URL(s)**.
3. Open die URL op je telefoon (telefoon en pc op hetzelfde netwerk).

Snelle commando's:
- `phone status` - toont of mobiele toegang actief is
- `phone link` - geeft direct de testlink

Screenshots op je telefoon opslaan:
- Gebruik `take screenshot`.
- In **Phone Lab** verschijnt automatisch de laatste screenshot.
- Op je telefoon start Echo direct een download; handmatig kan ook via **Save Last Screenshot**.

### Samsung voice fallback
Als je Samsung-browser geen ingebouwde Web Speech API heeft, schakelt Echo automatisch naar **Quick voice capture**:

1. Tik op `Quick voice capture`.
2. Neem je stemopdracht op.
3. Echo uploadt de opname en transcribeert die server-side.

Tip: zeg direct `hey echo ...` in dezelfde opname voor wake-compatibiliteit.

## App-modus (zonder URL typen)

### One-click starten
Dubbelklik op `Echo-App.vbs` in de app-map.

Deze launcher draait Echo in Flask app-modus en voorkomt dubbele instances:
- als Echo al draait, wordt geen tweede server gestart;
- bij code-updates blijft dezelfde app-instance actief.

Voor live code-sync tijdens ontwikkelen:
Dubbelklik op `Echo-App-LiveSync.vbs`.

Voor de nieuwe Auto-Sync launcher:
Dubbelklik op `Echo-App-AutoSync.vbs`.

Alternatief via terminal:
```powershell
cd c:\Users\nordi\Desktop\ai
Start-Echo-App.bat
```

Dit start Echo in app-venster modus, zet auto-reload aan, en opent automatisch bij wijzigingen.
`Echo-App.vbs` start dezelfde launcher zonder zichtbaar terminalvenster.
`Echo-App-LiveSync.vbs` start Echo en activeert tegelijk continue sync naar `release\Echo-App`.
`Echo-App-AutoSync.vbs` start dezelfde continue sync-flow met een duidelijke aparte launchernaam.
Bij code-updates blijft nu hetzelfde Echo-venster/tabblad actief; Echo ververst die instance automatisch zonder extra tabbladen te openen.

### Wake listener ("hey echo" opent app als die dicht is)
Start de wake listener eenmalig:
```powershell
Start-Echo-WakeListener.bat
```

Of verborgen:
- Dubbelklik `Echo-Wake-Listener.vbs`

Wanneer je "hey echo" zegt:
- opent Echo als de app dicht is;
- opent geen extra venster als Echo al zichtbaar open staat.

### Desktop-icoon maken
```powershell
powershell -ExecutionPolicy Bypass -File .\Install-Echo-Desktop-Shortcut.ps1
```

Dit maakt `Echo App.lnk` op je bureaublad.
Als `Echo-App.vbs` bestaat, gebruikt de snelkoppeling automatisch die one-click launcher.
Daarnaast wordt ook `Echo App (Live Sync).lnk` aangemaakt voor starten met continue code-sync.
En er wordt `Echo App (Auto Sync).lnk` aangemaakt voor de nieuwe Auto-Sync launcher.
Ook wordt `Echo Wake Listener.lnk` aangemaakt voor "hey echo" wake-open gedrag.
En er wordt automatisch een opstart-snelkoppeling geplaatst in je Windows Opstart-map:

- `Echo App (Auto Sync).lnk`

Daardoor start Echo vanzelf bij inloggen, inclusief Auto Sync.

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

## GitHub Actions download (voor clients)

Na elke push op `main` (of handmatig via workflow dispatch) bouwt GitHub Actions automatisch een downloadbaar artifact:

1. Open je repository op GitHub.
2. Ga naar **Actions**.
3. Open workflow **Build Echo Portable**.
4. Download artifact **Echo-App-Portable**.

Dit artifact bevat `Echo-App-Portable.zip` zodat clients direct kunnen reviewen.

## Hoe het werkt

- ✍️ **Typ commando's** - Voer commando's in via het invoerveld
- 🎤 **Spraak** - Klik op de knop en spreek je commando in (op Samsung kan dit `Quick voice capture` zijn)
- ⚙️ **Instellingen** - Pas je voorkeuren aan via het instellingenmenu
- 💬 **Live chat** - Zie alle communicatie in het chatvenster

## Echo Werkruimte

Open **Echo Workspace / Werkruimte** in het dashboard. De werkruimte volgt de taalinstelling van Echo; voor audio kun je de gesproken taal afzonderlijk kiezen. Daar vind je vier hulpmiddelen:

- **Spraaknotities:** neem audio op of upload een spraakbericht (maximaal 12 MB), kies zo nodig de gesproken taal en laat Echo de transcriptie omzetten naar een bewerkbare Markdown-notitie. Je kunt de notitie kopiëren of downloaden; die wordt niet automatisch opgeslagen. Whisper ondersteunt meer audioformaten dan de Google-fallback en kan bij het eerste gebruik een model moeten downloaden.
- **Later lezen:** voeg een openbare artikel-URL toe. Echo bewaart de titel, een korte samenvatting en labels; je kunt zoeken, filteren, artikelen als gelezen of ongelezen markeren en verwijderen.
- **Vertalen:** plak een e-mail of tekst, of upload een PDF, DOCX, EML, TXT of Markdown-bestand. Kies de doeltaal en geef eventueel extra context voor toon en woordkeuze. Het resultaat is bewerkbare tekst; de oorspronkelijke documentopmaak wordt niet als Word- of PDF-bestand behouden.
- **Samenvatten:** plak tekst, upload een document of geef een openbare artikel-URL op. Lange bronnen worden in delen verwerkt. Grote documenten kunnen daardoor enkele minuten duren en meerdere modelaanvragen kosten.

Documenten mogen maximaal 20 MB en 1.000 PDF-pagina's bevatten; de uitgelezen tekst mag maximaal 600.000 tekens zijn. Webpagina's en PDF's via een URL zijn beperkt tot 5 MB en moeten openbaar bereikbaar zijn; inlogmuren worden niet omzeild en websites die hun tekst uitsluitend met JavaScript laden werken mogelijk niet. Plak in dat geval de artikeltekst in het samenvatveld. Alleen selecteerbare PDF-tekst wordt verwerkt: voor scans is eerst OCR nodig. Informatie in afbeeldingen en sommige onderdelen van Word-documenten kan ontbreken; Echo toont daarvoor een waarschuwing. E-mailbijlagen moeten afzonderlijk worden geüpload.

Deze functies vereisen een ingeschakeld, geconfigureerd OpenAI-compatibel AI-model, bijvoorbeeld OpenAI, Azure OpenAI of Ollama (zie **Online AI-antwoorden** en **Lokale AI met Ollama** hieronder). De tekst wordt naar dat ingestelde model gestuurd; spraakherkenning kan daarnaast Google gebruiken als Whisper niet beschikbaar is. Deel uitsluitend gegevens die je daarvoor mag gebruiken en controleer AI-resultaten op fouten.

De leeslijst staat standaard lokaal onder `%LOCALAPPDATA%\Echo\workspace\personal`; demo-modus gebruikt een aparte gedeelde `demo`-map. In enterprise-modus krijgt iedere bedrijfsgebruiker een eigen leeslijst onder de enterprise-gegevensmap. Met `ECHO_WORKSPACE_DATA_DIR` kun je de locatie voor persoonlijke en demo-leeslijsten aanpassen. De lijst bevat de URL, inclusief eventuele queryparameters, maar niet de volledige artikeltekst. Maak zelf een back-up van deze gegevens. In de gewone modus gebruikt Echo geen afzonderlijke login: gebruik die alleen op een vertrouwd netwerk; kies anders de beveiligde demo- of enterprise-modus.

## Aanwezigheidsdetectie & Beveiliging (Windows)

Open **Aanwezigheid & Beveiliging / Presence & Security** in het dashboard op de pc
waar Echo draait. Gebruik `http://localhost:5000` (of de poort die Echo toont).
Dit werkt niet via je telefoon, een LAN-adres, demo-modus of bedrijfsmodus.

1. Herstart Echo via `Start-Echo-App.bat` of `Echo-App.vbs` om ook het nieuwe
   camerapakket te installeren. Bij handmatig starten: `python -m pip install -r requirements.txt`.
2. Sluit Camera Lab, Teams en andere apps die de webcam gebruiken. Geef in
   **Windows-instellingen > Privacy en beveiliging > Camera** desktop-apps toegang.
3. Kies de wachttijd (standaard **30 seconden**, instelbaar van 10 tot 600),
   het cameranummer (**0** is meestal de standaardcamera; probeer anders 1 of 2)
   en wel of geen geluid bij terugkomst.
4. Vink de toestemming aan en klik **Detectie inschakelen**. Kijk twee seconden
   recht in de camera en wacht op **De bewaking is actief**.
5. Loop weg. Als gedurende de wachttijd geen gezicht zichtbaar is, vraagt Echo
   Windows te vergrendelen. Bij terugkomst en twee seconden zichtbaar gezicht
   klinkt optioneel eenmaal een kort geluid op de pc.
6. Klik **Detectie stoppen** om de camera vrij te geven of instellingen te wijzigen.
   Alleen de pagina of het app-venster sluiten stopt de achtergrondserver niet
   noodzakelijk, en dus ook niet de detectie. Een afgesloten of herstartte server
   stopt de detectie; na elke Echo-herstart moet je haar bewust opnieuw inschakelen.
   Instellingen gelden voor de lopende serversessie.

**Ontgrendelen:** Echo ontgrendelt Windows niet en bewaart geen pincode of wachtwoord.
Gebruik **Windows-instellingen > Accounts > Aanmeldingsopties > Gezichtsherkenning
(Windows Hello)** met een geschikte IR-camera, of ontgrendel met je pincode/wachtwoord.
Een gewone webcam wordt door deze functie geen Windows Hello-camera.

**Privacy en beperkingen:** de lokale OpenCV-gezichtsdetector gebruikt alleen
camerabeelden in het werkgeheugen. Er worden geen beelden, gezichtsprofielen of
identiteiten opgeslagen of naar een AI-dienst verstuurd. Dit is aanwezigheidsdetectie,
geen identiteitscontrole of vervanging van Windows-beveiliging: ieder gezicht, ook
een foto, kan de detectie beinvloeden. Slecht licht of wegkijken kan onbedoeld
vergrendelen veroorzaken. Laat de gewone Windows-vergrendeltimer aan en gebruik
bij twijfel `Windows+L`.

Bij een camera-, vergrendel- of geluidsfout stopt de detectie en verschijnt een
foutmelding op de aanwezigheidspagina. Een camerafout veroorzaakt geen vergrendeling.
Het terugkomstsignaal werkt alleen zolang de pc wakker is en de camera ook op het
vergrendelscherm beschikbaar blijft. Als Windows de camera blokkeert of Windows Hello
haar overneemt, kan Echo geen terugkomst melden; start de detectie na het ontgrendelen
opnieuw. Stop detectie of kies een andere webcam als Windows Hello en Echo conflicteren.

## Houding & Gebaren: lokale camera-assistent

Open **Houding & Gebaren / Posture & Gestures** in het dashboard op de Windows-pc
waar Echo draait, via `localhost` of `127.0.0.1`. Dit is uitgeschakeld in demo- en
bedrijfsmodus en niet op afstand te bedienen. Installeer bij handmatig starten
eerst `python -m pip install -r requirements.txt` en herstart de server.
In het dashboard kun je de pagina ook vinden door bij **Filter acties** op
`Spotify`, `camera` of `gebaren` te zoeken; **Escape** wist de zoekopdracht.
Met **NL / EN** bovenaan wissel je alleen de taal van deze pagina; de algemene
taalinstelling van Echo verandert niet. Het overzicht toont apart of de camera
aanstaat, of je hand is gescand en of gebaaracties aanstaan. Bij een verbroken
verbinding worden deze statussen **onbekend**: de camera kan dan nog actief zijn.
Bij een upgrade van de eerdere aanwezigheidsfunctie vervangt de launcher het oude
`opencv-python-headless` automatisch door `opencv-contrib-python`. Bij handmatig
upgraden: sluit de server, voer eenmalig
`python -m pip uninstall -y opencv-python-headless opencv-contrib-python` uit en
installeer daarna opnieuw de requirements. Installeer niet beide OpenCV-varianten
naast elkaar: ze gebruiken dezelfde Python-module.

### Houdingsherinneringen

1. Kies cameranummer **0** (of je andere webcam), vink **Houdingsherinneringen**
   aan, geef toestemming en start de camera-assistent.
2. Zet de camera vast, zorg voor goed licht en breng je hoofd en beide schouders
   in beeld. De gespiegeld weergegeven herkenningspunten helpen bij het richten.
3. Ga comfortabel rechtop zitten en klik **Rechte zithouding instellen**.
   Houd dit twee seconden vast en wacht op de bevestiging.
4. Echo vergelijkt daarna de positie van je hoofd ten opzichte van je schouders
   met deze referentie. Na standaard **30 seconden** onafgebroken vooroverzitten
   verschijnt een herinnering. De wachttijd is instelbaar tussen 10 en 300 seconden.
   Er verschijnt maximaal eenmaal per twee minuten een herinnering.
5. Je kunt apart een Windows-meldingsgeluid aanzetten en **Bureaubladmeldingen
   toestaan** aanklikken. Browsermeldingen vereisen toestemming en een geopend
   tabblad met deze pagina; zonder die toestemming blijven meldingen in Echo
   zichtbaar, ook in het dashboard.

Dit is een ruwe webcam-gebaseerde herinnering, geen medische beoordeling of
betrouwbare meting van je wervelkolom. Bij ontbrekende herkenningspunten pauzeert
de tijdmeting; Echo doet dan geen uitspraak over je houding. Kalibreer opnieuw
als je de camera verplaatst of anders gaat zitten.

### Handgebaren: één scan

1. Vink **Handgebaren herkennen** aan voordat je de camera-assistent start. Laat
   **Extra gebaren** aan voor wijzen, knijpen, V-teken, duimen en gebaren met twee handen;
   zet het uit als je alleen vegen en de vuist wilt gebruiken. Kies vooraf of
   vegen **muziek / Spotify** of **Windows-bureaubladen** bedienen. De instellingen
   voor camera, microfoon, houding en extra gebaren vind je onder **Camera,
   microfoon en meer instellingen**.
2. Geef toestemming en start de camera-assistent. Echo toont de herkenning zonder
   computeracties totdat je de handscan kiest. Houd je hele hand in beeld, met
   je handpalm naar de camera, en zorg voor voldoende licht. De verbonden lijnen
   tonen de herkende hand en vingers; dit is geen camerabeeld.
3. Klik **Hand scannen en gebaren activeren** en houd één open hand ongeveer één
   seconde stil tot de voortgangsbalk 100% bereikt. Laat je andere hand tijdens
   de scan zakken. **Na een geslaagde scan staan computeracties direct aan.**
   Je hoeft geen vuist te scannen; daarna werken beide handen. De scan controleert
   alleen of een open hand duidelijk zichtbaar is: hij herkent of authenticeert
   geen persoon en maakt geen persoonlijk handprofiel.
4. Gebruik **Handscan stoppen** om een lopende scan te annuleren of **Alleen
   oefenen** om computeracties direct uit te zetten. De status toont dan nog
   steeds wat wordt herkend.
   Na het oefenen of ontgrendelen kun je **Gebaaracties opnieuw activeren** kiezen.
5. Gebruik de gebaren:
   - Veeg een open hand in ongeveer een seconde horizontaal over minstens een
     kwart van de weergegeven schets. Naar rechts: volgend nummer/bureaublad.
     Naar links: vorig nummer/bureaublad. Media-acties gaan naar de Windows-mediaspeler;
     virtuele bureaubladen moeten al bestaan.
   - Houd een vuist **0,8 seconden** vast: Echo dempt de gekozen Windows-microfoon.
   - Laat je hand tussen eenmalige acties even zakken of toon duidelijk een ander
     gebaar. Een aangehouden gebaar wordt niet herhaald; tussen eenmalige acties
     zit minimaal twee seconden wachttijd. Volume met de duim herhaalt juist
     zolang je die vasthoudt.

**Spotify:** open Spotify en start eerst muziek, zodat Spotify de actieve
Windows-mediasessie is. Kies daarna **Muziek / Spotify** en activeer gebaaracties
met de handscan. Veeg naar links of rechts voor het vorige of volgende nummer;
een opgestoken wijsvinger die je **0,8 seconden stilhoudt** pauzeert of hervat de
actieve mediaspeler. Een bewegende wijsvinger telt niet als deze bewuste opdracht.
Een open hand blijft voor vegen en pauzeert muziek niet. Echo gebruikt
de gewone Windows-mediatoetsen: er wordt geen Spotify-account gekoppeld en een
andere actieve mediaspeler kan de actie ontvangen.

**Twee handen en extra gebaren:** je andere hand mag gewoon in beeld blijven; elk
gebaar werkt met beide handen. Met **Extra gebaren** aan:

| Gebaar | Actie |
| --- | --- |
| Open hand naar links/rechts vegen | Vorig/volgend nummer of bureaublad |
| Vuist 0,8 s vasthouden | Gekozen microfoon dempen |
| Wijsvinger (alleen wijsvinger omhoog) 0,8 s stilhouden | Afspelen/pauzeren, eenmaal per gebaar |
| Duim en wijsvinger bijna samen, andere drie vingers gestrekt | Na 0,4 s: verder uit elkaar = volume omhoog; dichterbij = omlaag |
| V-teken (wijs- en middelvinger) 0,8 s | Bureaublad tonen; nogmaals om vensters terug te halen |
| Duim omhoog vanuit een vuist | Volume omhoog, herhaalt elke 0,3 s zolang je vasthoudt |
| Duim omlaag vanuit een vuist | Volume omlaag, herhaalt elke 0,3 s zolang je vasthoudt |
| Twee vuisten 1 s vasthouden | Geluid van de speakers aan/uit (niet de microfoon) |
| Twee open handen uit elkaar / naar elkaar | Inzoomen / uitzoomen (Ctrl + / Ctrl -) |

**Knijpvolume:** richt je handpalm naar de camera, houd je middelvinger, ringvinger
en pink gestrekt en breng je duim en wijsvinger dicht bij elkaar. Houd dit **0,4 seconden**
stil voordat je de afstand verandert. Echo markeert beide vingertoppen in de
schets. Open daarna langzaam je duim en wijsvinger voor harder en breng ze weer
dichter bij elkaar voor zachter. Laat voor zachter bij het beginnen een kleine
ruimte tussen beide vingertoppen over; knijp die daarna dicht. Strek alle vingers
en begin opnieuw als je meer bereik nodig hebt, of gebruik het duimgebaar.
Je regelt het gewone Windows-systeemvolume in
kleine stapjes, hoogstens eenmaal per **0,3 seconden**. Dezelfde afstand
vasthouden verandert niets; kleine trillingen en alleen dichter naar de camera
bewegen tellen niet mee. Knijp met **één hand tegelijk**; andere handacties worden
tijdens het knijpen onderdrukt. Strek alle vingers om de bediening los te laten.
Bij onduidelijke of verloren herkenning vervalt de volumereferentie, zodat Echo
geen gemiste bewegingen inhaalt. Breng je duim en wijsvinger opnieuw samen als de
knijpherkenning is gestopt. **Alleen oefenen** en vergrendelen blijven alle
computeracties uitschakelen.

Wil je na het zoomen nog een keer zoomen, laat dan eerst een hand zakken. Twee handen
die tegelijk uit elkaar of naar elkaar bewegen, tellen nooit als veeg. Houd voor een
gewone vuist je duim tegen je vingers; een duidelijk omhoog of omlaag gestoken duim
regelt het volume. Echo gebruikt een vooraf getraind gebarenmodel; als dat een
open hand geen naam geeft, controleert Echo ook of alle vier vingers duidelijk
gestrekt zijn. Echo houdt rekening met wisselende links/rechts-labels en korte onderbrekingen,
maar voert bij een onduidelijke vorm niets uit. Houd twee handen voldoende uit elkaar; bij
overlappende handposities kan Echo ze niet betrouwbaar volgen en wacht het met
acties. Een langere onderbreking reset de vasthoudtijd. Na een eenmalige actie blijft
dezelfde handstand geblokkeerd totdat je hem duidelijk verandert of de hand even
uit beeld haalt. De scanstatus blijft alleen in het geheugen: na stoppen moet je
opnieuw scannen. Wil je instellingen wijzigen, stop dan de camera-assistent en
start en scan daarna opnieuw.

**Snellere herkenning:** Echo verwerkt handgebaren met een doeltempo van 20 beelden
per seconde; de schets wordt tijdens gebruik ook maximaal 20 keer per seconde
vernieuwd. De werkelijke snelheid en verwerkingstijd staan onder de schets.
De camera wordt continu uitgelezen zonder wachtrij van oude beelden; houdingsanalyse
draait op 5 controles per seconde om meer rekentijd voor je handen over te houden.
Je kunt je open hand eerst stilhouden en daarna vegen zonder een timerreset af te
wachten. De bewuste vuistduur van 0,8 seconden en de pauze van twee seconden tussen
acties blijven tegen onbedoelde bediening bestaan. Bij weinig licht of een trage
webcam kan de werkelijke snelheid lager zijn; zorg voor goede verlichting en zet
**Houdingsherinneringen** uit als je alleen gebaren gebruikt.

**Microfoon tijdens calls:** selecteer dezelfde microfoon als je bel-app gebruikt.
Open hiervoor **Camera, microfoon en meer instellingen**. Met **Microfoonlijst
verversen** kun je aangesloten apparaten opnieuw ophalen zonder de pagina te
herladen. Als je gebaren gebruikt en een eerder gekozen microfoon niet meer
beschikbaar is, kies je bewust een andere voordat je start; Echo schakelt niet
ongemerkt over op een ander apparaat. Standaard gebruikt Echo de
Windows-communicatiemicrofoon. De mute werkt op het Windows-apparaat; het
mute-icoon in Teams, Zoom, Discord of
een browser kan daardoor ongewijzigd blijven. Controleer dit eerst buiten een
echte call. Een vuist dempt
alleen: het is geen toggle en Echo schakelt de microfoon nooit vanzelf weer in.
Gebruik **Microfoon weer aan** of je Windows-geluidsinstellingen om bewust te
ontdempen. Stoppen of afsluiten laat een gedempte microfoon gedempt; na een volledige
serverherstart kun je haar via Windows-geluidsinstellingen weer inschakelen.
Als de wake-up-luisteraar dezelfde microfoon gebruikt, kan die je na het muten
ook niet meer horen. Gebruik dan de knop **Microfoon weer aan**, niet een spraakopdracht.

### Privacy, camera delen en stoppen

De eerste start haalt ongeveer 14 MB aan vooraf getrainde MediaPipe-modellen op
bij Google; de bestanden worden met een vastgelegde SHA-256 gecontroleerd en lokaal
gecachet in `%LOCALAPPDATA%\Echo\models`. Daarna kan herkenning offline werken.
Beelden worden nooit geupload of opgenomen. Alleen tijdelijke herkenningspunten
gaan naar je lokale browser voor de schets. De handscan maakt geen persoonsprofiel.
Na iedere detectiestart moet je opnieuw bewust scannen om gebaaracties te activeren;
de zithouding stel je desgewenst apart opnieuw in.

Met hetzelfde cameranummer delen deze functie en **Aanwezigheid & Beveiliging**
een cameraverbinding. Elke functie heeft haar eigen stopknop; de camera wordt pas
vrijgegeven wanneer beide zijn gestopt. Andere apps zoals Camera Lab of Windows
Hello kunnen nog wel met deze verbinding conflicteren.

Gebruik **Stoppen** om deze bewaking te stoppen; alleen het tabblad sluiten stopt
haar niet. Op het Windows-vergrendelscherm worden acties gepauzeerd en uitgeschakeld.
Na ontgrendelen moet je acties handmatig opnieuw activeren. Camerafouten stoppen
de bewaking met een foutmelding; een mislukte Windows-actie schakelt gebaaracties
uit. Bij twijfel: schakel acties uit en gebruik je gewone bediening.

## Systeemzorg: LAN, logboeken en hardwareprofielen

Open **Systeemzorg / System care** in het dashboard, of
`http://127.0.0.1:5000/systeemzorg` op de pc waarop Echo draait.
Deze functies zijn lokaal, opt-in en uitgeschakeld in demo-/bedrijfsmodus.
Er wordt geen externe AI aangeroepen voor deze analyse.

### Netwerk- en logbewaking gebruiken

1. Vink **LAN-apparaten ontdekken** en/of **Lokale systeemlogboeken analyseren** aan.
2. Kies voor LAN de adapter van je eigen wifi-/kabelnetwerk. Alleen rechtstreeks
   aangesloten private IPv4-subnetten van /24 t/m /30 zijn toegestaan, maximaal
   254 hostadressen. Grotere netwerken worden geweigerd, niet stilzwijgend
   gedeeltelijk gescand. IPv6 wordt niet gescand.
3. Kies intervallen (standaard LAN elke 300 seconden, logs elke 60 seconden) en
   het **Meldingsprofiel**, bijvoorbeeld Security. Dat label wijzigt je actieve
   Echo-profiel niet. Geluid en bureaubladmeldingen zijn afzonderlijk optioneel.
4. Geef toestemming en klik **Bewaking starten**. De eerste controle begint direct.
5. Controleer onbekende apparaten met je routerinventaris. Klik alleen bij
   herkenbare apparaten op **Vertrouwen**; met **Vertrouwen intrekken** maak je
   dit ongedaan. De eerste scan vertrouwt niet automatisch alle apparaten.

LAN-detectie gebruikt beperkte ICMP-probes en de buur-/ARP-tabel, geen poortscan.
Een apparaat krijgt alleen een recente waarneming bij een echo-antwoord of een
bereikbare buurvermelding. De lijst toont **laatst gezien**, geen garantie dat
het apparaat nog verbonden is. Firewalls, slaapstand, wifi-isolatie en ontbrekende
MAC-adressen beperken detectie. Vertrouwen wordt per adapter/subnet en MAC-adres
bewaard, nooit alleen per IP: DHCP kan een adres opnieuw uitdelen. Een MAC-adres
kan veranderen of worden vervalst; dit is geen authenticatie of indringerdetectie.
Onbekende apparaten worden gegroepeerd gemeld, normaal maximaal eenmaal per dag
per identiteit. Er worden geen apparaten automatisch geblokkeerd.

Windows leest System/Application-waarschuwingen, fouten en kritieke gebeurtenissen,
plus Security-events 4625 (mislukte aanmelding), 4740 (accountvergrendeling) en
1102 (auditlog gewist). De eerste lezing kijkt maximaal 15 minuten terug; daarna
wordt per kanaal verdergelezen, in batches van maximaal 200. Een achterstand,
logreset of ontbrekende leesrechten staat zichtbaar bij de dekking. **Access denied**
betekent dat die bron niet is gecontroleerd. Geef zo nodig gerichte leesrechten
via Windows-beheer; Echo verhoogt zijn rechten niet zelf.

Linux ondersteunt bestaande `syslog`, `messages`, `auth.log` en `secure` onder
`/var/log`, met incrementele offsets en rotatie-/truncate-detectie. Per bron wordt
maximaal 64 KiB per ronde gelezen, aanvankelijk de recente staart van het bestand.
Een uitsluitend journald-gebaseerd systeem wordt expliciet als niet ondersteund
gemeld. Regels herkennen onder andere mislukte aanmeldingen, crashes, OOM en fouten;
ze zijn **signalen, geen bewijs van een aanval**. Er worden geen ruwe logregels of
accountvelden opgeslagen of verstuurd, alleen lokale interpretaties/eventmetadata.

Details staan uitsluitend op de lokale Systeemzorg-pagina. Het gewone dashboard
ontvangt alleen een algemene melding met het gekozen profiellabel, zonder
apparaatadressen of logdetails. Er wordt geen cloudspraak gebruikt. Windows-geluid
is begrensd tot eenmaal per 30 seconden; bureaubladmeldingen werken zolang deze
pagina openstaat en je browser toestemming heeft.

### Lokale AI-bestands- en loganalyse (Ollama)

Open **Systeemzorg** via `http://127.0.0.1:5000/systeemzorg`. Bovenaan staat een
aparte **Lokale AI-bestands- en loganalyse**. Deze gebruikt niet de normale
chat, het ingestelde cloudmodel, spraakuitvoer of de gespreksgeschiedenis.
Ook als je gewone chat een online AI gebruikt, gaat deze analyse uitsluitend
naar de vaste lokale Ollama-service op `127.0.0.1:11434`, zonder HTTP-proxy of
redirects en zonder cloudfallback.

1. Installeer/start een vertrouwde lokale Ollama-installatie. Schakel Ollama's
   cloudfuncties uit met `OLLAMA_NO_CLOUD=1` **voor het starten van Ollama**,
   of voeg `"disable_ollama_cloud": true` toe aan je bestaande
   `%USERPROFILE%\.ollama\server.json`. Behoud andere bestaande instellingen.
   Herstart Ollama na deze wijziging; Echo aanpassen is hiervoor niet genoeg.
   Houd Ollama's poort afgeschermd voor andere computers.
2. Download indien nodig zelf een lokaal tekstmodel, bijvoorbeeld
   `ollama pull qwen2.5:3b`. Downloaden vereist internet en opslagruimte;
   de latere analyse kan offline. Echo downloadt niets automatisch.
   Kies een model met minstens een 32K-contextvenster.
3. Klik **Lokale modellen ophalen** en kies een model. Cloudmodellen,
   niet-geïnstalleerde modellen en modellen waarvan lokale verwerking niet
   bevestigd kan worden, worden geweigerd voordat bestandsinhoud wordt verstuurd.
4. Kies **1 tot 5** UTF-8-tekst-/logbestanden, samen hoogstens **64 KiB** en
   **12.000 tekens**. Onder meer `.log`, `.txt`, `.md`, `.py`, `.json` en `.ps1`
   zijn toegestaan. Gebruik een klein relevant logfragment; te veel regels of
   tekens worden expliciet geweigerd in plaats van stilzwijgend afgekapt.
   Selecteer geen wachtwoorden, sleutels of andere geheimen; bestandsnaamfilters
   kunnen niet alle gevoelige inhoud herkennen.
5. Geef toestemming en klik **Lokaal analyseren**. Echo vraagt naar mogelijke
   fouten, crashes, mislukte logins of veiligheidsrisico's. Het resultaat toont
   bronbestand, regelnummer, letterlijk citaat, uitleg en een advies. Echo
   controleert of de aangehaalde regel/citaten echt in jouw selectie staan.
   De AI-uitleg blijft een inschatting, geen bewijs of volledige security-audit.
6. Gebruik **Selectie en rapport wissen** om de gegevens uit de pagina te
   verwijderen. Echo slaat broninhoud en rapport niet op en voegt ze niet aan
   chatgeheugen toe. Gebruik geen browserextensies of externe Ollama-configuratie
   die je invoer doorsturen.

Er wordt niets uitgevoerd, gerepareerd of verwijderd. Er is geen automatische
mapscan, toegang tot Event Viewer of wijziging van de bestaande logbewaking;
exporteer daarvoor zelf een relevant tekstfragment. Modeluitval, een onvolledig
antwoord of verzonnen bronverwijzing levert een foutmelding op, geen verzonnen
succesrapport. Er kan maar één analyse tegelijk draaien. De lokale aanvraag
wacht maximaal drie minuten op Ollama; bij een timeout kan Ollama nog kort
doorrekenen, maar Echo start niet automatisch opnieuw. Een tabblad sluiten
annuleert de aanvraag niet gegarandeerd.

Lokale modellen vragen geen prijs per cloudaanvraag, maar gebruiken wel je eigen
RAM/VRAM, opslag en stroom. Snelheid en kwaliteit hangen van het gekozen model en
je hardware af. Controleer adviezen zelf; geen gevonden fouten betekent niet dat
een bestand of computer veilig is. Ook deze functie is uitsluitend lokaal
beschikbaar, buiten demo- en bedrijfsmodus.

### Gaming / Zwaar werk en RAM

1. Kies onder **Hardwareacties per profiel** bijvoorbeeld **Gaming** of **Zwaar werk**.
2. Selecteer met Ctrl + klik uitsluitend apps die je echt wilt laten stoppen.
   Alle geschikte instanties van het gekozen programmabestand vallen onder de
   toestemming. Sla werk eerst op: Windows-procesbeeindiging is niet hetzelfde
   als een nette afsluiting.
3. Kies eventueel een bestaand Windows-energieplan en **Actieve koeling op
   netstroom verkiezen**. Zonder keuze blijft het energiebeleid ongewijzigd.
4. Klik **Opslaan en voorbeeld**. Controleer namen, paden, PID's, starttijden en
   geheugen. Klik binnen 30 seconden op **Uitvoering bevestigen** en bevestig
   de waarschuwing. Verlopen voorbeelden moet je opnieuw maken.
5. Bekijk de hardwaretaak: `completed`, `partial` of `error`, met resultaten per
   proces. Beschikbaar RAM wordt werkelijk voor/na gemeten; andere apps kunnen
   dat tegelijk veranderen, dus het verschil is geen gegarandeerde winst.

Systeem-/beveiligingsprocessen, browsers (inclusief Echo's venster), Python/Node,
editors, Echo's procesfamilie, andere gebruikers en andere Windows-sessies worden
beschermd. Vlak voor beeindiging worden PID, starttijd, pad, eigenaar en beleid
opnieuw gecontroleerd. Er is geen willekeurige RAM-/cache-cleaner en geen
escalatie naar geforceerd herhaald stoppen.

Optioneel: klik **Activeren bij handmatige profielwissels** en bevestig de
waarschuwing. Gedurende deze Echo-sessie voeren handmatige profielkeuzes met
**Profiel Toepassen** op het lokale dashboard het **opgeslagen** hardwarebeleid
uit zonder nieuw voorbeeld. Externe instellingen en de automatische intentrouter
mogen dat niet. **Profielautomatiek uit** stopt toekomstige automatische jobs;
een al begonnen job wordt niet teruggedraaid. Zonder deze opt-in zijn Gaming en
Zwaar werk alleen stille Echo-profielen en stoppen ze geen apps.

### Automatische CPU/RAM-bescherming

Deze Windows-functie staat standaard uit en vereist nieuwe toestemming na elke
Echo-herstart. Alleen het opgeslagen beleid van je op dat moment actieve
Echo-profiel kan worden gebruikt; de AI kiest niet zelf welke apps mogen stoppen.

1. Open **Systeemzorg** via het dashboard, of ga lokaal naar
   `http://127.0.0.1:5000/systeemzorg`.
2. Selecteer bij **Hardwareacties per profiel** bijvoorbeeld **Gaming** en
   keur met Ctrl + klik uitsluitend achtergrondapps goed waarvan stoppen veilig
   is. Klik **Beleid opslaan**. Een voorbeeld uitvoeren is hiervoor niet nodig.
3. Kies hetzelfde profiel in het Echo-dashboard en klik **Profiel Toepassen**.
   Laat **Activeren bij handmatige profielwissels** uit als je alleen de
   CPU/RAM-bewaking wilt: die oudere optie voert het volledige hardwarebeleid
   direct bij een handmatige profielwissel uit.
4. Kies dit profiel onder **Automatische CPU/RAM-bescherming**. Laat de lokale
   Windows-spraakmelding aan als je een gesproken melding wilt.
5. Sla werk op, vink de sessietoestemming aan, klik **CPU/RAM-bescherming
   inschakelen** en bevestig de waarschuwing.
6. Bekijk CPU/RAM, het tijdstip van de laatste werkelijk gestopte app en de
   resultaten onder **Hardwaretaak**. Met **CPU/RAM-bescherming uitschakelen**
   trek je toekomstige toestemming in. Een tabblad sluiten schakelt niets uit.

Echo meet iedere 5 seconden. De eerste meting is een nulmeting. Alleen na
minimaal 10 seconden aaneengesloten metingen **boven 80% CPU of RAM** wordt een
actie overwogen; precies 80%, korte pieken en onderbroken metingen zijn niet
genoeg. Een CPU-kandidaat moet minimaal 5% van de totale CPU gebruiken; een
RAM-kandidaat minimaal 128 MiB wanneer RAM hoog is. Echo probeert hoogstens
een zwaar goedgekeurd proces per minuut te stoppen, slechts eenmaal per
PID/starttijd-combinatie, zonder geforceerde tweede poging.

Direct voor het stoppen worden identiteit, eigenaar, sessie, opgeslagen beleid
en actieve app opnieuw gecontroleerd. De actieve app, zijn procesfamilie en
andere instanties met hetzelfde programmabestand blijven beschermd, naast de
algemene systeem-/beveiligingsuitsluitingen. Kan Echo de ontgrendelde desktop
of actieve-appidentiteit niet bevestigen, dan stopt het geen app en wordt de
automatiek met een zichtbare fout uitgeschakeld. Een profielwissel of gewijzigd
toestemmingsbeleid schakelt deze sessietoestemming ook uit.

Deze bewaking wijzigt geen energieplan of koelbeleid. Een gesproken melding
volgt alleen na bevestigde procesbeeindiging, uitsluitend via lokale Windows-
spraak, zonder cloudfallback. Ontbreekt een lokale stem, dan start de bewaking
met spraak niet; schakel spraak uit of installeer zelf een Windows-stem. Een
meet-/spraakfout schakelt de bewaking uit met een zichtbare fout. Een proces
dat niet stopt, blijft zichtbaar als `still_running` of `error`; Echo forceert
geen afsluiting en beweert niet dat RAM of CPU gegarandeerd daalt.

**Let op:** stoppen is geen nette applicatie-afsluiting. Onopgeslagen werk kan
verloren gaan; gestopte apps worden niet automatisch heropend.

### Energiebeleid herstellen

**Energie-instellingen herstellen** zet het oorspronkelijk opgeslagen energieplan
en gewijzigde AC-koelinstellingen terug, ook na een Echo-herstart. Herstelgegevens
worden voor een wijziging vastgelegd en pas na gecontroleerd herstel verwijderd.
Bij een deels mislukte energieactie blijven ze beschikbaar. Herstel of Normaal
kiezen heropent geen gestopte apps en herstelt geen verloren werk.

Actieve koeling is Windows-beleid, **geen directe ventilator-RPM-regelaar**.
Firmware bepaalt de echte snelheid. Op de gecontroleerde MSI Thin GF63 staat
actieve koeling op netstroom al aan; opnieuw instellen hoeft niets te veranderen.
Gebruik fabrikantspecifieke software, zoals MSI Center wanneer je model dat
ondersteunt, voor verdere ventilatorregeling. Batterij-koelbeleid wordt niet aangepast.

Voorkeuren, vertrouwde apparaten, policies, logcheckpoints, maximaal 200 meldingen
(de pagina toont de nieuwste 100) en herstelgegevens blijven lokaal in
`%LOCALAPPDATA%\Echo\system-care\state.sqlite3`, of op Linux onder
`~/.local/share/Echo/system-care`. Niet-vertrouwde apparaten vervallen na 30 dagen
zonder waarneming. **Stoppen** stopt de bewaking; een tabblad sluiten niet.
Na een serverherstart staan bewaking en profielautomatiek altijd uit, ook als je
voorkeuren bewaard zijn.

## Vergaderopname & lokale transcriptie (Teams, Zoom, Meet)

Open **Vergaderopname** in het dashboard, of ga naar
`http://127.0.0.1:5000/vergadering`. Alles gebeurt op deze pc: audio en tekst
worden nergens naartoe gestuurd.

1. Vink aan dat alle deelnemers weten dat je opneemt (verplicht; opnemen zonder
   dat anderen het weten kan in strijd zijn met privacyregels zoals de AVG).
2. Kies of je microfoon ook mee moet (standaard aan) en geef eventueel een titel.
3. Klik **Opname starten**. Echo neemt via WASAPI-*loopback* op wat uit je
   speakers/koptelefoon komt (dus de andere deelnemers) en apart je microfoon.
   Een rode stip en timer tonen dat de opname loopt.
4. Klik na de vergadering **Stoppen & opslaan**. Een tabblad sluiten stopt de
   opname niet; na 4 uur stopt hij automatisch.
5. Kies de taal (Nederlands, Engels of automatisch) en klik **Uitschrijven**.
   Whisper (`faster-whisper`) draait lokaal; met een NVIDIA-GPU gaat een uur in
   enkele minuten. Ontbreken CUDA-bibliotheken (zoals `cublas64_12.dll`), dan
   schakelt Echo automatisch over op de CPU (trager, wel correct).
6. Bekijk het resultaat met **Tonen**, of download **.txt** (met tijdstempels)
   of **.srt** (ondertitels). **Verwijderen** wist audio én tekst.

Tips en grenzen:

- **Sprekers scheiden (Jij / Anderen)** schrijft beide sporen apart uit. Gebruik
  dit alleen met een koptelefoon; anders vangt je microfoon ook de speakers op
  en krijg je dubbele zinnen.
- Opnames staan in `%LOCALAPPDATA%\Echo\meetings` (buiten de projectmap, dus
  nooit op GitHub), als 16 kHz mono WAV: ongeveer 115 MB per uur per spoor.
  Er moet minimaal 1 GB vrij zijn om te starten.
- Stiltes waarin Windows geen loopbackaudio levert worden opgevuld, zodat de
  tijdstempels van beide sporen gelijk blijven.
- Model, apparaat en precisie komen uit de Whisper-instellingen van Echo.
- De pagina en API werken alleen via localhost, buiten demo-/bedrijfsmodus, en
  wijzigingen vereisen het lokale paginatoken.

## Webautomatisering & Datalekcheck

Open **Webautomatisering & Datalekcheck** in het dashboard, of
`http://127.0.0.1:5000/webautomatisering` op de pc waarop Echo draait. De pagina
en API werken alleen lokaal, met een sessietoken, en zijn uitgeschakeld in
demo-/bedrijfsmodus. Er wordt geen externe AI gebruikt.

### Voorraad-watcher, winkelwagen, automatisch bestellen en reserveren

1. Vul onder **1. Nieuwe watcher** een naam en de productpagina in.
2. Kies wat Echo doet als het product weer op voorraad is:
   - **Alleen melden**;
   - **In winkelwagen leggen (geen reservering)**;
   - **In winkelwagen + kassa openen - jij betaalt zelf**;
   - **Automatisch bestellen (aparte toestemming)**: daadwerkelijk de laatste
     bestel-/betaalknop uitvoeren;
   - **Automatisch reserveren (aparte toestemming)**: daadwerkelijk de
     reservering bevestigen, zonder dit gelijk te stellen aan een winkelwagen.
3. Kies een interval (60-86400 seconden) en eventueel een **Maximumprijs**. Boven
   die prijs doet Echo niets en noteert dit alleen bij **Activiteit**. Eigen "op voorraad"-
   en "uitverkocht"-zinnen zijn optioneel; Echo kent ook gangbare Nederlandse en
   Engelse teksten, ontkenningen zoals "niet meer op voorraad" en schema.org-data.
4. Geef per element (winkelwagen-knop, voorraadlabel, prijs, afrekenknop) een
   CSS-selector en/of de zichtbare tekst. Voor de kassa kan ook een kassa-/
   winkelwagen-URL. Vink de winkelwagen-toestemming aan voor de modi met een
   winkelwagenactie, en klik **Watcher opslaan**.
5. Vink onder **2. Bewaking en winkelvenster** de toestemming aan en klik
   **Bewaking starten**. Geluid en bureaubladmeldingen zijn optioneel.

Per watcher kun je **Nu controleren (geen actie)** gebruiken om te testen zonder
winkelwagenactie, en **Pauzeren**, **Hervatten**, **Bewerken** of **Verwijderen**.
Een melding komt bij de overgang naar "op voorraad", niet bij elke controle.
Na een automatische winkelwagenactie pauzeert de watcher, zodat niets dubbel in je
mandje komt. Gebruik daarna **Hervatten en opnieuw actie toestaan** als je dat wilt.
Bij een CAPTCHA/botcontrole of 5 fouten op rij pauzeert de watcher ook. Bij
rate-limiting wacht Echo steeds langer, tot maximaal een uur.

**De bestaande winkelwagen-/kassamodi plaatsen nog steeds geen bestelling.**
Definitieve bestel-, betaal- en reserveerknoppen worden daarin geweigerd, ook
bij selectorherstel. Alleen de twee nieuwe expliciet toegestane transactiemodi
kunnen een bindende bestelling/betaling of reservering indienen.
CAPTCHA's en botcontroles worden niet omzeild. Respecteer de
voorwaarden van de winkel; veel winkels staan geautomatiseerde aankopen niet toe.

Winkelwagenacties draaien in een apart, blijvend Echo-browserprofiel. Vul een
**Winkel-URL** in, klik **Winkelvenster openen**, log eenmalig in en sluit het
venster. Echo bewaart die sessie op deze pc. Na een actie blijft het venster open,
zodat je zelf kunt afrekenen.

#### Een echte bestelling of reservering instellen

1. Kies **Automatisch bestellen** of **Automatisch reserveren**. Vul verplicht
   een **totaalbudget** en valuta in. Dit budget geldt zowel voor de waargenomen
   productprijs als voor het definitieve totaal, inclusief verzending, belasting
   en toeslagen. Er wordt maximaal een exemplaar van een product toegestaan.
2. Bereid in **Winkelvenster openen** zelf de winkelaccount, bezorggegevens en
   eventueel opgeslagen betaalwijze voor. Gebruik een lege winkelwagen.
   Echo vult geen kaartgegevens of extra formulieren in en omzeilt geen
   betaalautorisatie. Werkt de winkel niet met een reeds voorbereide laatste
   bevestigingsstap, gebruik dan de handmatige kassamodus.
3. Configureer bij bestellen de winkelwagenknop en kassa-URL/-navigatieknop.
   Bij reserveren wordt direct de productpagina gebruikt, of de opgegeven
   reserverings-URL; er wordt niet eerst iets in de winkelwagen gelegd.
   De uiteindelijke pagina moet dezelfde http(s)-origine als de productpagina
   hebben (schema, host en poort). Externe betaalproviders/3-D Secure moet je
   handmatig afhandelen.
4. Vul bij **Expliciete eenmalige transactie** de exacte CSS-selectors in voor:
   - de laatste bestel-/reserveerknop, met zijn exacte zichtbare tekst;
   - **alle** productnamen/-varianten in het definitieve overzicht, plus de
     exacte gewenste product-/SKU-tekst; de selector moet precies een product
     opleveren, niet alleen het gewenste product uit een grotere winkelwagen;
   - **alle** aantallen in het overzicht, die precies een veld met waarde `1`
     moeten opleveren;
   - het volledige definitieve totaalbedrag, met valuta;
   - een unieke succesbevestiging, met exacte tekst, die pas na succesvol
     bestellen/reserveren zichtbaar wordt (bijvoorbeeld `Bestelling bevestigd`).
5. Geef zowel de workflowtoestemming als de **aparte eenmalige
   transactietoestemming**, klik **Watcher opslaan** en controleer de
   bevestigingsvraag met product, aantal, budget en valuta. Bij bewerken moet
   je opnieuw toestemming geven. Start daarna de bewaking.

Zodra er duidelijke voorraad is, voert Echo de toegestane taak uit, ook wanneer
het artikel bij de eerste controle al op voorraad is. Direct voor de laatste
klik worden product, aantal, definitief totaal, valuta, knoptekst en origine
opnieuw gecontroleerd. De laatste DOM-controle en klik vinden samen plaats,
zodat een tussentijdse wijziging van die gegevens de klik blokkeert.
`EUR`/`GBP` of hun symbolen en `USD`/`US$` worden ondersteund; alleen `$` is
te dubbelzinnig. Een ontbrekend veld, extra product, hoger bedrag, ander
product/aantal, gewijzigde definitieve selector of CAPTCHA blokkeert uitvoering.

Echo meldt **order_confirmed** of **reservation_confirmed** uitsluitend wanneer
de ingestelde bevestiging daarna zichtbaar wordt. Bij een timeout, fout of
onbevestigde inzending is de uitkomst **onbekend**, nooit automatisch geslaagd.
Controleer dan je account/bevestigingsmail in de winkel voordat je iets herhaalt.
De indieningspoging wordt **voor de laatste klik** lokaal vastgelegd en blijft
na een crash, herstart of bewerking behouden. Er volgt geen automatische
herhaling, ook niet bij een nieuwe voorraadmelding. Alleen **Hervatten en
opnieuw actie toestaan**, met de expliciete waarschuwing voor nog een transactie,
kan de blokkering opheffen. Stoppen/pauzeren annuleert nog niet ingediende acties,
maar kan een al verzonden bestelling of reservering niet ongedaan maken.

### Zelfherstellende selectors

Echo onthoudt per element een vingerafdruk: tekst, aria-label, id, test-id,
klassen en omgeving. Werkt een selector niet meer, dan zoekt Echo het beste
nieuwe element. Een selector wordt alleen automatisch vervangen bij een duidelijke
match (score minimaal 0,55 en duidelijk beter dan het op een na beste element).
Bij twijfel past Echo niets aan en klikt niets; bij de watcher zie je dan de beste
kandidaten. Betaal-/bestel-/reserveerknoppen worden nooit als kandidaat gekozen
voor winkelwagennavigatie. De aparte definitieve transactievelden worden bewust
niet automatisch hersteld: bij een wijziging configureer en autoriseer je ze opnieuw. Een
uitverkochte pagina zonder winkelwagenknop leidt niet tot een "reparatie".

Onder **Selectors en herstelgeschiedenis** zie je per element de versies met reden en score.
Met **Terugzetten** maak je een eerdere versie weer actief (als nieuwe versie).
Per element blijven de laatste 25 versies bewaard.

### Datalekcheck (OSINT op je eigen gegevens)

1. Voeg onder **3. Datalekcheck** je e-mailadres, gebruikersnaam of domein toe
   (maximaal 20) en bevestig **Dit is van mij**. Gebruik dit alleen voor gegevens
   die van jou zijn of waarvoor je toestemming hebt.
2. Klik **Controleren** per regel of **Alles controleren**.
3. Optioneel: zet **Automatisch opnieuw controleren als HIBP een nieuw lek
   publiceert** aan (elke 6-168 uur) en klik **Toepassen**. Je krijgt alleen een
   melding bij een nieuw gevonden lek ten opzichte van de vorige controle.

E-mail- en domeinzoekacties vereisen een betaalde
[Have I Been Pwned API-sleutel](https://haveibeenpwned.com/API/Key). Klik
**Controleren en opslaan**: de sleutel wordt eerst bij HIBP gecontroleerd en dan
met Windows DPAPI versleuteld voor jouw Windows-account opgeslagen. Je kunt ook
de omgevingsvariabele `HIBP_API_KEY` zetten; die gaat dan voor. Echo houdt zich
aan de requestlimiet van je abonnement.

- **E-mail**: datalekken en (indien je abonnement dat toestaat) pastes.
- **Domein**: zonder sleutel alleen of de site zelf gelekt is. Voor alle adressen
  op jouw domein moet je het domein eerst verifieren in het
  [HIBP-dashboard](https://haveibeenpwned.com/Dashboard/Redirect/Domains).
- **Gebruikersnaam**: Echo controleert openbaar of de naam bestaat op onder meer
  GitHub, GitLab, Docker Hub, PyPI, Keybase, DEV, Chess.com, Lichess, Reddit en
  Hacker News. Een treffer betekent alleen dat die naam daar bestaat; het is niet
  per se jouw account en zegt niets over een lek.

De **Wachtwoordcheck** gebruikt k-anonimiteit: je browser hasht het wachtwoord
met SHA-1, alleen de eerste 5 tekens van de hash gaan via Echo naar Pwned
Passwords, en de vergelijking gebeurt in je browser. Het wachtwoord bereikt de
Echo-server nooit en het invoerveld wordt daarna leeggemaakt.

Gegevens blijven lokaal in `%LOCALAPPDATA%\Echo\web-automation` (watchers,
selectorgeschiedenis, de laatste 300 gebeurtenissen en het winkelprofiel
`shop-profile`) en `%LOCALAPPDATA%\Echo\osint` (identifiers, resultaten en de
versleutelde sleutel). **Opgeslagen sleutel wissen** verwijdert de sleutel; het
winkelprofiel wis je door Echo te stoppen en de map `shop-profile` te verwijderen.
Na een serverherstart staan de voorraadbewaking en de lekmonitor altijd uit.

## Beveiligde bedrijfsdemo

Gebruik de demo-modus wanneer je Echo op een vertrouwd netwerk aan anderen laat zien. Echo vraagt dan om een toegangscode, beschermt de API met een sessie en schakelt computerbesturing uit. Zonder geldige configuratie blijft de demo gesloten.

Stel de volgende variabelen in voordat je Echo start:

```powershell
$env:ECHO_DEMO_MODE = "true"
$env:ECHO_DEMO_PASSWORD = "kies-een-unieke-code-van-minimaal-12-tekens"
$env:ECHO_SESSION_SECRET = (python -c "import secrets; print(secrets.token_urlsafe(48))")
python server.py
```

Je kunt dezelfde variabelen in het lokale `.env`-bestand zetten. Gebruik een eigen toegangscode en bewaar `.env` buiten Git. In demo-modus luistert Echo, als `ECHO_HOST` niet is ingesteld, alleen op deze computer. Wil je andere apparaten toegang geven, stel dan bewust `ECHO_HOST=0.0.0.0` in en gebruik een HTTPS-proxy met `ECHO_COOKIE_SECURE=true`; stel de demo niet rechtstreeks via onbeveiligde HTTP aan een netwerk bloot. De demo gebruikt één gedeelde sessie en biedt geen gebruikers- of bedrijfsisolatie: gebruik hem niet voor vertrouwelijke bedrijfsgegevens.

## Bedrijfskennis-demo

Echo kan vragen beantwoorden op basis van uitsluitend Markdown- en tekstbestanden in `bedrijfsdocumenten/`. Elk antwoord toont de bestandsnaam en regelnummers van de gevonden fragmenten. Andere projectbestanden worden niet gebruikt voor deze antwoorden. Voeg alleen informatie toe die je voor je demo mag delen; het gevonden fragment wordt naar het ingestelde AI-model gestuurd.

Probeer bijvoorbeeld `vraag bedrijfsdocumenten: wat is het retourbeleid?` of klik op **Vraag de bedrijfsdocumenten** in Echo. Het voorbeeldbestand `bedrijfsdocumenten/voorbeeld-bedrijf.md` bevat fictief retourbeleid. Zet je goedgekeurde bedrijfsdocumenten in deze map om de demonstratie met je eigen toegestane voorbeeldmateriaal te personaliseren. Als Echo geen relevante bron vindt of er geen AI-model beschikbaar is, meldt het dat expliciet in plaats van een antwoord te verzinnen.

Echo toont bij bedrijfskennis-antwoorden bronverwijzingen en vraagt of het antwoord nuttig was. Het kwaliteitsblok telt beantwoorde vragen, vragen zonder bron, modelproblemen en positieve/negatieve beoordelingen; het percentage is het aandeel positieve beoordelingen van alle ontvangen beoordelingen, geen automatische meting van feitelijke juistheid. Alleen aggregaten en tijdelijke, willekeurige feedback-ID's worden lokaal bewaard in `echo_knowledge_metrics.json`. Vraag-, antwoord- en documenttekst wordt niet in dit bestand opgeslagen. De laatste 500 feedback-ID's blijven beschikbaar; oudere onbeoordeelde feedback kan daardoor verlopen. Dit zijn lokale demonstratiemetrieken, geen onafhankelijke kwaliteits- of tijdsbesparingsmeting.

## Gescheiden bedrijfsomgevingen (eerste versie)

Voor een lokale proef met meerdere bedrijven kun je de bedrijfsomgeving inschakelen. Deze modus gebruikt accounts in plaats van één gedeelde toegangscode, heeft geen openbare registratie en beperkt elke bedrijfsaccount tot de eigen documenten, gebruikers en kwaliteitscijfers. Een platformbeheerder maakt bedrijven en de eerste bedrijfsbeheerder aan; bedrijfsbeheerders kunnen alleen medewerkers van hun eigen bedrijf toevoegen en uitschakelen. Medewerkers kunnen vragen stellen en feedback geven, maar geen accounts beheren. Persoonlijke Echo-modus en bedrijfsomgeving zijn bewust gescheiden.

Stel vóór de eerste start lokale geheimen in (gebruik unieke wachtwoorden en commit ze nooit):

```powershell
$env:ECHO_ENTERPRISE_MODE = "true"
$env:ECHO_ENTERPRISE_ADMIN_USERNAME = "platform-admin"
$env:ECHO_ENTERPRISE_ADMIN_PASSWORD = "kies-een-uniek-wachtwoord-van-minimaal-12-tekens"
$env:ECHO_SESSION_SECRET = (python -c "import secrets; print(secrets.token_urlsafe(48))")
python server.py
```

De platformbeheerder wordt bij de eerste start aangemaakt in `enterprise-data/enterprise.sqlite3`; wachtwoorden worden gehasht opgeslagen. De omgeving luistert standaard alleen op localhost. Voor netwerkgebruik is HTTPS vereist: configureer een HTTPS-proxy en stel `ECHO_HOST=127.0.0.1` en `ECHO_COOKIE_SECURE=true` in. Als Echo direct op een netwerkinterface luistert, weigert de enterprise-modus te starten zonder Secure-cookies. Zet goedgekeurde `.md`- en `.txt`-bestanden handmatig in de documentenmap die bij het bedrijf wordt getoond. `ECHO_ENTERPRISE_DATA_DIR` en `ECHO_ENTERPRISE_DATABASE` kunnen worden gebruikt om de dataopslaglocatie te wijzigen. Metrics en SQLite-accountgegevens blijven lokaal onder de data-directory.

Bedrijfsbeheerders beheren documenten via **Bedrijfsdocumenten beheren** in hun beheerpagina: één `.md`- of `.txt`-bestand per upload, UTF-8, maximaal 200 KB per bestand en 100 documenten per bedrijf. Bestaande bestandsnamen worden niet stilzwijgend overschreven; verwijder een oude versie eerst. Leden kunnen de documentlijst zien en ermee vragen stellen, maar niet uploaden of verwijderen. De documentlijst toont alleen naam, bestandsgrootte en wijzigingsdatum.

De beheerpagina bevat ook een activiteitenlogboek met aanmaak van bedrijven/accounts, accountstatuswijzigingen en documentuploads/-verwijderingen. Alleen de bedrijfsbeheerder kan het logboek van het eigen bedrijf bekijken. Het logboek bewaart gebruikersnamen, actie, doel en tijdstip (geen wachtwoorden, vraag-/antwoordtekst of documentinhoud); per bedrijf blijven maximaal 500 activiteiten bewaard.

Bedrijfsbeheerders kunnen het wachtwoord van een medewerker resetten. Echo toont dan één keer een willekeurig tijdelijk wachtwoord; geef dit rechtstreeks door via een vertrouwd kanaal. Bij de volgende login moet de medewerker een nieuw wachtwoord van minimaal 12 tekens kiezen. De reset meldt alle bestaande sessies van die account af en wordt zonder wachtwoordinhoud in het activiteitenlogboek vastgelegd. De resetfunctie verstuurt zelf geen e-mail.

Dit is een eerste lokale multi-bedrijfsproef, geen volledige SaaS-beveiligingscertificering: accountuitnodigingen/e-mailverificatie, back-ups en externe databasehosting zijn nog niet inbegrepen. Publiceer de omgeving niet met echte vertrouwelijke documenten voordat die operationele onderdelen en je HTTPS/proxy-configuratie zijn gecontroleerd.

## Beschikbare commando's

- `open youtube` - Opent YouTube
- `open google` - Opent Google
- `zoek op het weer morgen`, `kan je opzoeken hoe ik ...`, `search for ...` - Zoekt automatisch op Google zonder dat je expliciet "search google" hoeft te typen
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
- `how much battery do I have left`, `hoeveel batterij heb ik nog` - Batterijstatus in natuurlijke taal
- `set brightness to 40`, `zet helderheid op 40 procent`, `maak scherm helderder`, `maak scherm donkerder` - Schermhelderheid bedienen
- `wifi quality`, `is mijn wifi goed genoeg voor upload en download` - Wifi linkkwaliteit + upload/download diagnose
- `remember that my name is Nordin` - Slaat je naam of een feit op in langetermijngeheugen
- `save note buy milk` - Slaat een korte notitie op
- `what do you remember about me` - Laat Echo zijn opgeslagen langetermijngeheugen samenvatten
- `add task buy milk`, `show tasks`, `set timer for 5 minutes`, `remind me in 10 minutes to stretch`, `show agenda` - Planner, timers en herinneringen
- `read this page`, `summarize this page`, `summarize https://example.com` - Leest of vat webpagina's samen
- `fill form with Jan, jan@example.com, hallo`, `submit form` - Vult browserformulieren in via automation-modus
- `switch window`, `next tab`, `copy`, `paste`, `save` - Extra computerbesturing
- `denk mee over mijn planning`, `think with me about this` - Echo denkt actief met je mee in concrete stappen
- `vraag door over mijn project`, `ask follow-up questions about my code` - Echo stelt eerst gerichte vervolgvragen (alleen als jij dat vraagt)

## Instellingen (in HTML)

- 📝 **Naam** - Verander de naam van je AI
- 🔗 **URL's** - Stel YouTube en Google URL in
- 😊 **Emoji's** - Zet emoji's aan/uit
- 🔊 **Spraak** - Text-to-speech aan/uit

## Extra features

- **Website Scanner**
  Open `Website Scanner` in het Website Audit-paneel om pagina's, links, afbeeldingen, CSS,
  formulieren en veilige browserinteracties te controleren. De Echo-startlauncher installeert
  automatisch de benodigde Python-pakketten en Playwright Chromium-browser. Lokale
  ontwikkelsites kun je als `http://localhost:3000` scannen op dezelfde pc als Echo;
  per scan worden maximaal 250 interne pagina's gevolgd.

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

- **Google Gemini via Node bridge**
  Voor veilige Gemini-integratie (zonder API key in de browser) gebruik je de nieuwe Node backend in `gemini-node/`.
  ```powershell
  cd gemini-node
  Copy-Item .env.example .env
  # zet daarna GEMINI_API_KEY in .env
  npm install
  npm run start
  ```
  Standaard draait de bridge op `http://127.0.0.1:8787` met endpoint `POST /api/echo`.
  In de UI is nu `static/gemini-api-client.js` geladen, met de functie:
  ```javascript
  const antwoord = await askEchoWithGemini("Status report");
  ```
  De J.A.R.V.I.S.-stijl System Instruction staat in `gemini-node/src/geminiClient.js`.

- **Lokale computerbesturing via Node (`child_process`)**
  Echo kan nu ook echte Windows-acties uitvoeren via de Node bridge, aangestuurd door Gemini action-planning.

  Belangrijke endpoints:
  - `GET /api/device/capabilities`
  - `POST /api/device/execute`

  Ondersteunde acties (allowlist):
  - `open_app` (`notepad`, `calculator`, `explorer`, `edge`, `chrome`, `settings`)
  - `set_volume` (`up`, `down`, `mute`)
  - `lock_screen` (met bevestigingsflow)

  Voorbeeld directe call vanaf browser of frontend:
  ```javascript
  const result = await sendEchoDeviceCommand("open notepad");
  console.log(result);
  ```

  Voor lock screen is bevestiging nodig; herhaal dan met `confirm`:
  ```javascript
  await sendEchoDeviceCommand("lock screen confirm");
  ```

  De uitvoering gebeurt in:
  - `gemini-node/src/deviceControl.js` (Windows command executie via `child_process.execFile`)
  - `gemini-node/src/geminiClient.js` (Gemini JSON action planner)
  - `gemini-node/src/server.js` (API-routes en veiligheidschecks)

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
