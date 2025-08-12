import axios from "axios";

// ---- axios instance (NEW) ----
export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 10000,
});

// ---- types ----
export type NearbyInput = {
  address: string;
  max_walk_time?: number; // optional; backend defaults to 5
};

export type NearbyItem = {
  kerbside_id: string;
  zone_number: string;
  status_description: string;
  status_timestamp: string;
  latitude: number;
  longitude: number;
  last_updated: string;
  is_occupied: boolean;
  sign_text: string;
  days_of_week: string;
  start_time?: string;
  end_time?: string;
  walk_time?: number;
  distance_km?: number;
  predicted_available_probability?: number;
};

export type PredictItem = NearbyItem;

export type PredictInput = NearbyInput & {
  datetime: string | Date;
};

// ---- response wrappers (NEW) ----
export type OriginDTO = {
  latitude: number;
  longitude: number;
  address: string;
  formatted_address: string;
};

export type NearbyApiResponse = {
  origin: OriginDTO;
  nearby: NearbyItem[];
};

export type PredictApiResponse = {
  origin: OriginDTO;
  nearby: PredictItem[];
};

// ---- helpers ----
function withOptionalWalk<T extends { address: string; max_walk_time?: number }>(body: T) {
  return {
    address: body.address,
    ...(body.max_walk_time ? { max_walk_time: body.max_walk_time } : {}),
  };
}

// ---- APIs ----
// 维持原返回类型：数组
export async function fetchNearby(body: NearbyInput): Promise<NearbyItem[]> {
  const payload = withOptionalWalk(body);
  const { data } = await api.post<NearbyApiResponse>("/parking/nearby", payload); // CHANGED
  return data.nearby; // CHANGED
}

export async function fetchNearbyPredict(body: PredictInput): Promise<PredictItem[]> {
  const { datetime, ...others } = body;
  const payload = {
    ...withOptionalWalk(others),
    datetime: typeof datetime === "string" ? datetime : datetime.toISOString(),
  };
  const { data } = await api.post<PredictApiResponse>("/parking/nearby/predict", payload); // CHANGED
  return data.nearby; // CHANGED
}

// 需要 origin 时用这两个（NEW）
export async function fetchNearbyWithOrigin(body: NearbyInput): Promise<NearbyApiResponse> {
  const payload = withOptionalWalk(body);
  const { data } = await api.post<NearbyApiResponse>("/parking/nearby", payload);
  return data;
}

export async function fetchNearbyPredictWithOrigin(body: PredictInput): Promise<PredictApiResponse> {
  const { datetime, ...others } = body;
  const payload = {
    ...withOptionalWalk(others),
    datetime: typeof datetime === "string" ? datetime : datetime.toISOString(),
  };
  const { data } = await api.post<PredictApiResponse>("/parking/nearby/predict", payload);
  return data;
}
