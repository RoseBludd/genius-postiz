#!/usr/bin/env python3
"""Patch Postiz image with Genius branding."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path("/app")
ICON = Path("/tmp/genius-logo-icon.png")
WORDMARK = Path("/tmp/genius-logo-wordmark.png")
CUSTOM_CSS = Path("/app/custom.css")

REPLACEMENTS = [
    ("Postiz Login", "Genius Login"),
    ("Postiz Register", "Genius Register"),
    ("Gitroom Login", "Genius Login"),
    ("Gitroom Register", "Genius Register"),
    ("Gitroom", "Genius"),
    ("Postiz To Grow Their Social Presence", "Genius To Grow Their Social Presence"),
    ("Postiz", "Genius"),
    ("postiz", "genius"),
]

BRAND_COLOR_REPLACEMENTS = [
    ("#612BD3", "#2563eb"),
    ("#612bd3", "#2563eb"),
    ("#FC69FF", "#5b9cff"),
    ("#fc69ff", "#5b9cff"),
]

LOGO_IMG = (
    '<img src="/favicon.png" alt="Genius" width="60" height="60" '
    'class="mt-[8px] min-w-[60px] min-h-[60px] w-[60px] h-[60px] rounded-[12px] object-contain" />'
)

LOGO_COMPONENT = """'use client';

export const Logo = () => {
  return (
    <img
      src="/favicon.png"
      alt="Genius"
      width={60}
      height={60}
      className="mt-[8px] min-w-[60px] min-h-[60px] w-[60px] h-[60px] rounded-[12px] object-contain"
    />
  );
};
"""

SVG_LOGO_RE = re.compile(
    r'<svg[^>]*viewBox="0 0 60 60"[^>]*>.*?</svg>',
    re.DOTALL,
)
AUTH_WORDMARK_SVG_RE = re.compile(
    r'<svg[^>]*viewBox="0 0 101 33"[^>]*>.*?</svg>',
    re.DOTALL,
)
AUTH_WORDMARK_IMG = (
    '<img src="/genius-wordmark.png" alt="Genius" width="180" height="40" '
    'style="display:block;margin:0 auto 20px auto" />'
)


def write_favicon_ico(dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        from PIL import Image

        src = Image.open(ICON).convert("RGBA")
        src.save(dest, format="ICO", sizes=[(16, 16), (32, 32), (48, 48)])
        return
    except Exception:
        pass
    dest.write_bytes(ICON.read_bytes())


def replace_public_assets() -> None:
    public_dirs = list(ROOT.glob("apps/frontend/public"))
    public_dirs.extend(ROOT.glob("**/public"))
    seen: set[Path] = set()
    for public in public_dirs:
        if not public.is_dir() or public in seen:
            continue
        seen.add(public)
        public.mkdir(parents=True, exist_ok=True)
        (public / "genius-icon.png").write_bytes(ICON.read_bytes())
        (public / "genius-wordmark.png").write_bytes(WORDMARK.read_bytes())
        for name in (
            "favicon.png",
            "postiz-fav.png",
            "logo.png",
        ):
            (public / name).write_bytes(ICON.read_bytes())
        write_favicon_ico(public / "favicon.ico")

        wordmark_svg = (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 240 48" role="img" aria-label="Genius">'
            '<image href="/genius-wordmark.png" width="240" height="48"/></svg>'
        )
        icon_svg = (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" role="img" aria-label="Genius">'
            '<image href="/genius-icon.png" width="64" height="64"/></svg>'
        )
        for name, content in (
            ("logo.svg", icon_svg),
            ("postiz.svg", icon_svg),
            ("logo-text.svg", wordmark_svg),
            ("postiz-text.svg", wordmark_svg),
        ):
            (public / name).write_text(content, encoding="utf-8")


def scrub_text() -> None:
    targets: list[Path] = []
    for pattern in ("apps/frontend/.next", "apps/frontend/public"):
        targets.extend(ROOT.glob(f"{pattern}/**/*"))
    for path in targets:
        if not path.is_file() or path.suffix not in {".js", ".html", ".json", ".css", ".rsc"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            continue
        original = text
        for old, new in REPLACEMENTS:
            text = text.replace(old, new)
        for old, new in BRAND_COLOR_REPLACEMENTS:
            text = text.replace(old, new)
        if text != original:
            path.write_text(text, encoding="utf-8")


def patch_logo_component() -> None:
    logo_path = ROOT / "apps/frontend/src/components/new-layout/logo.tsx"
    if logo_path.parent.exists():
        logo_path.write_text(LOGO_COMPONENT, encoding="utf-8")

    logo_text = ROOT / "apps/frontend/src/components/ui/logo-text.component.tsx"
    if logo_text.parent.exists():
        logo_text.write_text(
            """import React from 'react';

