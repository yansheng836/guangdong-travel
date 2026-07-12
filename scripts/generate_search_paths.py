"""Generate search paths for Docsify search plugin.

Scans all city directories for .md attraction files and generates
the paths array for the Docsify search configuration in index.html.
"""

import os
import re

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX_HTML = os.path.join(ROOT_DIR, 'index.html')

# 21 prefecture-level cities in Guangdong
CITIES = [
    '广州市', '深圳市', '珠海市', '汕头市', '佛山市', '韶关市',
    '河源市', '梅州市', '惠州市', '汕尾市', '东莞市', '中山市',
    '江门市', '阳江市', '湛江市', '茂名市', '肇庆市', '清远市',
    '潮州市', '揭阳市', '云浮市',
]


def collect_paths():
    paths = []
    for city in CITIES:
        city_dir = os.path.join(ROOT_DIR, city)
        if not os.path.isdir(city_dir):
            continue
        fnames = sorted(f for f in os.listdir(city_dir)
                        if f.endswith('.md') and f != 'README.md'
                        and not f.startswith('_'))
        for fname in fnames:
            path = '/' + city + '/' + fname.replace('.md', '')
            paths.append(path)
    paths.insert(0, '/')
    return paths


def generate_paths_js(paths):
    """Generate the JavaScript paths array as a string."""
    lines = ['        paths: [']
    for p in paths:
        lines.append(f"          '{p}',")
    lines.append('        ],')
    return '\n'.join(lines)


def update_index_html(paths_js):
    with open(INDEX_HTML, 'r', encoding='utf-8') as f:
        content = f.read()

    # Try to replace existing paths array
    pattern = r'        paths: \[[\s\S]*?        \],'
    if re.search(pattern, content):
        content = re.sub(pattern, paths_js, content)
        with open(INDEX_HTML, 'w', encoding='utf-8') as f:
            f.write(content)
        print('index.html updated successfully.')
        return True

    # No existing paths array — insert one after maxAge line
    insert_after = '        maxAge: 86400000,'
    if insert_after in content:
        content = content.replace(insert_after, insert_after + '\n' + paths_js, 1)
        with open(INDEX_HTML, 'w', encoding='utf-8') as f:
            f.write(content)
        print('index.html updated (inserted new paths array).')
        return True

    print('ERROR: Could not find insertion point in index.html.')
    return False


def main():
    paths = collect_paths()
    print(f'Found {len(paths)} paths ({len(paths) - 1} attractions).')
    paths_js = generate_paths_js(paths)
    update_index_html(paths_js)


if __name__ == '__main__':
    main()