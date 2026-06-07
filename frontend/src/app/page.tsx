"use client";

import { useState, useEffect, useCallback, useMemo, useRef } from "react";
import { SearchBar } from "@/components/SearchBar";
import { CategoryFilter } from "@/components/CategoryFilter";
import { WarehouseBar } from "@/components/WarehouseBar";
import { ItemGrid } from "@/components/ItemGrid";
import { fetchWarehouses, fetchItems, fetchConfig } from "@/lib/api";
import { getCategory } from "@/lib/categories";
import { useDebouncedValue } from "@/lib/hooks";
import { Item, Warehouse, Category } from "@/lib/types";

export default function Home() {
  const [warehouses, setWarehouses] = useState<Warehouse[]>([]);
  const [items, setItems] = useState<Item[]>([]);
  const [activeWh, setActiveWh] = useState("__all__");
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState<Category>("all");
  const [sortKey, setSortKey] = useState<"count" | "name">("count");
  const [sortDir, setSortDir] = useState<1 | -1>(-1);
  const [refreshInterval, setRefreshInterval] = useState(15);
  const [generatedAt, setGeneratedAt] = useState("");
  const [loading, setLoading] = useState(true);
  const tooltipRef = useRef<HTMLDivElement>(null);

  const loadData = useCallback(async () => {
    try {
      const [whData, itemData] = await Promise.all([
        fetchWarehouses(),
        fetchItems(activeWh),
      ]);
      setWarehouses(whData.warehouses);
      setItems(itemData.items);
      setGeneratedAt(itemData.generated_at);
    } catch (e) {
      console.error("Failed to load data:", e);
    } finally {
      setLoading(false);
    }
  }, [activeWh]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  useEffect(() => {
    fetchConfig().then((cfg) => setRefreshInterval(cfg.refresh_interval));
  }, []);

  useEffect(() => {
    const id = setInterval(loadData, refreshInterval * 1000);
    return () => clearInterval(id);
  }, [loadData, refreshInterval]);

  const handleWhChange = (id: string) => {
    setActiveWh(id);
  };

  // Category counts
  const categoryCounts = useMemo(() => {
    const counts: Record<Category, number> = {
      all: items.length,
      blocks: 0,
      tools: 0,
      armor: 0,
      food: 0,
      resources: 0,
      other: 0,
    };
    items.forEach((it) => {
      const cat = getCategory(it.id);
      counts[cat]++;
    });
    return counts;
  }, [items]);

  // Filtered + sorted items
  const debouncedSearch = useDebouncedValue(search, 150);
  const filtered = useMemo(() => {
    let list = items;

    // Category filter
    if (category !== "all") {
      list = list.filter((it) => getCategory(it.id) === category);
    }

    // Search filter
    if (debouncedSearch) {
      const q = debouncedSearch.toLowerCase();
      list = list.filter(
        (it) =>
          it.name.toLowerCase().includes(q) ||
          it.name_ru.toLowerCase().includes(q) ||
          it.id.toLowerCase().includes(q)
      );
    }

    // Sort
    list = [...list].sort((a, b) => {
      if (sortKey === "name") {
        return a.name.localeCompare(b.name) * sortDir;
      }
      return (a.count - b.count) * sortDir;
    });

    return list;
  }, [items, category, debouncedSearch, sortKey, sortDir]);

  const handleSort = () => {
    if (sortKey === "count" && sortDir === -1) {
      setSortDir(1);
    } else if (sortKey === "count" && sortDir === 1) {
      setSortKey("name");
      setSortDir(1);
    } else if (sortKey === "name" && sortDir === 1) {
      setSortDir(-1);
    } else {
      setSortKey("count");
      setSortDir(-1);
    }
  };

  const sortLabel =
    sortKey === "count"
      ? sortDir === -1
        ? "Кол-во ▼"
        : "Кол-во ▲"
      : sortDir === 1
      ? "Имя А-Я"
      : "Имя Я-А";

  const handleHover = useCallback((item: Item | null, e: React.MouseEvent) => {
    const el = tooltipRef.current;
    if (!el) return;
    if (!item) {
      el.style.display = "none";
      return;
    }
    const name = item.name_ru || item.name;
    const shulk = item.full_shulkers > 0
      ? `<div style="margin-top:4px;font-size:12px;color:#9ca3af">Шалкеров: <b style="color:#34d399">${item.full_shulkers}</b></div>` : "";
    el.innerHTML =
      `<div style="font-size:13px;font-weight:600;color:#fff">${name}</div>` +
      (item.name_ru ? `<div style="font-size:11px;color:#6b7280;margin-top:2px">${item.name}</div>` : "") +
      `<div style="font-size:11px;color:#6b7280;margin-top:2px">${item.id}</div>` +
      `<div style="margin-top:6px;font-size:12px;color:#9ca3af">Кол-во: <b style="color:#34d399">${item.count.toLocaleString("ru-RU")}</b></div>` +
      shulk;
    el.style.display = "block";
    const x = e.clientX + 14;
    const y = e.clientY + 14;
    el.style.left = (x + 260 > window.innerWidth ? e.clientX - 260 : x) + "px";
    el.style.top = (y + 100 > window.innerHeight ? e.clientY - 100 : y) + "px";
  }, []);

  const stats = useMemo(() => ({
    unique: filtered.length,
    total: filtered.reduce((s, it) => s + it.count, 0),
  }), [filtered]);

  return (
    <main className="h-screen p-3 md:p-4 overflow-hidden">
      <div className="glass rounded-2xl p-4 max-w-[1800px] mx-auto h-full flex flex-col gap-3">
        {/* Header */}
        <div className="flex items-center justify-between flex-wrap gap-3 shrink-0">
          <h1 className="text-xl font-bold bg-gradient-to-r from-purple-400 to-indigo-400 bg-clip-text text-transparent">
            ME Terminal
          </h1>
          <div className="flex items-center gap-3 text-xs text-[var(--muted-foreground)]">
            <span className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-emerald-500 shadow-[0_0_6px_rgba(16,185,129,0.6)]" />
              Online
            </span>
            {generatedAt && (
              <span>
                {new Date(generatedAt).toLocaleString("ru-RU", {
                  day: "2-digit",
                  month: "2-digit",
                  hour: "2-digit",
                  minute: "2-digit",
                })}
              </span>
            )}
          </div>
        </div>

        {/* Toolbar */}
        <div className="flex gap-3 items-center shrink-0">
          <SearchBar value={search} onChange={setSearch} />
          <CategoryFilter
            active={category}
            onChange={setCategory}
            counts={categoryCounts}
          />
          <button
            onClick={handleSort}
            className="px-4 py-2.5 text-sm rounded-lg border border-[var(--border)] bg-[var(--secondary)] text-[var(--muted-foreground)] hover:bg-white/5 hover:text-[var(--foreground)] transition-all whitespace-nowrap"
          >
            {sortLabel}
          </button>
        </div>

        {/* Warehouses */}
        <div className="shrink-0">
        <WarehouseBar
          warehouses={warehouses}
          active={activeWh}
          onChange={handleWhChange}
        />
        </div>

        {/* Grid */}
        <div className="glass rounded-xl p-3 flex-1 min-h-0 overflow-hidden">
          <ItemGrid items={filtered} loading={loading} onHover={handleHover} />
        </div>

        {/* Status bar */}
        <div className="flex gap-6 text-xs text-[var(--muted-foreground)] shrink-0">
          <span>
            Предметов:{" "}
            <span className="text-emerald-400 font-semibold">
              {stats.unique.toLocaleString("ru-RU")}
            </span>
          </span>
          <span>
            Всего:{" "}
            <span className="text-emerald-400 font-semibold">
              {stats.total.toLocaleString("ru-RU")}
            </span>
          </span>
        </div>
      </div>

      <div
        ref={tooltipRef}
        className="fixed z-[9999] pointer-events-none hidden rounded-lg px-3 py-2.5 max-w-[260px] border border-purple-500/30 shadow-lg shadow-purple-500/10"
        style={{ background: "#0f0f1a", borderColor: "rgba(139,92,246,0.3)" }}
      />
    </main>
  );
}
