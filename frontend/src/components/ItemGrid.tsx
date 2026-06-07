"use client";

import { memo } from "react";
import { Item } from "@/lib/types";
import { getIconUrl } from "@/lib/api";

interface ItemGridProps {
  items: Item[];
  loading?: boolean;
  onHover: (item: Item | null, e: React.MouseEvent) => void;
}

function fmtQty(n: number): string {
  if (n < 1000) return String(n);
  if (n < 1e6) {
    const k = n / 1000;
    return (k < 10 ? k.toFixed(1) : Math.round(k)) + "K";
  }
  const m = n / 1e6;
  return (m < 10 ? m.toFixed(1) : Math.round(m)) + "M";
}

const Slot = memo(function Slot({
  item,
  onMouseEnter,
}: {
  item: Item;
  onMouseEnter: (e: React.MouseEvent) => void;
}) {
  const url = getIconUrl(item.icon);
  return (
    <div
      className="relative aspect-square rounded-lg border border-[var(--border)] bg-[var(--secondary)] flex items-center justify-center overflow-hidden slot-hover"
      style={{ contain: "layout style paint" }}
      onMouseEnter={onMouseEnter}
    >
      {url ? (
        <img
          src={url}
          alt=""
          loading="lazy"
          decoding="async"
          className="w-[70%] h-[70%] object-contain"
          style={{ imageRendering: "pixelated" }}
        />
      ) : (
        <span className="text-[9px] text-center text-[var(--muted-foreground)] leading-tight px-1">
          {(item.name_ru || item.name).split(" ").slice(0, 2).join(" ")}
        </span>
      )}
      <span className="absolute right-1 bottom-0 text-[11px] font-bold text-emerald-400">
        {fmtQty(item.count)}
      </span>
    </div>
  );
});

export function ItemGrid({ items, loading, onHover }: ItemGridProps) {
  if (loading) {
    return (
      <div className="flex items-center justify-center h-full text-[var(--muted-foreground)]">
        <div className="flex items-center gap-3">
          <div className="w-5 h-5 border-2 border-purple-500/30 border-t-purple-500 rounded-full animate-spin" />
          Загрузка...
        </div>
      </div>
    );
  }

  if (items.length === 0) {
    return (
      <div className="flex items-center justify-center h-full text-[var(--muted-foreground)]">
        Ничего не найдено
      </div>
    );
  }

  return (
    <div
      className="h-full overflow-y-auto scrollbar-thin"
      style={{ willChange: "scroll-position" }}
      onMouseLeave={() => onHover(null, {} as React.MouseEvent)}
    >
      <div className="grid grid-cols-[repeat(auto-fill,minmax(75px,1fr))] gap-1.5">
        {items.map((item) => (
          <Slot
            key={item.id}
            item={item}
            onMouseEnter={(e) => onHover(item, e)}
          />
        ))}
      </div>
    </div>
  );
}
