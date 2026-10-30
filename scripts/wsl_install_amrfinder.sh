#!/bin/bash
set -e
cd /tmp

echo "=== Checking AMRFinderPlus releases ==="
curl -sL 'https://api.github.com/repos/NCBIAMRFinder/amrfinder/releases/latest' -o release.json 2>/dev/null

python3 << 'PYEOF'
import json
try:
    with open('release.json') as f:
        d = json.load(f)
    print(f"Tag: {d.get('tag_name', 'unknown')}")
    print("Assets:")
    for a in d.get('assets', []):
        print(f"  {a['name']} ({a['size']//1024} KB)")
except Exception as e:
    print(f"Error: {e}")
PYEOF

echo ""
echo "=== Downloading ==="
# Try the first linux tarball
URL=$(python3 -c "
import json
try:
    with open('release.json') as f:
        d = json.load(f)
    for a in d.get('assets', []):
        if 'linux' in a['name'].lower() and 'tar' in a['name'].lower():
            print(a['browser_download_url'])
            exit(0)
except:
    pass
print('')
")

if [ -n "$URL" ]; then
    echo "Downloading: $URL"
    curl -L "$URL" -o amrfinder.tar.gz 2>/dev/null
    if [ -s amrfinder.tar.gz ]; then
        echo "Download successful: $(wc -c < amrfinder.tar.gz) bytes"
        mkdir -p amrfinder_install
        tar xzf amrfinder.tar.gz -C amrfinder_install 2>/dev/null || true
        ls -la amrfinder_install/
    else
        echo "Download failed or empty"
    fi
else
    echo "No Linux binary found in release"
fi

# Check if we got anything
if [ -f amrfinder_install/amrfinder ] || [ -f amrfinder_install/bin/amrfinder ]; then
    BINARY=$(find amrfinder_install -name 'amrfinder' -type f | head -1)
    echo "Found binary: $BINARY"
    mkdir -p ~/.local/bin
    cp "$BINARY" ~/.local/bin/amrfinder
    chmod +x ~/.local/bin/amrfinder
    export PATH="$HOME/.local/bin:$PATH"
    amrfinder --version
    echo "SUCCESS: AMRFinderPlus installed!"
else
    echo "FAILED: Could not install AMRFinderPlus"
    echo "Manual installation required:"
    echo "  1. Go to https://github.com/NCBIAMRFinder/amrfinder/releases"
    echo "  2. Download the linux tarball"
    echo "  3. Extract and copy amrfinder to ~/.local/bin/"
    echo "  4. Download database: amrfinder --update_now"
fi
