#!/usr/bin/env python3
from __future__ import annotations
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
REQUIRED = [
    "item_id","source_id","canonical_url","event_time","observed_at","indexed_at",
    "timezone","extractor_version","user_agent","allowlist_proof_ref",
    "fetched_payload_sha256","extracted_fields_sha256","fields","hashes"
]

def validate_fields(expected):
    return [field for field in REQUIRED if field not in expected]

def rss_actual(path: Path):
    tree = ET.parse(path)
    item = tree.find('.//item')
    return {
        'title': item.findtext('title', default=''),
        'description': item.findtext('description', default='')
    }

def api_actual(path: Path):
    data = json.loads(path.read_text())
    node = data[0]
    return {'title': node.get('title', ''), 'value': str(node.get('value', ''))}

def main():
    out_path = Path(sys.argv[1])
    root = Path('tests/goldens')
    rss_results = []
    api_results = []
    for expected_path in sorted(root.glob('rss/*_expected.json')):
        raw_path = expected_path.with_name(expected_path.name.replace('_expected.json', '_raw.xml'))
        expected = json.loads(expected_path.read_text())
        missing = validate_fields(expected)
        actual = rss_actual(raw_path)
        rss_results.append({
            'name': expected_path.stem,
            'missing': missing,
            'title_match': actual['title'] == expected['fields'].get('title'),
            'description_match': actual['description'] == expected['fields'].get('description')
        })
    for expected_path in sorted(root.glob('api/*_expected.json')):
        raw_path = expected_path.with_name(expected_path.name.replace('_expected.json', '_raw.json'))
        expected = json.loads(expected_path.read_text())
        missing = validate_fields(expected)
        actual = api_actual(raw_path)
        api_results.append({
            'name': expected_path.stem,
            'missing': missing,
            'title_match': actual['title'] == expected['fields'].get('title')
        })
    passed = all(not r['missing'] and r['title_match'] and r.get('description_match', True) for r in rss_results) and \
             all(not r['missing'] and r['title_match'] for r in api_results)
    report = {'rss': rss_results, 'api': api_results, 'passed': passed}
    out_path.write_text(json.dumps(report, indent=2), encoding='utf-8')
    if not passed:
        sys.exit(1)

if __name__ == '__main__':
    main()
