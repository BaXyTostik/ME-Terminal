export interface Item {
  id: string;
  name: string;
  name_ru: string;
  count: number;
  full_shulkers: number;
  icon: string | null;
}

export interface Warehouse {
  id: string;
  name: string;
  item_count: number;
  total_count: number;
}

export interface WarehousesResponse {
  warehouses: Warehouse[];
  generated_at: string;
}

export interface ItemsResponse {
  warehouse_id: string;
  warehouse_name: string;
  generated_at: string;
  items: Item[];
  stats: {
    unique_items: number;
    total_count: number;
  };
}

export interface ConfigResponse {
  refresh_interval: number;
  data_file: string;
}

export type Category =
  | "all"
  | "blocks"
  | "tools"
  | "armor"
  | "food"
  | "resources"
  | "other";
