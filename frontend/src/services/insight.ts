// Robust API client that works with remote HTTPS API.
// Uses VITE_API_BASE_URL; falls back to https://api-tp41.xyz
const RAW_BASE =
  import.meta.env.VITE_API_BASE_URL?.toString() || 'https://api-tp41.xyz';

// remove trailing slashes
const BASE = RAW_BASE.replace(/\/+$/, '');

function joinUrl(path: string) {
  return path.startsWith('/') ? `${BASE}${path}` : `${BASE}/${path}`;
}

function toQuery(params: Record<string, any>) {
  const q = Object.entries(params)
    .filter(([_, v]) => v !== undefined && v !== null && v !== '')
    .map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(v)}`)
    .join('&');
  return q ? `?${q}` : '';
}

async function http<T>(path: string, init?: RequestInit): Promise<T> {
  // 12s timeout
  const ctrl = new AbortController();
  const t = setTimeout(() => ctrl.abort(), 12000);

  try {
    const res = await fetch(joinUrl(path), {
      headers: { 'Content-Type': 'application/json' },
      signal: ctrl.signal,
      ...init,
    });
    if (!res.ok) {
      const text = await res.text().catch(() => '');
      throw new Error(`HTTP ${res.status} ${res.statusText}${text ? ` - ${text}` : ''}`);
    }
    return (await res.json()) as T;
  } finally {
    clearTimeout(t);
  }
}

/** ---- Types (only the fields the UI actually uses) ---- */
export type SeriesPoint = { year: number; value: number };
export type PercentPoint = { year: number; percent: number };

export interface CarOwnershipResp {
  values: SeriesPoint[];
  yearlyPercentageChange?: PercentPoint[];
  averageAnnualGrowthRate?: number;
  vehiclesPer1000?: SeriesPoint[] | null;
}

export interface CbdPopulationResp {
  values: SeriesPoint[];
  yearlyPercentageChange?: PercentPoint[];
  averageAnnualGrowthRate?: number;
}

/** ---- API surface ----
 * Backend assumed routes:
 *   GET /insights/carOwnership?stateCode=VIC&startYear=2001&endYear=2021
 *   GET /insights/cbdPopulation?regionId=CBD_MEL&startYear=2001&endYear=2021
 */
export const insightsApi = {
  carOwnership: (stateCode: string, startYear?: number, endYear?: number) =>
    http<CarOwnershipResp>(
      `/insights/carOwnership${toQuery({ stateCode, startYear, endYear })}`
    ),

  cbdPopulation: (regionId: string, startYear?: number, endYear?: number) =>
    http<CbdPopulationResp>(
      `/insights/cbdPopulation${toQuery({ regionId, startYear, endYear })}`
    ),
};
