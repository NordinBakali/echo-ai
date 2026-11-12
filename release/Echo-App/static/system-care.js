(() => {
    'use strict';
    const $ = id => document.getElementById(`care-${id}`);
    const nl = document.body.dataset.language === 'nl';
    const text = (en, dutch) => nl ? dutch : en;
    const token = document.querySelector('meta[name="echo-system-token"]').content;
    const profiles = { normal: text('Normal', 'Normaal'), streaming: 'Streaming', security: 'Security', gaming: 'Gaming', heavy_work: text('Heavy work', 'Zwaar werk') };
    let care, available, previewToken = '', initialized = false, lastAlert = 0, busy = false;
    const mib = value => `${(value / 1048576).toFixed(1)} MiB`;
    const date = value => value ? new Date(value * 1000).toLocaleString() : '-';
    const kinds = {
        unknown_device: text('Unknown LAN device', 'Onbekend LAN-apparaat'),
        failed_login: text('Failed sign-in / account lockout', 'Mislukte login / accountvergrendeling'),
        log_cleared: text('Audit log cleared', 'Auditlog gewist'),
        crash: text('Crash or memory shortage', 'Crash of geheugentekort'),
        system_error: text('System warning / error', 'Systeemwaarschuwing / fout'),
        resource_pressure: text('High CPU/RAM: approved app stopped', 'Hoge CPU/RAM: goedgekeurde app gestopt'),
    };

    async function api(action, data) {
        const response = await fetch(`/api/systeemzorg/${action}`, {
            method: data === undefined ? 'GET' : 'POST',
            headers: { 'Content-Type': 'application/json', 'X-Echo-System-Token': token },
            body: data === undefined ? undefined : JSON.stringify(data),
            cache: 'no-store', signal: AbortSignal.timeout(35000),
        });
        const result = await response.json();
        if (!response.ok || result.status !== 'success') throw new Error(result.message || `HTTP ${response.status}`);
        return result;
    }

    function discardPreview() {
        previewToken = '';
        $('execute').disabled = true;
        $('preview').textContent = '';
    }

    function render(data) {
        care = data;
        $('status').textContent = `${data.running ? (data.stopping ? text('Stopping...', 'Bezig met stoppen...') : text('Monitoring on.', 'Bewaking aan.')) : text('Monitoring off.', 'Bewaking uit.')} ${text('Last LAN scan:', 'Laatste LAN-scan:')} ${date(data.last_network)}. ${text('Last log attempt:', 'Laatste logpoging:')} ${date(data.last_logs)}`;
        $('coverage').textContent = Object.entries(data.errors).map(([source, error]) => `${source}: ${error}`).join('\n');
        $('stop').disabled = !data.running;
        for (const element of $('monitor').elements) {
            if (element.id !== 'care-stop') element.disabled = data.running || busy;
        }
        $('start').disabled = data.running || busy || !$('consent').checked;
        $('restore').disabled = !data.can_restore_power || data.resource.status === 'running';
        $('auto-status').textContent = data.automatic_resources ? text('Approved profile actions: enabled for this session.', 'Goedgekeurde profielacties: aan voor deze sessie.') : text('Profile automation: off.', 'Profielautomatiek: uit.');
        $('auto-on').disabled = data.automatic_resources;
        $('auto-off').disabled = !data.automatic_resources;
        const job = data.resource;
        const pressure = data.pressure;
        if (pressure.enabled) $('pressure-profile').value = pressure.profile;
        $('pressure-active').textContent = `${text('Active Echo profile', 'Actief Echo-profiel')}: ${profiles[pressure.active_profile] || pressure.active_profile}`;
        $('pressure-status').textContent = `${pressure.enabled ? text('CPU/RAM protection ON.', 'CPU/RAM-bescherming AAN.') : pressure.running ? text('Stopping CPU/RAM protection…', 'CPU/RAM-bescherming stoppen…') : text('CPU/RAM protection OFF.', 'CPU/RAM-bescherming UIT.')} ` +
            `CPU: ${pressure.cpu === null ? '-' : pressure.cpu.toFixed(1) + '%'} | RAM: ${pressure.ram === null ? '-' : pressure.ram.toFixed(1) + '%'} | ` +
            `${text('Last stopped app', 'Laatste gestopte app')}: ${date(pressure.last_action)} | ${text('Inaccessible processes', 'Niet toegankelijke processen')}: ${pressure.inaccessible}`;
        $('pressure-error').textContent = pressure.error;
        for (const id of ['pressure-profile', 'pressure-speech', 'pressure-consent']) $(id).disabled = pressure.enabled || pressure.running || busy;
        $('pressure-start').disabled = pressure.enabled || pressure.running || busy || !$('pressure-consent').checked ||
            $('pressure-profile').value !== pressure.active_profile || !data.policies[$('pressure-profile').value]?.apps.length;
        $('pressure-stop').disabled = busy || (!pressure.enabled && !pressure.running);
        $('job').textContent = `${text('Hardware job:', 'Hardwaretaak:')} ${job.status}${job.error ? `\n${job.error}` : ''}` +
            (job.memory ? `\n${text('Available RAM:', 'Beschikbaar RAM:')} ${mib(job.memory.available)} (${text('measured change, not guaranteed gain', 'gemeten verschil, geen gegarandeerde winst')}: ${mib(job.available_change)})` : '') +
            (job.processes || []).map(p => `\n${p.name} (${p.pid}): ${p.status}${p.error ? ` - ${p.error}` : ''}`).join('');
        $('devices').replaceChildren();
        for (const device of data.devices) {
            const li = document.createElement('li');
            li.textContent = `${device.ip} | ${device.mac || text('MAC unavailable', 'MAC onbekend')} | ${device.scope} | ${device.trusted ? text('Trusted', 'Vertrouwd') : text('Unknown', 'Onbekend')} | ${text('Last seen', 'Laatst gezien')}: ${date(device.last_seen)} `;
            if (device.mac) {
                const button = document.createElement('button');
                button.type = 'button';
                button.className = 'secondary-button';
                button.textContent = device.trusted ? text('Revoke trust', 'Vertrouwen intrekken') : text('Trust', 'Vertrouwen');
                button.onclick = () => perform(() => api('trust', { scope: device.scope, identity: device.identity, trusted: !device.trusted }));
                li.append(button);
            }
            $('devices').append(li);
        }
        $('alerts').replaceChildren();
        for (const alert of data.alerts) {
            const li = document.createElement('li');
            li.textContent = `[${profiles[alert.profile]}] ${date(alert.created)} - ${kinds[alert.kind] || alert.kind}: ${alert.summary}`;
            $('alerts').append(li);
        }
        const newest = data.alerts[0];
        if (initialized && newest && newest.id > lastAlert && data.config.desktop && 'Notification' in window && Notification.permission === 'granted') {
            new Notification(`Echo - ${profiles[newest.profile]}`, { body: kinds[newest.kind] || newest.kind, tag: 'echo-system-care' });
        }
        lastAlert = Math.max(lastAlert, newest?.id || 0);
    }

    async function perform(action) {
        if (busy) return;
        busy = true;
        $('error').textContent = '';
        try {
            const result = await action();
            if (result?.care) render(result.care);
        } catch (error) {
            $('error').textContent = text('Action failed: ', 'Actie mislukt: ') + error.message;
        } finally {
            busy = false;
            if (care) render(care);
        }
    }

    function loadPolicy() {
        discardPreview();
        if (!available || !care) return;
        const policy = care.policies[$('profile').value] || { apps: [], power_plan: '', active_cooling: false };
        const apps = new Map();
        for (const item of available.processes.items) {
            const previous = apps.get(item.exe);
            apps.set(item.exe, { name: item.name, memory: item.memory + (previous?.memory || 0) });
        }
        for (const path of policy.apps) {
            if (!apps.has(path)) apps.set(path, { name: text('Not running', 'Niet actief'), memory: 0 });
        }
        $('apps').replaceChildren();
        for (const [path, item] of apps) {
            $('apps').add(new Option(`${item.name} - ${mib(item.memory)} - ${path}`, path, false, policy.apps.includes(path)));
        }
        $('power').value = policy.power_plan;
        if ($('power').value !== policy.power_plan) {
            $('power').add(new Option(text('Saved plan unavailable', 'Opgeslagen plan niet beschikbaar'), policy.power_plan, false, true));
        }
        $('cooling').checked = policy.active_cooling;
    }

    async function refreshResources() {
        available = await api('resources');
        $('power').replaceChildren(new Option(text('Leave unchanged', 'Niet wijzigen'), ''));
        for (const plan of available.power.plans) $('power').add(new Option(plan.name, plan.id));
        $('power').disabled = !available.power.supported;
        $('cooling').disabled = !available.power.active_cooling;
        $('capabilities').textContent = `${text('Available RAM:', 'Beschikbaar RAM:')} ${mib(available.memory.available)}. ${text('Inaccessible processes:', 'Niet toegankelijke processen:')} ${available.processes.inaccessible}.`;
        loadPolicy();
    }

    async function savePolicy() {
        discardPreview();
        const result = await api('policy', {
            profile: $('profile').value,
            policy: { apps: Array.from($('apps').selectedOptions, o => o.value), power_plan: $('power').value, active_cooling: $('cooling').checked },
        });
        render(result.care);
        return result;
    }

    for (const id of ['profile', 'alert-profile', 'pressure-profile']) {
        for (const [value, label] of Object.entries(profiles)) $(id).add(new Option(label, value));
    }
    $('profile').value = 'gaming';
    $('pressure-profile').value = 'gaming';
    $('pressure-consent').onchange = () => { if (care) render(care); };
    $('pressure-profile').onchange = () => { $('pressure-consent').checked = false; if (care) render(care); };
    $('pressure-form').onsubmit = event => {
        event.preventDefault();
        void perform(async () => {
            if (!window.confirm(text(
                'Automatically terminate heavy approved background apps above 80% CPU/RAM for this session? Unsaved work may be lost. The active app remains protected.',
                'Zware goedgekeurde achtergrondapps automatisch stoppen boven 80% CPU/RAM voor deze sessie? Onopgeslagen werk kan verloren gaan. De actieve app blijft beschermd.'
            ))) return;
            return api('pressure-start', {
                profile: $('pressure-profile').value, authorized: $('pressure-consent').checked,
                speech: $('pressure-speech').checked,
            });
        });
    };
    $('pressure-stop').onclick = () => perform(() => api('pressure-stop', {}));
    $('consent').onchange = () => { if (care) render(care); };
    $('profile').onchange = loadPolicy;
    $('policy').onchange = discardPreview;
    $('policy').onsubmit = event => { event.preventDefault(); void perform(savePolicy); };
    $('refresh-apps').onclick = () => perform(refreshResources);
    $('monitor').onsubmit = event => {
        event.preventDefault();
        void perform(async () => {
            if ($('desktop').checked) {
                if (!('Notification' in window) || await Notification.requestPermission() !== 'granted') {
                    throw new Error(text('Desktop notification permission was not granted. Uncheck that option or allow notifications.', 'Geen toestemming voor bureaubladmeldingen. Zet die optie uit of sta meldingen toe.'));
                }
            }
            return api('start', { authorized: $('consent').checked, config: {
                network: $('network').checked, logs: $('logs').checked, address: $('adapter').value,
                network_interval: Number($('network-interval').value), log_interval: Number($('log-interval').value),
                alert_profile: $('alert-profile').value, sound: $('sound').checked, desktop: $('desktop').checked,
            } });
        });
    };
    $('stop').onclick = () => perform(() => api('stop', {}));
    $('preview-button').onclick = () => perform(async () => {
        await savePolicy();
        const { preview } = await api('preview', { profile: $('profile').value });
        previewToken = preview.token;
        $('preview').textContent = `${profiles[preview.profile]}: ${preview.processes.length} ${text('processes', 'processen')} / ${mib(preview.estimated_process_memory)}\n` +
            preview.processes.map(p => `${p.name} | PID ${p.pid} | ${new Date(p.created * 1000).toLocaleString()} | ${mib(p.memory)} | ${p.exe}`).join('\n') +
            `\n${text('Power plan', 'Energieplan')}: ${preview.policy.power_plan || '-'}\n${text('Active cooling', 'Actieve koeling')}: ${preview.policy.active_cooling}`;
        $('execute').disabled = false;
    });
    $('execute').onclick = () => perform(async () => {
        if (!previewToken || !window.confirm(text('Terminate these exact approved processes and apply the shown power settings? Unsaved work may be lost.', 'Deze exacte goedgekeurde processen stoppen en de getoonde energie-instellingen toepassen? Onopgeslagen werk kan verloren gaan.'))) return;
        const value = previewToken;
        discardPreview();
        return api('execute', { token: value });
    });
    $('auto-on').onclick = () => perform(async () => {
        if (!window.confirm(text('Apply SAVED policies without a new preview whenever you manually apply a profile locally? This can terminate apps and lose unsaved work.', 'OPGESLAGEN beleid zonder nieuw voorbeeld uitvoeren bij elke handmatige lokale profielwissel? Dit kan apps stoppen en onopgeslagen werk verliezen.'))) return;
        return api('automatic', { enabled: true });
    });
    $('auto-off').onclick = () => perform(() => api('automatic', { enabled: false }));
    $('restore').onclick = () => perform(() => api('restore', {}));

    async function initialize() {
        await perform(async () => {
            const [status, interfaces] = await Promise.all([api('status'), api('adapters')]);
            for (const item of interfaces.adapters) {
                const option = new Option(`${item.name}: ${item.address} (${item.network})${item.supported ? '' : text(' - unsupported size', ' - niet ondersteunde grootte')}`, item.address);
                option.disabled = !item.supported;
                $('adapter').add(option);
            }
            const config = status.care.config;
            for (const name of ['network', 'logs', 'sound', 'desktop']) $(name).checked = config[name];
            $('adapter').value = config.address;
            $('network-interval').value = config.network_interval;
            $('log-interval').value = config.log_interval;
            $('alert-profile').value = config.alert_profile;
            render(status.care);
            $('pressure-profile').value = status.care.pressure.enabled
                ? status.care.pressure.profile : status.care.pressure.active_profile;
            await refreshResources();
            initialized = true;
        });
        setTimeout(poll, 2000);
    }
    async function poll() {
        if (!busy) {
            try { render((await api('status')).care); }
            catch (error) {
                $('error').textContent = text('Status unavailable: ', 'Status niet beschikbaar: ') + error.message;
                $('pressure-status').textContent = text('CPU/RAM protection status unknown; it may still be active.', 'Status CPU/RAM-bescherming onbekend; deze kan nog actief zijn.');
            }
        }
        setTimeout(poll, 2000);
    }
    void initialize();
})();
