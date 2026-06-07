"""
Chest Tracker Web Server — v3
Читает containers.json, раздаёт данные по складам через REST API.
Без внешних зависимостей.
"""

import json
import os
import time
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH  = os.path.join(BASE_DIR, 'config.json')
STATIC_DIR   = os.path.join(BASE_DIR, 'static')
TEX_DIR      = os.path.join(STATIC_DIR, 'textures')
TEX_FAITHFUL = os.path.join(TEX_DIR, 'faithful')  # 64x64 Faithful
TEX_JAR      = os.path.join(TEX_DIR, 'jar')       # 16x16 jar fallback
TEX_RENDERS  = os.path.join(TEX_DIR, 'renders')   # 3D webp renders
PRISMARINE_MAP = os.path.join(TEX_DIR, 'prismarine_map.json')


def load_config():
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


# ===================== ICON RESOLVER =====================

_manifest = None
_prismarine_map = None

_ALIASES = {
    'magma_block':    ('block', 'magma'),
    'pumpkin':        ('block', 'pumpkin_side'),
    'melon':          ('block', 'melon_side'),
    'hay_block':      ('block', 'hay_block_side'),
    'dried_kelp_block': ('block', 'dried_kelp_top'),
    'chest':          ('block', 'oak_planks'),
    'trapped_chest':  ('block', 'oak_planks'),
    'ender_chest':    ('block', 'obsidian'),
    'deepslate':      ('block', 'deepslate_top'),
    'bamboo_block':   ('block', 'bamboo_block'),
    'shulker_box':    ('item',  'shulker_box'),
    'snow_block':     ('block', 'snow'),
    'smooth_quartz':  ('block', 'quartz_block_bottom'),
    'smooth_sandstone': ('block', 'sandstone_top'),
    'smooth_red_sandstone': ('block', 'red_sandstone_top'),
    'moss_carpet':    ('block', 'moss_block'),
    'nether_brick_fence': ('block', 'nether_bricks'),
    'sticky_piston':  ('block', 'piston_top_sticky'),
    'compass':        ('item',  'compass_00'),
    'clock':          ('item',  'clock_00'),
    'recovery_compass': ('item', 'recovery_compass_00'),
    'crossbow':       ('item',  'crossbow_arrow'),
    'tipped_arrow':   ('item',  'tipped_arrow_base'),
    'enchanted_golden_apple': ('item', 'golden_apple'),
    'dried_ghast':    ('item',  'ghast_tear'),
    'light_weighted_pressure_plate': ('block', 'gold_block'),
    'heavy_weighted_pressure_plate': ('block', 'iron_block'),
    'stone_button':   ('block', 'stone'),
    'stone_pressure_plate': ('block', 'stone'),
    'polished_blackstone_button': ('block', 'polished_blackstone'),
    'polished_blackstone_pressure_plate': ('block', 'polished_blackstone'),
    'purpur_stairs':  ('block', 'purpur_block'),
    'purpur_slab':    ('block', 'purpur_block'),
}


def _load_manifest():
    global _manifest
    if _manifest is not None:
        return _manifest
    result = {'renders': set(), 'faithful_item': set(), 'faithful_block': set(),
              'jar_item': set(), 'jar_block': set()}
    # 3D renders (webp)
    if os.path.isdir(TEX_RENDERS):
        for f in os.listdir(TEX_RENDERS):
            if f.endswith('.webp'):
                result['renders'].add(f[:-5])
    for kind in ('item', 'block'):
        d = os.path.join(TEX_FAITHFUL, kind)
        if os.path.isdir(d):
            for f in os.listdir(d):
                if f.endswith('.png'):
                    result['faithful_' + kind].add(f[:-4])
        d2 = os.path.join(TEX_JAR, kind)
        if os.path.isdir(d2):
            for f in os.listdir(d2):
                if f.endswith('.png'):
                    result['jar_' + kind].add(f[:-4])
    _manifest = result
    return result


