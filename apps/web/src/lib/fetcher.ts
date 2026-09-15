export const fetcher = async (url: string) => {
  const res = await fetch(url);
  if (!res.ok) {
    const errorInfo = await res.json().catch(() => null);
    const error = new Error(errorInfo?.detail || "Failed to fetch data from Netrava Fabric API");
    throw error;
  }
  return res.json();
};
