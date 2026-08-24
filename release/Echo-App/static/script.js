const speechBtn = document.getElementById('speechBtn');
const speechBtnLabel = document.getElementById('speechBtnLabel');
const settingsBtn = document.getElementById('settingsBtn');
const sendBtn = document.getElementById('sendBtn');
const commandInput = document.getElementById('commandInput');
const messagesDiv = document.getElementById('messages');
const statusDiv = document.getElementById('status');
const quickActions = document.getElementById('quickActions');
const optionDeck = document.getElementById('optionDeck');
const modeStrip = document.getElementById('modeStrip');
const promptStudio = document.getElementById('promptStudio');
const intentShell = document.getElementById('intentShell');
const intentChipButtons = document.querySelectorAll('.intent-chip');
const routePanel = document.getElementById('routePanel');
const routePanelStatus = document.getElementById('routePanelStatus');
const routeIntentToken = document.getElementById('routeIntentToken');
const routeToolToken = document.getElementById('routeToolToken');
const routeCategoryToken = document.getElementById('routeCategoryToken');
const routeAutomationToken = document.getElementById('routeAutomationToken');
const routePanelCopy = document.getElementById('routePanelCopy');
const commandLab = document.getElementById('commandLab');
const commandDiscoveryInput = document.getElementById('commandDiscoveryInput');
const commandDiscoveryList = document.getElementById('commandDiscoveryList');
const dashboardSurface = document.getElementById('dashboardSurface');
const quickActionButtons = document.querySelectorAll('.quick-action');
const featureActionButtons = document.querySelectorAll('.feature-action');
const promptSuggestionButtons = document.querySelectorAll('.prompt-chip');
const browserWorkbenchButtons = document.querySelectorAll('.workbench-action--browser');
const fileWorkbenchButtons = document.querySelectorAll('.workbench-action--file');
const subtitleText = document.getElementById('subtitleText');
const heroEyebrow = document.getElementById('heroEyebrow');
const heroTitle = document.getElementById('heroTitle');
const heroCopy = document.getElementById('heroCopy');
const heroTagVoice = document.getElementById('heroTagVoice');
const heroTagActions = document.getElementById('heroTagActions');
const heroTagThink = document.getElementById('heroTagThink');
const commandsTitle = document.getElementById('commandsTitle');
const commandsText = document.getElementById('commandsText');
const microphoneTitle = document.getElementById('microphoneTitle');
const microphoneText = document.getElementById('microphoneText');
const messageHint = document.getElementById('messageHint');
const controlLabel = document.getElementById('controlLabel');
const liveStatusLabel = document.getElementById('liveStatusLabel');
const tipsLabel = document.getElementById('tipsLabel');
const tipOne = document.getElementById('tipOne');
const tipTwo = document.getElementById('tipTwo');
const tipThree = document.getElementById('tipThree');
const echoFace = document.getElementById('echoFace');
const computerPanelLabel = document.getElementById('computerPanelLabel');
const computerPanelNote = document.getElementById('computerPanelNote');
const computerSystemLabel = document.getElementById('computerSystemLabel');
const computerMacroLabel = document.getElementById('computerMacroLabel');
const computerActionButtons = document.querySelectorAll('.computer-action');
const modeAiCard = document.getElementById('modeAiCard');
const modeAiValue = document.getElementById('modeAiValue');
const modeAiMeta = document.getElementById('modeAiMeta');
const modeThinkCard = document.getElementById('modeThinkCard');
const modeThinkValue = document.getElementById('modeThinkValue');
const modeThinkMeta = document.getElementById('modeThinkMeta');
const modeMemoryCard = document.getElementById('modeMemoryCard');
const modeMemoryValue = document.getElementById('modeMemoryValue');
const modeMemoryMeta = document.getElementById('modeMemoryMeta');
const modeAutomationCard = document.getElementById('modeAutomationCard');
const modeAutomationValue = document.getElementById('modeAutomationValue');
const modeAutomationMeta = document.getElementById('modeAutomationMeta');
const modeVoiceCard = document.getElementById('modeVoiceCard');
const modeVoiceValue = document.getElementById('modeVoiceValue');
const modeVoiceMeta = document.getElementById('modeVoiceMeta');
const dashboardModelValue = document.getElementById('dashboardModelValue');
const dashboardModelMeta = document.getElementById('dashboardModelMeta');
const dashboardCommandValue = document.getElementById('dashboardCommandValue');
const dashboardCommandMeta = document.getElementById('dashboardCommandMeta');
const dashboardUptimeValue = document.getElementById('dashboardUptimeValue');
const dashboardUptimeMeta = document.getElementById('dashboardUptimeMeta');
const dashboardAutomationValue = document.getElementById('dashboardAutomationValue');
const dashboardAutomationMeta = document.getElementById('dashboardAutomationMeta');
const dashboardGeneratedAtLabel = document.getElementById('dashboardGeneratedAtLabel');
const dashboardRecentActionsList = document.getElementById('dashboardRecentActionsList');
const plannerTaskCountPill = document.getElementById('plannerTaskCountPill');
const plannerTimerCountPill = document.getElementById('plannerTimerCountPill');
const plannerReminderCountPill = document.getElementById('plannerReminderCountPill');
const plannerQuickInput = document.getElementById('plannerQuickInput');
const plannerQuickTaskBtn = document.getElementById('plannerQuickTaskBtn');
const plannerQuickReminderBtn = document.getElementById('plannerQuickReminderBtn');
const plannerTasksList = document.getElementById('plannerTasksList');
const plannerTimersList = document.getElementById('plannerTimersList');
const plannerRemindersList = document.getElementById('plannerRemindersList');
const plannerNotificationsList = document.getElementById('plannerNotificationsList');
const systemScanCard = document.getElementById('systemScanCard');
const systemScanVisual = document.getElementById('systemScanVisual');
const systemScanMessage = document.getElementById('systemScanMessage');
const systemScanStatusText = document.getElementById('systemScanStatusText');
const systemScanStageText = document.getElementById('systemScanStageText');
const systemScanProgressFill = document.getElementById('systemScanProgressFill');
const systemScanProgressText = document.getElementById('systemScanProgressText');
const systemScanStartedAt = document.getElementById('systemScanStartedAt');
const systemScanUpdatedAt = document.getElementById('systemScanUpdatedAt');
const systemScanLogList = document.getElementById('systemScanLogList');
const browserWorkbenchUrl = document.getElementById('browserWorkbenchUrl');
const browserWorkbenchFormValues = document.getElementById('browserWorkbenchFormValues');
const browserWorkbenchMeta = document.getElementById('browserWorkbenchMeta');
const fileWorkbenchPath = document.getElementById('fileWorkbenchPath');
const fileWorkbenchRewrite = document.getElementById('fileWorkbenchRewrite');
const workspaceSearchInput = document.getElementById('workspaceSearchInput');
const fileWorkbenchMeta = document.getElementById('fileWorkbenchMeta');
const voiceVisualizerTitle = document.getElementById('voiceVisualizerTitle');
const voiceVisualizerCopy = document.getElementById('voiceVisualizerCopy');
const voiceVisualizerMicLabel = document.getElementById('voiceVisualizerMicLabel');
const voiceVisualizerAiLabel = document.getElementById('voiceVisualizerAiLabel');
const voiceVisualizerStatus = document.getElementById('voiceVisualizerStatus');
const voiceVisualizerCanvas = document.getElementById('voiceVisualizerCanvas');
const safetyConfirmModal = document.getElementById('safetyConfirmModal');
const safetyConfirmKicker = document.getElementById('safetyConfirmKicker');
const safetyConfirmTitle = document.getElementById('safetyConfirmTitle');
const safetyConfirmBody = document.getElementById('safetyConfirmBody');
const safetyConfirmTarget = document.getElementById('safetyConfirmTarget');
const safetyConfirmYesBtn = document.getElementById('safetyConfirmYesBtn');
const safetyConfirmNoBtn = document.getElementById('safetyConfirmNoBtn');

// Settings Modal
const modal = document.getElementById('settingsModal');
const closeModal = document.getElementById('closeModal');
const saveSettingsBtn = document.getElementById('saveSettingsBtn');
const stemSelect = document.getElementById('stemSelect');
const testVoiceBtn = document.getElementById('testVoiceBtn');
const taalSelect = document.getElementById('taal');
const settingsKicker = document.getElementById('settingsKicker');
const settingsTitle = document.getElementById('settingsTitle');
const settingsSubtitle = document.getElementById('settingsSubtitle');
const settingsSectionIdentity = document.getElementById('settingsSectionIdentity');
const settingsSectionDestinations = document.getElementById('settingsSectionDestinations');
const settingsSectionVoice = document.getElementById('settingsSectionVoice');
const settingsSectionBehavior = document.getElementById('settingsSectionBehavior');
const naamLabel = document.getElementById('naamLabel');
const clientNaamLabel = document.getElementById('clientNaamLabel');
const taalLabel = document.getElementById('taalLabel');
const youtubeUrlLabel = document.getElementById('youtubeUrlLabel');
const googleUrlLabel = document.getElementById('googleUrlLabel');
const wakeWordLabel = document.getElementById('wakeWordLabel');
const stemSelectLabel = document.getElementById('stemSelectLabel');
const computerBesturingLabelText = document.getElementById('computerBesturingLabelText');
const computerBesturingNote = document.getElementById('computerBesturingNote');
const emojiGebruikLabelText = document.getElementById('emojiGebruikLabelText');
const begroetingTonenLabelText = document.getElementById('begroetingTonenLabelText');
const spraakUitgangLabelText = document.getElementById('spraakUitgangLabelText');
const clientNaamInput = document.getElementById('clientNaam');

