// DOM-referenties voor HUD, commandokanaal en statuspanelen.
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
const dailySecurityKicker = document.getElementById('dailySecurityKicker');
const dailySecurityState = document.getElementById('dailySecurityState');
const dailySecuritySchedule = document.getElementById('dailySecuritySchedule');
const dailySecurityResult = document.getElementById('dailySecurityResult');
const commandForm = document.getElementById('commandForm');
const commandInput = document.getElementById('commandInput');
const sendBtn = document.getElementById('sendBtn');
const commandSuggestions = document.getElementById('commandSuggestions');
const messages = document.getElementById('messages');
const visualizer = document.getElementById('voiceVisualizer');
const visualizerBars = Array.from(visualizer ? visualizer.querySelectorAll('.bar') : []);
const quickButtons = Array.from(document.querySelectorAll('.panel-action:not(.routine-action)'));
const routineButtons = Array.from(document.querySelectorAll('.routine-action'));
const mobileAccessState = document.getElementById('mobileAccessState');
const mobileAccessHint = document.getElementById('mobileAccessHint');
const mobileAccessLinks = document.getElementById('mobileAccessLinks');
const mobileCopyLinkBtn = document.getElementById('mobileCopyLinkBtn');
const mobileOpenLinkBtn = document.getElementById('mobileOpenLinkBtn');
const mobileScreenshotState = document.getElementById('mobileScreenshotState');
const mobileSaveScreenshotBtn = document.getElementById('mobileSaveScreenshotBtn');
const mobileOpenScreenshotBtn = document.getElementById('mobileOpenScreenshotBtn');
const cameraKicker = document.getElementById('cameraKicker');
const cameraState = document.getElementById('cameraState');
const cameraInsight = document.getElementById('cameraInsight');
const cameraPreview = document.getElementById('cameraPreview');
const cameraPreviewOverlay = document.getElementById('cameraPreviewOverlay');
const cameraStartBtn = document.getElementById('cameraStartBtn');
const cameraStopBtn = document.getElementById('cameraStopBtn');
const cameraScanQrBtn = document.getElementById('cameraScanQrBtn');
const cameraMoodBtn = document.getElementById('cameraMoodBtn');
const cameraMuteBtn = document.getElementById('cameraMuteBtn');
const cameraDeafenBtn = document.getElementById('cameraDeafenBtn');
const streamKicker = document.getElementById('streamKicker');
const streamStatusNote = document.getElementById('streamStatusNote');
const streamModeBtn = document.getElementById('streamModeBtn');
const streamGoLiveBtn = document.getElementById('streamGoLiveBtn');
const streamStopBtn = document.getElementById('streamStopBtn');
const streamRecStartBtn = document.getElementById('streamRecStartBtn');
const streamRecStopBtn = document.getElementById('streamRecStopBtn');
const streamSceneLiveBtn = document.getElementById('streamSceneLiveBtn');
const streamSceneBrbBtn = document.getElementById('streamSceneBrbBtn');
const streamSceneGameBtn = document.getElementById('streamSceneGameBtn');
const streamMarkerBtn = document.getElementById('streamMarkerBtn');
const streamMicBtn = document.getElementById('streamMicBtn');
const streamHelpBtn = document.getElementById('streamHelpBtn');
const overviewKicker = document.getElementById('overviewKicker');
const overviewMicChip = document.getElementById('overviewMicChip');
const overviewVoiceChip = document.getElementById('overviewVoiceChip');
const overviewCameraChip = document.getElementById('overviewCameraChip');
const overviewPendingChip = document.getElementById('overviewPendingChip');
const overviewStreamChip = document.getElementById('overviewStreamChip');
const actionFilterLabel = document.getElementById('actionFilterLabel');
const actionFilterInput = document.getElementById('actionFilterInput');
const actionFilterHint = document.getElementById('actionFilterHint');
const settingsProfilePanel = document.getElementById('settingsProfilePanel');
const settingsProfileKicker = document.getElementById('settingsProfileKicker');
const settingsProfileState = document.getElementById('settingsProfileState');
const settingsProfileSummary = document.getElementById('settingsProfileSummary');
const settingsProfileForm = document.getElementById('settingsProfileForm');
const settingsProfileSelect = document.getElementById('settingsProfileSelect');
const settingsProfileApplyBtn = document.getElementById('settingsProfileApplyBtn');
const settingsProfileLaunchBtn = document.getElementById('settingsProfileLaunchBtn');
const settingsProfileActionsTitle = document.getElementById('settingsProfileActionsTitle');
const settingsProfileEffects = document.getElementById('settingsProfileEffects');
const settingsProfileActions = document.getElementById('settingsProfileActions');
const settingsProfileRouterState = document.getElementById('settingsProfileRouterState');
const settingsProfileRouterForm = document.getElementById('settingsProfileRouterForm');
const settingsProfileRouterEnabledToggle = document.getElementById('settingsProfileRouterEnabledToggle');
const settingsProfileRouterEnabledLabel = document.getElementById('settingsProfileRouterEnabledLabel');
const settingsProfileSuggestThresholdLabel = document.getElementById('settingsProfileSuggestThresholdLabel');
const settingsProfileAutoThresholdLabel = document.getElementById('settingsProfileAutoThresholdLabel');
const settingsProfileSuggestThresholdInput = document.getElementById('settingsProfileSuggestThresholdInput');
const settingsProfileAutoThresholdInput = document.getElementById('settingsProfileAutoThresholdInput');
const settingsProfileRouterSaveBtn = document.getElementById('settingsProfileRouterSaveBtn');
const settingsProfileActionsEditorLabel = document.getElementById('settingsProfileActionsEditorLabel');
const settingsProfileActionsEditor = document.getElementById('settingsProfileActionsEditor');
const settingsProfileActionsSaveBtn = document.getElementById('settingsProfileActionsSaveBtn');
const settingsProfileActionsResetBtn = document.getElementById('settingsProfileActionsResetBtn');
const websiteAuditKicker = document.getElementById('websiteAuditKicker');
const websiteAuditState = document.getElementById('websiteAuditState');
const websiteAuditForm = document.getElementById('websiteAuditForm');
const websiteAuditUrlInput = document.getElementById('websiteAuditUrlInput');
const websiteAuditProfileSelect = document.getElementById('websiteAuditProfileSelect');
const websiteAuditStartBtn = document.getElementById('websiteAuditStartBtn');
const websiteAuditStatusBtn = document.getElementById('websiteAuditStatusBtn');
const websiteAuditReportBtn = document.getElementById('websiteAuditReportBtn');
const websiteAuditDownloadJsonBtn = document.getElementById('websiteAuditDownloadJsonBtn');
const websiteAuditDownloadMdBtn = document.getElementById('websiteAuditDownloadMdBtn');
const websiteAuditDownloadPdfBtn = document.getElementById('websiteAuditDownloadPdfBtn');
const websiteAuditScheduleStatusBtn = document.getElementById('websiteAuditScheduleStatusBtn');
const websiteAuditScore = document.getElementById('websiteAuditScore');
const websiteAuditMeta = document.getElementById('websiteAuditMeta');
const websiteAuditScheduleState = document.getElementById('websiteAuditScheduleState');
const websiteAuditProgressBar = document.getElementById('websiteAuditProgressBar');
const websiteAuditScheduleForm = document.getElementById('websiteAuditScheduleForm');
const websiteAuditScheduleUrlInput = document.getElementById('websiteAuditScheduleUrlInput');
const websiteAuditScheduleProfileSelect = document.getElementById('websiteAuditScheduleProfileSelect');
const websiteAuditFrequencySelect = document.getElementById('websiteAuditFrequencySelect');
const websiteAuditTimeInput = document.getElementById('websiteAuditTimeInput');
const websiteAuditAlertDropInput = document.getElementById('websiteAuditAlertDropInput');
const websiteAuditWebhookInput = document.getElementById('websiteAuditWebhookInput');
const websiteAuditScheduleEnabledToggle = document.getElementById('websiteAuditScheduleEnabledToggle');
const websiteAuditAlertCriticalToggle = document.getElementById('websiteAuditAlertCriticalToggle');
const websiteAuditScheduleSaveBtn = document.getElementById('websiteAuditScheduleSaveBtn');
const websiteAuditFindings = document.getElementById('websiteAuditFindings');
const websiteAuditRecommendations = document.getElementById('websiteAuditRecommendations');
const websiteAuditLogs = document.getElementById('websiteAuditLogs');
const mobileVoiceFileInput = document.getElementById('mobileVoiceFileInput');
const historyCommands = document.getElementById('historyCommands');
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

// Centrale client-state voor spraak, dashboard en runtime watchers.
const appState = {
    bootComplete: false,
    dashboardActive: true,
    listeningWanted: false,
    listeningActive: false,
    speakingActive: false,
    speakingPulseTimer: null,
    visualizerTimer: 0,
    visualizerLastFrameAt: 0,
    voiceInputMode: 'none',
    isSamsungBrowser: false,
    voiceUploadInFlight: false,
    recognition: null,
    language: 'nl-NL',
    wakeWord: 'hey echo',
    wakeArmed: false,
    wakeArmTimer: null,
    wakeArmTimeoutMs: 9000,
    aiName: 'Echo',
    voiceOutputEnabled: true,
    voiceOutputUserEnabled: true,
    micMuted: false,
    deafenEnabled: false,
    browserVoicePreference: '',
    premiumVoiceId: '',
    premiumTtsBaseUrl: '',
    premiumTtsAvailable: false,
    premiumTtsProbeAt: 0,
    voiceList: [],
    speechRequestId: 0,
    voiceTranscriptBuffer: [],
    voiceTranscriptTimer: null,
    lastVoiceTranscriptNormalized: '',
    lastVoiceTranscriptAt: 0,
    lastVoiceCommandDispatchedNormalized: '',
    lastVoiceCommandDispatchedAt: 0,
    voiceCommandInFlight: false,
    recognitionErrorStreak: 0,
    recognitionRestartCount: 0,
    recognitionRestartTimer: null,
    lastAssistantMessageNormalized: '',
    lastAssistantMessageAt: 0,
    activeAudio: null,
    activeAudioUrl: '',
    cameraStream: null,
    cameraPermission: 'unknown',
    cameraBusy: false,
    lastDetectedMood: '',
    streamLive: false,
    streamRecording: false,
    actionFilterQuery: '',
    settingsProfile: 'normal',
    settingsProfileSelected: 'normal',
    settingsProfiles: ['normal', 'streaming', 'security'],
    settingsProfileConfigs: {},
    settingsProfileActionsByProfile: {},
    settingsProfileActionsEditorDirty: false,
    settingsProfileApplying: false,
    settingsProfileLaunching: false,
    settingsProfileRouterEnabled: true,
    settingsProfileRouterSuggestThreshold: 62,
    settingsProfileRouterAutoThreshold: 86,
    settingsProfileRouterSaving: false,
    settingsProfileIntentHint: null,
    settingsProfileHighlightTimer: 0,
    threatLevel: 'nominal',
    threatResetTimer: null,
    runtimeBuildId: '',
    runtimeVersionPollTimer: null,
    dashboardPollTimer: null,
    dashboardRefreshInFlight: false,
    dashboardRefreshQueued: false,
    dashboardLastRefreshAt: 0,
    dashboardRenderRaf: 0,
    dashboardPendingPayload: null,
    dashboardSectionSignatures: {},
    apiBaseUrl: '',
    apiDiscoveryInFlight: null,
    dailySecuritySnapshot: {
        enabled: false,
        scheduled_time: '03:00',
        monitor_running: false,
        supported: true,
    },
    mobileAccessSnapshot: {
        enabled: false,
        network_urls: [],
        primary_network_url: '',
        access_hint_en: '',
        access_hint_nl: '',
    },
    latestScreenshotSnapshot: {
        available: false,
        filename: '',
        download_path: '',
        mobile_primary_download_url: '',
    },
    websiteAuditSnapshot: {
        running: false,
        state: 'idle',
        scan_id: '',
        progress_percent: 0,
        profile: 'standard',
        target_url: '',
        score: 0,
        grade: '',
        exposure_level: '',
        checks_passed: 0,
        checks_warn: 0,
        checks_failed: 0,
        findings_top: [],
        remediation_top: [],
        recent_logs: [],
        last_result: '',
        last_report_json: '',
        last_report_markdown: '',
        last_report_pdf: '',
        pdf_available: false,
    },
    websiteAuditScheduleSnapshot: {
        enabled: false,
        frequency: 'daily',
        scheduled_time: '04:30',
        target_url: '',
        profile: 'standard',
        next_run_at: 0,
        next_run_label: '',
        monitor_running: false,
        alert_score_drop: 12,
        alert_on_critical: true,
        alert_webhook_configured: false,
        last_alert_result: '',
    },
    mobilePrimaryUrl: '',
    commandHistory: [],
    commandHistoryCursor: -1,
    visibleCommandSuggestions: [],
    selectedSuggestionIndex: -1,
    pendingCommands: {
        confirm: 'bevestig wachtende actie',
        cancel: 'annuleer wachtende actie',
    },
};

const RUNTIME_VERSION_POLL_MS = 2200;
const DASHBOARD_POLL_MS = 12000;
const VOICE_DUPLICATE_WINDOW_MS = 2800;
const VOICE_COMMAND_DISPATCH_DUPLICATE_WINDOW_MS = 5200;
const VOICE_TRANSCRIPT_BUFFER_MS = 650;
const ASSISTANT_DUPLICATE_WINDOW_MS = 7000;
const RECOGNITION_RESTART_BASE_DELAY_MS = 280;
const RECOGNITION_MAX_RESTARTS = 6;
const RECOGNITION_FALLBACK_THRESHOLD = 3;
const DASHBOARD_REFRESH_MIN_INTERVAL_MS = 900;
const VISUALIZER_ACTIVE_FRAME_MS = 90;
const VISUALIZER_IDLE_FRAME_MS = 180;
const MAX_FEED_MESSAGES = 120;
const API_DISCOVERY_TIMEOUT_MS = 420;
const ECHO_RUNTIME_PORT_START = 5000;
const ECHO_RUNTIME_PORT_SPAN = 50;
const COMMAND_HISTORY_STORAGE_KEY = 'echo_command_history_v1';
const COMMAND_HISTORY_MAX_ITEMS = 16;
const VOICE_UPLOAD_TIMEOUT_MS = 28000;
const CAMERA_SCAN_ATTEMPTS = 8;
const CAMERA_SCAN_INTERVAL_MS = 260;
const YOUTUBE_SEARCH_BASE_URL = 'https://www.youtube.com/results?search_query=';
const MAX_COMMAND_SUGGESTIONS = 6;
const ACTION_FILTER_BUTTON_SELECTOR = [
    '.panel-action',
    '#cameraStartBtn',
    '#cameraStopBtn',
    '#cameraScanQrBtn',
    '#cameraMoodBtn',
    '#cameraMuteBtn',
    '#cameraDeafenBtn',
    '#mobileCopyLinkBtn',
    '#mobileOpenLinkBtn',
    '#mobileSaveScreenshotBtn',
    '#mobileOpenScreenshotBtn',
].join(', ');
const PANEL_COLLAPSE_STORAGE_KEY = 'echo_panel_collapse_v1';
const STANDAARD_INGEKLAPTE_PANEL_IDS = ['mobileLabPanel', 'cameraLabPanel'];
const LOCAL_SLASH_SUGGESTIONS = [
    '/help',
    '/scanqr',
    '/mood',
    '/golive',
    '/endlive',
    '/record on',
    '/record off',
    '/scene live',
    '/scene brb',
    '/scene game',
    '/marker',
    '/stream on',
    '/stream off',
    '/stream help',
    '/audit status',
    '/audit report',
    '/audit schedule',
    '/mute',
    '/unmute',
    '/deafen',
    '/undeafen',
    '/camera on',
    '/camera off',
    '/clear',
    '/lang',
];

// Threat-profielen sturen visuele state en contextlabels in de UI.
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

const SETTINGS_PROFILE_BASE_CONFIGS = {
    normal: {
        agent_modus: true,
        geheugen_modus: true,
        prioriteit_modus: true,
        computerbesturing_toestaan: false,
        online_ai_modus: true,
        ai_agent_primair: true,
        spraak_ingang: false,
        spraak_uitgang: true,
        spraak_input_provider: 'google',
        spraak_provider: 'local',
        security_scan_daily_enabled: false,
        website_audit_schedule_profile: 'standard',
        stream_auto_focus_obs: true,
    },
    streaming: {
        agent_modus: true,
        geheugen_modus: true,
        prioriteit_modus: false,
        computerbesturing_toestaan: true,
        online_ai_modus: true,
        ai_agent_primair: true,
        spraak_ingang: true,
        spraak_uitgang: false,
        spraak_input_provider: 'whisper',
        spraak_provider: 'local',
        security_scan_daily_enabled: false,
        website_audit_schedule_profile: 'quick',
        stream_auto_focus_obs: true,
    },
    security: {
        agent_modus: true,
        geheugen_modus: true,
        prioriteit_modus: true,
        computerbesturing_toestaan: false,
        online_ai_modus: false,
        ai_agent_primair: false,
        spraak_ingang: false,
        spraak_uitgang: true,
        spraak_input_provider: 'google',
        spraak_provider: 'local',
        security_scan_daily_enabled: true,
        website_audit_schedule_profile: 'security',
        stream_auto_focus_obs: false,
    },
};

const SETTINGS_PROFILE_ACTION_PRESETS = {
    normal: [
        { command: 'system info and show agenda and show tasks', labelKey: 'settings_profile_action_daily_briefing' },
        { command: 'show tasks', labelKey: 'settings_profile_action_task_radar' },
        { command: 'phone status', labelKey: 'settings_profile_action_phone_status' },
        { command: 'take screenshot', labelKey: 'settings_profile_action_take_screenshot' },
    ],
    streaming: [
        { command: 'stream mode on', labelKey: 'settings_profile_action_stream_mode' },
        { command: 'stream start', labelKey: 'settings_profile_action_stream_start' },
        { command: 'stream recording start', labelKey: 'settings_profile_action_stream_record' },
        { command: 'stream help', labelKey: 'settings_profile_action_stream_help' },
    ],
    security: [
        { command: 'website audit status', labelKey: 'settings_profile_action_audit_status' },
        { command: 'website audit report latest', labelKey: 'settings_profile_action_audit_report' },
        { command: 'website audit schedule status', labelKey: 'settings_profile_action_audit_schedule' },
        { command: 'enable automation mode', labelKey: 'settings_profile_action_enable_automation' },
    ],
};

const SETTINGS_PROFILE_LAUNCH_SEQUENCES = {
    normal: ['system info and show agenda and show tasks'],
    streaming: ['stream mode on', 'stream help'],
    security: ['website audit status', 'website audit schedule status'],
};

const SETTINGS_PROFILE_INTENT_RULES = {
    streaming: [
        { pattern: /\bstream\b|\bstreaming\b|\bobs\b|\bgo\s*live\b|\blive\s*stream\b/, score: 38, hint: 'settings_profile_router_hint_stream_core' },
        { pattern: /\bscene\b|\bbrb\b|\bmarker\b|\brecord(?:ing)?\b|\bmic\s*toggle\b/, score: 30, hint: 'settings_profile_router_hint_stream_controls' },
        { pattern: /\btwitch\b|\byoutube\s*live\b|\bchat\s*overlay\b/, score: 24, hint: 'settings_profile_router_hint_stream_platform' },
    ],
    security: [
        { pattern: /\bsecurity\b|\bsecure\b|\bthreat\b|\bmalware\b|\bvirus\b|\bprivacy\b/, score: 38, hint: 'settings_profile_router_hint_security_core' },
        { pattern: /\baudit\b|\bscan\b|\bvulnerab(?:ility|ilities)\b|\bfirewall\b|\bphishing\b/, score: 30, hint: 'settings_profile_router_hint_security_scan' },
        { pattern: /\bwebsite\s*audit\b|\bquick\s*checker\b|\bquick\s*check\b/, score: 28, hint: 'settings_profile_router_hint_security_web' },
    ],
    normal: [
        { pattern: /\bagenda\b|\btasks?\b|\btimer\b|\breminder\b|\bcalendar\b/, score: 20, hint: 'settings_profile_router_hint_normal_planning' },
        { pattern: /\bgoogle\b|\byoutube\b|\bcalculator\b|\bexplorer\b|\bweather\b|\btime\b/, score: 16, hint: 'settings_profile_router_hint_normal_daily' },
        { pattern: /\bnotes?\b|\bmail\b|\bsearch\b|\bsystem\s*info\b|\bphone\s*status\b/, score: 14, hint: 'settings_profile_router_hint_normal_productivity' },
    ],
};

