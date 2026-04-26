// ============================================================
// Shared logic for the Excel Processor mini-app:
//   - Loads app config from /api/excel/config
//   - Handles MSAL auth (only when provider requires it)
//   - Wraps the API calls (read sheet / update cell)
//   - Exposes window.ExcelApp for the page-specific scripts.
// ============================================================
(function () {
    let msalInstance = null;
    let appConfig = null;

    const loginRequest = {
        scopes: ["Files.ReadWrite", "Sites.ReadWrite.All"],
    };

    async function init() {
        const resp = await fetch("/api/excel/config");
        appConfig = await resp.json();

        if (appConfig.requires_auth) {
            initMsal();
            // Try silent login if there's a cached account
            const accounts = msalInstance.getAllAccounts();
            if (accounts.length > 0) {
                try {
                    await msalInstance.acquireTokenSilent({ ...loginRequest, account: accounts[0] });
                } catch { /* ignored */ }
            }
        }
        return appConfig;
    }

    function initMsal() {
        if (!appConfig.azure_client_id) {
            throw new Error("Azure AD not configured. Set AZURE_CLIENT_ID in .env");
        }
        const authority = appConfig.azure_tenant_id
            ? `https://login.microsoftonline.com/${appConfig.azure_tenant_id}`
            : "https://login.microsoftonline.com/organizations";
        msalInstance = new msal.PublicClientApplication({
            auth: {
                clientId: appConfig.azure_client_id,
                authority,
                redirectUri: window.location.origin,
            },
            cache: { cacheLocation: "sessionStorage" },
        });
    }

    async function getToken() {
        if (!appConfig.requires_auth) return "";
        const accounts = msalInstance.getAllAccounts();
        if (accounts.length === 0) {
            const resp = await msalInstance.loginPopup(loginRequest);
            return resp.accessToken;
        }
        try {
            const resp = await msalInstance.acquireTokenSilent({ ...loginRequest, account: accounts[0] });
            return resp.accessToken;
        } catch {
            const resp = await msalInstance.loginPopup(loginRequest);
            return resp.accessToken;
        }
    }

    async function readSheet() {
        const token = await getToken();
        const params = new URLSearchParams();
        if (appConfig.excel_file_url) params.set("file_url", appConfig.excel_file_url);
        if (appConfig.excel_sheet_name) params.set("sheet_name", appConfig.excel_sheet_name);

        const headers = token ? { Authorization: `Bearer ${token}` } : {};
        const resp = await fetch(`/api/excel/sheet?${params}`, { headers });
        if (!resp.ok) {
            const err = await resp.json().catch(() => ({ detail: resp.statusText }));
            throw new Error(err.detail || resp.statusText);
        }
        return resp.json();
    }

    async function updateCell(cellAddress, value) {
        const token = await getToken();
        const headers = { "Content-Type": "application/json" };
        if (token) headers.Authorization = `Bearer ${token}`;

        const resp = await fetch("/api/excel/cell", {
            method: "PATCH",
            headers,
            body: JSON.stringify({
                file_url: appConfig.excel_file_url,
                sheet_name: appConfig.excel_sheet_name,
                cell_address: cellAddress,
                value,
            }),
        });
        if (!resp.ok) {
            const err = await resp.json().catch(() => ({ detail: resp.statusText }));
            throw new Error(err.detail || resp.statusText);
        }
        return true;
    }

    function escapeHtml(str) {
        const div = document.createElement("div");
        div.appendChild(document.createTextNode(str));
        return div.innerHTML;
    }

    function showToast(msg, type) {
        let toast = document.getElementById("toast");
        if (!toast) {
            toast = document.createElement("div");
            toast.id = "toast";
            document.body.appendChild(toast);
        }
        toast.textContent = msg;
        toast.className = `${type || "info"} show`;
        setTimeout(() => { toast.className = ""; }, 3500);
    }

    window.ExcelApp = {
        init,
        getConfig: () => appConfig,
        readSheet,
        updateCell,
        escapeHtml,
        showToast,
    };
})();
