(() => {
    'use strict';
    const nl = document.body.dataset.language === 'nl';
    const t = (en, dutch) => nl ? dutch : en;
    const el = (id) => document.getElementById(`coach-${id}`);
    const fields = {camera_index: 'camera', posture: 'posture', gestures: 'gestures', extra_gestures: 'extra',
        delay_seconds: 'delay', swipe_action: 'swipe', microphone: 'microphone', sound: 'sound'};
    const token = document.querySelector('meta[name="echo-presence-token"]').content;
    const canvas = el('preview');
    const ctx = canvas.getContext('2d');
    let current = null, busy = false, online = false, revision = 0, initialized = false, lastAlerts = null;
    let actionError = '', microphoneMessage = '', microphoneLoading = false, microphoneEdited = false;
    class ServerResponseError extends Error {}
    const setText = (node, text) => { if (node.textContent !== text) node.textContent = text; };
    const states = {
        stopped: t('Off. Camera released by this feature.', 'Uit. Deze functie heeft de camera vrijgegeven.'),
        starting: t('Loading local models and camera; first download can take a minute...', 'Lokale modellen en camera laden; de eerste download kan een minuut duren...'),
        monitoring: t('Camera active. ', 'Camera actief. '),
        stopping: t('Stopping and releasing the camera...', 'Stoppen en camera vrijgeven...'),
        paused: t('Paused: desktop locked or unavailable. Re-enable actions after unlocking.', 'Gepauzeerd: bureaublad vergrendeld of niet beschikbaar. Activeer acties opnieuw na ontgrendelen.'),
        error: t('Detection stopped.', 'Detectie gestopt.'),
    };
    const postures = {
        needs_calibration: t('Set your upright posture first.', 'Stel eerst je rechte zithouding in.'),
        no_pose: t('Head and shoulders not clearly visible.', 'Hoofd en schouders niet duidelijk zichtbaar.'),
        upright: t('Posture close to your baseline.', 'Houding lijkt op je ingestelde zithouding.'),
        leaning: t('Leaning forward detected; timing...', 'Vooroverzitten herkend; tijd bijhouden...'),
    };
    const reminder = t('You have been leaning forward for a while. Relax your shoulders or take a short break.',
        'Je zit al even voorover. Ontspan je schouders of neem een korte pauze.');
    const notices = {
        trained: t('Calibration saved for this session.', 'Kalibratie bewaard voor deze sessie.'),
        scan_complete: t('Hand scanned. Gesture actions are now ON.', 'Hand gescand. Gebaaracties staan nu AAN.'),
        scan_cancelled: t('Hand scan cancelled. Gesture actions remain off.', 'Handscan gestopt. Gebaaracties blijven uit.'),
        training_failed: t('Scan or calibration failed. Check framing, show the requested pose, then try again.', 'Scan of kalibratie mislukt. Controleer het beeld, toon de gevraagde houding en probeer opnieuw.'),
        posture_reminder: reminder,
        microphone: t('Microphone control failed. Gesture actions disabled.', 'Microfoonbediening mislukt. Gebaaracties uitgeschakeld.'),
        action: t('Windows action failed. Gesture actions disabled.', 'Windows-actie mislukt. Gebaaracties uitgeschakeld.'),
        locked: states.paused,
        dependency: t('A required package is missing. Restart via the Echo launcher.', 'Een benodigd pakket ontbreekt. Herstart via de Echo-launcher.'),
    };
    const labels = {open: t('open hand', 'open hand'), fist: t('fist', 'vuist'), point: t('pointing finger', 'wijsvinger'),
        peace: t('V sign', 'V-teken'), pinch: t('pinch', 'knijpgebaar'),
        thumb_up: t('thumb up', 'duim omhoog'), thumb_down: t('thumb down', 'duim omlaag'),
        two_open: t('two open hands', 'twee open handen'), two_fists: t('two fists', 'twee vuisten'), unknown: t('not recognized', 'niet herkend')};
    const sides = {Left: t('left', 'links'), Right: t('right', 'rechts'), Hand: t('hand', 'hand')};
    const actionNames = {mute: t('microphone muted', 'microfoon gedempt'), play_pause: t('play/pause', 'afspelen/pauzeren'),
        show_desktop: t('show desktop', 'bureaublad tonen'), volume_up: t('volume up', 'volume omhoog'),
        volume_down: t('volume down', 'volume omlaag'), speaker_mute: t('sound on/off', 'geluid aan/uit'),
        zoom_in: t('zoom in', 'inzoomen'), zoom_out: t('zoom out', 'uitzoomen')};
    const handConnections = [[0, 1], [1, 2], [2, 3], [3, 4], [0, 5], [5, 6], [6, 7], [7, 8],
        [5, 9], [9, 10], [10, 11], [11, 12], [9, 13], [13, 14], [14, 15], [15, 16],
        [13, 17], [17, 18], [18, 19], [19, 20], [17, 0]];
    const handColors = ['#6cf3d1', '#ffd27d'];
    const label = (name) => labels[name] || labels.unknown;
    const scanNeedsRestart = (data) => data.gesture_ready && ['stopped', 'stopping', 'error'].includes(data.phase);
    const missingFeatures = t('Enable posture reminders or hand gestures before starting.',
        'Schakel houdingsherinneringen of handgebaren in voordat je start.');

    function actionName(name, swipe) {
        if (name === 'left' || name === 'right') {
            const next = name === 'right';
            return swipe === 'desktop' ? (next ? t('next desktop', 'volgend bureaublad') : t('previous desktop', 'vorig bureaublad'))
                : (next ? t('next track', 'volgend nummer') : t('previous track', 'vorig nummer'));
        }
        return actionNames[name] || '';
    }

    function setSummary(data) {
        const unknown = t('Unknown', 'Onbekend');
        const cameraStates = {
            stopped: [t('Off', 'Uit'), 'off'],
            starting: [t('Starting', 'Starten'), 'warning'],
            monitoring: [t('On', 'Aan'), 'active'],
            stopping: [t('Stopping', 'Stoppen'), 'warning'],
            paused: [t('Paused', 'Gepauzeerd'), 'warning'],
            error: [t('Error', 'Fout'), 'error'],
        };
        const camera = data ? cameraStates[data.phase] : [unknown, 'unknown'];
        const scanning = data && data.training === 'activate';
        const scanExpired = data && scanNeedsRestart(data);
        const scan = !data ? [unknown, 'unknown'] : scanning ? [t('Scanning', 'Scannen'), 'warning']
            : scanExpired ? [t('Scan again', 'Opnieuw scannen'), 'warning']
            : data.gesture_ready ? [t('Ready', 'Klaar'), 'active'] : [t('Not scanned', 'Nog niet gescand'), 'off'];
        const actions = !data ? [unknown, 'unknown'] : data.armed
            ? [t('On', 'Aan'), 'active'] : [t('Off', 'Uit'), 'off'];
        for (const [id, value] of [['state-camera', camera], ['state-scan', scan], ['state-actions', actions]]) {
            setText(el(id), value[0]);
            if (el(id).dataset.state !== value[1]) el(id).dataset.state = value[1];
        }
    }

    function selectMicrophone(value) {
        const select = el('microphone');
        let option = Array.from(select.options).find((item) => item.value === value);
        if (!option) {
            option = new Option(t('Saved microphone (unavailable)', 'Opgeslagen microfoon (niet beschikbaar)'), value);
            option.dataset.unavailable = 'true';
            select.add(option);
        }
        select.value = value;
    }

    function microphoneUnavailable() {
        const option = el('microphone').selectedOptions[0];
        return Boolean(option && option.dataset.unavailable === 'true');
    }

    function updateMicrophoneStatus() {
        const unavailable = microphoneUnavailable()
            ? el('gestures').checked
                ? t('The saved microphone is not in the list. Refresh it or choose another microphone before starting.',
                    'De opgeslagen microfoon staat niet in de lijst. Ververs de lijst of kies een andere microfoon voordat je start.')
                : t('The saved microphone is not in the list. Choose another before using gestures.',
                    'De opgeslagen microfoon staat niet in de lijst. Kies een andere als je gebaren wilt gebruiken.')
            : '';
        setText(el('device-status'), [microphoneMessage, unavailable].filter(Boolean).join(' '));
    }

    function controls() {
        const running = Boolean(current && current.running);
        for (const id of [...Object.values(fields), 'consent']) el(id).disabled = busy || running;
        el('start').disabled = busy || !online || running || !el('consent').checked
            || (el('gestures').checked && microphoneUnavailable());
        el('stop').disabled = busy || !running;
        el('refresh-microphones').disabled = busy || microphoneLoading;
        document.querySelectorAll('[data-train]').forEach((button) => {
            const enabled = current && current.settings[button.dataset.train === 'posture' ? 'posture' : 'gestures'];
            button.disabled = busy || !online || !enabled || current.phase !== 'monitoring' || Boolean(current.training);
        });
        el('arm').disabled = busy || !online || !current || current.phase !== 'monitoring'
            || !current.gesture_ready || Boolean(current.training) || current.armed;
        el('disarm').disabled = busy || !current || (!current.armed && current.training !== 'activate');
        setText(el('disarm'), current && current.training === 'activate'
            ? t('Cancel hand scan', 'Handscan stoppen') : t('Practice only', 'Alleen oefenen'));
        el('unmute').disabled = busy || !online || !current || !current.muted_by_echo;
    }

    function draw(points, hands, training) {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.fillStyle = '#9fcfff';
        for (const [x, y] of points.pose) {
            ctx.beginPath();
            ctx.arc(x * canvas.width, y * canvas.height, 3, 0, Math.PI * 2);
            ctx.fill();
        }
        for (let offset = 0; offset + 21 <= points.hand.length; offset += 21) {
            const index = offset / 21;
            const coordinates = points.hand.slice(offset, offset + 21);
            ctx.strokeStyle = ctx.fillStyle = handColors[index % handColors.length];
            ctx.lineWidth = 3;
            ctx.beginPath();
            for (const [start, end] of handConnections) {
                ctx.moveTo(coordinates[start][0] * canvas.width, coordinates[start][1] * canvas.height);
                ctx.lineTo(coordinates[end][0] * canvas.width, coordinates[end][1] * canvas.height);
            }
            ctx.stroke();
            for (const [x, y] of coordinates) {
                ctx.beginPath();
                ctx.arc(x * canvas.width, y * canvas.height, 3, 0, Math.PI * 2);
                ctx.fill();
            }
            if (!training && hands[index]) {
                if (hands[index].gesture === 'pinch') {
                    ctx.save();
                    ctx.strokeStyle = ctx.fillStyle = '#ffffff';
                    ctx.setLineDash([6, 4]);
                    ctx.beginPath();
                    ctx.moveTo(coordinates[4][0] * canvas.width, coordinates[4][1] * canvas.height);
                    ctx.lineTo(coordinates[8][0] * canvas.width, coordinates[8][1] * canvas.height);
                    ctx.stroke();
                    for (const tip of [4, 8]) {
                        ctx.beginPath();
                        ctx.arc(coordinates[tip][0] * canvas.width, coordinates[tip][1] * canvas.height, 6, 0, Math.PI * 2);
                        ctx.fill();
                    }
                    ctx.restore();
                }
                const text = `${sides[hands[index].side] || sides.Hand}: ${label(hands[index].gesture)}`;
                const [x, y] = coordinates[0];
                ctx.font = 'bold 16px Segoe UI, sans-serif';
                ctx.fillText(text, Math.max(4, Math.min(canvas.width - ctx.measureText(text).width - 4, x * canvas.width)), Math.max(18, y * canvas.height - 10));
            }
        }
    }

    function guidance(data) {
        if (data.phase === 'stopped') return t('Start the camera assistant to see your hands and the next step.',
            'Start de camera-assistent om je handen en de volgende stap te zien.');
        if (data.phase !== 'monitoring') return states[data.phase];
        if (data.training === 'posture') return t('Keep your head and shoulders in view and sit upright until the bar reaches 100%.',
            'Houd je hoofd en schouders in beeld en zit rechtop tot de balk 100% is.');
        if (!data.settings.gestures) return t('Hand gestures are off. Stop the assistant and enable Recognize hand gestures.',
            'Handgebaren staan uit. Stop de assistent en vink Handgebaren herkennen aan.');
        const count = Math.floor(data.points.hand.length / 21);
        if (data.training === 'activate' || data.training === 'open' || data.training === 'fist') {
            if (!count) return t('No hand visible. Hold one whole hand in front of the camera in good light.',
                'Geen hand zichtbaar. Houd één hele hand voor de camera en zorg voor goed licht.');
            if (count > 1) return t('Show only one hand while teaching; lower the other hand.',
                'Toon tijdens het aanleren maar één hand; laat je andere hand zakken.');
            return data.training !== 'fist'
                ? t('I see one hand. Face your palm toward the camera, extend your fingers and hold still until 100%.',
                    'Ik zie één hand. Richt je handpalm naar de camera, strek je vingers en houd stil tot 100%.')
                : t('I see one hand. Make a fist with your fingers folded and hold still until 100%.',
                    'Ik zie één hand. Maak een vuist met je vingers gevouwen en houd stil tot 100%.');
        }
        if (!count) return t('No hand visible. Show your entire hand in the sketch and improve the lighting.',
            'Geen hand zichtbaar. Toon je hele hand in de schets en zorg voor goed licht.');
        if (!data.gesture_ready) return t('I see your hand. Click Scan hand and enable gestures and hold your open palm still.',
            'Ik zie je hand. Klik op Hand scannen en gebaren activeren en houd je open hand stil.');
        if (data.gesture === 'unknown') return count === 2
            ? t('I see two hands, but the gestures are unclear. Keep your hands apart and all fingers in view.',
                'Ik zie twee handen, maar de gebaren zijn niet duidelijk. Houd je handen uit elkaar en alle vingers in beeld.')
            : t('I see a hand, but the gesture is unclear. Keep all fingers in view and try again.',
                'Ik zie een hand, maar het gebaar is niet duidelijk. Houd alle vingers in beeld en probeer opnieuw.');
        if (!data.armed) return t(`Practice mode: I recognize ${label(data.gesture)}. Enable gesture actions when ready.`,
            `Oefenstand: ik herken ${label(data.gesture)}. Klik op Gebaaracties opnieuw activeren als je klaar bent.`);
        const release = data.hands.some((hand) => hand.needs_release
            && (hand.gesture === data.gesture || data.gesture === 'two_open' || data.gesture === 'two_fists'));
        if (release) return t('Gesture already used. Lower a hand or show a different gesture before repeating.',
            'Dit gebaar is al uitgevoerd. Laat een hand even zakken of toon een ander gebaar voordat je het herhaalt.');
        if (data.gesture === 'pinch' && data.hands.filter((hand) => hand.gesture === 'pinch').length > 1) {
            return t('Use one pinching hand at a time. Lower the other hand, then touch thumb and index finger again.',
                'Knijp met één hand tegelijk. Laat de andere hand zakken en breng duim en wijsvinger opnieuw samen.');
        }
        if (data.cooldown_seconds > 0 && data.gesture !== 'pinch') return t('Please wait briefly before the next gesture action.',
            'Wacht even voordat Echo de volgende gebaaractie uitvoert.');
        const instructions = {
            open: t('Open hand recognized. Swipe horizontally across a quarter of the sketch.',
                'Open hand herkend. Veeg horizontaal over een kwart van de schets.'),
            fist: t('Fist recognized. Hold for 0.8 seconds to mute the selected microphone.',
                'Vuist herkend. Houd 0,8 seconden vast om de gekozen microfoon te dempen.'),
            point: t('Pointing finger recognized. Hold your hand still for 0.8 seconds to play or pause.',
                'Wijsvinger herkend. Houd je hand 0,8 seconden stil voor afspelen of pauzeren.'),
            pinch: t('Pinch recognized. Keep thumb and index finger close for 0.4 seconds, then widen to raise volume or narrow to lower it. Keep the other three fingers extended.',
                'Knijpgebaar herkend. Houd duim en wijsvinger 0,4 seconden dicht bij elkaar; verder uit elkaar is harder, dichterbij is zachter. Houd de andere drie vingers gestrekt.'),
            peace: t('V sign recognized. Hold for 0.8 seconds to show the desktop.',
                'V-teken herkend. Houd 0,8 seconden vast om het bureaublad te tonen.'),
            thumb_up: t('Thumb up recognized. Hold to turn up the volume.', 'Duim omhoog herkend. Houd vast om het volume te verhogen.'),
            thumb_down: t('Thumb down recognized. Hold to turn down the volume.', 'Duim omlaag herkend. Houd vast om het volume te verlagen.'),
            two_fists: t('Two fists recognized. Hold for 1 second to toggle speaker sound.',
                'Twee vuisten herkend. Houd 1 seconde vast om het speakergeluid aan of uit te zetten.'),
            two_open: t('Two open hands recognized. Move them apart or together to zoom.',
                'Twee open handen herkend. Beweeg ze uit elkaar of naar elkaar toe om te zoomen.'),
        };
        return instructions[data.gesture] || t('Gesture recognized.', 'Gebaar herkend.');
    }

    function render(data) {
        if (!data || !Object.hasOwn(states, data.phase)
            || typeof data.running !== 'boolean' || typeof data.armed !== 'boolean' || typeof data.gesture_ready !== 'boolean'
            || !data.settings || typeof data.settings !== 'object' || typeof data.settings.microphone !== 'string'
            || typeof data.settings.posture !== 'boolean' || typeof data.settings.gestures !== 'boolean'
            || !data.points || !Array.isArray(data.points.pose) || !Array.isArray(data.points.hand) || !Array.isArray(data.hands)) {
            throw new ServerResponseError(t('Invalid camera status.', 'Ongeldige camerastatus.'));
        }
        current = data;
        online = true;
        if (!initialized || data.running) {
            for (const [key, id] of Object.entries(fields)) {
                const input = el(id);
                if (input.type === 'checkbox') input.checked = data.settings[key];
                else if (key === 'microphone') selectMicrophone(data.settings[key]);
                else input.value = data.settings[key];
            }
            initialized = true;
        }
        setSummary(data);
        updateMicrophoneStatus();
        const notice = data.phase === 'monitoring' ? notices[data.notice] : '';
        const message = actionError || data.error_message || notice || states[data.phase];
        setText(el('status'), message + (!actionError && !data.error_message && data.phase === 'monitoring' && data.settings.posture
            ? ` ${postures[data.posture_state]}` : ''));
        el('status').dataset.kind = actionError || data.error_message ? 'error' : '';
        setText(el('training'), data.training
            ? t('Hold the requested pose: ', 'Houd de gevraagde houding vast: ')
                + `${data.training === 'posture' ? t('upright posture', 'rechte zithouding') : label(data.training === 'activate' ? 'open' : data.training)} (${Math.floor(data.progress / 25) * 25}%)` : '');
        el('progress').hidden = !data.training;
        if (el('progress').value !== data.progress) el('progress').value = data.progress;
        setText(el('guide'), guidance(data));
        const hands = data.phase === 'monitoring' && data.hands.length > 1
            ? ` (${data.hands.map((hand) => `${sides[hand.side] || sides.Hand}: ${label(hand.gesture)}`).join(', ')})` : '';
        const scanExpired = scanNeedsRestart(data);
        const scanStatus = scanExpired ? t('scan again after starting', 'opnieuw scannen na het starten')
            : data.gesture_ready ? t('ready', 'klaar') : t('not yet done', 'nog niet gedaan');
        const recognized = data.phase === 'monitoring' ? label(data.gesture) : t('unavailable', 'niet beschikbaar');
        setText(el('recognition'), `${t('Hand scan', 'Handscan')}: ${scanStatus} | ${t('Recognized', 'Herkend')}: ${recognized}${hands}`);
        const last = data.actions ? actionName(data.last_action, data.settings.swipe_action) : '';
        const actionState = data.armed ? t('Actions ON.', 'Acties AAN.')
            : data.phase === 'monitoring' && data.settings.gestures ? t('Practice mode: no gesture actions.', 'Oefenstand: geen gebaaracties.')
            : t('Gesture actions are off.', 'Gebaaracties staan uit.');
        setText(el('action'), actionState
            + ` ${t('Actions sent', 'Acties verstuurd')}: ${data.actions}`
            + (last ? ` | ${t('Last action', 'Laatste actie')}: ${last}.` : '')
            + (data.muted_by_echo ? t(' Echo last muted the selected microphone; unmute explicitly.', ' Echo heeft de gekozen microfoon gemutet; zet deze zelf weer aan.') : ''));
        draw(data.points, data.hands, data.training);
        el('preview-placeholder').hidden = Boolean(data.points.pose.length || data.points.hand.length);
        setText(el('preview-message'), data.phase === 'monitoring'
            ? t('Waiting for visible landmarks', 'Wachten op herkenningspunten')
            : t('Your hand sketch appears here', 'Hier verschijnt je handschets'));
        const measured = Number.isFinite(data.fps) && Number.isFinite(data.processing_ms);
        setText(el('performance'), data.phase !== 'monitoring' ? '' : measured
            ? `${t('Recognition', 'Herkenning')}: ${data.fps.toFixed(1)} fps | ${t('Processing', 'Verwerking')}: ${data.processing_ms.toFixed(0)} ms`
            : t('Restart Echo to see the processing speed.', 'Herstart Echo om het verwerkingstempo te zien.'));
        if (lastAlerts !== null && data.alerts > lastAlerts && 'Notification' in window && Notification.permission === 'granted') {
            new Notification('Echo', {body: reminder, tag: 'echo-posture'});
        }
        lastAlerts = data.alerts;
        controls();
    }

    async function request(action, body) {
        const response = await fetch(`/api/camera-assistent/${action}`, {
            method: body === undefined ? 'GET' : 'POST',
            headers: body === undefined ? {'X-Echo-UI-Language': nl ? 'nl' : 'en'}
                : {'Content-Type': 'application/json', 'X-Echo-Presence-Token': token, 'X-Echo-UI-Language': nl ? 'nl' : 'en'},
            body: body === undefined ? undefined : JSON.stringify(body),
            cache: 'no-store', signal: AbortSignal.timeout(8000),
        });
        let data;
        try {
            data = await response.json();
        } catch (error) {
            if (!(error instanceof SyntaxError)) throw error;
            throw new ServerResponseError(`${t('Unexpected response from Echo', 'Onverwacht antwoord van Echo')} (HTTP ${response.status}).`);
        }
        if (!response.ok || !data || data.status !== 'success') {
            throw new ServerResponseError(data && typeof data.message === 'string' && data.message.trim()
                ? data.message : `${t('Echo rejected the request', 'Echo heeft het verzoek geweigerd')} (HTTP ${response.status}).`);
        }
        return data;
    }

    function failure(error) {
        online = false;
        setSummary(null);
        const detail = error instanceof ServerResponseError ? error.message
            : `${t('Connection error', 'Verbindingsfout')}: ${error.message}`;
        setText(el('status'), `${detail} ${t('Status uncertain; monitoring may still be active.', 'Status onzeker; bewaking kan nog actief zijn.')}`);
        el('status').dataset.kind = 'error';
        setText(el('guide'), error instanceof ServerResponseError
            ? t('Echo could not provide the camera status. Monitoring may still be active.',
                'Echo kon de camerastatus niet ophalen. Bewaking kan nog actief zijn.')
            : t('Echo is unreachable. Check the connection; the camera may still be active.',
                'Echo is niet bereikbaar. Controleer de verbinding; de camera kan nog actief zijn.'));
        setText(el('training'), '');
        setText(el('recognition'), t('Hand scan status unknown.', 'Handscanstatus onbekend.'));
        setText(el('action'), t('Gesture action status unknown.', 'Status van gebaaracties onbekend.'));
        setText(el('performance'), '');
        el('progress').hidden = true;
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        el('preview-placeholder').hidden = false;
        setText(el('preview-message'), t('Camera status unknown', 'Camerastatus onbekend'));
        controls();
    }

    async function change(action, data = {}) {
        if (busy) return;
        busy = true;
        revision++;
        actionError = '';
        controls();
        try { render((await request(action, data)).camera); }
        catch (error) {
            actionError = error instanceof ServerResponseError ? error.message
                : `${t('Request failed', 'Verzoek mislukt')}: ${error.message}`;
            if (error instanceof ServerResponseError) {
                setSummary(null);
                setText(el('status'), actionError);
                el('status').dataset.kind = 'error';
                setText(el('guide'), t('Echo rejected the action. Checking the current status...',
                    'Echo heeft de actie geweigerd. De huidige status wordt gecontroleerd...'));
                try { render((await request('status')).camera); }
                catch (statusError) { failure(statusError); }
            } else {
                failure(error);
            }
        }
        finally { busy = false; controls(); }
    }

    async function poll() {
        const started = performance.now();
        const version = revision;
        if (!busy) {
            try {
                const data = await request('status');
                if (version === revision) render(data.camera);
            } catch (error) { if (version === revision) failure(error); }
        }
        const interval = online && current && current.running && !document.hidden ? 50 : 1000;
        setTimeout(poll, Math.max(0, interval - (performance.now() - started)));
    }

    el('form').addEventListener('submit', (event) => {
        event.preventDefault();
        if (el('start').disabled || !el('form').reportValidity()) return;
        if (!el('posture').checked && !el('gestures').checked) {
            actionError = missingFeatures;
            el('settings').open = true;
            setText(el('status'), actionError);
            el('status').dataset.kind = 'error';
            el('gestures').focus();
            return;
        }
        const data = {};
        for (const [key, id] of Object.entries(fields)) {
            const input = el(id);
            data[key] = input.type === 'checkbox' ? input.checked : input.type === 'number' ? Number(input.value) : input.value;
        }
        change('start', data);
    });
    el('form').addEventListener('invalid', (event) => {
        const section = event.target.closest('details');
        if (section) section.open = true;
    }, true);
    el('consent').addEventListener('change', controls);
    for (const id of ['posture', 'gestures']) {
        el(id).addEventListener('change', () => {
            if (actionError === missingFeatures && (el('posture').checked || el('gestures').checked)) {
                actionError = '';
                if (current && online) render(current);
            }
            updateMicrophoneStatus();
            controls();
        });
    }
    el('microphone').addEventListener('change', () => {
        microphoneEdited = true;
        updateMicrophoneStatus();
        controls();
    });
    el('stop').addEventListener('click', () => change('stop'));
    el('arm').addEventListener('click', () => change('arm', {enabled: true}));
    el('disarm').addEventListener('click', () => change('arm', {enabled: false}));
    el('unmute').addEventListener('click', () => change('unmute'));
    document.querySelectorAll('[data-train]').forEach((button) => button.addEventListener('click', () => change('train', {target: button.dataset.train})));
    el('notifications').addEventListener('click', async () => {
        try {
            if (!('Notification' in window)) throw new Error(t('Desktop notifications are unavailable in this browser.', 'Bureaubladmeldingen zijn niet beschikbaar in deze browser.'));
            const permission = await Notification.requestPermission();
            el('notification-status').textContent = permission === 'granted'
                ? t('Desktop reminders enabled while this page stays open.', 'Bureaubladmeldingen actief zolang deze pagina openblijft.')
                : t('Permission not granted. Reminders remain visible in Echo.', 'Geen toestemming. Herinneringen blijven zichtbaar in Echo.');
        } catch (error) { el('notification-status').textContent = error.message; }
    });
    async function refreshMicrophones() {
        if (microphoneLoading) return;
        microphoneLoading = true;
        microphoneMessage = t('Loading microphones...', 'Microfoonlijst laden...');
        updateMicrophoneStatus();
        controls();
        try {
            const data = await request('microphones');
            if (!Array.isArray(data.microphones)
                || data.microphones.some((device) => !device || typeof device.id !== 'string' || typeof device.name !== 'string')) {
                throw new ServerResponseError(t('Invalid microphone list.', 'Ongeldige microfoonlijst.'));
            }
            const select = el('microphone');
            const selected = current && (current.running || !microphoneEdited) ? current.settings.microphone : select.value;
            const options = [select.options[0]];
            const ids = new Set([options[0].value]);
            for (const device of data.microphones) {
                if (!ids.has(device.id)) {
                    options.push(new Option(device.name, device.id));
                    ids.add(device.id);
                }
            }
            select.replaceChildren(...options);
            selectMicrophone(selected);
            microphoneMessage = '';
        } catch (error) {
            microphoneMessage = `${t('Could not load microphones', 'Microfoonlijst kon niet worden geladen')}: ${error.message}. `
                + t('Open settings and refresh the list to try again.', 'Open de instellingen en ververs de lijst om opnieuw te proberen.');
        } finally {
            microphoneLoading = false;
            updateMicrophoneStatus();
            controls();
        }
    }
    el('refresh-microphones').addEventListener('click', refreshMicrophones);
    poll();
    refreshMicrophones();
})();
