"use client";

import { useState } from "react";
import { ChevronDown } from "lucide-react";
import { Category } from "@/lib/types";
import { CATEGORIES } from "@/lib/categories";

interface CategoryFilterProps {
  active: Category;
  onChange: (category: Category) => void;
  counts: Record<Category, number>;
}

export function CategoryFilter({
  active,
  onChange,
  counts,
}: CategoryFilterProps) {
  const [open, setOpen] = useState(false);
  const activeLabel =
    CATEGORIES.find((c) => c.id === active)?.label ?? "Все";

  return (
    <div className="relative">
      <button
        onClick={() => setOpen(!open)}
        className={`flex items-center gap-2 px-4 py-2 text-sm rounded-lg border transition-all ${
          active !== "all"
            ? "border-[var(--primary)] bg-[var(--accent)] text-[var(--accent-foreground)] neon-border"
            : "border-[var(--border)] bg-[var(--secondary)] text-[var(--muted-foreground)] hover:bg-white/5"
        }`}
      >
        <span>{activeLabel}</span>
        {active !== "all" && (
          <span className="text-xs opacity-60">{counts[active]}</span>
        )}
        <ChevronDown
          className={`w-4 h-4 transition-transform ${
            open ? "rotate-180" : ""
          }`}
        />
      </button>

      {open && (
        <>
          {/* Backdrop */}
          <div
            className="fixed inset-0 z-40"
            onClick={() => setOpen(false)}
          />
          <div className="absolute top-full left-0 mt-2 z-50 rounded-lg p-2 min-w-[200px] shadow-xl shadow-black/50 bg-[#0f0f1a] border border-white/10">
            {CATEGORIES.map((cat) => (
              <button
                key={cat.id}
                onClick={() => {
                  onChange(cat.id);
                  setOpen(false);
                }}
                className={`w-full text-left px-3 py-2 text-sm rounded-md transition-all flex items-center justify-between ${
                  active === cat.id
                    ? "bg-[var(--accent)] text-[var(--accent-foreground)]"
                    : "text-[var(--muted-foreground)] hover:bg-white/5 hover:text-[var(--foreground)]"
                }`}
              >
                <span>{cat.label}</span>
                <span className="text-xs opacity-50">{counts[cat.id]}</span>
              </button>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
