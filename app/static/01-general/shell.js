// ============================================================
// Mini-Apps registry. To add a new mini-app:
//   1. Create a new folder under app/static/  (e.g. 03-myapp/)
//   2. Add an entry below pointing to its main HTML file.
// ============================================================
const APPS = [
    {
        id: "excel-processor",
        title: "Excel Processor",
        icon: "\u{1F4C8}",   // 📈
        url: "/02-excelprocessor/table.html",
    },
    // Example for the future:
    // { id: "another-app", title: "Another Mini-App", icon: "\u{1F680}", url: "/03-anotherapp/index.html" },
];

// ============================================================
// Wire up the sidebar
// ============================================================
const sidebarList = document.getElementById("sidebar-list");
const sidebar = document.getElementById("sidebar");
const toggleBtn = document.getElementById("toggle-sidebar");
const frame = document.getElementById("app-frame");
const titleEl = document.getElementById("current-app-title");

// Build sidebar items
APPS.forEach((app) => {
    const li = document.createElement("li");
    li.className = "sidebar-item";
    li.dataset.appId = app.id;
    li.innerHTML = `<span class="icon">${app.icon}</span><span>${app.title}</span>`;
    li.addEventListener("click", () => loadApp(app));
    sidebarList.appendChild(li);
});

function loadApp(app) {
    document.querySelectorAll(".sidebar-item").forEach((el) =>
        el.classList.toggle("active", el.dataset.appId === app.id),
    );
    frame.src = app.url;
    titleEl.textContent = app.title;
    document.title = `${app.title} | Mini-Apps`;
}

// Sidebar collapse toggle (persisted)
const COLLAPSED_KEY = "sidebar-collapsed";
if (localStorage.getItem(COLLAPSED_KEY) === "1") sidebar.classList.add("collapsed");

toggleBtn.addEventListener("click", () => {
    sidebar.classList.toggle("collapsed");
    localStorage.setItem(COLLAPSED_KEY, sidebar.classList.contains("collapsed") ? "1" : "0");
});

// Auto-load the first app on startup
if (APPS.length > 0) loadApp(APPS[0]);
