#!/usr/bin/env python3
"""
Simple helper to update Helm chart values.yaml image.repository and image.tag
Input: a file where each line is SERVICE|IMAGE|TAG

This script searches for src/<service>/chart/values.yaml or src/<service>/Chart/values.yaml
and sets:
  image:
    repository: <IMAGE>
    tag: <TAG>

It preserves other keys and writes YAML with default formatting.
"""
import sys
import os
from pathlib import Path

try:
    import yaml
except Exception:
    print("PyYAML is required. Please install with: pip install pyyaml")
    sys.exit(2)


def update_values(svc: str, image: str, tag: str) -> bool:
    candidates = [Path('src') / svc / 'chart' / 'values.yaml', Path('src') / svc / 'Chart' / 'values.yaml']
    for p in candidates:
        if p.exists():
            print(f"Updating {p}: image={image}, tag={tag}")
            data = {}
            try:
                with p.open('r', encoding='utf-8') as fh:
                    data = yaml.safe_load(fh) or {}
            except Exception as e:
                print(f"Failed to read {p}: {e}")
                return False

            img = data.get('image', {}) or {}
            img['repository'] = image
            img['tag'] = tag
            data['image'] = img

            try:
                with p.open('w', encoding='utf-8') as fh:
                    yaml.dump(data, fh, sort_keys=False)
            except Exception as e:
                print(f"Failed to write {p}: {e}")
                return False
            return True
    print(f"No values.yaml found for {svc}; skipped")
    return False


def main():
    if len(sys.argv) < 2:
        print("Usage: update_helm_values.py <pushed_images_file>")
        sys.exit(1)

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"File not found: {path}")
        sys.exit(1)

    updated = []
    with path.open('r', encoding='utf-8') as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            parts = line.split('|')
            if len(parts) != 3:
                print(f"Skipping malformed line: {line}")
                continue
            svc, image, tag = parts
            if update_values(svc, image, tag):
                updated.append(str(Path('src') / svc / 'chart' / 'values.yaml'))

    if not updated:
        print('No helm values updated')
        return

    print('Updated files:')
    for p in updated:
        print(' -', p)


if __name__ == '__main__':
    main()
