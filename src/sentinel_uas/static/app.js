const button = document.querySelector("#load-button");
const tokenInput = document.querySelector("#token");
const message = document.querySelector("#message");

async function getJson(path, token) {
  const response = await fetch(path, { headers: { "X-Lab-Token": token } });
  if (!response.ok) {
    const body = await response.json().catch(() => ({ detail: "Request failed" }));
    throw new Error(body.detail || `HTTP ${response.status}`);
  }
  return response.json();
}

function renderFleet(drones) {
  const body = document.querySelector("#fleet-body");
  body.replaceChildren(...drones.map((drone) => {
    const row = document.createElement("tr");
    const values = [
      drone.drone_id,
      drone.call_sign,
      drone.mode,
      `${drone.battery_pct}%`,
      `${drone.link_quality_pct}%`,
    ];
    for (const value of values) {
      const cell = document.createElement("td");
      cell.textContent = value;
      row.appendChild(cell);
    }
    return row;
  }));
}

async function loadDashboard() {
  const token = tokenInput.value.trim();
  message.textContent = "Loading...";
  try {
    const [healthResponse, fleet, metrics] = await Promise.all([
      fetch("/health").then((response) => response.json()),
      getJson("/api/v1/fleet", token),
      getJson("/api/v1/assurance/metrics", token),
    ]);
    document.querySelector("#service-status").textContent = healthResponse.status.toUpperCase();
    document.querySelector("#service-status").className = "status good";
    document.querySelector("#fleet-total").textContent = metrics.drones_total;
    document.querySelector("#fleet-active").textContent = metrics.drones_active;
    document.querySelector("#audit-events").textContent = metrics.audit_events;
    document.querySelector("#audit-valid").textContent = metrics.audit_chain_valid ? "VALID" : "FAILED";
    renderFleet(fleet);
    message.textContent = `Loaded ${fleet.length} simulated aircraft.`;
  } catch (error) {
    document.querySelector("#service-status").textContent = "ERROR";
    document.querySelector("#service-status").className = "status bad";
    message.textContent = error.message;
  }
}

button.addEventListener("click", loadDashboard);
tokenInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter") loadDashboard();
});
