const quickCheckerState = {
    mode: 'quick',
    running: false,
    startedAt: 0,
    progressTimer: 0,
    progressValue: 0,
    lastPayload: null,
    activeTaskId: '',
    popupMode: false,
};

const LIVE_STAGE_ORDER = ['queued', 'module_load', 'scan_running', 'report_build', 'cache_store', 'completed'];

const el = {
    form: document.getElementById('quickCheckerForm'),
    urlInput: document.getElementById('quickCheckerUrlInput'),
    modeQuickBtn: document.getElementById('quickCheckerModeQuick'),
    modeHardBtn: document.getElementById('quickCheckerModeHard'),
    startBtn: document.getElementById('quickCheckerStartBtn'),
    popupBtn: document.getElementById('quickCheckerOpenPopupBtn'),
    backToEchoBtn: document.getElementById('quickCheckerBackToEchoBtn'),
    status: document.getElementById('quickCheckerStatus'),
    progressFill: document.getElementById('quickCheckerProgressFill'),
    progressPercent: document.getElementById('quickCheckerProgressPercent'),
    duration: document.getElementById('quickCheckerDuration'),
    overallScore: document.getElementById('quickCheckerOverallScore'),
    grade: document.getElementById('quickCheckerGrade'),
    risk: document.getElementById('quickCheckerRisk'),
    findingsCount: document.getElementById('quickCheckerFindingsCount'),
    ratings: document.getElementById('quickCheckerRatings'),
    adminContacts: document.getElementById('quickCheckerAdminContacts'),
    actionPlan: document.getElementById('quickCheckerActionPlan'),
    topPriorities: document.getElementById('quickCheckerTopPriorities'),
    findingsList: document.getElementById('quickCheckerFindingsList'),
    priorityLegend: document.getElementById('quickCheckerPriorityLegend'),
    liveStages: document.getElementById('quickCheckerLiveStages'),
    downloadJsonBtn: document.getElementById('quickCheckerDownloadJsonBtn'),
    downloadTxtBtn: document.getElementById('quickCheckerDownloadTxtBtn'),
    downloadBriefBtn: document.getElementById('quickCheckerDownloadBriefBtn'),
    copyPrioritiesBtn: document.getElementById('quickCheckerCopyPrioritiesBtn'),
    copyClientBtn: document.getElementById('quickCheckerCopyClientBtn'),
    clientMessage: document.getElementById('quickCheckerClientMessage'),
    textReport: document.getElementById('quickCheckerTextReport'),
};

function setMode(mode) {
    quickCheckerState.mode = mode === 'hard' ? 'hard' : 'quick';

    if (el.modeQuickBtn) {
        el.modeQuickBtn.classList.toggle('is-active', quickCheckerState.mode === 'quick');
    }
    if (el.modeHardBtn) {
        el.modeHardBtn.classList.toggle('is-active', quickCheckerState.mode === 'hard');
    }
}

function setStatus(message, tone = 'idle') {
    if (!el.status) {
        return;
    }
    el.status.textContent = String(message || '').trim();
    el.status.dataset.tone = tone;
}

function setProgress(value) {
    const normalized = Math.max(0, Math.min(100, Number(value || 0)));
    quickCheckerState.progressValue = normalized;

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
    if (!el.duration || !quickCheckerState.startedAt) {
        return;
    }
    const elapsed = (Date.now() - quickCheckerState.startedAt) / 1000;
    el.duration.textContent = `Tijd: ${formatDuration(elapsed)}`;
}

function startProgressAnimation() {
    stopProgressAnimation();
    setProgress(3);
    updateDurationLabel();

    quickCheckerState.progressTimer = window.setInterval(() => {
        updateDurationLabel();
        if (!quickCheckerState.running) {
            return;
        }

        const current = quickCheckerState.progressValue;
        if (current >= 92) {
            return;
        }

        const step = current < 45 ? 4 : (current < 70 ? 2.2 : 1.2);
        setProgress(current + step);
    }, 280);
}

