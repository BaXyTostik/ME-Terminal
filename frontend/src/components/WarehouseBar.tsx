"use client";

import { Warehouse } from "@/lib/types";

interface WarehouseBarProps {
  warehouses: Warehouse[];
  active: string;
  onChange: (id: string) => void;
}

function fmtCount(n: number): string {
  if (n < 1000) return String(n);
  if (n < 1_000_000) {
    const k = n / 1000;
    return (k < 10 ? k.toFixed(1) : Math.round(k)) + "K";
  }
  const m = n / 1_000_000;
  return (m < 10 ? m.toFixed(1) : Math.round(m)) + "M";
}

export function WarehouseBar({
  warehouses,
  active,
  onChange,
}: WarehouseBarProps) {
  return (
    <div className="flex gap-2 flex-wrap">
      {warehouses.map((wh) => (
        <button
          key={wh.id}
          onClick={() => onChange(wh.id)}
          className={`px-4 py-2 text-sm rounded-lg border transition-all ${
            active === wh.id
              ? "border-[var(--primary)] bg-[var(--accent)] text-[var(--primary-foreground)] neon-border"
              : "border-[var(--border)] bg-[var(--secondary)] text-[var(--muted-foreground)] hover:bg-white/5 hover:text-[var(--foreground)]"
          }`}
        >
          {wh.name}
          <span className="ml-2 text-xs opacity-50">
            {fmtCount(wh.total_count)}
          </span>
        </button>
      ))}
    </div>
  );
}
