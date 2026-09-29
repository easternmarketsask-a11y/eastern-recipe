"""Install reviewed AI recipe illustrations from a local id-to-PNG manifest.

Usage: python scripts/install_recipe_images.py _incoming/image-manifest.json
Original photographs are retained; new filenames avoid stale image caches.
"""
import json
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


def main():
    manifest = json.loads(Path(sys.argv[1]).read_text(encoding='utf-8-sig'))
    path = ROOT / 'data/recipes.json'
    data = json.loads(path.read_text(encoding='utf-8'))
    index = {r['id']: r for r in data['recipes']}
    for rid, source in manifest.items():
        recipe = index[rid]
        rel = f'assets/images/{rid}-ai-202609.jpg'
        with Image.open(source) as im:
            im.convert('RGB').save(ROOT / rel, quality=90, optimize=True)
        recipe['image'] = rel
        recipe['image_credit'] = 'AI-generated illustration; OpenAI imagegen, 2026-09-29'
    # The bound product is minced pork; name, steps and image must agree.
    pork = index['pork-green-pepper']
    pork['name_cn'] = '青椒肉末'
    pork['name_en'] = 'Minced Pork with Green Peppers'
    pork['steps'][0] = '猪肉末加生抽、料酒、淀粉、少许油抓匀，冷藏腌制10分钟。'
    pork['steps'][-1] = '倒回炒好的肉末，加生抽、少许盐和1汤匙水炒匀，肉末中心达到71°C后出锅。'
    # Make the specialty root useful to first-time cooks without medicinal claims.
    root = index['pueraria-pork-soup']
    root['steps'][0] = '粉葛是广东常用的煲汤根茎，汤味清甜、煮后带粉糯感；它与沙葛是不同食材。约2小时，4人份。粉葛削皮切厚块；猪筒骨冷水下锅，煮开后再煮3分钟，捞出用温水冲净浮沫。'
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'Installed {len(manifest)} reviewed illustrations')


if __name__ == '__main__':
    main()
