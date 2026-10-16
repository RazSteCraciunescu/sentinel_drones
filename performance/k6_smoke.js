import http from "k6/http";
import { check, sleep } from "k6";

export const options = {
  scenarios: {
    assurance_smoke: {
      executor: "constant-vus",
      vus: 5,
      duration: "30s"
    }
  },
  thresholds: {
    http_req_failed: ["rate<0.01"],
    http_req_duration: ["p(95)<300"]
  }
};

const BASE_URL = __ENV.BASE_URL || "http://127.0.0.1:8080";
const TOKEN = __ENV.LAB_TOKEN || "observer-local-token";

export default function () {
  const health = http.get(`${BASE_URL}/health`);
  check(health, { "health returns 200": (response) => response.status === 200 });

  const fleet = http.get(`${BASE_URL}/api/v1/fleet`, {
    headers: { "X-Lab-Token": TOKEN }
  });
  check(fleet, {
    "fleet returns 200": (response) => response.status === 200,
    "fleet contains three records": (response) => response.json().length === 3
  });

  sleep(1);
}
