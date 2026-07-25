import http from 'k6/http';
import { check } from 'k6';

const BASE = __ENV.BASE || 'http://localhost:8080';
const SLUG = 'Ansub8R';
export const options = {
    summaryTrendStats: ['min', 'med', 'avg', 'p(90)', 'p(95)', 'p(99)', 'p(99.9)', 'max'],
    scenarios: {
        reads: { 
            executor: 'constant-arrival-rate',
            rate: 2000,
            timeUnit: '1s',
            duration: '30s',
            preAllocatedVUs: 1000,
            maxVUs: 5000
        },
    },
    thresholds: { http_req_failed: ['rate<0.01'] },
};

export default function () {
  const r = http.get(BASE + '/' + SLUG, { redirects: 0 });
  check(r, { 'is 302': (x) => x.status === 302 });
}