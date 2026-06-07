"""
Chest Tracker NBT Parser
Парсит .nbt файлы Chest Tracker, фильтрует по координатам,
разворачивает шалкер-боксы, суммирует предметы.
Без внешних зависимостей (только стандартная библиотека).
"""

import struct
import gzip
import io
import os
import glob
import json
from collections import defaultdict


# ===================== NBT PARSER =====================

def _read_string(buf):
    length = struct.unpack('>H', buf.read(2))[0]
    return buf.read(length).decode('utf-8', errors='replace')


def _read_tag(buf, tag_type=None):
    if tag_type is None:
        tag_type = struct.unpack('b', buf.read(1))[0]
        if tag_type == 0:
            return None, None, None
        name = _read_string(buf)
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
        val = _read_string(buf)
    elif tag_type == 9:
        lt = struct.unpack('b', buf.read(1))[0]
        n = struct.unpack('>i', buf.read(4))[0]
        val = [_read_tag(buf, lt)[2] for _ in range(n)]
    elif tag_type == 10:
        val = {}
        while True:
            tt, tname, tv = _read_tag(buf)
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
    """Читает и парсит gzip-сжатый NBT файл -> dict."""
    with open(filepath, 'rb') as f:
        raw = f.read()
    # Chest Tracker файлы gzip-сжаты, но подстрахуемся
    if raw[:2] == b'\x1f\x8b':
        raw = gzip.decompress(raw)
    buf = io.BytesIO(raw)
    _, _, root = _read_tag(buf)
    return root


# ===================== FILE FINDER =====================

def find_nbt_file(nbt_dir, pattern):
    """
    Ищет .nbt файл в папке, в имени которого есть pattern.
    Поддержка нескольких IP: berёт самый свежий по дате изменения.
    Игнорирует .meta и .corrupt файлы.
    """
    if not os.path.isdir(nbt_dir):
        return None

    candidates = []
    for path in glob.glob(os.path.join(nbt_dir, '*.nbt')):
        name = os.path.basename(path).lower()
        if pattern.lower() in name:
            candidates.append(path)

    if not candidates:
        return None

    # Самый недавно изменённый файл
    candidates.sort(key=lambda p: os.path.getmtime(p), reverse=True)
    return candidates[0]


# ===================== COORDINATE FILTER =====================

def _parse_coord(coord_str):
    """'-3932,-52,-607' -> (-3932, -52, -607). None при ошибке."""
    try:
        parts = coord_str.split(',')
        return int(parts[0]), int(parts[1]), int(parts[2])
    except (ValueError, IndexError):
        return None


def _in_box(coord, point_a, point_b):
    """Проверяет, попадает ли coord в куб между point_a и point_b."""
    x, y, z = coord
    min_x, max_x = min(point_a['x'], point_b['x']), max(point_a['x'], point_b['x'])
    min_y, max_y = min(point_a['y'], point_b['y']), max(point_a['y'], point_b['y'])
    min_z, max_z = min(point_a['z'], point_b['z']), max(point_a['z'], point_b['z'])
    return (min_x <= x <= max_x and
            min_y <= y <= max_y and
            min_z <= z <= max_z)


# ===================== ITEM EXTRACTION =====================

def _extract_items(items_list, coord_str, results, unpack_shulkers, depth=0):
    """
    Рекурсивно извлекает предметы из контейнера.
    Если unpack_shulkers=True — разворачивает вложенные шалкер-боксы.
    """
    if not isinstance(items_list, list):
        return

    for item in items_list:
        if not isinstance(item, dict):
            continue
        item_id = item.get('id', '')
        if not item_id:
            continue
        count = item.get('count', 1)

        nested = None
        components = item.get('components', {})
        if isinstance(components, dict):
            nested = components.get('minecraft:container')

        if unpack_shulkers and nested and isinstance(nested, list):
            nested_items = [
                slot['item'] for slot in nested
                if isinstance(slot, dict) and 'item' in slot
            ]
            _extract_items(nested_items, coord_str, results,
                           unpack_shulkers, depth + 1)
        else:
            results.append({
                'id': item_id,
                'count': count,
                'location': coord_str,
            })


