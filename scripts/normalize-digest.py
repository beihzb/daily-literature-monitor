#!/usr/bin/env python3
"""
Pre-delivery digest normalizer for daily-literature-monitor.

Run this on digest.md BEFORE delivery (chat/email/etc.).
Fixes the most common format failures:
  1. Proc Natl Acad Sci U S A → PNAS
  2. Elife → eLife
  3. Section order validation (against SECTION_ORDER below)
  4. Journal name variants (Nat Commun → correct display)

The SECTION_ORDER and EMOJI_MAP below are defaults from the original
author's research topics. Edit them to match your own digest sections
(see README.md "个人偏好设置" for guidance).

Usage:
    python3 normalize-digest.py /path/to/digest.md [--fix] [--check-only]

Without --fix, only reports issues. With --fix, rewrites the file in-place.
"""
import re, sys, os

# Windows consoles often use a legacy code page (e.g. GBK) that cannot print
# ✓ / • / emoji; force UTF-8 output so the checker works everywhere.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

# Default section order (generic examples — NOT a personal research profile).
# Edit this list to match YOUR digest's section order.
SECTION_ORDER = [
    '生物信息学',
    '单细胞与空间',
    '基因调控与发育',
    '进化与基因组',
]

# Emoji variants that may appear for each section name
EMOJI_MAP = {
    '生物信息学': ('💻', ['⚙️']),        # current, [historical]
    '单细胞与空间': ('🔬', []),
    '基因调控与发育': ('🧬', []),
    '进化与基因组': ('🌲', ['基因组与进化']),
}


def find_sections_current(text):
    r"""Find sections in current format: **━━ {emoji} {name} (N)**━━

    Accepts both trailing variants seen in real digests:
    - "**━━ 💻 生物信息学 (3)**━━"  (canonical, ends with `**━━`)
    - "**━━ 💻 生物信息学 (3) ━━**" (legacy variant, ends with `━━**`)
    `[^\s]+` keeps the emoji (including multi-codepoint emoji like 👁️) intact,
    and `(.+?)` captures the full section name (spaces allowed).
    """
    pattern = r'\*\*━━\s*([^\s]+)\s*(.+?)\s*\((\d+)\)\s*(?:\*\*━━|━━\*\*)'
    matches = []
    for m in re.finditer(pattern, text):
        emoji = m.group(1)
        name = m.group(2)
        matches.append((m.start(), emoji, name))
    return matches


def find_sections_old(text):
    """Find sections in old format: ━━━ {emoji} {name} ━━━"""
    pattern = r'━━━\s*(\S)\s*(.+?)\s*━━━'
    matches = []
    for m in re.finditer(pattern, text):
        emoji = m.group(1)
        name = m.group(2)
        matches.append((m.start(), emoji, name))
    return matches


def check_section_order(text):
    sections = find_sections_current(text)
    if not sections:
        sections = find_sections_old(text)
        if not sections:
            return ["Could not find any section headers — check format"]
        issues = ["Using old section format (━━━ ... ━━━) instead of current (**━━ ... (N)**━━)"]
    else:
        issues = []

    found_names = [s[2] for s in sections]
    expected_active = [s for s in SECTION_ORDER if s in found_names]

    for i, name in enumerate(found_names):
        if i >= len(expected_active) or name != expected_active[i]:
            issues.append(
                f"Section #{i}: '{name}' — expected "
                f"'{expected_active[i] if i < len(expected_active) else '(should not be here)'}'"
            )
    return issues


def check_journal_names(text):
    issues = []
    if re.search(r'\*Proc Natl Acad Sci U S A\*', text):
        issues.append("Found '*Proc Natl Acad Sci U S A*' — must be '*PNAS*'")
    if re.search(r'\*Elife\*', text):
        issues.append("Found '*Elife*' — must be '*eLife*'")
    if re.search(r'\*Sci Adv\*', text):
        issues.append("Found '*Sci Adv*' — must be '*Science Advances*'")
    return issues


def fix_text(text):
    text = text.replace('*Proc Natl Acad Sci U S A*', '*PNAS*')
    text = text.replace('*Proc Natl Acad Sci U S A *', '*PNAS*')
    text = text.replace('*Elife*', '*eLife*')
    text = text.replace('*Sci Adv*', '*Science Advances*')
    return text


def main():
    args = sys.argv[1:]
    if not args:
        print("Usage: normalize-digest.py <digest.md> [--fix] [--check-only]")
        sys.exit(1)
    path = args[0]
    do_fix = '--fix' in args
    check_only = '--check-only' in args
    if not os.path.exists(path):
        print(f"File not found: {path}")
        sys.exit(1)
    # Read as UTF-8 (BOM-tolerant): digests contain emoji + CJK and may be
    # written by Windows editors that add a BOM; default locale encodings (GBK)
    # would crash on UTF-8 content.
    with open(path, encoding="utf-8-sig") as f:
        text = f.read()

    all_issues = []
    all_issues.extend(check_section_order(text))
    all_issues.extend(check_journal_names(text))

    if not all_issues:
        print("✓ No issues found — digest is clean.")
        return

    print(f"Found {len(all_issues)} issue(s):")
    for issue in all_issues:
        print(f"  • {issue}")

    if do_fix:
        fixed = fix_text(text)
        with open(path, 'w', encoding="utf-8") as f:
            f.write(fixed)
        print(f"\n  → Fixed and saved to {path}")
    if check_only:
        print(f"\n  → Check mode: no changes made. Run with --fix to apply fixes.")


if __name__ == '__main__':
    main()