const UI_TEKST = {
    English: {
        docLang: 'en',
        speechLang: 'en-US',
        subtitle: 'Your personal AI assistant',
        heroEyebrow: 'Resonance Ready',
        heroTitle: 'Talk, type, search, and think out loud.',
        heroCopy: 'Echo works best when the next action is close: voice commands, quick buttons, and a live conversation area in one flow.',
        heroTagVoice: 'Voice-first',
        heroTagActions: 'Fast actions',
        heroTagThink: 'Think with Echo',
        commandsTitle: 'Talk naturally',
        commandsText: 'You do not need exact commands. Tell Echo what you want to open, read, summarize, explain, or plan, and it will choose the best route.',
        microphoneTitle: '🎙️ Microphone Mode:',
        microphoneText: 'Click <code>Microphone Always On</code>, say <code>hey echo</code>, then say your command.',
        voiceVisualizerTitle: 'Voice activity',
        voiceVisualizerCopy: 'Watch the waveform respond to your microphone while Echo listens and pulse when Echo speaks back.',
        voiceVisualizerMicLabel: 'Microphone',
        voiceVisualizerAiLabel: 'Echo voice',
        voiceVisualizerStateIdle: 'Idle',
        voiceVisualizerStateListening: 'Listening',
        voiceVisualizerStateSpeaking: 'Speaking',
        voiceVisualizerStateWarning: 'Mic access needed',
        commandPlaceholder: 'Type a command for Echo',
        send: 'Send',
        quickActionsAria: 'Quick commands',
        optionsAria: 'Echo options',
        modeStripAria: 'Echo modes',
        promptStudioAria: 'Prompt studio',
        dashboardSurfaceAria: 'Echo dashboard',
        modeAiLabel: 'AI',
        modeThinkLabel: 'Thinking',
        modeMemoryLabel: 'Memory',
        modeAutomationLabel: 'Automation',
        modeVoiceLabel: 'Voice',
        modeLoadingValue: 'Checking',
        modeLoadingMeta: 'Syncing with settings',
        modeStateOn: 'On',
        modeStateOff: 'Off',
        modeAiValueBuiltin: 'Built-in only',
        modeAiValueModel: 'Model on',
        modeAiValueAgent: 'Agent-first',
        modeAiMetaBuiltin: 'Local rules and tools only',
        modeAiMetaModel: 'Model: {model}',
        modeThinkValueGuided: 'Guided',
        modeThinkValueDirect: 'Direct',
        modeThinkMetaPriorityOn: 'Plans are reordered for speed',
        modeThinkMetaPriorityOff: 'Plans stay in original order',
        modeMemoryMetaOn: 'Long-term memory is available',
        modeMemoryMetaOff: 'No memory context is used',
        modeAutomationValueReady: 'Unlocked',
        modeAutomationValueLocked: 'Locked',
        modeAutomationMetaReady: 'Say enable automation mode when needed',
        modeAutomationMetaLocked: 'Turn on advanced control in settings',
        modeVoiceValueOn: 'Voice on',
        modeVoiceValueOff: 'Voice off',
        modeVoiceMeta: '{language} · wake word {wakeWord}',
        dashboardEyebrow: 'Live dashboard',
        dashboardTitle: 'See what Echo is doing now',
        dashboardCopy: 'Runtime health, recent actions, and active tools update here automatically.',
        dashboardMetricModelLabel: 'Model',
        dashboardMetricCommandLabel: 'Last command',
        dashboardMetricUptimeLabel: 'Uptime',
        dashboardMetricAutomationLabel: 'Automation',
        dashboardMetricWaitingMeta: 'Waiting for dashboard data',
        dashboardNoCommandValue: 'None yet',
        dashboardNoCommandMeta: 'No actions recorded yet',
        dashboardRecentActionsLabel: 'Recent actions',
        dashboardRecentActionsEmpty: 'Recent actions will appear here after you use Echo.',
        dashboardGeneratedAtLabelText: 'Last sync {time}',
        dashboardCommandMetaSuccess: '{duration} ms · completed',
        dashboardCommandMetaError: '{duration} ms · failed',
        dashboardAutomationActiveValue: 'Live',
        dashboardAutomationReadyValue: 'Ready',
        dashboardAutomationLockedValue: 'Locked',
        dashboardAutomationActiveMeta: '{remaining} left in this automation window',
        dashboardAutomationReadyMeta: 'Advanced control is allowed but not active yet',
        dashboardAutomationLockedMeta: 'Turn on advanced control in settings first',
        systemScanEyebrow: 'System diagnostics',
        systemScanTitle: 'Windows integrity scan',
        systemScanIdleMessage: 'System scan is idle. Say start system scan when you are ready.',
        systemScanRunningMessage: 'System Scan in Progress. DISM and SFC are running in the background.',
        systemScanCompletedMessage: 'System scan completed. DISM and SFC checks finished.',
        systemScanErrorMessage: 'System scan stopped with an error.',
        systemScanStatusIdle: 'Idle',
        systemScanStatusRunning: 'Scanning',
        systemScanStatusCompleted: 'Completed',
        systemScanStatusError: 'Attention',
        systemScanStageIdle: 'No diagnostic scan running.',
        systemScanLogLabel: 'Recent scan logs',
        systemScanLogsEmpty: 'No scan logs yet.',
        systemScanStartedLabel: 'Started {time}',
        systemScanUpdatedLabel: 'Updated {time}',
        systemScanProgressLabel: 'Progress {value}%',
        safetyConfirmKicker: 'Safety check',
        safetyConfirmTitle: 'Approve this action?',
        safetyConfirmFallback: 'Echo is waiting for your decision on a sensitive action.',
        safetyConfirmTargetPrefix: 'Target: {target}',
        safetyConfirmYes: 'Yes, continue',
        safetyConfirmNo: 'No, cancel',
        safetyConfirmCommandConfirm: 'Approve pending action',
        safetyConfirmCommandCancel: 'Cancel pending action',
        plannerBoardEyebrow: 'Planner board',
        plannerBoardTitle: 'Tasks, timers, reminders',
        plannerQuickLabel: 'Quick add',
        plannerQuickPlaceholder: 'Add a task or reminder idea',
        plannerQuickTaskBtn: 'Add task',
        plannerQuickReminderBtn: 'Remind in 30m',
        plannerQuickNeedText: 'Type a task or reminder first.',
        plannerTasksLabel: 'Open tasks',
        plannerTimersLabel: 'Active timers',
        plannerRemindersLabel: 'Pending reminders',
        plannerNotificationsLabel: 'Notifications',
        plannerTasksEmpty: 'No open tasks.',
        plannerTimersEmpty: 'No active timers.',
        plannerRemindersEmpty: 'No pending reminders.',
        plannerNotificationsEmpty: 'No recent notifications.',
        plannerTaskCountLabel: '{count} tasks',
        plannerTimerCountLabel: '{count} timers',
        plannerReminderCountLabel: '{count} reminders',
        browserWorkbenchEyebrow: 'Browser workbench',
        browserWorkbenchTitle: 'Read, open, summarize, fill',
        browserWorkbenchCopy: 'Use the current tab or a pasted URL, then trigger one focused browser task.',
        browserWorkbenchUrlLabel: 'Page or URL',
        browserWorkbenchUrlPlaceholder: 'https://example.com or leave empty for current tab',
        browserWorkbenchFormLabel: 'Form values',
        browserWorkbenchFormPlaceholder: 'One value per line or comma separated',
        browserActionOpenUrl: 'Open URL',
        browserActionReadCurrent: 'Read current',
        browserActionSummarizeCurrent: 'Summarize current',
        browserActionSummarizeUrl: 'Summarize URL',
        browserActionFillForm: 'Fill form',
        browserWorkbenchMetaEmpty: 'Recent browser action: none yet.',
        browserWorkbenchNeedUrl: 'Enter a URL first.',
        browserWorkbenchNeedFormValues: 'Enter form values first.',
        fileWorkbenchEyebrow: 'File workbench',
        fileWorkbenchTitle: 'Preview, summarize, rewrite',
        fileWorkbenchCopy: 'Pick a suggested file, inspect it, summarize it, or prepare an AI rewrite.',
        fileWorkbenchPathLabel: 'Suggested file',
        fileWorkbenchEmptyOption: 'Select a file',
        fileWorkbenchRewriteLabel: 'Rewrite instruction',
        fileWorkbenchRewritePlaceholder: 'Make it shorter, clearer, more friendly, or more technical',
        fileActionRead: 'Preview file',
        fileActionSummarize: 'Summarize file',
        fileActionRewrite: 'Rewrite file',
        workspaceSearchLabel: 'Workspace search',
        workspaceSearchPlaceholder: 'Search for ollama, planner, README, or a file name',
        fileActionSearch: 'Search workspace',
        fileWorkbenchMetaEmpty: 'Suggested files update automatically from the workspace.',
        fileWorkbenchNeedPath: 'Choose a file first.',
        fileWorkbenchNeedRewrite: 'Type a rewrite instruction first.',
        fileWorkbenchNeedSearch: 'Type a search query first.',
        quickAction_youtube: 'Open YouTube',
        quickAction_google: 'Open Google',
        quickAction_calculator: 'Open Calculator',
        quickAction_think: 'Think With Echo',
        quickAction_folder: 'Create Demo Folder',
        quickAction_explorer: 'Open Explorer',
        featureAction_task_list: 'Show Tasks',
        featureAction_agenda_show: 'Show Agenda',
        featureAction_timer_5: 'Start 5 Min Timer',
        featureAction_reminder_break: 'Stretch Reminder',
        featureAction_browser_current_url: 'Current URL',
        featureAction_browser_read_page: 'Read This Page',
        featureAction_browser_summarize_page: 'Summarize This Page',
        featureAction_browser_focus_edge: 'Focus Edge',
        featureAction_file_summarize_readme: 'Summarize README',
        featureAction_workspace_search_ollama: 'Search Workspace',
        featureAction_memory_show: 'What Do You Remember?',
        featureAction_system_info: 'System Info',
        panelPlannerLabel: 'Planner',
        panelPlannerCopy: 'Jump into tasks, timers, and reminders without typing the full sentence every time.',
        panelBrowserLabel: 'Browser',
        panelBrowserCopy: 'Use the active tab as context for reading, summarizing, and navigation commands.',
        panelWorkspaceLabel: 'Workspace',
        panelWorkspaceCopy: 'Surface memory, file tools, and system insight from one place.',
        promptStudioEyebrow: 'Prompt studio',
        promptStudioTitle: 'Start from a stronger prompt',
        promptStudioCopy: 'Tap a pattern to fill the composer, adjust it if you want, then send it.',
        promptCardPlanningLabel: 'Plan',
        promptCardResearchLabel: 'Research',
        promptCardBuildLabel: 'Build',
        promptChip_plan_day: 'Plan my day',
        promptChip_focus_hour: 'Help me focus for an hour',
        promptChip_set_break_reminder: 'Set a break reminder',
        promptChip_summarize_tab: 'Summarize this page',
        promptChip_search_workspace: 'Search the workspace',
        promptChip_memory_review: 'What do you remember?',
        promptChip_rewrite_readme: 'Rewrite README',
        promptChip_system_review: 'Check my system',
        promptChip_automation_ready: 'Prepare automation',
        intentGuideEyebrow: 'Start here',
        intentGuideTitle: 'Tell Echo what kind of help you want',
        intentGuideCopy: 'Echo is more consistent when it knows whether you want an explanation, an action, or both in one pass.',
        intentChip_answer: 'Explain something',
        intentChip_action: 'Do a task',
        intentChip_hybrid: 'Do + explain',
        intentChip_automation: 'Automation ready',
        routePanelEyebrow: 'Execution path',
        routePanelTitle: 'See how Echo routed your request',
        routePanelCopyIdle: 'Echo will show whether it detected a question, an action, or a mixed request.',
        routePanelCopyLocked: 'Automation is locked. Turn on advanced control in settings before browser and desktop control tasks.',
        routePanelCopyReady: 'Automation is allowed. Say enable automation mode when you want active browser or desktop control.',
        routePanelCopyLive: 'Automation is live. Browser and desktop actions can run until the window closes.',
        routeStatusWaiting: 'Waiting',
        routeStatusRouting: 'Routing',
        routeStatusAnswered: 'Answered',
        routeStatusCompleted: 'Completed',
        routeStatusFallback: 'Fallback',
        routeStatusError: 'Error',
        routeStatusToolPlanning: 'Planning tools',
        routeTokenIntent: 'Intent: {value}',
        routeTokenTool: 'Tool: {value}',
        routeTokenCategory: 'Category: {value}',
        routeTokenAutomation: 'Automation: {value}',
        routeIntent_answer: 'Answer',
        routeIntent_action: 'Action',
        routeIntent_hybrid: 'Mixed',
        routeIntent_memory: 'Memory',
        routeIntent_unknown: 'Unknown',
        routeTool_builtin_answer: 'Built-in answer',
        routeTool_online_answer: 'Online answer',
        routeTool_guided_answer: 'Think mode',
        routeTool_local_plan: 'Local tools',
        routeTool_online_action_planner: 'AI tool plan',
        routeTool_memory: 'Memory',
        routeTool_fallback: 'Fallback',
        routeTool_error: 'Error',
        routeCategory_answer: 'Reasoning',
        routeCategory_browser: 'Browser',
        routeCategory_workspace: 'Workspace',
        routeCategory_planner: 'Planner',
        routeCategory_automation: 'Automation',
        routeCategory_system: 'System',
        routeCategory_general: 'General',
        routeCategory_memory: 'Memory',
        automationStateLocked: 'Locked',
        automationStateReady: 'Ready',
        automationStateLive: 'Live ({remaining})',
        automationNeedsSettings: 'Turn on advanced control in settings first.',
        automationNeedsEnable: 'Enable automation mode first for this action.',
        commandDrawerSummary: 'Need ideas? Show a few examples',
        commandLabEyebrow: 'Command ideas',
        commandLabTitle: 'Peek at a few examples',
        commandLabCopy: 'Open this only when you want inspiration. Tap an example to fill the composer, then adjust it in your own words.',
        commandDiscoveryLabel: 'Find a pattern',
        commandDiscoveryPlaceholder: 'Search browser, planner, file, memory, or automation commands',
        commandDiscoveryEmpty: 'No matching command examples yet. Try browser, planner, file, memory, or automation.',
        hint: 'Type a command or use the microphone. Example: show agenda, summarize this page, summarize README.md, or what do you remember about me. Browser reading needs automation mode.',
        controlLabel: 'Control',
        computerPanelLabel: 'Computer Control',
        computerPanelNote: 'Enable automation mode first for screenshots, macros, and window control.',
        computerSystemLabel: 'Session + Windows',
        computerMacroLabel: 'App Macros',
        computerAction_automation_enable: 'Enable Automation',
        computerAction_automation_disable: 'Disable Automation',
        computerAction_system_scan_start: 'Start System Scan',
        computerAction_system_scan_status: 'Check Scan Status',
        computerAction_screenshot: 'Take Screenshot',
        computerAction_maximize_window: 'Maximize Window',
        computerAction_close_window: 'Close Window',
        computerAction_focus_edge: 'Focus Edge',
        computerAction_volume_up: 'Volume Up',
        computerAction_mute_volume: 'Mute Volume',
        computerAction_vscode_new_file: 'VS Code New File',
        computerAction_edge_inprivate: 'Edge InPrivate',
        computerAction_discord_search: 'Discord Search',
        computerAction_discord_mute: 'Discord Mute',
        computerAction_whatsapp_new_chat: 'WhatsApp New Chat',
        computerAction_steam_search: 'Steam Search',
        liveStatusLabel: 'Live Status',
        tipsLabel: 'Better Results',
        tipOne: 'Ask for one task at a time when you want speed.',
        tipTwo: 'Use the planner, browser, and workspace panels when you want the newer features without remembering the exact command.',
        tipThree: 'Ask Echo to think with you or rewrite a file when you need help shaping work.',
        settingsKicker: 'Tune Echo',
        settingsTitle: '⚙️ Settings',
        settingsSubtitle: 'Adjust voice, language, quick destinations, assistant modes, and how Echo responds.',
        settingsSectionIdentity: 'Profile',
        settingsSectionDestinations: 'Shortcuts',
        settingsSectionVoice: 'Voice',
        settingsSectionBehavior: 'Behavior',
        settingsSectionModes: 'Assistant modes',
        settingsModesNote: 'These switches let you decide whether Echo should use memory, multi-step planning, and the connected AI model more aggressively.',
        aiName: 'AI name:',
        clientNameLabel: 'Client name:',
        clientNamePlaceholder: 'Your name',
        language: 'Language:',
        youtubeUrl: 'YouTube URL:',
        googleUrl: 'Google URL:',
        wakeWord: 'Wake word:',
        chooseVoice: 'Choose voice:',
        computerControl: 'Allow advanced computer control',
        computerControlNote: 'This unlocks mouse, keyboard, screenshot, wifi, bluetooth, and app macro commands. You still need to say enable automation mode before Echo can use them.',
        useEmojis: 'Use emojis',
        showGreeting: 'Show greeting',
        voiceOutput: 'Voice output (text-to-speech)',
        agentModeLabel: 'Enable think-with-me mode',
        primaryAgentLabel: 'Use AI agent first',
        onlineAiModeLabel: 'Allow connected AI answers',
        memoryModeLabel: 'Use long-term memory',
        priorityModeLabel: 'Reorder multi-step plans',
        saveSettings: '💾 Save settings',
        settingsButton: '⚙️ Settings',
        micOrbReady: 'Microphone Ready',
        micOrbListening: 'Listening...',
        micOrbPaused: 'Tap To Start',
        micOrbSpeaking: 'Echo Speaking',
        micOrbUnavailable: 'No Mic Support',
        microphoneAlwaysOn: '🎤 Microphone Always On',
        microphoneActive: '🎤 Microphone Active',
        microphonePaused: '🎤 Start Microphone',
        automaticVoice: 'Automatic (English)',
        wakeWordPlaceholder: 'hey echo',
        defaultWakeWord: 'hey echo',
        testVoice: '🔊 Test voice',
        testVoiceSample: 'Hey, how can I help you?',
        typeCommandFirst: 'Type a command first.',
        working: 'Working...',
        heard: 'Heard: {text}',
        speechHeardAction: 'I heard: {text}. I will do that now.',
        successVoice: 'Done. Echo replied by voice.',
        successPlain: 'Done.',
        genericError: 'Something went wrong.',
        connectionProblem: 'There was a problem sending the request.',
        connectionError: 'Connection error.',
        speechUnsupported: 'This browser does not support speech recognition.',
        reactivateVoice: 'Click the microphone once to reactivate voice.',
        awakeReply: 'Hey, how can I help you?',
        awakeReplyPersonal: 'Hey {clientName}, how can I assist you?',
        awakeStatus: 'Echo is awake. Say your next command.',
        sleepReply: 'Okay, going back to standby.',
        speechError: 'Speech error. Check microphone permissions.',
        speechErrorVoice: 'I cannot hear you clearly. Check your microphone.',
        microphoneActivated: 'Microphone activated. Say: {wakeWord}',
        microphonePermission: 'Could not start the microphone. Check browser permissions.',
        microphoneStaysOn: 'The microphone stays on.',
        microphoneStopped: 'Microphone stopped.',
        savingFailed: 'Saving failed.',
        settingsSaved: 'Settings saved.',
        voiceTestPlayed: 'Voice test played.',
        promptReady: 'Prompt ready. Edit it or press Send.',
        grantPermission: 'Click the microphone once to grant permission.',
        greeting: 'Hello! Type a command or say hey echo to wake me up.',
        voiceModeActive: 'Voice mode active. Say: {wakeWord}',
        textModeActive: 'Text mode active. Use the command box to control Echo.',
        standby: 'Standby. Say: {wakeWord}',
        errorPrefix: 'Error: '
    },
    Nederlands: {
        docLang: 'nl',
        speechLang: 'nl-NL',
        subtitle: 'Jouw persoonlijke AI-assistent',
        heroEyebrow: 'Klaar om mee te denken',
        heroTitle: 'Praat, typ, zoek en denk samen hardop.',
        heroCopy: 'Echo werkt het best als de volgende stap dichtbij is: spraak, snelle acties en een live gesprek in een vloeiende werkruimte.',
        heroTagVoice: 'Spraak eerst',
        heroTagActions: 'Snelle acties',
        heroTagThink: 'Denk met Echo',
        commandsTitle: 'Praat gewoon natuurlijk',
        commandsText: 'Je hebt geen exacte commando\'s nodig. Zeg wat Echo moet openen, lezen, samenvatten, uitleggen of plannen, dan kiest hij zelf de beste route.',
        microphoneTitle: '🎙️ Microfoonmodus:',
        microphoneText: 'Klik op <code>Microfoon altijd aan</code>, zeg <code>hee echo</code> en daarna je opdracht.',
        voiceVisualizerTitle: 'Stemactiviteit',
        voiceVisualizerCopy: 'Zie de golfvorm reageren op je microfoon terwijl Echo luistert en pulseren wanneer Echo terugpraat.',
        voiceVisualizerMicLabel: 'Microfoon',
        voiceVisualizerAiLabel: 'Echo-stem',
        voiceVisualizerStateIdle: 'Stand-by',
        voiceVisualizerStateListening: 'Luistert',
        voiceVisualizerStateSpeaking: 'Praat',
        voiceVisualizerStateWarning: 'Microfoontoegang nodig',
        commandPlaceholder: 'Typ een opdracht voor Echo',
        send: 'Verstuur',
        quickActionsAria: 'Snelle opdrachten',
        optionsAria: 'Echo-opties',
        modeStripAria: 'Echo-modi',
        promptStudioAria: 'Promptstudio',
        modeAiLabel: 'AI',
        modeThinkLabel: 'Denken',
        modeMemoryLabel: 'Geheugen',
        modeAutomationLabel: 'Automation',
        modeVoiceLabel: 'Stem',
        modeLoadingValue: 'Controleren',
        modeLoadingMeta: 'Bezig met instellingen synchroniseren',
        modeStateOn: 'Aan',
        modeStateOff: 'Uit',
        modeAiValueBuiltin: 'Alleen ingebouwd',
        modeAiValueModel: 'Model aan',
        modeAiValueAgent: 'Agent eerst',
        modeAiMetaBuiltin: 'Alleen lokale regels en tools',
        modeAiMetaModel: 'Model: {model}',
        modeThinkValueGuided: 'Meedenkend',
        modeThinkValueDirect: 'Direct',
        modeThinkMetaPriorityOn: 'Plannen worden herschikt voor snelheid',
        modeThinkMetaPriorityOff: 'Plannen blijven in oorspronkelijke volgorde',
        modeMemoryMetaOn: 'Langetermijngeheugen is beschikbaar',
        modeMemoryMetaOff: 'Er wordt geen geheugensamenvatting gebruikt',
        modeAutomationValueReady: 'Ontgrendeld',
        modeAutomationValueLocked: 'Vergrendeld',
        modeAutomationMetaReady: 'Zeg schakel automation-modus in wanneer nodig',
        modeAutomationMetaLocked: 'Zet geavanceerde besturing aan in instellingen',
        modeVoiceValueOn: 'Stem aan',
        modeVoiceValueOff: 'Stem uit',
        modeVoiceMeta: '{language} · wake word {wakeWord}',
        dashboardEyebrow: 'Live dashboard',
        dashboardTitle: 'Zie wat Echo nu doet',
        dashboardCopy: 'Runtime-status, recente acties en actieve tools verversen hier automatisch.',
        dashboardMetricModelLabel: 'Model',
        dashboardMetricCommandLabel: 'Laatste opdracht',
        dashboardMetricUptimeLabel: 'Actief sinds',
        dashboardMetricAutomationLabel: 'Automation',
        dashboardMetricWaitingMeta: 'Wacht op dashboarddata',
        dashboardNoCommandValue: 'Nog niets',
        dashboardNoCommandMeta: 'Er zijn nog geen acties vastgelegd',
        dashboardRecentActionsLabel: 'Recente acties',
        dashboardRecentActionsEmpty: 'Recente acties verschijnen hier nadat je Echo gebruikt.',
        dashboardGeneratedAtLabelText: 'Laatste sync {time}',
        dashboardCommandMetaSuccess: '{duration} ms · voltooid',
        dashboardCommandMetaError: '{duration} ms · mislukt',
        dashboardAutomationActiveValue: 'Actief',
        dashboardAutomationReadyValue: 'Klaar',
        dashboardAutomationLockedValue: 'Vergrendeld',
        dashboardAutomationActiveMeta: '{remaining} over in dit automation-venster',
        dashboardAutomationReadyMeta: 'Geavanceerde besturing mag, maar staat nog niet aan',
        dashboardAutomationLockedMeta: 'Zet eerst geavanceerde besturing aan in instellingen',
        systemScanEyebrow: 'Systeemdiagnostiek',
        systemScanTitle: 'Windows integriteitsscan',
        systemScanIdleMessage: 'Systeemscan staat stand-by. Zeg start systeemscan wanneer je klaar bent.',
        systemScanRunningMessage: 'Systeemscan bezig. DISM en SFC draaien op de achtergrond.',
        systemScanCompletedMessage: 'Systeemscan voltooid. DISM- en SFC-controles zijn afgerond.',
        systemScanErrorMessage: 'Systeemscan is gestopt met een fout.',
        systemScanStatusIdle: 'Stand-by',
        systemScanStatusRunning: 'Scannen',
        systemScanStatusCompleted: 'Voltooid',
        systemScanStatusError: 'Let op',
        systemScanStageIdle: 'Er draait nu geen diagnostische scan.',
        systemScanLogLabel: 'Recente scanlogs',
        systemScanLogsEmpty: 'Nog geen scanlogs.',
        systemScanStartedLabel: 'Gestart {time}',
        systemScanUpdatedLabel: 'Bijgewerkt {time}',
        systemScanProgressLabel: 'Voortgang {value}%',
        safetyConfirmKicker: 'Veiligheidscontrole',
        safetyConfirmTitle: 'Deze actie goedkeuren?',
        safetyConfirmFallback: 'Echo wacht op je keuze voor een gevoelige actie.',
        safetyConfirmTargetPrefix: 'Doel: {target}',
        safetyConfirmYes: 'Ja, doorgaan',
        safetyConfirmNo: 'Nee, annuleren',
        safetyConfirmCommandConfirm: 'Bevestig wachtende actie',
        safetyConfirmCommandCancel: 'Annuleer wachtende actie',
        plannerBoardEyebrow: 'Plannerbord',
        plannerBoardTitle: 'Taken, timers, herinneringen',
        plannerQuickLabel: 'Snel toevoegen',
        plannerQuickPlaceholder: 'Voeg een taak of herinnering toe',
        plannerQuickTaskBtn: 'Taak toevoegen',
        plannerQuickReminderBtn: 'Herinner over 30m',
        plannerQuickNeedText: 'Typ eerst een taak of herinnering.',
        plannerTasksLabel: 'Open taken',
        plannerTimersLabel: 'Actieve timers',
        plannerRemindersLabel: 'Open herinneringen',
        plannerNotificationsLabel: 'Notificaties',
        plannerTasksEmpty: 'Geen open taken.',
        plannerTimersEmpty: 'Geen actieve timers.',
        plannerRemindersEmpty: 'Geen open herinneringen.',
        plannerNotificationsEmpty: 'Geen recente notificaties.',
        plannerTaskCountLabel: '{count} taken',
        plannerTimerCountLabel: '{count} timers',
        plannerReminderCountLabel: '{count} herinneringen',
        browserWorkbenchEyebrow: 'Browser-workbench',
        browserWorkbenchTitle: 'Lezen, openen, samenvatten, invullen',
        browserWorkbenchCopy: 'Gebruik de huidige tab of een geplakte URL en start daarna één gerichte browsertak.',
        browserWorkbenchUrlLabel: 'Pagina of URL',
        browserWorkbenchUrlPlaceholder: 'https://example.com of leeg laten voor de huidige tab',
        browserWorkbenchFormLabel: 'Formulierwaarden',
        browserWorkbenchFormPlaceholder: 'Eén waarde per regel of komma-gescheiden',
        browserActionOpenUrl: 'Open URL',
        browserActionReadCurrent: 'Lees huidige',
        browserActionSummarizeCurrent: 'Vat huidige samen',
        browserActionSummarizeUrl: 'Vat URL samen',
        browserActionFillForm: 'Vul formulier',
        browserWorkbenchMetaEmpty: 'Recente browseractie: nog niets.',
        browserWorkbenchNeedUrl: 'Vul eerst een URL in.',
        browserWorkbenchNeedFormValues: 'Vul eerst formulierwaarden in.',
        fileWorkbenchEyebrow: 'Bestands-workbench',
        fileWorkbenchTitle: 'Preview, samenvatten, herschrijven',
        fileWorkbenchCopy: 'Kies een voorgesteld bestand, bekijk het, vat het samen of bereid een AI-herschrijving voor.',
        fileWorkbenchPathLabel: 'Voorgesteld bestand',
        fileWorkbenchEmptyOption: 'Kies een bestand',
        fileWorkbenchRewriteLabel: 'Herschrijfinstructie',
        fileWorkbenchRewritePlaceholder: 'Maak het korter, duidelijker, vriendelijker of technischer',
        fileActionRead: 'Preview bestand',
        fileActionSummarize: 'Vat bestand samen',
        fileActionRewrite: 'Herschrijf bestand',
        workspaceSearchLabel: 'Workspace zoeken',
        workspaceSearchPlaceholder: 'Zoek naar ollama, planner, README of een bestandsnaam',
        fileActionSearch: 'Zoek workspace',
        fileWorkbenchMetaEmpty: 'Voorgestelde bestanden verversen automatisch vanuit de workspace.',
        fileWorkbenchNeedPath: 'Kies eerst een bestand.',
        fileWorkbenchNeedRewrite: 'Typ eerst een herschrijfinstructie.',
        fileWorkbenchNeedSearch: 'Typ eerst een zoekopdracht.',
        quickAction_youtube: 'Open YouTube',
        quickAction_google: 'Open Google',
        quickAction_calculator: 'Open rekenmachine',
        quickAction_think: 'Denk met Echo mee',
        quickAction_folder: 'Maak demomap',
        quickAction_explorer: 'Open Verkenner',
        featureAction_task_list: 'Toon taken',
        featureAction_agenda_show: 'Toon agenda',
        featureAction_timer_5: 'Start timer 5 min',
        featureAction_reminder_break: 'Herinner aan stretchen',
        featureAction_browser_current_url: 'Huidige URL',
        featureAction_browser_read_page: 'Lees deze pagina',
        featureAction_browser_summarize_page: 'Vat deze pagina samen',
        featureAction_browser_focus_edge: 'Activeer Edge',
        featureAction_file_summarize_readme: 'Vat README samen',
        featureAction_workspace_search_ollama: 'Zoek in workspace',
        featureAction_memory_show: 'Wat weet je over mij?',
        featureAction_system_info: 'Systeeminfo',
        panelPlannerLabel: 'Planner',
        panelPlannerCopy: 'Spring direct naar taken, timers en herinneringen zonder steeds de hele zin te typen.',
        panelBrowserLabel: 'Browser',
        panelBrowserCopy: 'Gebruik de actieve tab als context voor lees-, samenvat- en navigatieopdrachten.',
        panelWorkspaceLabel: 'Workspace',
        panelWorkspaceCopy: 'Breng geheugen, bestandstools en systeeminzicht samen op één plek.',
        promptStudioEyebrow: 'Promptstudio',
        promptStudioTitle: 'Begin met een sterkere prompt',
        promptStudioCopy: 'Tik op een patroon om het opdrachtveld te vullen, pas het aan als je wilt en verstuur het daarna.',
        promptCardPlanningLabel: 'Plannen',
        promptCardResearchLabel: 'Onderzoeken',
        promptCardBuildLabel: 'Bouwen',
        promptChip_plan_day: 'Plan mijn dag',
        promptChip_focus_hour: 'Help me een uur focussen',
        promptChip_set_break_reminder: 'Zet een pauzeherinnering',
        promptChip_summarize_tab: 'Vat deze pagina samen',
        promptChip_search_workspace: 'Zoek in de workspace',
        promptChip_memory_review: 'Wat weet je over mij?',
        promptChip_rewrite_readme: 'Herschrijf README',
        promptChip_system_review: 'Check mijn systeem',
        promptChip_automation_ready: 'Maak automation klaar',
        intentGuideEyebrow: 'Start hier',
        intentGuideTitle: 'Vertel Echo welk soort hulp je wilt',
        intentGuideCopy: 'Echo reageert consistenter als hij weet of je uitleg, een actie of allebei in één verzoek wilt.',
        intentChip_answer: 'Leg iets uit',
        intentChip_action: 'Voer een taak uit',
        intentChip_hybrid: 'Doe + leg uit',
        intentChip_automation: 'Automation klaarzetten',
        routePanelEyebrow: 'Uitvoerpad',
        routePanelTitle: 'Zie hoe Echo je verzoek heeft gerouteerd',
        routePanelCopyIdle: 'Echo laat hier zien of hij een vraag, een actie of een gemengd verzoek zag.',
        routePanelCopyLocked: 'Automation is vergrendeld. Zet eerst geavanceerde besturing aan in instellingen voor browser- en desktopacties.',
        routePanelCopyReady: 'Automation is toegestaan. Zeg schakel automation-modus in als je actieve browser- of desktopbesturing wilt.',
        routePanelCopyLive: 'Automation is actief. Browser- en desktopacties kunnen lopen tot het venster sluit.',
        routeStatusWaiting: 'Wachtend',
        routeStatusRouting: 'Routeren',
        routeStatusAnswered: 'Beantwoord',
        routeStatusCompleted: 'Voltooid',
        routeStatusFallback: 'Fallback',
        routeStatusError: 'Fout',
        routeStatusToolPlanning: 'Tools plannen',
        routeTokenIntent: 'Intentie: {value}',
        routeTokenTool: 'Tool: {value}',
        routeTokenCategory: 'Categorie: {value}',
        routeTokenAutomation: 'Automation: {value}',
        routeIntent_answer: 'Antwoord',
        routeIntent_action: 'Actie',
        routeIntent_hybrid: 'Gemengd',
        routeIntent_memory: 'Geheugen',
        routeIntent_unknown: 'Onbekend',
        routeTool_builtin_answer: 'Ingebouwd antwoord',
        routeTool_online_answer: 'Online antwoord',
        routeTool_guided_answer: 'Meedenkmodus',
        routeTool_local_plan: 'Lokale tools',
        routeTool_online_action_planner: 'AI-toolplan',
        routeTool_memory: 'Geheugen',
        routeTool_fallback: 'Fallback',
        routeTool_error: 'Fout',
        routeCategory_answer: 'Redeneren',
        routeCategory_browser: 'Browser',
        routeCategory_workspace: 'Workspace',
        routeCategory_planner: 'Planner',
        routeCategory_automation: 'Automation',
        routeCategory_system: 'Systeem',
        routeCategory_general: 'Algemeen',
        routeCategory_memory: 'Geheugen',
        automationStateLocked: 'Vergrendeld',
        automationStateReady: 'Klaar',
        automationStateLive: 'Actief ({remaining})',
        automationNeedsSettings: 'Zet eerst geavanceerde besturing aan in instellingen.',
        automationNeedsEnable: 'Schakel eerst automation-modus in voor deze actie.',
        commandDrawerSummary: 'Idee nodig? Laat een paar voorbeelden zien',
        commandLabEyebrow: 'Opdrachtideeën',
        commandLabTitle: 'Kijk alleen even als je inspiratie wilt',
        commandLabCopy: 'Open dit alleen als je een voorbeeld wilt. Tik op een idee om het opdrachtveld te vullen en maak er daarna je eigen zin van.',
        commandDiscoveryLabel: 'Zoek een patroon',
        commandDiscoveryPlaceholder: 'Zoek browser-, planner-, bestands-, geheugen- of automation-commando\'s',
        commandDiscoveryEmpty: 'Nog geen passende commando-voorbeelden. Probeer browser, planner, bestand, geheugen of automation.',
        hint: 'Typ een opdracht of gebruik de microfoon. Voorbeeld: toon agenda, vat deze pagina samen, vat README.md samen of wat weet je over mij. Browser lezen heeft automation-modus nodig.',
        controlLabel: 'Bediening',
        computerPanelLabel: 'Computerbediening',
        computerPanelNote: 'Schakel eerst automation-modus in voor screenshots, macro\'s en vensterbeheer.',
        computerSystemLabel: 'Sessie + vensters',
        computerMacroLabel: 'App-macro\'s',
        computerAction_automation_enable: 'Automation aan',
        computerAction_automation_disable: 'Automation uit',
        computerAction_system_scan_start: 'Start systeemscan',
        computerAction_system_scan_status: 'Check scanstatus',
        computerAction_screenshot: 'Maak screenshot',
        computerAction_maximize_window: 'Maximaliseer venster',
        computerAction_close_window: 'Sluit venster',
        computerAction_focus_edge: 'Activeer Edge',
        computerAction_volume_up: 'Volume omhoog',
        computerAction_mute_volume: 'Volume stil',
        computerAction_vscode_new_file: 'VS Code nieuw bestand',
        computerAction_edge_inprivate: 'Edge InPrivate',
        computerAction_discord_search: 'Zoek in Discord',
        computerAction_discord_mute: 'Discord dempen',
        computerAction_whatsapp_new_chat: 'WhatsApp nieuwe chat',
        computerAction_steam_search: 'Zoek in Steam',
        liveStatusLabel: 'Live status',
        tipsLabel: 'Betere resultaten',
        tipOne: 'Vraag om een taak tegelijk als je snelheid wilt.',
        tipTwo: 'Gebruik de planner-, browser- en workspacepanelen als je de nieuwe functies wilt zonder precieze commando\'s te onthouden.',
        tipThree: 'Vraag Echo om mee te denken of een bestand te herschrijven als je werk nog vorm moet krijgen.',
        settingsKicker: 'Echo afstellen',
        settingsTitle: '⚙️ Instellingen',
        settingsSubtitle: 'Pas stem, taal, snelle bestemmingen, assistentmodi en de reacties van Echo aan.',
        settingsSectionIdentity: 'Profiel',
        settingsSectionDestinations: 'Snelkoppelingen',
        settingsSectionVoice: 'Stem',
        settingsSectionBehavior: 'Gedrag',
        settingsSectionModes: 'Assistentmodi',
        settingsModesNote: 'Met deze schakelaars bepaal je of Echo geheugen, meerstapsplanning en het gekoppelde AI-model actiever gebruikt.',
        aiName: 'AI-naam:',
        clientNameLabel: 'Jouw naam:',
        clientNamePlaceholder: 'Jouw naam',
        language: 'Taal:',
        youtubeUrl: 'YouTube-URL:',
        googleUrl: 'Google-URL:',
        wakeWord: 'Wake word:',
        chooseVoice: 'Kies stem:',
        computerControl: 'Sta geavanceerde computerbesturing toe',
        computerControlNote: 'Dit ontgrendelt muis-, toetsenbord-, screenshot-, wifi-, bluetooth- en app-macro-opdrachten. Je moet nog steeds eerst zeggen: schakel automation-modus in.',
        useEmojis: 'Gebruik emoji\'s',
        showGreeting: 'Toon begroeting',
        voiceOutput: 'Spraakuitvoer (text-to-speech)',
        agentModeLabel: 'Schakel denk-met-mij-modus in',
        primaryAgentLabel: 'Gebruik eerst de AI-agent',
        onlineAiModeLabel: 'Sta gekoppelde AI-antwoorden toe',
        memoryModeLabel: 'Gebruik langetermijngeheugen',
        priorityModeLabel: 'Herschik meerstapsplannen',
        saveSettings: '💾 Instellingen opslaan',
        settingsButton: '⚙️ Instellingen',
        micOrbReady: 'Microfoon klaar',
        micOrbListening: 'Luisteren...',
        micOrbPaused: 'Tik om te starten',
        micOrbSpeaking: 'Echo praat',
        micOrbUnavailable: 'Geen mic-ondersteuning',
        microphoneAlwaysOn: '🎤 Microfoon altijd aan',
        microphoneActive: '🎤 Microfoon actief',
        microphonePaused: '🎤 Start microfoon',
        automaticVoice: 'Automatisch (Nederlands)',
        wakeWordPlaceholder: 'hee echo',
        defaultWakeWord: 'hee echo',
        testVoice: '🔊 Test stem',
        testVoiceSample: 'Hoi, waarmee kan ik helpen?',
        typeCommandFirst: 'Typ eerst een opdracht.',
        working: 'Bezig...',
        heard: 'Gehoord: {text}',
        speechHeardAction: 'Ik hoorde: {text}. Ik ga dat nu uitvoeren.',
        successVoice: 'Klaar. Echo antwoordde met spraak.',
        successPlain: 'Klaar.',
        genericError: 'Er ging iets mis.',
        connectionProblem: 'Er was een probleem met het versturen van de opdracht.',
        connectionError: 'Verbindingsfout.',
        speechUnsupported: 'Deze browser ondersteunt geen spraakherkenning.',
        reactivateVoice: 'Klik een keer op de microfoon om spraak opnieuw te activeren.',
        awakeReply: 'Ja, zeg het maar.',
        awakeReplyPersonal: 'Hey {clientName}, hoe kan ik je helpen?',
        awakeStatus: 'Echo luistert. Zeg je volgende opdracht.',
        sleepReply: 'Prima, ik ga terug naar stand-by.',
        speechError: 'Spraakfout. Controleer de microfoonrechten.',
        speechErrorVoice: 'Ik kan je niet goed horen. Controleer je microfoon.',
        microphoneActivated: 'Microfoon geactiveerd. Zeg: {wakeWord}',
        microphonePermission: 'De microfoon kon niet starten. Controleer je browserrechten.',
        microphoneStaysOn: 'De microfoon blijft aan.',
        microphoneStopped: 'Microfoon gestopt.',
        savingFailed: 'Opslaan mislukt.',
        settingsSaved: 'Instellingen opgeslagen.',
        voiceTestPlayed: 'Stemtest afgespeeld.',
        promptReady: 'Prompt staat klaar. Pas hem aan of druk op Verstuur.',
        grantPermission: 'Klik een keer op de microfoon om toestemming te geven.',
        greeting: 'Hallo! Typ een opdracht of zeg hee echo om me wakker te maken.',
        voiceModeActive: 'Spraakmodus actief. Zeg: {wakeWord}',
        textModeActive: 'Tekstmodus actief. Gebruik het opdrachtveld om Echo te bedienen.',
        standby: 'Stand-by. Zeg: {wakeWord}',
        errorPrefix: 'Fout: '
    }
};

