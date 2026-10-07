const functionalCheckerState = {
    running: false,
    activeTaskId: '',
    startedAt: 0,
    durationTimer: 0,
    progress: 0,
    lastLogKey: '',
    rawReportUrl: '',
    frameReportUrl: '',
};

const FUNCTIONAL_STAGE_ORDER = [
    'queued',
    'module_load',
    'homepage',
    'parse_dom',
    'links',
    'buttons',
    'search_bars',
    'summary',
    'report_build',
    'completed',
    'failed',
];

const stageLabels = {
    queued: 'Wachtrij',
    module_load: 'Module',
    homepage: 'Homepage',
    parse_dom: 'DOM Parse',
    links: 'Links',
    buttons: 'Knoppen',
    search_bars: 'Zoekbalk',
    summary: 'Samenvatting',
    report_build: 'Rapport',
    completed: 'Klaar',
    failed: 'Mislukt',
};

const el = {
    form: document.getElementById('functionalCheckerForm'),
    urlInput: document.getElementById('functionalCheckerUrlInput'),
    startBtn: document.getElementById('functionalCheckerStartBtn'),
    openQuickBtn: document.getElementById('functionalCheckerOpenQuickBtn'),
    openReportBtn: document.getElementById('functionalCheckerOpenReportBtn'),
    backBtn: document.getElementById('functionalCheckerBackBtn'),
    target: document.getElementById('functionalCheckerTarget'),
    state: document.getElementById('functionalCheckerState'),
    progressFill: document.getElementById('functionalCheckerProgressFill'),
    progressPercent: document.getElementById('functionalCheckerProgressPercent'),
    duration: document.getElementById('functionalCheckerDuration'),
    currentTest: document.getElementById('functionalCheckerCurrentTest'),
    stages: document.getElementById('functionalCheckerStages'),
    counters: document.getElementById('functionalCheckerCounters'),
    liveLog: document.getElementById('functionalCheckerLiveLog'),
    frame: document.getElementById('functionalCheckerFrame'),
};

function normalizeStatus(value) {
    const status = String(value || '').trim().toLowerCase();
    if (status === 'completed' || status === 'failed' || status === 'running' || status === 'queued') {
        return status;
    }
    return 'queued';
}

function normalizeStage(value) {
    const stage = String(value || '').trim().toLowerCase();
    return FUNCTIONAL_STAGE_ORDER.includes(stage) ? stage : 'queued';
}

function stageIndex(stage) {
    const normalized = normalizeStage(stage);
    const index = FUNCTIONAL_STAGE_ORDER.indexOf(normalized);
    if (index >= 0) {
        return index;
    }
    return FUNCTIONAL_STAGE_ORDER.indexOf('completed');
}

function setState(message, tone = 'idle') {
    if (!el.state) {
        return;
    }

    el.state.textContent = String(message || '').trim();
    el.state.dataset.tone = String(tone || 'idle').trim().toLowerCase();
}

function setTargetLine(targetUrl = '') {
    if (!el.target) {
        return;
    }

    const cleaned = String(targetUrl || '').trim();
    el.target.textContent = cleaned
        ? `Doel: ${cleaned}`
        : 'Doel: wacht op URL-invoer';
}

function setCurrentTest(currentTest = null) {
    if (!el.currentTest) {
        return;
    }

    const task = currentTest && typeof currentTest === 'object' ? currentTest : {};
    const testType = String(task.type || '').trim().toLowerCase();
    const testId = String(task.id || '').trim();
    const testTarget = String(task.target || '').trim();

    if (!testType && !testId && !testTarget) {
        el.currentTest.textContent = 'Huidige test: -';
        return;
    }

    const label = stageLabels[testType] || testType.toUpperCase() || 'TEST';
    const detail = [testId, testTarget].filter(Boolean).join(' | ');
    el.currentTest.textContent = `Huidige test: ${label}${detail ? ` | ${detail}` : ''}`;
}

function setProgress(value) {
    const normalized = Math.max(0, Math.min(100, Number(value || 0)));
    functionalCheckerState.progress = normalized;

    if (el.progressFill) {
        el.progressFill.style.width = `${normalized}%`;
    }

    if (el.progressPercent) {
        el.progressPercent.textContent = `${Math.round(normalized)}%`;
    }
}

