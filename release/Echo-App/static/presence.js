(() => {
    'use strict';

    const dutch = document.body.dataset.language === 'nl';
    const text = (en, nl) => dutch ? nl : en;
    const form = document.getElementById('presence-form');
    const delay = document.getElementById('presence-delay');
    const camera = document.getElementById('presence-camera');
    const notify = document.getElementById('presence-notify');
    const consent = document.getElementById('presence-consent');
    const start = document.getElementById('presence-start');
    const stop = document.getElementById('presence-stop');
    const status = document.getElementById('presence-status');
    const returns = document.getElementById('presence-returns');
    const token = document.querySelector('meta[name="echo-presence-token"]').content;
    let current = null;
    let busy = false;
    let connected = false;
    let initialized = false;
    let revision = 0;
    let actionError = '';

    const phases = {
        stopped: text('Off. The webcam is not in use by presence detection.', 'Uit. De webcam is niet in gebruik voor aanwezigheidsdetectie.'),
        starting: text('Opening the webcam...', 'Webcam openen...'),
        waiting: text('Look at the camera for two seconds. Detection is not armed yet.', 'Kijk twee seconden naar de camera. De bewaking is nog niet actief.'),
        confirming: text('Face detected; confirming presence...', 'Gezicht gezien; aanwezigheid bevestigen...'),
        present: text('Face detected. Detection is armed.', 'Gezicht gezien. De bewaking is actief.'),
        away: text('No face visible. Locking in {seconds} seconds.', 'Geen gezicht zichtbaar. Vergrendelen over {seconds} seconden.'),
        lock_requested: text('Windows lock requested. On return, unlock with Windows Hello or your PIN.', 'Vergrendeling aangevraagd bij Windows. Ontgrendel bij terugkomst met Windows Hello of je pincode.'),
        stopping: text('Stopping; waiting for the camera to be released...', 'Stoppen; wachten tot de camera is vrijgegeven...'),
        error: text('Detection stopped due to an error.', 'Detectie gestopt door een fout.'),
    };

    function updateControls() {
        const running = Boolean(current && current.running);
        start.disabled = busy || !connected || !current || !current.supported || running || !consent.checked;
        stop.disabled = busy || !running;
        for (const input of [delay, camera, notify, consent]) {
            input.disabled = busy || running;
        }
    }

    function render(value) {
        if (!value || typeof value.running !== 'boolean' || !Object.hasOwn(phases, value.phase)) {
            throw new Error(text('Invalid detection status received.', 'Ongeldige detectiestatus ontvangen.'));
        }
        current = value;
        connected = true;
        if (!initialized || value.running) {
            delay.value = value.delay_seconds;
            camera.value = value.camera_index;
            notify.value = String(value.notify);
            initialized = true;
        }
        status.textContent = !value.supported
            ? text('This feature requires Windows.', 'Deze functie vereist Windows.')
            : actionError || value.error_message || phases[value.phase].replace('{seconds}', String(value.seconds_remaining));
        status.classList.toggle('error', Boolean(actionError || value.error_message) || !value.supported);
        returns.textContent = text('Returns detected this session: ', 'Terugkomsten in deze sessie: ') + value.return_count;
        updateControls();
    }

    async function request(action, settings) {
        const controller = new AbortController();
        const timeout = setTimeout(() => controller.abort(), 8000);
        try {
            const response = await fetch(`/api/aanwezigheid/${action}`, {
                method: settings === undefined ? 'GET' : 'POST',
                cache: 'no-store',
                headers: settings === undefined ? {} : {
                    'Content-Type': 'application/json',
                    'X-Echo-Presence-Token': token,
                },
                body: settings === undefined ? undefined : JSON.stringify(settings),
                signal: controller.signal,
            });
            const data = await response.json();
            if (!response.ok || data.status !== 'success') {
                throw new Error(data.message || text('The request failed.', 'Het verzoek is mislukt.'));
            }
            return data.presence;
        } finally {
            clearTimeout(timeout);
        }
    }

    function showError(error) {
        connected = false;
        status.textContent = `${error.message} ${text(
            'Status is uncertain; detection may still be running. Reconnect to Echo to check or stop it.',
            'Status onzeker; detectie kan nog actief zijn. Herstel de verbinding met Echo om dit te controleren of te stoppen.'
        )}`;
        status.classList.add('error');
        updateControls();
    }

    async function poll() {
        const requestedRevision = revision;
        if (!busy) {
            try {
                const value = await request('status');
                if (requestedRevision === revision) render(value);
            } catch (error) {
                if (requestedRevision === revision) showError(error);
            }
        }
        setTimeout(poll, 1500);
    }

    async function change(action, settings) {
        revision += 1;
        actionError = '';
        busy = true;
        updateControls();
        try {
            render(await request(action, settings));
        } catch (error) {
            actionError = error.message;
            showError(error);
        } finally {
            busy = false;
            updateControls();
        }
    }

    consent.addEventListener('change', updateControls);
    form.addEventListener('submit', (event) => {
        event.preventDefault();
        if (start.disabled || !form.reportValidity()) return;
        change('start', {
            delay_seconds: Number(delay.value),
            camera_index: Number(camera.value),
            notify: notify.value === 'true',
        });
    });
    stop.addEventListener('click', () => change('stop', {}));
    poll();
})();
