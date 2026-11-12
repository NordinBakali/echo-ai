'use strict';

(() => {
    const root = document.querySelector('.workspace-shell');
    const apiRoot = root.dataset.api;
    const dutch = document.body.dataset.language === 'nl';
    const messages = {
        network: ['Could not reach Echo. Check your connection.', 'Echo is niet bereikbaar. Controleer je verbinding.'],
        invalid: ['Echo returned an invalid response.', 'Echo gaf een ongeldig antwoord.'],
        working: ['Processing. Long documents may take several minutes…', 'Bezig met verwerken. Lange documenten kunnen enkele minuten duren…'],
        done: ['Ready.', 'Klaar.'],
        loading: ['Loading your reading list…', 'Je leeslijst wordt geladen…'],
        added: ['Article added to your reading list.', 'Artikel aan je leeslijst toegevoegd.'],
        updated: ['Reading list updated.', 'Leeslijst bijgewerkt.'],
        noItems: ['Your reading list is empty.', 'Je leeslijst is nog leeg.'],
        noMatches: ['No articles match this filter.', 'Geen artikelen gevonden met dit filter.'],
        read: ['Read', 'Gelezen'],
        unread: ['Unread', 'Ongelezen'],
        markRead: ['Mark as read', 'Markeer als gelezen'],
        markUnread: ['Mark as unread', 'Markeer als ongelezen'],
        remove: ['Remove', 'Verwijderen'],
        confirmRemove: ['Remove this article from your reading list?', 'Dit artikel uit je leeslijst verwijderen?'],
        copy: ['Copied to the clipboard.', 'Gekopieerd naar het klembord.'],
        copyFailed: ['Copying failed. Select and copy the text manually.', 'Kopiëren is mislukt. Selecteer en kopieer de tekst handmatig.'],
        downloaded: ['Download started.', 'Download gestart.'],
        chooseVoice: ['Choose or record an audio message, or enter a transcript.', 'Kies of neem een spraakbericht op, of vul een transcriptie in.'],
        audioLarge: ['The audio file exceeds 12 MB.', 'Het audiobestand is groter dan 12 MB.'],
        documentLarge: ['The document exceeds 20 MB.', 'Het document is groter dan 20 MB.'],
        transcribing: ['Transcribing the voice message…', 'Spraakbericht wordt uitgeschreven…'],
        recording: ['Recording… Stop the recording before creating the note.', 'Opname loopt… Stop de opname voordat je de notitie maakt.'],
        recordingReady: ['Recording ready. Create a note to transcribe it.', 'Opname is klaar. Maak een notitie om deze uit te schrijven.'],
        changeLanguage: ['Clear the transcript to transcribe the audio again in the selected language.', 'Wis de transcriptie om de audio opnieuw uit te schrijven in de gekozen taal.'],
        recordUnsupported: ['Recording is unavailable in this browser. You can upload an audio file instead.', 'Opnemen is niet beschikbaar in deze browser. Je kunt wel een audiobestand uploaden.'],
        recordFailed: ['Recording failed. Check microphone permissions or upload a file.', 'Opnemen is mislukt. Controleer de microfoonrechten of upload een bestand.'],
        recordEmpty: ['The recording was empty. Try again.', 'De opname was leeg. Probeer opnieuw.'],
        recordLimit: ['The recording exceeded the 12 MB limit.', 'De opname is groter dan de limiet van 12 MB.'],
        recordTimed: ['Recording stopped after 10 minutes. Create a note to transcribe it.', 'Opname na 10 minuten gestopt. Maak een notitie om deze uit te schrijven.'],
    };
    const t = (key) => messages[key][dutch ? 1 : 0];
    const byId = (id) => document.getElementById(id);
    const status = (element, text, kind = '') => {
        element.textContent = text;
        element.dataset.kind = kind;
    };

    async function requestApi(path, options = {}) {
        let response;
        try {
            response = await fetch(apiRoot + path, { cache: 'no-store', ...options });
        } catch (_error) {
            throw new Error(t('network'));
        }
        let data;
        try {
            data = await response.json();
        } catch (_error) {
            throw new Error(t('invalid'));
        }
        if (!response.ok || !data || data.status !== 'success') {
            throw new Error(typeof data?.message === 'string' && data.message ? data.message : t('invalid'));
        }
        return data;
    }

    function showResult(resultId, value) {
        const output = byId(resultId);
        output.value = value;
        updateOutputControls(resultId);
    }

    function updateOutputControls(resultId) {
        const available = Boolean(byId(resultId).value.trim());
        document.querySelectorAll(`[data-copy="${resultId}"], [data-download="${resultId}"]`).forEach((button) => {
            button.disabled = !available;
        });
        if (resultId === 'voice-result') renderNotePreview(byId(resultId).value);
    }

    function renderNotePreview(text) {
        const preview = byId('note-preview');
        const content = byId('note-preview-content');
        preview.hidden = !text.trim();
        content.replaceChildren();
        let list = null;
        text.split(/\r?\n/).forEach((line) => {
            const heading = line.match(/^(#{1,3})\s+(.+)$/);
            const bullet = line.match(/^\s*[-*]\s+(.+)$/);
            if (heading) {
                list = null;
                const element = document.createElement(heading[1].length === 1 ? 'h3' : 'h4');
                element.textContent = heading[2];
                content.append(element);
            } else if (bullet) {
                if (!list) {
                    list = document.createElement('ul');
                    content.append(list);
                }
                const element = document.createElement('li');
                element.textContent = bullet[1];
                list.append(element);
            } else if (line.trim()) {
                list = null;
                const element = document.createElement('p');
                element.textContent = line;
                content.append(element);
            } else {
                list = null;
            }
        });
    }

    function finishStatus(element, warnings) {
        if (Array.isArray(warnings) && warnings.length) {
            status(element, `${t('done')} ${warnings.join(' ')}`, 'warning');
        } else {
            status(element, t('done'));
        }
    }

    const tabs = Array.from(document.querySelectorAll('[role="tab"]'));
    function activateTab(tab, focus = false) {
        tabs.forEach((item) => {
            const active = item === tab;
            item.setAttribute('aria-selected', String(active));
            item.tabIndex = active ? 0 : -1;
            byId(item.getAttribute('aria-controls')).hidden = !active;
        });
        if (focus) {
            tab.focus();
        }
    }
    tabs.forEach((tab, index) => {
        tab.addEventListener('click', () => activateTab(tab));
        tab.addEventListener('keydown', (event) => {
            let next = index;
            if (event.key === 'ArrowRight' || event.key === 'ArrowDown') next = (index + 1) % tabs.length;
            else if (event.key === 'ArrowLeft' || event.key === 'ArrowUp') next = (index - 1 + tabs.length) % tabs.length;
            else if (event.key === 'Home') next = 0;
            else if (event.key === 'End') next = tabs.length - 1;
            else return;
            event.preventDefault();
            activateTab(tabs[next], true);
        });
    });

    document.querySelectorAll('.result').forEach((output) => {
        output.addEventListener('input', () => updateOutputControls(output.id));
    });
    document.querySelectorAll('[data-copy]').forEach((button) => {
        button.addEventListener('click', async () => {
            const panelStatus = button.closest('.workspace-panel').querySelector('.status');
            try {
                if (!navigator.clipboard || !navigator.clipboard.writeText) {
                    throw new Error(t('copyFailed'));
                }
                await navigator.clipboard.writeText(byId(button.dataset.copy).value);
                status(panelStatus, t('copy'));
            } catch (_error) {
                status(panelStatus, t('copyFailed'), 'error');
            }
        });
    });
    document.querySelectorAll('[data-download]').forEach((button) => {
        button.addEventListener('click', () => {
            const text = byId(button.dataset.download).value;
            const blob = new Blob([text], { type: 'text/plain;charset=utf-8' });
            const url = URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.download = button.dataset.filename;
            document.body.append(link);
            link.click();
            link.remove();
            window.setTimeout(() => URL.revokeObjectURL(url), 1000);
            status(button.closest('.workspace-panel').querySelector('.status'), t('downloaded'));
        });
    });

    const voiceForm = byId('voice-form');
    const voiceFileInput = byId('voice-file');
    const voiceTranscript = byId('voice-transcript');
    const voiceStatus = byId('voice-status');
    const voicePreview = byId('voice-preview');
    const recordStart = byId('record-start');
    const recordStop = byId('record-stop');
    let selectedAudio = null;
    let previewUrl = '';
    let recorder = null;
    let recordStream = null;
    let recordTimer = null;

    function setAudio(file) {
        selectedAudio = file;
        voiceTranscript.value = '';
        if (previewUrl) URL.revokeObjectURL(previewUrl);
        previewUrl = file ? URL.createObjectURL(file) : '';
        voicePreview.hidden = !file;
        if (file) voicePreview.src = previewUrl;
        else voicePreview.removeAttribute('src');
    }

    function releaseMicrophone() {
        if (recordTimer) window.clearTimeout(recordTimer);
        recordTimer = null;
        if (recordStream) recordStream.getTracks().forEach((track) => track.stop());
        recordStream = null;
        recorder = null;
        recordStart.disabled = false;
        recordStop.disabled = true;
        voiceFileInput.disabled = false;
    }

    voiceFileInput.addEventListener('change', () => {
        const file = voiceFileInput.files[0] || null;
        setAudio(file);
        status(voiceStatus, file && file.size > 12 * 1024 * 1024 ? t('audioLarge') : '', file && file.size > 12 * 1024 * 1024 ? 'error' : '');
    });
    byId('voice-language').addEventListener('change', () => {
        if (selectedAudio && voiceTranscript.value.trim()) status(voiceStatus, t('changeLanguage'), 'warning');
    });

    recordStart.addEventListener('click', async () => {
        if (!navigator.mediaDevices?.getUserMedia || typeof MediaRecorder === 'undefined') {
            status(voiceStatus, t('recordUnsupported'), 'error');
            return;
        }
        recordStart.disabled = true;
        let failed = false;
        let exceeded = false;
        let timedOut = false;
        let bytes = 0;
        const chunks = [];
        try {
            recordStream = await navigator.mediaDevices.getUserMedia({ audio: true });
            const preferred = ['audio/webm;codecs=opus', 'audio/ogg;codecs=opus', 'audio/mp4']
                .find((type) => MediaRecorder.isTypeSupported(type));
            recorder = preferred ? new MediaRecorder(recordStream, { mimeType: preferred }) : new MediaRecorder(recordStream);
            const activeRecorder = recorder;
            activeRecorder.addEventListener('dataavailable', (event) => {
                if (event.data.size) {
                    bytes += event.data.size;
                    if (bytes <= 12 * 1024 * 1024) chunks.push(event.data);
                    else {
                        exceeded = true;
                        if (activeRecorder.state !== 'inactive') activeRecorder.stop();
                    }
                }
            });
            activeRecorder.addEventListener('error', () => {
                failed = true;
                status(voiceStatus, t('recordFailed'), 'error');
                if (activeRecorder.state !== 'inactive') activeRecorder.stop();
                else releaseMicrophone();
            });
            activeRecorder.addEventListener('stop', () => {
                const mime = activeRecorder.mimeType || 'audio/webm';
                releaseMicrophone();
                if (failed) return;
                if (exceeded) {
                    status(voiceStatus, t('recordLimit'), 'error');
                    return;
                }
                if (!chunks.length) {
                    status(voiceStatus, t('recordEmpty'), 'error');
                    return;
                }
                const extension = mime.includes('ogg') ? 'ogg' : (mime.includes('mp4') ? 'm4a' : 'webm');
                const file = new File(chunks, `echo-opname.${extension}`, { type: mime });
                voiceFileInput.value = '';
                setAudio(file);
                status(voiceStatus, timedOut ? t('recordTimed') : t('recordingReady'));
            });
            activeRecorder.start(1000);
            recordStop.disabled = false;
            voiceFileInput.disabled = true;
            status(voiceStatus, t('recording'));
            recordTimer = window.setTimeout(() => {
                timedOut = true;
                if (activeRecorder.state !== 'inactive') activeRecorder.stop();
            }, 10 * 60 * 1000);
        } catch (_error) {
            releaseMicrophone();
            status(voiceStatus, t('recordFailed'), 'error');
        }
    });

    recordStop.addEventListener('click', () => {
        if (recorder && recorder.state !== 'inactive') {
            recordStop.disabled = true;
            recorder.stop();
        }
    });

    voiceForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        if (recorder && recorder.state !== 'inactive') {
            status(voiceStatus, t('recording'), 'error');
            return;
        }
        const submit = voiceForm.querySelector('[type="submit"]');
        submit.disabled = true;
        showResult('voice-result', '');
        try {
            if (!voiceTranscript.value.trim()) {
                if (!selectedAudio) throw new Error(t('chooseVoice'));
                if (selectedAudio.size > 12 * 1024 * 1024) throw new Error(t('audioLarge'));
                status(voiceStatus, t('transcribing'));
                const audio = new FormData();
                audio.append('audio', selectedAudio, selectedAudio.name || 'opname.webm');
                audio.append('language', byId('voice-language').value);
                const transcript = await requestApi('/transcribeer', { method: 'POST', body: audio });
                if (typeof transcript.gesproken !== 'string' || !transcript.gesproken.trim()) throw new Error(t('invalid'));
                voiceTranscript.value = transcript.gesproken;
            }
            status(voiceStatus, t('working'));
            const form = new FormData();
            form.append('action', 'note');
            form.append('text', voiceTranscript.value);
            const result = await requestApi('/verwerk', { method: 'POST', body: form });
            if (typeof result.result !== 'string' || !result.result.trim()) throw new Error(t('invalid'));
            showResult('voice-result', result.result);
            finishStatus(voiceStatus, result.warnings);
        } catch (error) {
            status(voiceStatus, error.message || t('invalid'), 'error');
        } finally {
            submit.disabled = false;
        }
    });

    async function processDocumentForm(event, action) {
        event.preventDefault();
        const formElement = event.currentTarget;
        const submit = formElement.querySelector('[type="submit"]');
        const formStatus = byId(`${action}-status`);
        const outputId = `${action}-result`;
        const file = byId(`${action}-file`).files[0];
        submit.disabled = true;
        showResult(outputId, '');
        try {
            if (file && file.size > 20 * 1024 * 1024) throw new Error(t('documentLarge'));
            status(formStatus, t('working'));
            const form = new FormData();
            form.append('action', action);
            form.append('text', byId(`${action}-text`).value);
            if (file) form.append('document', file);
            if (action === 'translate') {
                form.append('target_language', byId('translate-language').value);
                form.append('context', byId('translate-context').value);
            } else {
                form.append('url', byId('summary-url').value);
            }
            const result = await requestApi('/verwerk', { method: 'POST', body: form });
            if (typeof result.result !== 'string' || !result.result.trim()) throw new Error(t('invalid'));
            showResult(outputId, result.result);
            finishStatus(formStatus, result.warnings);
        } catch (error) {
            status(formStatus, error.message || t('invalid'), 'error');
        } finally {
            submit.disabled = false;
        }
    }
    byId('translate-form').addEventListener('submit', (event) => processDocumentForm(event, 'translate'));
    byId('summary-form').addEventListener('submit', (event) => processDocumentForm(event, 'summary'));

    const readingStatus = byId('reading-status');
    const readingList = byId('reading-list');
    const readingSearch = byId('reading-search');
    const readingFilter = byId('reading-filter');
    let readingItems = [];

    function renderReadingList() {
        const query = readingSearch.value.trim().toLocaleLowerCase();
        const filter = readingFilter.value;
        const filtered = readingItems.filter((item) => {
            const text = [item.title, item.summary, item.url, ...item.labels].join(' ').toLocaleLowerCase();
            return text.includes(query) && (filter === 'all' || (filter === 'read') === item.read);
        });
        readingList.replaceChildren();
        if (!filtered.length) {
            const empty = document.createElement('p');
            empty.className = 'empty-list';
            empty.textContent = readingItems.length ? t('noMatches') : t('noItems');
            readingList.append(empty);
            return;
        }
        filtered.forEach((item) => {
            const card = document.createElement('article');
            card.className = 'reading-card';
            const heading = document.createElement('h3');
            const link = document.createElement('a');
            link.href = item.url;
            link.target = '_blank';
            link.rel = 'noopener noreferrer';
            link.textContent = item.title;
            heading.append(link);
            const state = document.createElement('span');
            state.className = 'reading-state';
            state.textContent = item.read ? t('read') : t('unread');
            const summary = document.createElement('p');
            summary.textContent = item.summary;
            const labels = document.createElement('div');
            labels.className = 'reading-meta';
            item.labels.forEach((label) => {
                const chip = document.createElement('span');
                chip.className = 'reading-label';
                chip.textContent = label;
                labels.append(chip);
            });
            const actions = document.createElement('div');
            actions.className = 'button-row';
            const toggle = document.createElement('button');
            toggle.type = 'button';
            toggle.className = 'secondary-button';
            toggle.textContent = item.read ? t('markUnread') : t('markRead');
            const remove = document.createElement('button');
            remove.type = 'button';
            remove.className = 'secondary-button';
            remove.textContent = t('remove');
            toggle.addEventListener('click', async () => {
                toggle.disabled = true;
                remove.disabled = true;
                try {
                    await requestApi(`/leeslijst/${encodeURIComponent(item.id)}`, {
                        method: 'PATCH',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ read: !item.read }),
                    });
                    await loadReadingList();
                    status(readingStatus, t('updated'));
                } catch (error) {
                    status(readingStatus, error.message || t('invalid'), 'error');
                    toggle.disabled = false;
                    remove.disabled = false;
                }
            });
            remove.addEventListener('click', async () => {
                if (!window.confirm(t('confirmRemove'))) return;
                toggle.disabled = true;
                remove.disabled = true;
                try {
                    await requestApi(`/leeslijst/${encodeURIComponent(item.id)}`, { method: 'DELETE' });
                    await loadReadingList();
                    status(readingStatus, t('updated'));
                } catch (error) {
                    status(readingStatus, error.message || t('invalid'), 'error');
                    toggle.disabled = false;
                    remove.disabled = false;
                }
            });
            actions.append(toggle, remove);
            card.append(heading, state, summary, labels, actions);
            readingList.append(card);
        });
    }

    async function loadReadingList() {
        const data = await requestApi('/leeslijst');
        if (!Array.isArray(data.items) || data.items.some((item) => (
            !item || typeof item.id !== 'string' || typeof item.title !== 'string'
            || typeof item.url !== 'string' || !/^https?:\/\//i.test(item.url)
            || typeof item.summary !== 'string' || typeof item.read !== 'boolean'
            || !Array.isArray(item.labels) || item.labels.some((label) => typeof label !== 'string')
        ))) {
            throw new Error(t('invalid'));
        }
        readingItems = data.items;
        renderReadingList();
    }
    readingSearch.addEventListener('input', renderReadingList);
    readingFilter.addEventListener('change', renderReadingList);

    byId('reading-form').addEventListener('submit', async (event) => {
        event.preventDefault();
        const form = event.currentTarget;
        const submit = form.querySelector('[type="submit"]');
        submit.disabled = true;
        status(readingStatus, t('working'));
        try {
            const result = await requestApi('/leeslijst', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url: byId('reading-url').value }),
            });
            await loadReadingList();
            byId('reading-url').value = '';
            if (Array.isArray(result.warnings) && result.warnings.length) {
                status(readingStatus, `${t('added')} ${result.warnings.join(' ')}`, 'warning');
            } else {
                status(readingStatus, t('added'));
            }
        } catch (error) {
            status(readingStatus, error.message || t('invalid'), 'error');
        } finally {
            submit.disabled = false;
        }
    });

    status(readingStatus, t('loading'));
    loadReadingList().then(() => status(readingStatus, '')).catch((error) => {
        status(readingStatus, error.message || t('invalid'), 'error');
    });
    window.addEventListener('beforeunload', () => {
        if (recordStream) recordStream.getTracks().forEach((track) => track.stop());
        if (previewUrl) URL.revokeObjectURL(previewUrl);
    });
})();