// Tweetalige UI-strings met variabele placeholders.
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
        command_duplicate_ignored: 'Dubbel antwoord genegeerd',
        wake_acknowledged: 'Wake bevestigd. Wacht op opdracht...',
        wake_confirmed_executing: 'Wake bevestigd. Spraakopdracht wordt uitgevoerd...',
        wake_word_required: 'Zeg eerst "{wakeWord}" en daarna je opdracht.',
        wake_locked_first: 'Wake-gate vergrendeld. Zeg eerst "{wakeWord}".',
        wake_detected_inline: 'Wake gedetecteerd. Inline-opdracht wordt uitgevoerd...',
        wake_detected_waiting: 'Wake gedetecteerd. Wacht op spraakopdracht...',
        voice_recognition_unavailable_browser: 'Spraakherkenning is niet beschikbaar in deze browser',
        voice_recognition_unavailable: 'Spraakherkenning niet beschikbaar',
        voice_listening_disabled: 'Stemluisteren uitgeschakeld',
        voice_not_supported: 'Stem niet ondersteund',
        voice_input_quick_capture: 'Snelle spraakopname',
        voice_manual_mobile_hint: 'Samsung-compatibiliteit actief. Gebruik snelle spraakopname of typ je opdracht.',
        voice_upload_processing: 'Spraakopname verwerken...',
        voice_upload_failed: 'Spraakopname kon niet verwerkt worden.',
        voice_upload_empty: 'Geen spraaktekst gevonden in opname.',
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
        dashboard_mode_online: 'Dashboard actief. Typ een opdracht of start stemluisteren.',
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
        request_failed_runtime_hint: 'Geen verbinding met Echo-server. Start Echo opnieuw via Start-Echo-App.bat en probeer opnieuw.',
        daily_security_kicker: 'Dagelijkse Beveiligingsscan',
        daily_security_state_unsupported: 'Dagelijkse scan niet ondersteund op dit systeem',
        daily_security_state_disabled: 'Dagelijkse scan: UIT',
        daily_security_state_enabled: 'Dagelijkse scan: AAN ({monitor})',
        daily_security_monitor_online: 'monitor actief',
        daily_security_monitor_offline: 'monitor uit',
        daily_security_schedule_disabled: 'Schema: uitgeschakeld',
        daily_security_schedule_basic: 'Schema: dagelijks om {time}',
        daily_security_schedule_with_next: 'Schema: dagelijks om {time} | Volgende: {next}',
        daily_security_last_never: 'Laatste: nog niet gestart',
        daily_security_last_success: 'Laatste: gestart op {when}',
        daily_security_last_skipped: 'Laatste: overgeslagen op {when}',
        daily_security_result: 'Resultaat: {result}',
        mobile_access_checking: 'Telefoontoegang controleren...',
        mobile_access_ready: 'Telefoontoegang actief: {url}',
        mobile_access_enabled_no_url: 'Telefoontoegang aan, maar nog geen URL gevonden',
        mobile_access_disabled: 'Telefoontoegang uit (alleen lokaal)',
        mobile_access_no_links: 'Nog geen telefoonlinks beschikbaar.',
        mobile_access_copy_success: 'Telefoonlink gekopieerd naar klembord.',
        mobile_access_copy_missing: 'Geen telefoonlink beschikbaar om te kopieren.',
        mobile_access_copy_failed: 'Kopieren mislukt. Houd de link ingedrukt en kopieer handmatig.',
        mobile_access_open_missing: 'Geen telefoonlink beschikbaar om te openen.',
        mobile_save_screenshot_button: 'Sla laatste screenshot op',
        mobile_open_screenshot_button: 'Open screenshot',
        mobile_screenshot_none: 'Nog geen screenshot beschikbaar.',
        mobile_screenshot_ready: 'Laatste screenshot: {name}',
        mobile_screenshot_save_success: 'Screenshot-download gestart op je telefoon.',
        mobile_screenshot_save_missing: 'Geen screenshot beschikbaar om op te slaan.',
        mobile_screenshot_save_failed: 'Screenshot opslaan op telefoon mislukte.',
        mobile_screenshot_open_missing: 'Geen screenshot beschikbaar om te openen.',
        routine_prefill_ready: 'Concept klaar. Voeg alleen nog je tekst toe.',
        camera_kicker: 'Camera Lab',
        camera_start_button: 'Start Camera',
        camera_stop_button: 'Stop Camera',
        camera_scan_qr_button: 'Scan QR',
        camera_mood_button: 'Mood Check',
        camera_mute_button: 'Mute Mic',
        camera_unmute_button: 'Unmute Mic',
        camera_deafen_button: 'Deafen Echo',
        camera_undeafen_button: 'Undeafen Echo',
        camera_state_off: 'Camera: uit',
        camera_state_requesting: 'Camera: toestemming gevraagd...',
        camera_state_ready: 'Camera: actief',
        camera_state_denied: 'Camera: toestemming geweigerd',
        camera_state_unavailable: 'Camera niet beschikbaar in deze browser',
        camera_insight_idle: 'Nog geen QR of mood scan uitgevoerd.',
        camera_busy: 'Camera bezig...',
        camera_qr_scanning: 'QR-scan bezig...',
        camera_qr_found: 'QR gevonden: {value}',
        camera_qr_not_found: 'Geen QR-code gevonden. Houd de code dichterbij en probeer opnieuw.',
        camera_qr_not_supported: 'QR-scan wordt niet ondersteund in deze browser.',
        camera_qr_open_link_confirm: 'QR-link openen in een nieuw tabblad?\n\n{url}',
        camera_preview_not_ready: 'Nog geen camerabeeld beschikbaar. Probeer opnieuw.',
        camera_mood_scanning: 'Mood check bezig...',
        camera_face_not_found: 'Geen gezicht gevonden. Kijk recht in de camera en probeer opnieuw.',
        camera_mood_manual_prompt: 'Typ je mood: sad, chill of happy',
        camera_mood_manual_cancelled: 'Mood check geannuleerd.',
        camera_talk_check: 'Heb je nu zin om met Echo te praten?',
        camera_talk_later: 'Begrepen, ik blijf op de achtergrond. Roep me als je wilt praten.',
        camera_mood_low: 'Je lijkt wat laag in energie.',
        camera_mood_happy: 'Je lijkt vrolijk.',
        camera_mood_neutral: 'Je lijkt rustig.',
        camera_music_low_open: 'Ik open opbeurende muziek om je mood te liften.',
        camera_music_happy_open: 'Ik open een happy playlist om je vibe vast te houden.',
        camera_music_neutral_open: 'Ik open rustige muziek die bij je tempo past.',
        camera_music_popup_blocked: 'Kon geen nieuw tabblad openen. Schakel pop-ups toe voor deze pagina.',
        camera_mic_muted: 'Microfoon gemute. Echo luistert niet.',
        camera_mic_unmuted: 'Microfoon weer actief. Echo kan weer luisteren.',
        camera_mic_blocked: 'Microfoon staat op mute. Klik Unmute Mic in Camera Lab.',
        camera_deafen_enabled: 'Echo gedeafend. Stem-audio staat uit.',
        camera_deafen_disabled: 'Echo undeafened. Stem-audio staat weer aan.',
        stream_kicker: 'Streaming Deck',
        stream_note: 'One-tap stream controls for OBS.',
        stream_mode_button: 'Stream Mode',
        stream_go_live_button: 'Go Live',
        stream_stop_live_button: 'Stop Live',
        stream_record_start_button: 'Start Recording',
        stream_record_stop_button: 'Stop Recording',
        stream_scene_live_button: 'Scene Live',
        stream_scene_brb_button: 'Scene BRB',
        stream_scene_game_button: 'Scene Game',
        stream_marker_button: 'Drop Marker',
        stream_mic_toggle_button: 'Mic Toggle',
        stream_help_button: 'Stream Help',
        settings_profile_kicker: 'Echo Profielen',
        settings_profile_state_idle: 'Kies een profiel en klik op toepassen.',
        settings_profile_state_current: 'Actief profiel: {profile}',
        settings_profile_state_preview: 'Geselecteerd: {selected} | Actief: {active}. Klik op toepassen om te wisselen.',
        settings_profile_state_launching: 'Profiel wordt gestart: {profile}...',
        settings_profile_applying: 'Profiel wordt toegepast...',
        settings_profile_apply_button: 'Profiel Toepassen',
        settings_profile_launch_button: 'Toepassen + Profiel Starten',
        settings_profile_launching: 'Profielworkflow starten...',
        settings_profile_launch_done: 'Profiel gestart: {profile}.',
        settings_profile_launch_failed: 'Profiel starten mislukt.',
        settings_profile_router_state_idle: 'Auto-router: standby',
        settings_profile_router_state_off: 'Auto-router uit. Echo wisselt geen profiel automatisch.',
        settings_profile_router_state_suggest: 'Router suggestie: {profile} ({confidence}%)',
        settings_profile_router_state_auto: 'Router auto-switch: {profile} ({confidence}%)',
        settings_profile_router_switched: 'Auto-router schakelde over naar {profile} ({confidence}%).',
        settings_profile_router_switch_failed: 'Auto-router kon profiel niet wisselen. Verder met huidig profiel.',
        settings_profile_router_settings_saved: 'Auto-router instellingen opgeslagen.',
        settings_profile_router_settings_failed: 'Auto-router instellingen opslaan mislukt.',
        settings_profile_router_enabled_label: 'Auto-profielrouter',
        settings_profile_router_suggest_label: 'Suggestie %',
        settings_profile_router_auto_label: 'Auto-switch %',
        settings_profile_router_save_button: 'Router Opslaan',
        settings_profile_router_hint_stream_core: 'stream-kernwoorden gedetecteerd',
        settings_profile_router_hint_stream_controls: 'streamcontrols gedetecteerd',
        settings_profile_router_hint_stream_platform: 'streamplatform-signalen gedetecteerd',
        settings_profile_router_hint_security_core: 'security-kernwoorden gedetecteerd',
        settings_profile_router_hint_security_scan: 'scan/audit-signalen gedetecteerd',
        settings_profile_router_hint_security_web: 'website-audit-signalen gedetecteerd',
        settings_profile_router_hint_normal_planning: 'planning-signalen gedetecteerd',
        settings_profile_router_hint_normal_daily: 'dagelijkse taken-signalen gedetecteerd',
        settings_profile_router_hint_normal_productivity: 'productiviteitssignalen gedetecteerd',
        settings_profile_actions_editor_label: 'Aangepaste acties (een commando per regel)',
        settings_profile_actions_editor_placeholder: 'stream mode on\nstream start\nstream help',
        settings_profile_actions_save_button: 'Acties Opslaan',
        settings_profile_actions_reset_button: 'Reset Standaard',
        settings_profile_actions_save_success: 'Profielacties opgeslagen voor {profile}.',
        settings_profile_actions_save_failed: 'Profielacties opslaan mislukt.',
        settings_profile_actions_reset_success: 'Standaard profielacties teruggezet voor {profile}.',
        settings_profile_actions_reset_failed: 'Standaard profielacties resetten mislukt.',
        settings_profile_apply_success: 'Profiel toegepast: {profile}.',
        settings_profile_apply_failed: 'Profiel toepassen mislukt.',
        settings_profile_summary_normal: 'Normaal gebruik: stabiele dagelijkse assistent met balans tussen AI, geheugen en veiligheid.',
        settings_profile_summary_streaming: 'Streaming: snelle live control, steminput aan en OBS focus voor soepele stream-acties.',
        settings_profile_summary_security: 'Security: defensieve modus met dagelijkse security-focus en strengere auditkeuzes.',
        settings_profile_actions_title: 'Profielacties',
        settings_profile_on: 'AAN',
        settings_profile_off: 'UIT',
        settings_profile_provider_local: 'Lokaal',
        settings_profile_provider_cloud: 'Cloud',
        settings_profile_provider_google: 'Google',
        settings_profile_provider_whisper: 'Whisper',
        settings_profile_effect_agent_mode: 'Agent Modus',
        settings_profile_effect_memory_mode: 'Geheugen Modus',
        settings_profile_effect_priority_mode: 'Prioriteit Modus',
        settings_profile_effect_automation: 'Computerbesturing',
        settings_profile_effect_online_ai: 'Online AI',
        settings_profile_effect_voice_input: 'Stem Input',
        settings_profile_effect_voice_output: 'Stem Output',
        settings_profile_effect_stt_provider: 'STT Provider',
        settings_profile_effect_tts_provider: 'TTS Provider',
        settings_profile_effect_security_daily: 'Dagelijkse Security Scan',
        settings_profile_effect_audit_profile: 'Website Audit Profiel',
        settings_profile_effect_obs_focus: 'OBS Auto Focus',
        settings_profile_action_daily_briefing: 'Daily Briefing',
        settings_profile_action_task_radar: 'Task Radar',
        settings_profile_action_phone_status: 'Phone Link Status',
        settings_profile_action_take_screenshot: 'Take Screenshot',
        settings_profile_action_stream_mode: 'Stream Mode On',
        settings_profile_action_stream_start: 'Go Live',
        settings_profile_action_stream_record: 'Start Recording',
        settings_profile_action_stream_help: 'Stream Help',
        settings_profile_action_audit_status: 'Audit Status',
        settings_profile_action_audit_report: 'Laatste Audit Rapport',
        settings_profile_action_audit_schedule: 'Audit Schedule Status',
        settings_profile_action_enable_automation: 'Enable Automation',
        settings_profile_option_normal: 'Normaal Gebruik',
        settings_profile_option_streaming: 'Streaming',
        settings_profile_option_security: 'Security',
        website_audit_kicker: 'Website Audit',
        website_audit_idle: 'Audit stand-by. Voeg een URL toe en start een scan.',
        website_audit_running: 'Audit bezig: {stage} ({progress}%)',
        website_audit_completed: 'Audit klaar voor {target}.',
        website_audit_error: 'Auditfout: {message}',
        website_audit_url_placeholder: 'https://voorbeeld.nl',
        website_audit_start_button: 'Start Audit',
        website_audit_status_button: 'Audit Status',
        website_audit_report_button: 'Laatste Rapport',
        website_audit_download_json_button: 'Download JSON',
        website_audit_download_md_button: 'Download MD',
        website_audit_download_pdf_button: 'Download PDF',
        website_audit_schedule_status_button: 'Schedule Status',
        website_audit_schedule_url_placeholder: 'Scheduler URL (optioneel)',
        website_audit_schedule_webhook_placeholder: 'Alert webhook (optioneel)',
        website_audit_schedule_enabled_label: 'Scheduler aan',
        website_audit_schedule_alert_critical_label: 'Alert kritisch',
        website_audit_schedule_save_button: 'Schema opslaan',
        website_audit_schedule_save_success: 'Website-auditschema opgeslagen.',
        website_audit_schedule_save_failed: 'Website-auditschema opslaan mislukt.',
        website_audit_schedule_state_off: 'Scheduler: uit',
        website_audit_schedule_state_no_target: 'Scheduler aan ({frequency} {time}), maar geen doel-URL ingesteld.',
        website_audit_schedule_state_on: 'Scheduler: {frequency} om {time} | Volgende: {next}',
        website_audit_frequency_daily: 'Dagelijks',
        website_audit_frequency_weekly: 'Wekelijks',
        website_audit_profile_quick: 'Snel',
        website_audit_profile_standard: 'Standaard',
        website_audit_profile_security: 'Beveiliging',
        website_audit_profile_full: 'Volledig',
        website_audit_start_missing_url: 'Voeg eerst een website-URL toe.',
        website_audit_score_line: 'Score: {score}/100 ({grade})',
        website_audit_score_pending: 'Score: --',
        website_audit_meta_line: 'Pass: {pass} | Warn: {warn} | Fail: {fail}',
        website_audit_findings_empty: 'Nog geen bevindingen om te tonen.',
        website_audit_recommendations_empty: 'Nog geen actieplan gevonden.',
        website_audit_logs_empty: 'Nog geen audit-logs beschikbaar.',
        website_audit_download_unavailable: 'Geen auditrapport beschikbaar om te downloaden.',
        website_audit_download_started: 'Download gestart ({format}).',
        overview_kicker: 'Command Center',
        overview_filter_label: 'Filter Acties',
        overview_filter_placeholder: 'Filter: stream, camera, security',
        overview_filter_hint: 'Typ om acties en routines snel te vinden.',
        overview_filter_active: '{visible} zichtbaar, {hidden} verborgen door filter.',
        overview_chip_mic_ready: 'MIC READY',
        overview_chip_mic_muted: 'MIC MUTED',
        overview_chip_mic_listening: 'MIC LISTENING',
        overview_chip_voice_ready: 'VOICE READY',
        overview_chip_voice_deafened: 'VOICE DEAFENED',
        overview_chip_voice_speaking: 'VOICE SPEAKING',
        overview_chip_camera_on: 'CAMERA ON',
        overview_chip_camera_off: 'CAMERA OFF',
        overview_chip_pending_on: 'CONFIRM NEEDED',
        overview_chip_pending_off: 'NO PENDING',
        overview_chip_stream_live: 'STREAM LIVE',
        overview_chip_stream_recording: 'STREAM REC',
        overview_chip_stream_live_recording: 'LIVE + REC',
        overview_chip_stream_idle: 'STREAM STANDBY',
        panel_expand: 'Uitklappen',
        panel_collapse: 'Inklappen',
        voice_status_mic_muted: 'Microfoon staat op mute',
        voice_button_muted: 'Mic Gemute',
        command_suggestions_empty: 'Geen suggesties',
        shortcut_help_text: 'Lokale snelkoppelingen: /help, /scanqr, /mood, /golive, /endlive, /record on, /record off, /scene live, /scene brb, /scene game, /marker, /stream on, /stream off, /stream help, /audit status, /audit report, /audit schedule, /mute, /unmute, /deafen, /undeafen, /camera on, /camera off, /clear, /lang',
        shortcut_unknown: 'Onbekende snelkoppeling. Typ /help voor opties.',
        history_empty: 'Nog geen recente commando\'s.',
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
        command_duplicate_ignored: 'Duplicate reply ignored',
        wake_acknowledged: 'Wake acknowledged. Awaiting command...',
        wake_confirmed_executing: 'Wake confirmed. Executing voice command...',
        wake_word_required: 'Say "{wakeWord}" first, then your command.',
        wake_locked_first: 'Wake gate locked. Say "{wakeWord}" first.',
        wake_detected_inline: 'Wake detected. Executing inline command...',
        wake_detected_waiting: 'Wake detected. Awaiting voice command...',
        voice_recognition_unavailable_browser: 'Voice recognition is not available in this browser',
        voice_recognition_unavailable: 'Voice recognition unavailable',
        voice_listening_disabled: 'Voice listening disabled',
        voice_not_supported: 'Voice Not Supported',
        voice_input_quick_capture: 'Quick voice capture',
        voice_manual_mobile_hint: 'Samsung compatibility mode is active. Use quick voice capture or type your command.',
        voice_upload_processing: 'Processing voice capture...',
        voice_upload_failed: 'Could not process voice capture.',
        voice_upload_empty: 'No speech detected in the recording.',
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
        dashboard_mode_online: 'Dashboard active. Type a command or start voice listening.',
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
        request_failed_runtime_hint: 'Could not reach the Echo server. Restart Echo with Start-Echo-App.bat and try again.',
        daily_security_kicker: 'Daily Security Scan',
        daily_security_state_unsupported: 'Daily scan is not supported on this system',
        daily_security_state_disabled: 'Daily scan: OFF',
        daily_security_state_enabled: 'Daily scan: ON ({monitor})',
        daily_security_monitor_online: 'monitor active',
        daily_security_monitor_offline: 'monitor idle',
        daily_security_schedule_disabled: 'Schedule: disabled',
        daily_security_schedule_basic: 'Schedule: every day at {time}',
        daily_security_schedule_with_next: 'Schedule: every day at {time} | Next: {next}',
        daily_security_last_never: 'Last: not started yet',
        daily_security_last_success: 'Last: started at {when}',
        daily_security_last_skipped: 'Last: skipped at {when}',
        daily_security_result: 'Result: {result}',
        mobile_access_checking: 'Checking phone access...',
        mobile_access_ready: 'Phone access active: {url}',
        mobile_access_enabled_no_url: 'Phone access enabled, but no URL detected yet',
        mobile_access_disabled: 'Phone access disabled (local only)',
        mobile_access_no_links: 'No phone links available yet.',
        mobile_access_copy_success: 'Phone link copied to clipboard.',
        mobile_access_copy_missing: 'No phone link available to copy.',
        mobile_access_copy_failed: 'Copy failed. Long-press the link and copy it manually.',
        mobile_access_open_missing: 'No phone link available to open.',
        mobile_save_screenshot_button: 'Save last screenshot',
        mobile_open_screenshot_button: 'Open screenshot',
        mobile_screenshot_none: 'No screenshot available yet.',
        mobile_screenshot_ready: 'Latest screenshot: {name}',
        mobile_screenshot_save_success: 'Screenshot download started on your phone.',
        mobile_screenshot_save_missing: 'No screenshot available to save.',
        mobile_screenshot_save_failed: 'Could not save screenshot to your phone.',
        mobile_screenshot_open_missing: 'No screenshot available to open.',
        routine_prefill_ready: 'Draft ready. Add your text and send.',
        camera_kicker: 'Camera Lab',
        camera_start_button: 'Start Camera',
        camera_stop_button: 'Stop Camera',
        camera_scan_qr_button: 'Scan QR',
        camera_mood_button: 'Mood Check',
        camera_mute_button: 'Mute Mic',
        camera_unmute_button: 'Unmute Mic',
        camera_deafen_button: 'Deafen Echo',
        camera_undeafen_button: 'Undeafen Echo',
        camera_state_off: 'Camera: off',
        camera_state_requesting: 'Camera: requesting permission...',
        camera_state_ready: 'Camera: active',
        camera_state_denied: 'Camera: permission denied',
        camera_state_unavailable: 'Camera is not available in this browser',
        camera_insight_idle: 'No QR or mood scan yet.',
        camera_busy: 'Camera busy...',
        camera_qr_scanning: 'Scanning QR code...',
        camera_qr_found: 'QR found: {value}',
        camera_qr_not_found: 'No QR code detected. Move closer and try again.',
        camera_qr_not_supported: 'QR scanning is not supported in this browser.',
        camera_qr_open_link_confirm: 'Open this QR link in a new tab?\n\n{url}',
        camera_preview_not_ready: 'No camera frame available yet. Try again.',
        camera_mood_scanning: 'Running mood check...',
        camera_face_not_found: 'No face detected. Look at the camera and try again.',
        camera_mood_manual_prompt: 'Type your mood: sad, chill, or happy',
        camera_mood_manual_cancelled: 'Mood check canceled.',
        camera_talk_check: 'Do you feel like talking with Echo right now?',
        camera_talk_later: 'Understood. I will stay in the background until you call me.',
        camera_mood_low: 'You look a bit low-energy.',
        camera_mood_happy: 'You look cheerful.',
        camera_mood_neutral: 'You look calm.',
        camera_music_low_open: 'Opening uplifting music to raise your mood.',
        camera_music_happy_open: 'Opening a happy playlist to keep your vibe going.',
        camera_music_neutral_open: 'Opening calm music that matches your pace.',
        camera_music_popup_blocked: 'Could not open a new tab. Allow pop-ups for this page.',
        camera_mic_muted: 'Microphone muted. Echo is not listening.',
        camera_mic_unmuted: 'Microphone unmuted. Echo can listen again.',
        camera_mic_blocked: 'Microphone is muted. Click Unmute Mic in Camera Lab.',
        camera_deafen_enabled: 'Echo deafened. Voice audio is off.',
        camera_deafen_disabled: 'Echo undeafened. Voice audio is on again.',
        stream_kicker: 'Streaming Deck',
        stream_note: 'One-tap stream controls for OBS.',
        stream_mode_button: 'Stream Mode',
        stream_go_live_button: 'Go Live',
        stream_stop_live_button: 'Stop Live',
        stream_record_start_button: 'Start Recording',
        stream_record_stop_button: 'Stop Recording',
        stream_scene_live_button: 'Scene Live',
        stream_scene_brb_button: 'Scene BRB',
        stream_scene_game_button: 'Scene Game',
        stream_marker_button: 'Drop Marker',
        stream_mic_toggle_button: 'Mic Toggle',
        stream_help_button: 'Stream Help',
        settings_profile_kicker: 'Echo Profiles',
        settings_profile_state_idle: 'Choose a profile and click apply.',
        settings_profile_state_current: 'Active profile: {profile}',
        settings_profile_state_preview: 'Selected: {selected} | Active: {active}. Click apply to switch.',
        settings_profile_state_launching: 'Starting profile: {profile}...',
        settings_profile_applying: 'Applying profile...',
        settings_profile_apply_button: 'Apply Profile',
        settings_profile_launch_button: 'Apply + Start Profile',
        settings_profile_launching: 'Starting profile workflow...',
        settings_profile_launch_done: 'Profile started: {profile}.',
        settings_profile_launch_failed: 'Could not start profile workflow.',
        settings_profile_router_state_idle: 'Auto-router: standby',
        settings_profile_router_state_off: 'Auto-router is off. Echo will not switch profiles automatically.',
        settings_profile_router_state_suggest: 'Router suggestion: {profile} ({confidence}%)',
        settings_profile_router_state_auto: 'Router auto-switch: {profile} ({confidence}%)',
        settings_profile_router_switched: 'Auto-router switched to {profile} ({confidence}%).',
        settings_profile_router_switch_failed: 'Auto-router could not switch profile. Continuing with current profile.',
        settings_profile_router_settings_saved: 'Auto-router settings saved.',
        settings_profile_router_settings_failed: 'Could not save auto-router settings.',
        settings_profile_router_enabled_label: 'Auto profile router',
        settings_profile_router_suggest_label: 'Suggest %',
        settings_profile_router_auto_label: 'Auto-switch %',
        settings_profile_router_save_button: 'Save Router',
        settings_profile_router_hint_stream_core: 'streaming keywords detected',
        settings_profile_router_hint_stream_controls: 'stream controls detected',
        settings_profile_router_hint_stream_platform: 'stream platform cues detected',
        settings_profile_router_hint_security_core: 'security keywords detected',
        settings_profile_router_hint_security_scan: 'scan/audit signals detected',
        settings_profile_router_hint_security_web: 'website audit signals detected',
        settings_profile_router_hint_normal_planning: 'planning signals detected',
        settings_profile_router_hint_normal_daily: 'daily-task signals detected',
        settings_profile_router_hint_normal_productivity: 'productivity signals detected',
        settings_profile_actions_editor_label: 'Custom actions (one command per line)',
        settings_profile_actions_editor_placeholder: 'stream mode on\nstream start\nstream help',
        settings_profile_actions_save_button: 'Save Actions',
        settings_profile_actions_reset_button: 'Reset Defaults',
        settings_profile_actions_save_success: 'Saved profile actions for {profile}.',
        settings_profile_actions_save_failed: 'Could not save profile actions.',
        settings_profile_actions_reset_success: 'Reset default actions for {profile}.',
        settings_profile_actions_reset_failed: 'Could not reset default profile actions.',
        settings_profile_apply_success: 'Profile applied: {profile}.',
        settings_profile_apply_failed: 'Could not apply profile.',
        settings_profile_summary_normal: 'Normal use: balanced daily assistant profile for AI, memory, and safe control.',
        settings_profile_summary_streaming: 'Streaming: fast live controls, voice input enabled, and OBS-first flow.',
        settings_profile_summary_security: 'Security: defensive mode with daily security focus and stricter audit defaults.',
        settings_profile_actions_title: 'Profile actions',
        settings_profile_on: 'ON',
        settings_profile_off: 'OFF',
        settings_profile_provider_local: 'Local',
        settings_profile_provider_cloud: 'Cloud',
        settings_profile_provider_google: 'Google',
        settings_profile_provider_whisper: 'Whisper',
        settings_profile_effect_agent_mode: 'Agent Mode',
        settings_profile_effect_memory_mode: 'Memory Mode',
        settings_profile_effect_priority_mode: 'Priority Mode',
        settings_profile_effect_automation: 'Computer Control',
        settings_profile_effect_online_ai: 'Online AI',
        settings_profile_effect_voice_input: 'Voice Input',
        settings_profile_effect_voice_output: 'Voice Output',
        settings_profile_effect_stt_provider: 'STT Provider',
        settings_profile_effect_tts_provider: 'TTS Provider',
        settings_profile_effect_security_daily: 'Daily Security Scan',
        settings_profile_effect_audit_profile: 'Website Audit Profile',
        settings_profile_effect_obs_focus: 'OBS Auto Focus',
        settings_profile_action_daily_briefing: 'Daily Briefing',
        settings_profile_action_task_radar: 'Task Radar',
        settings_profile_action_phone_status: 'Phone Link Status',
        settings_profile_action_take_screenshot: 'Take Screenshot',
        settings_profile_action_stream_mode: 'Stream Mode On',
        settings_profile_action_stream_start: 'Go Live',
        settings_profile_action_stream_record: 'Start Recording',
        settings_profile_action_stream_help: 'Stream Help',
        settings_profile_action_audit_status: 'Audit Status',
        settings_profile_action_audit_report: 'Latest Audit Report',
        settings_profile_action_audit_schedule: 'Audit Schedule Status',
        settings_profile_action_enable_automation: 'Enable Automation',
        settings_profile_option_normal: 'Normal Use',
        settings_profile_option_streaming: 'Streaming',
        settings_profile_option_security: 'Security',
        website_audit_kicker: 'Website Audit',
        website_audit_idle: 'Audit idle. Add a URL and start a scan.',
        website_audit_running: 'Audit running: {stage} ({progress}%)',
        website_audit_completed: 'Audit completed for {target}.',
        website_audit_error: 'Audit error: {message}',
        website_audit_url_placeholder: 'https://example.com',
        website_audit_start_button: 'Start Audit',
        website_audit_status_button: 'Audit Status',
        website_audit_report_button: 'Latest Report',
        website_audit_download_json_button: 'Download JSON',
        website_audit_download_md_button: 'Download MD',
        website_audit_download_pdf_button: 'Download PDF',
        website_audit_schedule_status_button: 'Schedule Status',
        website_audit_schedule_url_placeholder: 'Scheduler URL (optional)',
        website_audit_schedule_webhook_placeholder: 'Alert webhook (optional)',
        website_audit_schedule_enabled_label: 'Scheduler On',
        website_audit_schedule_alert_critical_label: 'Alert Critical',
        website_audit_schedule_save_button: 'Save Schedule',
        website_audit_schedule_save_success: 'Website audit schedule saved.',
        website_audit_schedule_save_failed: 'Could not save website audit schedule.',
        website_audit_schedule_state_off: 'Scheduler: off',
        website_audit_schedule_state_no_target: 'Scheduler is on ({frequency} {time}), but no target URL is configured.',
        website_audit_schedule_state_on: 'Scheduler: {frequency} at {time} | Next: {next}',
        website_audit_frequency_daily: 'Daily',
        website_audit_frequency_weekly: 'Weekly',
        website_audit_profile_quick: 'Quick',
        website_audit_profile_standard: 'Standard',
        website_audit_profile_security: 'Security',
        website_audit_profile_full: 'Full',
        website_audit_start_missing_url: 'Add a website URL first.',
        website_audit_score_line: 'Score: {score}/100 ({grade})',
        website_audit_score_pending: 'Score: --',
        website_audit_meta_line: 'Pass: {pass} | Warn: {warn} | Fail: {fail}',
        website_audit_findings_empty: 'No findings to show yet.',
        website_audit_recommendations_empty: 'No remediation plan available yet.',
        website_audit_logs_empty: 'No audit logs available yet.',
        website_audit_download_unavailable: 'No audit report available for download.',
        website_audit_download_started: 'Download started ({format}).',
        overview_kicker: 'Command Center',
        overview_filter_label: 'Filter Actions',
        overview_filter_placeholder: 'Filter: stream, camera, security',
        overview_filter_hint: 'Type to quickly find actions and routines.',
        overview_filter_active: '{visible} visible, {hidden} hidden by filter.',
        overview_chip_mic_ready: 'MIC READY',
        overview_chip_mic_muted: 'MIC MUTED',
        overview_chip_mic_listening: 'MIC LISTENING',
        overview_chip_voice_ready: 'VOICE READY',
        overview_chip_voice_deafened: 'VOICE DEAFENED',
        overview_chip_voice_speaking: 'VOICE SPEAKING',
        overview_chip_camera_on: 'CAMERA ON',
        overview_chip_camera_off: 'CAMERA OFF',
        overview_chip_pending_on: 'CONFIRM NEEDED',
        overview_chip_pending_off: 'NO PENDING',
        overview_chip_stream_live: 'STREAM LIVE',
        overview_chip_stream_recording: 'STREAM REC',
        overview_chip_stream_live_recording: 'LIVE + REC',
        overview_chip_stream_idle: 'STREAM STANDBY',
        panel_expand: 'Expand',
        panel_collapse: 'Collapse',
        voice_status_mic_muted: 'Microphone muted',
        voice_button_muted: 'Mic Muted',
        command_suggestions_empty: 'No suggestions',
        shortcut_help_text: 'Local shortcuts: /help, /scanqr, /mood, /golive, /endlive, /record on, /record off, /scene live, /scene brb, /scene game, /marker, /stream on, /stream off, /stream help, /audit status, /audit report, /audit schedule, /mute, /unmute, /deafen, /undeafen, /camera on, /camera off, /clear, /lang',
        shortcut_unknown: 'Unknown shortcut. Type /help for options.',
        history_empty: 'No recent commands yet.',
    },
};

// Keywords om commando's grof te classificeren voor threat-indicator feedback.
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
        'stream ',
        'obs',
        'go live',
        'recording',
        'scene ',
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

