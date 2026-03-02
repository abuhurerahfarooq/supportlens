let traces = [];
let selectedCategory = "";

const API_BASE = "/api";

// Chat toggle
const chatPanel = document.getElementById('chatPanel');
const closeBtn = document.getElementById('closeChatBtn');
const openBtn = document.getElementById('openChatBtn');

closeBtn.addEventListener('click', () => {
    chatPanel.classList.add('hidden');
    openBtn.style.display = 'block';
});

openBtn.addEventListener('click', () => {
    chatPanel.classList.remove('hidden');
    openBtn.style.display = 'none';
});

document.addEventListener("DOMContentLoaded", () => {
    loadTraces();
    setupCategoryDropdown();

    document.getElementById("sendBtn").addEventListener("click", sendMessage);
    document.getElementById("chatInput").addEventListener("keypress", e => {
        if (e.key === "Enter") sendMessage();
    });
});


// =============================
// Send Chat Message
// =============================
async function sendMessage() {
    const input = document.getElementById("chatInput");
    const message = input.value.trim();
    if (!message) return;

    appendChat("You", message);
    input.value = "";

    try {
        const chatRes = await fetch(`${API_BASE}/chat`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message })
        });

        const chatData = await chatRes.json();
        appendChat("Bot", chatData.bot_response);

        const traceRes = await fetch(`${API_BASE}/traces`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                user_message: chatData.user_message,
                bot_response: chatData.bot_response
            })
        });

        const traceData = await traceRes.json();

        const newTrace = {
            timestamp: new Date(traceData.timestamp).toLocaleString(),
            user: traceData.user_message,
            bot: traceData.bot_response,
            category: traceData.category,
            response_time: traceData.response_time_ms
        };

        if (!selectedCategory || selectedCategory === newTrace.category) {
            traces.unshift(newTrace);
        }

        renderTable();
        renderCategoryBreakdown(selectedCategory);

    } catch (err) {
        console.error("Error:", err);
    }
}


// =============================
// Append Chat Messages (Styled)
// =============================
function appendChat(sender, text) {
    const container = document.getElementById("chatMessages");

    const div = document.createElement("div");
    div.className = sender === "You" ? "chat-user" : "chat-bot";
    div.innerHTML = `<strong>${sender}:</strong> ${text}`;

    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
}


// =============================
// Load Traces
// =============================
async function loadTraces(category = "") {
    try {
        let url = `${API_BASE}/traces`;
        if (category) url += "?category=" + encodeURIComponent(category);

        const res = await fetch(url);
        const data = await res.json();

        traces = data.map(t => ({
            timestamp: new Date(t.timestamp).toLocaleString(),
            user: t.user_message,
            bot: t.bot_response,
            category: t.category,
            response_time: t.response_time_ms
        }));

        renderTable();
        renderCategoryBreakdown(category);

    } catch (err) {
        console.error("Error loading traces:", err);
    }
}


// =============================
// Render Table
// =============================
function renderTable() {
    const tbody = document.querySelector("#traces tbody");
    tbody.innerHTML = "";

    traces.forEach((t) => {
        const safeClass = formatCategoryClass(t.category);

        const row = document.createElement("tr");
        row.classList.add("clickable-row");

        row.innerHTML = `
            <td>${t.timestamp}</td>
            <td>${truncate(t.user)}</td>
            <td>${truncate(t.bot)}</td>
            <td><span class="badge ${safeClass}">${t.category}</span></td>
            <td>${t.response_time} ms</td>
        `;

        row.addEventListener("click", () => toggleDetails(row, t));

        tbody.appendChild(row);
    });
}

function toggleDetails(row, trace) {

    // If next row is already detail → remove it
    if (row.nextSibling && row.nextSibling.classList?.contains("detail-row")) {
        row.nextSibling.remove();
        return;
    }

    const detailRow = document.createElement("tr");
    detailRow.classList.add("detail-row");

    detailRow.innerHTML = `
        <td colspan="5">
            <div class="trace-detail">
                <strong>Full User Message:</strong>
                <p>${trace.user}</p>

                <strong>Full Bot Response:</strong>
                <p>${trace.bot}</p>
            </div>
        </td>
    `;

    row.parentNode.insertBefore(detailRow, row.nextSibling);
}