let spraakUitgangActief = true;
let botIsAanHetPraten = false;
let hervatNaSpraak = false;
let speechQueue = Promise.resolve();
let actieveTaal = 'English';
let actieveSpraakTaal = UI_TEKST.English.speechLang;
let uiSettingsState = {};
let dashboardState = {};
let routeringState = {};
let dashboardPollInterval = null;
let runtimeVersiePollInterval = null;
let runtimeBuildId = null;
let pendingConfirmationState = null;
let safetyConfirmBusy = false;
let voiceVisualizerContext = null;
let voiceVisualizerFrameId = null;
let voiceVisualizerLastTime = 0;
let voiceVisualizerPhase = 0;
let voiceMicContext = null;
let voiceMicAnalyser = null;
let voiceMicSource = null;
let voiceMicData = null;
let voiceMicLevel = 0;
let voiceOutputLevel = 0;
let voiceOutputPulse = 0;
let voiceOutputActive = false;
let voiceMicDenied = false;

function normaliseerTaalwaarde(taal) {
    return String(taal || '').toLowerCase().startsWith('nl') || String(taal || '').toLowerCase() === 'nederlands'
        ? 'Nederlands'
        : 'English';
}

function vertaal(key, variabelen = {}) {
    const woordenboek = UI_TEKST[actieveTaal] || UI_TEKST.English;
    let tekst = woordenboek[key] ?? UI_TEKST.English[key] ?? key;

    Object.entries(variabelen).forEach(([naam, waarde]) => {
        tekst = tekst.replaceAll('{' + naam + '}', waarde);
    });

    return tekst;
}