async function resetLegacyServiceWorkerState() {
    if (!('serviceWorker' in navigator)) {
        return false;
    }

    try {
        const registrations = await navigator.serviceWorker.getRegistrations();
        await Promise.all(registrations.map((registration) => registration.unregister()));
    } catch (_error) {
        // Continue startup even when unregistering fails.
    }

    if ('caches' in window) {
        try {
            const cacheKeys = await caches.keys();
            await Promise.all(
                cacheKeys
                    .filter((key) => String(key || '').toLowerCase().startsWith('echo-app-shell-'))
                    .map((key) => caches.delete(key))
            );
        } catch (_error) {
            // Cache cleanup is best-effort.
        }
    }

    if (navigator.serviceWorker.controller && !sessionStorage.getItem('echo_sw_reset_done')) {
        sessionStorage.setItem('echo_sw_reset_done', '1');
        const url = new URL(window.location.href);
        url.searchParams.set('_fresh', String(Date.now()));
        window.location.replace(url.toString());
        return true;
    }

    return false;
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

function detectSamsungBrowser() {
    const userAgent = String(navigator.userAgent || '');
    return /SamsungBrowser/i.test(userAgent);
}

function isVoiceUploadFallbackAvailable() {
    return Boolean(mobileVoiceFileInput && typeof FormData !== 'undefined');
}

function isMobileDeviceContext() {
    const userAgent = String(navigator.userAgent || '');
    const touchPointer = typeof window.matchMedia === 'function' && window.matchMedia('(pointer: coarse)').matches;
    return touchPointer || /Android|iPhone|iPad|iPod|Mobile/i.test(userAgent);
}

function tekstVoorTaal(engels, nederlands) {
    return isNederlandsActief() ? String(nederlands || '') : String(engels || '');
}

function actieveUiTaalCode() {
    return isNederlandsActief() ? 'nl' : 'en';
}

function uiTekst(sleutel, variabelen = {}) {
    // Lookup met fallback + eenvoudige placeholdervervanging.
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

function setTextContentIfChanged(element, waarde) {
    if (!element) {
        return false;
    }

    const volgende = String(waarde || '');
    if (String(element.textContent || '') === volgende) {
        return false;
    }

    element.textContent = volgende;
    return true;
}

function setElementDisabledIfChanged(element, disabled) {
    if (!element) {
        return false;
    }

    const volgende = Boolean(disabled);
    if (Boolean(element.disabled) === volgende) {
        return false;
    }

    element.disabled = volgende;
    return true;
}

function serialiseerVoorUiSignature(waarde) {
    try {
        return JSON.stringify(waarde);
    } catch (_error) {
        return String(waarde || '');
    }
}

function dashboardSectieIsGewijzigd(sleutel, payload, force = false) {
    if (force) {
        appState.dashboardSectionSignatures[sleutel] = '';
    }

    const signature = serialiseerVoorUiSignature(payload);
    if (appState.dashboardSectionSignatures[sleutel] === signature) {
        return false;
    }

    appState.dashboardSectionSignatures[sleutel] = signature;
    return true;
}

function parseerBoolWaarde(waarde, standaard = false) {
    // Accepteer zowel booleans als stringvarianten uit API/settings payloads.
    if (typeof waarde === 'boolean') {
        return waarde;
    }

    const tekst = String(waarde || '').trim().toLowerCase();
    if (['1', 'true', 'yes', 'y', 'ja', 'on'].includes(tekst)) {
        return true;
    }
    if (['0', 'false', 'no', 'n', 'nee', 'off'].includes(tekst)) {
        return false;
    }
    return Boolean(standaard);
}

function formatteerLocaleDatumTijd(unixSeconden) {
    // Toon planner-timestamps in de actieve UI-taal.
    const waarde = Number(unixSeconden || 0);
    if (!Number.isFinite(waarde) || waarde <= 0) {
        return '';
    }

    try {
        const taal = isNederlandsActief() ? 'nl-NL' : 'en-US';
        return new Date(waarde * 1000).toLocaleString(taal, {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
        });
    } catch (_error) {
        return '';
    }
}

function renderDailySecurityPanel(payload) {
    // Render is tolerant: ontbrekende velden vallen terug op snapshot/defaults.
    if (!dailySecurityState || !dailySecuritySchedule || !dailySecurityResult) {
        return;
    }

    const data = payload && typeof payload === 'object' ? payload : {};
    // Merge zodat laatste bekende status zichtbaar blijft bij tijdelijke fetch-fouten.
    appState.dailySecuritySnapshot = {
        ...appState.dailySecuritySnapshot,
        ...data,
    };

    const supported = appState.dailySecuritySnapshot.supported !== false;
    const enabled = parseerBoolWaarde(appState.dailySecuritySnapshot.enabled, false);
    const monitorRunning = parseerBoolWaarde(appState.dailySecuritySnapshot.monitor_running, false);
    const geplandeTijd = String(appState.dailySecuritySnapshot.scheduled_time || '03:00').trim() || '03:00';
    const volgendeLabel = String(appState.dailySecuritySnapshot.next_run_label || '').trim()
        || formatteerLocaleDatumTijd(appState.dailySecuritySnapshot.next_run_at);

    let statusRegel = uiTekst('daily_security_state_disabled');
    if (!supported) {
        statusRegel = uiTekst('daily_security_state_unsupported');
    } else if (enabled) {
        statusRegel = uiTekst('daily_security_state_enabled', {
            monitor: monitorRunning ? uiTekst('daily_security_monitor_online') : uiTekst('daily_security_monitor_offline'),
        });
    }
    dailySecurityState.textContent = statusRegel;

    let schemaRegel = uiTekst('daily_security_schedule_disabled');
    if (supported && enabled) {
        schemaRegel = volgendeLabel
            ? uiTekst('daily_security_schedule_with_next', { time: geplandeTijd, next: volgendeLabel })
            : uiTekst('daily_security_schedule_basic', { time: geplandeTijd });
    }
    dailySecuritySchedule.textContent = schemaRegel;

    const laatsteTriggerTijd = Number(appState.dailySecuritySnapshot.last_triggered_at || 0);
    const laatsteResultaat = String(appState.dailySecuritySnapshot.last_trigger_result || '').trim();
    const laatsteTriggerSucces = appState.dailySecuritySnapshot.last_trigger_success === true;
    const laatsteWhenLabel = formatteerLocaleDatumTijd(laatsteTriggerTijd);

    let resultaatRegel = uiTekst('daily_security_last_never');
    if (laatsteTriggerTijd > 0) {
        resultaatRegel = uiTekst(
            laatsteTriggerSucces ? 'daily_security_last_success' : 'daily_security_last_skipped',
            { when: laatsteWhenLabel || '--' }
        );
    }

    if (laatsteResultaat) {
        resultaatRegel += ' | ' + uiTekst('daily_security_result', { result: laatsteResultaat });
    }
    dailySecurityResult.textContent = resultaatRegel;
}

function mobileHintTekstUitPayload(payload = {}) {
    const preferred = isNederlandsActief() ? payload.access_hint_nl : payload.access_hint_en;
    const fallback = isNederlandsActief() ? payload.access_hint_en : payload.access_hint_nl;
    return String(preferred || fallback || '').trim();
}

function normaliseerMobieleLinks(rawLinks) {
    if (!Array.isArray(rawLinks)) {
        return [];
    }

    const links = rawLinks
        .map((item) => String(item || '').trim())
        .filter((item) => item.startsWith('http://') || item.startsWith('https://'));

    return Array.from(new Set(links));
}

function compacteLabelVoorMobieleUrl(url, index) {
    try {
        const parsed = new URL(url);
        return `#${index + 1} ${parsed.hostname}:${parsed.port || '80'}`;
    } catch (_error) {
        return `#${index + 1} ${url}`;
    }
}

function renderMobileAccessPanel(payload) {
    if (!mobileAccessState || !mobileAccessHint || !mobileAccessLinks) {
        return;
    }

    const update = payload && typeof payload === 'object' ? payload : {};
    appState.mobileAccessSnapshot = {
        ...appState.mobileAccessSnapshot,
        ...update,
    };

    const enabled = parseerBoolWaarde(appState.mobileAccessSnapshot.enabled, false);
    const links = normaliseerMobieleLinks(appState.mobileAccessSnapshot.network_urls);
    const primary = String(appState.mobileAccessSnapshot.primary_network_url || links[0] || '').trim();
    const hintTekst = mobileHintTekstUitPayload(appState.mobileAccessSnapshot);
    appState.mobilePrimaryUrl = primary;

    if (enabled && primary) {
        mobileAccessState.textContent = uiTekst('mobile_access_ready', { url: primary });
    } else if (enabled) {
        mobileAccessState.textContent = uiTekst('mobile_access_enabled_no_url');
    } else if (hintTekst) {
        mobileAccessState.textContent = uiTekst('mobile_access_disabled');
    } else {
        mobileAccessState.textContent = uiTekst('mobile_access_checking');
    }

    mobileAccessHint.textContent = hintTekst || uiTekst('mobile_access_checking');

    mobileAccessLinks.innerHTML = '';
    if (!links.length) {
        const empty = document.createElement('p');
        empty.className = 'mobile-link-empty';
        empty.textContent = uiTekst('mobile_access_no_links');
        mobileAccessLinks.appendChild(empty);
        return;
    }

    links.slice(0, 5).forEach((url, index) => {
        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'mobile-link-chip';
        button.textContent = compacteLabelVoorMobieleUrl(url, index);
        button.title = url;
        button.addEventListener('click', () => {
            window.open(url, '_blank', 'noopener');
        });
        mobileAccessLinks.appendChild(button);
    });
}

function normaliseerScreenshotArtifact(payload = {}) {
    const data = payload && typeof payload === 'object' ? payload : {};
    const mobieleDownloadUrls = Array.isArray(data.mobile_download_urls)
        ? data.mobile_download_urls
            .map((item) => String(item || '').trim())
            .filter((item) => item.startsWith('http://') || item.startsWith('https://'))
        : [];

    const genormaliseerd = {
        available: parseerBoolWaarde(data.available, false),
        filename: String(data.filename || '').trim(),
        download_path: String(data.download_path || '').trim(),
        local_download_url: String(data.local_download_url || '').trim(),
        mobile_primary_download_url: String(data.mobile_primary_download_url || '').trim(),
        mobile_download_urls: mobieleDownloadUrls,
    };

    const heeftPad = Boolean(
        genormaliseerd.download_path
        || genormaliseerd.local_download_url
        || genormaliseerd.mobile_primary_download_url
        || genormaliseerd.mobile_download_urls.length
    );
    genormaliseerd.available = genormaliseerd.available && heeftPad;
    return genormaliseerd;
}

function resolveScreenshotDownloadUrl(snapshot = appState.latestScreenshotSnapshot) {
    const data = normaliseerScreenshotArtifact(snapshot);
    if (!data.available) {
        return '';
    }

    if (data.download_path) {
        const basis = normaliseerApiBaseUrl(appState.apiBaseUrl)
            || (isHttpPaginaContext() ? normaliseerApiBaseUrl(window.location.origin) : '');
        return combineerApiUrl(data.download_path, basis);
    }

    if (data.mobile_primary_download_url) {
        return data.mobile_primary_download_url;
    }

    if (data.mobile_download_urls.length) {
        return data.mobile_download_urls[0];
    }

    if (data.local_download_url) {
        if (data.local_download_url.startsWith('http://') || data.local_download_url.startsWith('https://')) {
            return data.local_download_url;
        }
        const basis = normaliseerApiBaseUrl(appState.apiBaseUrl)
            || (isHttpPaginaContext() ? normaliseerApiBaseUrl(window.location.origin) : '');
        return combineerApiUrl(data.local_download_url, basis);
    }

    return '';
}

function renderLatestScreenshotPanel(payload = {}) {
    if (!mobileScreenshotState || !mobileSaveScreenshotBtn || !mobileOpenScreenshotBtn) {
        return;
    }

    const snapshot = normaliseerScreenshotArtifact(payload);
    appState.latestScreenshotSnapshot = snapshot;

    if (snapshot.available) {
        mobileScreenshotState.textContent = uiTekst('mobile_screenshot_ready', {
            name: snapshot.filename || 'echo-screenshot.png',
        });
    } else {
        mobileScreenshotState.textContent = uiTekst('mobile_screenshot_none');
    }

    const downloadUrl = resolveScreenshotDownloadUrl(snapshot);
    const beschikbaar = Boolean(downloadUrl);
    mobileSaveScreenshotBtn.disabled = !beschikbaar;
    mobileOpenScreenshotBtn.disabled = !beschikbaar;
}

function normaliseerWebsiteAuditFrequency(waarde) {
    const raw = String(waarde || '').trim().toLowerCase();
    return raw === 'weekly' ? 'weekly' : 'daily';
}

function normaliseerWebsiteAuditTijd(waarde) {
    const raw = String(waarde || '').trim();
    const match = raw.match(/^(\d{1,2}):(\d{1,2})$/);
    if (!match) {
        return '04:30';
    }

    const uur = Number.parseInt(match[1], 10);
    const minuut = Number.parseInt(match[2], 10);
    if (!Number.isInteger(uur) || !Number.isInteger(minuut) || uur < 0 || uur > 23 || minuut < 0 || minuut > 59) {
        return '04:30';
    }

    return `${String(uur).padStart(2, '0')}:${String(minuut).padStart(2, '0')}`;
}

function normaliseerSettingsProfielNaam(waarde) {
    const raw = String(waarde || '').trim().toLowerCase();
    if (raw === 'streaming' || raw === 'security') {
        return raw;
    }
    return 'normal';
}

function normaliseerSettingsProfielenLijst(waarde) {
    const basis = ['normal', 'streaming', 'security'];
    const bron = [];

    if (Array.isArray(waarde)) {
        bron.push(...waarde);
    } else if (waarde && typeof waarde === 'object') {
        bron.push(...Object.keys(waarde));
    }

    const genormaliseerd = [];
    bron.forEach((item) => {
        const profiel = normaliseerSettingsProfielNaam(item);
        if (!genormaliseerd.includes(profiel)) {
            genormaliseerd.push(profiel);
        }
    });

    basis.forEach((item) => {
        if (!genormaliseerd.includes(item)) {
            genormaliseerd.push(item);
        }
    });

    return genormaliseerd;
}

function settingsProfielLabel(waarde) {
    const sleutel = normaliseerSettingsProfielNaam(waarde);
    return uiTekst('settings_profile_option_' + sleutel);
}

function normaliseerSettingsProfielProvider(waarde, toegestaan, fallback) {
    const raw = String(waarde || '').trim().toLowerCase();
    if (toegestaan.includes(raw)) {
        return raw;
    }
    return fallback;
}

function normaliseerSettingsWebsiteAuditProfiel(waarde) {
    const raw = String(waarde || '').trim().toLowerCase();
    if (raw === 'quick' || raw === 'security' || raw === 'full') {
        return raw;
    }
    return 'standard';
}

function normaliseerSettingsProfielConfig(naam, profielConfig) {
    const profielNaam = normaliseerSettingsProfielNaam(naam);
    const basis = SETTINGS_PROFILE_BASE_CONFIGS[profielNaam] || SETTINGS_PROFILE_BASE_CONFIGS.normal;
    const bron = profielConfig && typeof profielConfig === 'object' ? profielConfig : {};

    return {
        agent_modus: parseerBoolWaarde(bron.agent_modus, basis.agent_modus),
        geheugen_modus: parseerBoolWaarde(bron.geheugen_modus, basis.geheugen_modus),
        prioriteit_modus: parseerBoolWaarde(bron.prioriteit_modus, basis.prioriteit_modus),
        computerbesturing_toestaan: parseerBoolWaarde(bron.computerbesturing_toestaan, basis.computerbesturing_toestaan),
        online_ai_modus: parseerBoolWaarde(bron.online_ai_modus, basis.online_ai_modus),
        ai_agent_primair: parseerBoolWaarde(bron.ai_agent_primair, basis.ai_agent_primair),
        spraak_ingang: parseerBoolWaarde(bron.spraak_ingang, basis.spraak_ingang),
        spraak_uitgang: parseerBoolWaarde(bron.spraak_uitgang, basis.spraak_uitgang),
        spraak_input_provider: normaliseerSettingsProfielProvider(
            bron.spraak_input_provider,
            ['google', 'whisper'],
            basis.spraak_input_provider
        ),
        spraak_provider: normaliseerSettingsProfielProvider(
            bron.spraak_provider,
            ['local', 'google'],
            basis.spraak_provider
        ),
        security_scan_daily_enabled: parseerBoolWaarde(bron.security_scan_daily_enabled, basis.security_scan_daily_enabled),
        website_audit_schedule_profile: normaliseerSettingsWebsiteAuditProfiel(
            bron.website_audit_schedule_profile || basis.website_audit_schedule_profile
        ),
        stream_auto_focus_obs: parseerBoolWaarde(bron.stream_auto_focus_obs, basis.stream_auto_focus_obs),
    };
}

function normaliseerSettingsProfielConfigs(waarde) {
    const basis = {
        normal: normaliseerSettingsProfielConfig('normal', SETTINGS_PROFILE_BASE_CONFIGS.normal),
        streaming: normaliseerSettingsProfielConfig('streaming', SETTINGS_PROFILE_BASE_CONFIGS.streaming),
        security: normaliseerSettingsProfielConfig('security', SETTINGS_PROFILE_BASE_CONFIGS.security),
    };

    if (!waarde || typeof waarde !== 'object') {
        return basis;
    }

    Object.entries(waarde).forEach(([naam, config]) => {
        const profielNaam = normaliseerSettingsProfielNaam(naam);
        basis[profielNaam] = normaliseerSettingsProfielConfig(profielNaam, config);
    });

    return basis;
}

function extractSettingsProfielenUitPayload(payload = {}) {
    const data = payload && typeof payload === 'object' ? payload : {};

    if (Array.isArray(data.settings_profiles)) {
        return data.settings_profiles;
    }

    if (Array.isArray(data.settingsProfiles)) {
        return data.settingsProfiles;
    }

    if (data.instellingen_profielen && typeof data.instellingen_profielen === 'object') {
        return Object.keys(data.instellingen_profielen);
    }

    return [];
}

function extractSettingsProfielConfigsUitPayload(payload = {}) {
    const data = payload && typeof payload === 'object' ? payload : {};

    if (data.settings_profile_configs && typeof data.settings_profile_configs === 'object') {
        return data.settings_profile_configs;
    }

    if (data.instellingen_profielen && typeof data.instellingen_profielen === 'object') {
        return data.instellingen_profielen;
    }

    return {};
}

function normaliseerSettingsProfielActieItem(actie) {
    const data = actie && typeof actie === 'object' && !Array.isArray(actie)
        ? actie
        : { command: actie };

    const command = String(data.command || '').trim().replace(/\s+/g, ' ');
    if (!command) {
        return null;
    }

    const label = String(data.label || '').trim().replace(/\s+/g, ' ');
    const labelKey = String(data.labelKey || '').trim();
    const item = { command };
    if (label) {
        item.label = label;
    }
    if (labelKey) {
        item.labelKey = labelKey;
    }
    return item;
}

function normaliseerSettingsProfielActiesLijst(waarde, fallback = []) {
    const bron = Array.isArray(waarde) ? waarde : fallback;
    const lijst = [];

    bron.forEach((item) => {
        if (lijst.length >= 10) {
            return;
        }
        const actie = normaliseerSettingsProfielActieItem(item);
        if (actie) {
            lijst.push(actie);
        }
    });

    return lijst;
}

function normaliseerSettingsProfielActiesData(waarde) {
    const basis = {
        normal: normaliseerSettingsProfielActiesLijst(SETTINGS_PROFILE_ACTION_PRESETS.normal, SETTINGS_PROFILE_ACTION_PRESETS.normal),
        streaming: normaliseerSettingsProfielActiesLijst(SETTINGS_PROFILE_ACTION_PRESETS.streaming, SETTINGS_PROFILE_ACTION_PRESETS.streaming),
        security: normaliseerSettingsProfielActiesLijst(SETTINGS_PROFILE_ACTION_PRESETS.security, SETTINGS_PROFILE_ACTION_PRESETS.security),
    };

    if (!waarde || typeof waarde !== 'object') {
        return basis;
    }

    Object.entries(waarde).forEach(([naam, acties]) => {
        const profielNaam = normaliseerSettingsProfielNaam(naam);
        basis[profielNaam] = normaliseerSettingsProfielActiesLijst(
            acties,
            SETTINGS_PROFILE_ACTION_PRESETS[profielNaam] || SETTINGS_PROFILE_ACTION_PRESETS.normal
        );
    });

    return basis;
}

function extractSettingsProfielActiesUitPayload(payload = {}) {
    const data = payload && typeof payload === 'object' ? payload : {};
    if (data.settings_profile_actions && typeof data.settings_profile_actions === 'object') {
        return data.settings_profile_actions;
    }
    if (data.instellingen_profiel_acties && typeof data.instellingen_profiel_acties === 'object') {
        return data.instellingen_profiel_acties;
    }
    return {};
}

function begrensSettingsRouterThreshold(waarde, fallback, min, max) {
    const parsed = Number.parseInt(String(waarde || ''), 10);
    if (!Number.isInteger(parsed)) {
        return fallback;
    }
    return Math.max(min, Math.min(max, parsed));
}

function normaliseerSettingsProfileRouterConfig(payload = {}) {
    const data = payload && typeof payload === 'object' ? payload : {};

    const leesWaarde = (engelseSleutel, nederlandseSleutel, fallback) => {
        if (Object.prototype.hasOwnProperty.call(data, engelseSleutel)) {
            return data[engelseSleutel];
        }
        if (Object.prototype.hasOwnProperty.call(data, nederlandseSleutel)) {
            return data[nederlandseSleutel];
        }
        return fallback;
    };

    const enabled = parseerBoolWaarde(
        leesWaarde('profile_auto_router_enabled', 'profiel_auto_router_enabled', appState.settingsProfileRouterEnabled),
        true
    );

    const suggest = begrensSettingsRouterThreshold(
        leesWaarde(
            'profile_auto_router_suggest_threshold',
            'profiel_auto_router_suggest_threshold',
            appState.settingsProfileRouterSuggestThreshold
        ),
        62,
        35,
        95
    );

    const autoThresholdRuw = begrensSettingsRouterThreshold(
        leesWaarde(
            'profile_auto_router_auto_threshold',
            'profiel_auto_router_auto_threshold',
            appState.settingsProfileRouterAutoThreshold
        ),
        86,
        45,
        99
    );

    const autoThreshold = Math.max(Math.min(99, suggest + 5), autoThresholdRuw);
    return {
        enabled,
        suggestThreshold: suggest,
        autoThreshold,
    };
}

function analyseerSettingsProfielIntent(commandoTekst) {
    const tekst = normalizeText(commandoTekst);
    if (!tekst) {
        return null;
    }

    const scores = {
        normal: 4,
        streaming: 0,
        security: 0,
    };
    const hints = {
        normal: [],
        streaming: [],
        security: [],
    };

    Object.entries(SETTINGS_PROFILE_INTENT_RULES).forEach(([profiel, regels]) => {
        regels.forEach((regel) => {
            if (regel.pattern.test(tekst)) {
                scores[profiel] += Number(regel.score || 0);
                hints[profiel].push(String(regel.hint || '').trim());
            }
        });
    });

    const ranking = Object.entries(scores)
        .map(([profiel, score]) => ({ profiel, score: Number(score || 0) }))
        .sort((a, b) => b.score - a.score);

    const top = ranking[0];
    const second = ranking[1] || { score: 0 };
    if (!top || top.score <= 0) {
        return null;
    }

    const delta = top.score - Number(second.score || 0);
    const confidenceRaw = 44 + (top.score * 1.5) + (delta * 1.15);
    const confidence = Math.max(0, Math.min(99, Math.round(confidenceRaw)));

    return {
        profile: normaliseerSettingsProfielNaam(top.profiel),
        score: top.score,
        confidence,
        hintKey: hints[top.profiel][0] || '',
    };
}

function settingsProfielStatusLabel(waarde) {
    return parseerBoolWaarde(waarde, false) ? uiTekst('settings_profile_on') : uiTekst('settings_profile_off');
}

function settingsProfielProviderLabel(type, waarde) {
    const raw = String(waarde || '').trim().toLowerCase();
    if (type === 'stt') {
        return uiTekst(raw === 'whisper' ? 'settings_profile_provider_whisper' : 'settings_profile_provider_google');
    }
    return uiTekst(raw === 'google' ? 'settings_profile_provider_google' : 'settings_profile_provider_local');
}

function settingsProfielSummaryTekst(waarde) {
    const profielNaam = normaliseerSettingsProfielNaam(waarde);
    return uiTekst('settings_profile_summary_' + profielNaam);
}

function settingsProfielActiePreset(waarde) {
    const profielNaam = normaliseerSettingsProfielNaam(waarde);
    const acties = appState.settingsProfileActionsByProfile[profielNaam];
    if (Array.isArray(acties) && acties.length) {
        return acties;
    }
    return normaliseerSettingsProfielActiesLijst(
        SETTINGS_PROFILE_ACTION_PRESETS[profielNaam] || SETTINGS_PROFILE_ACTION_PRESETS.normal,
        SETTINGS_PROFILE_ACTION_PRESETS.normal
    );
}

function settingsProfielLaunchSequence(waarde) {
    const profielNaam = normaliseerSettingsProfielNaam(waarde);
    const custom = settingsProfielActiePreset(profielNaam)
        .map((actie) => String(actie.command || '').trim())
        .filter(Boolean)
        .slice(0, 2);
    if (custom.length) {
        return custom;
    }
    return SETTINGS_PROFILE_LAUNCH_SEQUENCES[profielNaam] || SETTINGS_PROFILE_LAUNCH_SEQUENCES.normal;
}

function settingsProfielActieLabel(actie) {
    const data = actie && typeof actie === 'object' ? actie : {};
    const labelKey = String(data.labelKey || '').trim();
    const labelTekst = String(data.label || '').trim();
    if (labelKey) {
        return uiTekst(labelKey);
    }
    if (labelTekst) {
        return labelTekst;
    }
    return String(data.command || '').trim();
}

function serializeSettingsProfielActiesVoorEditor(profielNaam) {
    const profiel = normaliseerSettingsProfielNaam(profielNaam);
    const lijst = settingsProfielActiePreset(profiel);
    return lijst
        .map((actie) => String(actie.command || '').trim())
        .filter(Boolean)
        .join('\n');
}

function renderSettingsProfielActiesEditor(profielNaam, options = {}) {
    if (!settingsProfileActionsEditor) {
        return;
    }

    const opts = options && typeof options === 'object' ? options : {};
    const force = parseerBoolWaarde(opts.force, false);
    const locked = parseerBoolWaarde(opts.locked, false);
    const volgendeWaarde = serializeSettingsProfielActiesVoorEditor(profielNaam);
    const heeftFocus = document.activeElement === settingsProfileActionsEditor;

    if (force || !heeftFocus || !appState.settingsProfileActionsEditorDirty) {
        settingsProfileActionsEditor.value = volgendeWaarde;
        appState.settingsProfileActionsEditorDirty = false;
    }

    settingsProfileActionsEditor.disabled = Boolean(locked);
}

function settingsProfielRouterStatusTekst() {
    if (!appState.settingsProfileRouterEnabled) {
        return uiTekst('settings_profile_router_state_off');
    }

    const hint = appState.settingsProfileIntentHint;
    if (!hint || !hint.profile) {
        return uiTekst('settings_profile_router_state_idle');
    }

    const profielLabel = settingsProfielLabel(hint.profile);
    const confidence = String(Math.max(0, Math.min(99, Number(hint.confidence || 0))));
    const statusKey = hint.mode === 'auto'
        ? 'settings_profile_router_state_auto'
        : 'settings_profile_router_state_suggest';
    let tekst = uiTekst(statusKey, {
        profile: profielLabel,
        confidence,
    });

    if (hint.hintKey) {
        tekst += ` | ${uiTekst(hint.hintKey)}`;
    }
    return tekst;
}

function renderSettingsProfielEffecten(profielNaam, profielConfig) {
    if (!settingsProfileEffects) {
        return;
    }

    const config = normaliseerSettingsProfielConfig(profielNaam, profielConfig);
    const auditProfiel = normaliseerSettingsWebsiteAuditProfiel(config.website_audit_schedule_profile);
    const regels = [
        {
            labelKey: 'settings_profile_effect_agent_mode',
            value: settingsProfielStatusLabel(config.agent_modus),
            state: parseerBoolWaarde(config.agent_modus, false) ? 'on' : 'off',
        },
        {
            labelKey: 'settings_profile_effect_memory_mode',
            value: settingsProfielStatusLabel(config.geheugen_modus),
            state: parseerBoolWaarde(config.geheugen_modus, false) ? 'on' : 'off',
        },
        {
            labelKey: 'settings_profile_effect_priority_mode',
            value: settingsProfielStatusLabel(config.prioriteit_modus),
            state: parseerBoolWaarde(config.prioriteit_modus, false) ? 'on' : 'off',
        },
        {
            labelKey: 'settings_profile_effect_automation',
            value: settingsProfielStatusLabel(config.computerbesturing_toestaan),
            state: parseerBoolWaarde(config.computerbesturing_toestaan, false) ? 'on' : 'off',
        },
        {
            labelKey: 'settings_profile_effect_online_ai',
            value: settingsProfielStatusLabel(config.online_ai_modus),
            state: parseerBoolWaarde(config.online_ai_modus, false) ? 'on' : 'off',
        },
        {
            labelKey: 'settings_profile_effect_voice_input',
            value: settingsProfielStatusLabel(config.spraak_ingang),
            state: parseerBoolWaarde(config.spraak_ingang, false) ? 'on' : 'off',
        },
        {
            labelKey: 'settings_profile_effect_voice_output',
            value: settingsProfielStatusLabel(config.spraak_uitgang),
            state: parseerBoolWaarde(config.spraak_uitgang, false) ? 'on' : 'off',
        },
        {
            labelKey: 'settings_profile_effect_stt_provider',
            value: settingsProfielProviderLabel('stt', config.spraak_input_provider),
            state: 'accent',
        },
        {
            labelKey: 'settings_profile_effect_tts_provider',
            value: settingsProfielProviderLabel('tts', config.spraak_provider),
            state: 'accent',
        },
        {
            labelKey: 'settings_profile_effect_security_daily',
            value: settingsProfielStatusLabel(config.security_scan_daily_enabled),
            state: parseerBoolWaarde(config.security_scan_daily_enabled, false) ? 'on' : 'off',
        },
        {
            labelKey: 'settings_profile_effect_audit_profile',
            value: uiTekst('website_audit_profile_' + auditProfiel),
            state: 'accent',
        },
        {
            labelKey: 'settings_profile_effect_obs_focus',
            value: settingsProfielStatusLabel(config.stream_auto_focus_obs),
            state: parseerBoolWaarde(config.stream_auto_focus_obs, false) ? 'on' : 'off',
        },
    ];

    settingsProfileEffects.innerHTML = '';
    regels.forEach((regel) => {
        const row = document.createElement('article');
        row.className = 'settings-profile-effect';

        const label = document.createElement('span');
        label.className = 'settings-profile-effect__label';
        label.textContent = uiTekst(regel.labelKey);
        row.appendChild(label);

        const value = document.createElement('span');
        value.className = 'settings-profile-effect__value';
        value.dataset.state = regel.state;
        value.textContent = String(regel.value || '').trim() || '-';
        row.appendChild(value);

        settingsProfileEffects.appendChild(row);
    });
}

function renderSettingsProfielActies(profielNaam, disabled = false) {
    if (!settingsProfileActions) {
        return;
    }

    const acties = settingsProfielActiePreset(profielNaam);
    settingsProfileActions.innerHTML = '';

    acties.forEach((actie) => {
        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'panel-action settings-profile-action';
        button.dataset.profileCommand = String(actie.command || '').trim();
        button.dataset.profileName = normaliseerSettingsProfielNaam(profielNaam);
        button.disabled = Boolean(disabled);
        button.textContent = settingsProfielActieLabel(actie);
        settingsProfileActions.appendChild(button);
    });
}

async function startSettingsProfielWorkflowVoorProfiel(waarde) {
    if (appState.settingsProfileApplying || appState.settingsProfileLaunching || appState.settingsProfileRouterSaving) {
        return;
    }

    const profielNaam = normaliseerSettingsProfielNaam(waarde);
    const launchActies = settingsProfielLaunchSequence(profielNaam);
    if (!Array.isArray(launchActies) || !launchActies.length) {
        return;
    }

    appState.settingsProfileLaunching = true;
    renderSettingsProfilePanel({
        launching: true,
        selected: profielNaam,
    });

    const profielLabel = settingsProfielLabel(profielNaam);
    setCommandStatus(uiTekst('settings_profile_state_launching', {
        profile: profielLabel,
    }));

    try {
        for (const actie of launchActies) {
            const commando = String(actie || '').trim();
            if (!commando) {
                continue;
            }
            await sendCommand(commando, 'quick');
        }

        const melding = uiTekst('settings_profile_launch_done', {
            profile: profielLabel,
        });
        setCommandStatus(melding);
        triggerHapticFeedback([40, 25, 40]);
    } catch (_error) {
        setCommandStatus(uiTekst('settings_profile_launch_failed'));
        triggerHapticFeedback([90, 35, 90]);
    } finally {
        appState.settingsProfileLaunching = false;
        renderSettingsProfilePanel({
            launching: false,
            selected: profielNaam,
        });
    }
}

async function startSettingsProfielFlow(event) {
    if (event && typeof event.preventDefault === 'function') {
        event.preventDefault();
    }

    if (!settingsProfileSelect || appState.settingsProfileApplying || appState.settingsProfileLaunching || appState.settingsProfileRouterSaving) {
        return;
    }

    const geselecteerdProfiel = normaliseerSettingsProfielNaam(settingsProfileSelect.value);
    if (geselecteerdProfiel !== appState.settingsProfile) {
        await applySettingsProfiel(null, {
            forcedProfile: geselecteerdProfiel,
            launchAfterApply: true,
        });
        return;
    }

    await startSettingsProfielWorkflowVoorProfiel(geselecteerdProfiel);
}

function bouwProfielActiesLijstUitEditor() {
    const lines = String(settingsProfileActionsEditor ? settingsProfileActionsEditor.value : '')
        .split(/\r?\n/)
        .map((line) => line.trim())
        .filter(Boolean)
        .slice(0, 10);

    return normaliseerSettingsProfielActiesLijst(lines, []);
}

async function saveSettingsProfielActies(event) {
    if (event && typeof event.preventDefault === 'function') {
        event.preventDefault();
    }

    if (!settingsProfileActionsEditor || appState.settingsProfileApplying || appState.settingsProfileLaunching || appState.settingsProfileRouterSaving) {
        return;
    }

    const profielNaam = normaliseerSettingsProfielNaam(appState.settingsProfileSelected || appState.settingsProfile);
    const acties = bouwProfielActiesLijstUitEditor();
    if (!acties.length) {
        setCommandStatus(uiTekst('settings_profile_actions_save_failed'));
        triggerHapticFeedback([90, 35, 90]);
        return;
    }

    const volgendeActies = {
        ...appState.settingsProfileActionsByProfile,
        [profielNaam]: acties,
    };

    appState.settingsProfileRouterSaving = true;
    renderSettingsProfilePanel({
        profileActions: volgendeActies,
        routerSaving: true,
    });

    try {
        const response = await fetchEchoApi('/api/instellingen', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                instellingen_profiel_acties: volgendeActies,
            }),
        }, 9000);

        const data = await response.json().catch(() => ({
            status: 'error',
            message: uiTekst('invalid_server_response'),
        }));

        if (!response.ok || data.status !== 'success') {
            const message = String(data.message || '').trim() || uiTekst('settings_profile_actions_save_failed');
            throw new Error(message);
        }

        const payloadActies = extractSettingsProfielActiesUitPayload(data);
        appState.settingsProfileActionsByProfile = normaliseerSettingsProfielActiesData(
            Object.keys(payloadActies).length ? payloadActies : volgendeActies
        );
        appState.settingsProfileActionsEditorDirty = false;
        appState.settingsProfileRouterSaving = false;

        renderSettingsProfilePanel({
            profileActions: appState.settingsProfileActionsByProfile,
            routerSaving: false,
        });

        const melding = uiTekst('settings_profile_actions_save_success', {
            profile: settingsProfielLabel(profielNaam),
        });
        addMessage('ai', melding);
        setCommandStatus(melding);
        triggerHapticFeedback(40);
    } catch (error) {
        appState.settingsProfileRouterSaving = false;
        renderSettingsProfilePanel({ routerSaving: false });
        const rawMessage = error instanceof Error ? String(error.message || '').trim() : '';
        const melding = rawMessage || uiTekst('settings_profile_actions_save_failed');
        addMessage('error', melding);
        setCommandStatus(melding);
        triggerHapticFeedback([90, 35, 90]);
    }
}

async function resetSettingsProfielActies(event) {
    if (event && typeof event.preventDefault === 'function') {
        event.preventDefault();
    }

    if (appState.settingsProfileApplying || appState.settingsProfileLaunching || appState.settingsProfileRouterSaving) {
        return;
    }

    const profielNaam = normaliseerSettingsProfielNaam(appState.settingsProfileSelected || appState.settingsProfile);
    const standaardActies = normaliseerSettingsProfielActiesLijst(
        SETTINGS_PROFILE_ACTION_PRESETS[profielNaam] || SETTINGS_PROFILE_ACTION_PRESETS.normal,
        SETTINGS_PROFILE_ACTION_PRESETS.normal
    );

    const volgendeActies = {
        ...appState.settingsProfileActionsByProfile,
        [profielNaam]: standaardActies,
    };

    appState.settingsProfileRouterSaving = true;
    renderSettingsProfilePanel({
        profileActions: volgendeActies,
        routerSaving: true,
    });

    try {
        const response = await fetchEchoApi('/api/instellingen', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                instellingen_profiel_acties: volgendeActies,
            }),
        }, 9000);

        const data = await response.json().catch(() => ({
            status: 'error',
            message: uiTekst('invalid_server_response'),
        }));

        if (!response.ok || data.status !== 'success') {
            const message = String(data.message || '').trim() || uiTekst('settings_profile_actions_reset_failed');
            throw new Error(message);
        }

        const payloadActies = extractSettingsProfielActiesUitPayload(data);
        appState.settingsProfileActionsByProfile = normaliseerSettingsProfielActiesData(
            Object.keys(payloadActies).length ? payloadActies : volgendeActies
        );
        appState.settingsProfileActionsEditorDirty = false;
        appState.settingsProfileRouterSaving = false;

        renderSettingsProfilePanel({
            profileActions: appState.settingsProfileActionsByProfile,
            routerSaving: false,
        });

        const melding = uiTekst('settings_profile_actions_reset_success', {
            profile: settingsProfielLabel(profielNaam),
        });
        addMessage('ai', melding);
        setCommandStatus(melding);
        triggerHapticFeedback(40);
    } catch (error) {
        appState.settingsProfileRouterSaving = false;
        renderSettingsProfilePanel({ routerSaving: false });
        const rawMessage = error instanceof Error ? String(error.message || '').trim() : '';
        const melding = rawMessage || uiTekst('settings_profile_actions_reset_failed');
        addMessage('error', melding);
        setCommandStatus(melding);
        triggerHapticFeedback([90, 35, 90]);
    }
}

