(() => {
    const body = document.body;
    const viewerRole = body.dataset.userRole || "";
    async function api(path, options = {}) {
        const headers = { ...(options.headers || {}) };
        if (options.body && !(options.body instanceof FormData)) {
            headers["Content-Type"] = "application/json";
        }
        const response = await fetch(path, {
            credentials: "same-origin",
            ...options,
            headers,
        });
        const payload = await response.json().catch(() => ({}));
        if (!response.ok || payload.status !== "success") {
            throw new Error(payload.message || `Request failed (${response.status})`);
        }
        return payload;
    }

    function formatFileSize(bytes) {
        if (bytes < 1024) return `${bytes} B`;
        return `${(bytes / 1024).toFixed(1)} KB`;
    }

    async function loadAuditLog() {
        const list = document.getElementById("enterpriseAuditLog");
        const status = document.getElementById("enterpriseAuditStatus");
        if (!list || !status) return;
        const actionLabels = {
            company_created: "Bedrijfsomgeving aangemaakt",
            account_created: "Account toegevoegd",
            account_enabled: "Account ingeschakeld",
            account_disabled: "Account uitgeschakeld",
            password_reset: "Wachtwoord gereset",
            password_changed: "Nieuw wachtwoord ingesteld",
            document_uploaded: "Document geupload",
            document_deleted: "Document verwijderd",
        };
        try {
            const data = await api("/api/admin/audit-log");
            list.replaceChildren();
            status.textContent = data.events.length
                ? `Laatste ${data.events.length} activiteiten · maximaal ${data.max_retained_events} worden bewaard.`
                : "Er zijn nog geen beheeractiviteiten.";
            data.events.forEach((eventRecord) => {
                const item = document.createElement("article");
                item.className = "enterprise-list__item";
                const title = document.createElement("strong");
                title.textContent = actionLabels[eventRecord.action] || "Beheeractiviteit";
                const details = document.createElement("p");
                const timestamp = new Date(eventRecord.created_at).toLocaleString();
                details.textContent = `${eventRecord.actor_username} · ${eventRecord.target} · ${timestamp}`;
                item.append(title, details);
                list.appendChild(item);
            });
        } catch (error) {
            showError(status, error);
            list.replaceChildren();
        }
    }

    async function loadCompanyDocuments(list, status, canDelete) {
        if (!list || !status) return;
        try {
            const data = await api("/api/company-knowledge/documents");
            list.replaceChildren();
            if (!data.documents.length) {
                status.textContent = "Er staan nog geen bedrijfsdocumenten in deze omgeving.";
                return;
            }
            status.textContent = `${data.documents.length} van maximaal ${data.max_documents} documenten.`;
            data.documents.forEach((docRecord) => {
                const item = document.createElement("article");
                item.className = "enterprise-list__item";
                const name = document.createElement("strong");
                name.textContent = docRecord.name;
                const details = document.createElement("p");
                const updated = new Date(docRecord.updated_at).toLocaleString();
                details.textContent = `${formatFileSize(docRecord.size_bytes)} · gewijzigd ${updated}`;
                item.append(name, details);
                if (canDelete) {
                    const remove = document.createElement("button");
                    remove.className = "panel-action enterprise-user-status";
                    remove.type = "button";
                    remove.textContent = "Document verwijderen";
                    remove.addEventListener("click", async () => {
                        if (!window.confirm(`Weet je zeker dat je ${docRecord.name} wilt verwijderen?`)) return;
                        remove.disabled = true;
                        try {
                            await api(`/api/company-knowledge/documents/${docRecord.name.split("/").map(encodeURIComponent).join("/")}`, {
                                method: "DELETE",
                            });
                            await loadCompanyDocuments(list, status, canDelete);
                            await loadAuditLog();
                        } catch (error) {
                            status.textContent = error.message;
                            remove.disabled = false;
                        }
                    });
                    item.appendChild(remove);
                }
                list.appendChild(item);
            });
        } catch (error) {
            showError(status, error);
        }
    }

    function showError(element, error) {
        if (element) {
            element.textContent = error.message || "Er is iets misgegaan.";
        }
    }

    function buildUserListItem(user) {
        const item = document.createElement("article");
        item.className = "enterprise-list__item";
        const label = document.createElement("span");
        label.textContent = `${user.username} · ${user.role} · ${user.enabled ? "actief" : "uitgeschakeld"}`;
        item.appendChild(label);
        const canManage = (viewerRole === "superadmin" && user.role !== "superadmin")
            || (viewerRole === "company_admin" && user.role === "member");
        if (canManage) {
            const button = document.createElement("button");
            button.className = "panel-action enterprise-user-status";
            button.type = "button";
            button.textContent = user.enabled ? "Account uitschakelen" : "Account inschakelen";
            button.addEventListener("click", async () => {
                button.disabled = true;
                try {
                    await api(`/api/admin/users/${encodeURIComponent(user.id)}/status`, {
                        method: "PATCH",
                        body: JSON.stringify({ enabled: !user.enabled }),
                    });
                    user.enabled = !user.enabled;
                    label.textContent = `${user.username} · ${user.role} · ${user.enabled ? "actief" : "uitgeschakeld"}`;
                    button.textContent = user.enabled ? "Account uitschakelen" : "Account inschakelen";
                    await loadAuditLog();
                } catch (error) {
                    label.textContent = error.message;
                } finally {
                    button.disabled = false;
                }
            });
            item.appendChild(button);

            const resetButton = document.createElement("button");
            resetButton.className = "panel-action enterprise-user-status";
            resetButton.type = "button";
            resetButton.textContent = "Wachtwoord resetten";
            resetButton.addEventListener("click", async () => {
                if (!window.confirm(`Een tijdelijk wachtwoord maken voor ${user.username}? Alle bestaande sessies worden afgemeld.`)) return;
                resetButton.disabled = true;
                try {
                    const data = await api(`/api/admin/users/${encodeURIComponent(user.id)}/password-reset`, {
                        method: "POST",
                        body: JSON.stringify({}),
                    });
                    let temporaryPassword = item.querySelector(".enterprise-temporary-password");
                    if (!temporaryPassword) {
                        temporaryPassword = document.createElement("p");
                        temporaryPassword.className = "enterprise-temporary-password";
                        item.appendChild(temporaryPassword);
                    }
                    temporaryPassword.textContent = `Eenmalig tijdelijk wachtwoord (geef dit rechtstreeks door): ${data.temporary_password}`;
                    await loadAuditLog();
                } catch (error) {
                    label.textContent = error.message;
                } finally {
                    resetButton.disabled = false;
                }
            });
            item.appendChild(resetButton);
        }
        return item;
    }

    async function refreshMetrics() {
        const status = document.getElementById("enterpriseMetricsStatus");
        const values = document.getElementById("enterpriseMetricsValues");
        if (!status || !values) return;
        try {
            const data = await api("/api/company-knowledge/metrics");
            const percentage = data.positive_feedback_percent === null
                ? "nog geen beoordelingen"
                : `${data.positive_feedback_percent}% positief (${data.feedback_count} beoordelingen)`;
            values.textContent = `${data.total_questions} vragen · ${data.answered} beantwoord · ${data.no_sources} zonder bron · ${data.model_unavailable + data.model_error} modelproblemen · ${percentage}`;
            status.textContent = "Lokale cijfers voor deze bedrijfsomgeving; vraag- en antwoordtekst wordt niet opgeslagen.";
        } catch (error) {
            showError(status, error);
            values.textContent = "";
        }
    }

    const refreshButton = document.getElementById("enterpriseMetricsRefresh");
    if (refreshButton) refreshButton.addEventListener("click", () => void refreshMetrics());

    const questionForm = document.getElementById("enterpriseQuestionForm");
    if (questionForm) {
        const status = document.getElementById("enterpriseQuestionStatus");
        const answer = document.getElementById("enterpriseAnswer");
        const feedback = document.getElementById("enterpriseFeedback");
        questionForm.addEventListener("submit", async (event) => {
            event.preventDefault();
            const question = document.getElementById("enterpriseQuestion").value.trim();
            status.textContent = "Echo zoekt in de documenten van jouw bedrijf...";
            answer.textContent = "";
            feedback.replaceChildren();
            feedback.hidden = true;
            try {
                const data = await api("/api/company-knowledge/query", {
                    method: "POST",
                    body: JSON.stringify({ question }),
                });
                answer.textContent = data.answer;
                status.textContent = data.metrics_available
                    ? "Antwoord gegenereerd."
                    : "Antwoord gegenereerd, maar kwaliteitsmeting kon niet worden opgeslagen.";
                if (data.feedback_id) {
                    feedback.hidden = false;
                    const prompt = document.createElement("span");
                    prompt.textContent = "Was dit antwoord nuttig?";
                    feedback.appendChild(prompt);
                    [
                        ["positive", "Ja"],
                        ["negative", "Nee"],
                    ].forEach(([rating, label]) => {
                        const button = document.createElement("button");
                        button.className = "company-knowledge-feedback__button";
                        button.type = "button";
                        button.textContent = label;
                        button.addEventListener("click", async () => {
                            button.disabled = true;
                            try {
                                await api("/api/company-knowledge/feedback", {
                                    method: "POST",
                                    body: JSON.stringify({ feedback_id: data.feedback_id, rating }),
                                });
                                feedback.textContent = "Bedankt voor je feedback.";
                                void refreshMetrics();
                            } catch (error) {
                                button.disabled = false;
                                prompt.textContent = error.message;
                            }
                        });
                        feedback.appendChild(button);
                    });
                }
                void refreshMetrics();
            } catch (error) {
                showError(status, error);
            }
        });
        void refreshMetrics();
        void loadCompanyDocuments(
            document.getElementById("enterpriseDocumentsList"),
            document.getElementById("enterpriseDocumentsStatus"),
            false,
        );
        void loadAuditLog();
    }

    const companyForm = document.getElementById("createCompanyForm");
    if (companyForm) {
        const status = document.getElementById("createCompanyStatus");
        const list = document.getElementById("companyList");
        async function loadCompanies() {
            try {
                const data = await api("/api/admin/companies");
                list.replaceChildren();
                data.companies.forEach((company) => {
                    const item = document.createElement("article");
                    item.className = "enterprise-list__item";
                    const title = document.createElement("strong");
                    title.textContent = company.name;
                    const details = document.createElement("p");
                    details.textContent = `ID: ${company.id} · ${company.user_count} accounts · documentenmap: ${company.documents_directory}`;
                    const usersButton = document.createElement("button");
                    usersButton.className = "panel-action";
                    usersButton.type = "button";
                    usersButton.textContent = "Accounts tonen";
                    const users = document.createElement("div");
                    users.className = "enterprise-list";
                    usersButton.addEventListener("click", async () => {
                        usersButton.disabled = true;
                        try {
                            const data = await api(`/api/admin/users?company_id=${encodeURIComponent(company.id)}`);
                            users.replaceChildren(...data.users.map(buildUserListItem));
                            usersButton.textContent = "Accounts vernieuwen";
                        } catch (error) {
                            showError(status, error);
                        } finally {
                            usersButton.disabled = false;
                        }
                    });
                    item.append(title, details, usersButton, users);
                    list.appendChild(item);
                });
            } catch (error) {
                showError(status, error);
            }
        }
        companyForm.addEventListener("submit", async (event) => {
            event.preventDefault();
            const form = new FormData(companyForm);
            const values = Object.fromEntries(form.entries());
            status.textContent = "Bedrijfsomgeving wordt aangemaakt...";
            try {
                const data = await api("/api/admin/companies", {
                    method: "POST",
                    body: JSON.stringify(values),
                });
                companyForm.reset();
                status.textContent = `Bedrijf ${data.company.name} aangemaakt. Eerste beheerder: ${data.admin.username}. Documentenmap: ${data.documents_directory}`;
                await loadCompanies();
            } catch (error) {
                showError(status, error);
            }
        });
        void loadCompanies();
    }

    const userForm = document.getElementById("createUserForm");
    if (userForm) {
        const status = document.getElementById("createUserStatus");
        const list = document.getElementById("userList");
        async function loadUsers() {
            try {
                const data = await api("/api/admin/users");
                list.replaceChildren();
                data.users.forEach((user) => {
                    list.appendChild(buildUserListItem(user));
                });
            } catch (error) {
                showError(status, error);
            }
        }
        userForm.addEventListener("submit", async (event) => {
            event.preventDefault();
            const values = Object.fromEntries(new FormData(userForm).entries());
            status.textContent = "Account wordt aangemaakt...";
            try {
                await api("/api/admin/users", {
                    method: "POST",
                    body: JSON.stringify(values),
                });
                userForm.reset();
                status.textContent = "Medewerker toegevoegd aan jouw bedrijfsomgeving.";
                await loadUsers();
                await loadAuditLog();
            } catch (error) {
                showError(status, error);
            }
        });
        void loadUsers();
    }

    const uploadForm = document.getElementById("uploadCompanyDocumentForm");
    if (uploadForm) {
        const status = document.getElementById("companyDocumentsStatus");
        const list = document.getElementById("companyDocumentsList");
        uploadForm.addEventListener("submit", async (event) => {
            event.preventDefault();
            const file = document.getElementById("companyDocumentFile").files[0];
            if (!file) return;
            status.textContent = "Document wordt gecontroleerd en geupload...";
            const formData = new FormData();
            formData.append("document", file);
            try {
                const data = await api("/api/company-knowledge/documents", {
                    method: "POST",
                    body: formData,
                });
                status.textContent = `${data.document.name} is toegevoegd (${formatFileSize(data.document.size_bytes)}).`;
                uploadForm.reset();
                await loadCompanyDocuments(list, status, true);
                await loadAuditLog();
            } catch (error) {
                showError(status, error);
            }
        });
        void loadCompanyDocuments(list, status, true);
    }

    const auditRefresh = document.getElementById("enterpriseAuditRefresh");
    if (auditRefresh) {
        auditRefresh.addEventListener("click", () => void loadAuditLog());
    }
})();
