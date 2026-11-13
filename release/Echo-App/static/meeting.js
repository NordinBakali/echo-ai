(() => {
    'use strict';
    const $ = id => document.getElementById(`meeting-${id}`);
    const nl = document.body.dataset.language === 'nl';
    const text = (en, dutch) => nl ? dutch : en;
    const token = document.querySelector('meta[name="echo-meeting-token"]').content;
    let state = null, busy = false, tick = null, base = 0, baseAt = 0;

    const clock = seconds => {
        const s = Math.max(0, Math.floor(seconds));
        return [Math.floor(s / 3600), Math.floor(s % 3600 / 60), s % 60].map(v => String(v).padStart(2, '0')).join(':');
    };
    const statusLabel = {
        recording: text('Recording…', 'Bezig met opnemen…'),
        recorded: text('Recorded — not transcribed yet', 'Opgenomen — nog niet uitgeschreven'),
        transcribing: text('Transcribing…', 'Bezig met uitschrijven…'),
        summarizing: text('Summarising with local AI…', 'Bezig met samenvatten (lokale AI)…'),
        transcribed: text('Transcript ready', 'Transcriptie klaar'),
        error: text('Error', 'Fout'),
    };

    async function api(action, data) {
        const response = await fetch(`/api/vergadering/${action}`, {
            method: data === undefined ? 'GET' : 'POST',
            headers: { 'Content-Type': 'application/json', 'X-Echo-Meeting-Token': token },
            body: data === undefined ? undefined : JSON.stringify(data),
            cache: 'no-store',
        });
        const result = await response.json();
        if (!response.ok || result.status !== 'success') throw new Error(result.message || `HTTP ${response.status}`);
        state = result.meeting;
        render();
        return result;
    }

    async function run(action, data) {
        if (busy) return;
        busy = true;
        $('error').textContent = '';
        updateButtons();
        try { await api(action, data); } catch (error) { $('error').textContent = error.message; }
        busy = false;
        updateButtons();
    }

    function updateButtons() {
        const rec = state && state.recording;
        $('start').disabled = busy || !state || !state.available || !!rec || !$('consent').checked;
        $('stop').disabled = busy || !rec;
        $('mic').disabled = $('title').disabled = !!rec;
        $('auto-save').disabled = busy || !state || ($('auto-enabled').checked && !$('auto-consent').checked);
    }

    const summaryModel = () => $('model').value;
    const busyStatus = status => status === 'recording' || status === 'transcribing' || status === 'summarizing';

    async function loadModels() {
        const select = $('model');
        let models = [], message = '';
        try {
            const response = await fetch('/api/vergadering/models', { cache: 'no-store' });
            const result = await response.json();
            models = Array.isArray(result.models) ? result.models : [];
            message = result.message || '';
        } catch (error) { message = error.message; }
        const wanted = select.dataset.wanted || select.value;
        select.replaceChildren();
        const none = document.createElement('option');
        none.value = '';
        none.textContent = models.length ? text('— no summary —', '— geen samenvatting —')
            : text('No local model found', 'Geen lokaal model gevonden');
        select.append(none);
        for (const name of models) {
            const option = document.createElement('option');
            option.value = option.textContent = name;
            select.append(option);
        }
        select.value = models.includes(wanted) ? wanted : (models[0] || '');
        if (!models.length) {
            $('model-help').textContent = (message ? message + ' ' : '') + text(
                'Start Ollama and install a model, e.g. in a terminal: ollama pull llama3.1 — then reload this page.',
                'Start Ollama en installeer een model, bijv. in een terminal: ollama pull llama3.1 — en vernieuw daarna deze pagina.');
        }
        render();
    }

    function button(label, onClick, primary) {
        const el = document.createElement('button');
        el.type = 'button';
        el.className = primary ? 'primary-button' : 'secondary-button';
        el.textContent = label;
        el.addEventListener('click', onClick);
        return el;
    }

    function link(label, href) {
        const el = document.createElement('a');
        el.className = 'secondary-button';
        el.href = href;
        el.textContent = label;
        return el;
    }

    async function preview(id, kind = 'txt') {
        const box = $('preview');
        try {
            const response = await fetch(`/api/vergadering/transcript/${encodeURIComponent(id)}.${kind}`, { cache: 'no-store' });
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            box.textContent = await response.text();
            box.hidden = false;
            box.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        } catch (error) { $('error').textContent = error.message; }
    }

    function render() {
        if (!state) return;
        const rec = state.recording;
        $('dot').classList.toggle('live', !!rec);
        $('state').textContent = !state.available
            ? text('Windows loopback audio is unavailable on this PC.', 'Windows-loopbackaudio is niet beschikbaar op deze pc.')
            : rec ? text('Recording', 'Opname loopt') : text('Not recording', 'Geen opname');
        if (rec) {
            base = rec.elapsed; baseAt = performance.now();
            $('devices').textContent = `${text('Speakers', 'Speakers')}: ${rec.speakers_device || '-'}`
                + (rec.microphone ? ` · ${text('Microphone', 'Microfoon')}: ${rec.microphone_device || '-'}` : '');
            if (!tick) tick = setInterval(() => { $('timer').textContent = clock(base + (performance.now() - baseAt) / 1000); }, 500);
        } else {
            clearInterval(tick); tick = null;
            $('timer').textContent = '00:00:00';
            $('devices').textContent = '';
        }
        document.title = `${rec ? '● ' : ''}${text('Meeting recorder', 'Vergaderopname')} - Echo`;
        renderAuto();

        const list = $('list');
        list.replaceChildren();
        if (!state.meetings.length) {
            const li = document.createElement('li');
            li.textContent = text('No meetings yet.', 'Nog geen vergaderingen.');
            list.append(li);
        }
        for (const m of state.meetings) {
            const li = document.createElement('li');
            const title = document.createElement('strong');
            title.textContent = m.title;
            const info = document.createElement('div');
            info.className = 'field-help';
            info.textContent = `${new Date(m.started_at).toLocaleString()} · ${clock(m.duration)} · `
                + `${m.microphone ? text('speakers + mic', 'speakers + microfoon') : text('speakers only', 'alleen speakers')} · `
                + (statusLabel[m.status] || m.status) + (m.error ? `: ${m.error}` : '')
                + (m.summary_error && m.status !== 'summarizing' ? ` · ${text('Summary failed', 'Samenvatting mislukt')}: ${m.summary_error}` : '')
                + (m.has_summary && m.status !== 'summarizing' ? ` · ${m.action_items ?? 0} ${text('action items', 'actiepunten')}` : '');
            li.append(title, info);
            if (m.status === 'transcribing' || m.status === 'summarizing') {
                const bar = document.createElement('progress');
                bar.max = 100; bar.value = m.progress || 0;
                li.append(bar);
            }
            const row = document.createElement('div');
            row.className = 'button-row';
            if (!busyStatus(m.status)) {
                row.append(button(m.has_transcript ? text('Transcribe again', 'Opnieuw uitschrijven') : text('Transcribe', 'Uitschrijven'),
                    () => run('transcribe', {
                        id: m.id, language: $('language').value, separate: $('separate').checked,
                        summary_model: $('autosummary').checked ? summaryModel() : '',
                    }), !m.has_transcript));
            }
            if (m.has_transcript && !busyStatus(m.status) && summaryModel()) {
                row.append(button(m.has_summary ? text('Summarise again', 'Opnieuw samenvatten') : text('Summarise', 'Samenvatten'),
                    () => run('summarize', { id: m.id, model: summaryModel() }), !m.has_summary));
            }
            if (m.has_summary) {
                row.append(button(text('Show summary', 'Samenvatting tonen'), () => preview(m.id, 'md')));
                row.append(link('.md', `/api/vergadering/transcript/${encodeURIComponent(m.id)}.md?download=1`));
            }
            if (m.has_transcript) {
                row.append(button(text('Show transcript', 'Transcriptie tonen'), () => preview(m.id)));
                row.append(link('.txt', `/api/vergadering/transcript/${encodeURIComponent(m.id)}.txt?download=1`));
                row.append(link(text('.srt subtitles', '.srt-ondertitels'), `/api/vergadering/transcript/${encodeURIComponent(m.id)}.srt?download=1`));
            }
            if (!busyStatus(m.status)) {
                row.append(button(text('Delete', 'Verwijderen'), () => {
                    if (confirm(text('Delete this recording and transcript?', 'Deze opname en transcriptie verwijderen?'))) run('delete', { id: m.id });
                }));
            }
            li.append(row);
            list.append(li);
        }
        updateButtons();
    }

    let autoLoaded = false;
    function renderAuto() {
        const auto = state.auto;
        if (!auto) return;
        if (!autoLoaded) {
            autoLoaded = true;
            $('auto-enabled').checked = auto.enabled;
            $('auto-consent').checked = auto.enabled;
            if (auto.enabled) {
                $('mic').checked = auto.microphone;
                $('language').value = auto.language;
                $('separate').checked = auto.separate;
                $('model').dataset.wanted = auto.model;
                if ([...$('model').options].some(o => o.value === auto.model)) $('model').value = auto.model;
            }
        }
        const live = auto.enabled && auto.call_apps.length > 0;
        const pending = live && !auto.auto_meeting && auto.starts_in !== null && !auto.skipped;
        $('auto-dot').classList.toggle('live', live && !!auto.auto_meeting);
        $('auto-skip').hidden = !(live && !auto.auto_meeting && !auto.skipped);
        $('auto-state').textContent = !auto.supported ? text('Call detection only works on Windows.', 'Calldetectie werkt alleen op Windows.')
            : auto.error ? `${text('Problem', 'Probleem')}: ${auto.error}`
            : !auto.enabled ? text('Off', 'Uit')
            : auto.auto_meeting ? text(`In a ${auto.call_apps.join(', ')} call — recording`, `In een ${auto.call_apps.join(', ')}-call — opname loopt`)
            : live && auto.skipped ? text(`${auto.call_apps.join(', ')} call — not recorded`, `${auto.call_apps.join(', ')}-call — wordt niet opgenomen`)
            : pending ? text(`Announce the recording now: “My AI assistant is listening in to take the minutes.” Recording starts in ${auto.starts_in} s — nothing is recorded yet.`,
                `Kondig de opname nu aan: “Mijn AI-assistent luistert mee om de notulen te maken.” Opname start over ${auto.starts_in} s — er wordt nog niets opgenomen.`)
            : live ? text(`${auto.call_apps.join(', ')} call detected — you will be asked to announce the recording first…`, `${auto.call_apps.join(', ')}-call gedetecteerd — je krijgt eerst een seintje om de opname aan te kondigen…`)
            : text('On — waiting for a call', 'Aan — wacht op een call');
    }

    $('form').addEventListener('submit', event => {
        event.preventDefault();
        run('start', { authorized: $('consent').checked, microphone: $('mic').checked, title: $('title').value.trim() });
    });
    $('stop').addEventListener('click', () => run('stop', {}));
    $('auto-skip').addEventListener('click', () => run('skip', {}));
    $('consent').addEventListener('change', updateButtons);
    $('auto-enabled').addEventListener('change', updateButtons);
    $('auto-consent').addEventListener('change', updateButtons);
    $('model').addEventListener('change', render);
    $('auto-form').addEventListener('submit', event => {
        event.preventDefault();
        run('auto', {
            authorized: $('auto-consent').checked, enabled: $('auto-enabled').checked,
            microphone: $('mic').checked, language: $('language').value,
            separate: $('separate').checked && $('mic').checked,
            model: $('autosummary').checked ? summaryModel() : '',
        });
    });
    $('mic').addEventListener('change', () => { if (!$('mic').checked) $('separate').checked = false; });

    const refresh = () => api('status').catch(error => { $('error').textContent = error.message; });
    refresh().then(loadModels);
    setInterval(() => { if (!busy) refresh(); }, 3000);
})();