async function saveSettingsProfielRouter(event) {
    if (event && typeof event.preventDefault === 'function') {
        event.preventDefault();
    }

    if (appState.settingsProfileApplying || appState.settingsProfileLaunching || appState.settingsProfileRouterSaving) {
        return;
    }

    const routerEnabled = parseerBoolWaarde(
        settingsProfileRouterEnabledToggle && settingsProfileRouterEnabledToggle.checked,
        true
    );
    const suggestThreshold = begrensSettingsRouterThreshold(
        settingsProfileSuggestThresholdInput ? settingsProfileSuggestThresholdInput.value : appState.settingsProfileRouterSuggestThreshold,
        appState.settingsProfileRouterSuggestThreshold,
        35,
        95
    );
    const autoThresholdRuw = begrensSettingsRouterThreshold(
        settingsProfileAutoThresholdInput ? settingsProfileAutoThresholdInput.value : appState.settingsProfileRouterAutoThreshold,
        appState.settingsProfileRouterAutoThreshold,
        45,
        99
    );
    const autoThreshold = Math.max(Math.min(99, suggestThreshold + 5), autoThresholdRuw);

    appState.settingsProfileRouterSaving = true;
    renderSettingsProfilePanel({
        profile_auto_router_enabled: routerEnabled,
        profile_auto_router_suggest_threshold: suggestThreshold,
        profile_auto_router_auto_threshold: autoThreshold,
        routerSaving: true,
    });

    try {
        const response = await fetchEchoApi('/api/instellingen', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                profiel_auto_router_enabled: routerEnabled,
                profiel_auto_router_suggest_threshold: suggestThreshold,
                profiel_auto_router_auto_threshold: autoThreshold,
            }),
        }, 9000);

        const data = await response.json().catch(() => ({
            status: 'error',
            message: uiTekst('invalid_server_response'),
        }));

        if (!response.ok || data.status !== 'success') {
            const message = String(data.message || '').trim() || uiTekst('settings_profile_router_settings_failed');
            throw new Error(message);
        }

        const routerConfig = normaliseerSettingsProfileRouterConfig(data);
        appState.settingsProfileRouterEnabled = routerConfig.enabled;
        appState.settingsProfileRouterSuggestThreshold = routerConfig.suggestThreshold;
        appState.settingsProfileRouterAutoThreshold = routerConfig.autoThreshold;
        appState.settingsProfileRouterSaving = false;

        renderSettingsProfilePanel({
            profile_auto_router_enabled: appState.settingsProfileRouterEnabled,
            profile_auto_router_suggest_threshold: appState.settingsProfileRouterSuggestThreshold,
            profile_auto_router_auto_threshold: appState.settingsProfileRouterAutoThreshold,
            routerSaving: false,
        });

        const melding = uiTekst('settings_profile_router_settings_saved');
        setCommandStatus(melding);
        triggerHapticFeedback(40);
    } catch (error) {
        appState.settingsProfileRouterSaving = false;
        renderSettingsProfilePanel({ routerSaving: false });
        const rawMessage = error instanceof Error ? String(error.message || '').trim() : '';
        const melding = rawMessage || uiTekst('settings_profile_router_settings_failed');
        addMessage('error', melding);
        setCommandStatus(melding);
        triggerHapticFeedback([90, 35, 90]);
    }
}

function updateSettingsProfileIntentHint(commandoTekst, modeOverride = '') {
    const hint = analyseerSettingsProfielIntent(commandoTekst);
    if (!hint) {
        appState.settingsProfileIntentHint = null;
        renderSettingsProfilePanel({ intentHint: null });
        return null;
    }

    const mode = String(modeOverride || '').trim().toLowerCase();
    const resolvedMode = mode === 'auto'
        ? 'auto'
        : (hint.confidence >= appState.settingsProfileRouterAutoThreshold ? 'auto' : 'suggest');

    appState.settingsProfileIntentHint = {
        profile: hint.profile,
        confidence: hint.confidence,
        mode: resolvedMode,
        hintKey: hint.hintKey,
    };
    renderSettingsProfilePanel({ intentHint: appState.settingsProfileIntentHint });
    return appState.settingsProfileIntentHint;
}

function wisSettingsProfielHighlight() {
    if (appState.settingsProfileHighlightTimer) {
        window.clearTimeout(appState.settingsProfileHighlightTimer);
        appState.settingsProfileHighlightTimer = 0;
    }

    if (settingsProfilePanel) {
        settingsProfilePanel.dataset.applied = 'false';
    }
}

function markeerSettingsProfielToegepast() {
    if (!settingsProfilePanel) {
        return;
    }

    wisSettingsProfielHighlight();
    settingsProfilePanel.dataset.applied = 'true';
    appState.settingsProfileHighlightTimer = window.setTimeout(() => {
        if (settingsProfilePanel) {
            settingsProfilePanel.dataset.applied = 'false';
        }
        appState.settingsProfileHighlightTimer = 0;
    }, 1900);
}

function renderSettingsProfilePanel(payload = {}) {
    if (!settingsProfileKicker || !settingsProfileState || !settingsProfileSelect || !settingsProfileApplyBtn) {
        return;
    }

    const data = payload && typeof payload === 'object' ? payload : {};
    const profielBron = Object.prototype.hasOwnProperty.call(data, 'profile')
        ? data.profile
        : appState.settingsProfile;
    const geselecteerdProfielBron = Object.prototype.hasOwnProperty.call(data, 'selected')
        ? data.selected
        : appState.settingsProfileSelected;
    const profielenBron = Object.prototype.hasOwnProperty.call(data, 'profiles')
        ? data.profiles
        : appState.settingsProfiles;
    const profielConfigsBron = Object.prototype.hasOwnProperty.call(data, 'profileConfigs')
        ? data.profileConfigs
        : appState.settingsProfileConfigs;
    const profielActiesBron = Object.prototype.hasOwnProperty.call(data, 'profileActions')
        ? data.profileActions
        : appState.settingsProfileActionsByProfile;
    const applyingBron = Object.prototype.hasOwnProperty.call(data, 'applying')
        ? data.applying
        : appState.settingsProfileApplying;
    const launchingBron = Object.prototype.hasOwnProperty.call(data, 'launching')
        ? data.launching
        : appState.settingsProfileLaunching;
    const routerSavingBron = Object.prototype.hasOwnProperty.call(data, 'routerSaving')
        ? data.routerSaving
        : appState.settingsProfileRouterSaving;
    const intentHintBron = Object.prototype.hasOwnProperty.call(data, 'intentHint')
        ? data.intentHint
        : appState.settingsProfileIntentHint;

    appState.settingsProfile = normaliseerSettingsProfielNaam(profielBron);
    appState.settingsProfileSelected = normaliseerSettingsProfielNaam(geselecteerdProfielBron || appState.settingsProfile);
    appState.settingsProfiles = normaliseerSettingsProfielenLijst(profielenBron);
    appState.settingsProfileConfigs = normaliseerSettingsProfielConfigs(profielConfigsBron);
    appState.settingsProfileActionsByProfile = normaliseerSettingsProfielActiesData(profielActiesBron);
    appState.settingsProfileApplying = parseerBoolWaarde(applyingBron, false);
    appState.settingsProfileLaunching = parseerBoolWaarde(launchingBron, false);
    appState.settingsProfileRouterSaving = parseerBoolWaarde(routerSavingBron, false);

    const routerConfig = normaliseerSettingsProfileRouterConfig(data);
    appState.settingsProfileRouterEnabled = routerConfig.enabled;
    appState.settingsProfileRouterSuggestThreshold = routerConfig.suggestThreshold;
    appState.settingsProfileRouterAutoThreshold = routerConfig.autoThreshold;
    appState.settingsProfileIntentHint = intentHintBron && typeof intentHintBron === 'object'
        ? {
            profile: normaliseerSettingsProfielNaam(intentHintBron.profile || appState.settingsProfile),
            confidence: Math.max(0, Math.min(99, Number(intentHintBron.confidence || 0))),
            mode: String(intentHintBron.mode || 'suggest').trim().toLowerCase() === 'auto' ? 'auto' : 'suggest',
            hintKey: String(intentHintBron.hintKey || '').trim(),
        }
        : null;

    if (!appState.settingsProfiles.includes(appState.settingsProfile)) {
        appState.settingsProfiles = [appState.settingsProfile, ...appState.settingsProfiles];
    }
    if (!appState.settingsProfiles.includes(appState.settingsProfileSelected)) {
        appState.settingsProfiles = [appState.settingsProfileSelected, ...appState.settingsProfiles];
    }

    const bestaandeOpties = Array.from(settingsProfileSelect.options || [])
        .map((optie) => String(optie.value || '').trim().toLowerCase());
    const gewensteOpties = [...appState.settingsProfiles];
    const moetOptiesVerversen = bestaandeOpties.join('|') !== gewensteOpties.join('|');

    if (moetOptiesVerversen) {
        settingsProfileSelect.innerHTML = '';
        gewensteOpties.forEach((profiel) => {
            const option = document.createElement('option');
            option.value = profiel;
            option.textContent = settingsProfielLabel(profiel);
            settingsProfileSelect.appendChild(option);
        });
    } else {
        Array.from(settingsProfileSelect.options || []).forEach((optie) => {
            const profiel = normaliseerSettingsProfielNaam(optie.value);
            optie.textContent = settingsProfielLabel(profiel);
        });
    }

    if (document.activeElement !== settingsProfileSelect) {
        settingsProfileSelect.value = appState.settingsProfileSelected;
    }

    const profielInteractieGeblokkeerd = appState.settingsProfileApplying
        || appState.settingsProfileLaunching
        || appState.settingsProfileRouterSaving;
    settingsProfileSelect.disabled = profielInteractieGeblokkeerd;
    settingsProfileApplyBtn.disabled = profielInteractieGeblokkeerd;
    settingsProfileApplyBtn.textContent = appState.settingsProfileApplying
        ? uiTekst('settings_profile_applying')
        : uiTekst('settings_profile_apply_button');

    if (settingsProfileLaunchBtn) {
        settingsProfileLaunchBtn.disabled = profielInteractieGeblokkeerd;
        settingsProfileLaunchBtn.textContent = appState.settingsProfileLaunching
            ? uiTekst('settings_profile_launching')
            : uiTekst('settings_profile_launch_button');
    }

    if (settingsProfileSummary) {
        settingsProfileSummary.textContent = settingsProfielSummaryTekst(appState.settingsProfileSelected);
    }

    if (settingsProfileActionsTitle) {
        settingsProfileActionsTitle.textContent = uiTekst('settings_profile_actions_title');
    }

    if (settingsProfileActionsEditorLabel) {
        settingsProfileActionsEditorLabel.textContent = uiTekst('settings_profile_actions_editor_label');
    }

    if (settingsProfileActionsSaveBtn) {
        settingsProfileActionsSaveBtn.textContent = uiTekst('settings_profile_actions_save_button');
        settingsProfileActionsSaveBtn.disabled = profielInteractieGeblokkeerd;
    }

    if (settingsProfileActionsResetBtn) {
        settingsProfileActionsResetBtn.textContent = uiTekst('settings_profile_actions_reset_button');
        settingsProfileActionsResetBtn.disabled = profielInteractieGeblokkeerd;
    }

    if (settingsProfileActionsEditor) {
        settingsProfileActionsEditor.placeholder = uiTekst('settings_profile_actions_editor_placeholder');
    }

    if (settingsProfileRouterEnabledLabel) {
        settingsProfileRouterEnabledLabel.textContent = uiTekst('settings_profile_router_enabled_label');
    }
    if (settingsProfileSuggestThresholdLabel) {
        settingsProfileSuggestThresholdLabel.textContent = uiTekst('settings_profile_router_suggest_label');
    }
    if (settingsProfileAutoThresholdLabel) {
        settingsProfileAutoThresholdLabel.textContent = uiTekst('settings_profile_router_auto_label');
    }
    if (settingsProfileRouterSaveBtn) {
        settingsProfileRouterSaveBtn.textContent = uiTekst('settings_profile_router_save_button');
        settingsProfileRouterSaveBtn.disabled = profielInteractieGeblokkeerd;
    }
    if (settingsProfileRouterEnabledToggle && document.activeElement !== settingsProfileRouterEnabledToggle) {
        settingsProfileRouterEnabledToggle.checked = appState.settingsProfileRouterEnabled;
        settingsProfileRouterEnabledToggle.disabled = profielInteractieGeblokkeerd;
    }
    if (settingsProfileSuggestThresholdInput && document.activeElement !== settingsProfileSuggestThresholdInput) {
        settingsProfileSuggestThresholdInput.value = String(appState.settingsProfileRouterSuggestThreshold);
        settingsProfileSuggestThresholdInput.disabled = profielInteractieGeblokkeerd;
    }
    if (settingsProfileAutoThresholdInput && document.activeElement !== settingsProfileAutoThresholdInput) {
        settingsProfileAutoThresholdInput.value = String(appState.settingsProfileRouterAutoThreshold);
        settingsProfileAutoThresholdInput.disabled = profielInteractieGeblokkeerd;
    }

    if (settingsProfileRouterState) {
        settingsProfileRouterState.textContent = settingsProfielRouterStatusTekst();
    }

    const geselecteerdConfig = appState.settingsProfileConfigs[appState.settingsProfileSelected]
        || appState.settingsProfileConfigs[appState.settingsProfile]
        || SETTINGS_PROFILE_BASE_CONFIGS.normal;
    renderSettingsProfielEffecten(appState.settingsProfileSelected, geselecteerdConfig);
    renderSettingsProfielActies(appState.settingsProfileSelected, profielInteractieGeblokkeerd);
    renderSettingsProfielActiesEditor(appState.settingsProfileSelected, {
        locked: profielInteractieGeblokkeerd,
    });

    settingsProfileKicker.textContent = uiTekst('settings_profile_kicker');
    const actiefProfielLabel = settingsProfielLabel(appState.settingsProfile);
    const geselecteerdProfielLabel = settingsProfielLabel(appState.settingsProfileSelected);
    if (appState.settingsProfileApplying) {
        settingsProfileState.textContent = uiTekst('settings_profile_applying');
    } else if (appState.settingsProfileLaunching) {
        settingsProfileState.textContent = uiTekst('settings_profile_state_launching', {
            profile: geselecteerdProfielLabel,
        });
    } else if (appState.settingsProfileSelected !== appState.settingsProfile) {
        settingsProfileState.textContent = uiTekst('settings_profile_state_preview', {
            selected: geselecteerdProfielLabel,
            active: actiefProfielLabel,
        });
    } else {
        settingsProfileState.textContent = uiTekst('settings_profile_state_current', {
            profile: actiefProfielLabel,
        });
    }

    if (settingsProfilePanel) {
        settingsProfilePanel.dataset.applying = appState.settingsProfileApplying ? 'true' : 'false';
        settingsProfilePanel.dataset.launching = appState.settingsProfileLaunching ? 'true' : 'false';
        settingsProfilePanel.dataset.routerSaving = appState.settingsProfileRouterSaving ? 'true' : 'false';
        if (appState.settingsProfileApplying || appState.settingsProfileLaunching || appState.settingsProfileRouterSaving) {
            settingsProfilePanel.dataset.applied = 'false';
        } else if (!Object.prototype.hasOwnProperty.call(settingsProfilePanel.dataset, 'applied')) {
            settingsProfilePanel.dataset.applied = 'false';
        }
    }
}

async function applySettingsProfiel(event, options = {}) {
    if (event && typeof event.preventDefault === 'function') {
        event.preventDefault();
    }

    if (!settingsProfileSelect || appState.settingsProfileApplying || appState.settingsProfileLaunching || appState.settingsProfileRouterSaving) {
        return false;
    }

    const opts = options && typeof options === 'object' ? options : {};
    const geforceerdProfiel = Object.prototype.hasOwnProperty.call(opts, 'forcedProfile')
        ? normaliseerSettingsProfielNaam(opts.forcedProfile)
        : '';
    const launchAfterApply = parseerBoolWaarde(opts.launchAfterApply, false);
    const silent = parseerBoolWaarde(opts.silent, false);

    const geselecteerdProfiel = geforceerdProfiel || normaliseerSettingsProfielNaam(settingsProfileSelect.value);
    const vorigProfiel = appState.settingsProfile;
    const vorigGeselecteerdProfiel = appState.settingsProfileSelected;

    appState.settingsProfileApplying = true;
    appState.settingsProfileSelected = geselecteerdProfiel;
    wisSettingsProfielHighlight();
    renderSettingsProfilePanel({
        profile: geselecteerdProfiel,
        selected: geselecteerdProfiel,
        applying: true,
    });
    setCommandStatus(uiTekst('settings_profile_applying'));

    try {
        const response = await fetchEchoApi('/api/instellingen', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                instellingen_profiel: geselecteerdProfiel,
                apply_profile: true,
            }),
        }, 9000);

        const data = await response.json().catch(() => ({
            status: 'error',
            message: uiTekst('invalid_server_response'),
        }));

        if (!response.ok || data.status !== 'success') {
            const message = String(data.message || '').trim() || uiTekst('settings_profile_apply_failed');
            throw new Error(message);
        }

        const actiefProfiel = normaliseerSettingsProfielNaam(data.settings_profile || geselecteerdProfiel);
        const payloadProfielen = extractSettingsProfielenUitPayload(data);
        const profielOpties = normaliseerSettingsProfielenLijst(
            payloadProfielen.length ? payloadProfielen : appState.settingsProfiles
        );
        const payloadProfielConfigs = extractSettingsProfielConfigsUitPayload(data);
        const profielConfigs = normaliseerSettingsProfielConfigs(
            Object.keys(payloadProfielConfigs).length ? payloadProfielConfigs : appState.settingsProfileConfigs
        );
        const payloadProfielActies = extractSettingsProfielActiesUitPayload(data);
        const profielActies = normaliseerSettingsProfielActiesData(
            Object.keys(payloadProfielActies).length ? payloadProfielActies : appState.settingsProfileActionsByProfile
        );
        const routerConfig = normaliseerSettingsProfileRouterConfig(data);

        appState.settingsProfileApplying = false;
        appState.settingsProfileSelected = actiefProfiel;
        appState.settingsProfileActionsByProfile = profielActies;
        appState.settingsProfileRouterEnabled = routerConfig.enabled;
        appState.settingsProfileRouterSuggestThreshold = routerConfig.suggestThreshold;
        appState.settingsProfileRouterAutoThreshold = routerConfig.autoThreshold;
        renderSettingsProfilePanel({
            profile: actiefProfiel,
            selected: actiefProfiel,
            profiles: profielOpties,
            profileConfigs: profielConfigs,
            profileActions: profielActies,
            profile_auto_router_enabled: routerConfig.enabled,
            profile_auto_router_suggest_threshold: routerConfig.suggestThreshold,
            profile_auto_router_auto_threshold: routerConfig.autoThreshold,
            applying: false,
        });
        markeerSettingsProfielToegepast();

        const profielLabel = settingsProfielLabel(actiefProfiel);
        const melding = uiTekst('settings_profile_apply_success', {
            profile: profielLabel,
        });
        if (!silent) {
            addMessage('ai', melding);
            setCommandStatus(melding);
            triggerHapticFeedback(45);
        }

        await loadSettings();
        if (launchAfterApply) {
            await startSettingsProfielWorkflowVoorProfiel(actiefProfiel);
        }
        void refreshDashboardTelemetry();
        return true;
    } catch (error) {
        appState.settingsProfileApplying = false;
        appState.settingsProfileSelected = vorigGeselecteerdProfiel;
        wisSettingsProfielHighlight();
        renderSettingsProfilePanel({
            profile: vorigProfiel,
            selected: vorigGeselecteerdProfiel,
            applying: false,
        });

        const rawMessage = error instanceof Error ? String(error.message || '').trim() : '';
        const melding = rawMessage || uiTekst('settings_profile_apply_failed');
        if (!silent) {
            addMessage('error', melding);
            setCommandStatus(melding);
            triggerHapticFeedback([90, 35, 90]);
        }
        return false;
    }
}

function normaliseerWebsiteAuditSnapshot(payload = {}) {
    const bron = payload && typeof payload === 'object' ? payload : {};
    const vorige = appState.websiteAuditSnapshot && typeof appState.websiteAuditSnapshot === 'object'
        ? appState.websiteAuditSnapshot
        : {};

    const parseIntSafe = (waarde, fallback = 0) => {
        const nummer = Number(waarde);
        if (!Number.isFinite(nummer)) {
            return fallback;
        }
        return Math.max(0, Math.round(nummer));
    };

    const severityBron = bron.severity_totals && typeof bron.severity_totals === 'object'
        ? bron.severity_totals
        : (vorige.severity_totals && typeof vorige.severity_totals === 'object' ? vorige.severity_totals : {});

    const findingsBron = Array.isArray(bron.findings_top)
        ? bron.findings_top
        : (Array.isArray(vorige.findings_top) ? vorige.findings_top : []);

    const remediationBron = Array.isArray(bron.remediation_top)
        ? bron.remediation_top
        : (Array.isArray(vorige.remediation_top) ? vorige.remediation_top : []);

    const logsBron = Array.isArray(bron.recent_logs)
        ? bron.recent_logs
        : (Array.isArray(vorige.recent_logs) ? vorige.recent_logs : []);

    const downloadPathsBron = bron.download_paths && typeof bron.download_paths === 'object'
        ? bron.download_paths
        : (vorige.download_paths && typeof vorige.download_paths === 'object' ? vorige.download_paths : {});

    return {
        ...vorige,
        running: parseerBoolWaarde(bron.running, parseerBoolWaarde(vorige.running, false)),
        state: String(bron.state || vorige.state || 'idle').trim().toLowerCase() || 'idle',
        scan_id: String(bron.scan_id || vorige.scan_id || '').trim().toLowerCase(),
        stage: String(bron.stage || vorige.stage || '').trim(),
        progress_percent: parseIntSafe(
            Object.prototype.hasOwnProperty.call(bron, 'progress_percent') ? bron.progress_percent : vorige.progress_percent,
            0
        ),
        profile: String(bron.profile || vorige.profile || 'standard').trim().toLowerCase() || 'standard',
        target_url: String(bron.target_url || vorige.target_url || '').trim(),
        target_host: String(bron.target_host || vorige.target_host || '').trim(),
        score: parseIntSafe(Object.prototype.hasOwnProperty.call(bron, 'score') ? bron.score : vorige.score, 0),
        grade: String(bron.grade || vorige.grade || '').trim(),
        exposure_level: String(bron.exposure_level || vorige.exposure_level || '').trim(),
        checks_total: parseIntSafe(Object.prototype.hasOwnProperty.call(bron, 'checks_total') ? bron.checks_total : vorige.checks_total, 0),
        checks_passed: parseIntSafe(Object.prototype.hasOwnProperty.call(bron, 'checks_passed') ? bron.checks_passed : vorige.checks_passed, 0),
        checks_warn: parseIntSafe(Object.prototype.hasOwnProperty.call(bron, 'checks_warn') ? bron.checks_warn : vorige.checks_warn, 0),
        checks_failed: parseIntSafe(Object.prototype.hasOwnProperty.call(bron, 'checks_failed') ? bron.checks_failed : vorige.checks_failed, 0),
        findings_total: parseIntSafe(Object.prototype.hasOwnProperty.call(bron, 'findings_total') ? bron.findings_total : vorige.findings_total, 0),
        findings_top: findingsBron
            .filter((item) => item && typeof item === 'object')
            .slice(0, 8)
            .map((item) => ({ ...item })),
        remediation_top: remediationBron
            .filter((item) => item && typeof item === 'object')
            .slice(0, 8)
            .map((item) => ({ ...item })),
        recent_logs: logsBron
            .filter((item) => item && typeof item === 'object')
            .slice(-25)
            .map((item) => ({
                message: String(item.message || '').trim(),
                at: Number(item.at || 0) || 0,
            }))
            .filter((item) => item.message),
        severity_totals: {
            critical: parseIntSafe(severityBron.critical, 0),
            high: parseIntSafe(severityBron.high, 0),
            medium: parseIntSafe(severityBron.medium, 0),
            low: parseIntSafe(severityBron.low, 0),
        },
        last_result: String(bron.last_result || vorige.last_result || '').trim(),
        last_error: String(bron.last_error || vorige.last_error || '').trim(),
        last_report_json: String(bron.last_report_json || vorige.last_report_json || '').trim(),
        last_report_markdown: String(bron.last_report_markdown || vorige.last_report_markdown || '').trim(),
        last_report_pdf: String(bron.last_report_pdf || vorige.last_report_pdf || '').trim(),
        pdf_available: parseerBoolWaarde(
            Object.prototype.hasOwnProperty.call(bron, 'pdf_available') ? bron.pdf_available : vorige.pdf_available,
            false
        ),
        download_paths: {
            json: String(downloadPathsBron.json || '').trim(),
            markdown: String(downloadPathsBron.markdown || '').trim(),
            pdf: String(downloadPathsBron.pdf || '').trim(),
        },
    };
}

function normaliseerWebsiteAuditScheduleSnapshot(payload = {}) {
    const bron = payload && typeof payload === 'object' ? payload : {};
    const vorige = appState.websiteAuditScheduleSnapshot && typeof appState.websiteAuditScheduleSnapshot === 'object'
        ? appState.websiteAuditScheduleSnapshot
        : {};

    const parseIntSafe = (waarde, fallback = 0, minimum = 0, maximum = 9999) => {
        const nummer = Number(waarde);
        if (!Number.isFinite(nummer)) {
            return fallback;
        }
        return Math.min(maximum, Math.max(minimum, Math.round(nummer)));
    };

    return {
        ...vorige,
        enabled: parseerBoolWaarde(bron.enabled, parseerBoolWaarde(vorige.enabled, false)),
        frequency: normaliseerWebsiteAuditFrequency(bron.frequency || vorige.frequency || 'daily'),
        scheduled_time: normaliseerWebsiteAuditTijd(bron.scheduled_time || vorige.scheduled_time || '04:30'),
        target_url: String(bron.target_url || vorige.target_url || '').trim(),
        profile: String(bron.profile || vorige.profile || 'standard').trim().toLowerCase() || 'standard',
        next_run_at: Number(bron.next_run_at || vorige.next_run_at || 0) || 0,
        next_run_label: String(bron.next_run_label || vorige.next_run_label || '').trim(),
        monitor_running: parseerBoolWaarde(bron.monitor_running, parseerBoolWaarde(vorige.monitor_running, false)),
        alert_score_drop: parseIntSafe(bron.alert_score_drop || vorige.alert_score_drop, 12, 0, 60),
        alert_on_critical: parseerBoolWaarde(bron.alert_on_critical, parseerBoolWaarde(vorige.alert_on_critical, true)),
        alert_webhook_configured: parseerBoolWaarde(
            bron.alert_webhook_configured,
            parseerBoolWaarde(vorige.alert_webhook_configured, false)
        ),
        alert_webhook: String(bron.alert_webhook || vorige.alert_webhook || '').trim(),
        last_alert_result: String(bron.last_alert_result || vorige.last_alert_result || '').trim(),
        last_alert_at: Number(bron.last_alert_at || vorige.last_alert_at || 0) || 0,
        last_completed_scan_id: String(bron.last_completed_scan_id || vorige.last_completed_scan_id || '').trim(),
        last_completed_score: parseIntSafe(bron.last_completed_score || vorige.last_completed_score, 0, 0, 100),
        updated_at: Number(bron.updated_at || vorige.updated_at || 0) || 0,
    };
}

function normaliseerWebsiteAuditSeverity(waarde) {
    const severity = String(waarde || '').trim().toLowerCase();
    if (severity === 'critical' || severity === 'high' || severity === 'medium' || severity === 'low') {
        return severity;
    }
    return 'low';
}

function websiteAuditFrequencyLabel(frequentie) {
    const sleutel = 'website_audit_frequency_' + normaliseerWebsiteAuditFrequency(frequentie);
    return uiTekst(sleutel);
}

function normaliseerWebsiteAuditDownloadFormaat(formaat) {
    const waarde = String(formaat || '').trim().toLowerCase();
    if (waarde === 'md' || waarde === 'markdown') {
        return 'markdown';
    }
    if (waarde === 'pdf') {
        return 'pdf';
    }
    return 'json';
}

function resolveWebsiteAuditDownloadPad(formaat, snapshot = appState.websiteAuditSnapshot) {
    const data = snapshot && typeof snapshot === 'object' ? snapshot : {};
    const norm = normaliseerWebsiteAuditDownloadFormaat(formaat);
    const paths = data.download_paths && typeof data.download_paths === 'object' ? data.download_paths : {};
    const explicietPad = String(paths[norm] || '').trim();
    if (explicietPad) {
        return explicietPad;
    }

    const scanId = String(data.scan_id || '').trim().toLowerCase();
    if (scanId) {
        return `/api/website-audit/report/${scanId}/download/${norm}`;
    }
    return `/api/website-audit/report/latest/download/${norm}`;
}

function resolveWebsiteAuditDownloadUrl(formaat, snapshot = appState.websiteAuditSnapshot) {
    const pad = resolveWebsiteAuditDownloadPad(formaat, snapshot);
    if (!pad) {
        return '';
    }

    if (pad.startsWith('http://') || pad.startsWith('https://')) {
        return pad;
    }

    const basis = normaliseerApiBaseUrl(appState.apiBaseUrl)
        || (isHttpPaginaContext() ? normaliseerApiBaseUrl(window.location.origin) : '');
    return combineerApiUrl(pad, basis);
}

function heeftWebsiteAuditRapport(snapshot = appState.websiteAuditSnapshot) {
    const data = snapshot && typeof snapshot === 'object' ? snapshot : {};
    return Boolean(
        data.scan_id
        || data.last_report_json
        || data.last_report_markdown
        || data.last_report_pdf
        || data.state === 'completed'
    );
}

function updateWebsiteAuditDownloadButtons(snapshot = appState.websiteAuditSnapshot) {
    const rapportBeschikbaar = heeftWebsiteAuditRapport(snapshot);
    if (websiteAuditDownloadJsonBtn) {
        websiteAuditDownloadJsonBtn.disabled = !rapportBeschikbaar;
    }
    if (websiteAuditDownloadMdBtn) {
        websiteAuditDownloadMdBtn.disabled = !rapportBeschikbaar;
    }
    if (websiteAuditDownloadPdfBtn) {
        const pdfMogelijk = rapportBeschikbaar && (parseerBoolWaarde(snapshot.pdf_available, false) || Boolean(snapshot.last_report_pdf));
        websiteAuditDownloadPdfBtn.disabled = !pdfMogelijk;
    }
}

function downloadWebsiteAuditReport(formaat) {
    const url = resolveWebsiteAuditDownloadUrl(formaat);
    if (!url) {
        setCommandStatus(uiTekst('website_audit_download_unavailable'));
        triggerHapticFeedback([90, 35, 90]);
        return false;
    }

    try {
        const link = document.createElement('a');
        link.href = url;
        link.rel = 'noopener';
        link.target = '_blank';
        link.style.display = 'none';
        document.body.appendChild(link);
        link.click();
        link.remove();

        setCommandStatus(uiTekst('website_audit_download_started', {
            format: normaliseerWebsiteAuditDownloadFormaat(formaat).toUpperCase(),
        }));
        triggerHapticFeedback(45);
        return true;
    } catch (_error) {
        setCommandStatus(uiTekst('website_audit_download_unavailable'));
        triggerHapticFeedback([90, 35, 90]);
        return false;
    }
}