function pasDynamischeVertalingenToe() {
    document.querySelectorAll('[data-i18n]').forEach((element) => {
        const key = element.dataset.i18n;
        if (!key) {
            return;
        }

        element.textContent = vertaal(key);
    });

    document.querySelectorAll('[data-i18n-placeholder]').forEach((element) => {
        const key = element.dataset.i18nPlaceholder;
        if (!key) {
            return;
        }

        element.placeholder = vertaal(key);
    });
}


function escapeHtml(tekst) {
    return String(tekst || '')
        .replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;')
        .replaceAll('"', '&quot;')
        .replaceAll("'", '&#39;');
}


function commandoVoorIntentChip(key) {
    const commandoSet = {
        English: {
            answer: 'what is the difference between RAM and storage',
            action: 'summarize README.md',
            hybrid: 'open google and explain what RAM is',
            automation: 'enable automation mode'
        },
        Nederlands: {
            answer: 'wat is het verschil tussen RAM en opslag',
            action: 'vat README.md samen',
            hybrid: 'open google en leg uit wat RAM is',
            automation: 'schakel automation-modus in'
        }
    };

    return (commandoSet[actieveTaal] || commandoSet.English)[key] || '';
}


function ontdekbareCommandoVoorbeelden() {
    return [
        { category: 'answer', command: commandoVoorIntentChip('answer') },
        { category: 'workspace', command: commandoVoorIntentChip('action') },
        { category: 'browser', command: commandoVoorIntentChip('hybrid') },
        { category: 'automation', command: commandoVoorIntentChip('automation') },
        { category: 'planner', command: commandoVoorFeatureKnop('task_list') },
        { category: 'planner', command: commandoVoorFeatureKnop('agenda_show') },
        { category: 'planner', command: commandoVoorFeatureKnop('timer_5') },
        { category: 'browser', command: commandoVoorFeatureKnop('browser_read_page') },
        { category: 'browser', command: commandoVoorFeatureKnop('browser_summarize_page') },
        { category: 'workspace', command: commandoVoorFeatureKnop('file_summarize_readme') },
        { category: 'workspace', command: commandoVoorFeatureKnop('workspace_search_ollama') },
        { category: 'memory', command: commandoVoorFeatureKnop('memory_show') },
        { category: 'system', command: commandoVoorFeatureKnop('system_info') },
        { category: 'system', command: commandoVoorComputerKnop('system_scan_start') },
        { category: 'system', command: commandoVoorComputerKnop('system_scan_status') },
        { category: 'automation', command: commandoVoorComputerKnop('screenshot') },
        { category: 'automation', command: commandoVoorComputerKnop('vscode_new_file') },
        { category: 'browser', command: commandoVoorPromptChip('summarize_tab') },
        { category: 'workspace', command: commandoVoorPromptChip('rewrite_readme') },
        { category: 'answer', command: commandoVoorPromptChip('focus_hour') }
    ].filter((item) => item.command);
}


function vertaalRouteringsWaarde(prefix, value, fallbackKey = '') {
    const sleutel = String(value || '').trim().toLowerCase() || fallbackKey;
    if (!sleutel) {
        return vertaal(prefix + 'unknown');
    }

    return vertaal(prefix + sleutel);
}


function automationLabel(modes = {}) {
    const automationAllowed = modes.automation_allowed ?? (modes.computerbesturing_toestaan === true);
    const automationActive = modes.automation_active === true;

    if (!automationAllowed) {
        return vertaal('automationStateLocked');
    }
    if (automationActive) {
        return vertaal('automationStateLive', { remaining: modes.automation_label || '0s' });
    }
    return vertaal('automationStateReady');
}


function renderCommandDiscovery(filterTekst = '') {
    if (!commandDiscoveryList) {
        return;
    }

    const zoekterm = normaliseerTekst(filterTekst || '');
    const items = ontdekbareCommandoVoorbeelden().filter((item) => {
        if (!zoekterm) {
            return true;
        }
        const haystack = normaliseerTekst(item.category + ' ' + item.command);
        return haystack.includes(zoekterm);
    });

    if (!items.length) {
        commandDiscoveryList.innerHTML = '<p class="command-discovery-empty">' + escapeHtml(vertaal('commandDiscoveryEmpty')) + '</p>';
        return;
    }

    commandDiscoveryList.innerHTML = items.map((item) => [
        '<button type="button" class="command-suggestion" data-command="' + escapeHtml(item.command) + '">',
        '<span class="command-suggestion__category">' + escapeHtml(vertaalRouteringsWaarde('routeCategory_', item.category, 'general')) + '</span>',
        '<span class="command-suggestion__command">' + escapeHtml(item.command) + '</span>',
        '</button>'
    ].join('')).join('');

    commandDiscoveryList.querySelectorAll('.command-suggestion').forEach((button) => {
        button.addEventListener('click', () => {
            plaatsPromptInComposer(button.dataset.command || '');
        });
    });
}


function updateRoutePanel(route = {}, modes = dashboardState.modes || {}) {
    routeringState = route && Object.keys(route).length ? { ...route } : routeringState;

    const actieveRoute = route && Object.keys(route).length ? route : routeringState;
    const intent = String(actieveRoute.intent || '').trim().toLowerCase();
    const tool = String(actieveRoute.tool || '').trim().toLowerCase();
    const category = String(actieveRoute.category || '').trim().toLowerCase();
    const phase = String(actieveRoute.phase || '').trim().toLowerCase();
    const note = String(actieveRoute.note || '').trim();
    const automationAllowed = (modes.automation_allowed ?? (modes.computerbesturing_toestaan === true)) === true;
    const automationRelevant = ['browser', 'automation'].includes(category);

    if (routePanel) {
        routePanel.dataset.state = phase || 'idle';
    }

    if (routePanelStatus) {
        const statusKeyMap = {
            routing: 'routeStatusRouting',
            answered: 'routeStatusAnswered',
            completed: 'routeStatusCompleted',
            fallback: 'routeStatusFallback',
            error: 'routeStatusError',
            tool_planning: 'routeStatusToolPlanning'
        };
        routePanelStatus.textContent = vertaal(statusKeyMap[phase] || 'routeStatusWaiting');
    }

    if (routeIntentToken) {
        routeIntentToken.textContent = vertaal('routeTokenIntent', {
            value: intent ? vertaalRouteringsWaarde('routeIntent_', intent, 'unknown') : '--'
        });
    }
    if (routeToolToken) {
        routeToolToken.textContent = vertaal('routeTokenTool', {
            value: tool ? vertaalRouteringsWaarde('routeTool_', tool, 'fallback') : '--'
        });
    }
    if (routeCategoryToken) {
        routeCategoryToken.textContent = vertaal('routeTokenCategory', {
            value: category ? vertaalRouteringsWaarde('routeCategory_', category, 'general') : '--'
        });
    }
    if (routeAutomationToken) {
        routeAutomationToken.textContent = vertaal('routeTokenAutomation', { value: automationLabel(modes) });
    }

    if (routePanelCopy) {
        if (note && phase === 'error') {
            routePanelCopy.textContent = note;
        } else if (automationRelevant && !automationAllowed) {
            routePanelCopy.textContent = vertaal('routePanelCopyLocked');
        } else if (automationRelevant && modes.automation_active) {
            routePanelCopy.textContent = vertaal('routePanelCopyLive');
        } else if (automationRelevant && automationAllowed) {
            routePanelCopy.textContent = vertaal('routePanelCopyReady');
        } else {
            routePanelCopy.textContent = vertaal('routePanelCopyIdle');
        }
    }
}


function syncAutomationLocks(modes = dashboardState.modes || {}) {
    const automationAllowed = (modes.automation_allowed ?? (modes.computerbesturing_toestaan === true)) === true;
    const automationActive = modes.automation_active === true;
    const lockedForSettings = !automationAllowed;
    const lockedForActivation = automationAllowed && !automationActive;

    computerActionButtons.forEach((button) => {
        const key = button.dataset.computerKey || '';
        const isEnableButton = key === 'automation_enable';
        const isDisableButton = key === 'automation_disable';

        let disabled = false;
        let title = '';
        if (isEnableButton) {
            disabled = lockedForSettings || automationActive;
            title = lockedForSettings ? vertaal('automationNeedsSettings') : (automationActive ? automationLabel(modes) : '');
        } else if (isDisableButton) {
            disabled = lockedForSettings || !automationActive;
            title = lockedForSettings ? vertaal('automationNeedsSettings') : (!automationActive ? vertaal('automationNeedsEnable') : '');
        } else {
            disabled = lockedForSettings || lockedForActivation;
            title = lockedForSettings ? vertaal('automationNeedsSettings') : (lockedForActivation ? vertaal('automationNeedsEnable') : '');
        }

        button.disabled = disabled;
        button.classList.toggle('is-locked', disabled);
        button.title = title;
    });

    browserWorkbenchButtons.forEach((button) => {
        const action = button.dataset.browserAction || '';
        const needsActiveAutomation = ['read_current', 'summarize_current', 'fill_form'].includes(action);
        const disabled = needsActiveAutomation && (lockedForSettings || lockedForActivation);
        button.disabled = disabled;
        button.classList.toggle('is-locked', disabled);
        button.title = disabled
            ? (lockedForSettings ? vertaal('automationNeedsSettings') : vertaal('automationNeedsEnable'))
            : '';
    });

    featureActionButtons.forEach((button) => {
        const key = button.dataset.featureKey || '';
        const needsActiveAutomation = ['browser_current_url', 'browser_read_page', 'browser_summarize_page', 'browser_focus_edge'].includes(key);
        const disabled = needsActiveAutomation && (lockedForSettings || lockedForActivation);
        button.disabled = disabled;
        button.classList.toggle('is-locked', disabled);
        button.title = disabled
            ? (lockedForSettings ? vertaal('automationNeedsSettings') : vertaal('automationNeedsEnable'))
            : '';
    });
}

function zetModuskaart(kaart, waardeElement, metaElement, waarde, meta, state = 'neutral') {
    if (kaart) {
        kaart.dataset.state = state;
    }
    if (waardeElement) {
        waardeElement.textContent = waarde;
    }
    if (metaElement) {
        metaElement.textContent = meta;
    }
}


function werkModusoverzichtBij(settings = {}) {
    const heeftInstellingen = settings && Object.keys(settings).length > 0;
    if (!heeftInstellingen) {
        zetModuskaart(modeAiCard, modeAiValue, modeAiMeta, vertaal('modeLoadingValue'), vertaal('modeLoadingMeta'));
        zetModuskaart(modeThinkCard, modeThinkValue, modeThinkMeta, vertaal('modeLoadingValue'), vertaal('modeLoadingMeta'));
        zetModuskaart(modeMemoryCard, modeMemoryValue, modeMemoryMeta, vertaal('modeLoadingValue'), vertaal('modeLoadingMeta'));
        zetModuskaart(modeAutomationCard, modeAutomationValue, modeAutomationMeta, vertaal('modeLoadingValue'), vertaal('modeLoadingMeta'));
        zetModuskaart(modeVoiceCard, modeVoiceValue, modeVoiceMeta, vertaal('modeLoadingValue'), vertaal('modeLoadingMeta'));
        return;
    }

    const modelNaam = String(settings.online_ai_model || 'qwen2.5:3b').trim() || 'qwen2.5:3b';
    const taal = normaliseerTaalwaarde(settings.taal || actieveTaal);
    const wakeWordInstelling = String(settings.wake_word || vertaal('defaultWakeWord')).trim() || vertaal('defaultWakeWord');

    if (settings.online_ai_modus === false) {
        zetModuskaart(modeAiCard, modeAiValue, modeAiMeta, vertaal('modeAiValueBuiltin'), vertaal('modeAiMetaBuiltin'), 'off');
    } else if (settings.ai_agent_primair !== false) {
        zetModuskaart(modeAiCard, modeAiValue, modeAiMeta, vertaal('modeAiValueAgent'), vertaal('modeAiMetaModel', { model: modelNaam }), 'on');
    } else {
        zetModuskaart(modeAiCard, modeAiValue, modeAiMeta, vertaal('modeAiValueModel'), vertaal('modeAiMetaModel', { model: modelNaam }), 'neutral');
    }

    zetModuskaart(
        modeThinkCard,
        modeThinkValue,
        modeThinkMeta,
        settings.agent_modus !== false ? vertaal('modeThinkValueGuided') : vertaal('modeThinkValueDirect'),
        settings.prioriteit_modus !== false ? vertaal('modeThinkMetaPriorityOn') : vertaal('modeThinkMetaPriorityOff'),
        settings.agent_modus !== false ? 'on' : 'neutral'
    );

    zetModuskaart(
        modeMemoryCard,
        modeMemoryValue,
        modeMemoryMeta,
        settings.geheugen_modus !== false ? vertaal('modeStateOn') : vertaal('modeStateOff'),
        settings.geheugen_modus !== false ? vertaal('modeMemoryMetaOn') : vertaal('modeMemoryMetaOff'),
        settings.geheugen_modus !== false ? 'on' : 'off'
    );

    zetModuskaart(
        modeAutomationCard,
        modeAutomationValue,
        modeAutomationMeta,
        settings.computerbesturing_toestaan === true ? vertaal('modeAutomationValueReady') : vertaal('modeAutomationValueLocked'),
        settings.computerbesturing_toestaan === true ? vertaal('modeAutomationMetaReady') : vertaal('modeAutomationMetaLocked'),
        settings.computerbesturing_toestaan === true ? 'on' : 'off'
    );

    zetModuskaart(
        modeVoiceCard,
        modeVoiceValue,
        modeVoiceMeta,
        settings.spraak_uitgang !== false ? vertaal('modeVoiceValueOn') : vertaal('modeVoiceValueOff'),
        vertaal('modeVoiceMeta', { language: taal, wakeWord: wakeWordInstelling }),
        settings.spraak_uitgang !== false ? 'neutral' : 'off'
    );
}


