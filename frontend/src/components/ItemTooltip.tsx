"use client";

import { Item } from "@/lib/types";

interface TooltipProps {
  item: Item | null;
  x: number;
  y: number;
}

function fmtFull(n: number): string {
  return n.toLocaleString("ru-RU");
}

export function ItemTooltip({ item, x, y }: TooltipProps) {
  if (!item) return null;

  const style: React.CSSProperties = {
    position: "fixed",
    left: x + 14,
    top: y + 14,
    zIndex: 9999,
    pointerEvents: "none",
  };

  // Prevent going off-screen
  if (typeof window !== "undefined") {
    if (x + 280 > window.innerWidth) style.left = x - 260;
    if (y + 120 > window.innerHeight) style.top = y - 100;
  }

  return (
    <div
      style={style}
      className="glass-strong rounded-lg px-3 py-2.5 max-w-[260px] border border-[var(--primary)]/30 shadow-lg shadow-purple-500/10"
    >
      <div className="text-sm font-semibold text-white">
        {item.name_ru || item.name}
      </div>
      {item.name_ru && (
        <div className="text-xs text-gray-400 mt-0.5">{item.name}</div>
      )}
      <div className="text-xs text-[var(--muted-foreground)] mt-0.5">
        {item.id}
      </div>
      <div className="text-xs text-gray-300 mt-2">
        Количество:{" "}
        <span className="text-emerald-400 font-bold">
          {fmtFull(item.count)}
        </span>
      </div>
      {item.full_shulkers > 0 && (
        <div className="text-xs text-gray-300 mt-1">
          Шалкеров:{" "}
          <span className="text-emerald-400 font-bold">
            {item.full_shulkers}
          </span>
        </div>
      )}
    </div>
  );
}