function formatteerWebsiteAuditLogTijd(unixSeconden) {
    const waarde = Number(unixSeconden || 0);
    if (!Number.isFinite(waarde) || waarde <= 0) {
        return '';
    }

    try {
        const taal = isNederlandsActief() ? 'nl-NL' : 'en-US';
        return new Date(waarde * 1000).toLocaleTimeString(taal, {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
        });
    } catch (_error) {
        return '';
    }
}

function renderWebsiteAuditRecommendations(snapshot) {
    if (!websiteAuditRecommendations) {
        return;
    }

    websiteAuditRecommendations.innerHTML = '';
    const aanbevelingen = Array.isArray(snapshot.remediation_top) ? snapshot.remediation_top : [];

    if (!aanbevelingen.length) {
        const empty = document.createElement('p');
        empty.className = 'website-audit-list-empty';
        empty.textContent = uiTekst('website_audit_recommendations_empty');
        websiteAuditRecommendations.appendChild(empty);
        return;
    }

    aanbevelingen.slice(0, 3).forEach((item, index) => {
        const title = String(item.title || item.action || '').trim() || `Action ${index + 1}`;
        const rationale = String(item.rationale || item.reason || '').trim();
        const effort = String(item.effort || '').trim();

        const blok = document.createElement('article');
        blok.className = 'website-audit-recommendation';

        const titelEl = document.createElement('p');
        titelEl.className = 'website-audit-recommendation__title';
        titelEl.textContent = `${index + 1}. ${title}`;
        blok.appendChild(titelEl);

        if (rationale) {
            const detailEl = document.createElement('p');
            detailEl.textContent = rationale;
            blok.appendChild(detailEl);
        }

        if (effort) {
            const effortEl = document.createElement('p');
            effortEl.textContent = `Effort: ${effort}`;
            blok.appendChild(effortEl);
        }

        websiteAuditRecommendations.appendChild(blok);
    });
}

function renderWebsiteAuditLogs(snapshot) {
    if (!websiteAuditLogs) {
        return;
    }

    websiteAuditLogs.innerHTML = '';
    const logs = Array.isArray(snapshot.recent_logs) ? snapshot.recent_logs : [];

    if (!logs.length) {
        const empty = document.createElement('p');
        empty.className = 'website-audit-list-empty';
        empty.textContent = uiTekst('website_audit_logs_empty');
        websiteAuditLogs.appendChild(empty);
        return;
    }

    logs.slice(-8).reverse().forEach((item) => {
        const regel = document.createElement('article');
        regel.className = 'website-audit-log';

        const tijd = formatteerWebsiteAuditLogTijd(item.at);
        if (tijd) {
            const tijdEl = document.createElement('span');
            tijdEl.className = 'website-audit-log__time';
            tijdEl.textContent = `[${tijd}]`;
            regel.appendChild(tijdEl);
        }

        const tekstEl = document.createElement('span');
        tekstEl.textContent = String(item.message || '').trim();
        regel.appendChild(tekstEl);

        websiteAuditLogs.appendChild(regel);
    });
}

function renderWebsiteAuditFindings(snapshot) {
    if (!websiteAuditFindings) {
        return;
    }

    websiteAuditFindings.innerHTML = '';
    const findings = Array.isArray(snapshot.findings_top) ? snapshot.findings_top : [];

    if (!findings.length) {
        const empty = document.createElement('p');
        empty.className = 'website-audit-findings-empty';
        empty.textContent = uiTekst('website_audit_findings_empty');
        websiteAuditFindings.appendChild(empty);
        return;
    }

    findings.slice(0, 5).forEach((finding) => {
        const severity = normaliseerWebsiteAuditSeverity(finding.severity);
        const status = String(finding.status || '').trim().toUpperCase() || 'INFO';
        const title = String(finding.title || finding.check_id || 'Finding').trim();
        const detail = String(finding.detail || '').trim();
        const recommendation = String(finding.recommendation || '').trim();
        const category = String(finding.category || '').trim();

        const item = document.createElement('article');
        item.className = 'website-audit-finding';
        item.dataset.severity = severity;

        const titleEl = document.createElement('p');
        titleEl.className = 'website-audit-finding__title';
        titleEl.textContent = `${status} | ${severity.toUpperCase()}${category ? ` | ${category.toUpperCase()}` : ''} | ${title}`;
        item.appendChild(titleEl);

        if (detail) {
            const detailEl = document.createElement('p');
            detailEl.className = 'website-audit-finding__detail';
            detailEl.textContent = detail;
            item.appendChild(detailEl);
        }

        if (recommendation) {
            const recEl = document.createElement('p');
            recEl.className = 'website-audit-finding__recommendation';
            recEl.textContent = recommendation;
            item.appendChild(recEl);
        }

        websiteAuditFindings.appendChild(item);
    });
}

function renderWebsiteAuditSchedulePanel(payload = {}, options = {}) {
    const snapshot = normaliseerWebsiteAuditScheduleSnapshot(payload);
    appState.websiteAuditScheduleSnapshot = snapshot;

    const frequentieLabel = websiteAuditFrequencyLabel(snapshot.frequency);
    const volgende = String(snapshot.next_run_label || '').trim() || formatteerLocaleDatumTijd(snapshot.next_run_at) || '-';

    if (websiteAuditScheduleState) {
        if (!snapshot.enabled) {
            websiteAuditScheduleState.textContent = uiTekst('website_audit_schedule_state_off');
        } else if (!snapshot.target_url) {
            websiteAuditScheduleState.textContent = uiTekst('website_audit_schedule_state_no_target', {
                frequency: frequentieLabel,
                time: snapshot.scheduled_time,
            });
        } else {
            websiteAuditScheduleState.textContent = uiTekst('website_audit_schedule_state_on', {
                frequency: frequentieLabel,
                time: snapshot.scheduled_time,
                next: volgende,
            });
        }

        if (snapshot.last_alert_result) {
            websiteAuditScheduleState.textContent += ` | ${snapshot.last_alert_result}`;
        }
    }

    if (options.syncForm === false) {
        return;
    }

    const veiligZetWaarde = (element, waarde) => {
        if (!element || document.activeElement === element) {
            return;
        }
        const tekst = String(waarde || '');
        if (String(element.value || '') !== tekst) {
            element.value = tekst;
        }
    };

    veiligZetWaarde(websiteAuditFrequencySelect, snapshot.frequency);
    veiligZetWaarde(websiteAuditTimeInput, snapshot.scheduled_time);
    veiligZetWaarde(websiteAuditScheduleUrlInput, snapshot.target_url);
    veiligZetWaarde(websiteAuditScheduleProfileSelect, snapshot.profile);
    veiligZetWaarde(websiteAuditAlertDropInput, String(snapshot.alert_score_drop));

    if (websiteAuditScheduleEnabledToggle && document.activeElement !== websiteAuditScheduleEnabledToggle) {
        websiteAuditScheduleEnabledToggle.checked = snapshot.enabled;
    }
    if (websiteAuditAlertCriticalToggle && document.activeElement !== websiteAuditAlertCriticalToggle) {
        websiteAuditAlertCriticalToggle.checked = snapshot.alert_on_critical;
    }

    if (websiteAuditWebhookInput && snapshot.alert_webhook && document.activeElement !== websiteAuditWebhookInput) {
        websiteAuditWebhookInput.value = snapshot.alert_webhook;
    }
}

function renderWebsiteAuditPanel(payload = {}) {
    if (!websiteAuditState || !websiteAuditScore || !websiteAuditMeta) {
        return;
    }

    const snapshot = normaliseerWebsiteAuditSnapshot(payload);
    appState.websiteAuditSnapshot = snapshot;

    const progress = Math.max(0, Math.min(100, Number(snapshot.progress_percent || 0)));
    const stageLabel = snapshot.stage || tekstVoorTaal('working', 'bezig');
    const targetLabel = snapshot.target_host || snapshot.target_url || tekstVoorTaal('target website', 'doelwebsite');

    if (snapshot.running) {
        websiteAuditState.textContent = uiTekst('website_audit_running', {
            stage: stageLabel,
            progress: String(progress),
        });
    } else if (snapshot.state === 'completed') {
        websiteAuditState.textContent = snapshot.last_result || uiTekst('website_audit_completed', { target: targetLabel });
    } else if (snapshot.state === 'error') {
        websiteAuditState.textContent = uiTekst('website_audit_error', {
            message: snapshot.last_result || snapshot.last_error || '-',
        });
    } else {
        websiteAuditState.textContent = uiTekst('website_audit_idle');
    }

    if (websiteAuditProgressBar) {
        websiteAuditProgressBar.style.width = `${progress}%`;
    }

    const heeftResultaat = snapshot.checks_total > 0 || snapshot.state === 'completed' || snapshot.state === 'error';
    if (heeftResultaat) {
        websiteAuditScore.textContent = uiTekst('website_audit_score_line', {
            score: String(snapshot.score || 0),
            grade: snapshot.grade || '--',
        });
    } else {
        websiteAuditScore.textContent = uiTekst('website_audit_score_pending');
    }

    websiteAuditMeta.textContent = uiTekst('website_audit_meta_line', {
        pass: String(snapshot.checks_passed || 0),
        warn: String(snapshot.checks_warn || 0),
        fail: String(snapshot.checks_failed || 0),
    });

    if (websiteAuditStartBtn) {
        websiteAuditStartBtn.disabled = snapshot.running;
    }
    if (websiteAuditProfileSelect) {
        websiteAuditProfileSelect.disabled = snapshot.running;
        if (websiteAuditProfileSelect.value !== snapshot.profile) {
            websiteAuditProfileSelect.value = snapshot.profile;
        }
    }

    if (websiteAuditUrlInput && !String(websiteAuditUrlInput.value || '').trim() && snapshot.target_url) {
        websiteAuditUrlInput.value = snapshot.target_url;
    }

    if (websiteAuditScheduleSaveBtn) {
        websiteAuditScheduleSaveBtn.disabled = snapshot.running;
    }

    updateWebsiteAuditDownloadButtons(snapshot);
    renderWebsiteAuditFindings(snapshot);
    renderWebsiteAuditRecommendations(snapshot);
    renderWebsiteAuditLogs(snapshot);
}

function saveLatestScreenshotToPhone(options = {}) {
    const snapshot = normaliseerScreenshotArtifact(appState.latestScreenshotSnapshot);
    if (!snapshot.available) {
        setCommandStatus(uiTekst('mobile_screenshot_save_missing'));
        triggerHapticFeedback([90, 35, 90]);
        return false;
    }

    const downloadUrl = resolveScreenshotDownloadUrl(snapshot);
    if (!downloadUrl) {
        setCommandStatus(uiTekst('mobile_screenshot_save_missing'));
        triggerHapticFeedback([90, 35, 90]);
        return false;
    }

    try {
        const link = document.createElement('a');
        link.href = downloadUrl;
        link.setAttribute('download', snapshot.filename || 'echo-screenshot.png');
        link.rel = 'noopener';
        link.style.display = 'none';
        document.body.appendChild(link);
        link.click();
        link.remove();

        setCommandStatus(uiTekst('mobile_screenshot_save_success'));
        triggerHapticFeedback(60);
        return true;
    } catch (_error) {
        if (options.allowOpenFallback) {
            try {
                window.open(downloadUrl, '_blank', 'noopener');
            } catch (_innerError) {
                // Ignore fallback open errors.
            }
        }
        setCommandStatus(uiTekst('mobile_screenshot_save_failed'));
        triggerHapticFeedback([90, 35, 90]);
        return false;
    }
}

function openLatestScreenshotInBrowser() {
    const snapshot = normaliseerScreenshotArtifact(appState.latestScreenshotSnapshot);
    if (!snapshot.available) {
        setCommandStatus(uiTekst('mobile_screenshot_open_missing'));
        triggerHapticFeedback([90, 35, 90]);
        return;
    }

    const downloadUrl = resolveScreenshotDownloadUrl(snapshot);
    if (!downloadUrl) {
        setCommandStatus(uiTekst('mobile_screenshot_open_missing'));
        triggerHapticFeedback([90, 35, 90]);
        return;
    }

    window.open(downloadUrl, '_blank', 'noopener');
    triggerHapticFeedback(45);
}

function maybeAutoSaveScreenshotToPhone(snapshotPayload) {
    const snapshot = normaliseerScreenshotArtifact(snapshotPayload);
    if (!snapshot.available) {
        return false;
    }

    renderLatestScreenshotPanel(snapshot);
    if (!isMobileDeviceContext()) {
        return false;
    }

    return saveLatestScreenshotToPhone({ allowOpenFallback: true });
}

function uniekeCommandoLijst(items) {
    const gezien = new Set();
    const resultaat = [];

    items.forEach((item) => {
        const tekst = String(item || '').trim();
        if (!tekst) {
            return;
        }

        const norm = normalizeText(tekst);
        if (!norm || gezien.has(norm)) {
            return;
        }

        gezien.add(norm);
        resultaat.push(tekst);
    });

    return resultaat;
}

function zetOverviewChip(chip, tekst, state = 'idle') {
    if (!chip) {
        return;
    }

    setTextContentIfChanged(chip, String(tekst || '').trim());
    if (String(chip.dataset.state || '') !== String(state || '')) {
        chip.dataset.state = state;
    }
}

function renderCommandCenterStatus() {
    const pendingActief = Boolean(pendingConfirm && !pendingConfirm.classList.contains('is-hidden'));
    const micStateKey = appState.micMuted
        ? 'overview_chip_mic_muted'
        : (appState.listeningActive ? 'overview_chip_mic_listening' : 'overview_chip_mic_ready');
    const micChipState = appState.micMuted ? 'warn' : (appState.listeningActive ? 'active' : 'idle');

    const voiceStateKey = appState.deafenEnabled
        ? 'overview_chip_voice_deafened'
        : (appState.speakingActive ? 'overview_chip_voice_speaking' : 'overview_chip_voice_ready');
    const voiceChipState = appState.deafenEnabled ? 'warn' : (appState.speakingActive ? 'active' : 'idle');

    const cameraActief = Boolean(appState.cameraStream);
    const cameraStateKey = cameraActief ? 'overview_chip_camera_on' : 'overview_chip_camera_off';

    let streamStateKey = 'overview_chip_stream_idle';
    if (appState.streamLive && appState.streamRecording) {
        streamStateKey = 'overview_chip_stream_live_recording';
    } else if (appState.streamLive) {
        streamStateKey = 'overview_chip_stream_live';
    } else if (appState.streamRecording) {
        streamStateKey = 'overview_chip_stream_recording';
    }

    zetOverviewChip(overviewMicChip, uiTekst(micStateKey), micChipState);
    zetOverviewChip(overviewVoiceChip, uiTekst(voiceStateKey), voiceChipState);
    zetOverviewChip(overviewCameraChip, uiTekst(cameraStateKey), cameraActief ? 'active' : 'idle');
    zetOverviewChip(
        overviewPendingChip,
        uiTekst(pendingActief ? 'overview_chip_pending_on' : 'overview_chip_pending_off'),
        pendingActief ? 'warn' : 'idle'
    );
    zetOverviewChip(overviewStreamChip, uiTekst(streamStateKey), streamStateKey === 'overview_chip_stream_idle' ? 'idle' : 'active');
}

function syncStreamStatusUitContext(commandText, serverMessage = '') {
    const combined = normalizeText(`${String(commandText || '')} ${String(serverMessage || '')}`);
    if (!combined) {
        return;
    }

    if (
        combined.includes('stream mode off')
        || combined.includes('stream-modus uit')
        || combined.includes('stream mode disabled')
    ) {
        appState.streamLive = false;
        appState.streamRecording = false;
    }

    if (
        combined.includes('stream recording stop')
        || combined.includes('stop recording')
        || combined.includes('recording stop')
        || combined.includes('opname stoppen')
    ) {
        appState.streamRecording = false;
    }

    if (
        combined.includes('stream stop')
        || combined.includes('stop stream')
        || combined.includes('stop live')
        || combined.includes('stream stoppen')
    ) {
        appState.streamLive = false;
    }

    if (
        combined.includes('stream recording start')
        || combined.includes('start recording')
        || combined.includes('recording start')
        || combined.includes('opname starten')
    ) {
        appState.streamRecording = true;
    }

    if (
        combined.includes('stream start')
        || combined.includes('go live')
        || combined.includes('ga live')
        || combined.includes('stream starten')
    ) {
        appState.streamLive = true;
    }

    renderCommandCenterStatus();
}

function actieFilterTekstVoorKnop(button) {
    const label = String(button && button.textContent ? button.textContent : '').trim();
    const commando = String(button && button.dataset ? (button.dataset.command || '') : '').trim();
    const fillCommand = String(button && button.dataset ? (button.dataset.fillCommand || '') : '').trim();
    return normalizeText(`${label} ${commando} ${fillCommand}`);
}

function applyActionFilter() {
    if (!actionFilterInput) {
        return;
    }

    const query = String(actionFilterInput.value || '').trim();
    appState.actionFilterQuery = query;
    const queryNorm = normalizeText(query);

    const collapsibleBlokken = Array.from(document.querySelectorAll('.panel-block.is-collapsible'));
    if (queryNorm) {
        collapsibleBlokken.forEach((blok) => {
            if (blok.classList.contains('is-collapsed')) {
                blok.dataset.filterExpanded = '1';
                setPanelIngeklapt(blok, false, { persist: false });
            }
        });
    } else {
        const opslag = leesPanelCollapseOpslag();
        collapsibleBlokken.forEach((blok) => {
            if (blok.dataset.filterExpanded !== '1') {
                return;
            }

            delete blok.dataset.filterExpanded;
            const sleutel = String(blok.dataset.panelKey || '').trim();
            const opgeslagenWaarde = sleutel ? opslag[sleutel] : undefined;
            const heeftOpgeslagenWaarde = typeof opgeslagenWaarde === 'boolean';
            const gewensteInklapStatus = heeftOpgeslagenWaarde ? opgeslagenWaarde : isStandaardIngeklapt(blok);
            setPanelIngeklapt(blok, gewensteInklapStatus, { persist: false });
        });
    }

    let zichtbaar = 0;
    let verborgen = 0;
    const actieKnoppen = Array.from(document.querySelectorAll(ACTION_FILTER_BUTTON_SELECTOR));

    actieKnoppen.forEach((button) => {
        const filterTekst = actieFilterTekstVoorKnop(button);
        const zichtbaarNu = !queryNorm || filterTekst.includes(queryNorm);
        button.classList.toggle('is-filter-hidden', !zichtbaarNu);
        if (zichtbaarNu) {
            zichtbaar += 1;
        } else {
            verborgen += 1;
        }
    });

    const panelBlokken = Array.from(document.querySelectorAll('.hud-panel .panel-block'));
    panelBlokken.forEach((blok) => {
        if (blok.id === 'commandCenterPanel') {
            return;
        }

        const knopElementen = Array.from(blok.querySelectorAll(ACTION_FILTER_BUTTON_SELECTOR));
        if (!knopElementen.length) {
            blok.classList.remove('is-filter-empty');
            return;
        }

        const heeftZichtbaar = knopElementen.some((element) => !element.classList.contains('is-filter-hidden'));
        blok.classList.toggle('is-filter-empty', Boolean(queryNorm) && !heeftZichtbaar);
    });

    if (actionFilterHint) {
        actionFilterHint.textContent = queryNorm
            ? uiTekst('overview_filter_active', { visible: String(zichtbaar), hidden: String(verborgen) })
            : uiTekst('overview_filter_hint');
    }
}

function leesPanelCollapseOpslag() {
    try {
        const raw = localStorage.getItem(PANEL_COLLAPSE_STORAGE_KEY);
        if (!raw) {
            return {};
        }
        const parsed = JSON.parse(raw);
        return parsed && typeof parsed === 'object' ? parsed : {};
    } catch (_error) {
        return {};
    }
}

function schrijfPanelCollapseOpslag(waarde) {
    try {
        localStorage.setItem(PANEL_COLLAPSE_STORAGE_KEY, JSON.stringify(waarde));
    } catch (_error) {
        // Ignore storage errors (private mode, quota).
    }
}

function panelSleutelVoorBlok(blok, index) {
    const metId = String(blok.id || '').trim();
    if (metId) {
        return metId;
    }

    const kicker = blok.querySelector('.panel-kicker');
    const kickerSleutel = normalizeText(kicker ? kicker.textContent : '').replace(/\s+/g, '-').slice(0, 36);
    return kickerSleutel ? `panel-${kickerSleutel}` : `panel-${index + 1}`;
}

function isStandaardIngeklapt(blok) {
    return STANDAARD_INGEKLAPTE_PANEL_IDS.includes(String(blok.id || '').trim());
}

function setPanelIngeklapt(blok, ingeklapt, opties = {}) {
    const collapsed = Boolean(ingeklapt);
    blok.classList.toggle('is-collapsed', collapsed);

    const toggle = blok.querySelector('.panel-collapse-toggle');
    if (toggle) {
        toggle.textContent = collapsed ? '+' : '-';
        toggle.setAttribute('aria-expanded', String(!collapsed));
        toggle.setAttribute('title', uiTekst(collapsed ? 'panel_expand' : 'panel_collapse'));
        toggle.setAttribute('aria-label', uiTekst(collapsed ? 'panel_expand' : 'panel_collapse'));
    }

    if (opties.persist !== false) {
        const opslag = leesPanelCollapseOpslag();
        const sleutel = String(blok.dataset.panelKey || '').trim();
        if (sleutel) {
            opslag[sleutel] = collapsed;
            schrijfPanelCollapseOpslag(opslag);
        }
    }
}

function updatePanelCollapseToggleLabels() {
    const blokken = Array.from(document.querySelectorAll('.panel-block.is-collapsible'));
    blokken.forEach((blok) => {
        const isCollapsed = blok.classList.contains('is-collapsed');
        const toggle = blok.querySelector('.panel-collapse-toggle');
        if (!toggle) {
            return;
        }
        toggle.setAttribute('title', uiTekst(isCollapsed ? 'panel_expand' : 'panel_collapse'));
        toggle.setAttribute('aria-label', uiTekst(isCollapsed ? 'panel_expand' : 'panel_collapse'));
    });
}

function initPanelCollapseControls() {
    const blokken = Array.from(document.querySelectorAll('.hud-panel .panel-block'));
    const opslag = leesPanelCollapseOpslag();

    blokken.forEach((blok, index) => {
        if (blok.dataset.collapseReady === '1') {
            return;
        }

        if (blok.id === 'commandCenterPanel' || blok.id === 'pendingConfirm' || blok.classList.contains('aux-actions')) {
            return;
        }

        const kicker = blok.querySelector('.panel-kicker');
        if (!kicker) {
            return;
        }

        const sleutel = panelSleutelVoorBlok(blok, index);
        blok.dataset.panelKey = sleutel;
        blok.dataset.collapseReady = '1';
        blok.classList.add('is-collapsible');

        const toggle = document.createElement('button');
        toggle.type = 'button';
        toggle.className = 'panel-collapse-toggle';
        toggle.addEventListener('click', () => {
            const nieuweState = !blok.classList.contains('is-collapsed');
            setPanelIngeklapt(blok, nieuweState, { persist: true });
            renderCommandCenterStatus();
        });
        blok.appendChild(toggle);

        const opgeslagenWaarde = opslag[sleutel];
        const heeftOpgeslagenWaarde = typeof opgeslagenWaarde === 'boolean';
        const startIngeklapt = heeftOpgeslagenWaarde ? opgeslagenWaarde : isStandaardIngeklapt(blok);
        setPanelIngeklapt(blok, startIngeklapt, { persist: false });
    });

    updatePanelCollapseToggleLabels();
}

function verzamelPaneelCommandoSuggesties() {
    const knoppen = [...quickButtons, ...routineButtons];
    const suggesties = [];

    knoppen.forEach((button) => {
        const command = String(button && button.dataset ? (button.dataset.command || '') : '').trim();
        if (command) {
            suggesties.push(command);
        }

        const fillCommand = String(button && button.dataset ? (button.dataset.fillCommand || '') : '').trim();
        if (fillCommand) {
            suggesties.push(fillCommand + '...');
        }
    });

    return uniekeCommandoLijst(suggesties);
}

function scoreSuggestie(zoekNorm, suggestieTekst) {
    const suggestieNorm = normalizeText(suggestieTekst);
    if (!zoekNorm) {
        return 0;
    }

    if (suggestieNorm === zoekNorm) {
        return 120;
    }
    if (suggestieNorm.startsWith(zoekNorm)) {
        return 90;
    }
    if (suggestieNorm.includes(zoekNorm)) {
        return 50;
    }
    return -1;
}