def resolve_icon(item_id):
    """
    Возвращает URL-путь к иконке.
    Приоритет: 3D render (webp) → Faithful 64x → jar 16x → prismarine map.
    """
    m = _load_manifest()
    n = item_id.replace('minecraft:', '')

    # 0. 3D render — наивысший приоритет
    if n in m['renders']:
        return 'renders/' + n + '.webp'

    def check(name):
        if name in m['renders']:
            return 'renders/' + name + '.webp'
        if name in m['faithful_item']:
            return 'faithful/item/' + name
        if name in m['faithful_block']:
            return 'faithful/block/' + name
        if name in m['jar_item']:
            return 'jar/item/' + name
        if name in m['jar_block']:
            return 'jar/block/' + name
        return None

    # 1. Алиас
    if n in _ALIASES:
        kind, aname = _ALIASES[n]
        r = check(aname)
        if r:
            return r

    # 2. Прямое совпадение
    r = check(n)
    if r:
        return r

    # 3. Паттерны преобразования
    cands = []
    if '_wood' in n:
        cands.append(n.replace('_wood', '_log'))
        cands.append(n.replace('stripped_', '').replace('_wood', '_log'))
    if n.endswith('_carpet'):
        cands.append(n[:-7] + '_wool')
    if n.endswith('_slab') or n.endswith('_stairs'):
        base = n.rsplit('_', 1)[0]
        cands += [base, base + 's', base + '_side', base + '_top']
    if n.endswith('_wall'):
        base = n[:-5]
        cands += [base, base + 's']
    if n.endswith('_fence') or n.endswith('_fence_gate'):
        cands.append(n.split('_fence')[0] + '_planks')
        cands.append(n.split('_fence')[0] + 's')
    if n.endswith('_button') or n.endswith('_pressure_plate'):
        base = n.split('_button')[0].split('_pressure')[0]
        cands += [base + '_planks', base, base + '_block']
    if n.startswith('waxed_'):
        cands.append(n[6:])
    if n.endswith('_hyphae'):
        cands.append(n.replace('_hyphae', '_stem'))
    if n.endswith('_bed'):
        cands.append(n.replace('_bed', '_wool'))
    if n.endswith('_banner'):
        cands.append(n.replace('_banner', '_wool'))
    if n.endswith('_stained_glass_pane'):
        cands.append(n.replace('_stained_glass_pane', '_stained_glass'))
    # smooth_*_slab → smooth_* уже обработан выше, но нужен _top
    if n.startswith('smooth_') and not n.endswith(('_slab','_stairs','_wall')):
        cands.append(n + '_top')
    cands += [n + '_side', n + '_top', n + '_front', n + '_0', n + 's']

    for c in cands:
        r = check(c)
        if r:
            return r

    # 4. Prismarine маппинг (финальный fallback)
    global _prismarine_map
    if _prismarine_map is None:
        if os.path.isfile(PRISMARINE_MAP):
            with open(PRISMARINE_MAP, 'r', encoding='utf-8') as f:
                _prismarine_map = json.load(f)
        else:
            _prismarine_map = {}
    tex_path = _prismarine_map.get(n, '')
    if tex_path:
        # tex_path like "block/oak_planks" or "items/compass_16"
        # normalize "items/x" -> "item/x" for our structure
        tex_path = tex_path.replace('items/', 'item/')
        parts = tex_path.split('/', 1)
        if len(parts) == 2:
            kind, tname = parts
            r = check(tname)
            if r:
                return r
    return None


def fmt_name(item_id):
    return item_id.replace('minecraft:', '').replace('_', ' ').title()


# ===== Russian locale =====
_ru_names = None

def _load_ru_names():
    global _ru_names
    if _ru_names is not None:
        return _ru_names
    ru_path = os.path.join(BASE_DIR, 'frontend', 'src', 'lib', 'ru_names.json')
    if os.path.isfile(ru_path):
        with open(ru_path, 'r', encoding='utf-8') as f:
            _ru_names = json.load(f)
    else:
        _ru_names = {}
    return _ru_names


def get_ru_name(item_id):
    m = _load_ru_names()
    n = item_id.replace('minecraft:', '')
    return m.get(n, '')


# ===================== DATA LOADER =====================

_cache_lock = threading.Lock()
_cache = {'warehouses': None, 'items': {}, 'ts': 0, 'mtime': 0}
CACHE_TTL = 5


def _build_items(totals, shulkers):
    items = []
    for item_id, count in totals.items():
        if not isinstance(count, (int, float)) or count <= 0:
            continue
        items.append({
            'id': item_id,
            'name': fmt_name(item_id),
            'name_ru': get_ru_name(item_id),
            'count': int(count),
            'full_shulkers': shulkers.get(item_id, 0),
            'icon': resolve_icon(item_id),
        })
    items.sort(key=lambda x: -x['count'])
    return items


def load_data(cfg):
    path = cfg['data_file'].replace('/', os.sep)
    if not os.path.isfile(path):
        return None, {'error': 'Файл не найден: ' + path}
    try:
        with open(path, 'r', encoding='utf-8') as f:
            raw = json.load(f)
    except Exception as e:
        return None, {'error': 'Ошибка JSON: ' + str(e)}

    shulkers = raw.get('grandFullShulkers', {})
    generated_at = raw.get('generatedAt', '')

    # Собираем список складов
    warehouses = []
    items_by_wh = {}

    for world in raw.get('worlds', []):
        for dim in world.get('dimensions', []):
            wh_id = world['name'] + '/' + dim['name']
            wh_name = dim['name']
            totals = dim.get('totals', {})
            items = _build_items(totals, shulkers)
            warehouses.append({
                'id': wh_id,
                'name': wh_name,
                'item_count': len(items),
                'total_count': sum(i['count'] for i in items),
            })
            items_by_wh[wh_id] = items

    # Добавляем "Все склады" (grandTotals)
    grand_totals = raw.get('grandTotals', {})
    grand_items = _build_items(grand_totals, shulkers)
    warehouses.insert(0, {
        'id': '__all__',
        'name': 'Все склады',
        'item_count': len(grand_items),
        'total_count': sum(i['count'] for i in grand_items),
    })
    items_by_wh['__all__'] = grand_items

    return generated_at, {'warehouses': warehouses, 'items_by_wh': items_by_wh}


