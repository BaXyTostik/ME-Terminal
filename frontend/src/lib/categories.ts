import { Category } from "./types";

export const CATEGORIES: { id: Category; label: string; icon: string }[] = [
  { id: "all", label: "Все", icon: "grid" },
  { id: "blocks", label: "Блоки", icon: "box" },
  { id: "tools", label: "Инструменты", icon: "wrench" },
  { id: "armor", label: "Броня", icon: "shield" },
  { id: "food", label: "Еда", icon: "apple" },
  { id: "resources", label: "Ресурсы", icon: "gem" },
  { id: "other", label: "Разное", icon: "layers" },
];

const BLOCK_PATTERNS = [
  "_slab", "_stairs", "_wall", "_log", "_planks", "_block",
  "_ore", "_bricks", "_fence", "_door", "_trapdoor", "_wood",
  "_terracotta", "_concrete", "_wool", "_glass", "_carpet",
  "_stone", "deepslate", "sandstone", "basalt", "obsidian",
  "granite", "diorite", "andesite", "tuff", "calcite",
];

const TOOL_PATTERNS = [
  "_pickaxe", "_axe", "_shovel", "_hoe", "_sword",
  "bow", "crossbow", "trident", "fishing_rod", "shears",
  "flint_and_steel", "compass", "clock", "spyglass", "mace",
];

const ARMOR_PATTERNS = [
  "_helmet", "_chestplate", "_leggings", "_boots",
  "_horse_armor", "elytra", "shield", "turtle_helmet",
];

const FOOD_PATTERNS = [
  "wheat", "carrot", "potato", "beef", "porkchop",
  "chicken", "bread", "apple", "melon", "cookie",
  "cake", "soup", "stew", "salmon", "cod", "beetroot",
  "sweet_berries", "glow_berries", "mushroom", "rabbit",
  "mutton", "dried_kelp", "honey", "pumpkin_pie",
];

const RESOURCE_PATTERNS = [
  "_ingot", "_nugget", "_shard", "_crystal",
  "diamond", "emerald", "lapis", "redstone",
  "quartz", "amethyst", "copper", "gold_block",
  "iron_block", "netherite", "coal", "charcoal",
  "blaze_rod", "blaze_powder", "ender_pearl",
  "ghast_tear", "slime_ball", "phantom_membrane",
];

function matchesAny(id: string, patterns: string[]): boolean {
  const n = id.replace("minecraft:", "");
  return patterns.some((p) => n.includes(p));
}

export function getCategory(itemId: string): Category {
  if (matchesAny(itemId, ARMOR_PATTERNS)) return "armor";
  if (matchesAny(itemId, TOOL_PATTERNS)) return "tools";
  if (matchesAny(itemId, FOOD_PATTERNS)) return "food";
  if (matchesAny(itemId, RESOURCE_PATTERNS)) return "resources";
  if (matchesAny(itemId, BLOCK_PATTERNS)) return "blocks";
  return "other";
}