function buildCommandSuggestions(invoer) {
    const query = String(invoer || '').trim();
    if (!query) {
        return [];
    }

    const queryNorm = normalizeText(query).replace(/^\//, '');
    if (!queryNorm) {
        return [];
    }

    const bronnen = uniekeCommandoLijst([
        ...LOCAL_SLASH_SUGGESTIONS,
        ...appState.commandHistory,
        ...verzamelPaneelCommandoSuggesties(),
    ]);

    const ranked = bronnen
        .map((suggestie) => ({
            text: suggestie,
            score: scoreSuggestie(queryNorm, suggestie),
        }))
        .filter((item) => item.score >= 0)
        .sort((a, b) => {
            if (b.score !== a.score) {
                return b.score - a.score;
            }
            return a.text.length - b.text.length;
        })
        .slice(0, MAX_COMMAND_SUGGESTIONS);

    return ranked.map((item) => item.text);
}

function renderCommandSuggestions(suggesties, options = {}) {
    if (!commandSuggestions) {
        return;
    }

    const lijst = Array.isArray(suggesties) ? suggesties : [];
    appState.visibleCommandSuggestions = lijst;

    if (!lijst.length) {
        appState.selectedSuggestionIndex = -1;
        commandSuggestions.innerHTML = '';
        if (options.showEmpty) {
            const empty = document.createElement('p');
            empty.className = 'command-suggestions-empty';
            empty.textContent = uiTekst('command_suggestions_empty');
            commandSuggestions.appendChild(empty);
        }
        return;
    }

    if (appState.selectedSuggestionIndex >= lijst.length) {
        appState.selectedSuggestionIndex = 0;
    }

    commandSuggestions.innerHTML = '';

    lijst.forEach((suggestie, index) => {
        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'command-suggestion';
        if (index === appState.selectedSuggestionIndex) {
            button.classList.add('is-active');
        }
        button.textContent = suggestie;
        button.title = suggestie;
        button.addEventListener('click', () => {
            setCommandDraft(suggestie);
            appState.selectedSuggestionIndex = index;
            renderCommandSuggestions(lijst);
        });
        commandSuggestions.appendChild(button);
    });
}

function refreshCommandSuggestionsFromInput() {
    const waarde = String(commandInput ? commandInput.value : '').trim();
    if (!waarde) {
        renderCommandSuggestions([]);
        return;
    }

    const suggesties = buildCommandSuggestions(waarde);
    appState.selectedSuggestionIndex = suggesties.length ? 0 : -1;
    renderCommandSuggestions(suggesties, { showEmpty: waarde.startsWith('/') });
}

function kiesActieveSuggestie() {
    const lijst = appState.visibleCommandSuggestions;
    if (!Array.isArray(lijst) || !lijst.length) {
        return false;
    }

    const index = appState.selectedSuggestionIndex >= 0 ? appState.selectedSuggestionIndex : 0;
    const gekozen = String(lijst[index] || '').trim();
    if (!gekozen) {
        return false;
    }

    setCommandDraft(gekozen);
    refreshCommandSuggestionsFromInput();
    return true;
}

function navigeerSuggesties(richting) {
    const lijst = appState.visibleCommandSuggestions;
    if (!Array.isArray(lijst) || !lijst.length) {
        return false;
    }

    if (appState.selectedSuggestionIndex < 0) {
        appState.selectedSuggestionIndex = 0;
    } else {
        const volgende = appState.selectedSuggestionIndex + richting;
        if (volgende < 0) {
            appState.selectedSuggestionIndex = lijst.length - 1;
        } else if (volgende >= lijst.length) {
            appState.selectedSuggestionIndex = 0;
        } else {
            appState.selectedSuggestionIndex = volgende;
        }
    }

    renderCommandSuggestions(lijst);
    return true;
}

function hideCommandSuggestions() {
    renderCommandSuggestions([]);
}

async function handelLokaleSnelkoppelingAf(commandText, source = 'text') {
    const commando = String(commandText || '').trim();
    if (!commando.startsWith('/')) {
        return false;
    }

    if (source !== 'system') {
        addMessage('user', commando);
    }

    const inhoud = commando.slice(1).trim().toLowerCase();

    if (inhoud === 'help') {
        const melding = uiTekst('shortcut_help_text');
        addMessage('ai', melding);
        setCommandStatus(melding);
        const gesproken = await speakText(melding, { profile: 'status' });
        if (!gesproken) {
            pulseSpeaking(900);
        }
        return true;
    }

    if (inhoud === 'scanqr') {
        await voerQrScanUit();
        return true;
    }

    if (inhoud === 'mood') {
        await voerMoodCheckUit();
        return true;
    }

    if (inhoud === 'golive') {
        await sendCommand('stream start', 'system');
        return true;
    }

    if (inhoud === 'endlive') {
        await sendCommand('stream stop', 'system');
        return true;
    }

    if (inhoud === 'record on') {
        await sendCommand('stream recording start', 'system');
        return true;
    }

    if (inhoud === 'record off') {
        await sendCommand('stream recording stop', 'system');
        return true;
    }

    if (inhoud === 'scene live') {
        await sendCommand('stream scene live', 'system');
        return true;
    }

    if (inhoud === 'scene brb') {
        await sendCommand('stream scene brb', 'system');
        return true;
    }

    if (inhoud === 'scene game') {
        await sendCommand('stream scene game', 'system');
        return true;
    }

    if (inhoud === 'marker') {
        await sendCommand('stream marker', 'system');
        return true;
    }

    if (inhoud === 'stream on') {
        await sendCommand('stream mode on', 'system');
        return true;
    }

    if (inhoud === 'stream off') {
        await sendCommand('stream mode off', 'system');
        return true;
    }

    if (inhoud === 'stream help') {
        await sendCommand('stream help', 'system');
        return true;
    }

    if (inhoud === 'audit status') {
        await sendCommand('website audit status', 'system');
        return true;
    }

    if (inhoud === 'audit report') {
        await sendCommand('website audit report latest', 'system');
        return true;
    }

    if (inhoud === 'audit schedule') {
        await sendCommand('website audit schedule status', 'system');
        return true;
    }

    if (inhoud === 'mute') {
        setMicMuted(true);
        return true;
    }

    if (inhoud === 'unmute') {
        setMicMuted(false);
        return true;
    }

    if (inhoud === 'deafen') {
        setDeafenEnabled(true);
        return true;
    }

    if (inhoud === 'undeafen') {
        setDeafenEnabled(false);
        return true;
    }

    if (inhoud === 'camera on') {
        await voerCameraTaakUit(async () => {
            const gestart = await startCameraStream();
            if (gestart) {
                triggerHapticFeedback(40);
            }
            return gestart;
        });
        return true;
    }

    if (inhoud === 'camera off') {
        stopCameraStream();
        zetCameraInsightTekst(uiTekst('camera_insight_idle'));
        setCommandStatus(uiTekst('camera_state_off'));
        renderCameraPanel();
        triggerHapticFeedback(30);
        return true;
    }

    if (inhoud === 'clear') {
        clearFeed();
        setCommandStatus(uiTekst('feed_cleared'));
        triggerHapticFeedback(35);
        return true;
    }

    if (inhoud === 'lang') {
        await toggleAppLanguage();
        return true;
    }

    const onbekend = uiTekst('shortcut_unknown');
    addMessage('error', onbekend);
    setCommandStatus(onbekend);
    triggerHapticFeedback([80, 28, 80]);
    return true;
}

function cameraIsBeschikbaar() {
    return Boolean(navigator.mediaDevices && typeof navigator.mediaDevices.getUserMedia === 'function');
}

function qrDetectieBeschikbaar() {
    return typeof window.BarcodeDetector === 'function';
}

function gezichtDetectieBeschikbaar() {
    return typeof window.FaceDetector === 'function';
}

function zetCameraInsightTekst(tekst) {
    if (cameraInsight) {
        cameraInsight.textContent = String(tekst || '').trim();
    }
}

function zetCameraOverlayTekst(tekst) {
    if (cameraPreviewOverlay) {
        cameraPreviewOverlay.textContent = String(tekst || '').trim();
    }
}

function renderCameraPanel() {
    const cameraActief = Boolean(appState.cameraStream);
    const cameraBeschikbaar = cameraIsBeschikbaar();
    const previewShell = cameraPreview ? cameraPreview.closest('.camera-preview-shell') : null;

    if (previewShell) {
        previewShell.classList.toggle('is-live', cameraActief);
    }

    if (cameraState) {
        if (!cameraBeschikbaar) {
            cameraState.textContent = uiTekst('camera_state_unavailable');
        } else if (cameraActief) {
            cameraState.textContent = uiTekst('camera_state_ready');
        } else if (appState.cameraPermission === 'denied') {
            cameraState.textContent = uiTekst('camera_state_denied');
        } else if (appState.cameraBusy) {
            cameraState.textContent = uiTekst('camera_busy');
        } else {
            cameraState.textContent = uiTekst('camera_state_off');
        }
    }

    if (!cameraActief) {
        if (!cameraBeschikbaar) {
            zetCameraOverlayTekst(uiTekst('camera_state_unavailable'));
        } else if (appState.cameraPermission === 'denied') {
            zetCameraOverlayTekst(uiTekst('camera_state_denied'));
        } else if (appState.cameraBusy) {
            zetCameraOverlayTekst(uiTekst('camera_busy'));
        } else {
            zetCameraOverlayTekst(uiTekst('camera_state_off'));
        }
    } else if (appState.cameraBusy) {
        zetCameraOverlayTekst(uiTekst('camera_busy'));
    } else {
        zetCameraOverlayTekst(uiTekst('camera_state_ready'));
    }

    if (cameraStartBtn) {
        cameraStartBtn.disabled = !cameraBeschikbaar || cameraActief || appState.cameraBusy;
    }
    if (cameraStopBtn) {
        cameraStopBtn.disabled = !cameraActief || appState.cameraBusy;
    }
    if (cameraScanQrBtn) {
        cameraScanQrBtn.disabled = !cameraBeschikbaar || appState.cameraBusy;
    }
    if (cameraMoodBtn) {
        cameraMoodBtn.disabled = !cameraBeschikbaar || appState.cameraBusy;
    }
    if (cameraMuteBtn) {
        cameraMuteBtn.disabled = appState.cameraBusy;
        cameraMuteBtn.textContent = appState.micMuted
            ? uiTekst('camera_unmute_button')
            : uiTekst('camera_mute_button');
    }
    if (cameraDeafenBtn) {
        cameraDeafenBtn.disabled = appState.cameraBusy;
        cameraDeafenBtn.textContent = appState.deafenEnabled
            ? uiTekst('camera_undeafen_button')
            : uiTekst('camera_deafen_button');
    }

    if (cameraInsight && !String(cameraInsight.textContent || '').trim()) {
        cameraInsight.textContent = uiTekst('camera_insight_idle');
    }

    renderCommandCenterStatus();
}

function setMicMuted(actief, opties = {}) {
    const volgend = Boolean(actief);
    if (volgend === appState.micMuted) {
        renderCameraPanel();
        return;
    }

    appState.micMuted = volgend;

    if (volgend) {
        appState.listeningWanted = false;
        stopRecognition();
        setListening(false);
    }

    const melding = uiTekst(volgend ? 'camera_mic_muted' : 'camera_mic_unmuted');
    setCommandStatus(melding);
    zetCameraInsightTekst(melding);
    if (opties.feed !== false) {
        addMessage('ai', melding);
    }
    triggerHapticFeedback(volgend ? [65, 28, 65] : 45);
    updateSpeechButtonLabel();
    renderCameraPanel();
}

function setDeafenEnabled(actief, opties = {}) {
    const volgend = Boolean(actief);
    if (volgend === appState.deafenEnabled) {
        renderCameraPanel();
        return;
    }

    appState.deafenEnabled = volgend;
    appState.voiceOutputEnabled = volgend ? false : appState.voiceOutputUserEnabled;

    if (volgend) {
        stopActiveSpeechPlayback();
    }

    const melding = uiTekst(volgend ? 'camera_deafen_enabled' : 'camera_deafen_disabled');
    setCommandStatus(melding);
    zetCameraInsightTekst(melding);
    if (opties.feed !== false) {
        addMessage('ai', melding);
    }
    triggerHapticFeedback(volgend ? [65, 28, 65] : 45);
    updateIdleVoiceStatus();
    renderCameraPanel();
}

async function voerCameraTaakUit(taak) {
    if (appState.cameraBusy) {
        return false;
    }

    appState.cameraBusy = true;
    renderCameraPanel();

    try {
        return await taak();
    } finally {
        appState.cameraBusy = false;
        renderCameraPanel();
    }
}

function stopCameraStream() {
    if (appState.cameraStream) {
        appState.cameraStream.getTracks().forEach((track) => {
            try {
                track.stop();
            } catch (_error) {
                // Ignore individual track stop errors.
            }
        });
    }

    appState.cameraStream = null;
    if (cameraPreview) {
        try {
            cameraPreview.pause();
        } catch (_error) {
            // Ignore pause errors.
        }
        cameraPreview.srcObject = null;
    }
}

async function startCameraStream() {
    if (!cameraIsBeschikbaar()) {
        const melding = uiTekst('camera_state_unavailable');
        setCommandStatus(melding);
        zetCameraInsightTekst(melding);
        renderCameraPanel();
        return false;
    }

    if (appState.cameraStream) {
        renderCameraPanel();
        return true;
    }

    if (cameraState) {
        cameraState.textContent = uiTekst('camera_state_requesting');
    }
    zetCameraOverlayTekst(uiTekst('camera_state_requesting'));

    try {
        const stream = await navigator.mediaDevices.getUserMedia({
            audio: false,
            video: {
                facingMode: 'user',
                width: { ideal: 960 },
                height: { ideal: 540 },
            },
        });

        appState.cameraStream = stream;
        appState.cameraPermission = 'granted';

        if (cameraPreview) {
            cameraPreview.srcObject = stream;
            try {
                await cameraPreview.play();
            } catch (_error) {
                // Some browsers need a next gesture to start playback.
            }
        }

        if (!cameraInsight || !String(cameraInsight.textContent || '').trim()) {
            zetCameraInsightTekst(uiTekst('camera_insight_idle'));
        }

        setCommandStatus(uiTekst('camera_state_ready'));
        renderCameraPanel();
        return true;
    } catch (error) {
        const foutcode = error && typeof error === 'object' && 'name' in error ? String(error.name || '') : '';
        appState.cameraPermission = foutcode === 'NotAllowedError' ? 'denied' : 'unknown';

        const melding = appState.cameraPermission === 'denied'
            ? uiTekst('camera_state_denied')
            : uiTekst('camera_state_unavailable');
        setCommandStatus(melding);
        zetCameraInsightTekst(melding);
        renderCameraPanel();
        triggerHapticFeedback([90, 35, 90]);
        return false;
    }
}

async function wachtOpCameraFrame(timeoutMs = 2000) {
    if (!cameraPreview) {
        return false;
    }

    const startedAt = Date.now();
    while ((Date.now() - startedAt) < timeoutMs) {
        if (cameraPreview.readyState >= HTMLMediaElement.HAVE_CURRENT_DATA && cameraPreview.videoWidth > 0 && cameraPreview.videoHeight > 0) {
            return true;
        }
        await sleep(90);
    }
    return false;
}

function veiligeHttpUrlUitTekst(waarde) {
    const tekst = String(waarde || '').trim();
    if (!tekst) {
        return '';
    }

    try {
        const parsed = new URL(tekst);
        if (parsed.protocol === 'http:' || parsed.protocol === 'https:') {
            return parsed.toString();
        }
    } catch (_error) {
        return '';
    }

    return '';
}

async function detecteerQrWaardeUitPreview() {
    if (!cameraPreview || !qrDetectieBeschikbaar()) {
        return '';
    }

    let detector = null;
    try {
        detector = new window.BarcodeDetector({ formats: ['qr_code'] });
    } catch (_error) {
        try {
            detector = new window.BarcodeDetector();
        } catch (_innerError) {
            return '';
        }
    }

    for (let poging = 0; poging < CAMERA_SCAN_ATTEMPTS; poging += 1) {
        try {
            const resultaten = await detector.detect(cameraPreview);
            if (Array.isArray(resultaten) && resultaten.length) {
                const waarde = String(resultaten[0].rawValue || '').trim();
                if (waarde) {
                    return waarde;
                }
            }
        } catch (_error) {
            // Keep trying within the retry window.
        }

        await sleep(CAMERA_SCAN_INTERVAL_MS);
    }

    return '';
}

function puntenVoorLandmark(landmarks, typeNaam) {
    if (!Array.isArray(landmarks)) {
        return [];
    }

    const match = landmarks.find((item) => {
        const type = normalizeText(item && item.type ? item.type : '');
        return type === normalizeText(typeNaam);
    });

    if (!match || !Array.isArray(match.locations)) {
        return [];
    }

    return match.locations.filter((punt) => punt && Number.isFinite(punt.x) && Number.isFinite(punt.y));
}

function berekenPuntenBereik(punten) {
    if (!Array.isArray(punten) || !punten.length) {
        return { width: 0, height: 0 };
    }

    let minX = Number.POSITIVE_INFINITY;
    let maxX = Number.NEGATIVE_INFINITY;
    let minY = Number.POSITIVE_INFINITY;
    let maxY = Number.NEGATIVE_INFINITY;

    punten.forEach((punt) => {
        minX = Math.min(minX, punt.x);
        maxX = Math.max(maxX, punt.x);
        minY = Math.min(minY, punt.y);
        maxY = Math.max(maxY, punt.y);
    });

    return {
        width: Math.max(0, maxX - minX),
        height: Math.max(0, maxY - minY),
    };
}

function schatMoodVanGezicht(gezicht) {
    const landmarks = Array.isArray(gezicht && gezicht.landmarks) ? gezicht.landmarks : [];
    const mondPunten = puntenVoorLandmark(landmarks, 'mouth');
    if (!mondPunten.length) {
        return 'unknown';
    }

    const mondBereik = berekenPuntenBereik(mondPunten);
    const gezichtBreedte = Number(gezicht && gezicht.boundingBox && gezicht.boundingBox.width) || 1;
    const mondBreedteRatio = mondBereik.width / Math.max(1, gezichtBreedte);
    const mondOpenRatio = mondBereik.height / Math.max(1, gezichtBreedte);

    // Snelle heuristiek: we schatten vibe op basis van mondvorm, zonder biometrie op te slaan.
    if (mondBreedteRatio >= 0.36 || mondOpenRatio >= 0.1) {
        return 'happy';
    }
    if (mondBreedteRatio <= 0.24 && mondOpenRatio <= 0.05) {
        return 'low';
    }
    return 'neutral';
}

async function detecteerMoodUitPreview() {
    if (!cameraPreview || !gezichtDetectieBeschikbaar()) {
        return 'unknown';
    }

    let detector = null;
    try {
        detector = new window.FaceDetector({
            fastMode: true,
            maxDetectedFaces: 1,
        });
    } catch (_error) {
        return 'unknown';
    }

    for (let poging = 0; poging < CAMERA_SCAN_ATTEMPTS; poging += 1) {
        try {
            const gezichten = await detector.detect(cameraPreview);
            if (Array.isArray(gezichten) && gezichten.length) {
                return schatMoodVanGezicht(gezichten[0]);
            }
        } catch (_error) {
            return 'unknown';
        }

        await sleep(CAMERA_SCAN_INTERVAL_MS);
    }

    return 'no-face';
}

function normaliseerMoodInvoer(waarde) {
    const tekst = normalizeText(waarde);
    if (!tekst) {
        return '';
    }

    const lageMoodHints = ['sad', 'down', 'low', 'verdrietig', 'somber', 'moe'];
    if (lageMoodHints.some((hint) => tekst.includes(hint))) {
        return 'low';
    }

    const blijeMoodHints = ['happy', 'blij', 'vrolijk', 'energetic', 'energiek'];
    if (blijeMoodHints.some((hint) => tekst.includes(hint))) {
        return 'happy';
    }

    const neutraleMoodHints = ['neutral', 'neutraal', 'chill', 'calm', 'rustig', 'ok'];
    if (neutraleMoodHints.some((hint) => tekst.includes(hint))) {
        return 'neutral';
    }

    return '';
}

function muziekPlanVoorMood(mood) {
    if (mood === 'low') {
        return {
            moodSleutel: 'camera_mood_low',
            muziekSleutel: 'camera_music_low_open',
            zoekterm: 'uplifting happy music mix',
        };
    }

    if (mood === 'happy') {
        return {
            moodSleutel: 'camera_mood_happy',
            muziekSleutel: 'camera_music_happy_open',
            zoekterm: 'happy upbeat playlist',
        };
    }

    return {
        moodSleutel: 'camera_mood_neutral',
        muziekSleutel: 'camera_music_neutral_open',
        zoekterm: 'calm focus music mix',
    };
}

function openYouTubeZoekresultaat(zoekterm) {
    const query = String(zoekterm || '').trim();
    if (!query) {
        return false;
    }

    const doelUrl = YOUTUBE_SEARCH_BASE_URL + encodeURIComponent(query);
    const popup = window.open(doelUrl, '_blank', 'noopener');
    return Boolean(popup);
}

async function voerQrScanUit() {
    return await voerCameraTaakUit(async () => {
        setCommandStatus(uiTekst('camera_qr_scanning'));
        zetCameraInsightTekst(uiTekst('camera_qr_scanning'));

        const cameraKlaar = await startCameraStream();
        if (!cameraKlaar) {
            return false;
        }

        if (!qrDetectieBeschikbaar()) {
            const melding = uiTekst('camera_qr_not_supported');
            setCommandStatus(melding);
            zetCameraInsightTekst(melding);
            return false;
        }

        const frameKlaar = await wachtOpCameraFrame();
        if (!frameKlaar) {
            const melding = uiTekst('camera_preview_not_ready');
            setCommandStatus(melding);
            zetCameraInsightTekst(melding);
            return false;
        }

        const qrWaarde = await detecteerQrWaardeUitPreview();
        if (!qrWaarde) {
            const melding = uiTekst('camera_qr_not_found');
            setCommandStatus(melding);
            zetCameraInsightTekst(melding);
            triggerHapticFeedback([80, 30, 80]);
            return false;
        }

        const gevondenTekst = uiTekst('camera_qr_found', { value: qrWaarde });
        setCommandStatus(gevondenTekst);
        zetCameraInsightTekst(gevondenTekst);
        addMessage('ai', gevondenTekst);
        triggerHapticFeedback([60, 35, 60]);

        const qrUrl = veiligeHttpUrlUitTekst(qrWaarde);
        if (qrUrl) {
            const wilOpenen = window.confirm(uiTekst('camera_qr_open_link_confirm', { url: qrUrl }));
            if (wilOpenen) {
                window.open(qrUrl, '_blank', 'noopener');
            }
        }

        return true;
    });
}

async function voerMoodCheckUit() {
    return await voerCameraTaakUit(async () => {
        setCommandStatus(uiTekst('camera_mood_scanning'));
        zetCameraInsightTekst(uiTekst('camera_mood_scanning'));

        const cameraKlaar = await startCameraStream();
        if (!cameraKlaar) {
            return false;
        }

        const frameKlaar = await wachtOpCameraFrame();
        if (!frameKlaar) {
            const melding = uiTekst('camera_preview_not_ready');
            setCommandStatus(melding);
            zetCameraInsightTekst(melding);
            return false;
        }

        let mood = await detecteerMoodUitPreview();
        if (mood === 'no-face') {
            const melding = uiTekst('camera_face_not_found');
            setCommandStatus(melding);
            zetCameraInsightTekst(melding);
            triggerHapticFeedback([80, 30, 80]);
            return false;
        }

        if (mood === 'unknown') {
            const handmatigeMood = window.prompt(uiTekst('camera_mood_manual_prompt'), 'sad');
            mood = normaliseerMoodInvoer(handmatigeMood);
            if (!mood) {
                const melding = uiTekst('camera_mood_manual_cancelled');
                setCommandStatus(melding);
                zetCameraInsightTekst(melding);
                return false;
            }
        }

        appState.lastDetectedMood = mood;

        const wilPraten = window.confirm(uiTekst('camera_talk_check'));
        if (!wilPraten) {
            const melding = uiTekst('camera_talk_later');
            setCommandStatus(melding);
            zetCameraInsightTekst(melding);
            addMessage('ai', melding);
            triggerHapticFeedback(42);
            return true;
        }

        const plan = muziekPlanVoorMood(mood);
        const moodTekst = uiTekst(plan.moodSleutel);
        const muziekTekst = uiTekst(plan.muziekSleutel);
        const volledigeTekst = moodTekst + ' ' + muziekTekst;

        setCommandStatus(muziekTekst);
        zetCameraInsightTekst(volledigeTekst);
        addMessage('ai', volledigeTekst);

        const geopend = openYouTubeZoekresultaat(plan.zoekterm);
        if (!geopend) {
            const blokMelding = uiTekst('camera_music_popup_blocked');
            addMessage('error', blokMelding);
            setCommandStatus(blokMelding);
            triggerHapticFeedback([90, 35, 90]);
            return false;
        }

        triggerHapticFeedback([55, 30, 55]);
        return true;
    });
}

function triggerHapticFeedback(pattern) {
    if (!('vibrate' in navigator)) {
        return;
    }
    try {
        navigator.vibrate(pattern);
    } catch (_error) {
        // Ignore vibration errors.
    }
}

function saveCommandHistory() {
    try {
        localStorage.setItem(COMMAND_HISTORY_STORAGE_KEY, JSON.stringify(appState.commandHistory));
    } catch (_error) {
        // Ignore storage write issues.
    }
}

function loadCommandHistory() {
    try {
        const raw = localStorage.getItem(COMMAND_HISTORY_STORAGE_KEY);
        const parsed = raw ? JSON.parse(raw) : [];
        if (Array.isArray(parsed)) {
            appState.commandHistory = parsed
                .map((item) => String(item || '').trim())
                .filter(Boolean)
                .slice(0, COMMAND_HISTORY_MAX_ITEMS);
        }
    } catch (_error) {
        appState.commandHistory = [];
    }

    appState.commandHistoryCursor = -1;
    renderCommandHistory();
}

function rememberCommand(commandText) {
    const value = String(commandText || '').trim();
    if (!value) {
        return;
    }

    const normalized = normalizeText(value);
    const next = [value];
    appState.commandHistory.forEach((existing) => {
        if (normalizeText(existing) !== normalized) {
            next.push(existing);
        }
    });

    appState.commandHistory = next.slice(0, COMMAND_HISTORY_MAX_ITEMS);
    appState.commandHistoryCursor = -1;
    saveCommandHistory();
    renderCommandHistory();
}

function setCommandDraft(value) {
    if (!commandInput) {
        return;
    }

    commandInput.value = String(value || '');
    commandInput.focus();
    const end = commandInput.value.length;
    commandInput.setSelectionRange(end, end);
    refreshCommandSuggestionsFromInput();
}

function navigateCommandHistory(direction) {
    if (!commandInput || !appState.commandHistory.length) {
        return;
    }

    if (direction < 0) {
        if (appState.commandHistoryCursor < appState.commandHistory.length - 1) {
            appState.commandHistoryCursor += 1;
        }
    } else if (direction > 0) {
        if (appState.commandHistoryCursor > 0) {
            appState.commandHistoryCursor -= 1;
        } else {
            appState.commandHistoryCursor = -1;
            setCommandDraft('');
            return;
        }
    }

    if (appState.commandHistoryCursor >= 0) {
        const draft = appState.commandHistory[appState.commandHistoryCursor] || '';
        setCommandDraft(draft);
    }
}

function renderCommandHistory() {
    if (!historyCommands) {
        return;
    }

    historyCommands.innerHTML = '';

    if (!appState.commandHistory.length) {
        const empty = document.createElement('p');
        empty.className = 'history-empty';
        empty.textContent = uiTekst('history_empty');
        historyCommands.appendChild(empty);
        return;
    }

    appState.commandHistory.slice(0, 8).forEach((command) => {
        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'history-command';
        button.textContent = command;
        button.title = command;
        button.addEventListener('click', () => {
            setCommandDraft(command);
        });
        historyCommands.appendChild(button);
    });
}

function updateViewportModeClass() {
    if (!body) {
        return;
    }

    const touchPointer = typeof window.matchMedia === 'function' && window.matchMedia('(pointer: coarse)').matches;
    const compactViewport = window.innerWidth <= 980;
    body.classList.toggle('touch-optimized', touchPointer || compactViewport);
}

function normalizeAppLanguage(taalCode) {
    // Normaliseer varianten naar stabiele browsertaalcodes.
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
    // Uniform fetch-patroon met abort-timeout voor responsieve UI.
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

function isHttpPaginaContext() {
    const protocol = String(window.location && window.location.protocol ? window.location.protocol : '').toLowerCase();
    return protocol === 'http:' || protocol === 'https:';
}

function normaliseerApiBaseUrl(baseUrl) {
    return String(baseUrl || '').trim().replace(/\/+$/, '');
}

function combineerApiUrl(path, baseUrl = '') {
    const pad = String(path || '').startsWith('/') ? String(path || '') : '/' + String(path || '');
    const base = normaliseerApiBaseUrl(baseUrl);
    return base ? base + pad : pad;
}

function isZelfdeOriginUrl(url) {
    if (!isHttpPaginaContext()) {
        return false;
    }

    try {
        return new URL(url, window.location.href).origin === window.location.origin;
    } catch (_error) {
        return false;
    }
}

function verzameldeRuntimePoorten() {
    const poorten = new Set();
    const huidigePoort = Number.parseInt(String(window.location && window.location.port ? window.location.port : ''), 10);
    if (Number.isInteger(huidigePoort) && huidigePoort > 0 && huidigePoort <= 65535) {
        poorten.add(huidigePoort);
    }

    for (let poort = ECHO_RUNTIME_PORT_START; poort <= ECHO_RUNTIME_PORT_START + ECHO_RUNTIME_PORT_SPAN; poort += 1) {
        poorten.add(poort);
    }

    return Array.from(poorten.values());
}

function verzamelApiBaseKandidaten() {
    const hosts = [];
    const locatieHost = String(window.location && window.location.hostname ? window.location.hostname : '').trim();
    if (locatieHost && locatieHost !== '0.0.0.0') {
        hosts.push(locatieHost);
    }
    hosts.push('127.0.0.1', 'localhost');

    const uniekeHosts = Array.from(new Set(hosts));
    const poorten = verzameldeRuntimePoorten();
    const kandidaten = [];
    for (const host of uniekeHosts) {
        for (const poort of poorten) {
            kandidaten.push(`http://${host}:${poort}`);
        }
    }

    const schoon = kandidaten.map((waarde) => normaliseerApiBaseUrl(waarde)).filter(Boolean);
    return Array.from(new Set(schoon));
}

async function eersteGeslaagdeWaarde(promises) {
    if (!promises.length) {
        return '';
    }

    if (typeof Promise.any === 'function') {
        try {
            return await Promise.any(promises);
        } catch (_error) {
            return '';
        }
    }

    const resultaten = await Promise.allSettled(promises);
    for (const resultaat of resultaten) {
        if (resultaat.status === 'fulfilled' && resultaat.value) {
            return resultaat.value;
        }
    }
    return '';
}

async function probeApiRuntimeBase(baseUrl) {
    const runtimeUrl = combineerApiUrl('/api/runtime-version', baseUrl);
    const response = await fetchWithTimeout(runtimeUrl, {
        method: 'GET',
        cache: 'no-store',
        mode: 'cors',
    }, API_DISCOVERY_TIMEOUT_MS);

    if (!response.ok) {
        throw new Error('runtime endpoint unavailable');
    }

    const payload = await response.json().catch(() => null);
    if (!payload || typeof payload !== 'object') {
        throw new Error('runtime payload invalid');
    }

    if (!payload.build_id && !payload.started_at) {
        throw new Error('runtime payload missing markers');
    }

    return normaliseerApiBaseUrl(baseUrl);
}

async function ontdekApiBaseUrl(force = false) {
    if (!force && appState.apiBaseUrl) {
        return appState.apiBaseUrl;
    }

    if (appState.apiDiscoveryInFlight) {
        return appState.apiDiscoveryInFlight;
    }

    const discoveryTask = (async () => {
        if (isHttpPaginaContext()) {
            const originBase = normaliseerApiBaseUrl(window.location.origin);
            try {
                const originResponse = await fetchWithTimeout('/api/runtime-version', {
                    method: 'GET',
                    cache: 'no-store',
                }, API_DISCOVERY_TIMEOUT_MS);
                if (originResponse.ok) {
                    appState.apiBaseUrl = originBase;
                    return originBase;
                }
            } catch (_error) {
                // Bij runtime-herstart proberen we alternatieve lokale poorten.
            }
        }

        const kandidaten = verzamelApiBaseKandidaten();
        const probes = kandidaten.map((baseUrl) => probeApiRuntimeBase(baseUrl));
        const gevonden = await eersteGeslaagdeWaarde(probes);
        if (gevonden) {
            appState.apiBaseUrl = gevonden;
        }
        return gevonden;
    })();

    appState.apiDiscoveryInFlight = discoveryTask;
    try {
        return await discoveryTask;
    } finally {
        appState.apiDiscoveryInFlight = null;
    }
}

function bouwFetchOptiesVoorApi(opties = {}, crossOrigin = false) {
    const fetchOpties = {
        ...opties,
    };
    if (crossOrigin) {
        fetchOpties.mode = 'cors';
    }
    return fetchOpties;
}

async function fetchEchoApi(path, options = {}, timeoutMs = 5000) {
    const pad = String(path || '').startsWith('/') ? String(path || '') : '/' + String(path || '');
    let laatsteFout = null;

    const probeer = async (url, gekoppeldeBase = '') => {
        if (!url) {
            return null;
        }
        try {
            const crossOrigin = !isZelfdeOriginUrl(url);
            const response = await fetchWithTimeout(url, bouwFetchOptiesVoorApi(options, crossOrigin), timeoutMs);
            if (gekoppeldeBase) {
                appState.apiBaseUrl = normaliseerApiBaseUrl(gekoppeldeBase);
            } else if (isHttpPaginaContext()) {
                appState.apiBaseUrl = normaliseerApiBaseUrl(window.location.origin);
            }
            return response;
        } catch (error) {
            laatsteFout = error;
            return null;
        }
    };

    if (isHttpPaginaContext()) {
        const directResponse = await probeer(pad, window.location.origin);
        if (directResponse) {
            return directResponse;
        }
    }

    const cachedBase = normaliseerApiBaseUrl(appState.apiBaseUrl);
    if (cachedBase) {
        const cachedResponse = await probeer(combineerApiUrl(pad, cachedBase), cachedBase);
        if (cachedResponse) {
            return cachedResponse;
        }
    }

    const discoveredBase = await ontdekApiBaseUrl(true);
    if (discoveredBase) {
        const discoveredResponse = await probeer(combineerApiUrl(pad, discoveredBase), discoveredBase);
        if (discoveredResponse) {
            return discoveredResponse;
        }
    }

    throw laatsteFout || new Error(uiTekst('request_failed'));
}

async function fetchRuntimeVersion() {
    try {
        const response = await fetchEchoApi('/api/runtime-version', {
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
    // Stop polling bij tab-close of mode-switch.
    if (!appState.runtimeVersionPollTimer) {
        return;
    }

    window.clearInterval(appState.runtimeVersionPollTimer);
    appState.runtimeVersionPollTimer = null;
}

function stopDashboardWatcher() {
    // Stop dashboardpolling om dubbele interval-timers te voorkomen.
    if (!appState.dashboardPollTimer) {
        if (appState.dashboardRenderRaf) {
            window.cancelAnimationFrame(appState.dashboardRenderRaf);
            appState.dashboardRenderRaf = 0;
        }
        appState.dashboardPendingPayload = null;
        appState.dashboardRefreshQueued = false;
        return;
    }

    window.clearInterval(appState.dashboardPollTimer);
    appState.dashboardPollTimer = null;
    if (appState.dashboardRenderRaf) {
        window.cancelAnimationFrame(appState.dashboardRenderRaf);
        appState.dashboardRenderRaf = 0;
    }
    appState.dashboardPendingPayload = null;
    appState.dashboardRefreshQueued = false;
}

function renderDashboardPayload(payload = {}, force = false) {
    if (!payload || typeof payload !== 'object') {
        return;
    }

    if (
        Object.prototype.hasOwnProperty.call(payload, 'modes')
        && payload.modes
        && typeof payload.modes === 'object'
        && dashboardSectieIsGewijzigd('modes', payload.modes, force)
    ) {
        renderSettingsProfilePanel({
            profile: payload.modes.settings_profile,
            profiles: payload.modes.settings_profiles,
            profileConfigs: payload.modes.settings_profile_configs,
            profileActions: payload.modes.settings_profile_actions,
            profile_auto_router_enabled: payload.modes.profile_auto_router_enabled,
            profile_auto_router_suggest_threshold: payload.modes.profile_auto_router_suggest_threshold,
            profile_auto_router_auto_threshold: payload.modes.profile_auto_router_auto_threshold,
        });
    }

    if (
        Object.prototype.hasOwnProperty.call(payload, 'security_daily_scan')
        && dashboardSectieIsGewijzigd('security_daily_scan', payload.security_daily_scan, force)
    ) {
        renderDailySecurityPanel(payload.security_daily_scan);
    }

    if (
        Object.prototype.hasOwnProperty.call(payload, 'mobile_access')
        && dashboardSectieIsGewijzigd('mobile_access', payload.mobile_access, force)
    ) {
        renderMobileAccessPanel(payload.mobile_access);
    }

    if (
        Object.prototype.hasOwnProperty.call(payload, 'latest_screenshot')
        && dashboardSectieIsGewijzigd('latest_screenshot', payload.latest_screenshot, force)
    ) {
        renderLatestScreenshotPanel(payload.latest_screenshot);
    }

    if (
        Object.prototype.hasOwnProperty.call(payload, 'website_audit')
        && dashboardSectieIsGewijzigd('website_audit', payload.website_audit, force)
    ) {
        renderWebsiteAuditPanel(payload.website_audit);
    }

    if (
        Object.prototype.hasOwnProperty.call(payload, 'website_audit_schedule')
        && dashboardSectieIsGewijzigd('website_audit_schedule', payload.website_audit_schedule, force)
    ) {
        renderWebsiteAuditSchedulePanel(payload.website_audit_schedule);
    }

    if (
        Object.prototype.hasOwnProperty.call(payload, 'pending_confirmation')
        && dashboardSectieIsGewijzigd('pending_confirmation', payload.pending_confirmation, force)
    ) {
        renderPendingConfirmation(payload.pending_confirmation);
    }
}

function queueDashboardPayloadRender(payload = {}, force = false) {
    if (!payload || typeof payload !== 'object') {
        return;
    }

    const bestaand = appState.dashboardPendingPayload && typeof appState.dashboardPendingPayload === 'object'
        ? appState.dashboardPendingPayload
        : { payload: {}, force: false };

    appState.dashboardPendingPayload = {
        payload: {
            ...bestaand.payload,
            ...payload,
        },
        force: Boolean(force || bestaand.force),
    };

    if (appState.dashboardRenderRaf) {
        return;
    }

    appState.dashboardRenderRaf = window.requestAnimationFrame(() => {
        appState.dashboardRenderRaf = 0;
        const pending = appState.dashboardPendingPayload;
        appState.dashboardPendingPayload = null;
        if (!pending || typeof pending !== 'object') {
            return;
        }
        renderDashboardPayload(pending.payload, Boolean(pending.force));
    });
}

async function haalJsonViaEchoApi(path, timeoutMs = 1400) {
    try {
        const response = await fetchEchoApi(path, {
            method: 'GET',
            cache: 'no-store',
        }, timeoutMs);
        if (!response.ok) {
            return null;
        }
        return await response.json().catch(() => null);
    } catch (_error) {
        return null;
    }
}

async function refreshDashboardTelemetry(force = false) {
    // Voorkom overlap en throttle losse handmatige refresh-triggers.
    const nu = Date.now();
    if (!force && (nu - appState.dashboardLastRefreshAt) < DASHBOARD_REFRESH_MIN_INTERVAL_MS) {
        return;
    }

    if (appState.dashboardRefreshInFlight) {
        appState.dashboardRefreshQueued = true;
        return;
    }

    appState.dashboardRefreshInFlight = true;
    appState.dashboardLastRefreshAt = nu;

    try {
        try {
            const payload = await haalJsonViaEchoApi('/api/dashboard', 1800);
            if (payload && typeof payload === 'object') {
                queueDashboardPayloadRender(payload, force);
                return;
            }
        } catch (_error) {
            // Val terug op losse deel-endpoints als dashboard tijdelijk niet reageert.
        }

        const [mobileData, screenshotData, auditData, settingsData] = await Promise.all([
            haalJsonViaEchoApi('/api/mobile-access', 1400),
            haalJsonViaEchoApi('/api/screenshot/latest', 1400),
            haalJsonViaEchoApi('/api/website-audit/status', 1400),
            haalJsonViaEchoApi('/api/instellingen', 1600),
        ]);

        const fallbackPayload = {};
        if (mobileData && typeof mobileData === 'object') {
            fallbackPayload.mobile_access = mobileData;
        }
        if (screenshotData && typeof screenshotData === 'object') {
            fallbackPayload.latest_screenshot = screenshotData;
        }
        if (auditData && typeof auditData === 'object') {
            fallbackPayload.website_audit = auditData.audit || auditData;
            fallbackPayload.website_audit_schedule = auditData.schedule || auditData.website_audit_schedule || {};
        }

        if (settingsData && typeof settingsData === 'object') {
            const profiel = normaliseerSettingsProfielNaam(
                settingsData.instellingen_profiel || settingsData.settings_profile || appState.settingsProfile
            );
            const profielLijst = normaliseerSettingsProfielenLijst(extractSettingsProfielenUitPayload(settingsData));
            const profielConfigs = normaliseerSettingsProfielConfigs(extractSettingsProfielConfigsUitPayload(settingsData));
            const profielActies = normaliseerSettingsProfielActiesData(extractSettingsProfielActiesUitPayload(settingsData));
            const routerConfig = normaliseerSettingsProfileRouterConfig(settingsData);

            fallbackPayload.modes = {
                settings_profile: profiel,
                settings_profiles: profielLijst,
                settings_profile_configs: profielConfigs,
                settings_profile_actions: profielActies,
                profile_auto_router_enabled: routerConfig.enabled,
                profile_auto_router_suggest_threshold: routerConfig.suggestThreshold,
                profile_auto_router_auto_threshold: routerConfig.autoThreshold,
            };
        }

        if (Object.keys(fallbackPayload).length) {
            queueDashboardPayloadRender(fallbackPayload, force);
        }
    } finally {
        appState.dashboardRefreshInFlight = false;
        if (appState.dashboardRefreshQueued) {
            appState.dashboardRefreshQueued = false;
            window.setTimeout(() => {
                void refreshDashboardTelemetry(force);
            }, 120);
        }
    }
}

function startDashboardWatcher() {
    // Poll alleen in browsercontexten waar HTTP API-calls beschikbaar zijn.
    stopDashboardWatcher();

    const protocol = String(window.location && window.location.protocol ? window.location.protocol : '').toLowerCase();
    if (protocol !== 'http:' && protocol !== 'https:') {
        return;
    }

    void refreshDashboardTelemetry(true);
    appState.dashboardPollTimer = window.setInterval(() => {
        void refreshDashboardTelemetry();
    }, DASHBOARD_POLL_MS);
}

function startRuntimeVersionWatcher() {
    // Versiebewaker forceert reload als backend-runtime wisselt.
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
        setTextContentIfChanged(wakeGateStatus, uiTekst('wake_gate_armed'));
        wakeGateStatus.classList.add('is-armed');
        return;
    }

    setTextContentIfChanged(wakeGateStatus, uiTekst('wake_gate_locked'));
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

function updateSpeechButtonLabel() {
    if (!speechBtn) {
        return;
    }

    if (appState.micMuted) {
        setElementDisabledIfChanged(speechBtn, true);
        setTextContentIfChanged(speechBtn, uiTekst('voice_button_muted'));
        return;
    }

    if (appState.voiceInputMode === 'upload') {
        setElementDisabledIfChanged(speechBtn, appState.voiceUploadInFlight);
        setTextContentIfChanged(
            speechBtn,
            appState.voiceUploadInFlight
                ? uiTekst('voice_upload_processing')
                : uiTekst('voice_input_quick_capture')
        );
        return;
    }

    if (appState.voiceInputMode === 'browser') {
        setElementDisabledIfChanged(speechBtn, false);
        setTextContentIfChanged(
            speechBtn,
            appState.listeningActive
                ? uiTekst('speech_listening_stop')
                : uiTekst('speech_listening_start')
        );
        return;
    }

    setElementDisabledIfChanged(speechBtn, true);
    setTextContentIfChanged(speechBtn, uiTekst('voice_not_supported'));
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
    updateSpeechButtonLabel();

    if (pendingConfirmYes) {
        pendingConfirmYes.textContent = uiTekst('confirm_button');
    }

    if (pendingConfirmNo) {
        pendingConfirmNo.textContent = uiTekst('cancel_button');
    }

    if (pendingConfirmKicker) {
        pendingConfirmKicker.textContent = uiTekst('pending_confirm_kicker');
    }

    if (mobileSaveScreenshotBtn) {
        mobileSaveScreenshotBtn.textContent = uiTekst('mobile_save_screenshot_button');
    }

    if (mobileOpenScreenshotBtn) {
        mobileOpenScreenshotBtn.textContent = uiTekst('mobile_open_screenshot_button');
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

    if (dailySecurityKicker) {
        dailySecurityKicker.textContent = uiTekst('daily_security_kicker');
    }

    if (cameraKicker) {
        cameraKicker.textContent = uiTekst('camera_kicker');
    }

    if (cameraStartBtn) {
        cameraStartBtn.textContent = uiTekst('camera_start_button');
    }

    if (cameraStopBtn) {
        cameraStopBtn.textContent = uiTekst('camera_stop_button');
    }

    if (cameraScanQrBtn) {
        cameraScanQrBtn.textContent = uiTekst('camera_scan_qr_button');
    }

    if (cameraMoodBtn) {
        cameraMoodBtn.textContent = uiTekst('camera_mood_button');
    }

    if (streamKicker) {
        streamKicker.textContent = uiTekst('stream_kicker');
    }

    if (streamStatusNote) {
        streamStatusNote.textContent = uiTekst('stream_note');
    }

    if (streamModeBtn) {
        streamModeBtn.textContent = uiTekst('stream_mode_button');
    }

    if (streamGoLiveBtn) {
        streamGoLiveBtn.textContent = uiTekst('stream_go_live_button');
    }

    if (streamStopBtn) {
        streamStopBtn.textContent = uiTekst('stream_stop_live_button');
    }

    if (streamRecStartBtn) {
        streamRecStartBtn.textContent = uiTekst('stream_record_start_button');
    }

    if (streamRecStopBtn) {
        streamRecStopBtn.textContent = uiTekst('stream_record_stop_button');
    }

    if (streamSceneLiveBtn) {
        streamSceneLiveBtn.textContent = uiTekst('stream_scene_live_button');
    }

    if (streamSceneBrbBtn) {
        streamSceneBrbBtn.textContent = uiTekst('stream_scene_brb_button');
    }

    if (streamSceneGameBtn) {
        streamSceneGameBtn.textContent = uiTekst('stream_scene_game_button');
    }

    if (streamMarkerBtn) {
        streamMarkerBtn.textContent = uiTekst('stream_marker_button');
    }

    if (streamMicBtn) {
        streamMicBtn.textContent = uiTekst('stream_mic_toggle_button');
    }

    if (streamHelpBtn) {
        streamHelpBtn.textContent = uiTekst('stream_help_button');
    }

    if (websiteAuditKicker) {
        websiteAuditKicker.textContent = uiTekst('website_audit_kicker');
    }

    if (websiteAuditUrlInput) {
        websiteAuditUrlInput.placeholder = uiTekst('website_audit_url_placeholder');
    }

    if (websiteAuditStartBtn) {
        websiteAuditStartBtn.textContent = uiTekst('website_audit_start_button');
    }

    if (websiteAuditStatusBtn) {
        websiteAuditStatusBtn.textContent = uiTekst('website_audit_status_button');
    }

    if (websiteAuditReportBtn) {
        websiteAuditReportBtn.textContent = uiTekst('website_audit_report_button');
    }

    if (websiteAuditDownloadJsonBtn) {
        websiteAuditDownloadJsonBtn.textContent = uiTekst('website_audit_download_json_button');
    }

    if (websiteAuditDownloadMdBtn) {
        websiteAuditDownloadMdBtn.textContent = uiTekst('website_audit_download_md_button');
    }

    if (websiteAuditDownloadPdfBtn) {
        websiteAuditDownloadPdfBtn.textContent = uiTekst('website_audit_download_pdf_button');
    }

    if (websiteAuditScheduleStatusBtn) {
        websiteAuditScheduleStatusBtn.textContent = uiTekst('website_audit_schedule_status_button');
    }

    if (websiteAuditScheduleUrlInput) {
        websiteAuditScheduleUrlInput.placeholder = uiTekst('website_audit_schedule_url_placeholder');
    }

    if (websiteAuditWebhookInput) {
        websiteAuditWebhookInput.placeholder = uiTekst('website_audit_schedule_webhook_placeholder');
    }

    if (websiteAuditScheduleEnabledToggle) {
        const label = websiteAuditScheduleEnabledToggle.closest('label');
        const tekst = label ? label.querySelector('span') : null;
        if (tekst) {
            tekst.textContent = uiTekst('website_audit_schedule_enabled_label');
        }
    }

    if (websiteAuditAlertCriticalToggle) {
        const label = websiteAuditAlertCriticalToggle.closest('label');
        const tekst = label ? label.querySelector('span') : null;
        if (tekst) {
            tekst.textContent = uiTekst('website_audit_schedule_alert_critical_label');
        }
    }

    if (websiteAuditScheduleSaveBtn) {
        websiteAuditScheduleSaveBtn.textContent = uiTekst('website_audit_schedule_save_button');
    }

    if (websiteAuditProfileSelect) {
        Array.from(websiteAuditProfileSelect.options || []).forEach((optie) => {
            const waarde = String(optie.value || '').trim().toLowerCase();
            if (!waarde) {
                return;
            }
            optie.textContent = uiTekst('website_audit_profile_' + waarde);
        });
    }

    if (websiteAuditScheduleProfileSelect) {
        Array.from(websiteAuditScheduleProfileSelect.options || []).forEach((optie) => {
            const waarde = String(optie.value || '').trim().toLowerCase();
            if (!waarde) {
                return;
            }
            optie.textContent = uiTekst('website_audit_profile_' + waarde);
        });
    }

    if (websiteAuditFrequencySelect) {
        Array.from(websiteAuditFrequencySelect.options || []).forEach((optie) => {
            const waarde = normaliseerWebsiteAuditFrequency(optie.value);
            optie.textContent = uiTekst('website_audit_frequency_' + waarde);
        });
    }

    if (overviewKicker) {
        overviewKicker.textContent = uiTekst('overview_kicker');
    }

    if (actionFilterLabel) {
        actionFilterLabel.textContent = uiTekst('overview_filter_label');
    }

    if (actionFilterInput) {
        actionFilterInput.placeholder = uiTekst('overview_filter_placeholder');
        if (actionFilterInput.value !== appState.actionFilterQuery) {
            actionFilterInput.value = appState.actionFilterQuery;
        }
    }

    if (actionFilterHint && !normalizeText(appState.actionFilterQuery)) {
        actionFilterHint.textContent = uiTekst('overview_filter_hint');
    }

    if (!pendingConfirm || pendingConfirm.classList.contains('is-hidden')) {
        resetPendingCommandsDefaults();
    }

    renderDailySecurityPanel(appState.dailySecuritySnapshot);
    renderSettingsProfilePanel({
        profile: appState.settingsProfile,
        profiles: appState.settingsProfiles,
        applying: appState.settingsProfileApplying,
    });
    renderMobileAccessPanel(appState.mobileAccessSnapshot);
    renderLatestScreenshotPanel(appState.latestScreenshotSnapshot);
    renderWebsiteAuditPanel(appState.websiteAuditSnapshot);
    renderWebsiteAuditSchedulePanel(appState.websiteAuditScheduleSnapshot);
    renderCameraPanel();
    renderCommandHistory();
    refreshCommandSuggestionsFromInput();
    updatePanelCollapseToggleLabels();
    applyActionFilter();
    renderCommandCenterStatus();

    setMode(appState.dashboardActive);
    updateWakeGateStatus();
    updateIdleVoiceStatus();
    setThreatState(appState.threatLevel, threatContextForLevel(appState.threatLevel), 0);
}

async function persistLanguageSetting() {
    try {
        await fetchEchoApi('/api/instellingen', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                taal: isNederlandsActief() ? 'Nederlands' : 'English',
            }),
        }, 4500);
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

    const zatDichtbijOnderkant = (messages.scrollHeight - (messages.scrollTop + messages.clientHeight)) < 40;

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

    while (messages.childElementCount > MAX_FEED_MESSAGES) {
        const oudste = messages.firstElementChild;
        if (!oudste) {
            break;
        }
        messages.removeChild(oudste);
    }

    if (zatDichtbijOnderkant || kind === 'user') {
        messages.scrollTop = messages.scrollHeight;
    }
}

function setCommandStatus(text) {
    setTextContentIfChanged(commandStatus, text);
}

function isRecentDuplicateAssistantMessage(text) {
    const normalized = normalizeText(cleanTextForSpeech(text));
    if (!normalized) {
        return false;
    }

    const now = Date.now();
    const isDuplicate = normalized === appState.lastAssistantMessageNormalized
        && (now - appState.lastAssistantMessageAt) < ASSISTANT_DUPLICATE_WINDOW_MS;

    appState.lastAssistantMessageNormalized = normalized;
    appState.lastAssistantMessageAt = now;
    return isDuplicate;
}

function setVoiceStatus(text) {
    setTextContentIfChanged(voiceStatus, text);
}

function refreshCoreStateClasses() {
    if (!coreMicBtn) {
        return;
    }
    coreMicBtn.classList.toggle('is-listening', appState.listeningActive);
    coreMicBtn.classList.toggle('is-speaking', appState.speakingActive);
}

function updateIdleVoiceStatus() {
    let statusTekst = uiTekst('voice_standby');

    if (appState.speakingActive) {
        statusTekst = uiTekst('voice_speaking');
    } else if (appState.voiceUploadInFlight) {
        statusTekst = uiTekst('voice_upload_processing');
    } else if (appState.micMuted) {
        statusTekst = uiTekst('voice_status_mic_muted');
    } else if (appState.listeningActive) {
        statusTekst = appState.wakeArmed
            ? uiTekst('voice_wake_confirmed')
            : uiTekst('voice_listening_for_wake', { wakeWord: appState.wakeWord });
    } else if (appState.voiceInputMode === 'upload') {
        statusTekst = uiTekst('voice_manual_mobile_hint');
    }

    setVoiceStatus(statusTekst);
    renderCommandCenterStatus();
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
    updateSpeechButtonLabel();
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
        renderCommandCenterStatus();
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
    renderCommandCenterStatus();
}

async function sendCommand(command, source = 'text') {
    const commandText = String(command || '').trim();
    const commandNormalized = normalizeText(commandText);
    if (!commandText) {
        return;
    }

    hideCommandSuggestions();

    if (await handelLokaleSnelkoppelingAf(commandText, source)) {
        return;
    }

    if (source !== 'system') {
        const routerHint = updateSettingsProfileIntentHint(commandText);
        const heeftProfielMismatch = Boolean(routerHint && routerHint.profile && routerHint.profile !== appState.settingsProfile);

        if (appState.settingsProfileRouterEnabled && heeftProfielMismatch) {
            const confidence = Number(routerHint.confidence || 0);
            if (confidence >= appState.settingsProfileRouterAutoThreshold) {
                const autoHint = updateSettingsProfileIntentHint(commandText, 'auto');
                const wisselGelukt = await applySettingsProfiel(null, {
                    forcedProfile: routerHint.profile,
                    silent: true,
                });
                if (wisselGelukt) {
                    const melding = uiTekst('settings_profile_router_switched', {
                        profile: settingsProfielLabel(routerHint.profile),
                        confidence: String(Math.max(0, Math.min(99, Number(routerHint.confidence || 0)))),
                    });
                    setCommandStatus(melding);
                    triggerHapticFeedback([25, 20, 25]);
                    if (autoHint) {
                        renderSettingsProfilePanel({ intentHint: autoHint });
                    }
                } else {
                    setCommandStatus(uiTekst('settings_profile_router_switch_failed'));
                }
            } else if (confidence >= appState.settingsProfileRouterSuggestThreshold) {
                const suggestie = uiTekst('settings_profile_router_state_suggest', {
                    profile: settingsProfielLabel(routerHint.profile),
                    confidence: String(Math.max(0, Math.min(99, Number(routerHint.confidence || 0)))),
                });
                setCommandStatus(suggestie);
            }
        }
    }

    if (source !== 'system') {
        rememberCommand(commandText);
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
                const isDuplicateReply = isRecentDuplicateAssistantMessage(deviceMessage);

                if (isDuplicateReply) {
                    setCommandStatus(uiTekst('command_duplicate_ignored'));
                } else if (isError) {
                    addMessage('error', deviceMessage);
                    setCommandStatus(uiTekst('command_device_failed'));
                    setThreatState('critical', uiTekst('threat_context_device_failure'), 10000);
                    triggerHapticFeedback([80, 30, 80]);
                } else {
                    addMessage('ai', deviceMessage);
                    setCommandStatus(needsConfirmation ? uiTekst('command_device_confirmation') : uiTekst('command_device_completed'));
                    setThreatState(
                        needsConfirmation ? 'elevated' : threatProfile.level,
                        needsConfirmation ? uiTekst('threat_context_device_confirmation') : threatProfile.context,
                        needsConfirmation ? 12000 : 7000
                    );
                    triggerHapticFeedback(needsConfirmation ? [70, 30, 70] : 50);
                }

                renderPendingConfirmation(null);

                const speechProfile = needsConfirmation
                    ? 'confirmation'
                    : (isError ? 'warning' : profileForSpeechMessage(deviceMessage, profileForThreatLevel(threatProfile.level)));

                if (!isDuplicateReply) {
                    const spoken = await speakText(deviceMessage, { profile: speechProfile });
                    if (!spoken) {
                        pulseSpeaking(isError ? 1500 : 1200);
                    }
                }

                return;
            }
        }

        const response = await fetchEchoApi('/api/commando', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                commando: commandText,
                server_speech: false,
                source,
            }),
        }, 12000);

        const data = await response.json().catch(() => ({
            status: 'error',
            message: uiTekst('invalid_server_response'),
        }));

        const ok = response.ok && data.status === 'success';
        const message = String(data.message || '').trim() || (ok
            ? tekstVoorTaal('Done.', 'Klaar.')
            : tekstVoorTaal('Command failed.', 'Opdracht mislukt.'));
        const hasPendingConfirmation = Boolean(data.pending_confirmation && data.pending_confirmation.pending);
        if (ok && !hasPendingConfirmation && !data.duplicate_ignored) {
            syncStreamStatusUitContext(commandText, message);
        }
        const screenshotArtifact = normaliseerScreenshotArtifact(data.artifacts && data.artifacts.screenshot);
        if (screenshotArtifact.available) {
            renderLatestScreenshotPanel(screenshotArtifact);
        }
        if (data.duplicate_ignored) {
            setCommandStatus(uiTekst('command_duplicate_ignored'));
            renderPendingConfirmation(data.pending_confirmation);
            return;
        }

        const pendingPrompt = hasPendingConfirmation
            ? String(
                data.pending_confirmation.prompt
                || (isNederlandsActief() ? data.pending_confirmation.prompt_nl : data.pending_confirmation.prompt_en)
                || (isNederlandsActief() ? data.pending_confirmation.prompt_en : data.pending_confirmation.prompt_nl)
                || uiTekst('pending_waiting_confirmation')
            ).trim()
            : '';
        const spokenText = pendingPrompt || message;
        const isDuplicateReply = isRecentDuplicateAssistantMessage(spokenText);

        if (ok && !isDuplicateReply) {
            addMessage('ai', message);
            setCommandStatus(uiTekst('command_completed_ms', { duration: String(data.duration_ms || 0) }));
            triggerHapticFeedback(50);

            const preset = pendingPrompt
                ? 'confirmation'
                : profileForSpeechMessage(message, profileForThreatLevel(threatProfile.level));

            const spoken = await speakText(spokenText, { profile: preset });
            if (!spoken) {
                pulseSpeaking();
            }
        } else if (ok) {
            setCommandStatus(uiTekst('command_duplicate_ignored'));
        } else if (!isDuplicateReply) {
            addMessage('error', message);
            setCommandStatus(uiTekst('command_failed'));
            setThreatState('elevated', uiTekst('threat_context_command_failure'), 9000);
            triggerHapticFeedback([80, 30, 80]);

            const spoken = await speakText(message, {
                profile: profileForSpeechMessage(message, 'warning'),
            });
            if (!spoken) {
                pulseSpeaking(1500);
            }
        } else {
            setCommandStatus(uiTekst('command_duplicate_ignored'));
        }

        renderPendingConfirmation(data.pending_confirmation);

        if (ok && commandNormalized.startsWith('website audit')) {
            void refreshDashboardTelemetry();
        }

        if (screenshotArtifact.available) {
            maybeAutoSaveScreenshotToPhone(screenshotArtifact);
        }

        if (hasPendingConfirmation) {
            setThreatState('elevated', uiTekst('threat_context_pending_confirmation'), 12000);
        }
    } catch (error) {
        const rawMessage = error instanceof Error ? String(error.message || '').trim() : '';
        const isTransportError = /failed to fetch|networkerror|load failed|fetch/i.test(rawMessage);
        const message = isTransportError
            ? uiTekst('request_failed_runtime_hint')
            : (rawMessage || uiTekst('request_failed'));
        addMessage('error', message);
        setCommandStatus(uiTekst('command_connection_error'));
        setThreatState('critical', uiTekst('threat_context_transport_failure'), 10000);
        triggerHapticFeedback([110, 45, 110]);

        const spoken = await speakText(message, { profile: 'warning' });
        if (!spoken) {
            pulseSpeaking(1400);
        }
    } finally {
        if (source === 'voice') {
            appState.voiceCommandInFlight = false;
        }
        if (sendBtn) {
            sendBtn.disabled = false;
        }
    }
}

