import axios from "axios";

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 10000,
});

export type NearbyInput = {
  address: string;
  max_walk_time?: number; // optional; backend defaults to 5
};

export type PredictInput = NearbyInput & {

  datetime: string | Date;
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

export type OriginDTO = {
  latitude: number;
  longitude: number;
  address: string;
  formatted_address: string;
};

export type NearbyApiResponse = { // NEW
  origin: OriginDTO;
  nearby: NearbyItem[];
};

export type PredictApiResponse = { // NEW
  origin: OriginDTO;
  nearby: PredictItem[];
};

function withOptionalWalk<T extends { address: string; max_walk_time?: number }>(body: T) {
  return {
    address: body.address,
    ...(body.max_walk_time ? { max_walk_time: body.max_walk_time } : {}),
  };
}

// ---- APIs ----
export async function fetchNearby(body: NearbyInput): Promise<NearbyItem[]> {
  const payload = withOptionalWalk(body);
  const { data } = await api.post<NearbyApiResponse>("/parking/nearby", payload);
  return data.nearby;
}

export async function fetchNearbyPredict(body: PredictInput): Promise<PredictItem[]> {
  const { datetime, ...others } = body;
  const payload = {
    ...withOptionalWalk(others),
    datetime: typeof datetime === "string" ? datetime : datetime.toISOString(),
  };
  const { data } = await api.post<PredictApiResponse>("/parking/nearby/predict", payload);
  return data.nearby;
}

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