function werkModusoverzichtBijDashboard(data = {}) {
    const modes = data.modes || {};
    const ai = data.ai || {};
    const memory = data.memory || {};

    if (!Object.keys(modes).length && !Object.keys(ai).length) {
        werkModusoverzichtBij(uiSettingsState);
        return;
    }

    if (!modes.online_ai_enabled) {
        zetModuskaart(modeAiCard, modeAiValue, modeAiMeta, vertaal('modeAiValueBuiltin'), vertaal('modeAiMetaBuiltin'), 'off');
    } else if (modes.ai_agent_first && ai.available) {
        zetModuskaart(modeAiCard, modeAiValue, modeAiMeta, vertaal('modeAiValueAgent'), ai.message || vertaal('modeAiMetaModel', { model: ai.model || 'qwen2.5:3b' }), 'on');
    } else if (ai.available) {
        zetModuskaart(modeAiCard, modeAiValue, modeAiMeta, vertaal('modeAiValueModel'), ai.message || vertaal('modeAiMetaModel', { model: ai.model || 'qwen2.5:3b' }), 'neutral');
    } else {
        zetModuskaart(modeAiCard, modeAiValue, modeAiMeta, vertaal('modeAiValueBuiltin'), ai.message || vertaal('modeAiMetaBuiltin'), 'off');
    }

    zetModuskaart(
        modeThinkCard,
        modeThinkValue,
        modeThinkMeta,
        modes.thinking_enabled ? vertaal('modeThinkValueGuided') : vertaal('modeThinkValueDirect'),
        modes.priority_enabled ? vertaal('modeThinkMetaPriorityOn') : vertaal('modeThinkMetaPriorityOff'),
        modes.thinking_enabled ? 'on' : 'neutral'
    );

    zetModuskaart(
        modeMemoryCard,
        modeMemoryValue,
        modeMemoryMeta,
        modes.memory_enabled ? vertaal('modeStateOn') : vertaal('modeStateOff'),
        modes.memory_enabled
            ? (memory.summary || vertaal('modeMemoryMetaOn'))
            : vertaal('modeMemoryMetaOff'),
        modes.memory_enabled ? 'on' : 'off'
    );

    if (!modes.automation_allowed) {
        zetModuskaart(modeAutomationCard, modeAutomationValue, modeAutomationMeta, vertaal('modeAutomationValueLocked'), vertaal('modeAutomationMetaLocked'), 'off');
    } else if (modes.automation_active) {
        zetModuskaart(modeAutomationCard, modeAutomationValue, modeAutomationMeta, vertaal('dashboardAutomationActiveValue'), vertaal('dashboardAutomationActiveMeta', { remaining: modes.automation_label || '0s' }), 'on');
    } else {
        zetModuskaart(modeAutomationCard, modeAutomationValue, modeAutomationMeta, vertaal('dashboardAutomationReadyValue'), vertaal('dashboardAutomationReadyMeta'), 'neutral');
    }

    zetModuskaart(
        modeVoiceCard,
        modeVoiceValue,
        modeVoiceMeta,
        modes.voice_output ? vertaal('modeVoiceValueOn') : vertaal('modeVoiceValueOff'),
        vertaal('modeVoiceMeta', { language: modes.language || actieveTaal, wakeWord: modes.wake_word || vertaal('defaultWakeWord') }),
        modes.voice_output ? 'neutral' : 'off'
    );
}


function renderLegeLijst(lijstElement, tekst) {
    if (!lijstElement) {
        return;
    }
    lijstElement.innerHTML = '<div class="mini-list-empty">' + escapeHtml(tekst) + '</div>';
}


function renderDashboardLijst(lijstElement, items, leegTekst, formatteerItem) {
    if (!lijstElement) {
        return;
    }
    if (!items || !items.length) {
        renderLegeLijst(lijstElement, leegTekst);
        return;
    }
    lijstElement.innerHTML = items.map(formatteerItem).join('');
}


function formatteerRecentActieItem(item) {
    return [
        '<article class="activity-item">',
        '<p class="activity-item-command">' + escapeHtml(item.command || '') + '</p>',
        '<p class="activity-item-result">' + escapeHtml(item.result || '') + '</p>',
        '</article>'
    ].join('');
}


function formatteerPlannerTaakItem(item) {
    return [
        '<article class="mini-list-item">',
        '<p class="mini-list-title">#' + escapeHtml(item.id) + ' ' + escapeHtml(item.text || '') + '</p>',
        '</article>'
    ].join('');
}


function formatteerPlannerTimerItem(item) {
    return [
        '<article class="mini-list-item">',
        '<p class="mini-list-title">#' + escapeHtml(item.id) + ' ' + escapeHtml(item.message || '') + '</p>',
        '<p class="mini-list-meta">' + escapeHtml(item.remaining_label || '') + '</p>',
        '</article>'
    ].join('');
}


function formatteerNotificatieItem(item) {
    return [
        '<article class="mini-list-item mini-list-item--notification">',
        '<p class="mini-list-title">' + escapeHtml(item.message || '') + '</p>',
        '<p class="mini-list-meta">' + escapeHtml(item.age_label || '') + '</p>',
        '</article>'
    ].join('');
}


function verversBestandsSuggesties(bestanden = []) {
    if (!fileWorkbenchPath) {
        return;
    }
    const huidigeWaarde = fileWorkbenchPath.value;
    const opties = ['<option value="">' + escapeHtml(vertaal('fileWorkbenchEmptyOption')) + '</option>'];
    bestanden.forEach((bestand) => {
        const path = String(bestand.path || '').trim();
        if (!path) {
            return;
        }
        opties.push('<option value="' + escapeHtml(path) + '">' + escapeHtml(path) + '</option>');
    });
    fileWorkbenchPath.innerHTML = opties.join('');
    if (huidigeWaarde && bestanden.some((bestand) => bestand.path === huidigeWaarde)) {
        fileWorkbenchPath.value = huidigeWaarde;
    }
}


function renderDashboard(data = {}) {
    dashboardState = data;
    updateSafetyBevestigingModal(data.pending_confirmation || null);
    werkModusoverzichtBijDashboard(data);

    const ai = data.ai || {};
    const runtime = data.runtime || {};
    const lastCommand = runtime.last_command || {};
    const planner = data.planner || {};
    const workspace = data.workspace || {};
    const modes = data.modes || {};
    const routing = data.routing || {};

    if (dashboardSurface) {
        dashboardSurface.setAttribute('aria-label', vertaal('dashboardSurfaceAria'));
    }

    if (dashboardModelValue) {
        dashboardModelValue.textContent = ai.model || vertaal('modeLoadingValue');
    }
    if (dashboardModelMeta) {
        dashboardModelMeta.textContent = ai.message || vertaal('dashboardMetricWaitingMeta');
    }

    if (dashboardCommandValue) {
        dashboardCommandValue.textContent = lastCommand.text || vertaal('dashboardNoCommandValue');
    }
    if (dashboardCommandMeta) {
        dashboardCommandMeta.textContent = lastCommand.text
            ? vertaal(lastCommand.success ? 'dashboardCommandMetaSuccess' : 'dashboardCommandMetaError', { duration: String(lastCommand.duration_ms || 0) })
            : vertaal('dashboardNoCommandMeta');
    }

    if (dashboardUptimeValue) {
        dashboardUptimeValue.textContent = runtime.uptime_label || '0s';
    }
    if (dashboardUptimeMeta) {
        dashboardUptimeMeta.textContent = vertaal('dashboardGeneratedAtLabelText', { time: data.generated_at_label || '--' });
    }

    if (dashboardAutomationValue) {
        dashboardAutomationValue.textContent = !modes.automation_allowed
            ? vertaal('dashboardAutomationLockedValue')
            : (modes.automation_active ? vertaal('dashboardAutomationActiveValue') : vertaal('dashboardAutomationReadyValue'));
    }
    if (dashboardAutomationMeta) {
        dashboardAutomationMeta.textContent = !modes.automation_allowed
            ? vertaal('dashboardAutomationLockedMeta')
            : (modes.automation_active
                ? vertaal('dashboardAutomationActiveMeta', { remaining: modes.automation_label || '0s' })
                : vertaal('dashboardAutomationReadyMeta'));
    }

    if (dashboardGeneratedAtLabel) {
        dashboardGeneratedAtLabel.textContent = vertaal('dashboardGeneratedAtLabelText', { time: data.generated_at_label || '--' });
    }

    updateRoutePanel(routing, modes);
    syncAutomationLocks(modes);

    renderDashboardLijst(
        dashboardRecentActionsList,
        workspace.recent_actions || [],
        vertaal('dashboardRecentActionsEmpty'),
        formatteerRecentActieItem
    );

    if (plannerTaskCountPill) {
        plannerTaskCountPill.textContent = vertaal('plannerTaskCountLabel', { count: String(planner.open_task_count || 0) });
    }
    if (plannerTimerCountPill) {
        plannerTimerCountPill.textContent = vertaal('plannerTimerCountLabel', { count: String(planner.active_timer_count || 0) });
    }
    if (plannerReminderCountPill) {
        plannerReminderCountPill.textContent = vertaal('plannerReminderCountLabel', { count: String(planner.pending_reminder_count || 0) });
    }

    renderDashboardLijst(plannerTasksList, planner.tasks || [], vertaal('plannerTasksEmpty'), formatteerPlannerTaakItem);
    renderDashboardLijst(plannerTimersList, planner.timers || [], vertaal('plannerTimersEmpty'), formatteerPlannerTimerItem);
    renderDashboardLijst(plannerRemindersList, planner.reminders || [], vertaal('plannerRemindersEmpty'), formatteerPlannerTimerItem);
    renderDashboardLijst(plannerNotificationsList, planner.notifications || [], vertaal('plannerNotificationsEmpty'), formatteerNotificatieItem);

    verversBestandsSuggesties(workspace.suggested_files || []);

    if (browserWorkbenchMeta) {
        browserWorkbenchMeta.textContent = workspace.recent_web_action
            ? workspace.recent_web_action
            : vertaal('browserWorkbenchMetaEmpty');
    }
    if (fileWorkbenchMeta) {
        fileWorkbenchMeta.textContent = (workspace.suggested_files || []).length
            ? ((workspace.suggested_files || []).map((bestand) => bestand.path).slice(0, 3).join(' | '))
            : vertaal('fileWorkbenchMetaEmpty');
    }
}


async function laadDashboard() {
    try {
        const response = await fetch('/api/dashboard');
        const data = await response.json();
        renderDashboard(data);
    } catch (error) {
        if (dashboardModelMeta) {
            dashboardModelMeta.textContent = error?.message || vertaal('connectionError');
        }
    }
}


function startDashboardPolling() {
    if (dashboardPollInterval) {
        window.clearInterval(dashboardPollInterval);
    }
    dashboardPollInterval = window.setInterval(() => {
        laadDashboard();
    }, 12000);
}


async function laadRuntimeVersie() {
    try {
        const response = await fetch(`/api/runtime-version?ts=${Date.now()}`, {
            cache: 'no-store',
        });

        if (!response.ok) {
            return;
        }

        const data = await response.json();
        const nieuweBuildId = String(data.build_id || '').trim();
        if (!nieuweBuildId) {
            return;
        }

        if (!runtimeBuildId) {
            runtimeBuildId = nieuweBuildId;
            return;
        }

        if (runtimeBuildId !== nieuweBuildId) {
            runtimeBuildId = nieuweBuildId;
            window.location.reload();
        }
    } catch (_error) {
        // Connection hiccups are expected while Flask restarts after file changes.
    }
}


function startRuntimeVersiePolling() {
    if (runtimeVersiePollInterval) {
        window.clearInterval(runtimeVersiePollInterval);
    }

    void laadRuntimeVersie();
    runtimeVersiePollInterval = window.setInterval(() => {
        void laadRuntimeVersie();
    }, 2500);
}


async function registreerServiceWorker() {
    if (!('serviceWorker' in navigator)) {
        return;
    }

    try {
        await navigator.serviceWorker.register('/service-worker.js');
    } catch (_error) {
        // Service worker is optional; app keeps working without it.
    }
}

function setStatusText(text, className = 'status') {
    statusDiv.className = className;
    statusDiv.textContent = text;
}

function setTranslatedStatus(key, variabelen = {}, className = 'status') {
    setStatusText(vertaal(key, variabelen), className);
}

function voiceVisualizerHeeftMicOndersteuning() {
    return Boolean(
        navigator.mediaDevices
        && typeof navigator.mediaDevices.getUserMedia === 'function'
        && (window.AudioContext || window.webkitAudioContext)
    );
}

function voiceVisualizerStateDescriptor() {
    if (voiceOutputActive || botIsAanHetPraten) {
        return { key: 'voiceVisualizerStateSpeaking', tone: 'speaking' };
    }
    if (luisterenActief) {
        return { key: 'voiceVisualizerStateListening', tone: 'listening' };
    }
    if (voiceMicDenied || !voiceVisualizerHeeftMicOndersteuning()) {
        return { key: 'voiceVisualizerStateWarning', tone: 'warning' };
    }
    return { key: 'voiceVisualizerStateIdle', tone: 'idle' };
}

function updateVoiceVisualizerStatus() {
    if (!voiceVisualizerStatus) {
        return;
    }

    const descriptor = voiceVisualizerStateDescriptor();
    voiceVisualizerStatus.textContent = vertaal(descriptor.key);
    voiceVisualizerStatus.dataset.state = descriptor.tone;
}

function resizeVoiceVisualizerCanvas() {
    if (!voiceVisualizerCanvas || !voiceVisualizerContext) {
        return;
    }

    const rect = voiceVisualizerCanvas.getBoundingClientRect();
    const dpr = Math.max(1, window.devicePixelRatio || 1);
    const width = Math.max(180, Math.round(rect.width));
    const height = Math.max(110, Math.round(rect.height));
    const scaledWidth = Math.round(width * dpr);
    const scaledHeight = Math.round(height * dpr);

    if (voiceVisualizerCanvas.width !== scaledWidth || voiceVisualizerCanvas.height !== scaledHeight) {
        voiceVisualizerCanvas.width = scaledWidth;
        voiceVisualizerCanvas.height = scaledHeight;
    }
}

async function zorgVoorVoiceVisualizerMicrofoon() {
    if (!voiceVisualizerCanvas || !voiceVisualizerHeeftMicOndersteuning()) {
        updateVoiceVisualizerStatus();
        return false;
    }

    if (voiceMicAnalyser && voiceMicData && voiceMicSource) {
        if (voiceMicContext && voiceMicContext.state === 'suspended') {
            try {
                await voiceMicContext.resume();
            } catch (_err) {
                // Ignore resume errors; analyzer may still work.
            }
        }
        return true;
    }

    const AudioContextClass = window.AudioContext || window.webkitAudioContext;
    if (!AudioContextClass) {
        updateVoiceVisualizerStatus();
        return false;
    }

    try {
        const stream = await navigator.mediaDevices.getUserMedia({
            audio: {
                echoCancellation: true,
                noiseSuppression: true,
                autoGainControl: true,
            },
        });

        voiceMicContext = new AudioContextClass();
        if (voiceMicContext.state === 'suspended') {
            await voiceMicContext.resume();
        }

        voiceMicSource = voiceMicContext.createMediaStreamSource(stream);
        voiceMicAnalyser = voiceMicContext.createAnalyser();
        voiceMicAnalyser.fftSize = 256;
        voiceMicAnalyser.smoothingTimeConstant = 0.74;
        voiceMicData = new Uint8Array(voiceMicAnalyser.fftSize);
        voiceMicSource.connect(voiceMicAnalyser);
        voiceMicDenied = false;
        updateVoiceVisualizerStatus();
        return true;
    } catch (_err) {
        voiceMicDenied = true;
        updateVoiceVisualizerStatus();
        return false;
    }
}

function leesVoiceVisualizerMicrofoonNiveau() {
    if (!voiceMicAnalyser || !voiceMicData) {
        return 0;
    }

    voiceMicAnalyser.getByteTimeDomainData(voiceMicData);

    let sum = 0;
    for (let index = 0; index < voiceMicData.length; index += 1) {
        const sample = (voiceMicData[index] - 128) / 128;
        sum += sample * sample;
    }
    const rms = Math.sqrt(sum / voiceMicData.length);
    return Math.min(1, rms * 3.8);
}

function triggerVoiceOutputPulse(strength = 0.45) {
    voiceOutputPulse = Math.max(voiceOutputPulse, Math.min(1, strength));
}

function setVoiceOutputActief(actief) {
    voiceOutputActive = Boolean(actief);
    if (voiceOutputActive) {
        triggerVoiceOutputPulse(0.42);
    }
    updateVoiceVisualizerStatus();
}