function clearVoiceTranscriptBuffer() {
    appState.voiceTranscriptBuffer = [];
    if (appState.voiceTranscriptTimer) {
        window.clearTimeout(appState.voiceTranscriptTimer);
        appState.voiceTranscriptTimer = null;
    }
}

function normaliseerVoiceTranscriptTekst(transcript) {
    const genormaliseerd = normalizeText(transcript);
    if (!genormaliseerd) {
        return '';
    }

    const woorden = genormaliseerd.split(' ').filter(Boolean);
    const compact = [];
    let vorige = '';
    let herhaling = 0;

    for (const woord of woorden) {
        if (woord === vorige) {
            herhaling += 1;
            if (herhaling >= 2) {
                continue;
            }
        } else {
            vorige = woord;
            herhaling = 0;
        }
        compact.push(woord);
    }

    return compact.join(' ').trim();
}

function clearRecognitionRestartTimer() {
    if (!appState.recognitionRestartTimer) {
        return;
    }

    window.clearTimeout(appState.recognitionRestartTimer);
    appState.recognitionRestartTimer = null;
}

function activeerVoiceUploadFallback(reasonCode = '') {
    if (!isVoiceUploadFallbackAvailable()) {
        return false;
    }

    clearRecognitionRestartTimer();
    clearVoiceTranscriptBuffer();
    appState.recognitionErrorStreak = 0;
    appState.recognitionRestartCount = 0;
    appState.listeningWanted = false;
    appState.voiceInputMode = 'upload';

    try {
        if (appState.recognition) {
            appState.recognition.stop();
        }
    } catch (_error) {
        // Ignore stop errors while switching fallback modes.
    }

    setListening(false);
    setWakeArmed(false);
    setVoiceStatus(uiTekst('voice_manual_mobile_hint'));
    setCommandStatus(uiTekst('voice_recognition_unavailable_browser'));
    updateSpeechButtonLabel();

    if (reasonCode) {
        console.warn('[Echo] Voice fallback enabled:', reasonCode);
    }

    return true;
}

function planRecognitionRestart(reasonCode = '') {
    if (!appState.listeningWanted || appState.voiceInputMode !== 'browser' || !appState.recognition) {
        return;
    }

    if (appState.recognitionRestartCount >= RECOGNITION_MAX_RESTARTS) {
        const fallbackActief = activeerVoiceUploadFallback(reasonCode || 'restart-limit');
        if (!fallbackActief) {
            appState.listeningWanted = false;
            setListening(false);
            setWakeArmed(false);
            setVoiceStatus(uiTekst('voice_recognition_unavailable'));
            setCommandStatus(uiTekst('voice_recognition_unavailable'));
        }
        return;
    }

    clearRecognitionRestartTimer();
    const poging = appState.recognitionRestartCount + 1;
    appState.recognitionRestartCount = poging;
    const vertraging = Math.min(1800, RECOGNITION_RESTART_BASE_DELAY_MS * poging);

    appState.recognitionRestartTimer = window.setTimeout(() => {
        appState.recognitionRestartTimer = null;
        if (!appState.listeningWanted || appState.voiceInputMode !== 'browser') {
            return;
        }
        startRecognition();
    }, vertraging);
}

function processVoiceTranscript(transcript) {
    const spokenRaw = normaliseerVoiceTranscriptTekst(transcript);
    if (!spokenRaw) {
        return;
    }

    const wakeExtraction = extractWakeCommand(spokenRaw);
    let commandToSend = spokenRaw;

    if (wakeExtraction.wakeDetected) {
        if (!wakeExtraction.command) {
            setWakeArmed(true);
            setCommandStatus(uiTekst('wake_acknowledged'));
            return;
        }

        commandToSend = wakeExtraction.command;
        setWakeArmed(false);
        setCommandStatus(uiTekst('wake_detected_inline'));
    } else if (appState.wakeArmed) {
        setWakeArmed(false);
        setCommandStatus(uiTekst('wake_confirmed_executing'));
    } else {
        setCommandStatus(uiTekst('wake_word_required', { wakeWord: appState.wakeWord }));
        setVoiceStatus(uiTekst('voice_listening_for_wake', { wakeWord: appState.wakeWord }));
        return;
    }

    const normalizedCommand = normalizeText(commandToSend);
    if (!normalizedCommand) {
        return;
    }

    const now = Date.now();
    const isTranscriptDuplicate = normalizedCommand === appState.lastVoiceTranscriptNormalized
        && (now - appState.lastVoiceTranscriptAt) < VOICE_DUPLICATE_WINDOW_MS;
    const isRecentDispatchDuplicate = normalizedCommand === appState.lastVoiceCommandDispatchedNormalized
        && (now - appState.lastVoiceCommandDispatchedAt) < VOICE_COMMAND_DISPATCH_DUPLICATE_WINDOW_MS;
    const isInflightDuplicate = appState.voiceCommandInFlight
        && normalizedCommand === appState.lastVoiceCommandDispatchedNormalized;

    if (isTranscriptDuplicate || isRecentDispatchDuplicate || isInflightDuplicate) {
        setVoiceStatus(tekstVoorTaal('Ignored duplicate voice command.', 'Dubbele spraakopdracht genegeerd.'));
        return;
    }

    appState.lastVoiceTranscriptNormalized = normalizedCommand;
    appState.lastVoiceTranscriptAt = now;
    appState.lastVoiceCommandDispatchedNormalized = normalizedCommand;
    appState.lastVoiceCommandDispatchedAt = now;
    appState.voiceCommandInFlight = true;

    const taak = sendCommand(commandToSend, 'voice');
    if (taak && typeof taak.finally === 'function') {
        taak.finally(() => {
            appState.voiceCommandInFlight = false;
        });
    } else {
        appState.voiceCommandInFlight = false;
    }
}

function handleRecognitionResult(event) {
    if (!event || !event.results) {
        return;
    }

    for (let index = event.resultIndex; index < event.results.length; index += 1) {
        const result = event.results[index];
        if (result && result.isFinal && result[0] && result[0].transcript) {
            const fragment = String(result[0].transcript).trim();
            if (!fragment) {
                continue;
            }

            appState.recognitionErrorStreak = 0;
            appState.recognitionRestartCount = 0;

            const normalizedFragment = normalizeText(fragment);
            const vorigeFragment = appState.voiceTranscriptBuffer.length
                ? normalizeText(appState.voiceTranscriptBuffer[appState.voiceTranscriptBuffer.length - 1])
                : '';

            if (normalizedFragment && normalizedFragment === vorigeFragment) {
                continue;
            }

            appState.voiceTranscriptBuffer.push(fragment);
            if (appState.voiceTranscriptTimer) {
                window.clearTimeout(appState.voiceTranscriptTimer);
            }
            appState.voiceTranscriptTimer = window.setTimeout(() => {
                const transcript = appState.voiceTranscriptBuffer.join(' ').trim();
                clearVoiceTranscriptBuffer();
                processVoiceTranscript(transcript);
            }, VOICE_TRANSCRIPT_BUFFER_MS);
        }
    }
}

