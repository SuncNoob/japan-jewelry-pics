"""Run Codex on the Agent Computer so Wuying gateway sessions are visible."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

CODEX_TIMEOUT_SECONDS = 1200
CODEX_LEASE_SECONDS = 1800


def codex_bin() -> str | None:
    return shutil.which("codex")


def jewelry_prompt(brand: str, url: str, allow_hosts: list[str], limit: int, pic_dir: str) -> str:
    hosts = ", ".join(allow_hosts)
    return f"""You are a 无影 Computer Agent. Use THIS machine's Codex tools and the browser-use MCP (real browser) so the session is visible in the Wuying console. Consume this Agent Computer's own Wuying gateway token. Do not ask for approval.

Brand: {brand}
Official start URL: {url}
Image output directory (create if needed): {pic_dir}
Max product photos: {limit}
Allowed hosts only: {hosts}

Do this:
1. Open the official site in the browser. Do not use a search engine as the source of images.
2. From the listing, click into at least 4 product detail pages (子页面 / individual jewelry items).
3. On each product page, download the actual product photo (the jewelry) into {pic_dir} as jpg/png/webp. Use curl or the browser. Filenames like 01.jpg, 02.jpg.
4. Skip logos, favicons, banners, payment icons, and empty placeholders.
5. Do not visit or save images from hosts outside the allow list.
6. Write {pic_dir}/manifest.json as [{{"file":"01.jpg","source_page":"...","image_url":"..."}}].

When finished, print DONE and the list of saved files. If the site blocks you, print FAIL and why.
"""


def run_codex(prompt: str, cwd: Path, timeout: int = CODEX_TIMEOUT_SECONDS) -> dict:
    binary = codex_bin()
    if not binary:
        return {"ok": False, "code": 127, "stdout": "", "stderr": "codex not found", "cmd": []}
    cwd = cwd.resolve()
    cmd = [
        binary,
        "exec",
        "--dangerously-bypass-approvals-and-sandbox",
        "-s",
        "danger-full-access",
        "-C",
        str(cwd),
        "-c",
        f'projects."{cwd}".trust_level="trusted"',
        prompt,
    ]
    env = os.environ.copy()
    env.setdefault("HOME", str(Path.home()))
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(cwd),
            env=env,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
        stdout = proc.stdout.decode("utf-8", "replace")
        stderr = proc.stderr.decode("utf-8", "replace")
        return {
            "ok": proc.returncode == 0,
            "code": proc.returncode,
            "stdout": stdout[-8000:],
            "stderr": stderr[-4000:],
            "cmd": cmd[:8],
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "ok": False,
            "code": 124,
            "stdout": (exc.stdout or b"").decode("utf-8", "replace")[-4000:],
            "stderr": "codex exec timed out",
            "cmd": cmd[:8],
        }
    except OSError as exc:
        return {"ok": False, "code": 1, "stdout": "", "stderr": str(exc), "cmd": cmd[:8]}
