#!/usr/bin/env python3
import json
import subprocess
import os

# Product detail URLs
urls = [
    "https://www.artidaoud.com/item/detail/1_1_12263105031/10",
    "https://www.artidaoud.com/item/detail/1_1_12263105030/20",
    "https://www.artidaoud.com/item/detail/1_1_12263105029/20",
    "https://www.artidaoud.com/item/detail/1_1_12263105028/20",
    "https://www.artidaoud.com/item/detail/1_1_12263105027/31",
    "https://www.artidaoud.com/item/detail/1_1_12263105026/31",
    "https://www.artidaoud.com/item/detail/1_1_12263105025/47",
    "https://www.artidaoud.com/item/detail/1_1_12263105024/26",
    "https://www.artidaoud.com/item/detail/1_1_12263105023/41",
    "https://www.artidaoud.com/item/detail/1_1_12263105022/43",
    "https://www.artidaoud.com/item/detail/1_1_12263105021/10",
    "https://www.artidaoud.com/item/detail/1_1_12263105020/43",
    "https://www.artidaoud.com/item/detail/1_1_12263205019/17",
    "https://www.artidaoud.com/item/detail/1_1_12263205018/17",
    "https://www.artidaoud.com/item/detail/1_1_12263205017/20",
    "https://www.artidaoud.com/item/detail/1_1_12263205015/20",
    "https://www.artidaoud.com/item/detail/1_1_12263205014/10",
    "https://www.artidaoud.com/item/detail/1_1_12261205010/04",
]

manifest = []
output_dir = "/home/admin/japan-jewelry-pics/pics/artida-oud"

for idx, url in enumerate(urls[:16], start=1):
    print(f"\n[{idx}/16] Processing: {url}")
    
    # Use browser-use to get og:image
    script = f'''
new_tab("{url}")
wait_for_load()
result = js("""
const og = document.querySelector('meta[property="og:image"]');
const title = document.querySelector('title');
JSON.stringify({{ogUrl: og ? og.content : null, title: title ? title.textContent : null}});
""")
print(result)
'''
    
    try:
        proc = subprocess.run(
            ["browser-use"],
            input=script,
            capture_output=True,
            text=True,
            timeout=30,
            cwd="/home/admin/japan-jewelry-pics"
        )
        
        output = proc.stdout.strip()
        print(f"Output: {output}")
        
        # Parse the output
        data = json.loads(output)
        og_url = data.get('ogUrl')
        title = data.get('title', '').replace('｜ARTIDA OUD（アルティーダ ウード）', '').strip()
        
        if og_url:
            # Download the image
            filename = f"{idx:02d}.jpg"
            filepath = os.path.join(output_dir, filename)
            
            curl_cmd = ["curl", "-s", "-L", "-o", filepath, og_url]
            subprocess.run(curl_cmd, timeout=30)
            
            # Add to manifest
            manifest.append({
                "file": filename,
                "source_page": url,
                "image_url": og_url,
                "product": title
            })
            
            print(f"✓ Saved: {filename} - {title}")
        else:
            print(f"✗ No og:image found")
            
    except Exception as e:
        print(f"✗ Error: {e}")

# Write manifest
manifest_path = os.path.join(output_dir, "manifest.json")
with open(manifest_path, "w", encoding="utf-8") as f:
    json.dump(manifest, f, ensure_ascii=False, indent=2)

print(f"\n\nDONE: Saved {len(manifest)} images from {len(manifest)} distinct detail pages")
print(f"Manifest: {manifest_path}")
