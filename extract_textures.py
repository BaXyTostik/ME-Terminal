"""
Извлекает текстуры предметов и блоков из client .jar Minecraft.
Кладёт PNG в static/textures/item и static/textures/block,
создаёт manifest.json со списком доступных имён для резолва иконок в JS.
Только стандартная библиотека.
"""

import os
import sys
import json
import zipfile

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(BASE_DIR, 'static', 'textures')

# Путь к jar можно передать аргументом, иначе берём дефолтный
DEFAULT_JAR = (
    r"C:\Users\Kosty\AppData\Roaming\.minecraft\versions\1.21.8\1.21.8.jar"
)

PREFIXES = {
    'item': 'assets/minecraft/textures/item/',
    'block': 'assets/minecraft/textures/block/',
}


def extract(jar_path):
    if not os.path.isfile(jar_path):
        print(f"[ОШИБКА] jar не найден: {jar_path}")
        return False

    manifest = {'item': [], 'block': []}
    total = 0

    with zipfile.ZipFile(jar_path) as z:
        for kind, prefix in PREFIXES.items():
            out_sub = os.path.join(OUT_DIR, kind)
            os.makedirs(out_sub, exist_ok=True)
            for entry in z.namelist():
                if not entry.startswith(prefix) or not entry.endswith('.png'):
                    continue
                name = entry[len(prefix):]
                # пропускаем вложенные папки (например item/goat_horn/...)
                if '/' in name:
                    continue
                with z.open(entry) as src:
                    data = src.read()
                with open(os.path.join(out_sub, name), 'wb') as dst:
                    dst.write(data)
                manifest[kind].append(name[:-4])  # без .png
                total += 1

    with open(os.path.join(OUT_DIR, 'manifest.json'), 'w', encoding='utf-8') as f:
        json.dump(manifest, f)

    print(f"Извлечено текстур: {total}")
    print(f"  item:  {len(manifest['item'])}")
    print(f"  block: {len(manifest['block'])}")
    print(f"Папка: {OUT_DIR}")
    return True


if __name__ == '__main__':
    jar = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_JAR
    print(f"Извлечение из: {jar}")
    extract(jar)
