"""Check the portable guide's documented file/link contract, without dependencies."""
import argparse
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit


REQUIRED = (
    'README.md', 'START-HERE.md', 'agent-learning.md', 'environment.md',
    'sources.md', 'templates.md', 'stl-to-scad.md', 'fusion-python-tu-hoc.md',
    'scad-to-fusion-task.md', 'parameter-change-validation.md',
    'error-cookbook.md', 'internet-learning.md', 'fusion-mcp-testing.md',
    'VALIDATION.md', 'examples/readiness-scenarios.md',
    'tools/validate-docs.py', 'tests/test_validate_docs.py',
)
TICK = chr(96)
LINK = re.compile(r'!?\[[^\]\n]*\]\(\s*(?:<([^>\n]+)>|([^\s()]+))\s*\)')


def prose_lines(text):
    fence = None
    for number, line in enumerate(text.splitlines(), 1):
        marker = re.match(r'^\s{0,3}(' + TICK + r'{3,}|~{3,})', line)
        if marker:
            value = marker.group(1)
            if fence is None:
                fence = value
            elif value[0] == fence[0] and len(value) >= len(fence):
                fence = None
            continue
        if fence is None:
            yield number, line


def anchors(path):
    found, counts = set(), {}
    for _, line in prose_lines(path.read_text(encoding='utf-8-sig')):
        found.update(re.findall(r'\bid=["\']([^"\']+)["\']', line))
        heading = re.match(r'^#{1,6}\s+(.+?)\s*#*\s*$', line)
        if heading:
            title = heading.group(1).replace(TICK, '')
            slug = re.sub(r'[^\w -]', '', title.lower()).replace(' ', '-')
            index = counts.get(slug, 0)
            found.add(slug + (f'-{index}' if index else ''))
            counts[slug] = index + 1
    return found


def validate(root):
    root = root.resolve()
    issues, link_count = [], 0
    for name in REQUIRED:
        if not (root / name).resolve().is_relative_to(root):
            issues.append({'file': name, 'check': 'outside_bundle'})
        elif not (root / name).is_file():
            issues.append({'file': name, 'check': 'missing_required'})
    files = sorted(root.rglob('*.md'))
    for path in files:
        if not path.resolve().is_relative_to(root):
            issues.append({'file': path.relative_to(root).as_posix(),
                           'check': 'outside_bundle'})
            continue
        try:
            for number, line in prose_lines(path.read_text(encoding='utf-8-sig')):
                line = re.sub(r'(' + TICK + r'+).*?\1', '', line)
                for match in LINK.finditer(line):
                    target = match.group(1) or match.group(2)
                    issue = {'file': path.relative_to(root).as_posix(),
                             'line': number, 'target': target}
                    if target.startswith(('/', '\\')) or re.match(r'^[A-Za-z]:[\\/]', target):
                        issues.append(dict(issue, check='absolute_path'))
                        continue
                    url = urlsplit(target)
                    if url.scheme in ('https', 'http', 'mailto'):
                        continue
                    if url.scheme:
                        issues.append(dict(issue, check='unsupported_scheme'))
                        continue
                    link_count += 1
                    destination = (path.parent / unquote(url.path)).resolve() if url.path else path
                    try:
                        destination.relative_to(root)
                    except ValueError:
                        issues.append(dict(issue, check='outside_bundle'))
                        continue
                    if not destination.exists():
                        issues.append(dict(issue, check='missing_target'))
                    elif url.fragment and (not destination.is_file() or
                                           unquote(url.fragment) not in anchors(destination)):
                        issues.append(dict(issue, check='missing_anchor'))
        except (OSError, UnicodeError, ValueError) as error:
            issues.append({'file': path.relative_to(root).as_posix(),
                           'check': 'read_or_parse_error', 'detail': str(error)})
    return {'root': str(root), 'markdown_files': len(files),
            'local_links': link_count, 'issues': issues}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    report = validate(parser.parse_args().root)
    print(json.dumps(report, indent=2))
    return 1 if report['issues'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