function stopProgressAnimation(finalPercent = null) {
    if (quickCheckerState.progressTimer) {
        window.clearInterval(quickCheckerState.progressTimer);
        quickCheckerState.progressTimer = 0;
    }

    if (finalPercent !== null) {
        setProgress(finalPercent);
    }
}

function normaliseerTaakStatus(status) {
    const value = String(status || '').trim().toLowerCase();
    if (value === 'completed' || value === 'failed' || value === 'running' || value === 'queued') {
        return value;
    }
    return 'queued';
}

function stageIndex(stage) {
    const normalized = String(stage || '').trim().toLowerCase();
    const index = LIVE_STAGE_ORDER.indexOf(normalized);
    return index >= 0 ? index : 0;
}

function resetLiveStages() {
    const nodes = el.liveStages ? Array.from(el.liveStages.querySelectorAll('li')) : [];
    nodes.forEach((node) => {
        node.dataset.state = 'idle';
    });
}

function updateLiveStages(stage, status = 'running') {
    const nodes = el.liveStages ? Array.from(el.liveStages.querySelectorAll('li')) : [];
    if (!nodes.length) {
        return;
    }

    const currentIndex = stageIndex(stage);
    const taskStatus = normaliseerTaakStatus(status);

    nodes.forEach((node, index) => {
        let state = 'idle';

        if (taskStatus === 'completed') {
            state = 'completed';
        } else if (taskStatus === 'failed') {
            if (index < currentIndex) {
                state = 'completed';
            } else if (index === currentIndex) {
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

function isPopupContext() {
    const query = new URLSearchParams(window.location.search || '');
    if (query.get('view') === 'popup') {
        return true;
    }

    try {
        return Boolean(window.opener && !window.opener.closed);
    } catch (_error) {
        return false;
    }
}

function updatePopupFlowState() {
    quickCheckerState.popupMode = isPopupContext();
    if (document.body) {
        document.body.classList.toggle('is-popup', quickCheckerState.popupMode);
    }

    if (el.popupBtn) {
        el.popupBtn.disabled = quickCheckerState.popupMode;
        el.popupBtn.textContent = quickCheckerState.popupMode ? 'Popup actief' : 'Open Popup';
    }

    if (el.backToEchoBtn) {
        el.backToEchoBtn.textContent = quickCheckerState.popupMode ? 'Terug naar Echo' : 'Ga naar Echo';
    }
}

function leegContainer(container, emptyText) {
    if (!container) {
        return;
    }
    container.innerHTML = '';

    const emptyNode = document.createElement('p');
    emptyNode.className = 'quick-checker-empty';
    emptyNode.textContent = emptyText;
    container.appendChild(emptyNode);
}

function renderRatings(report) {
    if (!el.ratings) {
        return;
    }

    el.ratings.innerHTML = '';
    const ratings = report && typeof report.ratings === 'object' ? report.ratings : null;
    if (!ratings) {
        leegContainer(el.ratings, 'Nog geen ratingdata.');
        return;
    }

    ['Intern', 'Security', 'Ontwerp', 'Performance'].forEach((name) => {
        const waarde = Number(ratings[name] || 0);

        const card = document.createElement('article');
        card.className = 'quick-checker-rating';

        const nameEl = document.createElement('p');
        nameEl.className = 'quick-checker-rating__name';
        nameEl.textContent = name;
        card.appendChild(nameEl);

        const valueEl = document.createElement('p');
        valueEl.className = 'quick-checker-rating__value';
        valueEl.textContent = Number.isFinite(waarde) && waarde > 0 ? `${waarde.toFixed(1)}/5` : '--';
        card.appendChild(valueEl);

        el.ratings.appendChild(card);
    });
}

function severityText(severity) {
    const raw = String(severity || '').trim().toLowerCase();
    if (raw === 'critical' || raw === 'high' || raw === 'medium' || raw === 'low') {
        return raw;
    }
    return 'low';
}

function severityWeight(severity) {
    const normalized = severityText(severity);
    if (normalized === 'critical') {
        return 4;
    }
    if (normalized === 'high') {
        return 3;
    }
    if (normalized === 'medium') {
        return 2;
    }
    return 1;
}

function urgencyForSeverity(severity, index) {
    const normalized = severityText(severity);
    if (normalized === 'critical') {
        return 'Direct';
    }
    if (normalized === 'high') {
        return index < 2 ? 'Vandaag' : 'Binnen 48h';
    }
    if (normalized === 'medium') {
        return 'Deze week';
    }
    return 'Wanneer mogelijk';
}

function renderAdminContacts(report) {
    if (!el.adminContacts) {
        return;
    }

    el.adminContacts.innerHTML = '';
    const contacts = Array.isArray(report.public_admin_contacts) ? report.public_admin_contacts : [];
    if (!contacts.length) {
        leegContainer(el.adminContacts, 'Geen publiek admin/contact account gevonden.');
        return;
    }

    contacts.forEach((item) => {
        const block = document.createElement('article');
        block.className = 'website-audit-log';

        const email = document.createElement('p');
        email.className = 'website-audit-recommendation__title';
        email.textContent = String(item.email || 'Onbekend account');
        block.appendChild(email);

        const detail = document.createElement('p');
        const pagina = String(item.page || '').trim();
        const reden = String(item.reason || '').trim();
        detail.textContent = `${pagina || '-'}${reden ? ` | ${reden}` : ''}`;
        block.appendChild(detail);

        el.adminContacts.appendChild(block);
    });
}

function renderActionPlan(report) {
    if (!el.actionPlan) {
        return;
    }

    el.actionPlan.innerHTML = '';
    const summary = report && typeof report.ai_summary === 'object' ? report.ai_summary : {};
    const plan = Array.isArray(summary.action_plan) ? summary.action_plan : [];

    if (!plan.length) {
        leegContainer(el.actionPlan, 'Geen AI actieplan beschikbaar.');
        return;
    }

    plan.forEach((item, index) => {
        const card = document.createElement('article');
        card.className = 'website-audit-recommendation';

        const title = document.createElement('p');
        title.className = 'website-audit-recommendation__title';
        title.textContent = `Stap ${index + 1}`;
        card.appendChild(title);

        const detail = document.createElement('p');
        detail.textContent = String(item || '').trim();
        card.appendChild(detail);

        el.actionPlan.appendChild(card);
    });
}

function renderTopPriorities(report) {
    if (!el.topPriorities) {
        return;
    }

    el.topPriorities.innerHTML = '';
    const summary = report && typeof report.ai_summary === 'object' ? report.ai_summary : {};
    const priorities = Array.isArray(summary.top_priorities) ? summary.top_priorities : [];

    if (!priorities.length) {
        leegContainer(el.topPriorities, 'Nog geen top prioriteiten.');
        return;
    }

    const orderedPriorities = [...priorities]
        .sort((left, right) => severityWeight(right.severity) - severityWeight(left.severity))
        .slice(0, 8);

    orderedPriorities.forEach((item, index) => {
        const severity = severityText(item.severity);
        const finding = document.createElement('article');
        finding.className = 'website-audit-finding';
        finding.dataset.severity = severity;

        const rank = document.createElement('p');
        rank.className = 'quick-checker-priority-rank';
        rank.textContent = `P${index + 1} | ${urgencyForSeverity(severity, index)}`;
        finding.appendChild(rank);

        const title = document.createElement('p');
        title.className = 'website-audit-finding__title';
        title.textContent = `${severity.toUpperCase()} | ${String(item.title || 'Prioriteit').trim()}`;
        finding.appendChild(title);

        const detail = document.createElement('p');
        detail.className = 'website-audit-finding__detail';
        detail.textContent = String(item.page || '').trim() || '-';
        finding.appendChild(detail);

        const fix = document.createElement('p');
        fix.className = 'website-audit-finding__recommendation';
        fix.textContent = String(item.fix || '').trim() || 'Geen fix-tekst meegegeven.';
        finding.appendChild(fix);

        el.topPriorities.appendChild(finding);
    });
}

function renderPriorityLegend(report) {
    if (!el.priorityLegend) {
        return;
    }

    el.priorityLegend.innerHTML = '';
    const analytics = report && typeof report.analytics === 'object' ? report.analytics : {};
    const bySeverity = analytics && typeof analytics.by_severity === 'object' ? analytics.by_severity : null;

    if (!bySeverity) {
        leegContainer(el.priorityLegend, 'Nog geen prioriteitenverdeling.');
        return;
    }

    ['critical', 'high', 'medium', 'low'].forEach((severity) => {
        const value = Number(bySeverity[severity] || 0);
        const chip = document.createElement('article');
        chip.className = 'quick-checker-priority-chip';

        const label = document.createElement('p');
        label.className = 'quick-checker-priority-chip__label';
        label.textContent = severity.toUpperCase();
        chip.appendChild(label);

        const amount = document.createElement('p');
        amount.className = 'quick-checker-priority-chip__value';
        amount.textContent = `${Number.isFinite(value) ? value : 0} open`;
        chip.appendChild(amount);

        el.priorityLegend.appendChild(chip);
    });
}

function renderFindings(report) {
    if (!el.findingsList) {
        return;
    }

    el.findingsList.innerHTML = '';
    const findings = Array.isArray(report.findings) ? report.findings : [];

    if (!findings.length) {
        leegContainer(el.findingsList, 'Geen findings ontvangen.');
        return;
    }

    findings.forEach((item) => {
        const severity = severityText(item.severity);
        const card = document.createElement('article');
        card.className = 'website-audit-finding';
        card.dataset.severity = severity;

        const title = document.createElement('p');
        title.className = 'website-audit-finding__title';
        title.textContent = `${severity.toUpperCase()} | ${String(item.category || 'Onbekend').trim().toUpperCase()} | ${String(item.title || '').trim()}`;
        card.appendChild(title);

        const page = document.createElement('p');
        page.className = 'website-audit-finding__detail';
        page.textContent = `Pagina: ${String(item.page || '-').trim()}`;
        card.appendChild(page);

        if (item.evidence) {
            const evidence = document.createElement('p');
            evidence.className = 'website-audit-finding__detail';
            evidence.textContent = `Evidence: ${String(item.evidence || '').trim()}`;
            card.appendChild(evidence);
        }

        if (item.fix) {
            const fix = document.createElement('p');
            fix.className = 'website-audit-finding__recommendation';
            fix.textContent = `Fix: ${String(item.fix || '').trim()}`;
            card.appendChild(fix);
        }

        el.findingsList.appendChild(card);
    });
}

function renderMetrics(report) {
    const overall = Number(report.overall_rating || 0);
    const industry = report && typeof report.industry_snapshot === 'object' ? report.industry_snapshot : {};
    const analytics = report && typeof report.analytics === 'object' ? report.analytics : {};

    if (el.overallScore) {
        el.overallScore.textContent = Number.isFinite(overall) && overall > 0 ? `${overall.toFixed(1)}/5` : '--';
    }
    if (el.grade) {
        el.grade.textContent = String(industry.overall_grade || '--');
    }
    if (el.risk) {
        const risk = Number(industry.risk_score || 0);
        const level = String(industry.risk_level || '').trim();
        el.risk.textContent = level ? `${risk}/100 (${level})` : `${risk}/100`;
    }
    if (el.findingsCount) {
        const total = Number(analytics.total_findings || 0);
        el.findingsCount.textContent = Number.isFinite(total) ? String(total) : '--';
    }
}

function setThreatFromReport(report) {
    const body = document.body;
    if (!body) {
        return;
    }

    const industry = report && typeof report.industry_snapshot === 'object' ? report.industry_snapshot : {};
    const risk = Number(industry.risk_score || 0);

    if (risk >= 80) {
        body.dataset.threat = 'critical';
    } else if (risk >= 55) {
        body.dataset.threat = 'elevated';
    } else if (risk >= 30) {
        body.dataset.threat = 'watch';
    } else {
        body.dataset.threat = 'nominal';
    }
}

function renderReport(payload) {
    if (!payload || typeof payload !== 'object') {
        return;
    }

    const report = payload.report && typeof payload.report === 'object' ? payload.report : {};
    quickCheckerState.lastPayload = payload;

    renderMetrics(report);
    renderRatings(report);
    renderAdminContacts(report);
    renderActionPlan(report);
    renderTopPriorities(report);
    renderPriorityLegend(report);
    renderFindings(report);
    setThreatFromReport(report);

    if (el.clientMessage) {
        const content = String(payload.client_message || '').trim();
        el.clientMessage.value = content || 'Geen klantbericht meegeleverd.';
    }

    if (el.textReport) {
        const textReport = String(payload.text_report || '').trim();
        el.textReport.textContent = textReport || 'Geen tekstuele rapportweergave meegeleverd.';
    }
}

function setControlsDisabled(disabled) {
    if (el.startBtn) {
        el.startBtn.disabled = disabled;
        el.startBtn.textContent = disabled ? 'Scannen...' : 'Start Scan';
    }
    if (el.urlInput) {
        el.urlInput.disabled = disabled;
    }
    if (el.modeQuickBtn) {
        el.modeQuickBtn.disabled = disabled;
    }
    if (el.modeHardBtn) {
        el.modeHardBtn.disabled = disabled;
    }
}

function bestandsnaamBasis(report) {
    const target = String(report.target || 'website').replace(/^https?:\/\//i, '');
    const host = target.split('/')[0].replace(/[^a-z0-9._-]/gi, '_') || 'website';
    const scanType = String(report.scan_type || quickCheckerState.mode || 'quick').toLowerCase();
    return `${host}_${scanType}_quick_checker`;
}

function downloadTekstBestand(fileName, content, mimeType = 'text/plain;charset=utf-8') {
    const tekst = String(content || '').trim();
    if (!tekst) {
        setStatus('Geen exportdata gevonden.', 'error');
        return false;
    }

    try {
        const blob = new Blob([tekst], { type: mimeType });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = fileName;
        document.body.appendChild(link);
        link.click();
        link.remove();
        URL.revokeObjectURL(url);
        return true;
    } catch (_error) {
        setStatus('Export downloaden is mislukt.', 'error');
        return false;
    }
}

function downloadJsonReport() {
    const payload = quickCheckerState.lastPayload;
    const report = payload && payload.report && typeof payload.report === 'object' ? payload.report : null;
    if (!report) {
        setStatus('Geen scanresultaat om op te slaan.', 'error');
        return;
    }

    try {
        const exported = downloadTekstBestand(
            `${bestandsnaamBasis(report)}.json`,
            JSON.stringify(report, null, 2),
            'application/json;charset=utf-8'
        );
        if (!exported) {
            return;
        }
        setStatus('JSON rapport gedownload.', 'success');
    } catch (_error) {
        setStatus('JSON rapport downloaden is mislukt.', 'error');
    }
}

function downloadTextReport() {
    const payload = quickCheckerState.lastPayload;
    const report = payload && payload.report && typeof payload.report === 'object' ? payload.report : null;
    if (!report) {
        setStatus('Geen scanresultaat om te exporteren.', 'error');
        return;
    }

    const textReport = String(payload.text_report || '').trim();
    if (!textReport) {
        setStatus('Geen tekstrapport beschikbaar.', 'error');
        return;
    }

    const exported = downloadTekstBestand(`${bestandsnaamBasis(report)}.txt`, textReport);
    if (exported) {
        setStatus('Tekstrapport gedownload.', 'success');
    }
}

function downloadClientBrief() {
    const payload = quickCheckerState.lastPayload;
    const report = payload && payload.report && typeof payload.report === 'object' ? payload.report : null;
    if (!report) {
        setStatus('Geen scanresultaat om te exporteren.', 'error');
        return;
    }

    const bericht = String(payload.client_message || '').trim();
    if (!bericht) {
        setStatus('Geen klantbericht beschikbaar.', 'error');
        return;
    }

    const exported = downloadTekstBestand(`${bestandsnaamBasis(report)}_client.txt`, bericht);
    if (exported) {
        setStatus('Client brief gedownload.', 'success');
    }
}

function buildPriorityDigest(report) {
    const target = String(report.target || '-').trim() || '-';
    const summary = report && typeof report.ai_summary === 'object' ? report.ai_summary : {};
    const priorities = Array.isArray(summary.top_priorities) ? summary.top_priorities : [];
    const actionPlan = Array.isArray(summary.action_plan) ? summary.action_plan : [];

    const lines = [
        'Quick Checker Prioriteitenoverzicht',
        `Target: ${target}`,
        '',
        'Top Prioriteiten:',
    ];

    if (!priorities.length) {
        lines.push('- Geen prioriteiten gevonden.');
    } else {
        priorities.slice(0, 8).forEach((item, index) => {
            const severity = severityText(item.severity).toUpperCase();
            const title = String(item.title || 'Prioriteit').trim();
            const page = String(item.page || '-').trim() || '-';
            lines.push(`${index + 1}. [${severity}] ${title} (${page})`);
        });
    }

    lines.push('', 'Actieplan:');
    if (!actionPlan.length) {
        lines.push('- Geen actieplan gevonden.');
    } else {
        actionPlan.forEach((item, index) => {
            lines.push(`${index + 1}. ${String(item || '').trim()}`);
        });
    }

    return lines.join('\n').trim();
}

async function copyPriorityDigest() {
    const payload = quickCheckerState.lastPayload;
    const report = payload && payload.report && typeof payload.report === 'object' ? payload.report : null;
    if (!report) {
        setStatus('Geen prioriteiten om te kopieren.', 'error');
        return;
    }

    const digest = buildPriorityDigest(report);
    if (!digest) {
        setStatus('Geen prioriteiten om te kopieren.', 'error');
        return;
    }

    try {
        if (navigator.clipboard && navigator.clipboard.writeText) {
            await navigator.clipboard.writeText(digest);
        } else {
            throw new Error('clipboard unavailable');
        }
        setStatus('Prioriteitenoverzicht gekopieerd.', 'success');
    } catch (_error) {
        setStatus('Kopieren van prioriteitenoverzicht is mislukt.', 'error');
    }
}

async function copyClientMessage() {
    if (!el.clientMessage) {
        return;
    }

    const text = String(el.clientMessage.value || '').trim();
    if (!text) {
        setStatus('Geen klantbericht om te kopieren.', 'error');
        return;
    }

    try {
        if (navigator.clipboard && navigator.clipboard.writeText) {
            await navigator.clipboard.writeText(text);
        } else {
            el.clientMessage.focus();
            el.clientMessage.select();
            document.execCommand('copy');
        }
        setStatus('Klantbericht gekopieerd naar klembord.', 'success');
    } catch (_error) {
        setStatus('Kopieren naar klembord is mislukt.', 'error');
    }
}

function wacht(ms) {
    return new Promise((resolve) => {
        window.setTimeout(resolve, Math.max(0, Number(ms || 0)));
    });
}

async function leesResponseJson(response) {
    try {
        const payload = await response.json();
        return payload && typeof payload === 'object' ? payload : {};
    } catch (_error) {
        return {};
    }
}

function applyTaskSnapshot(task) {
    if (!task || typeof task !== 'object') {
        return;
    }

    const status = normaliseerTaakStatus(task.status);
    const stage = String(task.stage || 'queued').trim().toLowerCase() || 'queued';
    const tone = status === 'failed' ? 'error' : (status === 'completed' ? 'success' : 'running');

    if (Number.isFinite(Number(task.progress_percent))) {
        setProgress(Number(task.progress_percent));
    }

    updateLiveStages(stage, status);

    const message = String(task.message || '').trim();
    if (message) {
        setStatus(message, tone);
    }

    const durationMs = Number(task.duration_ms || 0);
    if (durationMs > 0 && el.duration) {
        el.duration.textContent = `Tijd: ${formatDuration(durationMs / 1000)}`;
    }
}

async function fetchTaskStatus(taskId) {
    const response = await fetch(`/api/quick-check/status/${encodeURIComponent(taskId)}`, {
        cache: 'no-store',
    });

    const payload = await leesResponseJson(response);
    if (!response.ok || payload.status !== 'success') {
        const message = String(payload.message || 'Scanstatus ophalen is mislukt.');
        throw new Error(message);
    }

    return payload.task && typeof payload.task === 'object' ? payload.task : {};
}

async function wachtOpTaakAfronding(taskId) {
    const maxPolls = 260;

    for (let attempt = 0; attempt < maxPolls; attempt += 1) {
        if (!quickCheckerState.running || quickCheckerState.activeTaskId !== taskId) {
            return null;
        }

        await wacht(850);
        const task = await fetchTaskStatus(taskId);
        applyTaskSnapshot(task);

        const status = normaliseerTaakStatus(task.status);
        if (status === 'completed' || status === 'failed') {
            return task;
        }
    }

    throw new Error('Scanstatus timeout: geen afronding ontvangen.');
}

async function runLegacyScan(url) {
    updateLiveStages('scan_running', 'running');

    const response = await fetch('/api/quick-check/run', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            url,
            mode: quickCheckerState.mode,
        }),
    });

    const payload = await leesResponseJson(response);
    if (!response.ok || payload.status !== 'success') {
        const message = String(payload.message || 'Quick checker scan mislukt.');
        throw new Error(message);
    }

    updateLiveStages('completed', 'completed');
    return payload;
}

async function startScan(event) {
    event.preventDefault();
    if (quickCheckerState.running) {
        return;
    }

    const url = String(el.urlInput ? el.urlInput.value : '').trim();
    if (!url) {
        setStatus('Vul eerst een geldige URL in.', 'error');
        return;
    }

    quickCheckerState.running = true;
    quickCheckerState.startedAt = Date.now();
    quickCheckerState.activeTaskId = '';
    setControlsDisabled(true);
    resetLiveStages();
    updateLiveStages('queued', 'running');
    setStatus(`Scan gestart (${quickCheckerState.mode}).`, 'running');
    startProgressAnimation();

    try {
        const startResponse = await fetch('/api/quick-check/start', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                url,
                mode: quickCheckerState.mode,
            }),
        });

        if (startResponse.status === 404) {
            const legacyPayload = await runLegacyScan(url);
            renderReport(legacyPayload);
            stopProgressAnimation(100);

            const report = legacyPayload.report && typeof legacyPayload.report === 'object' ? legacyPayload.report : {};
            const target = String(report.target || url).trim();
            setStatus(`Scan afgerond voor ${target}.`, 'success');
            return;
        }

        const startPayload = await leesResponseJson(startResponse);
        if (!startResponse.ok || startPayload.status !== 'success') {
            const message = String(startPayload.message || 'Quick checker scan kon niet starten.');
            throw new Error(message);
        }

        const firstTask = startPayload.task && typeof startPayload.task === 'object' ? startPayload.task : {};
        applyTaskSnapshot(firstTask);

        const firstStatus = normaliseerTaakStatus(firstTask.status);
        if (firstStatus === 'completed') {
            if (firstTask.result && typeof firstTask.result === 'object') {
                renderReport(firstTask.result);
            }
            stopProgressAnimation(100);
            return;
        }

        if (firstStatus === 'failed') {
            const startError = String(firstTask.error || firstTask.message || 'Quick checker scan mislukt.').trim();
            throw new Error(startError || 'Quick checker scan mislukt.');
        }

        const taskId = String(firstTask.id || '').trim();
        if (!taskId) {
            throw new Error('Geen taak-id ontvangen voor live scanstatus.');
        }

        quickCheckerState.activeTaskId = taskId;
        const finalTask = await wachtOpTaakAfronding(taskId);
        if (!finalTask) {
            return;
        }

        const finalStatus = normaliseerTaakStatus(finalTask.status);
        if (finalStatus === 'completed') {
            if (finalTask.result && typeof finalTask.result === 'object') {
                renderReport(finalTask.result);
            }
            stopProgressAnimation(100);

            const taskResult = finalTask.result && typeof finalTask.result === 'object' ? finalTask.result : {};
            const report = taskResult.report && typeof taskResult.report === 'object' ? taskResult.report : {};
            const target = String(report.target || url).trim();
            setStatus(`Scan afgerond voor ${target}.`, 'success');
            return;
        }

        const finalError = String(finalTask.error || finalTask.message || 'Quick checker scan mislukt.').trim();
        throw new Error(finalError || 'Quick checker scan mislukt.');
    } catch (error) {
        stopProgressAnimation(0);
        updateLiveStages('scan_running', 'failed');
        setStatus(String(error && error.message ? error.message : 'Onbekende fout tijdens scan.'), 'error');
    } finally {
        quickCheckerState.running = false;
        quickCheckerState.activeTaskId = '';
        setControlsDisabled(false);
        updateDurationLabel();
    }
}