export const LogoTextComponent = () => {
  return (
    <img
      src="/genius-wordmark.png"
      alt="Genius"
      width={180}
      height={40}
      className="object-contain"
    />
  );
};
""",
            encoding="utf-8",
        )


def patch_inline_logos() -> None:
    """Swap baked-in Postiz SVG logos in prebuilt Next.js output for Genius images."""
    targets: list[Path] = []
    for pattern in ("apps/frontend/.next", "apps/frontend/public"):
        targets.extend(ROOT.glob(f"{pattern}/**/*"))
    for path in targets:
        if not path.is_file() or path.suffix not in {".js", ".html", ".json", ".rsc"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            continue
        original = text
        text = SVG_LOGO_RE.sub(LOGO_IMG, text)
        text = AUTH_WORDMARK_SVG_RE.sub(AUTH_WORDMARK_IMG, text)
        if text != original:
            path.write_text(text, encoding="utf-8")


def patch_auth_cookies() -> None:
    """Use host-only cookies on Railway; .railway.app is rejected on *.up.railway.app (PSL)."""
    patched_ts = """export function getCookieUrlFromDomain(domain: string) {
  const url = parse(domain);
  if (!url.hostname) return '';
  // Host-only cookies: parent-domain .railway.app is rejected on *.up.railway.app (PSL).
  if (url.hostname.endsWith('railway.app')) return url.hostname;
  return url.domain! ? '.' + url.domain! : url.hostname!;
}
"""
    for path in ROOT.rglob("subdomain.management.ts"):
        path.write_text(patched_ts, encoding="utf-8")

    for path in ROOT.rglob("subdomain.management.js"):
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            continue
        new_text = re.sub(
            r"return\s+url\.domain\s*\?\s*['\"]\.['\"]\s*\+\s*url\.domain\s*:\s*url\.hostname\s*;?",
            "if (!url.hostname) return ''; "
            "if (url.hostname.endsWith('railway.app')) return url.hostname; "
            "return url.domain ? '.' + url.domain : url.hostname;",
            text,
        )
        if new_text != text:
            path.write_text(new_text, encoding="utf-8")


def inject_custom_css() -> None:
    if not CUSTOM_CSS.exists():
        return
    css = CUSTOM_CSS.read_text(encoding="utf-8")
    for public in ROOT.glob("apps/frontend/public"):
        dest = public / "genius.css"
        dest.write_text(css, encoding="utf-8")

    for html_path in ROOT.glob("apps/frontend/.next/**/*.html"):
        try:
            html = html_path.read_text(encoding="utf-8")
        except Exception:
            continue
        if "/genius.css" in html:
            continue
        html = html.replace("</head>", '  <link rel="stylesheet" href="/genius.css" />\n</head>', 1)
        html_path.write_text(html, encoding="utf-8")

    layout = ROOT / "apps/frontend/src/app/layout.tsx"
    if layout.exists():
        text = layout.read_text(encoding="utf-8")
        if "genius.css" not in text:
            text = text.replace(
                'export default function RootLayout',
                'const geniusCss = "/genius.css";\n\nexport default function RootLayout',
                1,
            )
            text = re.sub(
                r"(<head[^>]*>)",
                r'\1<link rel="stylesheet" href="/genius.css" />',
                text,
                count=1,
            )
            layout.write_text(text, encoding="utf-8")


def main() -> None:
    replace_public_assets()
    patch_logo_component()
    patch_inline_logos()
    scrub_text()
    patch_auth_cookies()
    inject_custom_css()


if __name__ == "__main__":
    main()
