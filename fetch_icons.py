"""
fetch_icons.py
Скачивает иконки всех предметов из containers.json с minecraft.wiki.
Использует MediaWiki API для поиска точного имени файла.
Только стандартная библиотека Python.
"""

import json
import os
import time
import urllib.request
import urllib.parse
import urllib.error

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, 'region', 'containers.json')
OUT_DIR   = os.path.join(BASE_DIR, 'static', 'textures', 'wiki')
WIKI_API  = 'https://minecraft.wiki/api.php'
DELAY     = 0.3   # секунд между запросами (не перегружаем wiki)
TIMEOUT   = 15


def to_wiki_prefix(item_id):
    """minecraft:white_wool -> White_Wool"""
    name = item_id.replace('minecraft:', '')
    return '_'.join(w.capitalize() for w in name.split('_'))


def _query_images(prefix, limit=20, descending=True):
    """Запрашивает список изображений с wiki по префиксу."""
    params = urllib.parse.urlencode({
        'action': 'query', 'list': 'allimages',
        'aiprefix': prefix, 'ailimit': str(limit),
        'aisort': 'name',
        'aidir': 'descending' if descending else 'ascending',
        'format': 'json',
    })
    try:
        req = urllib.request.Request(
            WIKI_API + '?' + params,
            headers={'User-Agent': 'ChestTrackerBot/1.0'})
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            data = json.loads(r.read().decode('utf-8'))
        return data.get('query', {}).get('allimages', [])
    except Exception:
        return []


def _best(images):
    """Выбирает лучшую иконку из списка."""
    BAD = ('(facing', 'Revision', 'MCD', 'Texture)', '_item_model',
           '3D', 'Render', 'Screenshot', '.gif')
    good = [img for img in images
            if img['name'].endswith('.png')
            and not any(b in img['name'] for b in BAD)]
    if not good:
        good = [img for img in images if img['name'].endswith('.png')]
    if not good:
        return None, None
    best = good[0]
    return best['url'].split('?')[0], best['name']


def find_icon_url(prefix):
    """
    Ищет иконку для предмета через wiki API.
    Стратегия: _JE -> прямое совпадение -> без суффикса.
    Возвращает (url, filename) или (None, None).
    """
    # 1. Ищем PREFIX_JE... (самый надёжный вариант)
    imgs = _query_images(prefix + '_JE')
    url, name = _best(imgs)
    if url:
        return url, name
    time.sleep(DELAY)

    # 2. Прямое совпадение: PREFIX.png или PREFIX_BE...
    imgs = _query_images(prefix + '_BE')
    url, name = _best(imgs)
    if url:
        return url, name
    time.sleep(DELAY)

    # 3. Просто PREFIX — блоки без суффиксов (Gold_Block.png и т.д.)
    imgs = _query_images(prefix, limit=5, descending=False)
    # Берём только если имя == PREFIX.png (точное)
    exact = [img for img in imgs
             if img['name'] == prefix + '.png']
    if exact:
        best = exact[0]
        return best['url'].split('?')[0], best['name']

    return None, None


def download(url, dest_path):
    """Скачивает файл, возвращает True при успехе."""
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'ChestTrackerBot/1.0'})
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            data = r.read()
        with open(dest_path, 'wb') as f:
            f.write(data)
        return True
    except Exception as e:
        return False


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    # Загружаем список предметов
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        raw = json.load(f)
    items = list(raw.get('grandTotals', {}).keys())
    print(f"Предметов: {len(items)}")
    print(f"Папка: {OUT_DIR}")
    print()

    ok = skip = fail = 0
    fail_list = []

    for i, item_id in enumerate(items, 1):
        name = item_id.replace('minecraft:', '')
        dest = os.path.join(OUT_DIR, name + '.png')

        # Пропускаем уже скачанные
        if os.path.isfile(dest) and os.path.getsize(dest) > 100:
            skip += 1
            continue

        prefix = to_wiki_prefix(item_id)
        print(str(i).rjust(4) + '/' + str(len(items)) + ' ' + name.ljust(42), end=' ', flush=True)

        img_url, img_name = find_icon_url(prefix)

        if not img_url:
            print("НЕТ НА WIKI")
            fail += 1
            fail_list.append(item_id)
            continue

        if download(img_url, dest):
            print('OK  (' + img_name + ')')
            ok += 1
        else:
            print('ОШИБКА ЗАГРУЗКИ')
            fail += 1
            fail_list.append(item_id)

        time.sleep(DELAY)

    print()
    print('='*55)
    print('  Скачано:   ' + str(ok))
    print('  Пропущено: ' + str(skip))
    print('  Ошибки:    ' + str(fail))
    if fail_list:
        print('\nНе найдено на wiki:')
        for x in fail_list:
            print('  ' + x)
    print('='*55)


if __name__ == '__main__':
    main()