function formatDuration(seconds) {
    const total = Math.max(0, Math.round(Number(seconds || 0)));
    const mins = Math.floor(total / 60);
    const secs = total % 60;
    if (mins > 0) {
        return `${mins}m ${String(secs).padStart(2, '0')}s`;
    }
    return `${secs}s`;
}

function updateDurationLabel() {
    if (!el.duration || !functionalCheckerState.startedAt) {
        return;
    }

    const elapsed = (Date.now() - functionalCheckerState.startedAt) / 1000;
    el.duration.textContent = `Tijd: ${formatDuration(elapsed)}`;
}

function stopDurationTicker() {
    if (functionalCheckerState.durationTimer) {
        window.clearInterval(functionalCheckerState.durationTimer);
        functionalCheckerState.durationTimer = 0;
    }
}

function startDurationTicker() {
    stopDurationTicker();
    updateDurationLabel();

    functionalCheckerState.durationTimer = window.setInterval(() => {
        if (!functionalCheckerState.running) {
            return;
        }
        updateDurationLabel();
    }, 400);
}

function resetStages() {
    const nodes = el.stages ? Array.from(el.stages.querySelectorAll('li')) : [];
    nodes.forEach((node) => {
        node.dataset.state = 'idle';
    });
}

function updateStages(stage, status = 'running') {
    const nodes = el.stages ? Array.from(el.stages.querySelectorAll('li')) : [];
    if (!nodes.length) {
        return;
    }

    const currentIndex = stageIndex(stage);
    const normalizedStatus = normalizeStatus(status);

    nodes.forEach((node, index) => {
        let state = 'idle';

        if (normalizedStatus === 'completed') {
            state = 'completed';
        } else if (normalizedStatus === 'failed') {
            if (index < currentIndex) {
                state = 'completed';
            } else if (index === Math.min(currentIndex, nodes.length - 1)) {
                state = 'failed';
            }
        } else {
            if (index < currentIndex) {
                state = 'completed';
            } else if (index === currentIndex) {
                state = 'active';
            }
        }

        node.dataset.state = state;
    });
}

function clearLiveLog() {
    if (!el.liveLog) {
        return;
    }

    el.liveLog.innerHTML = '';
    const empty = document.createElement('p');
    empty.className = 'functional-checker-live-empty';
    empty.textContent = 'Nog geen live checks. Start Functional Check om stappen live te zien.';
    el.liveLog.appendChild(empty);
}

function appendLiveLog(message, tone = 'info') {
    if (!el.liveLog) {
        return;
    }

    const text = String(message || '').trim();
    if (!text) {
        return;
    }

    const emptyNode = el.liveLog.querySelector('.functional-checker-live-empty');
    if (emptyNode) {
        emptyNode.remove();
    }

    const line = document.createElement('p');
    line.className = 'functional-checker-live-line';
    line.dataset.tone = String(tone || 'info').trim().toLowerCase();
    const timestamp = new Date().toLocaleTimeString('nl-NL', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
    });
    line.textContent = `[${timestamp}] ${text}`;
    el.liveLog.appendChild(line);

    const lines = Array.from(el.liveLog.querySelectorAll('.functional-checker-live-line'));
    if (lines.length > 34) {
        lines.slice(0, lines.length - 34).forEach((node) => node.remove());
    }

    el.liveLog.scrollTop = el.liveLog.scrollHeight;
}

function renderCounters(summary = null) {
    if (!el.counters) {
        return;
    }

    el.counters.innerHTML = '';

    if (!summary || typeof summary !== 'object') {
        const empty = document.createElement('p');
        empty.className = 'functional-checker-counter-empty';
        empty.textContent = 'Wachten op scan samenvatting...';
        el.counters.appendChild(empty);
        return;
    }

    const rows = [
        `Overall: ${String(summary.overall_status || '-').toUpperCase()}`,
        `Links: ${Number(summary.links_ok || 0)}/${Number(summary.links_total || 0)}`,
        `Knoppen: ${Number(summary.buttons_ok || 0)}/${Number(summary.buttons_total || 0)}`,
        `Zoekbalk: ${Number(summary.search_ok || 0)}/${Number(summary.search_total || 0)}`,
        `CSS: ${Number(summary.css_ok || 0)}/${Number(summary.css_total || 0)}`,
    ];

    rows.forEach((row) => {
        const item = document.createElement('p');
        item.className = 'functional-checker-counter';
        item.textContent = row;
        el.counters.appendChild(item);
    });
}