def _format_name(item_id):
    """minecraft:white_wool -> White Wool"""
    return item_id.replace('minecraft:', '').replace('_', ' ').title()


# ===================== ICON RESOLVER =====================

_TEX_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        'static', 'textures')
_manifest = None
_ALIASES = {
    'magma_block': 'block/magma',
}


def _load_manifest():
    global _manifest
    if _manifest is None:
        path = os.path.join(_TEX_DIR, 'manifest.json')
        if os.path.isfile(path):
            with open(path, encoding='utf-8') as f:
                m = json.load(f)
            _manifest = {'item': set(m.get('item', [])),
                         'block': set(m.get('block', []))}
        else:
            _manifest = {'item': set(), 'block': set()}
    return _manifest


def resolve_icon(item_id):
    """Возвращает путь к текстуре (item/X или block/X) или None."""
    m = _load_manifest()
    n = item_id.replace('minecraft:', '')

    if n in _ALIASES:
        return _ALIASES[n]

    def has(name):
        if name in m['item']:
            return 'item/' + name
        if name in m['block']:
            return 'block/' + name
        return None

    r = has(n)
    if r:
        return r

    cands = []
    if n.endswith('_wood'):
        cands.append(n[:-5] + '_log')
    if n.endswith('_carpet'):
        cands.append(n[:-7] + '_wool')
    if n.endswith('_slab') or n.endswith('_wall'):
        cands.append(n.rsplit('_', 1)[0])
    if n.endswith('_stairs'):
        cands.append(n[:-7])
    if n.startswith('waxed_'):
        cands.append(n[6:])
    cands += [n + '_side', n + '_top', n + '_front', n + '_0']

    for c in cands:
        r = has(c)
        if r:
            return r
    return None


def get_items(config):

    """
    Главная функция: читает NBT, фильтрует, суммирует.
    Возвращает dict с items, containers, статистикой или ошибкой.
    """
    nbt_dir = config['nbt_dir']
    pattern = config['server_pattern']
    dimension = config['dimension']
    unpack = config.get('unpack_shulkers', True)
    use_filter = config.get('use_coord_filter', False)

    filepath = find_nbt_file(nbt_dir, pattern)
    if not filepath:
        return {'error': f"Файл с '{pattern}' не найден в {nbt_dir}"}

    try:
        root = parse_nbt_file(filepath)
    except Exception as e:
        return {'error': f"Ошибка парсинга: {e}"}

    dim_data = root.get(dimension)
    if not dim_data:
        return {'error': f"Измерение '{dimension}' не найдено",
                'available': list(root.keys())}

    memories = dim_data.get('memories', {})
    all_items = []
    containers = []

    for coord_str, memory in memories.items():
        coord = _parse_coord(coord_str)
        if coord is None:
            continue
        if use_filter and not _in_box(coord, config['point_a'], config['point_b']):
            continue

        items_list = memory.get('items', [])
        before = len(all_items)
        _extract_items(items_list, coord_str, all_items, unpack)

        containers.append({
            'coord': coord_str,
            'x': coord[0], 'y': coord[1], 'z': coord[2],
            'type': memory.get('container', 'unknown').replace('minecraft:', ''),
            'timestamp': memory.get('realTimestamp', ''),
            'extracted': len(all_items) - before,
        })

    # Суммирование
    totals = defaultdict(lambda: {'count': 0, 'locations': set()})
    for it in all_items:
        t = totals[it['id']]
        t['count'] += it['count']
        t['locations'].add(it['location'])

    items = []
    for item_id, data in totals.items():
        items.append({
            'id': item_id,
            'name': _format_name(item_id),
            'count': data['count'],
            'locations': sorted(data['locations']),
            'location_count': len(data['locations']),
            'icon': resolve_icon(item_id),
        })
    items.sort(key=lambda x: -x['count'])

    return {
        'file': os.path.basename(filepath),
        'file_mtime': os.path.getmtime(filepath),
        'dimension': dimension,
        'filtered': use_filter,
        'containers': containers,
        'items': items,
        'stats': {
            'container_count': len(containers),
            'unique_items': len(items),
            'total_count': sum(i['count'] for i in items),
        },
    }