function tekenVoiceVisualizerGolf(level, baselineRatio, colorStart, colorEnd, phaseOffset) {
    if (!voiceVisualizerContext || !voiceVisualizerCanvas) {
        return;
    }

    const width = voiceVisualizerCanvas.width;
    const height = voiceVisualizerCanvas.height;
    const baseline = height * baselineRatio;
    const amplitude = (height * 0.035) + (height * 0.26 * Math.min(1, level));
    const step = Math.max(4, Math.round(width / 140));
    const gradient = voiceVisualizerContext.createLinearGradient(0, baseline - amplitude, width, baseline + amplitude);
    gradient.addColorStop(0, colorStart);
    gradient.addColorStop(1, colorEnd);

    voiceVisualizerContext.lineJoin = 'round';
    voiceVisualizerContext.lineCap = 'round';

    voiceVisualizerContext.beginPath();
    for (let x = 0; x <= width; x += step) {
        const progress = x / width;
        const oscillation = (
            Math.sin((progress * Math.PI * 10) + (voiceVisualizerPhase * 3.1) + phaseOffset) * 0.62
            + Math.sin((progress * Math.PI * 24) - (voiceVisualizerPhase * 2.2) + (phaseOffset * 1.6)) * 0.34
        );
        const y = baseline + (oscillation * amplitude);
        if (x === 0) {
            voiceVisualizerContext.moveTo(x, y);
        } else {
            voiceVisualizerContext.lineTo(x, y);
        }
    }

    voiceVisualizerContext.strokeStyle = gradient;
    voiceVisualizerContext.lineWidth = Math.max(2.5, height * 0.016);
    voiceVisualizerContext.stroke();

    voiceVisualizerContext.strokeStyle = colorStart;
    voiceVisualizerContext.globalAlpha = 0.18;
    voiceVisualizerContext.lineWidth = Math.max(8, height * 0.04);
    voiceVisualizerContext.stroke();
    voiceVisualizerContext.globalAlpha = 1;
}

function renderVoiceVisualizerFrame(timestamp) {
    if (!voiceVisualizerContext || !voiceVisualizerCanvas) {
        voiceVisualizerFrameId = null;
        return;
    }

    const dt = voiceVisualizerLastTime
        ? Math.min(0.08, (timestamp - voiceVisualizerLastTime) / 1000)
        : (1 / 60);
    voiceVisualizerLastTime = timestamp;
    voiceVisualizerPhase += dt * 2.4;

    const micNow = leesVoiceVisualizerMicrofoonNiveau();
    voiceMicLevel = (voiceMicLevel * 0.82) + (micNow * 0.18);

    const speaking = voiceOutputActive || botIsAanHetPraten;
    let outputTarget = 0.015;
    if (speaking) {
        const shimmer = ((Math.sin(voiceVisualizerPhase * 7.8) + 1) / 2) * 0.08;
        outputTarget = 0.2 + voiceOutputPulse + shimmer + (Math.random() * 0.06);
    }

    voiceOutputPulse = Math.max(0, voiceOutputPulse - (dt * 0.76));
    voiceOutputLevel = (voiceOutputLevel * 0.84) + (Math.min(1, outputTarget) * 0.16);

    const width = voiceVisualizerCanvas.width;
    const height = voiceVisualizerCanvas.height;
    const bgGradient = voiceVisualizerContext.createLinearGradient(0, 0, 0, height);
    bgGradient.addColorStop(0, 'rgba(12, 40, 55, 0.95)');
    bgGradient.addColorStop(1, 'rgba(8, 29, 41, 1)');
    voiceVisualizerContext.fillStyle = bgGradient;
    voiceVisualizerContext.fillRect(0, 0, width, height);

    voiceVisualizerContext.strokeStyle = 'rgba(157, 197, 212, 0.14)';
    voiceVisualizerContext.lineWidth = 1;
    voiceVisualizerContext.beginPath();
    voiceVisualizerContext.moveTo(0, height * 0.34);
    voiceVisualizerContext.lineTo(width, height * 0.34);
    voiceVisualizerContext.moveTo(0, height * 0.72);
    voiceVisualizerContext.lineTo(width, height * 0.72);
    voiceVisualizerContext.stroke();

    tekenVoiceVisualizerGolf(
        Math.min(1, voiceMicLevel),
        0.34,
        'rgba(122, 238, 231, 0.95)',
        'rgba(56, 167, 199, 0.92)',
        0.45
    );

    tekenVoiceVisualizerGolf(
        Math.min(1, voiceOutputLevel),
        0.72,
        'rgba(255, 194, 137, 0.92)',
        'rgba(240, 121, 92, 0.92)',
        2.05
    );

    voiceVisualizerFrameId = window.requestAnimationFrame(renderVoiceVisualizerFrame);
}

function initialiseerVoiceVisualizer() {
    if (!voiceVisualizerCanvas || typeof voiceVisualizerCanvas.getContext !== 'function') {
        return;
    }

    voiceVisualizerContext = voiceVisualizerCanvas.getContext('2d');
    if (!voiceVisualizerContext) {
        return;
    }

    resizeVoiceVisualizerCanvas();
    window.addEventListener('resize', resizeVoiceVisualizerCanvas);
    if (!voiceVisualizerFrameId) {
        voiceVisualizerFrameId = window.requestAnimationFrame(renderVoiceVisualizerFrame);
    }

    updateVoiceVisualizerStatus();
}

function stelSafetyBevestigingKnoppenIn(enabled) {
    if (safetyConfirmYesBtn) {
        safetyConfirmYesBtn.disabled = !enabled;
    }
    if (safetyConfirmNoBtn) {
        safetyConfirmNoBtn.disabled = !enabled;
    }
}

function tekstVoorPendingBevestiging(pending = {}) {
    if (!pending || typeof pending !== 'object') {
        return '';
    }

    if (actieveTaal === 'Nederlands') {
        return String(pending.prompt_nl || pending.prompt || '').trim();
    }
    return String(pending.prompt_en || pending.prompt || '').trim();
}

function updateSafetyBevestigingModal(pending = null) {
    const heeftPending = Boolean(pending && pending.pending);
    pendingConfirmationState = heeftPending ? { ...pending } : null;

    if (!safetyConfirmModal) {
        return;
    }

    if (safetyConfirmKicker) {
        safetyConfirmKicker.textContent = vertaal('safetyConfirmKicker');
    }
    if (safetyConfirmTitle) {
        safetyConfirmTitle.textContent = vertaal('safetyConfirmTitle');
    }
    if (safetyConfirmYesBtn) {
        safetyConfirmYesBtn.textContent = vertaal('safetyConfirmYes');
    }
    if (safetyConfirmNoBtn) {
        safetyConfirmNoBtn.textContent = vertaal('safetyConfirmNo');
    }

    if (!heeftPending) {
        safetyConfirmModal.classList.remove('is-open');
        safetyConfirmModal.setAttribute('aria-hidden', 'true');
        document.body.classList.remove('safety-modal-open');
        safetyConfirmBusy = false;
        stelSafetyBevestigingKnoppenIn(true);
        if (safetyConfirmBody) {
            safetyConfirmBody.textContent = vertaal('safetyConfirmFallback');
        }
        if (safetyConfirmTarget) {
            safetyConfirmTarget.textContent = '';
            safetyConfirmTarget.style.display = 'none';
        }
        return;
    }

    const wasOpen = safetyConfirmModal.classList.contains('is-open');
    const promptTekst = tekstVoorPendingBevestiging(pendingConfirmationState) || vertaal('safetyConfirmFallback');
    const targetTekst = String(pendingConfirmationState.target || '').trim();

    if (safetyConfirmBody) {
        safetyConfirmBody.textContent = promptTekst;
    }
    if (safetyConfirmTarget) {
        if (targetTekst) {
            safetyConfirmTarget.textContent = vertaal('safetyConfirmTargetPrefix', { target: targetTekst });
            safetyConfirmTarget.style.display = 'block';
        } else {
            safetyConfirmTarget.textContent = '';
            safetyConfirmTarget.style.display = 'none';
        }
    }

    safetyConfirmModal.classList.add('is-open');
    safetyConfirmModal.setAttribute('aria-hidden', 'false');
    document.body.classList.add('safety-modal-open');
    stelSafetyBevestigingKnoppenIn(!safetyConfirmBusy);

    if (!wasOpen && safetyConfirmYesBtn) {
        safetyConfirmYesBtn.focus();
    }
}

async function verstuurSafetyBevestiging(bevestigen) {
    if (!pendingConfirmationState || safetyConfirmBusy) {
        return;
    }

    const commando = bevestigen
        ? String(pendingConfirmationState.confirm_command || 'confirm pending action')
        : String(pendingConfirmationState.cancel_command || 'cancel pending action');
    if (!commando.trim()) {
        return;
    }

    const zichtbareTekst = bevestigen
        ? vertaal('safetyConfirmCommandConfirm')
        : vertaal('safetyConfirmCommandCancel');

    safetyConfirmBusy = true;
    stelSafetyBevestigingKnoppenIn(false);

    try {
        await verstuurCommando(commando, { zichtbareTekst });
    } finally {
        safetyConfirmBusy = false;
        stelSafetyBevestigingKnoppenIn(true);
    }
}

function setEchoSpreekAnimatie(aan) {
    if (!echoFace) {
        return;
    }

    echoFace.classList.toggle('is-speaking', Boolean(aan));
}

function haalClientNaamVoorBegroeting() {
    const naam = String(clientNaam || '').trim();
    if (naam) {
        return naam;
    }
    return actieveTaal === 'Nederlands' ? 'vriend' : 'friend';
}

function maakWakeAntwoord() {
    return vertaal('awakeReplyPersonal', { clientName: haalClientNaamVoorBegroeting() });
}

function commandoVoorSnelknop(key) {
    const commandoSet = {
        English: {
            youtube: 'open youtube',
            google: 'open google',
            calculator: 'open calculator',
            think: 'help me plan my evening',
            folder: 'create folder demo',
            explorer: 'open file explorer'
        },
        Nederlands: {
            youtube: 'open youtube',
            google: 'open google',
            calculator: 'open rekenmachine',
            think: 'denk met me mee over mijn planning voor vanavond',
            folder: 'maak map demo',
            explorer: 'open verkenner'
        }
    };

    return (commandoSet[actieveTaal] || commandoSet.English)[key] || '';
}

function commandoVoorComputerKnop(key) {
    const commandoSet = {
        English: {
            automation_enable: 'enable automation mode',
            automation_disable: 'disable automation mode',
            system_scan_start: 'start system scan',
            system_scan_status: 'system scan status',
            screenshot: 'take screenshot',
            maximize_window: 'maximize window',
            close_window: 'close window',
            focus_edge: 'focus edge',
            volume_up: 'volume up',
            mute_volume: 'mute volume',
            vscode_new_file: 'vscode new file',
            edge_inprivate: 'edge inprivate',
            discord_search: 'discord search',
            discord_mute: 'discord mute',
            whatsapp_new_chat: 'whatsapp new chat',
            steam_search: 'steam search'
        },
        Nederlands: {
            automation_enable: 'schakel automation-modus in',
            automation_disable: 'schakel automation-modus uit',
            system_scan_start: 'start systeemscan',
            system_scan_status: 'systeemscan status',
            screenshot: 'maak screenshot',
            maximize_window: 'maximaliseer venster',
            close_window: 'sluit venster',
            focus_edge: 'activeer edge',
            volume_up: 'volume omhoog',
            mute_volume: 'volume stil',
            vscode_new_file: 'vscode new file',
            edge_inprivate: 'edge inprivate',
            discord_search: 'zoek in discord',
            discord_mute: 'discord dempen',
            whatsapp_new_chat: 'nieuw chat in whatsapp',
            steam_search: 'zoek in steam'
        }
    };

    return (commandoSet[actieveTaal] || commandoSet.English)[key] || '';
}

function commandoVoorFeatureKnop(key) {
    const commandoSet = {
        English: {
            task_list: 'show tasks',
            agenda_show: 'show agenda',
            timer_5: 'set timer for 5 minutes',
            reminder_break: 'remind me in 30 minutes to stretch',
            browser_current_url: 'current page url',
            browser_read_page: 'read this page',
            browser_summarize_page: 'summarize this page',
            browser_focus_edge: 'focus edge',
            file_summarize_readme: 'summarize README.md',
            workspace_search_ollama: 'search files for ollama',
            memory_show: 'what do you remember about me',
            system_info: 'system info'
        },
        Nederlands: {
            task_list: 'toon taken',
            agenda_show: 'toon agenda',
            timer_5: 'zet timer voor 5 minuten',
            reminder_break: 'herinner me over 30 minuten aan stretchen',
            browser_current_url: 'huidige pagina url',
            browser_read_page: 'lees deze pagina',
            browser_summarize_page: 'vat deze pagina samen',
            browser_focus_edge: 'activeer edge',
            file_summarize_readme: 'vat README.md samen',
            workspace_search_ollama: 'zoek in bestanden naar ollama',
            memory_show: 'wat weet je over mij',
            system_info: 'systeeminfo'
        }
    };

    return (commandoSet[actieveTaal] || commandoSet.English)[key] || '';
}


function commandoVoorPromptChip(key) {
    const commandoSet = {
        English: {
            plan_day: 'help me plan my day',
            focus_hour: 'help me focus for the next hour',
            set_break_reminder: 'remind me in 30 minutes to take a short break',
            summarize_tab: 'summarize this page',
            search_workspace: 'search files for ollama',
            memory_review: 'what do you remember about me',
            rewrite_readme: 'rewrite README.md to be shorter and clearer',
            system_review: 'system info',
            automation_ready: 'enable automation mode'
        },
        Nederlands: {
            plan_day: 'denk met me mee over mijn dagplanning',
            focus_hour: 'help me focussen voor het komende uur',
            set_break_reminder: 'herinner me over 30 minuten aan een korte pauze',
            summarize_tab: 'vat deze pagina samen',
            search_workspace: 'zoek in bestanden naar ollama',
            memory_review: 'wat weet je over mij',
            rewrite_readme: 'herschrijf README.md zodat het korter en duidelijker is',
            system_review: 'systeeminfo',
            automation_ready: 'schakel automation-modus in'
        }
    };

    return (commandoSet[actieveTaal] || commandoSet.English)[key] || '';
}


function plaatsPromptInComposer(command) {
    if (!commandInput || !command) {
        return;
    }

    commandInput.value = command;
    commandInput.focus();
    commandInput.setSelectionRange(command.length, command.length);
    setTranslatedStatus('promptReady', {}, 'status success');
}


function browserWorkbenchCommando(action) {
    const url = String(browserWorkbenchUrl ? browserWorkbenchUrl.value : '').trim();
    const formWaarden = String(browserWorkbenchFormValues ? browserWorkbenchFormValues.value : '').trim();

    if (action === 'open_url') {
        if (!url) {
            setTranslatedStatus('browserWorkbenchNeedUrl', {}, 'status error');
            return '';
        }
        return 'open browser url::edge||' + url;
    }
    if (action === 'read_current') {
        return actieveTaal === 'Nederlands' ? 'lees deze pagina' : 'read this page';
    }
    if (action === 'summarize_current') {
        return actieveTaal === 'Nederlands' ? 'vat deze pagina samen' : 'summarize this page';
    }
    if (action === 'summarize_url') {
        if (!url) {
            setTranslatedStatus('browserWorkbenchNeedUrl', {}, 'status error');
            return '';
        }
        return actieveTaal === 'Nederlands' ? ('vat ' + url + ' samen') : ('summarize ' + url);
    }
    if (action === 'fill_form') {
        if (!formWaarden) {
            setTranslatedStatus('browserWorkbenchNeedFormValues', {}, 'status error');
            return '';
        }
        const delen = formWaarden
            .split(/\n|,/)
            .map((deel) => deel.trim())
            .filter(Boolean);
        return actieveTaal === 'Nederlands'
            ? ('vul formulier in met ' + delen.join(', '))
            : ('fill form with ' + delen.join(', '));
    }
    return '';
}


function plannerQuickCommando(type) {
    const invoer = String(plannerQuickInput ? plannerQuickInput.value : '').trim();
    if (!invoer) {
        setTranslatedStatus('plannerQuickNeedText', {}, 'status error');
        return '';
    }

    if (type === 'task') {
        return 'task add::' + invoer;
    }
    if (type === 'reminder') {
        return 'reminder create::1800||' + invoer;
    }
    return '';
}


