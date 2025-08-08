export async function fetchJSON<T>(path: string): Promise<T> {
  const res = await fetch(path);
  if (!res.ok) throw new Error(`Failed: ${res.status}`);
  return res.json() as Promise<T>;
}