function startRecognition() {
    if (appState.voiceInputMode !== 'browser' || !appState.recognition || !appState.bootComplete) {
        return;
    }

    clearRecognitionRestartTimer();

    try {
        appState.recognition.lang = appState.language;
        appState.recognition.start();
    } catch (error) {
        appState.recognitionErrorStreak += 1;
        planRecognitionRestart('start-error');
        const code = error && typeof error === 'object' && 'name' in error
            ? String(error.name || '').trim().toLowerCase()
            : 'start';
        setCommandStatus(uiTekst('voice_error_code', { code }));
    }
}

function stopRecognition() {
    if (appState.voiceInputMode !== 'browser' || !appState.recognition) {
        return;
    }

    clearRecognitionRestartTimer();
    clearVoiceTranscriptBuffer();
    appState.recognitionErrorStreak = 0;
    appState.recognitionRestartCount = 0;
    setWakeArmed(false);

    try {
        appState.recognition.stop();
    } catch (_error) {
        // Ignore stop errors.
    }
}

async function uploadVoiceCaptureFile(audioFile) {
    if (!audioFile || appState.voiceUploadInFlight) {
        return;
    }

    appState.voiceUploadInFlight = true;
    appState.listeningWanted = false;
    setWakeArmed(false);
    updateSpeechButtonLabel();
    updateIdleVoiceStatus();
    setCommandStatus(uiTekst('voice_upload_processing'));

    try {
        const uploadName = String(audioFile.name || '').trim() || 'voice-capture.webm';
        const formData = new FormData();
        formData.append('audio', audioFile, uploadName);

        const response = await fetchEchoApi('/api/spraak-upload', {
            method: 'POST',
            body: formData,
        }, VOICE_UPLOAD_TIMEOUT_MS);

        const data = await response.json().catch(() => ({
            status: 'error',
            message: uiTekst('invalid_server_response'),
        }));

        const transcript = String(data.gesproken || '').trim();
        if (!response.ok || data.status !== 'success') {
            const foutmelding = String(data.message || '').trim() || uiTekst('voice_upload_failed');
            addMessage('error', foutmelding);
            setCommandStatus(foutmelding);
            setVoiceStatus(uiTekst('voice_upload_failed'));
            setThreatState('watch', uiTekst('threat_context_transport_failure'), 7000);
            triggerHapticFeedback([80, 30, 80]);
            return;
        }

        if (!transcript) {
            setCommandStatus(uiTekst('voice_upload_empty'));
            setVoiceStatus(uiTekst('voice_upload_empty'));
            triggerHapticFeedback([80, 30, 80]);
            return;
        }

        processVoiceTranscript(transcript);
    } catch (error) {
        const rawMessage = error instanceof Error ? String(error.message || '').trim() : '';
        const isTransportError = /failed to fetch|networkerror|load failed|fetch/i.test(rawMessage);
        const foutmelding = isTransportError
            ? uiTekst('request_failed_runtime_hint')
            : (rawMessage || uiTekst('voice_upload_failed'));
        addMessage('error', foutmelding);
        setCommandStatus(uiTekst('voice_upload_failed'));
        setVoiceStatus(uiTekst('voice_upload_failed'));
        setThreatState('critical', uiTekst('threat_context_transport_failure'), 9000);
        triggerHapticFeedback([80, 30, 80]);
    } finally {
        appState.voiceUploadInFlight = false;
        updateSpeechButtonLabel();
        updateIdleVoiceStatus();
    }
}

function openVoiceUploadCapturePicker() {
    if (!isVoiceUploadFallbackAvailable()) {
        appState.voiceInputMode = 'none';
        setCommandStatus(uiTekst('voice_not_supported'));
        updateSpeechButtonLabel();
        return;
    }

    if (appState.voiceUploadInFlight) {
        return;
    }

    if (mobileVoiceFileInput) {
        mobileVoiceFileInput.value = '';
        setCommandStatus(uiTekst('voice_input_quick_capture'));
        mobileVoiceFileInput.click();
    }
}

function toggleListening() {
    if (!appState.bootComplete) {
        return;
    }

    if (appState.micMuted) {
        const melding = uiTekst('camera_mic_blocked');
        setVoiceStatus(uiTekst('voice_status_mic_muted'));
        setCommandStatus(melding);
        zetCameraInsightTekst(melding);
        triggerHapticFeedback([80, 30, 80]);
        return;
    }

    if (appState.voiceInputMode === 'upload') {
        openVoiceUploadCapturePicker();
        return;
    }

    if (!appState.recognition || appState.voiceInputMode !== 'browser') {
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
    appState.isSamsungBrowser = detectSamsungBrowser();
    appState.recognitionErrorStreak = 0;
    appState.recognitionRestartCount = 0;
    clearRecognitionRestartTimer();

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
        if (isVoiceUploadFallbackAvailable()) {
            appState.voiceInputMode = 'upload';
            appState.recognition = null;
            setVoiceStatus(uiTekst('voice_manual_mobile_hint'));
            setCommandStatus(uiTekst('voice_recognition_unavailable_browser'));
            updateSpeechButtonLabel();
            return;
        }

        appState.voiceInputMode = 'none';
        appState.recognition = null;
        setVoiceStatus(uiTekst('voice_recognition_unavailable'));
        updateSpeechButtonLabel();
        return;
    }

    appState.voiceInputMode = 'browser';

    const recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = false;
    recognition.lang = appState.language;

    recognition.onstart = () => {
        appState.recognitionErrorStreak = 0;
        appState.recognitionRestartCount = 0;
        clearVoiceTranscriptBuffer();
        setListening(true);
        setCommandStatus(uiTekst('voice_listening_active'));
    };

    recognition.onresult = handleRecognitionResult;

    recognition.onerror = (event) => {
        const code = event && event.error ? String(event.error || '').trim().toLowerCase() : 'unknown';
        if (code === 'aborted' && !appState.listeningWanted) {
            return;
        }

        setCommandStatus(uiTekst('voice_error_code', { code }));

        if (code === 'service-not-allowed' || code === 'not-allowed') {
            appState.listeningWanted = false;
            setListening(false);
            setWakeArmed(false);
            const fallbackActief = activeerVoiceUploadFallback(code);
            if (!fallbackActief) {
                setVoiceStatus(uiTekst('microphone_permission_denied'));
                updateSpeechButtonLabel();
            }
            return;
        }

        if (code === 'audio-capture') {
            appState.recognitionErrorStreak += 1;
            if (appState.recognitionErrorStreak >= RECOGNITION_FALLBACK_THRESHOLD) {
                const fallbackActief = activeerVoiceUploadFallback(code);
                if (fallbackActief) {
                    return;
                }
            }
            setVoiceStatus('Geen microfoonsignaal. Controleer of je microfoon niet door een andere app wordt gebruikt.');
            return;
        }

        if (code === 'network') {
            appState.recognitionErrorStreak += 1;
            if (appState.recognitionErrorStreak >= RECOGNITION_FALLBACK_THRESHOLD) {
                const fallbackActief = activeerVoiceUploadFallback(code);
                if (fallbackActief) {
                    return;
                }
            }
            setVoiceStatus('Spraakherkenning kan geen verbinding maken. Controleer internet en probeer opnieuw.');
            return;
        }

        if (code === 'no-speech') {
            appState.recognitionErrorStreak += 1;
            if (appState.recognitionErrorStreak >= RECOGNITION_FALLBACK_THRESHOLD && appState.isSamsungBrowser) {
                const fallbackActief = activeerVoiceUploadFallback(code);
                if (fallbackActief) {
                    return;
                }
            }
            setVoiceStatus('Geen spraak gehoord. Spreek opnieuw nadat luisteren actief is.');
            return;
        }

        appState.recognitionErrorStreak += 1;
        if (appState.recognitionErrorStreak >= RECOGNITION_FALLBACK_THRESHOLD && appState.isSamsungBrowser) {
            const fallbackActief = activeerVoiceUploadFallback(code);
            if (fallbackActief) {
                return;
            }
        }
    };

    recognition.onend = () => {
        clearVoiceTranscriptBuffer();
        setWakeArmed(false);
        setListening(false);

        if (appState.voiceInputMode !== 'browser') {
            return;
        }

        if (
            appState.listeningWanted
            && appState.recognitionErrorStreak >= RECOGNITION_FALLBACK_THRESHOLD
            && activeerVoiceUploadFallback('error-streak')
        ) {
            return;
        }

        if (appState.listeningWanted) {
            planRecognitionRestart('onend');
        }
    };

    appState.recognition = recognition;
    updateSpeechButtonLabel();
}

function updateVisualizerBars(nowMs = performance.now()) {
    if (!visualizerBars.length) {
        return;
    }

    const hiddenIdle = Boolean(document.hidden) && !appState.speakingActive && !appState.listeningActive;
    const minInterval = hiddenIdle
        ? 420
        : (appState.speakingActive || appState.listeningActive ? VISUALIZER_ACTIVE_FRAME_MS : VISUALIZER_IDLE_FRAME_MS);

    if ((nowMs - appState.visualizerLastFrameAt) < minInterval) {
        return;
    }
    appState.visualizerLastFrameAt = nowMs;

    const osc = nowMs / 220;
    const base = appState.speakingActive
        ? 0.72
        : (appState.listeningActive ? 0.45 : 0.13);

    visualizerBars.forEach((bar, index) => {
        const harmonic = (Math.sin(osc + (index * 0.53)) + 1) * 0.13;
        const noise = Math.random() * (appState.speakingActive ? 0.34 : (appState.listeningActive ? 0.22 : 0.06));
        const level = Math.min(1, Math.max(0.08, base + harmonic + noise));
        bar.style.setProperty('--level', level.toFixed(3));
        bar.style.opacity = appState.speakingActive ? '1' : (appState.listeningActive ? '0.92' : '0.72');
    });
}

function visualizerFrameTick(nowMs) {
    updateVisualizerBars(nowMs);
    appState.visualizerTimer = window.requestAnimationFrame(visualizerFrameTick);
}

function stopVisualizer() {
    if (!appState.visualizerTimer) {
        return;
    }

    window.cancelAnimationFrame(appState.visualizerTimer);
    appState.visualizerTimer = 0;
}

function startVisualizer() {
    if (appState.visualizerTimer) {
        return;
    }

    appState.visualizerLastFrameAt = 0;
    appState.visualizerTimer = window.requestAnimationFrame(visualizerFrameTick);
}

async function loadSettings() {
    try {
        const response = await fetchEchoApi('/api/instellingen', { cache: 'no-store' }, 3000);
        if (!response.ok) {
            return;
        }

        const settings = await response.json();

        appState.aiName = String(settings.naam || 'Echo');
        appState.voiceOutputEnabled = settings.spraak_uitgang !== false;
        appState.voiceOutputUserEnabled = appState.voiceOutputEnabled;
        if (appState.deafenEnabled) {
            appState.voiceOutputEnabled = false;
        }

        appState.wakeWord = String(settings.wake_word || 'hey echo').trim() || 'hey echo';
        appState.browserVoicePreference = String(settings.browser_stem || '').trim();
        appState.premiumVoiceId = String(settings.premium_tts_voice_id || '').trim();
        appState.settingsProfile = normaliseerSettingsProfielNaam(
            settings.instellingen_profiel || settings.settings_profile || appState.settingsProfile
        );
        appState.settingsProfileSelected = appState.settingsProfile;
        appState.settingsProfiles = normaliseerSettingsProfielenLijst(extractSettingsProfielenUitPayload(settings));
        appState.settingsProfileConfigs = normaliseerSettingsProfielConfigs(
            extractSettingsProfielConfigsUitPayload(settings)
        );
        appState.settingsProfileActionsByProfile = normaliseerSettingsProfielActiesData(
            extractSettingsProfielActiesUitPayload(settings)
        );
        const routerConfig = normaliseerSettingsProfileRouterConfig(settings);
        appState.settingsProfileRouterEnabled = routerConfig.enabled;
        appState.settingsProfileRouterSuggestThreshold = routerConfig.suggestThreshold;
        appState.settingsProfileRouterAutoThreshold = routerConfig.autoThreshold;
        appState.settingsProfileApplying = false;
        appState.settingsProfileLaunching = false;
        appState.settingsProfileRouterSaving = false;
        appState.settingsProfileIntentHint = null;

        if (assistantName) {
            assistantName.textContent = appState.aiName.toUpperCase();
        }

        await setAppLanguage(bepaalSpraakTaalUitInstellingen(settings));

        renderDailySecurityPanel({
            enabled: parseerBoolWaarde(settings.security_scan_daily_enabled, false),
            scheduled_time: String(settings.security_scan_daily_time || '03:00').trim() || '03:00',
        });
        renderSettingsProfilePanel({
            profile: appState.settingsProfile,
            selected: appState.settingsProfileSelected,
            profiles: appState.settingsProfiles,
            profileConfigs: appState.settingsProfileConfigs,
            profileActions: appState.settingsProfileActionsByProfile,
            profile_auto_router_enabled: appState.settingsProfileRouterEnabled,
            profile_auto_router_suggest_threshold: appState.settingsProfileRouterSuggestThreshold,
            profile_auto_router_auto_threshold: appState.settingsProfileRouterAutoThreshold,
            applying: false,
            launching: false,
            routerSaving: false,
            intentHint: null,
        });
        renderWebsiteAuditSchedulePanel({
            enabled: parseerBoolWaarde(settings.website_audit_schedule_enabled, false),
            frequency: String(settings.website_audit_schedule_frequency || 'daily').trim().toLowerCase(),
            scheduled_time: String(settings.website_audit_schedule_time || '04:30').trim() || '04:30',
            target_url: String(settings.website_audit_schedule_target_url || '').trim(),
            profile: String(settings.website_audit_schedule_profile || 'standard').trim().toLowerCase(),
            alert_score_drop: Number(settings.website_audit_alert_score_drop || 12),
            alert_on_critical: parseerBoolWaarde(settings.website_audit_alert_on_critical, true),
        });
        renderMobileAccessPanel(appState.mobileAccessSnapshot);

        document.title = appState.aiName;
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

    if (mobileVoiceFileInput) {
        mobileVoiceFileInput.addEventListener('change', (event) => {
            const target = event.target;
            const files = target && target.files ? target.files : null;
            const selectedFile = files && files.length ? files[0] : null;
            if (target) {
                target.value = '';
            }
            if (!selectedFile) {
                return;
            }
            void uploadVoiceCaptureFile(selectedFile);
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
            const value = String(commandInput ? commandInput.value : '').trim();
            if (!value) {
                return;
            }
            void sendCommand(value, 'text');
            if (commandInput) {
                commandInput.value = '';
                commandInput.focus();
            }
            hideCommandSuggestions();
        });
    }

    if (settingsProfileForm) {
        settingsProfileForm.addEventListener('submit', (event) => {
            void applySettingsProfiel(event);
        });
    }

    if (settingsProfileRouterForm) {
        settingsProfileRouterForm.addEventListener('submit', (event) => {
            void saveSettingsProfielRouter(event);
        });
    }

    if (settingsProfileRouterEnabledToggle) {
        settingsProfileRouterEnabledToggle.addEventListener('change', () => {
            if (appState.settingsProfileApplying || appState.settingsProfileLaunching || appState.settingsProfileRouterSaving) {
                return;
            }
            renderSettingsProfilePanel({
                profile_auto_router_enabled: settingsProfileRouterEnabledToggle.checked,
            });
        });
    }

    const routerThresholdPreviewHandler = () => {
        if (appState.settingsProfileApplying || appState.settingsProfileLaunching || appState.settingsProfileRouterSaving) {
            return;
        }
        renderSettingsProfilePanel({
            profile_auto_router_suggest_threshold: settingsProfileSuggestThresholdInput
                ? settingsProfileSuggestThresholdInput.value
                : appState.settingsProfileRouterSuggestThreshold,
            profile_auto_router_auto_threshold: settingsProfileAutoThresholdInput
                ? settingsProfileAutoThresholdInput.value
                : appState.settingsProfileRouterAutoThreshold,
        });
    };

    if (settingsProfileSuggestThresholdInput) {
        settingsProfileSuggestThresholdInput.addEventListener('input', routerThresholdPreviewHandler);
    }

    if (settingsProfileAutoThresholdInput) {
        settingsProfileAutoThresholdInput.addEventListener('input', routerThresholdPreviewHandler);
    }

    if (settingsProfileLaunchBtn) {
        settingsProfileLaunchBtn.addEventListener('click', (event) => {
            void startSettingsProfielFlow(event);
        });
    }

    if (settingsProfileSelect) {
        settingsProfileSelect.addEventListener('change', () => {
            if (appState.settingsProfileApplying || appState.settingsProfileLaunching || appState.settingsProfileRouterSaving) {
                return;
            }

            appState.settingsProfileSelected = normaliseerSettingsProfielNaam(settingsProfileSelect.value);
            appState.settingsProfileActionsEditorDirty = false;
            renderSettingsProfilePanel({
                selected: appState.settingsProfileSelected,
            });
        });
    }

    if (settingsProfileActionsEditor) {
        settingsProfileActionsEditor.addEventListener('input', () => {
            appState.settingsProfileActionsEditorDirty = true;
        });
    }

    if (settingsProfileActionsSaveBtn) {
        settingsProfileActionsSaveBtn.addEventListener('click', (event) => {
            void saveSettingsProfielActies(event);
        });
    }

    if (settingsProfileActionsResetBtn) {
        settingsProfileActionsResetBtn.addEventListener('click', (event) => {
            void resetSettingsProfielActies(event);
        });
    }

    if (settingsProfileActions) {
        settingsProfileActions.addEventListener('click', (event) => {
            const target = event.target;
            const button = target instanceof Element
                ? target.closest('button[data-profile-command]')
                : null;

            if (!(button instanceof HTMLButtonElement)) {
                return;
            }

            const commando = String(button.dataset.profileCommand || '').trim();
            const actieProfiel = normaliseerSettingsProfielNaam(button.dataset.profileName || appState.settingsProfileSelected);
            if (!commando || appState.settingsProfileApplying || appState.settingsProfileLaunching || appState.settingsProfileRouterSaving) {
                return;
            }

            void (async () => {
                if (actieProfiel !== appState.settingsProfile) {
                    const toegepast = await applySettingsProfiel(null, {
                        forcedProfile: actieProfiel,
                    });
                    if (!toegepast) {
                        return;
                    }
                }
                await sendCommand(commando, 'quick');
            })();
        });
    }

    if (websiteAuditForm) {
        websiteAuditForm.addEventListener('submit', async (event) => {
            event.preventDefault();

            const doelUrl = String(websiteAuditUrlInput ? websiteAuditUrlInput.value : '').trim();
            const profiel = String(websiteAuditProfileSelect ? websiteAuditProfileSelect.value : 'standard').trim().toLowerCase() || 'standard';
            if (!doelUrl) {
                setCommandStatus(uiTekst('website_audit_start_missing_url'));
                triggerHapticFeedback([90, 35, 90]);
                if (websiteAuditUrlInput) {
                    websiteAuditUrlInput.focus();
                }
                return;
            }

            if (websiteAuditStartBtn) {
                websiteAuditStartBtn.disabled = true;
            }

            try {
                const response = await fetchEchoApi('/api/website-audit/start', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        url: doelUrl,
                        profile: profiel,
                    }),
                }, 12000);

                const data = await response.json().catch(() => ({
                    status: 'error',
                    message: uiTekst('invalid_server_response'),
                }));

                const ok = response.ok && data.status === 'success';
                const melding = String(data.message || '').trim() || (ok
                    ? tekstVoorTaal('Website audit started.', 'Website-audit gestart.')
                    : tekstVoorTaal('Website audit could not start.', 'Website-audit kon niet starten.'));

                if (ok) {
                    addMessage('ai', melding);
                    setCommandStatus(melding);
                    triggerHapticFeedback(55);
                } else {
                    addMessage('error', melding);
                    setCommandStatus(melding);
                    triggerHapticFeedback([90, 35, 90]);
                }

                if (data && typeof data === 'object' && data.audit) {
                    renderWebsiteAuditPanel(data.audit);
                }
                void refreshDashboardTelemetry();
            } catch (error) {
                const rawMessage = error instanceof Error ? String(error.message || '').trim() : '';
                const melding = rawMessage || uiTekst('request_failed');
                addMessage('error', melding);
                setCommandStatus(melding);
                triggerHapticFeedback([90, 35, 90]);
            } finally {
                renderWebsiteAuditPanel(appState.websiteAuditSnapshot);
            }
        });
    }

    if (websiteAuditScheduleForm) {
        websiteAuditScheduleForm.addEventListener('submit', async (event) => {
            event.preventDefault();

            const enabled = Boolean(websiteAuditScheduleEnabledToggle && websiteAuditScheduleEnabledToggle.checked);
            const frequency = normaliseerWebsiteAuditFrequency(
                websiteAuditFrequencySelect ? websiteAuditFrequencySelect.value : 'daily'
            );
            const scheduledTime = normaliseerWebsiteAuditTijd(
                websiteAuditTimeInput ? websiteAuditTimeInput.value : '04:30'
            );
            const targetUrl = String(
                (websiteAuditScheduleUrlInput && websiteAuditScheduleUrlInput.value)
                || (websiteAuditUrlInput && websiteAuditUrlInput.value)
                || ''
            ).trim();
            const profile = String(
                (websiteAuditScheduleProfileSelect && websiteAuditScheduleProfileSelect.value)
                || (websiteAuditProfileSelect && websiteAuditProfileSelect.value)
                || 'standard'
            ).trim().toLowerCase() || 'standard';
            const alertWebhook = String(websiteAuditWebhookInput ? websiteAuditWebhookInput.value : '').trim();
            const alertScoreDrop = Number(websiteAuditAlertDropInput ? websiteAuditAlertDropInput.value : 12);
            const alertOnCritical = Boolean(websiteAuditAlertCriticalToggle && websiteAuditAlertCriticalToggle.checked);

            if (websiteAuditScheduleSaveBtn) {
                websiteAuditScheduleSaveBtn.disabled = true;
            }

            try {
                const response = await fetchEchoApi('/api/website-audit/schedule', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        enabled,
                        frequency,
                        scheduled_time: scheduledTime,
                        target_url: targetUrl,
                        profile,
                        alert_webhook: alertWebhook,
                        alert_score_drop: Number.isFinite(alertScoreDrop) ? Math.round(alertScoreDrop) : 12,
                        alert_on_critical: alertOnCritical,
                    }),
                }, 12000);

                const data = await response.json().catch(() => ({
                    status: 'error',
                    message: uiTekst('invalid_server_response'),
                }));

                const ok = response.ok && data.status === 'success';
                const melding = String(data.message || '').trim() || (ok
                    ? uiTekst('website_audit_schedule_save_success')
                    : uiTekst('website_audit_schedule_save_failed'));

                if (ok) {
                    addMessage('ai', melding);
                    setCommandStatus(melding);
                    triggerHapticFeedback(45);
                } else {
                    addMessage('error', melding);
                    setCommandStatus(melding);
                    triggerHapticFeedback([90, 35, 90]);
                }

                if (data && typeof data === 'object' && data.schedule) {
                    renderWebsiteAuditSchedulePanel(data.schedule);
                }
                void refreshDashboardTelemetry();
            } catch (error) {
                const rawMessage = error instanceof Error ? String(error.message || '').trim() : '';
                const melding = rawMessage || uiTekst('website_audit_schedule_save_failed');
                addMessage('error', melding);
                setCommandStatus(melding);
                triggerHapticFeedback([90, 35, 90]);
            } finally {
                if (websiteAuditScheduleSaveBtn) {
                    websiteAuditScheduleSaveBtn.disabled = false;
                }
            }
        });
    }

    if (websiteAuditDownloadJsonBtn) {
        websiteAuditDownloadJsonBtn.addEventListener('click', () => {
            downloadWebsiteAuditReport('json');
        });
    }

    if (websiteAuditDownloadMdBtn) {
        websiteAuditDownloadMdBtn.addEventListener('click', () => {
            downloadWebsiteAuditReport('markdown');
        });
    }

    if (websiteAuditDownloadPdfBtn) {
        websiteAuditDownloadPdfBtn.addEventListener('click', () => {
            downloadWebsiteAuditReport('pdf');
        });
    }

    if (commandInput) {
        commandInput.addEventListener('input', () => {
            refreshCommandSuggestionsFromInput();
            updateSettingsProfileIntentHint(commandInput.value);
        });

        commandInput.addEventListener('keydown', (event) => {
            if (event.key === 'ArrowUp') {
                event.preventDefault();
                const hadSuggestions = navigeerSuggesties(-1);
                if (!hadSuggestions) {
                    navigateCommandHistory(-1);
                }
            } else if (event.key === 'ArrowDown') {
                event.preventDefault();
                const hadSuggestions = navigeerSuggesties(1);
                if (!hadSuggestions) {
                    navigateCommandHistory(1);
                }
            } else if (event.key === 'Tab') {
                if (kiesActieveSuggestie()) {
                    event.preventDefault();
                }
            } else if (event.key === 'Escape') {
                hideCommandSuggestions();
            }
        });

        commandInput.addEventListener('blur', () => {
            window.setTimeout(() => {
                hideCommandSuggestions();
            }, 120);
        });

        commandInput.addEventListener('focus', () => {
            refreshCommandSuggestionsFromInput();
            updateSettingsProfileIntentHint(commandInput.value);
        });

        commandInput.addEventListener('blur', () => {
            if (!String(commandInput.value || '').trim()) {
                appState.settingsProfileIntentHint = null;
                renderSettingsProfilePanel({ intentHint: null });
            }
        });
    }

    if (actionFilterInput) {
        actionFilterInput.addEventListener('input', () => {
            applyActionFilter();
        });

        actionFilterInput.addEventListener('keydown', (event) => {
            if (event.key !== 'Escape') {
                return;
            }

            const heeftWaarde = Boolean(String(actionFilterInput.value || '').trim());
            if (heeftWaarde) {
                actionFilterInput.value = '';
                applyActionFilter();
                event.preventDefault();
                return;
            }

            actionFilterInput.blur();
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

    routineButtons.forEach((button) => {
        button.addEventListener('click', () => {
            const fillCommand = String(button.dataset.fillCommand || '').trim();
            if (fillCommand) {
                setCommandDraft(fillCommand);
                setCommandStatus(uiTekst('routine_prefill_ready'));
                triggerHapticFeedback(35);
                return;
            }

            const command = String(button.dataset.command || '').trim();
            if (!command) {
                return;
            }
            void sendCommand(command, 'quick');
        });
    });

    if (mobileCopyLinkBtn) {
        mobileCopyLinkBtn.addEventListener('click', async () => {
            const link = String(appState.mobilePrimaryUrl || '').trim();
            if (!link) {
                setCommandStatus(uiTekst('mobile_access_copy_missing'));
                triggerHapticFeedback([90, 40, 90]);
                return;
            }

            try {
                if (navigator.clipboard && typeof navigator.clipboard.writeText === 'function') {
                    await navigator.clipboard.writeText(link);
                } else {
                    throw new Error('clipboard unavailable');
                }
                setCommandStatus(uiTekst('mobile_access_copy_success'));
                triggerHapticFeedback(55);
            } catch (_error) {
                setCommandStatus(uiTekst('mobile_access_copy_failed'));
                triggerHapticFeedback([90, 35, 90]);
            }
        });
    }

    if (mobileOpenLinkBtn) {
        mobileOpenLinkBtn.addEventListener('click', () => {
            const link = String(appState.mobilePrimaryUrl || '').trim();
            if (!link) {
                setCommandStatus(uiTekst('mobile_access_open_missing'));
                triggerHapticFeedback([90, 35, 90]);
                return;
            }

            window.open(link, '_blank', 'noopener');
            triggerHapticFeedback(45);
        });
    }

    if (mobileSaveScreenshotBtn) {
        mobileSaveScreenshotBtn.addEventListener('click', () => {
            saveLatestScreenshotToPhone({ allowOpenFallback: true });
        });
    }

    if (mobileOpenScreenshotBtn) {
        mobileOpenScreenshotBtn.addEventListener('click', () => {
            openLatestScreenshotInBrowser();
        });
    }

    if (cameraStartBtn) {
        cameraStartBtn.addEventListener('click', () => {
            void voerCameraTaakUit(async () => {
                const gestart = await startCameraStream();
                if (gestart) {
                    triggerHapticFeedback(40);
                }
                return gestart;
            });
        });
    }

    if (cameraStopBtn) {
        cameraStopBtn.addEventListener('click', () => {
            if (appState.cameraBusy) {
                return;
            }
            stopCameraStream();
            zetCameraInsightTekst(uiTekst('camera_insight_idle'));
            setCommandStatus(uiTekst('camera_state_off'));
            renderCameraPanel();
            triggerHapticFeedback(30);
        });
    }

    if (cameraScanQrBtn) {
        cameraScanQrBtn.addEventListener('click', () => {
            void voerQrScanUit();
        });
    }

    if (cameraMoodBtn) {
        cameraMoodBtn.addEventListener('click', () => {
            void voerMoodCheckUit();
        });
    }

    if (cameraMuteBtn) {
        cameraMuteBtn.addEventListener('click', () => {
            if (appState.cameraBusy) {
                return;
            }
            setMicMuted(!appState.micMuted);
        });
    }

    if (cameraDeafenBtn) {
        cameraDeafenBtn.addEventListener('click', () => {
            if (appState.cameraBusy) {
                return;
            }
            setDeafenEnabled(!appState.deafenEnabled);
        });
    }

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

    window.addEventListener('resize', () => {
        updateViewportModeClass();
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
    appState.listeningWanted = false;
    setListening(false);
    setCommandStatus(appState.dashboardActive ? uiTekst('dashboard_mode_online') : uiTekst('voice_mode_online'));
    updateIdleVoiceStatus();

    const intro = uiTekst('intro_online', { name: appState.aiName });
    addMessage('ai', intro);
    const spoken = await speakText(intro, { profile: 'status', rate: 0.98, pitch: 1 });
    if (!spoken) {
        pulseSpeaking(1500);
    }
}

async function init() {
    const reloadedAfterSwReset = await resetLegacyServiceWorkerState();
    if (reloadedAfterSwReset) {
        return;
    }

    setMode(true);
    setThreatState('nominal', threatContextForLevel('nominal'), 0);
    setListening(false);
    setWakeArmed(false);
    setSpeaking(false);
    renderPendingConfirmation(null);
    initPanelCollapseControls();
    updateLocalizedUiLabels();
    renderMobileAccessPanel({});
    renderLatestScreenshotPanel({});
    renderWebsiteAuditPanel({});
    renderWebsiteAuditSchedulePanel({});
    renderCameraPanel();
    loadCommandHistory();
    updateViewportModeClass();

    const settingsTaak = loadSettings();
    initRecognition();
    wireEvents();

    setVoiceStatus(uiTekst('boot_running'));
    setCommandStatus(uiTekst('core_initializing'));

    await Promise.allSettled([
        settingsTaak,
        runBootSequence(),
    ]);

    void ensureBrowserVoices();
    void probePremiumTtsEndpoint(false);
    startVisualizer();
    startRuntimeVersionWatcher();
    startDashboardWatcher();
}

window.addEventListener('load', () => {
    void init();
});

window.addEventListener('beforeunload', () => {
    appState.listeningWanted = false;
    clearRecognitionRestartTimer();
    stopVisualizer();
    stopCameraStream();
    stopDashboardWatcher();
    stopRuntimeVersionWatcher();
});
