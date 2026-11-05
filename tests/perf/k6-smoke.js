import http from "k6/http";
import { check, sleep } from "k6";

export const options = {
  vus: 10,
  duration: "1m",
  thresholds: {
    http_req_failed: ["rate<0.01"],
    http_req_duration: ["p(95)<600", "p(99)<1200"],
  },
};

const BASE = __ENV.BASE_URL || "http://localhost:46105";
const INDUSTRY = __ENV.INDUSTRY || "legal";

export default function () {
  const health = http.get(`${BASE}/v1/health`);
  check(health, { "health 200": (r) => r.status === 200 });

  const industries = http.get(`${BASE}/v1/industries`);
  check(industries, { "industries 200": (r) => r.status === 200 });

  const bundle = http.get(`${BASE}/v1/news/bundle?industry=${INDUSTRY}&locale=en`);
  check(bundle, {
    "bundle 200": (r) => r.status === 200,
    "bundle language": (r) => r.json("data.language") === "en",
  });

  const news = http.get(`${BASE}/v1/news?industry=${INDUSTRY}&locale=es&limit=10`);
  check(news, { "news 200": (r) => r.status === 200 });
  sleep(1);
}