function setFramePlaceholder() {
    if (!el.frame) {
        return;
    }

    const placeholder = 'Visual report verschijnt hier nadat de Functional Check klaar is.';
    el.frame.srcdoc = `<html><body style="margin:0;font-family:Segoe UI,Tahoma,Arial,sans-serif;background:#03111a;color:#c9ecff;display:flex;align-items:center;justify-content:center;min-height:100%;padding:16px;text-align:center;">${placeholder}</body></html>`;
}

function resolveReportUrl(reportPath) {
    const path = String(reportPath || '').trim();
    if (!path) {
        return '';
    }

    if (path.startsWith('http://') || path.startsWith('https://')) {
        return path;
    }

    try {
        return new URL(path, window.location.origin).toString();
    } catch (_error) {
        return path;
    }
}

function loadReportInFrame(reportUrl) {
    if (!el.frame) {
        return false;
    }

    const cleanUrl = String(reportUrl || '').trim();
    if (!cleanUrl) {
        return false;
    }

    const framedUrl = `${cleanUrl}${cleanUrl.includes('?') ? '&' : '?'}embed=functional&t=${Date.now()}`;
    functionalCheckerState.rawReportUrl = cleanUrl;
    functionalCheckerState.frameReportUrl = framedUrl;
    el.frame.src = framedUrl;
    updateControls();
    return true;
}

function openReportInTab() {
    const reportUrl = String(functionalCheckerState.rawReportUrl || '').trim();
    if (!reportUrl) {
        setState('Nog geen visueel rapport beschikbaar.', 'error');
        return;
    }

    window.open(reportUrl, '_blank', 'noopener');
}

function updateControls() {
    const disabled = functionalCheckerState.running;

    if (el.startBtn) {
        el.startBtn.disabled = disabled;
        el.startBtn.textContent = disabled ? 'Scannen...' : 'Start Functional Check';
    }

    if (el.urlInput) {
        el.urlInput.disabled = disabled;
    }

    if (el.openReportBtn) {
        el.openReportBtn.disabled = !String(functionalCheckerState.rawReportUrl || '').trim();
    }
}

function buildLogKey(task) {
    const status = normalizeStatus(task.status);
    const stage = normalizeStage(task.stage);
    const message = String(task.message || '').trim();
    const progress = Math.round(Number(task.progress_percent || 0));

    const currentTest = task.current_test && typeof task.current_test === 'object'
        ? task.current_test
        : {};
    const testType = String(currentTest.type || '').trim();
    const testId = String(currentTest.id || '').trim();
    const testTarget = String(currentTest.target || '').trim();

    return [status, stage, message, progress, testType, testId, testTarget].join('|');
}

function applyTask(task = {}) {
    if (!task || typeof task !== 'object') {
        return;
    }

    const status = normalizeStatus(task.status);
    const stage = normalizeStage(task.stage);
    const progress = Math.max(0, Math.min(100, Number(task.progress_percent || 0)));
    const message = String(task.message || '').trim();
    const targetUrl = String(task.target_url || '').trim();

    if (task.id) {
        functionalCheckerState.activeTaskId = String(task.id).trim();
    }

    functionalCheckerState.running = status !== 'completed' && status !== 'failed';

    if (targetUrl) {
        setTargetLine(targetUrl);
    }

    setProgress(progress);
    updateStages(stage, status);

    if (message) {
        const tone = status === 'failed' ? 'error' : (status === 'completed' ? 'success' : 'running');
        setState(message, tone);
    }

    const currentTest = task.current_test && typeof task.current_test === 'object'
        ? task.current_test
        : {};
    setCurrentTest(currentTest);

    const logKey = buildLogKey(task);
    if (logKey !== functionalCheckerState.lastLogKey && message) {
        const tone = status === 'failed' ? 'error' : (status === 'completed' ? 'success' : 'info');
        appendLiveLog(message, tone);
        functionalCheckerState.lastLogKey = logKey;
    }

    const resultPayload = task.result && typeof task.result === 'object' ? task.result : null;
    if (resultPayload && resultPayload.summary && typeof resultPayload.summary === 'object') {
        renderCounters(resultPayload.summary);
    }

    if (status === 'completed') {
        stopDurationTicker();
        const reportPath = resultPayload ? String(resultPayload.report_url || '').trim() : '';
        const reportUrl = resolveReportUrl(reportPath);
        if (reportUrl) {
            const loaded = loadReportInFrame(reportUrl);
            if (loaded) {
                appendLiveLog('Visueel rapport geladen in deze tab.', 'success');
            }
        }
    } else if (status === 'failed') {
        stopDurationTicker();
    }

    updateControls();
}

