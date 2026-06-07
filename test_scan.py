"""
Chest Tracker NBT Scanner - тестовый парсер
Парсит .nbt файлы Chest Tracker (Minecraft) без внешних зависимостей.
Показывает полную структуру контейнеров из minecraft:overworld.
"""

import struct
import gzip
import io
import sys
import os
from collections import defaultdict


# ===================== NBT PARSER =====================

def read_string(buf):
    length = struct.unpack('>H', buf.read(2))[0]
    return buf.read(length).decode('utf-8', errors='replace')


def read_tag(buf, tag_type=None):
    if tag_type is None:
        tag_type = struct.unpack('b', buf.read(1))[0]
        if tag_type == 0:
            return None, None, None
        name = read_string(buf)
    else:
        name = None

    if tag_type == 1:
        val = struct.unpack('b', buf.read(1))[0]
    elif tag_type == 2:
        val = struct.unpack('>h', buf.read(2))[0]
    elif tag_type == 3:
        val = struct.unpack('>i', buf.read(4))[0]
    elif tag_type == 4:
        val = struct.unpack('>q', buf.read(8))[0]
    elif tag_type == 5:
        val = struct.unpack('>f', buf.read(4))[0]
    elif tag_type == 6:
        val = struct.unpack('>d', buf.read(8))[0]
    elif tag_type == 7:
        n = struct.unpack('>i', buf.read(4))[0]
        val = buf.read(n)
    elif tag_type == 8:
        val = read_string(buf)
    elif tag_type == 9:
        lt = struct.unpack('b', buf.read(1))[0]
        n = struct.unpack('>i', buf.read(4))[0]
        val = [read_tag(buf, lt)[2] for _ in range(n)]
    elif tag_type == 10:
        val = {}
        while True:
            tt, tname, tv = read_tag(buf)
            if tt is None:
                break
            val[tname] = tv
    elif tag_type == 11:
        n = struct.unpack('>i', buf.read(4))[0]
        val = list(struct.unpack(f'>{n}i', buf.read(4 * n)))
    elif tag_type == 12:
        n = struct.unpack('>i', buf.read(4))[0]
        val = list(struct.unpack(f'>{n}q', buf.read(8 * n)))
    else:
        val = None

    return tag_type, name, val


def parse_nbt_file(filepath):
    """Читает и парсит gzip-сжатый NBT файл."""
    with open(filepath, 'rb') as f:
        data = gzip.decompress(f.read())
    buf = io.BytesIO(data)
    _, _, root = read_tag(buf)
    return root


# ===================== ITEM EXTRACTION =====================

def extract_items_from_container(items_list, coord_str, results, depth=0):
    """
    Извлекает предметы из контейнера.
    Рекурсивно разворачивает шалкер-боксы.
    """
    if not isinstance(items_list, list):
        return

    for item in items_list:
        if not isinstance(item, dict):
            continue
        item_id = item.get('id', '')
        count = item.get('count', 1)

        # Проверяем есть ли вложенный контейнер (шалкер-бокс)
        components = item.get('components', {})
        nested_container = None
        if isinstance(components, dict):
            nested_container = components.get('minecraft:container')

        if nested_container and isinstance(nested_container, list):
            # Это шалкер-бокс — разворачиваем содержимое
            nested_items = []
            for slot_data in nested_container:
                if isinstance(slot_data, dict) and 'item' in slot_data:
                    nested_items.append(slot_data['item'])
            extract_items_from_container(
                nested_items, coord_str, results, depth + 1
            )
        else:
            # Обычный предмет — добавляем
            results.append({
                'id': item_id,
                'count': count,
                'location': coord_str,
                'depth': depth
            })


# ===================== SCANNER =====================

