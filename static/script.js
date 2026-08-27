const body = document.body;

const modeToggle = document.getElementById('modeToggle');
const modeToggleText = document.getElementById('modeToggleText');
const languageToggleBtn = document.getElementById('languageToggleBtn');
const languageToggleLabel = document.getElementById('languageToggleLabel');
const coreMicBtn = document.getElementById('coreMicBtn');
const speechBtn = document.getElementById('speechBtn');
const clearLogBtn = document.getElementById('clearLogBtn');
const assistantName = document.getElementById('assistantName');
const voiceStatus = document.getElementById('voiceStatus');
const wakeWordHint = document.getElementById('wakeWordHint');
const wakeGateStatus = document.getElementById('wakeGateStatus');
const commandStatus = document.getElementById('commandStatus');
const threatLevelValue = document.getElementById('threatLevelValue');
const threatLevelContext = document.getElementById('threatLevelContext');
const commandForm = document.getElementById('commandForm');
const commandInput = document.getElementById('commandInput');
const sendBtn = document.getElementById('sendBtn');
const messages = document.getElementById('messages');
const visualizer = document.getElementById('voiceVisualizer');
const visualizerBars = Array.from(visualizer ? visualizer.querySelectorAll('.bar') : []);
const quickButtons = Array.from(document.querySelectorAll('.panel-action'));
const pendingConfirm = document.getElementById('pendingConfirm');
const pendingConfirmText = document.getElementById('pendingConfirmText');
const pendingConfirmKicker = document.getElementById('pendingConfirmKicker');
const pendingConfirmYes = document.getElementById('pendingConfirmYes');
const pendingConfirmNo = document.getElementById('pendingConfirmNo');
const bootKicker = document.getElementById('bootKicker');
const bootTitle = document.getElementById('bootTitle');
const bootLog = document.getElementById('bootLog');
const bootMeta = document.getElementById('bootMeta');
const bootProgressFill = document.getElementById('bootProgressFill');

const appState = {
    bootComplete: false,
    dashboardActive: false,
    listeningWanted: false,
    listeningActive: false,
    speakingActive: false,
    speakingPulseTimer: null,
    visualizerTimer: null,
    recognition: null,
    language: 'nl-NL',
    wakeWord: 'hey echo',
    wakeArmed: false,
    wakeArmTimer: null,
    wakeArmTimeoutMs: 9000,
    aiName: 'Echo',
    voiceOutputEnabled: true,
    browserVoicePreference: '',
    premiumVoiceId: '',
    premiumTtsBaseUrl: '',
    premiumTtsAvailable: false,
    premiumTtsProbeAt: 0,
    voiceList: [],
    speechRequestId: 0,
    activeAudio: null,
    activeAudioUrl: '',
    threatLevel: 'nominal',
    threatResetTimer: null,
    runtimeBuildId: '',
    runtimeVersionPollTimer: null,
    pendingCommands: {
        confirm: 'bevestig wachtende actie',
        cancel: 'annuleer wachtende actie',
    },
};

const RUNTIME_VERSION_POLL_MS = 2200;

const THREAT_LEVELS = {
    nominal: {
        label: 'NOMINAL',
        contextEn: 'VOICE CHANNEL IDLE',
        contextNl: 'STEMKANAAL STANDBY',
    },
    watch: {
        label: 'WATCH',
        contextEn: 'BROWSER ROUTING',
        contextNl: 'BROWSER ROUTING',
    },
    elevated: {
        label: 'ELEVATED',
        contextEn: 'AUTOMATION CONTROL',
        contextNl: 'AUTOMATISERINGSCONTROLE',
    },
    critical: {
        label: 'CRITICAL',
        contextEn: 'SYSTEM CONTROL',
        contextNl: 'SYSTEEMCONTROLE',
    },
};