// =============================
// Utility: Format Category Class
// Converts "Account Access" → "AccountAccess"
// =============================
function formatCategoryClass(category) {
    return category.replace(/\s/g, '');
}


// =============================
// Truncate Text
// =============================
function truncate(text) {
    return text.length > 50 ? text.substring(0, 50) + "..." : text;
}


// =============================
// Render Category Breakdown
// =============================
async function renderCategoryBreakdown(activeCategory = "") {
    const container = document.getElementById("categoryBreakdown");

    try {
        const res = await fetch(`${API_BASE}/analytics`);
        const data = await res.json();

        container.innerHTML = "";

        const allCard = document.createElement("div");
        allCard.className = `category-card all-category${activeCategory ? "" : " active"}`;
        allCard.innerHTML = `
            <div class="category-card-inner">
                <div class="category-title-row">
                    <span class="category-icon" aria-hidden="true">${getCategoryIcon("All")}</span>
                    <h4>All</h4>
                </div>
                <p class="category-metric">${data.total_traces || 0} traces</p>
                <small class="category-submetric">${Math.round(data.average_response_time_ms || 0)} ms avg response</small>
            </div>
        `;
        allCard.addEventListener("click", () => applyCategoryFilter(""));
        container.appendChild(allCard);

        Object.entries(data.breakdown).forEach(([category, info]) => {
            const div = document.createElement("div");

            const isActive = activeCategory === category ? " active" : "";
            div.className = `category-card ${formatCategoryClass(category)}${isActive}`;

            div.innerHTML = `
                <div class="category-card-inner">
                    <div class="category-title-row">
                        <span class="category-icon" aria-hidden="true">${getCategoryIcon(category)}</span>
                        <h4>${category}</h4>
                    </div>
                    <p class="category-metric">${info.count} traces</p>
                    <small class="category-submetric">${Math.round(info.average_response_time_ms || 0)} ms avg response</small>
                </div>
            `;

            div.addEventListener("click", () => applyCategoryFilter(category));
            container.appendChild(div);
        });

    } catch (err) {
        console.error("Error loading breakdown:", err);
    }
}


function setupCategoryDropdown() {
    const dropdown = document.getElementById("categoryDropdown");
    if (!dropdown) return;

    const selected = dropdown.querySelector(".selected");
    const options = dropdown.querySelector(".options");
    if (!selected || !options) return;

    selected.addEventListener("click", () => {
        options.style.display = options.style.display === "flex" ? "none" : "flex";
    });

    options.querySelectorAll("div").forEach(option => {
        option.addEventListener("click", () => {
            const value = option.dataset.value || "";
            selected.textContent = option.textContent;
            options.style.display = "none";
            applyCategoryFilter(value);
        });
    });

    document.addEventListener("click", e => {
        if (!dropdown.contains(e.target)) {
            options.style.display = "none";
        }
    });
}

function applyCategoryFilter(category) {
    selectedCategory = category;
    syncDropdownSelection(category);
    loadTraces(category);
}

function syncDropdownSelection(category) {
    const dropdown = document.getElementById("categoryDropdown");
    if (!dropdown) return;

    const selected = dropdown.querySelector(".selected");
    const options = dropdown.querySelector(".options");
    if (!selected || !options) return;

    const selectedOption = [...options.querySelectorAll("div")]
        .find(option => (option.dataset.value || "") === category);

    selected.textContent = selectedOption ? selectedOption.textContent : (category || "All");
}

function getCategoryIcon(category) {
    const icons = {
        "All": "&#128202;",
        "Billing": "&#128179;",
        "Refund": "&#128184;",
        "Account Access": "&#128274;",
        "Cancellation": "&#10060;",
        "General Inquiry": "&#128172;"
    };
    return icons[category] || "&#128172;";
}