def scan_overworld(root):
    """Сканирует все контейнеры в minecraft:overworld."""
    dimension_key = 'minecraft:overworld'
    dimension_data = root.get(dimension_key)
    if not dimension_data:
        print(f"[!] Измерение '{dimension_key}' не найдено в файле.")
        print(f"    Доступные ключи: {list(root.keys())}")
        return [], {}

    memories = dimension_data.get('memories', {})
    all_items = []
    containers_info = {}

    for coord_str, memory in memories.items():
        container_type = memory.get('container', 'unknown')
        items_list = memory.get('items', [])

        containers_info[coord_str] = {
            'type': container_type,
            'item_count': len(items_list) if isinstance(items_list, list) else 0,
            'timestamp': memory.get('realTimestamp', '?')
        }

        extract_items_from_container(items_list, coord_str, all_items)

    return all_items, containers_info


def format_item_name(item_id):
    """minecraft:white_wool -> White Wool"""
    name = item_id.replace('minecraft:', '').replace('_', ' ')
    return name.title()


# ===================== MAIN =====================

def main():
    # Получаем путь к файлу
    if len(sys.argv) > 1:
        filepath = sys.argv[1].strip('"').strip("'")
    else:
        print("Chest Tracker NBT Scanner")
        print("=" * 50)
        filepath = input("Введите путь к .nbt файлу: ").strip('"').strip("'")

    if not os.path.isfile(filepath):
        print(f"\n[ОШИБКА] Файл не найден: {filepath}")
        input("\nНажмите Enter для выхода...")
        sys.exit(1)

    print(f"\nФайл: {filepath}")
    print(f"Размер: {os.path.getsize(filepath)} байт")
    print("=" * 50)
    print("Парсинг NBT...")

    try:
        root = parse_nbt_file(filepath)
    except Exception as e:
        print(f"\n[ОШИБКА] Не удалось распарсить файл: {e}")
        input("\nНажмите Enter для выхода...")
        sys.exit(1)

    # Показываем доступные измерения
    print(f"\nИзмерения в файле:")
    for key in root.keys():
        dim_data = root[key]
        mem_count = 0
        if isinstance(dim_data, dict) and 'memories' in dim_data:
            mem_count = len(dim_data['memories'])
        print(f"  - {key} ({mem_count} контейнеров)")

    print("\n" + "=" * 50)
    print("Сканирование minecraft:overworld...")
    print("Фильтр координат: ВСЕ (без фильтра)")
    print("=" * 50)

    all_items, containers_info = scan_overworld(root)

    # === Вывод контейнеров ===
    print(f"\n{'='*50}")
    print(f"  КОНТЕЙНЕРЫ ({len(containers_info)} шт.)")
    print(f"{'='*50}\n")

    for coord, info in sorted(containers_info.items()):
        ctype = info['type'].replace('minecraft:', '')
        print(f"  ({coord})  [{ctype}]  предметов: {info['item_count']}")
        print(f"    timestamp: {info['timestamp']}")

    # === Суммирование предметов ===
    totals = defaultdict(lambda: {'count': 0, 'locations': set()})
    for item in all_items:
        key = item['id']
        totals[key]['count'] += item['count']
        totals[key]['locations'].add(item['location'])

    sorted_totals = sorted(totals.items(), key=lambda x: -x[1]['count'])

    print(f"\n{'='*50}")
    print(f"  ИТОГО ПРЕДМЕТОВ ({len(sorted_totals)} уникальных)")
    print(f"{'='*50}\n")

    print(f"  {'Предмет':<40} {'Кол-во':>8}  {'Мест':>4}")
    print(f"  {'-'*40} {'-'*8}  {'-'*4}")

    for item_id, data in sorted_totals:
        name = format_item_name(item_id)
        count = data['count']
        locs = len(data['locations'])
        print(f"  {name:<40} {count:>8}  {locs:>4}")

    # === Статистика ===
    total_count = sum(item['count'] for item in all_items)
    print(f"\n{'='*50}")
    print(f"  СТАТИСТИКА")
    print(f"{'='*50}")
    print(f"  Контейнеров:        {len(containers_info)}")
    print(f"  Уникальных предметов: {len(sorted_totals)}")
    print(f"  Общее количество:    {total_count}")
    print(f"{'='*50}")


if __name__ == '__main__':
    main()
    try:
        input("\nНажмите Enter для выхода...")
    except EOFError:
        pass
