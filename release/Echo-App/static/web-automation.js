(() => {
    'use strict';
    const $ = id => document.getElementById(`web-${id}`);
    const nl = document.body.dataset.language === 'nl';
    const text = (en, dutch) => nl ? dutch : en;
    const token = document.querySelector('meta[name="echo-web-token"]').content;
    const roles = {
        add_to_cart: text('Add-to-cart button', 'Winkelwagen-knop'), checkout: text('Checkout button', 'Afrekenknop'),
        stock_indicator: text('Stock label', 'Voorraadlabel'), price: text('Price', 'Prijs'),
    };
    const availability = {
        in_stock: text('In stock', 'Op voorraad'), out_of_stock: text('Sold out', 'Uitverkocht'),
        conflict: text('Signals disagree', 'Signalen spreken elkaar tegen'), unknown: text('Unknown', 'Onbekend'), '': '-',
    };
    const modes = { notify: text('Notify', 'Melden'), cart: text('Add to cart', 'In winkelwagen'), checkout: text('Cart + checkout', 'Winkelwagen + kassa'),
        order: text('Automatic order', 'Automatisch bestellen'), reserve: text('Automatic reservation', 'Automatisch reserveren') };
    const siteStatus = { exists: text('name exists', 'naam bestaat'), not_found: text('not found', 'niet gevonden'), unknown: text('unknown', 'onbekend') };
    const alertKinds = new Set(['restock', 'action_done', 'action_failed', 'blocked', 'failing', 'order_confirmed', 'reservation_confirmed', 'transaction_uncertain']);
    const date = value => value ? new Date(value * 1000).toLocaleString() : '-';
    const money = value => typeof value === 'number' ? value.toFixed(2) : '-';
    let state = null, osint = null, busy = false, initialized = false, lastEvent = 0;
    const openHistory = new Set();

    async function call(path, data, timeout = 35000) {
        const response = await fetch(`/api/webautomatisering/${path}`, {
            method: data === undefined ? 'GET' : 'POST',
            headers: { 'Content-Type': 'application/json', 'X-Echo-Web-Token': token },
            body: data === undefined ? undefined : JSON.stringify(data),
            cache: 'no-store', signal: AbortSignal.timeout(timeout),
        });
        let result;
        try {
            result = await response.json();
        } catch (error) {
            throw new Error(`HTTP ${response.status}`);
        }
        if (!response.ok || result.status !== 'success') throw new Error(result.message || `HTTP ${response.status}`);
        return result;
    }

    const element = (tag, content, className) => {
        const node = document.createElement(tag);
        if (content !== undefined) node.textContent = content;
        if (className) node.className = className;
        return node;
    };

    function button(label, handler, primary = false) {
        const node = element('button', label, primary ? 'primary-button' : 'secondary-button');
        node.type = 'button';
        node.disabled = busy;
        node.onclick = handler;
        return node;
    }

    async function perform(action) {
        if (busy) return;
        busy = true;
        $('error').textContent = '';
        render();
        try {
            const result = await action();
            if (result?.web) state = result.web;
            if (result?.osint) osint = result.osint;
            return result;
        } catch (error) {
            $('error').textContent = text('Action failed: ', 'Actie mislukt: ') + error.message;
        } finally {
            busy = false;
            render();
        }
    }

    function renderStatus() {
        const running = state.running;
        $('status').textContent = !state.available
            ? text('Playwright is not installed.', 'Playwright is niet geinstalleerd.')
            : `${running ? text('Monitor on.', 'Bewaking aan.') : text('Monitor off.', 'Bewaking uit.')}` +
              `${state.active ? text(' Checking now...', ' Nu aan het controleren...') : ''}` +
              Object.entries(state.errors).map(([source, error]) => `\n${source}: ${error}`).join('');
        $('start').disabled = busy || running || !$('consent').checked || !state.available;
        $('stop').disabled = busy || !running;
        const shop = state.shop;
        $('shop-status').textContent = shop.open
            ? `${text('Shop window open', 'Winkelvenster open')}${shop.host ? `: ${shop.host}` : ''}${shop.busy ? text(' (working...)', ' (bezig...)') : ''}`
            : text('Shop window closed.', 'Winkelvenster gesloten.') + (shop.error ? `\n${shop.error}` : '');
    }

    function selectorHistory(watch) {
        const details = element('details');
        details.open = openHistory.has(watch.id);
        details.ontoggle = () => { if (details.open) openHistory.add(watch.id); else openHistory.delete(watch.id); };
        details.append(element('summary', text('Selectors and repair history', 'Selectors en herstelgeschiedenis')));
        for (const [role, versions] of Object.entries(watch.selectors)) {
            details.append(element('strong', roles[role] || role));
            const list = element('ul');
            versions.forEach((version, index) => {
                const item = element('li', `v${version.version} ${index === 0 ? text('(active)', '(actief)') : ''} | ${version.selector || text('(text only)', '(alleen tekst)')} | ${version.reason}` +
                    `${version.score !== null ? ` | score ${version.score.toFixed(2)}` : ''} | ${date(version.created)}${version.seen ? ` | "${version.seen}"` : version.text ? ` | "${version.text}"` : ''} `);
                if (index > 0) {
                    item.append(button(text('Roll back', 'Terugzetten'), () => perform(() => call('rollback', { id: watch.id, role, version: version.version }))));
                }
                list.append(item);
            });
            details.append(list);
        }
        return details;
    }

    function renderWatches() {
        $('watches').replaceChildren();
        if (!state.watches.length) $('watches').append(element('li', text('No watches yet.', 'Nog geen watchers.')));
        for (const watch of state.watches) {
            const { config, state: info } = watch;
            const item = element('li');
            item.append(element('strong', `${config.name} - ${modes[config.mode]}${info.paused ? text(' (paused)', ' (gepauzeerd)') : ''}`));
            const lines = [
                config.url,
                `${text('Stock', 'Voorraad')}: ${availability[info.availability] ?? info.availability} | ${text('Price', 'Prijs')}: ${money(info.price)}` +
                    `${config.max_price !== null ? ` (max ${money(config.max_price)})` : ''} | ${text('Status', 'Status')}: ${info.status || '-'}`,
                `${text('Last check', 'Laatste controle')}: ${date(info.last_check)} | ${text('Next', 'Volgende')}: ${info.paused ? '-' : date(info.next_check)}`,
            ];
            for (const [role, element_] of Object.entries(info.elements || {})) {
                lines.push(`${roles[role] || role}: ${element_.status}${element_.label ? ` - "${element_.label}"` : ''}`);
            }
            if (info.last_error) lines.push(`${text('Error', 'Fout')}: ${info.last_error}`);
            if (watch.transaction) lines.push(`${text('Transaction', 'Transactie')}: ${watch.transaction.status} | ${watch.transaction.proof || text('Check the shop: outcome may be unknown. No automatic retry.', 'Controleer de winkel: uitkomst kan onbekend zijn. Geen automatische herhaling.')}`);
            for (const note of info.notes || []) lines.push(note);
            item.append(element('pre', lines.join('\n')));
            const row = element('div', undefined, 'button-row');
            row.append(button(text('Check now (no action)', 'Nu controleren (geen actie)'), () => perform(() => call('check', { id: watch.id }, 90000))));
            row.append(button(text('Edit', 'Bewerken'), () => edit(watch)));
            if (info.paused) {
                row.append(button(text('Resume', 'Hervatten'), () => perform(() => call('resume', { id: watch.id, rearm: false }))));
                row.append(button(text('Resume and allow action again', 'Hervatten en opnieuw actie toestaan'), () => perform(async () => {
                    if (!window.confirm(watch.transaction || ['order', 'reserve'].includes(config.mode)
                        ? text('Check your orders/reservations in the shop first, even if the outcome was unknown. Authorize ONE MORE transaction? You may be charged again.', 'Controleer eerst je bestellingen/reserveringen in de winkel, ook bij onbekende uitkomst. NOG EEN transactie toestaan? Je kunt opnieuw worden belast.')
                        : text('If the product is in stock at the next check, Echo will add it to the cart again. Continue?', 'Als het product bij de volgende controle op voorraad is, legt Echo het opnieuw in de winkelwagen. Doorgaan?'))) return;
                    return call('resume', { id: watch.id, rearm: true });
                })));
            } else {
                row.append(button(text('Pause', 'Pauzeren'), () => perform(() => call('pause', { id: watch.id }))));
            }
            row.append(button(text('Delete', 'Verwijderen'), () => perform(async () => {
                if (!window.confirm(text(`Delete watch "${config.name}"?`, `Watcher "${config.name}" verwijderen?`))) return;
                return call('delete', { id: watch.id });
            })));
            item.append(row, selectorHistory(watch));
            $('watches').append(item);
        }
    }

    function renderEvents() {
        const names = Object.fromEntries(state.watches.map(watch => [watch.id, watch.config.name]));
        $('events').replaceChildren(...state.events.map(event => element('li', `${date(event.created)} - ${names[event.watch_id] || '?'} - ${event.kind}: ${event.summary}`)));
        const newest = state.events.find(event => alertKinds.has(event.kind));
        if (initialized && newest && newest.id > lastEvent && $('desktop').checked && 'Notification' in window && Notification.permission === 'granted') {
            new Notification('Echo', { body: `${names[newest.watch_id] || ''}: ${newest.summary}`, tag: 'echo-web-automation' });
        }
        lastEvent = Math.max(lastEvent, state.events[0]?.id || 0);
    }

    function identifierLines(item) {
        const result = item.result;
        if (!result) return [text('Not checked yet.', 'Nog niet gecontroleerd.')];
        const lines = [`${text('Checked', 'Gecontroleerd')}: ${date(result.checked)}`];
        if (result.status !== 'ok') return [...lines, result.error || result.status];
        if (item.kind === 'username') {
            for (const site of result.sites) lines.push(`${site.site}: ${siteStatus[site.status]} - ${site.url}`);
            return lines;
        }
        lines.push(result.breaches.length
            ? `${result.breaches.length} ${item.kind === 'domain' ? text('breach(es) of this site', 'lek(ken) van deze site') : text('breach(es) found', 'lek(ken) gevonden')}`
            : (item.kind === 'domain' ? text('This site itself is not in HIBP.', 'Deze site zelf staat niet in HIBP.') : text('Good news: not found in any breach.', 'Goed nieuws: in geen enkel lek gevonden.')));
        if (result.new?.length) lines.push(`${text('NEW since last check', 'NIEUW sinds vorige controle')}: ${result.new.join(', ')}`);
        for (const breach of result.breaches) {
            lines.push(`- ${breach.title} (${breach.date})${breach.domain ? ` ${breach.domain}` : ''}: ${breach.data.join(', ')}`);
        }
        if (result.alias_count) lines.push(`${result.alias_count} ${text('address(es) on this domain appear in breaches', 'adres(sen) op dit domein komen voor in lekken')}: ${Object.keys(result.aliases).slice(0, 20).join(', ')}`);
        if (result.paste_count) lines.push(`${result.paste_count} paste(s): ${result.pastes.map(paste => `${paste.source} ${paste.date}`).join(', ')}`);
        return [...lines, ...(result.notes || [])];
    }

    function renderOsint() {
        const sources = { environment: text('Key from HIBP_API_KEY.', 'Sleutel uit HIBP_API_KEY.'), stored: text('Encrypted key stored.', 'Versleutelde sleutel opgeslagen.'), unreadable: text('Stored key unreadable - enter it again.', 'Opgeslagen sleutel onleesbaar - voer hem opnieuw in.'), '': text('No key: only domain-site and password checks are available.', 'Geen sleutel: alleen site- en wachtwoordchecks zijn beschikbaar.') };
        $('key-status').textContent = `${sources[osint.key_source] ?? osint.key_source}${osint.subscription ? ` ${osint.subscription}` : ''}${osint.rpm ? ` (${osint.rpm} RPM)` : ''}`;
        const job = osint.job;
        $('osint-job').textContent = job.running
            ? `${text('Checking', 'Bezig')}: ${job.done}/${job.total}`
            : job.finished ? `${text('Last run', 'Laatste run')}: ${date(job.finished)}${job.new ? ` - ${job.new} ${text('new breach result(s)', 'nieuwe lekresultaten')}` : ''}${job.error ? `\n${job.error}` : ''}` : '';
        const monitor = osint.monitor;
        $('osint-monitor-status').textContent = monitor.enabled
            ? `${text('Breach monitor on, every', 'Lekbewaking aan, elke')} ${monitor.hours} ${text('hours', 'uur')}. ${text('Latest HIBP breach', 'Nieuwste HIBP-lek')}: ${monitor.latest || '-'}${monitor.error ? `\n${monitor.error}` : ''}`
            : text('Breach monitor off.', 'Lekbewaking uit.');
        $('identifiers').replaceChildren();
        for (const item of osint.identifiers) {
            const li = element('li');
            li.append(element('strong', `${item.kind}: ${item.value}`), element('pre', identifierLines(item).join('\n')));
            const row = element('div', undefined, 'button-row');
            row.append(button(text('Check', 'Controleren'), () => perform(() => call('osint/check', { ids: [item.id] }))));
            row.append(button(text('Remove', 'Verwijderen'), () => perform(() => call('osint/remove', { id: item.id }))));
            li.append(row);
            $('identifiers').append(li);
        }
    }

    function render() {
        if (state) {
            renderStatus();
            renderWatches();
            renderEvents();
        }
        if (osint) renderOsint();
        for (const id of ['save', 'osint-add', 'osint-check-all', 'key-save', 'key-verify', 'key-clear', 'password-check', 'osint-monitor-save', 'shop-open', 'shop-close']) {
            $(id).disabled = busy;
        }
    }

    const terms = value => value.split(',').map(term => term.trim()).filter(Boolean);
    const elementFields = { add_to_cart: 'add', stock_indicator: 'stock', price: 'price', checkout: 'checkout' };
    const transactionFields = { button: 'final', item: 'item', quantity: 'quantity', total: 'total', confirmation: 'confirmation' };

    function transactionMode() {
        const enabled = ['order', 'reserve'].includes($('mode').value);
        $('transaction-fields').hidden = !enabled;
        $('transaction-fields').disabled = !enabled;
        $('max-price').required = enabled;
        for (const input of $('transaction-fields').querySelectorAll('input')) input.required = enabled;
        $('transaction-authorized').checked = false;
    }

    function clearForm() {
        $('form').reset();
        $('id').value = '';
        $('interval').value = 300;
        $('form-title').textContent = text('1. New watch', '1. Nieuwe watcher');
        transactionMode();
    }

    function edit(watch) {
        const config = watch.config;
        $('id').value = watch.id;
        $('name').value = config.name;
        $('url').value = config.url;
        $('mode').value = config.mode;
        $('interval').value = config.interval;
        $('max-price').value = config.max_price ?? '';
        $('in-text').value = config.in_stock_text.join(', ');
        $('out-text').value = config.out_of_stock_text.join(', ');
        for (const [role, prefix] of Object.entries(elementFields)) {
            const active = watch.selectors[role]?.[0];
            $(`${prefix}-selector`).value = active ? active.selector : (config.elements[role]?.selector || '');
            $(`${prefix}-text`).value = config.elements[role]?.text || '';
        }
        $('checkout-url').value = config.checkout_url;
        $('authorized').checked = config.authorized;
        transactionMode();
        const transaction = config.transaction;
        $('currency').value = transaction?.currency || 'EUR';
        for (const [role, prefix] of Object.entries(transactionFields)) {
            $(`${prefix}-selector`).value = transaction?.[role]?.selector || '';
            if ($(`${prefix}-text`)) $(`${prefix}-text`).value = transaction?.[role]?.text || '';
        }
        $('form-title').textContent = text(`1. Edit "${config.name}"`, `1. "${config.name}" bewerken`);
        $('form').scrollIntoView({ behavior: 'smooth' });
    }

    function collect() {
        const elements = {};
        for (const [role, prefix] of Object.entries(elementFields)) {
            const selector = $(`${prefix}-selector`).value.trim(), label = $(`${prefix}-text`).value.trim();
            if (selector || label) elements[role] = { selector, text: label };
        }
        const maxPrice = $('max-price').value.trim();
        const watch = {
            name: $('name').value.trim(), url: $('url').value.trim(), mode: $('mode').value,
            interval: Number.parseInt($('interval').value, 10), in_stock_text: terms($('in-text').value),
            out_of_stock_text: terms($('out-text').value), max_price: maxPrice ? Number(maxPrice) : null,
            elements, checkout_url: $('checkout-url').value.trim(), authorized: $('authorized').checked,
        };
        if (['order', 'reserve'].includes(watch.mode)) {
            watch.transaction = { authorized: $('transaction-authorized').checked, currency: $('currency').value };
            for (const [role, prefix] of Object.entries(transactionFields)) {
                watch.transaction[role] = { selector: $(`${prefix}-selector`).value.trim(),
                    text: role === 'quantity' ? '1' : ($(`${prefix}-text`)?.value.trim() || '') };
            }
        }
        return watch;
    }

    $('form').onsubmit = event => {
        event.preventDefault();
        void perform(async () => {
            const watch = collect();
            const confirmation = watch.transaction
                ? text(`Authorize ONE ${watch.mode} for "${watch.transaction.item.text}", quantity 1, total at most ${watch.max_price} ${watch.transaction.currency}? Echo may submit it without asking again when stock returns.`,
                    `EEN ${watch.mode === 'order' ? 'bestelling/betaling' : 'reservering'} van "${watch.transaction.item.text}", aantal 1, totaal maximaal ${watch.max_price} ${watch.transaction.currency} toestaan? Echo mag dit zonder nieuwe vraag uitvoeren zodra er voorraad is.`)
                : text('Echo will prepare the cart/checkout only. You finish any order yourself. Continue?',
                    'Echo bereidt alleen de winkelwagen/kassa voor. Jij rondt een eventuele bestelling zelf af. Doorgaan?');
            if (watch.mode !== 'notify' && !window.confirm(confirmation)) return;
            const result = await call('save', { id: $('id').value, watch });
            clearForm();
            return result;
        });
    };
    $('new').onclick = clearForm;
    $('mode').onchange = transactionMode;
    transactionMode();
    $('consent').onchange = render;
    $('desktop').checked = localStorage.getItem('echo-web-desktop') === '1';
    $('desktop').onchange = () => perform(async () => {
        if ($('desktop').checked && (!('Notification' in window) || await Notification.requestPermission() !== 'granted')) {
            $('desktop').checked = false;
            throw new Error(text('Desktop notification permission was not granted.', 'Geen toestemming voor bureaubladmeldingen.'));
        }
        localStorage.setItem('echo-web-desktop', $('desktop').checked ? '1' : '0');
    });
    $('start').onclick = () => perform(() => call('start', { authorized: $('consent').checked, sound: $('sound').checked }));
    $('stop').onclick = () => perform(() => call('stop', {}));
    $('shop-open').onclick = () => perform(() => call('shop_open', { url: $('shop-url').value.trim() }));
    $('shop-close').onclick = () => perform(() => call('shop_close', {}));

    $('osint-form').onsubmit = event => {
        event.preventDefault();
        void perform(async () => {
            const result = await call('osint/add', { kind: $('osint-kind').value, value: $('osint-value').value, owned: $('osint-owned').checked });
            $('osint-value').value = '';
            $('osint-owned').checked = false;
            return result;
        });
    };
    $('osint-check-all').onclick = () => perform(() => call('osint/check', { ids: [] }));
    $('key-save').onclick = () => perform(async () => {
        const result = await call('osint/set_key', { key: $('key').value.trim() });
        $('key').value = '';
        return result;
    });
    $('key-verify').onclick = () => perform(() => call('osint/verify_key', {}));
    $('key-clear').onclick = () => perform(() => call('osint/clear_key', {}));
    $('osint-monitor-save').onclick = () => perform(() => call('osint/monitor', {
        enabled: $('osint-monitor').checked, hours: Number.parseInt($('osint-hours').value, 10), sound: $('osint-sound').checked,
    }));
    $('password-check').onclick = () => perform(async () => {
        const password = $('password').value;
        $('password').value = '';
        $('password-result').textContent = '';
        if (!password) throw new Error(text('Enter a password.', 'Vul een wachtwoord in.'));
        const digest = await crypto.subtle.digest('SHA-1', new TextEncoder().encode(password));
        const hash = Array.from(new Uint8Array(digest), byte => byte.toString(16).padStart(2, '0')).join('').toUpperCase();
        const { lines } = await call('osint/password_range', { prefix: hash.slice(0, 5) });
        const match = lines.find(line => line.startsWith(`${hash.slice(5)}:`));
        const count = match ? Number(match.split(':')[1]) : 0;
        $('password-result').textContent = count
            ? text(`This password appears ${count.toLocaleString()} times in known leaks. Do not use it anywhere; change it wherever you use it.`, `Dit wachtwoord komt ${count.toLocaleString()} keer voor in bekende lekken. Gebruik het nergens meer en wijzig het overal waar je het gebruikt.`)
            : text('Not found in Pwned Passwords. That is good, but it is no guarantee the password is strong.', 'Niet gevonden in Pwned Passwords. Dat is goed, maar geen garantie dat het wachtwoord sterk is.');
    });

    async function refresh() {
        const result = await call('status');
        state = result.web;
        osint = result.osint;
    }

    async function poll() {
        if (!busy && document.visibilityState === 'visible') {
            try {
                await refresh();
                render();
            } catch (error) {
                $('error').textContent = text('Status unavailable: ', 'Status niet beschikbaar: ') + error.message;
            }
        }
        const fast = state?.active || osint?.job.running || state?.shop.busy;
        window.setTimeout(poll, fast ? 2000 : 6000);
    }

    async function initialize() {
        await perform(async () => {
            await refresh();
            $('sound').checked = state.sound;
            $('osint-monitor').checked = osint.monitor.enabled;
            $('osint-hours').value = osint.monitor.hours;
            $('osint-sound').checked = osint.monitor.sound;
            $('key-link').href = osint.key_page;
            $('dashboard-link').href = osint.dashboard;
            lastEvent = state.events[0]?.id || 0;
        });
        initialized = true;
        window.setTimeout(poll, 6000);
    }

    void initialize();
})();