function fileWorkbenchCommando(action) {
    const pad = String(fileWorkbenchPath ? fileWorkbenchPath.value : '').trim();
    const rewrite = String(fileWorkbenchRewrite ? fileWorkbenchRewrite.value : '').trim();
    const zoektekst = String(workspaceSearchInput ? workspaceSearchInput.value : '').trim();

    if ((action === 'read_file' || action === 'summarize_file' || action === 'rewrite_file') && !pad) {
        setTranslatedStatus('fileWorkbenchNeedPath', {}, 'status error');
        return '';
    }

    if (action === 'read_file') {
        return 'read file::' + pad;
    }
    if (action === 'summarize_file') {
        return 'summarize file::' + pad;
    }
    if (action === 'rewrite_file') {
        if (!rewrite) {
            setTranslatedStatus('fileWorkbenchNeedRewrite', {}, 'status error');
            return '';
        }
        return 'rewrite file::' + pad + '||' + rewrite;
    }
    if (action === 'search_workspace') {
        if (!zoektekst) {
            setTranslatedStatus('fileWorkbenchNeedSearch', {}, 'status error');
            return '';
        }
        return 'search files::' + zoektekst;
    }
    return '';
}

async function verstuurVooringevuldCommando(command) {
    if (!command) {
        return;
    }

    if (commandInput) {
        commandInput.value = command;
    }

    await verstuurTekstCommando();
}

function updateMicrofoonKnop() {
    if (!speechBtn) {
        return;
    }

    if (!SpeechRecognition) {
        const label = vertaal('micOrbUnavailable');
        if (speechBtnLabel) {
            speechBtnLabel.textContent = label;
        } else {
            speechBtn.textContent = label;
        }
        speechBtn.dataset.state = 'unsupported';
        speechBtn.setAttribute('aria-label', label);
        return;
    }

    let labelKey = 'micOrbPaused';
    let state = 'off';

    if (botIsAanHetPraten) {
        labelKey = 'micOrbSpeaking';
        state = 'speaking';
    } else if (luisterenActief) {
        labelKey = 'micOrbListening';
        state = 'listening';
    } else if (microfoonAltijdAan) {
        labelKey = 'micOrbReady';
        state = 'ready';
    }

    const label = vertaal(labelKey);
    if (speechBtnLabel) {
        speechBtnLabel.textContent = label;
    } else {
        speechBtn.textContent = label;
    }
    speechBtn.dataset.state = state;
    speechBtn.setAttribute('aria-label', label);
}

function verversStandaardBericht() {
    if (!messagesDiv) {
        return;
    }

    const berichten = Array.from(messagesDiv.querySelectorAll('.message'));
    if (berichten.length !== 1) {
        return;
    }

    const enigeBericht = berichten[0];
    const bekendeStandaardteksten = new Set([
        UI_TEKST.English.hint,
        UI_TEKST.Nederlands.hint,
        UI_TEKST.English.greeting,
        UI_TEKST.Nederlands.greeting
    ]);

    if (!bekendeStandaardteksten.has(enigeBericht.textContent.trim())) {
        return;
    }

    enigeBericht.textContent = begroetingTonenActief ? vertaal('greeting') : vertaal('hint');
}

function pasInterfaceTaalToe() {
    document.documentElement.lang = vertaal('docLang');

    if (subtitleText) subtitleText.textContent = vertaal('subtitle');
    if (heroEyebrow) heroEyebrow.textContent = vertaal('heroEyebrow');
    if (heroTitle) heroTitle.textContent = vertaal('heroTitle');
    if (heroCopy) heroCopy.textContent = vertaal('heroCopy');
    if (heroTagVoice) heroTagVoice.textContent = vertaal('heroTagVoice');
    if (heroTagActions) heroTagActions.textContent = vertaal('heroTagActions');
    if (heroTagThink) heroTagThink.textContent = vertaal('heroTagThink');
    if (commandsTitle) commandsTitle.textContent = vertaal('commandsTitle');
    if (commandsText) commandsText.innerHTML = vertaal('commandsText');
    if (microphoneTitle) microphoneTitle.textContent = vertaal('microphoneTitle');
    if (microphoneText) microphoneText.innerHTML = vertaal('microphoneText');
    if (voiceVisualizerTitle) voiceVisualizerTitle.textContent = vertaal('voiceVisualizerTitle');
    if (voiceVisualizerCopy) voiceVisualizerCopy.textContent = vertaal('voiceVisualizerCopy');
    if (voiceVisualizerMicLabel) voiceVisualizerMicLabel.textContent = vertaal('voiceVisualizerMicLabel');
    if (voiceVisualizerAiLabel) voiceVisualizerAiLabel.textContent = vertaal('voiceVisualizerAiLabel');
    if (commandInput) commandInput.placeholder = vertaal('commandPlaceholder');
    if (sendBtn) sendBtn.textContent = vertaal('send');
    if (quickActions) quickActions.setAttribute('aria-label', vertaal('quickActionsAria'));
    if (optionDeck) optionDeck.setAttribute('aria-label', vertaal('optionsAria'));
    if (modeStrip) modeStrip.setAttribute('aria-label', vertaal('modeStripAria'));
    if (promptStudio) promptStudio.setAttribute('aria-label', vertaal('promptStudioAria'));
    if (intentShell) intentShell.setAttribute('aria-label', vertaal('routePanelTitle'));
    if (commandLab) commandLab.setAttribute('aria-label', vertaal('commandLabTitle'));
    if (messageHint) messageHint.textContent = vertaal('hint');
    if (settingsKicker) settingsKicker.textContent = vertaal('settingsKicker');
    if (settingsTitle) settingsTitle.textContent = vertaal('settingsTitle');
    if (settingsSubtitle) settingsSubtitle.textContent = vertaal('settingsSubtitle');
    if (settingsSectionIdentity) settingsSectionIdentity.textContent = vertaal('settingsSectionIdentity');
    if (settingsSectionDestinations) settingsSectionDestinations.textContent = vertaal('settingsSectionDestinations');
    if (settingsSectionVoice) settingsSectionVoice.textContent = vertaal('settingsSectionVoice');
    if (settingsSectionBehavior) settingsSectionBehavior.textContent = vertaal('settingsSectionBehavior');
    if (naamLabel) naamLabel.textContent = vertaal('aiName');
    if (clientNaamLabel) clientNaamLabel.textContent = vertaal('clientNameLabel');
    if (taalLabel) taalLabel.textContent = vertaal('language');
    if (youtubeUrlLabel) youtubeUrlLabel.textContent = vertaal('youtubeUrl');
    if (googleUrlLabel) googleUrlLabel.textContent = vertaal('googleUrl');
    if (wakeWordLabel) wakeWordLabel.textContent = vertaal('wakeWord');
    if (stemSelectLabel) stemSelectLabel.textContent = vertaal('chooseVoice');
    if (computerBesturingLabelText) computerBesturingLabelText.textContent = vertaal('computerControl');
    if (computerBesturingNote) computerBesturingNote.textContent = vertaal('computerControlNote');
    if (emojiGebruikLabelText) emojiGebruikLabelText.textContent = vertaal('useEmojis');
    if (begroetingTonenLabelText) begroetingTonenLabelText.textContent = vertaal('showGreeting');
    if (spraakUitgangLabelText) spraakUitgangLabelText.textContent = vertaal('voiceOutput');
    if (clientNaamInput) clientNaamInput.placeholder = vertaal('clientNamePlaceholder');
    if (saveSettingsBtn) saveSettingsBtn.textContent = vertaal('saveSettings');
    if (settingsBtn) settingsBtn.textContent = vertaal('settingsButton');
    if (testVoiceBtn) testVoiceBtn.textContent = vertaal('testVoice');
    if (controlLabel) controlLabel.textContent = vertaal('controlLabel');
    if (computerPanelLabel) computerPanelLabel.textContent = vertaal('computerPanelLabel');
    if (computerPanelNote) computerPanelNote.textContent = vertaal('computerPanelNote');
    if (computerSystemLabel) computerSystemLabel.textContent = vertaal('computerSystemLabel');
    if (computerMacroLabel) computerMacroLabel.textContent = vertaal('computerMacroLabel');
    if (liveStatusLabel) liveStatusLabel.textContent = vertaal('liveStatusLabel');
    if (tipsLabel) tipsLabel.textContent = vertaal('tipsLabel');
    if (tipOne) tipOne.textContent = vertaal('tipOne');
    if (tipTwo) tipTwo.textContent = vertaal('tipTwo');
    if (tipThree) tipThree.textContent = vertaal('tipThree');

    pasDynamischeVertalingenToe();

    quickActionButtons.forEach((button) => {
        const key = button.dataset.commandKey;
        if (!key) {
            return;
        }

        button.dataset.command = commandoVoorSnelknop(key);
        button.textContent = vertaal('quickAction_' + key);
    });

    computerActionButtons.forEach((button) => {
        const key = button.dataset.computerKey;
        if (!key) {
            return;
        }

        button.dataset.command = commandoVoorComputerKnop(key);
        button.textContent = vertaal('computerAction_' + key);
    });

    featureActionButtons.forEach((button) => {
        const key = button.dataset.featureKey;
        if (!key) {
            return;
        }

        button.dataset.command = commandoVoorFeatureKnop(key);
        button.textContent = vertaal('featureAction_' + key);
    });

    promptSuggestionButtons.forEach((button) => {
        const key = button.dataset.promptKey;
        if (!key) {
            return;
        }

        button.dataset.command = commandoVoorPromptChip(key);
        button.textContent = vertaal('promptChip_' + key);
    });

    intentChipButtons.forEach((button) => {
        const key = button.dataset.intentKey;
        if (!key) {
            return;
        }

        button.dataset.command = commandoVoorIntentChip(key);
        button.textContent = vertaal('intentChip_' + key);
    });

    if (Object.keys(dashboardState || {}).length) {
        renderDashboard(dashboardState);
    } else {
        werkModusoverzichtBij(uiSettingsState);
        updateRoutePanel({}, uiSettingsState);
        syncAutomationLocks(uiSettingsState);
        if (dashboardModelMeta) {
            dashboardModelMeta.textContent = vertaal('dashboardMetricWaitingMeta');
        }
        if (dashboardCommandValue) {
            dashboardCommandValue.textContent = vertaal('dashboardNoCommandValue');
        }
        if (dashboardCommandMeta) {
            dashboardCommandMeta.textContent = vertaal('dashboardNoCommandMeta');
        }
        if (browserWorkbenchMeta) {
            browserWorkbenchMeta.textContent = vertaal('browserWorkbenchMetaEmpty');
        }
        if (fileWorkbenchMeta) {
            fileWorkbenchMeta.textContent = vertaal('fileWorkbenchMetaEmpty');
        }
        verversBestandsSuggesties([]);
    }

    updateSafetyBevestigingModal((dashboardState && dashboardState.pending_confirmation) || pendingConfirmationState);

    renderCommandDiscovery(commandDiscoveryInput ? commandDiscoveryInput.value : '');

    verversStandaardBericht();
    updateVoiceVisualizerStatus();
    updateMicrofoonKnop();
}

function speakText(text) {
    if (!('speechSynthesis' in window) || !text || !spraakUitgangActief) {
        return Promise.resolve();
    }

    speechQueue = speechQueue.then(() => new Promise((resolve) => {
        const startSpraak = () => {
            botIsAanHetPraten = true;
            setEchoSpreekAnimatie(true);
            setVoiceOutputActief(true);
            triggerVoiceOutputPulse(0.48);
            updateMicrofoonKnop();
            window.speechSynthesis.resume();

            const utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = actieveSpraakTaal;
            let afgerond = false;

            const rondSpraakAf = () => {
                if (afgerond) {
                    return;
                }

                afgerond = true;
                window.clearTimeout(fallbackTimer);
                botIsAanHetPraten = false;
                setEchoSpreekAnimatie(false);
                setVoiceOutputActief(false);
                updateMicrofoonKnop();

                if (hervatNaSpraak && recognition && microfoonAltijdAan && !luisterenActief) {
                    hervatNaSpraak = false;
                    setTimeout(() => {
                        try {
                            recognition.start();
                        } catch (_err) {
                            setTranslatedStatus('reactivateVoice');
                        }
                    }, 250);
                } else if (hervatNaSpraak) {
                    hervatNaSpraak = false;
                }

                resolve();
            };

            const fallbackTimer = window.setTimeout(() => {
                rondSpraakAf();
            }, 4000);

            if (gekozenStemUri) {
                const gekozenStem = window.speechSynthesis
                    .getVoices()
                    .find((stem) => stem.voiceURI === gekozenStemUri);
                if (gekozenStem) {
                    utterance.voice = gekozenStem;
                    utterance.lang = gekozenStem.lang || 'en-US';
                }
            }

            utterance.rate = 1;
            utterance.pitch = 1;
            utterance.volume = 1;

            utterance.onstart = () => {
                triggerVoiceOutputPulse(0.52);
            };

            utterance.onboundary = () => {
                triggerVoiceOutputPulse(0.3 + (Math.random() * 0.38));
            };

            utterance.onend = () => {
                rondSpraakAf();
            };

            utterance.onerror = () => {
                rondSpraakAf();
            };

            window.speechSynthesis.speak(utterance);
        };

        if (recognition && luisterenActief) {
            hervatNaSpraak = true;
            luisterenActief = false;
            try {
                recognition.stop();
            } catch (_err) {
                // Ignore stop errors and continue with speech.
            }
            setTimeout(startSpraak, 150);
        } else {
            startSpraak();
        }
    }));

    return speechQueue;
}

const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
let recognition = null;
let luisterenActief = false;
let microfoonAltijdAan = true;
let echoWakker = false;
let slaapTimer = null;
let wakeWord = 'hey echo';
let gekozenStemUri = '';
let beschikbareStemmen = [];
let begroetingTonenActief = true;
let clientNaam = '';

function scrollNaarLaatsteBericht() {
    if (!messagesDiv) {
        return;
    }

    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

function voegBerichtToe(type, text) {
    if (!messagesDiv || !text) {
        return;
    }

    const hint = messagesDiv.querySelector('.message.hint');
    if (hint) {
        hint.remove();
    }

    const message = document.createElement('div');
    message.className = 'message ' + type;
    message.textContent = text;
    messagesDiv.appendChild(message);
    scrollNaarLaatsteBericht();
}

function normaliseerTekst(tekst) {
    return tekst
        .normalize('NFD')
        .replace(/[\u0300-\u036f]/g, '')
        .toLowerCase()
        .replace(/[^a-z0-9\s]/g, '')
        .replace(/\s+/g, ' ')
        .trim();
}

function kiesVrouwenStem() {
    if (!('speechSynthesis' in window)) {
        return '';
    }

    const stemmen = window.speechSynthesis.getVoices();
    const taalPrefix = actieveSpraakTaal.toLowerCase().startsWith('nl') ? 'nl' : 'en';
    const stemmenVoorTaal = stemmen.filter((stem) => stem.lang && stem.lang.toLowerCase().startsWith(taalPrefix));
    const kandidaten = stemmenVoorTaal.length ? stemmenVoorTaal : stemmen;

    const vrouwenPatroon = taalPrefix === 'nl'
        ? /female|woman|fem|vrouw|marjolein|emma|claire|sophie/i
        : /female|woman|zira|hazel|aria|jenny|emma|sara|samantha|eva|claire|fem/i;
    const match = kandidaten.find((stem) => vrouwenPatroon.test(stem.name));
    return match ? match.voiceURI : '';
}

function updateStandbyTekst() {
    setTranslatedStatus('standby', { wakeWord }, 'status listening');
}

function laadStemmenDropdown() {
    if (!('speechSynthesis' in window) || !stemSelect) {
        return;
    }

    beschikbareStemmen = window.speechSynthesis.getVoices();
    stemSelect.innerHTML = '';

    const standaardOptie = document.createElement('option');
    standaardOptie.value = '';
    standaardOptie.textContent = vertaal('automaticVoice');
    stemSelect.appendChild(standaardOptie);

    beschikbareStemmen
        .filter((stem) => {
            const taalPrefix = actieveSpraakTaal.toLowerCase().startsWith('nl') ? 'nl' : 'en';
            return stem.lang && stem.lang.toLowerCase().startsWith(taalPrefix);
        })
        .forEach((stem) => {
            const optie = document.createElement('option');
            optie.value = stem.voiceURI;
            optie.textContent = stem.name + ' (' + stem.lang + ')';
            stemSelect.appendChild(optie);
        });

    if (!gekozenStemUri) {
        gekozenStemUri = kiesVrouwenStem();
    }

    if (gekozenStemUri) {
        stemSelect.value = gekozenStemUri;
    }
}

function haalWakeWordUitTekst(tekst) {
    const normalized = normaliseerTekst(tekst);
    const rawWake = normaliseerTekst(wakeWord || 'hey echo');

    const kandidaten = new Set([
        rawWake,
        'hey echo',
        'hee echo',
        'he echo',
        'hey ech',
        'hee ech',
        'hey ecko',
        'hee ecko',
        'echo'
    ]);

    for (const candidate of kandidaten) {
        if (!candidate) continue;
        const patroon = new RegExp('\\b' + candidate.replace(/\s+/g, '\\s+') + '\\b');
        if (patroon.test(normalized)) {
            const restCommando = normalized.replace(patroon, '').trim();
            return { gevonden: true, restCommando };
        }
    }

    return { gevonden: false, restCommando: '' };
}

function resetEchoNaarStandby() {
    echoWakker = false;
    if (slaapTimer) {
        clearTimeout(slaapTimer);
        slaapTimer = null;
    }
}

function startSlaapTimer() {
    if (slaapTimer) {
        clearTimeout(slaapTimer);
    }
    slaapTimer = setTimeout(() => {
        resetEchoNaarStandby();
        updateStandbyTekst();
    }, 10000);
}

async function verstuurTekstCommando() {
    const command = commandInput ? commandInput.value.trim() : '';

    if (!command) {
        setTranslatedStatus('typeCommandFirst', {}, 'status error');
        if (commandInput) {
            commandInput.focus();
        }
        return;
    }

    commandInput.value = '';
    await verstuurCommando(command, { zichtbareTekst: command });
}

async function verstuurCommando(command, opties = {}) {
    const opgeschoondCommando = command.trim();
    if (!opgeschoondCommando) return;

    const { uitSpraak = false, zichtbareTekst = opgeschoondCommando } = opties;

    voegBerichtToe('user', zichtbareTekst);

    setTranslatedStatus('working', {}, 'status working');

    if (uitSpraak) {
        await speakText(vertaal('speechHeardAction', { text: zichtbareTekst }));
    }

    try {
        const response = await fetch('/api/commando', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ commando: opgeschoondCommando })
        });

        const data = await response.json();
        updateRoutePanel(data.route || {}, dashboardState.modes || uiSettingsState);
        updateSafetyBevestigingModal(data.pending_confirmation || null);
        if (data.status === 'success') {
            voegBerichtToe('ai', data.message);
            await speakText(data.message);
            setTranslatedStatus(spraakUitgangActief ? 'successVoice' : 'successPlain', {}, 'status success');
        } else {
            const foutBericht = vertaal('errorPrefix') + data.message;
            voegBerichtToe('ai', foutBericht);
            await speakText(foutBericht);
            setStatusText(foutBericht, 'status error');
        }
    } catch (error) {
        const foutBericht = vertaal('connectionProblem');
        voegBerichtToe('ai', foutBericht);
        await speakText(foutBericht);
        setStatusText(foutBericht, 'status error');
    } finally {
        await laadDashboard();
    }
}