const UI_STRINGS = {
    nl: {
        mode_voice: 'STEMMODUS',
        mode_open_dashboard: 'OPEN PANEEL',
        mode_aria_voice: 'Schakel naar stemmodus',
        mode_aria_open_dashboard: 'Open dashboard-modus',
        language_toggle_label: 'NL -> EN',
        language_toggle_aria: 'Schakel taal naar Engels',
        language_changed_notice: 'Taal gewijzigd naar Nederlands.',
        wake_gate_armed: 'Wake-gate geactiveerd',
        wake_gate_locked: 'Wake-gate vergrendeld',
        wake_window_expired: 'Wake-venster verlopen. Zeg "{wakeWord}" opnieuw.',
        voice_speaking: 'Echo spreekt',
        voice_wake_confirmed: 'Wake bevestigd - spreek je opdracht',
        voice_listening_for_wake: 'Luistert naar activatiewoord: {wakeWord}',
        voice_standby: 'Stemstand-by - tik op de kern om te luisteren',
        speech_listening_start: 'Start stemluisteren',
        speech_listening_stop: 'Stop stemluisteren',
        pending_waiting_confirmation: 'Echo wacht op bevestiging.',
        pending_confirm_command: 'bevestig wachtende actie',
        pending_cancel_command: 'annuleer wachtende actie',
        command_executing: 'Uitvoeren [{channel}]: {command}',
        command_device_failed: 'Computeropdracht mislukt',
        command_device_confirmation: 'Bevestiging voor computeropdracht vereist',
        command_device_completed: 'Computeropdracht voltooid',
        command_completed_ms: 'Voltooid in {duration} ms',
        command_failed: 'Opdracht mislukt',
        command_connection_error: 'Verbindingsfout',
        wake_acknowledged: 'Wake bevestigd. Wacht op opdracht...',
        wake_confirmed_executing: 'Wake bevestigd. Spraakopdracht wordt uitgevoerd...',
        wake_locked_first: 'Wake-gate vergrendeld. Zeg eerst "{wakeWord}".',
        wake_detected_inline: 'Wake gedetecteerd. Inline-opdracht wordt uitgevoerd...',
        wake_detected_waiting: 'Wake gedetecteerd. Wacht op spraakopdracht...',
        voice_recognition_unavailable_browser: 'Spraakherkenning is niet beschikbaar in deze browser',
        voice_recognition_unavailable: 'Spraakherkenning niet beschikbaar',
        voice_listening_disabled: 'Stemluisteren uitgeschakeld',
        voice_not_supported: 'Stem niet ondersteund',
        voice_listening_active: 'Stemluisteren actief - activatiewoord vereist',
        voice_error_code: 'Spraakfout: {code}',
        microphone_permission_denied: 'Microfoonrechten geweigerd',
        feed_cleared: 'Feed gewist. Echo HUD-kanaal klaar.',
        wake_word_hint: 'Activatiewoord: {wakeWord}',
        command_input_placeholder: 'Typ een opdracht voor {name}',
        send_button: 'Verstuur',
        clear_feed_button: 'Wis feed',
        confirm_button: 'Bevestig',
        cancel_button: 'Annuleer',
        pending_confirm_kicker: 'Veiligheidscontrole',
        boot_kicker: 'ECHO SYSTEEMSTART',
        boot_title: 'ARC-KERN INITIALISEERT',
        boot_step_1: 'Reactor-lattice wordt opgestart...',
        boot_step_2: 'Spraakcapture-array wordt gekalibreerd...',
        boot_step_3: 'Commandobus wordt gekoppeld aan lokale runtime...',
        boot_step_4: 'Holografische oppervlakken worden geactiveerd...',
        boot_step_5: 'Echo-kern online.',
        voice_mode_online: 'Stemmodus online. Tik op de boogkern om te luisteren.',
        boot_running: 'Bootsequentie gestart...',
        core_initializing: 'Echo-kern initialiseren...',
        intro_online: '{name} systemen online. Ik wacht op je opdracht.',
        threat_context_general_command: 'ALGEMENE OPDRACHT',
        threat_context_device_failure: 'COMPUTERBESTURING MISLUKT',
        threat_context_device_confirmation: 'COMPUTERBEVESTIGING',
        threat_context_command_failure: 'OPDRACHT MISLUKT',
        threat_context_pending_confirmation: 'WACHT OP BEVESTIGING',
        threat_context_transport_failure: 'VERBINDINGSFOUT',
        invalid_server_response: 'Ongeldig antwoord van server',
        request_failed: 'Verzoek mislukt',
    },
    en: {
        mode_voice: 'VOICE MODE',
        mode_open_dashboard: 'OPEN DASHBOARD',
        mode_aria_voice: 'Switch to voice mode',
        mode_aria_open_dashboard: 'Open dashboard mode',
        language_toggle_label: 'EN -> NL',
        language_toggle_aria: 'Switch language to Dutch',
        language_changed_notice: 'Language switched to English.',
        wake_gate_armed: 'Wake gate armed',
        wake_gate_locked: 'Wake gate locked',
        wake_window_expired: 'Wake window expired. Say "{wakeWord}" again.',
        voice_speaking: 'Echo speaking',
        voice_wake_confirmed: 'Wake confirmed - speak your command',
        voice_listening_for_wake: 'Listening for wake word: {wakeWord}',
        voice_standby: 'Voice standby - tap core to listen',
        speech_listening_start: 'Start Voice Listening',
        speech_listening_stop: 'Stop Voice Listening',
        pending_waiting_confirmation: 'Echo is waiting for confirmation.',
        pending_confirm_command: 'confirm pending action',
        pending_cancel_command: 'cancel pending action',
        command_executing: 'Executing [{channel}]: {command}',
        command_device_failed: 'Device command failed',
        command_device_confirmation: 'Device confirmation required',
        command_device_completed: 'Device command completed',
        command_completed_ms: 'Completed in {duration} ms',
        command_failed: 'Command failed',
        command_connection_error: 'Connection error',
        wake_acknowledged: 'Wake acknowledged. Awaiting command...',
        wake_confirmed_executing: 'Wake confirmed. Executing voice command...',
        wake_locked_first: 'Wake gate locked. Say "{wakeWord}" first.',
        wake_detected_inline: 'Wake detected. Executing inline command...',
        wake_detected_waiting: 'Wake detected. Awaiting voice command...',
        voice_recognition_unavailable_browser: 'Voice recognition is not available in this browser',
        voice_recognition_unavailable: 'Voice recognition unavailable',
        voice_listening_disabled: 'Voice listening disabled',
        voice_not_supported: 'Voice Not Supported',
        voice_listening_active: 'Voice listening active - wake word required',
        voice_error_code: 'Voice error: {code}',
        microphone_permission_denied: 'Microphone permission denied',
        feed_cleared: 'Feed cleared. Echo HUD channel ready.',
        wake_word_hint: 'Wake word: {wakeWord}',
        command_input_placeholder: 'Type a command for {name}',
        send_button: 'Send',
        clear_feed_button: 'Clear Feed',
        confirm_button: 'Confirm',
        cancel_button: 'Cancel',
        pending_confirm_kicker: 'Safety Check',
        boot_kicker: 'ECHO SYSTEM BOOT',
        boot_title: 'ARC CORE INITIALIZING',
        boot_step_1: 'Powering reactor lattice...',
        boot_step_2: 'Calibrating voice capture array...',
        boot_step_3: 'Binding command bus to local runtime...',
        boot_step_4: 'Activating holographic surfaces...',
        boot_step_5: 'Echo core online.',
        voice_mode_online: 'Voice mode online. Tap the arc core to start listening.',
        boot_running: 'Boot sequence running...',
        core_initializing: 'Initializing Echo core...',
        intro_online: '{name} systems online. Awaiting your command.',
        threat_context_general_command: 'GENERAL COMMAND',
        threat_context_device_failure: 'DEVICE CONTROL FAILURE',
        threat_context_device_confirmation: 'DEVICE CONFIRMATION',
        threat_context_command_failure: 'COMMAND FAILURE',
        threat_context_pending_confirmation: 'PENDING CONFIRMATION',
        threat_context_transport_failure: 'TRANSPORT FAILURE',
        invalid_server_response: 'Invalid response from server',
        request_failed: 'Request failed',
    },
};

const THREAT_KEYWORDS = {
    critical: [
        'shutdown',
        'restart',
        'reboot',
        'close window',
        'kill process',
        'terminate',
        'delete',
        'remove',
        'format drive',
        'lock computer',
        'sleep computer',
        'task manager',
        'powershell',
        'cmd',
    ],
    elevated: [
        'automation',
        'automate',
        'script',
        'macro',
        'click',
        'type ',
        'press ',
        'scroll',
        'drag',
        'workflow',
        'take screenshot',
        'screenshot',
    ],
    watch: [
        'open google',
        'open youtube',
        'open browser',
        'open website',
        'search ',
        'zoek ',
        'website',
        'browser',
        'tab ',
        'edge',
        'chrome',
        'firefox',
    ],
};

const SPEECH_WARNING_HINTS = /(error|failed|failure|danger|critical|waarschuwing|fout|mislukt|blocked|denied|cannot|kan niet)/i;
const SPEECH_CONFIRMATION_HINTS = /(confirm|confirmation|verify|approval|bevestig|bevestiging|veiligheidscontrole|pending)/i;

const PREMIUM_TTS_BASE_URLS = [
    'http://127.0.0.1:8787',
    'http://localhost:8787',
];

const VOICE_QUALITY_HINTS = /google|microsoft|natural|neural|wavenet|enhanced|premium|online/;
const VOICE_NEGATIVE_HINTS = /espeak|festival|robot|compact|sam/;

const SPEECH_PROFILES = {
    status: {
        profile: 'status',
        rate: 0.99,
        pitch: 0.98,
        volume: 1,
        pauseMs: 70,
        maxSegmentLength: 220,
        voiceHints: /(assistant|conversational|calm|neutral|natural|professional|narration)/,
        voiceAvoidHints: /(shout|whisper|character|anime|cartoon)/,
    },
    confirmation: {
        profile: 'confirmation',
        rate: 0.95,
        pitch: 0.93,
        volume: 1,
        pauseMs: 95,
        maxSegmentLength: 190,
        voiceHints: /(clear|assistant|professional|support|guide|calm|confident)/,
        voiceAvoidHints: /(aggressive|angry|child|cartoon)/,
    },
    warning: {
        profile: 'warning',
        rate: 0.9,
        pitch: 0.86,
        volume: 1,
        pauseMs: 110,
        maxSegmentLength: 170,
        voiceHints: /(deep|authority|serious|command|broadcast|male|narration)/,
        voiceAvoidHints: /(soft|child|cartoon|anime|cute)/,
    },
};

function sleep(ms) {
    return new Promise((resolve) => {
        window.setTimeout(resolve, ms);
    });
}

function escapeHtml(text) {
    return String(text || '')
        .replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;')
        .replaceAll('"', '&quot;')
        .replaceAll("'", '&#39;');
}

function normalizeText(text) {
    return String(text || '')
        .toLowerCase()
        .replace(/[^a-z0-9\s]/g, ' ')
        .replace(/\s+/g, ' ')
        .trim();
}