function openAsPopup() {
    if (quickCheckerState.popupMode) {
        setStatus('Deze quick checker draait al als popup.', 'idle');
        return;
    }

    const popup = window.open('/quick-checker?view=popup', 'echoQuickChecker', 'popup=yes,width=1440,height=920,resizable=yes,scrollbars=yes');
    if (popup) {
        popup.focus();
        setStatus('Popup geopend. Gebruik daar de scan voor focusmodus.', 'success');
        return;
    }

    setStatus('Popup geblokkeerd door de browser-instellingen.', 'error');
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

function bindEvents() {
    if (el.modeQuickBtn) {
        el.modeQuickBtn.addEventListener('click', () => setMode('quick'));
    }
    if (el.modeHardBtn) {
        el.modeHardBtn.addEventListener('click', () => setMode('hard'));
    }
    if (el.form) {
        el.form.addEventListener('submit', startScan);
    }
    if (el.downloadJsonBtn) {
        el.downloadJsonBtn.addEventListener('click', downloadJsonReport);
    }
    if (el.downloadTxtBtn) {
        el.downloadTxtBtn.addEventListener('click', downloadTextReport);
    }
    if (el.downloadBriefBtn) {
        el.downloadBriefBtn.addEventListener('click', downloadClientBrief);
    }
    if (el.copyPrioritiesBtn) {
        el.copyPrioritiesBtn.addEventListener('click', () => {
            void copyPriorityDigest();
        });
    }
    if (el.copyClientBtn) {
        el.copyClientBtn.addEventListener('click', copyClientMessage);
    }
    if (el.popupBtn) {
        el.popupBtn.addEventListener('click', openAsPopup);
    }
    if (el.backToEchoBtn) {
        el.backToEchoBtn.addEventListener('click', backToEcho);
    }
}

function init() {
    updatePopupFlowState();
    setMode('quick');
    setStatus('Stand-by. Vul een URL in en start de scan.', 'idle');
    setProgress(0);
    resetLiveStages();
    updateLiveStages('queued', 'queued');

    if (el.duration) {
        el.duration.textContent = 'Tijd: --';
    }

    if (el.clientMessage) {
        el.clientMessage.value = 'Nog geen klantbericht. Start eerst een scan.';
    }

    if (el.textReport) {
        el.textReport.textContent = 'Nog geen rapport.';
    }

    leegContainer(el.ratings, 'Nog geen ratingdata.');
    leegContainer(el.adminContacts, 'Nog geen contactpunten gevonden.');
    leegContainer(el.actionPlan, 'Nog geen actieplan.');
    leegContainer(el.priorityLegend, 'Nog geen prioriteitenverdeling.');
    leegContainer(el.topPriorities, 'Nog geen prioriteiten.');
    leegContainer(el.findingsList, 'Nog geen bevindingen.');

    bindEvents();
}

init();

window.addEventListener('beforeunload', () => {
    quickCheckerState.running = false;
    quickCheckerState.activeTaskId = '';
    stopProgressAnimation();
});
