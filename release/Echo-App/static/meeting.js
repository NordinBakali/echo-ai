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

    async function preview(id) {
        const box = $('preview');
        try {
            const response = await fetch(`/api/vergadering/transcript/${encodeURIComponent(id)}.txt`, { cache: 'no-store' });
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
                + (statusLabel[m.status] || m.status) + (m.error ? `: ${m.error}` : '');
            li.append(title, info);
            if (m.status === 'transcribing') {
                const bar = document.createElement('progress');
                bar.max = 100; bar.value = m.progress || 0;
                li.append(bar);
            }
            const row = document.createElement('div');
            row.className = 'button-row';
            if (m.status !== 'recording' && m.status !== 'transcribing') {
                row.append(button(m.has_transcript ? text('Transcribe again', 'Opnieuw uitschrijven') : text('Transcribe', 'Uitschrijven'),
                    () => run('transcribe', { id: m.id, language: $('language').value, separate: $('separate').checked }), !m.has_transcript));
            }
            if (m.has_transcript) {
                row.append(button(text('Show', 'Tonen'), () => preview(m.id)));
                row.append(link('.txt', `/api/vergadering/transcript/${encodeURIComponent(m.id)}.txt?download=1`));
                row.append(link(text('.srt subtitles', '.srt-ondertitels'), `/api/vergadering/transcript/${encodeURIComponent(m.id)}.srt?download=1`));
            }
            if (m.status !== 'recording' && m.status !== 'transcribing') {
                row.append(button(text('Delete', 'Verwijderen'), () => {
                    if (confirm(text('Delete this recording and transcript?', 'Deze opname en transcriptie verwijderen?'))) run('delete', { id: m.id });
                }));
            }
            li.append(row);
            list.append(li);
        }
        updateButtons();
    }

    $('form').addEventListener('submit', event => {
        event.preventDefault();
        run('start', { authorized: $('consent').checked, microphone: $('mic').checked, title: $('title').value.trim() });
    });
    $('stop').addEventListener('click', () => run('stop', {}));
    $('consent').addEventListener('change', updateButtons);
    $('mic').addEventListener('change', () => { if (!$('mic').checked) $('separate').checked = false; });

    const refresh = () => api('status').catch(error => { $('error').textContent = error.message; });
    refresh();
    setInterval(() => { if (!busy) refresh(); }, 3000);
})();
