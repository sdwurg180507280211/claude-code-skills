#!/usr/bin/env python3
"""Apply Guangyu Online-style interview cards to xiaohu-wechat-format HTML.

This is a narrow brand adapter. It does not parse Markdown, write medical content,
generate images, or publish to WeChat. It only restyles xiaohu's stable
``data-container`` HTML contract and injects caller-supplied avatar/logo images.
"""

from __future__ import annotations

import argparse
import html as html_lib
import json
import re
import sys
from pathlib import Path

DIALOGUE_RE = re.compile(
    r'(?P<open><section\b(?=[^>]*\bdata-container=["\']dialogue-bubble["\'])'
    r'(?=[^>]*\bdata-side=["\'](?P<side>left|right)["\'])[^>]*>)'
    r'(?P<body>.*?)</section>',
    re.IGNORECASE | re.DOTALL,
)
SPEAKER_RE = re.compile(
    r'<p\b(?=[^>]*\bdata-container=["\']dialogue-speaker["\'])[^>]*>(?P<speaker>.*?)</p>',
    re.IGNORECASE | re.DOTALL,
)
TAG_RE = re.compile(r'<[^>]+>')


def _plain_text(fragment: str) -> str:
    return html_lib.unescape(TAG_RE.sub('', fragment)).strip()


def _set_inline_style(source: str, data_container: str, style: str) -> str:
    pattern = re.compile(
        rf'(<(?P<tag>section|p)\b(?=[^>]*\bdata-container=["\']{re.escape(data_container)}["\'])[^>]*)(>)',
        re.IGNORECASE,
    )

    def repl(match: re.Match[str]) -> str:
        opening = match.group(1)
        if re.search(r'\bstyle=["\'][^"\']*["\']', opening, flags=re.IGNORECASE):
            opening = re.sub(
                r'\bstyle=(["\'])[^"\']*\1',
                f'style="{style}"',
                opening,
                count=1,
                flags=re.IGNORECASE,
            )
        else:
            opening += f' style="{style}"'
        return opening + match.group(3)

    return pattern.sub(repl, source)


def _avatar_html(src: str, side: str, accent: str) -> str:
    escaped = html_lib.escape(src, quote=True)
    tail_margin = '0 0 0 17px' if side == 'left' else '0 17px 0 0'
    tail_border = (
        f'border-left:9px solid {accent};border-top:6px solid transparent;border-bottom:6px solid transparent;'
        if side == 'left'
        else f'border-right:9px solid {accent};border-top:6px solid transparent;border-bottom:6px solid transparent;'
    )
    return (
        '<section data-guangyu="avatar" '
        'style="display:inline-block;vertical-align:top;width:60px;flex:0 0 auto;text-align:center;">'
        f'<section style="display:inline-block;width:50px;height:50px;overflow:hidden;border-radius:50%;'
        f'background:{accent};padding:4px;box-sizing:border-box;">'
        '<section style="width:100%;height:100%;border:1px solid #fff;border-radius:50%;overflow:hidden;box-sizing:border-box;">'
        f'<img src="{escaped}" alt="" style="display:block;width:40px;height:40px;max-width:100%;object-fit:cover;border-radius:50%;" />'
        '</section></section>'
        f'<section aria-hidden="true" style="width:0;height:0;{tail_border}margin:{tail_margin};"></section>'
        '</section>'
    )


def enhance_html(source: str, avatars: dict[str, str], accent: str = '#F24D60') -> tuple[str, list[str]]:
    missing: list[str] = []

    # xiaohu's dialogue wrapper otherwise adds its own gray card around all bubbles.
    source = _set_inline_style(
        source,
        'dialogue',
        'margin:20px 0;padding:0;background:transparent;border-radius:0;',
    )
    source = _set_inline_style(
        source,
        'dialogue-title',
        f'text-align:center;font-size:14px;color:{accent};margin:0 0 14px;letter-spacing:1px;',
    )
    # Match the user-provided sample's full red-outline intro instead of xiaohu's left-border callout.
    source = _set_inline_style(
        source,
        'intro',
        f'margin:20px 0 28px;padding:22px 23px;background:#fff;border:2px solid {accent};border-radius:10px;box-sizing:border-box;',
    )
    source = _set_inline_style(
        source,
        'intro-label',
        f'font-size:13px;font-weight:bold;color:{accent};margin:0 0 8px;letter-spacing:2px;',
    )
    source = _set_inline_style(
        source,
        'intro-content',
        'font-size:15px;color:#3E3E3E;line-height:1.8;letter-spacing:.5px;margin:0;text-align:justify;',
    )

    def replace_bubble(match: re.Match[str]) -> str:
        side = match.group('side').lower()
        body = match.group('body')
        speaker_match = SPEAKER_RE.search(body)
        if not speaker_match:
            return match.group(0)
        speaker = _plain_text(speaker_match.group('speaker'))
        avatar_src = avatars.get(speaker)
        if not avatar_src:
            missing.append(speaker)
            return match.group(0)

        bubble_margin = '20px 15px 0 -30px' if side == 'left' else '20px -30px 0 15px'
        bubble_padding = '10px 20px' if side == 'left' else '15px 20px'
        row_align = 'flex-start' if side == 'left' else 'flex-end'
        bubble = (
            f'<section data-guangyu="bubble" data-side="{side}" '
            f'style="display:inline-block;vertical-align:top;flex:1 1 0%;background:#F2F2F2;'
            f'margin:{bubble_margin};padding:{bubble_padding};border-radius:5px;box-sizing:border-box;">'
            f'{body}</section>'
        )
        avatar = _avatar_html(avatar_src, side, accent)
        children = avatar + bubble if side == 'left' else bubble + avatar
        return (
            f'<section data-guangyu="dialogue-row" data-side="{side}" '
            f'style="display:flex;flex-flow:row;text-align:left;justify-content:{row_align};margin:20px 0 10px;box-sizing:border-box;">'
            f'{children}</section>'
        )

    source = DIALOGUE_RE.sub(replace_bubble, source)
    return source, sorted(set(missing))


def load_avatars(path: Path) -> dict[str, str]:
    data = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(data, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in data.items()):
        raise ValueError('avatars JSON must be an object mapping speaker names to image paths/URLs')
    return {k.strip(): v.strip() for k, v in data.items() if k.strip() and v.strip()}


def main() -> int:
    parser = argparse.ArgumentParser(description='Add Guangyu-style avatar dialogue cards to xiaohu formatted HTML.')
    parser.add_argument('--input', required=True, type=Path)
    parser.add_argument('--avatars', required=True, type=Path, help='JSON object: {"speaker": "image path or URL"}')
    parser.add_argument('--output', type=Path)
    parser.add_argument('--accent', default='#F24D60')
    args = parser.parse_args()

    try:
        avatars = load_avatars(args.avatars)
        source = args.input.read_text(encoding='utf-8')
        result, missing = enhance_html(source, avatars, accent=args.accent)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f'error: {exc}', file=sys.stderr)
        return 2

    if missing:
        print('error: missing avatar mapping for: ' + ', '.join(missing), file=sys.stderr)
        return 3

    output = args.output or args.input.with_name(args.input.stem + '.guangyu.html')
    output.write_text(result, encoding='utf-8')
    print(output)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