async function readResponseJson(response) {
    try {
        const payload = await response.json();
        return payload && typeof payload === 'object' ? payload : {};
    } catch (_error) {
        return {};
    }
}

function wait(ms) {
    return new Promise((resolve) => {
        window.setTimeout(resolve, Math.max(0, Number(ms || 0)));
    });
}

async function fetchTaskStatus(taskId) {
    const response = await fetch(`/api/website-functional-check/status/${encodeURIComponent(taskId)}`, {
        cache: 'no-store',
    });

    const payload = await readResponseJson(response);
    if (!response.ok || payload.status !== 'success') {
        const message = String(payload.message || 'Status ophalen van functional check is mislukt.').trim();
        throw new Error(message || 'Status ophalen van functional check is mislukt.');
    }

    return payload.task && typeof payload.task === 'object' ? payload.task : {};
}

async function waitForTaskCompletion(taskId) {
    const maxPolls = 360;

    for (let attempt = 0; attempt < maxPolls; attempt += 1) {
        if (!functionalCheckerState.running || functionalCheckerState.activeTaskId !== taskId) {
            return null;
        }

        await wait(850);
        const task = await fetchTaskStatus(taskId);
        applyTask(task);

        const status = normalizeStatus(task.status);
        if (status === 'completed' || status === 'failed') {
            return task;
        }
    }

    throw new Error('Timeout tijdens live scanstatus polling.');
}

async function startScan(event) {
    event.preventDefault();

    if (functionalCheckerState.running) {
        return;
    }

    const rawUrl = String(el.urlInput ? el.urlInput.value : '').trim();
    if (!rawUrl) {
        setState('Vul eerst een geldige URL in.', 'error');
        return;
    }

    functionalCheckerState.running = true;
    functionalCheckerState.activeTaskId = '';
    functionalCheckerState.startedAt = Date.now();
    functionalCheckerState.lastLogKey = '';
    functionalCheckerState.rawReportUrl = '';
    functionalCheckerState.frameReportUrl = '';

    setTargetLine(rawUrl);
    setCurrentTest(null);
    setProgress(2);
    setState('Functional check gestart.', 'running');
    resetStages();
    updateStages('queued', 'running');
    renderCounters(null);
    clearLiveLog();
    setFramePlaceholder();
    appendLiveLog('Scan gestart, taak wordt voorbereid...');
    startDurationTicker();
    updateControls();

    try {
        const response = await fetch('/api/website-functional-check/start', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                url: rawUrl,
            }),
        });

        const payload = await readResponseJson(response);
        if (!response.ok || payload.status !== 'success') {
            const message = String(payload.message || 'Functional check kon niet starten.').trim();
            throw new Error(message || 'Functional check kon niet starten.');
        }

        const firstTask = payload.task && typeof payload.task === 'object' ? payload.task : {};
        applyTask(firstTask);

        const firstStatus = normalizeStatus(firstTask.status);
        if (firstStatus === 'completed') {
            setState('Functional check afgerond.', 'success');
            return;
        }

        if (firstStatus === 'failed') {
            const startError = String(firstTask.error || firstTask.message || 'Functional check mislukt.').trim();
            throw new Error(startError || 'Functional check mislukt.');
        }

        const taskId = String(firstTask.id || '').trim();
        if (!taskId) {
            throw new Error('Geen taak-id ontvangen voor live functional check.');
        }

        functionalCheckerState.activeTaskId = taskId;
        const finalTask = await waitForTaskCompletion(taskId);
        if (!finalTask) {
            return;
        }

        const finalStatus = normalizeStatus(finalTask.status);
        if (finalStatus === 'failed') {
            const finalError = String(finalTask.error || finalTask.message || 'Functional check mislukt.').trim();
            throw new Error(finalError || 'Functional check mislukt.');
        }

        if (finalStatus === 'completed') {
            setState('Functional check afgerond.', 'success');
        }
    } catch (error) {
        functionalCheckerState.running = false;
        stopDurationTicker();
        updateStages('report_build', 'failed');

        const message = error instanceof Error
            ? String(error.message || 'Onbekende fout tijdens functional check.').trim()
            : 'Onbekende fout tijdens functional check.';

        setState(message || 'Onbekende fout tijdens functional check.', 'error');
        appendLiveLog(message || 'Onbekende fout tijdens functional check.', 'error');
    } finally {
        if (!functionalCheckerState.running) {
            stopDurationTicker();
            updateDurationLabel();
        }
        updateControls();
    }
}