function taalPrefix(taalCode) {
    const raw = String(taalCode || '').toLowerCase();
    const parts = raw.split('-').filter(Boolean);
    return parts.length ? parts[0] : raw;
}

function isNederlandsActief() {
    const prefix = taalPrefix(appState.language || 'nl-NL');
    return prefix === 'nl';
}

function tekstVoorTaal(engels, nederlands) {
    return isNederlandsActief() ? String(nederlands || '') : String(engels || '');
}

function actieveUiTaalCode() {
    return isNederlandsActief() ? 'nl' : 'en';
}

function uiTekst(sleutel, variabelen = {}) {
    const taalCode = actieveUiTaalCode();
    const woordenboek = UI_STRINGS[taalCode] || UI_STRINGS.en;
    let tekst = Object.prototype.hasOwnProperty.call(woordenboek, sleutel)
        ? String(woordenboek[sleutel])
        : String(sleutel || '');

    Object.entries(variabelen).forEach(([naam, waarde]) => {
        tekst = tekst.replaceAll('{' + naam + '}', String(waarde));
    });

    return tekst;
}

function normalizeAppLanguage(taalCode) {
    const raw = String(taalCode || '').trim().toLowerCase();
    if (!raw) {
        return 'nl-NL';
    }

    if (raw.includes('nederlands') || raw.includes('dutch') || raw.startsWith('nl')) {
        return 'nl-NL';
    }

    if (raw.includes('english') || raw.startsWith('en')) {
        return 'en-US';
    }

    return raw;
}

function threatContextForLevel(level) {
    const profile = THREAT_LEVELS[level] || THREAT_LEVELS.nominal;
    return isNederlandsActief() ? profile.contextNl : profile.contextEn;
}

function bepaalSpraakTaalUitInstellingen(settings = {}) {
    const configuredSpeechLang = String(settings.spraak_taal || '').trim();
    if (configuredSpeechLang) {
        return normalizeAppLanguage(configuredSpeechLang);
    }

    const taal = normalizeText(settings.taal || '');
    if (taal.startsWith('nl') || taal.includes('nederlands') || taal.includes('dutch')) {
        return normalizeAppLanguage('nl-NL');
    }

    if (taal.startsWith('en') || taal.includes('english')) {
        return normalizeAppLanguage('en-US');
    }

    return normalizeAppLanguage('nl-NL');
}

function buildPremiumTtsCandidates() {
    const host = String(window.location && window.location.hostname ? window.location.hostname : '').trim();
    const bases = [];

    if (host && host !== '0.0.0.0') {
        bases.push('http://' + host + ':8787');
    }

    PREMIUM_TTS_BASE_URLS.forEach((base) => {
        bases.push(base);
    });

    return Array.from(new Set(bases));
}

async function fetchWithTimeout(url, options = {}, timeoutMs = 5000) {
    const controller = new AbortController();
    const timer = window.setTimeout(() => {
        controller.abort();
    }, timeoutMs);

    try {
        return await fetch(url, {
            ...options,
            signal: controller.signal,
        });
    } finally {
        window.clearTimeout(timer);
    }
}

async function fetchRuntimeVersion() {
    try {
        const response = await fetchWithTimeout('/api/runtime-version', {
            method: 'GET',
            cache: 'no-store',
        }, 1400);

        if (!response.ok) {
            return null;
        }

        const payload = await response.json().catch(() => ({}));
        const buildId = String(payload && payload.build_id ? payload.build_id : '').trim();
        if (!buildId) {
            return null;
        }

        return {
            buildId,
            startedAt: Number(payload && payload.started_at ? payload.started_at : 0) || 0,
        };
    } catch (_error) {
        return null;
    }
}

async function checkRuntimeVersionUpdate() {
    const versionInfo = await fetchRuntimeVersion();
    if (!versionInfo) {
        return;
    }

    if (!appState.runtimeBuildId) {
        appState.runtimeBuildId = versionInfo.buildId;
        return;
    }

    if (versionInfo.buildId !== appState.runtimeBuildId) {
        appState.runtimeBuildId = versionInfo.buildId;
        window.location.reload();
    }
}

function stopRuntimeVersionWatcher() {
    if (!appState.runtimeVersionPollTimer) {
        return;
    }

    window.clearInterval(appState.runtimeVersionPollTimer);
    appState.runtimeVersionPollTimer = null;
}

function startRuntimeVersionWatcher() {
    stopRuntimeVersionWatcher();

    const protocol = String(window.location && window.location.protocol ? window.location.protocol : '').toLowerCase();
    if (protocol !== 'http:' && protocol !== 'https:') {
        return;
    }

    void checkRuntimeVersionUpdate();
    appState.runtimeVersionPollTimer = window.setInterval(() => {
        void checkRuntimeVersionUpdate();
    }, RUNTIME_VERSION_POLL_MS);
}

function cleanupActiveAudio() {
    if (appState.activeAudio) {
        try {
            appState.activeAudio.onended = null;
            appState.activeAudio.onerror = null;
            appState.activeAudio.pause();
        } catch (_error) {
            // Ignore audio cleanup issues.
        }
        appState.activeAudio = null;
    }

    if (appState.activeAudioUrl) {
        try {
            URL.revokeObjectURL(appState.activeAudioUrl);
        } catch (_error) {
            // Ignore URL revoke errors.
        }
        appState.activeAudioUrl = '';
    }
}

function stopActiveSpeechPlayback() {
    cleanupActiveAudio();

    if ('speechSynthesis' in window) {
        try {
            window.speechSynthesis.cancel();
        } catch (_error) {
            // Ignore cancel failures.
        }
    }

    setSpeaking(false);
}

