// DevPulse Dashboard Frontend Logic
let servicesMap = new Map();

document.addEventListener("DOMContentLoaded", () => {
    checkHealth();
    loadServices();
    loadIncidents();

    // Set periodic health check
    setInterval(checkHealth, 15000);

    // Form Event Listeners
    document.getElementById("service-form").addEventListener("submit", handleCreateService);
    document.getElementById("incident-form").addEventListener("submit", handleCreateIncident);
    document.getElementById("refresh-btn").addEventListener("click", () => {
        loadServices();
        loadIncidents();
        checkHealth();
    });
});

async function checkHealth() {
    const healthEl = document.getElementById("system-health");
    const healthText = document.getElementById("health-text");

    try {
        const res = await fetch("/healthz");
        if (res.ok) {
            const data = await res.json();
            healthEl.className = "health-pill healthy";
            healthText.textContent = `System Healthy (DB: ${data.database})`;
        } else {
            healthEl.className = "health-pill unhealthy";
            healthText.textContent = "System Unhealthy";
        }
    } catch (err) {
        healthEl.className = "health-pill unhealthy";
        healthText.textContent = "System Disconnected";
    }
}

async function loadServices() {
    try {
        const res = await fetch("/services");
        if (!res.ok) throw new Error("Failed to load services");
        const services = await res.json();

        servicesMap.clear();
        const listEl = document.getElementById("services-list");
        const selectEl = document.getElementById("incident-service");
        document.getElementById("stat-services").textContent = services.length;

        if (services.length === 0) {
            listEl.innerHTML = '<p class="empty-state">No services registered yet.</p>';
            selectEl.innerHTML = '<option value="">-- Select a Service --</option>';
            return;
        }

        listEl.innerHTML = "";
        selectEl.innerHTML = '<option value="">-- Select a Service --</option>';

        services.forEach(srv => {
            servicesMap.set(srv.id, srv.name);

            // Add to dropdown
            const opt = document.createElement("option");
            opt.value = srv.id;
            opt.textContent = srv.name;
            selectEl.appendChild(opt);

            // Add to list
            const item = document.createElement("div");
            item.className = "list-item";
            item.innerHTML = `
                <div>
                    <strong>${escapeHtml(srv.name)}</strong>
                    ${srv.url ? `<br><small><a href="${escapeHtml(srv.url)}" target="_blank" style="color: var(--primary); text-decoration: none;">${escapeHtml(srv.url)}</a></small>` : ""}
                </div>
                <small style="color: var(--text-secondary)">ID: ${srv.id}</small>
            `;
            listEl.appendChild(item);
        });
    } catch (err) {
        console.error("Error loading services:", err);
    }
}

async function handleCreateService(e) {
    e.preventDefault();
    const nameInput = document.getElementById("service-name");
    const urlInput = document.getElementById("service-url");

    try {
        const res = await fetch("/services", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                name: nameInput.value.trim(),
                url: urlInput.value.trim() || null
            })
        });

        if (!res.ok) {
            const err = await res.json();
            alert(`Error: ${err.detail || "Could not create service"}`);
            return;
        }

        nameInput.value = "";
        urlInput.value = "";
        await loadServices();
    } catch (err) {
        alert("Failed to submit service: " + err.message);
    }
}

async function loadIncidents() {
    try {
        const res = await fetch("/incidents");
        if (!res.ok) throw new Error("Failed to load incidents");
        const incidents = await res.json();

        const listEl = document.getElementById("incidents-list");
        let activeCount = 0;
        let resolvedCount = 0;

        incidents.forEach(inc => {
            if (inc.status === "resolved") {
                resolvedCount++;
            } else {
                activeCount++;
            }
        });

        document.getElementById("stat-active").textContent = activeCount;
        document.getElementById("stat-resolved").textContent = resolvedCount;

        if (incidents.length === 0) {
            listEl.innerHTML = '<p class="empty-state">No incidents reported. All systems normal.</p>';
            return;
        }

        listEl.innerHTML = "";
        incidents.forEach(inc => {
            const serviceName = servicesMap.get(inc.service_id) || `Service #${inc.service_id}`;
            const item = document.createElement("div");
            item.className = "list-item incident-item";

            const createdDate = new Date(inc.created_at).toLocaleString();
            const resolvedInfo = inc.resolved_at 
                ? ` &bull; Resolved: ${new Date(inc.resolved_at).toLocaleString()}` 
                : "";

            item.innerHTML = `
                <div class="incident-top">
                    <div>
                        <span class="pill sev-${inc.severity}">${inc.severity}</span>
                        <span class="incident-title" style="margin-left: 0.5rem">${escapeHtml(inc.title)}</span>
                    </div>
                    <div>
                        <select onchange="updateIncidentStatus(${inc.id}, this.value)" style="width: auto; padding: 0.25rem 0.5rem; font-size: 0.8rem;">
                            <option value="investigating" ${inc.status === 'investigating' ? 'selected' : ''}>Investigating</option>
                            <option value="identified" ${inc.status === 'identified' ? 'selected' : ''}>Identified</option>
                            <option value="monitoring" ${inc.status === 'monitoring' ? 'selected' : ''}>Monitoring</option>
                            <option value="resolved" ${inc.status === 'resolved' ? 'selected' : ''}>Resolved</option>
                        </select>
                    </div>
                </div>
                <div class="incident-meta">
                    <span>Target: <strong>${escapeHtml(serviceName)}</strong></span>
                    <span>Status: <strong class="status-${inc.status}">${inc.status.toUpperCase()}</strong></span>
                    <span>Reported: ${createdDate}${resolvedInfo}</span>
                </div>
            `;
            listEl.appendChild(item);
        });
    } catch (err) {
        console.error("Error loading incidents:", err);
    }
}

async function handleCreateIncident(e) {
    e.preventDefault();
    const serviceSelect = document.getElementById("incident-service");
    const titleInput = document.getElementById("incident-title");
    const severitySelect = document.getElementById("incident-severity");
    const statusSelect = document.getElementById("incident-status");

    if (!serviceSelect.value) {
        alert("Please select a target service first.");
        return;
    }

    try {
        const res = await fetch("/incidents", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                service_id: parseInt(serviceSelect.value, 10),
                title: titleInput.value.trim(),
                severity: severitySelect.value,
                status: statusSelect.value
            })
        });

        if (!res.ok) {
            const err = await res.json();
            alert(`Error: ${err.detail || "Could not report incident"}`);
            return;
        }

        titleInput.value = "";
        await loadIncidents();
    } catch (err) {
        alert("Failed to submit incident: " + err.message);
    }
}

async function updateIncidentStatus(incidentId, newStatus) {
    try {
        const res = await fetch(`/incidents/${incidentId}`, {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ status: newStatus })
        });

        if (!res.ok) {
            alert("Failed to update status");
        }
        await loadIncidents();
    } catch (err) {
        alert("Error updating status: " + err.message);
    }
}

function escapeHtml(str) {
    if (!str) return "";
    return str.replace(/[&<>'"]/g, 
        tag => ({
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            "'": '&#39;',
            '"': '&quot;'
        }[tag] || tag)
    );
}
