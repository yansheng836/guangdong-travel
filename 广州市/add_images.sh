#!/bin/bash
# Script to add images to Guangzhou attraction files from Wikimedia Commons

cd "F:/workspace/plain-project/guangdong-travel/广州市"

SUCCESS_COUNT=0
FAIL_COUNT=0
SKIP_COUNT=0
TOTAL=0

# Function to URL-encode a string
urlencode() {
    python3 -c "import urllib.parse; print(urllib.parse.quote('$1'))"
}

# Function to search Wikimedia Commons and get image URL
search_commons() {
    local name="$1"
    local encoded_name
    encoded_name=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$name'))")

    # Search Wikimedia Commons API
    local search_url="https://commons.wikimedia.org/w/api.php?action=query&list=search&srsearch=${encoded_name}&srnamespace=6&format=json&utf8=1&srlimit=5"
    local search_result
    search_result=$(curl -s -A "Mozilla/5.0 (compatible; ImageBot/1.0)" "$search_url" 2>/dev/null)

    if [ -z "$search_result" ]; then
        echo ""
        return
    fi

    # Extract first file title
    local file_title
    file_title=$(echo "$search_result" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    results = data.get('query', {}).get('search', [])
    for r in results:
        title = r.get('title', '')
        if title.startswith('File:'):
            print(title)
            break
except:
    pass
" 2>/dev/null)

    if [ -z "$file_title" ]; then
        echo ""
        return
    fi

    # Get image info (URL)
    local encoded_title
    encoded_title=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$file_title'))")
    local info_url="https://commons.wikimedia.org/w/api.php?action=query&titles=${encoded_title}&prop=imageinfo&iiprop=url&format=json&utf8=1"
    local info_result
    info_result=$(curl -s -A "Mozilla/5.0 (compatible; ImageBot/1.0)" "$info_url" 2>/dev/null)

    if [ -z "$info_result" ]; then
        echo ""
        return
    fi

    # Extract image URL
    local image_url
    image_url=$(echo "$info_result" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    pages = data.get('query', {}).get('pages', {})
    for pid, page in pages.items():
        imageinfo = page.get('imageinfo', [])
        if imageinfo:
            print(imageinfo[0].get('url', ''))
except:
    pass
" 2>/dev/null)

    echo "$image_url|$file_title"
}

# Process each file
for f in *.md; do
    # Skip non-attraction files
    if [ "$f" = "README.md" ] || [ "$f" = "_sidebar.md" ] || [ "$f" = "TEMPLATE.md" ] || [ "$f" = "add_images.sh" ]; then
        continue
    fi

    # Check if already has image
    if grep -qE '!\[|暂未找到照片' "$f" 2>/dev/null; then
        SKIP_COUNT=$((SKIP_COUNT + 1))
        continue
    fi

    TOTAL=$((TOTAL + 1))

    # Extract attraction name from first heading
    local name
    name=$(head -5 "$f" | grep '^# ' | head -1 | sed 's/^# //')
    if [ -z "$name" ]; then
        echo "[$TOTAL] SKIP (no name): $f"
        FAIL_COUNT=$((FAIL_COUNT + 1))
        continue
    fi

    echo "[$TOTAL] Processing: $name ($f)"

    # Search Wikimedia Commons
    local result
    result=$(search_commons "$name")

    if [ -n "$result" ]; then
        local image_url=$(echo "$result" | cut -d'|' -f1)
        local file_title=$(echo "$result" | cut -d'|' -f2-)

        if [ -n "$image_url" ]; then
            # Verify URL is accessible
            local http_code
            http_code=$(curl -s -o /dev/null -w "%{http_code}" -A "Mozilla/5.0 (compatible; ImageBot/1.0)" "$image_url" 2>/dev/null)

            if [ "$http_code" = "200" ]; then
                # Build the commons page URL
                local commons_page="https://commons.wikimedia.org/wiki/${file_title}"

                # Create the image section
                local image_section="## 景点图片

![${name}](${image_url})

> 图片来源：[Wikimedia Commons](${commons_page}) · 许可证：CC BY-SA 4.0

"

                # Insert after first heading, before ## 基本信息
                python3 -c "
import sys

with open('$f', 'r', encoding='utf-8') as file:
    content = file.read()

# Find the position after '# name\n' and before '## 基本信息'
lines = content.split('\n')
new_lines = []
inserted = False
for i, line in enumerate(lines):
    new_lines.append(line)
    if not inserted and line.startswith('# ') and i == 0:
        # Insert image section after the heading
        new_lines.append('')
        new_lines.append('## 景点图片')
        new_lines.append('')
        new_lines.append('![${name}](${image_url})')
        new_lines.append('')
        new_lines.append('> 图片来源：[Wikimedia Commons](${commons_page}) · 许可证：CC BY-SA 4.0')
        new_lines.append('')
        inserted = True

with open('$f', 'w', encoding='utf-8') as file:
    file.write('\n'.join(new_lines))
"

                echo "  -> SUCCESS: Added image from $file_title"
                SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
            else
                echo "  -> FAIL: Image URL returned HTTP $http_code"
                # Add placeholder
                python3 -c "
with open('$f', 'r', encoding='utf-8') as file:
    content = file.read()

lines = content.split('\n')
new_lines = []
inserted = False
for i, line in enumerate(lines):
    new_lines.append(line)
    if not inserted and line.startswith('# ') and i == 0:
        new_lines.append('')
        new_lines.append('## 景点图片')
        new_lines.append('')
        new_lines.append('> 📷 暂未找到照片')
        new_lines.append('')
        inserted = True

with open('$f', 'w', encoding='utf-8') as file:
    file.write('\n'.join(new_lines))
"
                FAIL_COUNT=$((FAIL_COUNT + 1))
            fi
        else
            echo "  -> FAIL: No image URL found"
            # Add placeholder
            python3 -c "
with open('$f', 'r', encoding='utf-8') as file:
    content = file.read()

lines = content.split('\n')
new_lines = []
inserted = False
for i, line in enumerate(lines):
    new_lines.append(line)
    if not inserted and line.startswith('# ') and i == 0:
        new_lines.append('')
        new_lines.append('## 景点图片')
        new_lines.append('')
        new_lines.append('> 📷 暂未找到照片')
        new_lines.append('')
        inserted = True

with open('$f', 'w', encoding='utf-8') as file:
    file.write('\n'.join(new_lines))
"
            FAIL_COUNT=$((FAIL_COUNT + 1))
        fi
    else
        echo "  -> FAIL: No results from Wikimedia Commons"
        # Add placeholder
        python3 -c "
with open('$f', 'r', encoding='utf-8') as file:
    content = file.read()

lines = content.split('\n')
new_lines = []
inserted = False
for i, line in enumerate(lines):
    new_lines.append(line)
    if not inserted and line.startswith('# ') and i == 0:
        new_lines.append('')
        new_lines.append('## 景点图片')
        new_lines.append('')
        new_lines.append('> 📷 暂未找到照片')
        new_lines.append('')
        inserted = True

with open('$f', 'w', encoding='utf-8') as file:
    file.write('\n'.join(new_lines))
"
        FAIL_COUNT=$((FAIL_COUNT + 1))
    fi

    # Wait 2-3 seconds between requests
    sleep 2.5
done

echo ""
echo "========================================="
echo "Processing complete!"
echo "Total processed: $TOTAL"
echo "Successfully added images: $SUCCESS_COUNT"
echo "Placeholder (no photo): $FAIL_COUNT"
echo "Already had images (skipped): $SKIP_COUNT"
echo "========================================="
