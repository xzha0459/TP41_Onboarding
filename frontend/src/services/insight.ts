const BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

async function http<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...init,
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}: ${await res.text()}`);
  return res.json() as Promise<T>;
}

/** Types match your Django responses */
export type SeriesPoint = { year: number; value: number };
export type PercentPoint = { year: number; percent: number };

export interface CarOwnershipResp {
  state: string;
  values: SeriesPoint[];
  yearlyPercentageChange: PercentPoint[];
  averageAnnualGrowthRate: number;
  vehiclesPer1000: SeriesPoint[] | null;
}

export interface CbdPopulationResp {
  region: { id: string; name: string; state: string };
  values: SeriesPoint[];
  yearlyPercentageChange: PercentPoint[];
  averageAnnualGrowthRate: number;
}

export const insightsApi = {
  /** GET /insights/carOwnership?stateCode=VIC&startYear=2015&endYear=2024 */
  carOwnership: (stateCode: string, startYear?: number, endYear?: number) =>
    http<CarOwnershipResp>(
      `/insights/carOwnership?stateCode=${encodeURIComponent(stateCode)}`
      + (startYear ? `&startYear=${startYear}` : '')
      + (endYear ? `&endYear=${endYear}` : '')
    ),

  /** GET /insights/cbdPopulation?regionId=CBD_MEL&startYear=2001&endYear=2021 */
  cbdPopulation: (regionId: string, startYear?: number, endYear?: number) =>
    http<CbdPopulationResp>(
      `/insights/cbdPopulation?regionId=${encodeURIComponent(regionId)}`
      + (startYear ? `&startYear=${startYear}` : '')
      + (endYear ? `&endYear=${endYear}` : '')
    ),
};