def get_cached(cfg):
    with _cache_lock:
        now = time.time()
        path = cfg['data_file'].replace('/', os.sep)
        mtime = os.path.getmtime(path) if os.path.isfile(path) else 0
        if (_cache['warehouses'] is None or
                now - _cache['ts'] > CACHE_TTL or
                mtime != _cache['mtime']):
            gen_at, data = load_data(cfg)
            if 'error' not in data:
                _cache['warehouses'] = data['warehouses']
                _cache['items'] = data['items_by_wh']
                _cache['gen_at'] = gen_at
            _cache['ts'] = now
            _cache['mtime'] = mtime
        return _cache


# ===================== HTTP HANDLER =====================

CONTENT_TYPES = {
    '.png': 'image/png', '.json': 'application/json; charset=utf-8',
    '.css': 'text/css; charset=utf-8', '.js': 'text/javascript; charset=utf-8',
    '.html': 'text/html; charset=utf-8', '.svg': 'image/svg+xml',
}


class Handler(BaseHTTPRequestHandler):
    def _json(self, obj, status=200):
        body = json.dumps(obj, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(body)

    def _file(self, path, ctype, cache=False):
        with open(path, 'rb') as f:
            body = f.read()
        self.send_response(200)
        self.send_header('Content-Type', ctype)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'public, max-age=86400' if cache else 'no-store')
        self.end_headers()
        self.wfile.write(body)

    def _tex(self, rel):
        """Раздаёт текстуры из static/textures/."""
        target = os.path.normpath(os.path.join(TEX_DIR, rel))
        if not target.startswith(TEX_DIR + os.sep) and target != TEX_DIR:
            self._json({'error': 'Forbidden'}, 403); return
        if not os.path.isfile(target):
            self._json({'error': 'Not found'}, 404); return
        ctype = 'image/webp' if target.endswith('.webp') else 'image/png'
        self._file(target, ctype, cache=True)

    def do_GET(self):
        route = self.path.split('?')[0]

        # Статика
        if route in ('/', '/index.html'):
            p = os.path.join(STATIC_DIR, 'index.html')
            self._file(p, 'text/html; charset=utf-8') if os.path.isfile(p) else self._json({'error': 'Not found'}, 404)
            return

        if route.startswith('/textures/'):
            self._tex(route[len('/textures/'):])
            return

        # API
        if route == '/api/warehouses':
            cfg = load_config()
            c = get_cached(cfg)
            if c['warehouses'] is None:
                self._json({'error': 'Данные не загружены'}, 500); return
            self._json({
                'warehouses': c['warehouses'],
                'generated_at': c.get('gen_at', ''),
            })
            return

        if route.startswith('/api/items'):
            # /api/items?wh=__all__
            wh_id = '__all__'
            if '?' in self.path:
                qs = self.path.split('?', 1)[1]
                for part in qs.split('&'):
                    if part.startswith('wh='):
                        import urllib.parse
                        wh_id = urllib.parse.unquote(part[3:])
            cfg = load_config()
            c = get_cached(cfg)
            items = c.get('items', {}).get(wh_id)
            if items is None:
                self._json({'error': 'Склад не найден: ' + wh_id}, 404); return
            wh_info = next((w for w in (c['warehouses'] or []) if w['id'] == wh_id), {})
            self._json({
                'warehouse_id': wh_id,
                'warehouse_name': wh_info.get('name', wh_id),
                'generated_at': c.get('gen_at', ''),
                'items': items,
                'stats': {
                    'unique_items': len(items),
                    'total_count': sum(i['count'] for i in items),
                },
            })
            return

        if route == '/api/config':
            cfg = load_config()
            self._json({'refresh_interval': cfg.get('refresh_interval', 15),
                        'data_file': os.path.basename(cfg.get('data_file', ''))})
            return

        self._json({'error': 'Not found'}, 404)

    def log_message(self, fmt, *args):
        print('  [' + self.log_date_time_string() + '] ' + self.requestline)


def main():
    cfg = load_config()
    host = cfg.get('host', '0.0.0.0')
    port = cfg.get('port', 8000)
    display = '127.0.0.1' if host == '0.0.0.0' else host
    server = ThreadingHTTPServer((host, port), Handler)
    print('=' * 50)
    print('  Chest Tracker Web Server')
    print('  http://' + display + ':' + str(port))
    if host == '0.0.0.0':
        print('  Для сети: http://<IP>:' + str(port))
    print('  Ctrl+C для остановки')
    print('=' * 50)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()


if __name__ == '__main__':
    main()