async function restoreLatestTask() {
    try {
        const response = await fetch('/api/website-functional-check/status/latest', {
            cache: 'no-store',
        });

        if (response.status === 404) {
            return;
        }

        const payload = await readResponseJson(response);
        if (!response.ok || payload.status !== 'success' || !payload.task || typeof payload.task !== 'object') {
            return;
        }

        const task = payload.task;
        const startedAtSeconds = Number(task.started_at || 0);
        if (startedAtSeconds > 0) {
            functionalCheckerState.startedAt = startedAtSeconds * 1000;
        }

        applyTask(task);

        const status = normalizeStatus(task.status);
        if (status === 'running' || status === 'queued') {
            functionalCheckerState.running = true;
            startDurationTicker();
            updateControls();

            const taskId = String(task.id || '').trim();
            if (taskId) {
                functionalCheckerState.activeTaskId = taskId;
                const finalTask = await waitForTaskCompletion(taskId);
                if (finalTask) {
                    const finalStatus = normalizeStatus(finalTask.status);
                    if (finalStatus === 'completed') {
                        setState('Functional check afgerond.', 'success');
                    } else if (finalStatus === 'failed') {
                        setState(String(finalTask.message || 'Functional check mislukt.'), 'error');
                    }
                }
            }
        }
    } catch (_error) {
        // Ignore restore errors to keep the checker usable.
    } finally {
        if (!functionalCheckerState.running) {
            stopDurationTicker();
        }
        updateControls();
    }
}

function openQuickCheckerTab() {
    const popup = window.open('/quick-checker', '_blank', 'noopener');
    if (popup) {
        popup.focus();
    }
}

function backToEcho() {
    try {
        if (window.opener && !window.opener.closed) {
            window.opener.focus();
            window.close();
            return;
        }
    } catch (_error) {
        // Fallback to root navigation when opener is unavailable.
    }

    window.location.href = '/';
}

function prefillUrlFromQuery() {
    const query = new URLSearchParams(window.location.search || '');
    const queryUrl = String(query.get('url') || '').trim();
    if (!queryUrl) {
        return;
    }

    if (el.urlInput) {
        el.urlInput.value = queryUrl;
    }

    setTargetLine(queryUrl);
}

function bindEvents() {
    if (el.form) {
        el.form.addEventListener('submit', startScan);
    }

    if (el.openReportBtn) {
        el.openReportBtn.addEventListener('click', openReportInTab);
    }

    if (el.openQuickBtn) {
        el.openQuickBtn.addEventListener('click', openQuickCheckerTab);
    }

    if (el.backBtn) {
        el.backBtn.addEventListener('click', backToEcho);
    }
}

function init() {
    setTargetLine('');
    setCurrentTest(null);
    setState('Stand-by. Vul een URL in en start de scan.', 'idle');
    setProgress(0);
    resetStages();
    updateStages('queued', 'queued');
    renderCounters(null);
    clearLiveLog();
    setFramePlaceholder();

    if (el.duration) {
        el.duration.textContent = 'Tijd: --';
    }

    prefillUrlFromQuery();
    bindEvents();
    updateControls();
    void restoreLatestTask();
}

init();

window.addEventListener('beforeunload', () => {
    functionalCheckerState.running = false;
    functionalCheckerState.activeTaskId = '';
    stopDurationTicker();
});
