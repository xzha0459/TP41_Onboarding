import axios from "axios";

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
  walk_time: number;
  distance_km: number;
};

export type PredictInput = NearbyInput & {
  datetime: string; // ISO 8601
};

export type PredictItem = NearbyItem & {
  predicted_available_probability: number;
};

// 如果用 Vite 代理，改成：const api = axios.create({ baseURL: "" });
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "",
  timeout: 10000,
});

// 只在传了且不等于默认值 5 时带上 max_walk_time
function withOptionalWalk<T extends NearbyInput>(body: T) {
  const { max_walk_time, ...rest } = body;
  return typeof max_walk_time === "number" && max_walk_time !== 5
    ? { ...rest, max_walk_time }
    : { ...rest };
}

export async function fetchNearby(body: NearbyInput): Promise<NearbyItem[]> {
  const payload = withOptionalWalk(body);
  const { data } = await api.post<NearbyItem[]>("/parking/nearby", payload);
  return data;
}

export async function fetchNearbyPredict(body: PredictInput): Promise<PredictItem[]> {
  const { datetime, ...others } = body;
  const payload = { ...withOptionalWalk(others), datetime };
  const { data } = await api.post<PredictItem[]>("/parking/nearby/predict", payload);
  return data;
}