function cleanTextForSpeech(text) {
    return String(text || '')
        .replace(/```[\s\S]*?```/g, ' ')
        .replace(/`([^`]+)`/g, '$1')
        .replace(/\[[^\]]+\]\([^\)]+\)/g, '$1')
        .replace(/https?:\/\/\S+/gi, '')
        .replace(/\s+/g, ' ')
        .trim();
}

function splitTextForSpeech(text, maxLength = 220) {
    const cleaned = cleanTextForSpeech(text);
    if (!cleaned) {
        return [];
    }

    const segments = [];

    function pushChunk(chunk) {
        const value = String(chunk || '').trim();
        if (!value) {
            return;
        }

        if (value.length <= maxLength) {
            segments.push(value);
            return;
        }

        const words = value.split(/\s+/).filter(Boolean);
        let current = '';

        words.forEach((word) => {
            const next = current ? current + ' ' + word : word;
            if (next.length <= maxLength) {
                current = next;
            } else {
                if (current) {
                    segments.push(current);
                }
                current = word;
            }
        });

        if (current) {
            segments.push(current);
        }
    }

    cleaned.split(/(?<=[.!?])\s+/).forEach((sentence) => {
        if (sentence.length <= maxLength) {
            pushChunk(sentence);
            return;
        }

        sentence.split(/(?<=[:;,])\s+/).forEach((part) => {
            pushChunk(part);
        });
    });

    return segments;
}

function normalizeSpeechProfile(profileName) {
    const key = String(profileName || '').trim().toLowerCase();
    if (Object.prototype.hasOwnProperty.call(SPEECH_PROFILES, key)) {
        return key;
    }
    return 'status';
}

function speechProfileForOptions(options = {}) {
    const normalized = normalizeSpeechProfile(options.profile);
    return SPEECH_PROFILES[normalized] || SPEECH_PROFILES.status;
}

function scoreBrowserVoice(voice, profileName = 'status') {
    const preferredVoice = normalizeText(appState.browserVoicePreference);
    const descriptor = normalizeText((voice && voice.name ? voice.name : '') + ' ' + (voice && voice.voiceURI ? voice.voiceURI : ''));
    const doelTaal = String(appState.language || 'en-US').toLowerCase();
    const doelPrefix = taalPrefix(doelTaal);
    const stemTaal = String(voice && voice.lang ? voice.lang : '').toLowerCase();
    const stemPrefix = taalPrefix(stemTaal);
    const speechProfile = SPEECH_PROFILES[normalizeSpeechProfile(profileName)] || SPEECH_PROFILES.status;

    let score = 0;

    if (preferredVoice && descriptor.includes(preferredVoice)) {
        score += 340;
    }

    if (stemTaal === doelTaal) {
        score += 180;
    } else if (stemPrefix && stemPrefix === doelPrefix) {
        score += 120;
    } else if (!stemTaal) {
        score += 10;
    } else {
        score -= 80;
    }

    if (VOICE_QUALITY_HINTS.test(descriptor)) {
        score += 66;
    }

    if (VOICE_NEGATIVE_HINTS.test(descriptor)) {
        score -= 120;
    }

    if (speechProfile.voiceHints && speechProfile.voiceHints.test(descriptor)) {
        score += 62;
    }

    if (speechProfile.voiceAvoidHints && speechProfile.voiceAvoidHints.test(descriptor)) {
        score -= 72;
    }

    if (voice && voice.localService === false) {
        score += 22;
    }

    if (doelPrefix === 'nl' && /(nederlands|dutch)/.test(descriptor)) {
        score += 50;
    }

    if (doelPrefix === 'en' && /(english|british|american|us)/.test(descriptor)) {
        score += 24;
    }

    return score;
}

function pickBestBrowserVoice(voices, profileName = 'status') {
    if (!Array.isArray(voices) || !voices.length) {
        return null;
    }

    const ranked = [...voices].sort((left, right) => scoreBrowserVoice(right, profileName) - scoreBrowserVoice(left, profileName));
    return ranked[0] || null;
}

async function ensureBrowserVoices(timeoutMs = 1800) {
    if (!('speechSynthesis' in window)) {
        return [];
    }

    let voices = window.speechSynthesis.getVoices();
    if (voices.length) {
        appState.voiceList = voices;
        return voices;
    }

    const startedAt = Date.now();
    while (Date.now() - startedAt < timeoutMs) {
        await sleep(120);
        voices = window.speechSynthesis.getVoices();
        if (voices.length) {
            appState.voiceList = voices;
            return voices;
        }
    }

    appState.voiceList = voices;
    return voices;
}

async function probePremiumTtsEndpoint(force = false) {
    const now = Date.now();
    if (!force && appState.premiumTtsProbeAt && (now - appState.premiumTtsProbeAt) < 90000) {
        return appState.premiumTtsAvailable;
    }

    appState.premiumTtsProbeAt = now;
    const candidates = buildPremiumTtsCandidates();

    for (const baseUrl of candidates) {
        try {
            const response = await fetchWithTimeout(baseUrl + '/health', {
                method: 'GET',
                cache: 'no-store',
            }, 1400);

            if (response.ok) {
                appState.premiumTtsBaseUrl = baseUrl;
                appState.premiumTtsAvailable = true;
                return true;
            }
        } catch (_error) {
            // Try next endpoint.
        }
    }

    appState.premiumTtsBaseUrl = '';
    appState.premiumTtsAvailable = false;
    return false;
}

function playAudioBlob(blob, requestId) {
    return new Promise((resolve) => {
        if (!(blob instanceof Blob) || !blob.size) {
            resolve(false);
            return;
        }

        cleanupActiveAudio();

        const objectUrl = URL.createObjectURL(blob);
        const audio = new Audio(objectUrl);
        appState.activeAudio = audio;
        appState.activeAudioUrl = objectUrl;

        const finalize = (ok) => {
            const stillCurrent = requestId === appState.speechRequestId;
            cleanupActiveAudio();
            setSpeaking(false);
            resolve(Boolean(ok && stillCurrent));
        };

        audio.onended = () => {
            finalize(true);
        };

        audio.onerror = () => {
            finalize(false);
        };

        setSpeaking(true);
        audio.play().catch(() => {
            finalize(false);
        });
    });
}

async function speakViaPremiumTts(text, requestId, options = {}) {
    const mayProbeAgain = !appState.premiumTtsAvailable && (Date.now() - appState.premiumTtsProbeAt > 90000);
    if (mayProbeAgain) {
        await probePremiumTtsEndpoint(true);
    }

    if (!appState.premiumTtsAvailable || !appState.premiumTtsBaseUrl) {
        return false;
    }

    const speechProfile = speechProfileForOptions(options);
    const payload = {
        text,
        profile: speechProfile.profile,
        language: appState.language,
    };

    const requestedVoiceId = String(options.voiceId || appState.premiumVoiceId || '').trim();
    if (requestedVoiceId) {
        payload.voiceId = requestedVoiceId;
    }

    try {
        const response = await fetchWithTimeout(appState.premiumTtsBaseUrl + '/api/tts/speak', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload),
        }, 14000);

        if (!response.ok) {
            if (response.status >= 500) {
                appState.premiumTtsAvailable = false;
            }
            return false;
        }

        const blob = await response.blob();
        if (requestId !== appState.speechRequestId) {
            return false;
        }

        return await playAudioBlob(blob, requestId);
    } catch (_error) {
        appState.premiumTtsAvailable = false;
        return false;
    }
}

function prosodyForSegment(segment, index, total, profileName, baseRate, basePitch) {
    let rate = Number(baseRate);
    let pitch = Number(basePitch);
    const speechProfile = SPEECH_PROFILES[normalizeSpeechProfile(profileName)] || SPEECH_PROFILES.status;

    if (!Number.isFinite(rate) || rate <= 0) {
        rate = Number(speechProfile.rate || 1.0);
    }
    if (!Number.isFinite(pitch) || pitch <= 0) {
        pitch = Number(speechProfile.pitch || 1.0);
    }

    if (segment.endsWith('?')) {
        rate -= 0.03;
        pitch += 0.07;
    }

    if (segment.endsWith('!')) {
        rate += 0.04;
        pitch += 0.03;
    }

    if (segment.length > 140) {
        rate -= 0.05;
    }

    if (index === total - 1) {
        rate -= 0.02;
    }

    if (normalizeSpeechProfile(profileName) === 'warning') {
        rate -= 0.02;
    }

    rate = Math.min(1.14, Math.max(0.84, rate));
    pitch = Math.min(1.22, Math.max(0.84, pitch));

    return { rate, pitch };
}

function speakBrowserSegment(utterance) {
    return new Promise((resolve) => {
        utterance.onend = () => {
            resolve(true);
        };

        utterance.onerror = () => {
            resolve(false);
        };

        try {
            window.speechSynthesis.speak(utterance);
        } catch (_error) {
            resolve(false);
        }
    });
}

async function speakViaBrowserTts(text, options, requestId) {
    if (!('speechSynthesis' in window)) {
        return false;
    }

    const speechProfile = speechProfileForOptions(options);
    const segments = splitTextForSpeech(text, speechProfile.maxSegmentLength || 220);
    if (!segments.length) {
        return false;
    }

    const voices = await ensureBrowserVoices();
    const selectedVoice = pickBestBrowserVoice(voices, speechProfile.profile);

    const baseRate = typeof options.rate === 'number' ? options.rate : speechProfile.rate;
    const basePitch = typeof options.pitch === 'number' ? options.pitch : speechProfile.pitch;
    const baseVolume = typeof options.volume === 'number' ? options.volume : speechProfile.volume;

    setSpeaking(true);

    for (let index = 0; index < segments.length; index += 1) {
        if (requestId !== appState.speechRequestId) {
            stopActiveSpeechPlayback();
            return false;
        }

        const segment = segments[index];
        const prosody = prosodyForSegment(segment, index, segments.length, speechProfile.profile, baseRate, basePitch);
        const utterance = new SpeechSynthesisUtterance(segment);

        utterance.lang = appState.language;
        utterance.rate = prosody.rate;
        utterance.pitch = prosody.pitch;
        utterance.volume = Math.max(0.1, Math.min(1, Number(baseVolume) || 1));

        if (selectedVoice) {
            utterance.voice = selectedVoice;
            if (selectedVoice.lang) {
                utterance.lang = selectedVoice.lang;
            }
        }

        const segmentOk = await speakBrowserSegment(utterance);
        if (!segmentOk) {
            setSpeaking(false);
            return false;
        }

        if (index < segments.length - 1) {
            await sleep(speechProfile.pauseMs || 70);
        }
    }

    setSpeaking(false);
    return true;
}

function getWakeWordVariants() {
    const configured = normalizeText(appState.wakeWord);
    const tokens = configured.split(' ').filter(Boolean);
    const primary = tokens.length ? tokens[tokens.length - 1] : 'echo';

    const variants = new Set([
        configured,
        primary,
        'hey ' + primary,
        'ok ' + primary,
        'okay ' + primary,
        'hello ' + primary,
        'hallo ' + primary,
        'hoi ' + primary,
    ]);

    return Array.from(variants)
        .filter(Boolean)
        .sort((left, right) => right.length - left.length);
}

function extractWakeCommand(spokenText) {
    const normalized = normalizeText(spokenText);
    if (!normalized) {
        return {
            wakeDetected: false,
            command: '',
        };
    }

    const wakeVariants = getWakeWordVariants();
    for (const variant of wakeVariants) {
        if (normalized === variant) {
            return {
                wakeDetected: true,
                command: '',
            };
        }

        const prefix = variant + ' ';
        if (normalized.startsWith(prefix)) {
            return {
                wakeDetected: true,
                command: normalized.slice(prefix.length).trim(),
            };
        }
    }

    return {
        wakeDetected: false,
        command: '',
    };
}

function updateWakeGateStatus() {
    if (!wakeGateStatus) {
        return;
    }

    if (appState.wakeArmed) {
        wakeGateStatus.textContent = uiTekst('wake_gate_armed');
        wakeGateStatus.classList.add('is-armed');
        return;
    }

    wakeGateStatus.textContent = uiTekst('wake_gate_locked');
    wakeGateStatus.classList.remove('is-armed');
}

function clearWakeArmTimer() {
    if (!appState.wakeArmTimer) {
        return;
    }

    window.clearTimeout(appState.wakeArmTimer);
    appState.wakeArmTimer = null;
}

function setWakeArmed(active) {
    appState.wakeArmed = Boolean(active);
    clearWakeArmTimer();

    if (appState.wakeArmed) {
        appState.wakeArmTimer = window.setTimeout(() => {
            appState.wakeArmTimer = null;
            appState.wakeArmed = false;
            updateWakeGateStatus();
            updateIdleVoiceStatus();
            setCommandStatus(uiTekst('wake_window_expired', { wakeWord: appState.wakeWord }));
        }, appState.wakeArmTimeoutMs);
    }

    updateWakeGateStatus();
    updateIdleVoiceStatus();
}

function setThreatState(level, context, holdMs = 0) {
    const safeLevel = THREAT_LEVELS[level] ? level : 'nominal';
    const profile = THREAT_LEVELS[safeLevel];

    appState.threatLevel = safeLevel;
    body.dataset.threat = safeLevel;

    if (threatLevelValue) {
        threatLevelValue.textContent = profile.label;
    }

    if (threatLevelContext) {
        threatLevelContext.textContent = String(context || threatContextForLevel(safeLevel)).toUpperCase();
    }

    if (appState.threatResetTimer) {
        window.clearTimeout(appState.threatResetTimer);
        appState.threatResetTimer = null;
    }

    if (holdMs > 0 && safeLevel !== 'nominal') {
        appState.threatResetTimer = window.setTimeout(() => {
            setThreatState('nominal', threatContextForLevel('nominal'), 0);
        }, holdMs);
    }
}

function hasKeywordMatch(input, keywords) {
    return keywords.some((keyword) => input.includes(keyword));
}

function classifyCommandThreat(commandText) {
    const normalized = normalizeText(commandText);

    if (hasKeywordMatch(normalized, THREAT_KEYWORDS.critical)) {
        return {
            level: 'critical',
            context: threatContextForLevel('critical'),
            channel: 'SYSTEM',
        };
    }

    if (hasKeywordMatch(normalized, THREAT_KEYWORDS.elevated)) {
        return {
            level: 'elevated',
            context: threatContextForLevel('elevated'),
            channel: 'AUTOMATION',
        };
    }

    if (hasKeywordMatch(normalized, THREAT_KEYWORDS.watch)) {
        return {
            level: 'watch',
            context: threatContextForLevel('watch'),
            channel: 'BROWSER',
        };
    }

    return {
        level: 'nominal',
        context: uiTekst('threat_context_general_command'),
        channel: 'GENERAL',
    };
}

function profileForThreatLevel(level) {
    const normalized = String(level || '').trim().toLowerCase();
    if (normalized === 'critical') {
        return 'warning';
    }
    if (normalized === 'elevated') {
        return 'confirmation';
    }
    return 'status';
}

function profileForSpeechMessage(message, fallbackProfile = 'status') {
    const text = String(message || '').trim();
    if (!text) {
        return normalizeSpeechProfile(fallbackProfile);
    }

    if (SPEECH_WARNING_HINTS.test(text)) {
        return 'warning';
    }

    if (SPEECH_CONFIRMATION_HINTS.test(text)) {
        return 'confirmation';
    }

    return normalizeSpeechProfile(fallbackProfile);
}

function setMode(active) {
    appState.dashboardActive = Boolean(active);
    body.classList.toggle('dashboard-active', appState.dashboardActive);

    if (!modeToggle) {
        return;
    }

    const label = appState.dashboardActive ? uiTekst('mode_voice') : uiTekst('mode_open_dashboard');
    modeToggle.setAttribute('aria-pressed', appState.dashboardActive ? 'true' : 'false');
    modeToggle.setAttribute('aria-label', appState.dashboardActive ? uiTekst('mode_aria_voice') : uiTekst('mode_aria_open_dashboard'));

    if (modeToggleText) {
        modeToggleText.textContent = label;
    } else {
        modeToggle.textContent = label;
    }
}

function updateLanguageToggleControl() {
    if (!languageToggleBtn) {
        return;
    }

    const label = uiTekst('language_toggle_label');
    languageToggleBtn.setAttribute('aria-label', uiTekst('language_toggle_aria'));

    if (languageToggleLabel) {
        languageToggleLabel.textContent = label;
        return;
    }

    languageToggleBtn.textContent = label;
}

function resetPendingCommandsDefaults() {
    appState.pendingCommands.confirm = uiTekst('pending_confirm_command');
    appState.pendingCommands.cancel = uiTekst('pending_cancel_command');
}

function updateLocalizedUiLabels() {
    document.documentElement.lang = isNederlandsActief() ? 'nl' : 'en';

    updateLanguageToggleControl();

    if (sendBtn) {
        sendBtn.textContent = uiTekst('send_button');
    }

    if (clearLogBtn) {
        clearLogBtn.textContent = uiTekst('clear_feed_button');
    }

    if (speechBtn) {
        speechBtn.textContent = appState.listeningActive
            ? uiTekst('speech_listening_stop')
            : uiTekst('speech_listening_start');
    }

    if (pendingConfirmYes) {
        pendingConfirmYes.textContent = uiTekst('confirm_button');
    }

    if (pendingConfirmNo) {
        pendingConfirmNo.textContent = uiTekst('cancel_button');
    }

    if (pendingConfirmKicker) {
        pendingConfirmKicker.textContent = uiTekst('pending_confirm_kicker');
    }

    if (bootKicker) {
        bootKicker.textContent = uiTekst('boot_kicker');
    }

    if (bootTitle) {
        bootTitle.textContent = uiTekst('boot_title');
    }

    if (wakeWordHint) {
        wakeWordHint.textContent = uiTekst('wake_word_hint', { wakeWord: appState.wakeWord });
    }

    if (commandInput) {
        commandInput.placeholder = uiTekst('command_input_placeholder', { name: appState.aiName });
    }

    if (!pendingConfirm || pendingConfirm.classList.contains('is-hidden')) {
        resetPendingCommandsDefaults();
    }

    setMode(appState.dashboardActive);
    updateWakeGateStatus();
    updateIdleVoiceStatus();
    setThreatState(appState.threatLevel, threatContextForLevel(appState.threatLevel), 0);
}

async function persistLanguageSetting() {
    try {
        await fetch('/api/instellingen', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                taal: isNederlandsActief() ? 'Nederlands' : 'English',
            }),
        });
    } catch (_error) {
        // Keep local language state even when settings save fails.
    }
}

async function setAppLanguage(nextLanguage, options = {}) {
    const normalized = normalizeAppLanguage(nextLanguage);
    const changed = normalized !== appState.language;
    appState.language = normalized;

    if (appState.recognition) {
        appState.recognition.lang = appState.language;
    }

    updateLocalizedUiLabels();

    if (changed && appState.recognition && appState.listeningWanted) {
        stopRecognition();
    }

    if (options.persist) {
        await persistLanguageSetting();
    }

    if (options.announce && changed && appState.bootComplete) {
        const notice = uiTekst('language_changed_notice');
        setCommandStatus(notice);
        const spoken = await speakText(notice, { profile: 'status' });
        if (!spoken) {
            pulseSpeaking(720);
        }
    }
}

async function toggleAppLanguage() {
    const next = isNederlandsActief() ? 'en-US' : 'nl-NL';
    await setAppLanguage(next, {
        persist: true,
        announce: true,
    });
}

function addMessage(kind, text) {
    if (!messages) {
        return;
    }

    const row = document.createElement('div');
    row.classList.add('message');
    if (kind === 'user') {
        row.classList.add('user');
    } else if (kind === 'error') {
        row.classList.add('error');
    } else {
        row.classList.add('ai');
    }

    row.innerHTML = escapeHtml(text);
    messages.appendChild(row);
    messages.scrollTop = messages.scrollHeight;
}

function setCommandStatus(text) {
    if (commandStatus) {
        commandStatus.textContent = text;
    }
}

function setVoiceStatus(text) {
    if (voiceStatus) {
        voiceStatus.textContent = text;
    }
}

function refreshCoreStateClasses() {
    if (!coreMicBtn) {
        return;
    }
    coreMicBtn.classList.toggle('is-listening', appState.listeningActive);
    coreMicBtn.classList.toggle('is-speaking', appState.speakingActive);
}

function updateIdleVoiceStatus() {
    if (appState.speakingActive) {
        setVoiceStatus(uiTekst('voice_speaking'));
        return;
    }

    if (appState.listeningActive) {
        if (appState.wakeArmed) {
            setVoiceStatus(uiTekst('voice_wake_confirmed'));
        } else {
            setVoiceStatus(uiTekst('voice_listening_for_wake', { wakeWord: appState.wakeWord }));
        }
        return;
    }

    setVoiceStatus(uiTekst('voice_standby'));
}

function setSpeaking(active) {
    appState.speakingActive = Boolean(active);
    refreshCoreStateClasses();
    updateIdleVoiceStatus();
}

function pulseSpeaking(durationMs = 1200) {
    setSpeaking(true);

    if (appState.speakingPulseTimer) {
        window.clearTimeout(appState.speakingPulseTimer);
    }

    appState.speakingPulseTimer = window.setTimeout(() => {
        setSpeaking(false);
        appState.speakingPulseTimer = null;
    }, durationMs);
}

function setListening(active) {
    appState.listeningActive = Boolean(active);

    if (!appState.listeningActive && appState.wakeArmed) {
        setWakeArmed(false);
    }

    refreshCoreStateClasses();
    updateIdleVoiceStatus();

    if (speechBtn) {
        speechBtn.textContent = appState.listeningActive
            ? uiTekst('speech_listening_stop')
            : uiTekst('speech_listening_start');
    }
}

async function speakText(text, options = {}) {
    if (!appState.voiceOutputEnabled) {
        return false;
    }

    const clean = cleanTextForSpeech(text);
    if (!clean) {
        return false;
    }

    appState.speechRequestId += 1;
    const requestId = appState.speechRequestId;

    stopActiveSpeechPlayback();

    const premiumSpoken = await speakViaPremiumTts(clean, requestId, options);
    if (premiumSpoken) {
        return true;
    }

    return await speakViaBrowserTts(clean, options, requestId);
}

async function tryHandleLocalDeviceAction(commandText) {
    const bridgeReady = await probePremiumTtsEndpoint(false);
    if (!bridgeReady || !appState.premiumTtsBaseUrl) {
        return {
            handled: false,
        };
    }

    try {
        const response = await fetchWithTimeout(appState.premiumTtsBaseUrl + '/api/device/execute', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                text: commandText,
                language: appState.language,
            }),
        }, 12000);

        if (response.status === 404) {
            return {
                handled: false,
            };
        }

        const payload = await response.json().catch(() => ({}));

        if (!response.ok) {
            return {
                handled: true,
                status: 'error',
                message: String(payload.message || payload.error || tekstVoorTaal('Device control request failed.', 'Computerbesturing is mislukt.')).trim(),
            };
        }

        if (!payload || typeof payload !== 'object') {
            return {
                handled: false,
            };
        }

        return payload;
    } catch (_error) {
        appState.premiumTtsAvailable = false;
        return {
            handled: false,
        };
    }
}

function renderPendingConfirmation(payload) {
    const pending = Boolean(payload && payload.pending);

    if (!pendingConfirm || !pendingConfirmText || !pendingConfirmYes || !pendingConfirmNo) {
        return;
    }

    if (!pending) {
        pendingConfirm.classList.add('is-hidden');
        pendingConfirmText.textContent = '';
        resetPendingCommandsDefaults();
        return;
    }

    const prompt = String(
        payload.prompt
        || (isNederlandsActief() ? payload.prompt_nl : payload.prompt_en)
        || (isNederlandsActief() ? payload.prompt_en : payload.prompt_nl)
        || uiTekst('pending_waiting_confirmation')
    ).trim();
    pendingConfirmText.textContent = prompt;
    pendingConfirm.classList.remove('is-hidden');

    appState.pendingCommands.confirm = String(payload.confirm_command || uiTekst('pending_confirm_command')).trim() || uiTekst('pending_confirm_command');
    appState.pendingCommands.cancel = String(payload.cancel_command || uiTekst('pending_cancel_command')).trim() || uiTekst('pending_cancel_command');
}

async function sendCommand(command, source = 'text') {
    const commandText = String(command || '').trim();
    if (!commandText) {
        return;
    }

    const threatProfile = classifyCommandThreat(commandText);
    setThreatState(threatProfile.level, threatProfile.context, 7000);

    if (source === 'voice') {
        addMessage('user', '[Voice] ' + commandText);
    } else if (source !== 'system') {
        addMessage('user', commandText);
    }

    setCommandStatus(uiTekst('command_executing', {
        channel: threatProfile.channel,
        command: commandText,
    }));

    if (sendBtn) {
        sendBtn.disabled = true;
    }

    try {
        if (source !== 'system') {
            const localDeviceResult = await tryHandleLocalDeviceAction(commandText);
            if (localDeviceResult && localDeviceResult.handled) {
                const deviceStatus = String(localDeviceResult.status || '').trim().toLowerCase();
                const deviceMessage = String(
                    localDeviceResult.message
                    || (localDeviceResult.result && localDeviceResult.result.message)
                    || tekstVoorTaal('Local system action completed.', 'Lokale systeemactie voltooid.')
                ).trim();

                const isError = deviceStatus === 'error';
                const needsConfirmation = deviceStatus === 'confirmation_required';

                if (isError) {
                    addMessage('error', deviceMessage);
                    setCommandStatus(uiTekst('command_device_failed'));
                    setThreatState('critical', uiTekst('threat_context_device_failure'), 10000);
                } else {
                    addMessage('ai', deviceMessage);
                    setCommandStatus(needsConfirmation ? uiTekst('command_device_confirmation') : uiTekst('command_device_completed'));
                    setThreatState(
                        needsConfirmation ? 'elevated' : threatProfile.level,
                        needsConfirmation ? uiTekst('threat_context_device_confirmation') : threatProfile.context,
                        needsConfirmation ? 12000 : 7000
                    );
                }

                renderPendingConfirmation(null);

                const speechProfile = needsConfirmation
                    ? 'confirmation'
                    : (isError ? 'warning' : profileForSpeechMessage(deviceMessage, profileForThreatLevel(threatProfile.level)));

                const spoken = await speakText(deviceMessage, { profile: speechProfile });
                if (!spoken) {
                    pulseSpeaking(isError ? 1500 : 1200);
                }

                return;
            }
        }

        const response = await fetch('/api/commando', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                commando: commandText,
                server_speech: false,
            }),
        });

        const data = await response.json().catch(() => ({
            status: 'error',
            message: uiTekst('invalid_server_response'),
        }));

        const ok = response.ok && data.status === 'success';
        const message = String(data.message || '').trim() || (ok
            ? tekstVoorTaal('Done.', 'Klaar.')
            : tekstVoorTaal('Command failed.', 'Opdracht mislukt.'));
        const hasPendingConfirmation = Boolean(data.pending_confirmation && data.pending_confirmation.pending);
        const pendingPrompt = hasPendingConfirmation
            ? String(
                data.pending_confirmation.prompt
                || (isNederlandsActief() ? data.pending_confirmation.prompt_nl : data.pending_confirmation.prompt_en)
                || (isNederlandsActief() ? data.pending_confirmation.prompt_en : data.pending_confirmation.prompt_nl)
                || uiTekst('pending_waiting_confirmation')
            ).trim()
            : '';

        if (ok) {
            addMessage('ai', message);
            setCommandStatus(uiTekst('command_completed_ms', { duration: String(data.duration_ms || 0) }));

            const spokenText = pendingPrompt || message;
            const preset = pendingPrompt
                ? 'confirmation'
                : profileForSpeechMessage(message, profileForThreatLevel(threatProfile.level));

            const spoken = await speakText(spokenText, { profile: preset });
            if (!spoken) {
                pulseSpeaking();
            }
        } else {
            addMessage('error', message);
            setCommandStatus(uiTekst('command_failed'));
            setThreatState('elevated', uiTekst('threat_context_command_failure'), 9000);

            const spoken = await speakText(message, {
                profile: profileForSpeechMessage(message, 'warning'),
            });
            if (!spoken) {
                pulseSpeaking(1500);
            }
        }

        renderPendingConfirmation(data.pending_confirmation);

        if (hasPendingConfirmation) {
            setThreatState('elevated', uiTekst('threat_context_pending_confirmation'), 12000);
        }
    } catch (error) {
        const message = error instanceof Error ? error.message : uiTekst('request_failed');
        addMessage('error', message);
        setCommandStatus(uiTekst('command_connection_error'));
        setThreatState('critical', uiTekst('threat_context_transport_failure'), 10000);

        const spoken = await speakText(message, { profile: 'warning' });
        if (!spoken) {
            pulseSpeaking(1400);
        }
    } finally {
        if (sendBtn) {
            sendBtn.disabled = false;
        }
    }
}

function processVoiceTranscript(transcript) {
    const spoken = String(transcript || '').trim();
    if (!spoken) {
        return;
    }

    const wakeResult = extractWakeCommand(spoken);

    if (appState.wakeArmed) {
        if (wakeResult.wakeDetected && !wakeResult.command) {
            setWakeArmed(true);
            setCommandStatus(uiTekst('wake_acknowledged'));
            return;
        }

        const armedCommand = wakeResult.wakeDetected && wakeResult.command ? wakeResult.command : spoken;
        setWakeArmed(false);
        setCommandStatus(uiTekst('wake_confirmed_executing'));
        void sendCommand(armedCommand, 'voice');
        return;
    }

    if (!wakeResult.wakeDetected) {
        setCommandStatus(uiTekst('wake_locked_first', { wakeWord: appState.wakeWord }));
        updateIdleVoiceStatus();
        return;
    }

    if (wakeResult.command) {
        setWakeArmed(false);
        setCommandStatus(uiTekst('wake_detected_inline'));
        void sendCommand(wakeResult.command, 'voice');
        return;
    }

    setWakeArmed(true);
    setCommandStatus(uiTekst('wake_detected_waiting'));
    pulseSpeaking(320);
}

function handleRecognitionResult(event) {
    if (!event || !event.results) {
        return;
    }

    for (let index = event.resultIndex; index < event.results.length; index += 1) {
        const result = event.results[index];
        if (result && result.isFinal && result[0] && result[0].transcript) {
            processVoiceTranscript(result[0].transcript);
        }
    }
}

function startRecognition() {
    if (!appState.recognition || !appState.bootComplete) {
        return;
    }

    try {
        appState.recognition.lang = appState.language;
        appState.recognition.start();
    } catch (_error) {
        // Start can fail if called too quickly.
    }
}

function stopRecognition() {
    if (!appState.recognition) {
        return;
    }

    setWakeArmed(false);

    try {
        appState.recognition.stop();
    } catch (_error) {
        // Ignore stop errors.
    }
}

function toggleListening() {
    if (!appState.bootComplete) {
        return;
    }

    if (!appState.recognition) {
        setVoiceStatus(uiTekst('voice_recognition_unavailable_browser'));
        setCommandStatus(uiTekst('voice_recognition_unavailable'));
        return;
    }

    appState.listeningWanted = !appState.listeningWanted;

    if (appState.listeningWanted) {
        startRecognition();
    } else {
        stopRecognition();
        setListening(false);
        setCommandStatus(uiTekst('voice_listening_disabled'));
    }
}

function initRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
        setVoiceStatus(uiTekst('voice_recognition_unavailable'));
        if (speechBtn) {
            speechBtn.disabled = true;
            speechBtn.textContent = uiTekst('voice_not_supported');
        }
        return;
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = false;
    recognition.lang = appState.language;

    recognition.onstart = () => {
        setListening(true);
        setCommandStatus(uiTekst('voice_listening_active'));
    };

    recognition.onresult = handleRecognitionResult;

    recognition.onerror = (event) => {
        const code = event && event.error ? String(event.error) : 'unknown';
        setCommandStatus(uiTekst('voice_error_code', { code }));

        if (code === 'not-allowed' || code === 'service-not-allowed') {
            appState.listeningWanted = false;
            setListening(false);
            setWakeArmed(false);
            setVoiceStatus(uiTekst('microphone_permission_denied'));
        }
    };

    recognition.onend = () => {
        setWakeArmed(false);
        setListening(false);
        if (appState.listeningWanted) {
            window.setTimeout(startRecognition, 280);
        }
    };

    appState.recognition = recognition;
}

function updateVisualizerBars() {
    if (!visualizerBars.length) {
        return;
    }

    const now = Date.now() / 220;
    const base = appState.speakingActive
        ? 0.72
        : (appState.listeningActive ? 0.45 : 0.13);

    visualizerBars.forEach((bar, index) => {
        const harmonic = (Math.sin(now + (index * 0.53)) + 1) * 0.13;
        const noise = Math.random() * (appState.speakingActive ? 0.34 : (appState.listeningActive ? 0.22 : 0.06));
        const level = Math.min(1, Math.max(0.08, base + harmonic + noise));
        bar.style.setProperty('--level', level.toFixed(3));
        bar.style.opacity = appState.speakingActive ? '1' : (appState.listeningActive ? '0.92' : '0.72');
    });
}

function startVisualizer() {
    if (appState.visualizerTimer) {
        return;
    }

    appState.visualizerTimer = window.setInterval(updateVisualizerBars, 90);
}

function clearFeed() {
    if (!messages) {
        return;
    }

    messages.innerHTML = '';
    addMessage('ai', uiTekst('feed_cleared'));
}

async function loadSettings() {
    try {
        const response = await fetch('/api/instellingen', { cache: 'no-store' });
        if (!response.ok) {
            return;
        }

        const settings = await response.json();

        appState.aiName = String(settings.naam || 'Echo');
        appState.voiceOutputEnabled = settings.spraak_uitgang !== false;

        appState.wakeWord = String(settings.wake_word || 'hey echo').trim() || 'hey echo';
        appState.browserVoicePreference = String(settings.browser_stem || '').trim();
        appState.premiumVoiceId = String(settings.premium_tts_voice_id || '').trim();

        if (assistantName) {
            assistantName.textContent = appState.aiName.toUpperCase();
        }

        await setAppLanguage(bepaalSpraakTaalUitInstellingen(settings));

        document.title = appState.aiName;

        void ensureBrowserVoices();
        void probePremiumTtsEndpoint(false);
    } catch (_error) {
        // Keep defaults if settings endpoint is unavailable.
    }
}

function wireEvents() {
    if (modeToggle) {
        modeToggle.addEventListener('click', () => {
            if (!appState.bootComplete) {
                return;
            }
            setMode(!appState.dashboardActive);
        });
    }

    if (coreMicBtn) {
        coreMicBtn.addEventListener('click', () => {
            toggleListening();
        });
    }

    if (speechBtn) {
        speechBtn.addEventListener('click', () => {
            toggleListening();
        });
    }

    if (clearLogBtn) {
        clearLogBtn.addEventListener('click', () => {
            clearFeed();
        });
    }

    if (languageToggleBtn) {
        languageToggleBtn.addEventListener('click', () => {
            void toggleAppLanguage();
        });
    }

    if (commandForm) {
        commandForm.addEventListener('submit', (event) => {
            event.preventDefault();
            const value = commandInput ? commandInput.value : '';
            if (!String(value || '').trim()) {
                return;
            }
            void sendCommand(value, 'text');
            if (commandInput) {
                commandInput.value = '';
                commandInput.focus();
            }
        });
    }

    quickButtons.forEach((button) => {
        button.addEventListener('click', () => {
            const command = String(button.dataset.command || '').trim();
            if (!command) {
                return;
            }
            void sendCommand(command, 'quick');
        });
    });

    if (pendingConfirmYes) {
        pendingConfirmYes.addEventListener('click', () => {
            void sendCommand(appState.pendingCommands.confirm, 'system');
        });
    }

    if (pendingConfirmNo) {
        pendingConfirmNo.addEventListener('click', () => {
            void sendCommand(appState.pendingCommands.cancel, 'system');
        });
    }

    window.addEventListener('keydown', (event) => {
        if (!appState.bootComplete) {
            return;
        }

        if (event.key === 'Escape' && appState.dashboardActive) {
            setMode(false);
        }

        if (event.key.toLowerCase() === 'd' && event.altKey) {
            event.preventDefault();
            setMode(!appState.dashboardActive);
        }

        if (event.key === '/' && appState.dashboardActive) {
            event.preventDefault();
            if (commandInput) {
                commandInput.focus();
            }
        }
    });
}

async function runBootSequence() {
    const steps = [
        uiTekst('boot_step_1'),
        uiTekst('boot_step_2'),
        uiTekst('boot_step_3'),
        uiTekst('boot_step_4'),
        uiTekst('boot_step_5'),
    ];

    for (let index = 0; index < steps.length; index += 1) {
        const progress = Math.round(((index + 1) / steps.length) * 100);

        if (bootLog) {
            bootLog.textContent = steps[index];
        }
        if (bootMeta) {
            bootMeta.textContent = String(progress) + '%';
        }
        if (bootProgressFill) {
            bootProgressFill.style.width = String(progress) + '%';
        }

        await sleep(index === steps.length - 1 ? 460 : 620);
    }

    body.classList.add('boot-complete');
    await sleep(760);
    body.classList.remove('booting');

    appState.bootComplete = true;
    setCommandStatus(uiTekst('voice_mode_online'));
    updateIdleVoiceStatus();

    const intro = uiTekst('intro_online', { name: appState.aiName });
    addMessage('ai', intro);
    const spoken = await speakText(intro, { profile: 'status', rate: 0.98, pitch: 1 });
    if (!spoken) {
        pulseSpeaking(1500);
    }
}

async function init() {
    setMode(false);
    setThreatState('nominal', threatContextForLevel('nominal'), 0);
    setListening(false);
    setWakeArmed(false);
    setSpeaking(false);
    renderPendingConfirmation(null);
    updateLocalizedUiLabels();

    await loadSettings();
    void ensureBrowserVoices();
    void probePremiumTtsEndpoint(false);
    initRecognition();
    wireEvents();
    startVisualizer();
    startRuntimeVersionWatcher();

    setVoiceStatus(uiTekst('boot_running'));
    setCommandStatus(uiTekst('core_initializing'));

    await runBootSequence();
}

window.addEventListener('load', () => {
    void init();
});

window.addEventListener('beforeunload', () => {
    stopRuntimeVersionWatcher();
});
