import {
  WarehousesResponse,
  ItemsResponse,
  ConfigResponse,
} from "./types";

const BASE = "";

export async function fetchWarehouses(): Promise<WarehousesResponse> {
  const res = await fetch(`${BASE}/api/warehouses`);
  if (!res.ok) throw new Error("Failed to fetch warehouses");
  return res.json();
}

export async function fetchItems(warehouseId: string): Promise<ItemsResponse> {
  const res = await fetch(
    `${BASE}/api/items?wh=${encodeURIComponent(warehouseId)}`
  );
  if (!res.ok) throw new Error("Failed to fetch items");
  return res.json();
}

export async function fetchConfig(): Promise<ConfigResponse> {
  const res = await fetch(`${BASE}/api/config`);
  if (!res.ok) throw new Error("Failed to fetch config");
  return res.json();
}

export function getIconUrl(icon: string | null): string | null {
  if (!icon) return null;
  if (icon.endsWith(".webp")) return `/textures/${icon}`;
  return `/textures/${icon}.png`;
}