function initialiseerSpraakherkenning() {
    if (!SpeechRecognition) {
        speechBtn.disabled = true;
        setTranslatedStatus('speechUnsupported');
        voiceMicDenied = true;
        updateVoiceVisualizerStatus();
        updateMicrofoonKnop();
        return;
    }

    recognition = new SpeechRecognition();
    recognition.lang = actieveSpraakTaal;
    recognition.continuous = true;
    recognition.interimResults = false;

    recognition.onstart = () => {
        luisterenActief = true;
        updateMicrofoonKnop();
        speechBtn.disabled = microfoonAltijdAan;
        updateStandbyTekst();
        void zorgVoorVoiceVisualizerMicrofoon();
        updateVoiceVisualizerStatus();
    };

    recognition.onresult = async (event) => {
        const lastIndex = event.results.length - 1;
        const gesprokenTekst = event.results[lastIndex][0].transcript.trim();
        const tekst = normaliseerTekst(gesprokenTekst);
        const wakeWordData = haalWakeWordUitTekst(tekst);

        setTranslatedStatus('heard', { text: gesprokenTekst });

        if (wakeWordData.gevonden && !echoWakker) {
            echoWakker = true;
            startSlaapTimer();

            const restCommando = wakeWordData.restCommando;
            if (restCommando) {
                await verstuurCommando(restCommando, {
                    uitSpraak: true,
                    zichtbareTekst: gesprokenTekst
                });
                resetEchoNaarStandby();
                updateStandbyTekst();
            } else {
                const antwoord = maakWakeAntwoord();
                voegBerichtToe('user', gesprokenTekst);
                voegBerichtToe('ai', antwoord);
                await speakText(antwoord);
                setTranslatedStatus('awakeStatus');
            }
            return;
        }

        if (!echoWakker) {
            updateStandbyTekst();
            return;
        }

        if (tekst === 'go to sleep' || tekst === 'sleep' || tekst === 'ga slapen' || tekst === 'slaap') {
            resetEchoNaarStandby();
            const slaapBericht = vertaal('sleepReply');
            voegBerichtToe('user', gesprokenTekst);
            voegBerichtToe('ai', slaapBericht);
            await speakText(slaapBericht);
            updateStandbyTekst();
            return;
        }

        startSlaapTimer();
        await verstuurCommando(tekst, {
            uitSpraak: true,
            zichtbareTekst: gesprokenTekst
        });
        resetEchoNaarStandby();
        updateStandbyTekst();
    };

    recognition.onerror = () => {
        setTranslatedStatus('speechError');
        if (!botIsAanHetPraten) {
            speakText(vertaal('speechErrorVoice'));
        }
        updateVoiceVisualizerStatus();
    };

    recognition.onend = () => {
        if (luisterenActief && !botIsAanHetPraten) {
            try {
                recognition.start();
            } catch (_err) {
                luisterenActief = false;
                updateMicrofoonKnop();
                speechBtn.disabled = false;
                setTranslatedStatus('microphoneStopped');
            }
        }
        updateVoiceVisualizerStatus();
    };
}

function toggleMicrofoon() {
    if (!recognition) {
        updateVoiceVisualizerStatus();
        return;
    }

    if (microfoonAltijdAan && !luisterenActief) {
        try {
            void zorgVoorVoiceVisualizerMicrofoon();
            recognition.start();
            setTranslatedStatus('microphoneActivated', { wakeWord }, 'status listening');
        } catch (_err) {
            setTranslatedStatus('microphonePermission');
        }
        updateVoiceVisualizerStatus();
        return;
    }

    if (microfoonAltijdAan && luisterenActief) {
        setTranslatedStatus('microphoneStaysOn', {}, 'status listening');
        updateVoiceVisualizerStatus();
        return;
    }

    if (!luisterenActief) {
        void zorgVoorVoiceVisualizerMicrofoon();
        recognition.start();
    } else {
        luisterenActief = false;
        resetEchoNaarStandby();
        recognition.stop();
        updateMicrofoonKnop();
        setTranslatedStatus('microphoneStopped');
    }

    updateVoiceVisualizerStatus();
}

// Load and display settings
async function loadSettings() {
    try {
        const response = await fetch('/api/instellingen');
        const settings = await response.json();

        uiSettingsState = { ...settings };
        actieveTaal = normaliseerTaalwaarde(settings.taal || 'English');
        actieveSpraakTaal = settings.spraak_taal || UI_TEKST[actieveTaal].speechLang;
        pasInterfaceTaalToe();

        document.getElementById('naam').value = settings.naam || '';
        clientNaam = String(settings.client_naam || '').trim();
        if (clientNaamInput) {
            clientNaamInput.value = clientNaam;
        }
        if (taalSelect) {
            taalSelect.value = actieveTaal;
        }
        document.getElementById('youtubeUrl').value = settings.youtube_url || '';
        document.getElementById('googleUrl').value = settings.google_url || '';
        document.getElementById('computerBesturingToestaan').checked = settings.computerbesturing_toestaan === true;
        document.getElementById('emojiGebruik').checked = settings.emoji_gebruik || false;
        begroetingTonenActief = settings.begroeting_tonen !== false;
        document.getElementById('begroetingTonen').checked = begroetingTonenActief;
        spraakUitgangActief = settings.spraak_uitgang !== false;
        document.getElementById('spraakUitgang').checked = spraakUitgangActief;
        document.getElementById('agentModus').checked = settings.agent_modus !== false;
        document.getElementById('aiAgentPrimair').checked = settings.ai_agent_primair !== false;
        document.getElementById('onlineAiModus').checked = settings.online_ai_modus !== false;
        document.getElementById('geheugenModus').checked = settings.geheugen_modus !== false;
        document.getElementById('prioriteitModus').checked = settings.prioriteit_modus !== false;
        document.getElementById('wakeWord').value = settings.wake_word || vertaal('defaultWakeWord');

        wakeWord = normaliseerTekst(settings.wake_word || vertaal('defaultWakeWord'));
        document.getElementById('wakeWord').placeholder = vertaal('wakeWordPlaceholder');
        gekozenStemUri = settings.browser_stem || kiesVrouwenStem();
        if (recognition) {
            recognition.lang = actieveSpraakTaal;
        }
        laadStemmenDropdown();
        if (Object.keys(dashboardState || {}).length) {
            renderDashboard(dashboardState);
        }
    } catch (error) {
        console.error('Error loading settings:', error);
    }
}

// Save settings
async function saveSettings() {
    actieveTaal = normaliseerTaalwaarde(taalSelect ? taalSelect.value : actieveTaal);
    actieveSpraakTaal = UI_TEKST[actieveTaal].speechLang;

    gekozenStemUri = stemSelect ? stemSelect.value : '';
    clientNaam = clientNaamInput ? clientNaamInput.value.trim() : '';
    const wakeWordInvoer = (document.getElementById('wakeWord').value || '').trim() || vertaal('defaultWakeWord');
    wakeWord = normaliseerTekst(wakeWordInvoer);
    spraakUitgangActief = document.getElementById('spraakUitgang').checked;
    if (recognition) {
        recognition.lang = actieveSpraakTaal;
    }

    const settings = {
        naam: document.getElementById('naam').value,
        client_naam: clientNaam,
        taal: actieveTaal,
        youtube_url: document.getElementById('youtubeUrl').value,
        google_url: document.getElementById('googleUrl').value,
        computerbesturing_toestaan: document.getElementById('computerBesturingToestaan').checked,
        emoji_gebruik: document.getElementById('emojiGebruik').checked,
        begroeting_tonen: document.getElementById('begroetingTonen').checked,
        spraak_uitgang: document.getElementById('spraakUitgang').checked,
        agent_modus: document.getElementById('agentModus').checked,
        ai_agent_primair: document.getElementById('aiAgentPrimair').checked,
        online_ai_modus: document.getElementById('onlineAiModus').checked,
        geheugen_modus: document.getElementById('geheugenModus').checked,
        prioriteit_modus: document.getElementById('prioriteitModus').checked,
        spraak_taal: actieveSpraakTaal,
        wake_word: wakeWordInvoer,
        browser_stem: gekozenStemUri
    };

    uiSettingsState = { ...uiSettingsState, ...settings };
    pasInterfaceTaalToe();

    try {
        const response = await fetch('/api/instellingen', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(settings)
        });

        const data = await response.json();
        if (data.status === 'success') {
            await speakText(data.message || vertaal('settingsSaved'));
            if (luisterenActief) {
                updateStandbyTekst();
            } else {
                setTranslatedStatus('settingsSaved', {}, 'status success');
            }
            await laadDashboard();
            closeModalFunc();
        }
    } catch (error) {
        await speakText(vertaal('savingFailed'));
        setTranslatedStatus('savingFailed', {}, 'status error');
    }
}

// Modal functions
function openModalFunc() {
    modal.style.display = 'block';
    loadSettings();
}

function closeModalFunc() {
    modal.style.display = 'none';
}

// Event listeners
if (speechBtn) {
    speechBtn.addEventListener('click', toggleMicrofoon);
}

if (sendBtn) {
    sendBtn.addEventListener('click', verstuurTekstCommando);
}

if (commandInput) {
    commandInput.addEventListener('keydown', async (event) => {
        if (event.key !== 'Enter') {
            return;
        }

        event.preventDefault();
        await verstuurTekstCommando();
    });
}

quickActionButtons.forEach((button) => {
    button.addEventListener('click', async () => {
        const command = button.dataset.command || commandoVoorSnelknop(button.dataset.commandKey || '');
        await verstuurVooringevuldCommando(command);
    });
});

computerActionButtons.forEach((button) => {
    button.addEventListener('click', async () => {
        const command = button.dataset.command || commandoVoorComputerKnop(button.dataset.computerKey || '');
        await verstuurVooringevuldCommando(command);
    });
});

featureActionButtons.forEach((button) => {
    button.addEventListener('click', async () => {
        const command = button.dataset.command || commandoVoorFeatureKnop(button.dataset.featureKey || '');
        await verstuurVooringevuldCommando(command);
    });
});

promptSuggestionButtons.forEach((button) => {
    button.addEventListener('click', () => {
        const command = button.dataset.command || commandoVoorPromptChip(button.dataset.promptKey || '');
        plaatsPromptInComposer(command);
    });
});

intentChipButtons.forEach((button) => {
    button.addEventListener('click', () => {
        const command = button.dataset.command || commandoVoorIntentChip(button.dataset.intentKey || '');
        plaatsPromptInComposer(command);
    });
});

browserWorkbenchButtons.forEach((button) => {
    button.addEventListener('click', async () => {
        const command = browserWorkbenchCommando(button.dataset.browserAction || '');
        if (!command) {
            return;
        }
        await verstuurVooringevuldCommando(command);
    });
});

fileWorkbenchButtons.forEach((button) => {
    button.addEventListener('click', async () => {
        const command = fileWorkbenchCommando(button.dataset.fileAction || '');
        if (!command) {
            return;
        }
        await verstuurVooringevuldCommando(command);
    });
});

if (plannerQuickTaskBtn) {
    plannerQuickTaskBtn.addEventListener('click', async () => {
        const command = plannerQuickCommando('task');
        if (!command) {
            return;
        }
        await verstuurVooringevuldCommando(command);
        plannerQuickInput.value = '';
    });
}

if (plannerQuickReminderBtn) {
    plannerQuickReminderBtn.addEventListener('click', async () => {
        const command = plannerQuickCommando('reminder');
        if (!command) {
            return;
        }
        await verstuurVooringevuldCommando(command);
        plannerQuickInput.value = '';
    });
}

if (plannerQuickInput) {
    plannerQuickInput.addEventListener('keydown', async (event) => {
        if (event.key !== 'Enter') {
            return;
        }
        event.preventDefault();
        const command = plannerQuickCommando('task');
        if (!command) {
            return;
        }
        await verstuurVooringevuldCommando(command);
        plannerQuickInput.value = '';
    });
}

if (workspaceSearchInput) {
    workspaceSearchInput.addEventListener('keydown', async (event) => {
        if (event.key !== 'Enter') {
            return;
        }
        event.preventDefault();
        const command = fileWorkbenchCommando('search_workspace');
        if (!command) {
            return;
        }
        await verstuurVooringevuldCommando(command);
    });
}

if (commandDiscoveryInput) {
    commandDiscoveryInput.addEventListener('input', () => {
        renderCommandDiscovery(commandDiscoveryInput.value);
    });
}

if (testVoiceBtn) {
    testVoiceBtn.addEventListener('click', async () => {
        await speakText(vertaal('testVoiceSample'));
        setTranslatedStatus('voiceTestPlayed');
    });
}

if (taalSelect) {
    taalSelect.addEventListener('change', () => {
        actieveTaal = normaliseerTaalwaarde(taalSelect.value);
        actieveSpraakTaal = UI_TEKST[actieveTaal].speechLang;
        pasInterfaceTaalToe();
        document.getElementById('wakeWord').placeholder = vertaal('wakeWordPlaceholder');
        laadStemmenDropdown();
        if (luisterenActief) {
            updateStandbyTekst();
        }
    });
}

settingsBtn.addEventListener('click', openModalFunc);
closeModal.addEventListener('click', closeModalFunc);
saveSettingsBtn.addEventListener('click', saveSettings);

if (safetyConfirmYesBtn) {
    safetyConfirmYesBtn.addEventListener('click', async () => {
        await verstuurSafetyBevestiging(true);
    });
}

if (safetyConfirmNoBtn) {
    safetyConfirmNoBtn.addEventListener('click', async () => {
        await verstuurSafetyBevestiging(false);
    });
}

window.addEventListener('click', (event) => {
    if (event.target === modal) closeModalFunc();
});

if ('speechSynthesis' in window) {
    window.speechSynthesis.onvoiceschanged = laadStemmenDropdown;
}

// Initial spoken message
window.addEventListener('load', async () => {
    void registreerServiceWorker();
    initialiseerVoiceVisualizer();
    initialiseerSpraakherkenning();
    await loadSettings();
    await laadDashboard();
    startDashboardPolling();
    startRuntimeVersiePolling();

    setTimeout(() => {
        if (recognition && !luisterenActief) {
            try {
                void zorgVoorVoiceVisualizerMicrofoon();
                recognition.start();
            } catch (_err) {
                speechBtn.disabled = false;
                updateMicrofoonKnop();
                setTranslatedStatus('grantPermission');
            }
        }
    }, 500);

    if (begroetingTonenActief) {
        const begroeting = vertaal('greeting');
        voegBerichtToe('ai', begroeting);
        speakText(begroeting);
    }

    if (SpeechRecognition) {
        setTranslatedStatus('voiceModeActive', { wakeWord }, 'status listening');
    } else {
        setTranslatedStatus('textModeActive');
    }
    updateVoiceVisualizerStatus();

    if (commandInput) {
        commandInput.focus();
    }
});
