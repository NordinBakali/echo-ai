(() => {
    'use strict';
    const el = name => document.getElementById(`local-ai-${name}`);
    const nl = document.body.dataset.language === 'nl';
    const t = (en, dutch) => nl ? dutch : en;
    const token = document.querySelector('meta[name="echo-system-token"]').content;
    let busy = false;

    function controls() {
        el('submit').disabled = busy || !el('consent').checked || !el('model').value || !el('files').files.length;
        for (const name of ['model', 'refresh', 'files', 'consent', 'clear']) el(name).disabled = busy;
    }

    function clearReport() {
        el('report').hidden = true;
        el('summary').textContent = '';
        el('findings').replaceChildren();
        el('error').textContent = '';
        el('status').textContent = '';
    }

    async function request(action, data) {
        const response = await fetch(`/api/systeemzorg/local-ai/${action}`, {
            method: data === undefined ? 'GET' : 'POST',
            headers: {'Content-Type': 'application/json', 'X-Echo-System-Token': token},
            body: data === undefined ? undefined : JSON.stringify(data),
            cache: 'no-store', signal: AbortSignal.timeout(data === undefined ? 10000 : 195000),
        });
        const result = await response.json();
        if (!response.ok || result.status !== 'success') throw new Error(result.message || `HTTP ${response.status}`);
        return result;
    }

    el('refresh').onclick = async () => {
        if (busy) return;
        busy = true;
        clearReport();
        controls();
        el('model').replaceChildren(new Option(t('Choose a local model', 'Kies een lokaal model'), ''));
        try {
            const result = await request('models');
            for (const model of result.models) el('model').add(new Option(model, model));
            el('status').textContent = result.models.length
                ? t('Choose a model and files. Nothing has been analyzed yet.', 'Kies een model en bestanden. Er is nog niets geanalyseerd.')
                : t('No local models found. Install a local text model in Ollama yourself.', 'Geen lokale modellen gevonden. Installeer zelf een lokaal tekstmodel in Ollama.');
        } catch (error) {
            el('error').textContent = error.message;
        } finally {
            busy = false;
            controls();
        }
    };

    for (const name of ['files', 'model', 'consent']) {
        el(name).onchange = () => { clearReport(); controls(); };
    }
    el('clear').onclick = () => {
        el('files').value = '';
        el('consent').checked = false;
        clearReport();
        controls();
    };

    el('form').onsubmit = async event => {
        event.preventDefault();
        if (busy || !el('form').reportValidity()) return;
        busy = true;
        clearReport();
        controls();
        el('status').textContent = t('Analyzing locally… This can take up to 3 minutes.', 'Lokaal analyseren… Dit kan tot 3 minuten duren.');
        try {
            const selection = Array.from(el('files').files);
            if (selection.length > 5 || selection.reduce((sum, file) => sum + file.size, 0) > 65536) {
                throw new Error(t('Select at most 5 files, at most 64 KiB combined.', 'Kies maximaal 5 bestanden, samen maximaal 64 KiB.'));
            }
            const decoder = new TextDecoder('utf-8', {fatal: true});
            const files = [];
            for (const file of selection) files.push({name: file.name, text: decoder.decode(await file.arrayBuffer())});
            if (files.reduce((sum, file) => sum + Array.from(file.text).length, 0) > 12000) {
                throw new Error(t('Select a smaller excerpt: at most 12,000 characters combined.', 'Kies een kleiner fragment: samen maximaal 12.000 tekens.'));
            }
            const {report} = await request('analyze', {model: el('model').value, files, authorized: el('consent').checked});
            el('summary').textContent = report.summary;
            for (const finding of report.findings) {
                const item = document.createElement('li');
                item.style.whiteSpace = 'pre-wrap';
                item.textContent = `${finding.file}:${finding.line}\n${finding.evidence}\n${finding.explanation}\n${finding.next_step}`;
                el('findings').append(item);
            }
            el('report').hidden = false;
            el('status').textContent = `${t('Analyzed locally', 'Lokaal geanalyseerd')}: ${report.model} | ${report.files.join(', ')} | ${report.findings.length} ${t('findings', 'bevindingen')}`;
        } catch (error) {
            el('status').textContent = t('Analysis not completed. No cloud fallback was used.', 'Analyse niet voltooid. Er is geen cloudfallback gebruikt.');
            el('error').textContent = error instanceof TypeError
                ? t('Could not read the selected UTF-8 files or reach Echo. Check the files and connection.', 'Kon de gekozen UTF-8-bestanden niet lezen of Echo niet bereiken. Controleer bestanden en verbinding.')
                : error.message;
        } finally {
            busy = false;
            controls();
        }
    };
    controls();
})();
