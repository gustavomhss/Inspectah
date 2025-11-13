#!/usr/bin/env python3
from __future__ import annotations
import datetime
import json
import sys
from pathlib import Path

def main() -> None:
    evid_dir = Path(sys.argv[1])
    scorecard_path = Path(sys.argv[2])
    report = {
        'validator': json.loads((evid_dir / 'validator_report.json').read_text()),
        'fts': json.loads((evid_dir / 'fts_smoke.json').read_text()),
        'export': json.loads((evid_dir / 'export_smoke.json').read_text()),
        'timestamp': datetime.datetime.utcnow().isoformat() + 'Z'
    }
    (evid_dir / 'report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    scorecard = {
        'gate': 'T4',
        'version': '1.0',
        'started_at': report['timestamp'],
        'finished_at': report['timestamp'],
        'passed': report['validator'].get('passed', False),
        'failures': [] if report['validator'].get('passed', False) else ['validator_failed'],
        'artifacts': [
            {'path': 'out/evidence/T4_golden/report.json'},
            {'path': 'out/evidence/T4_golden/fts_smoke.json'},
            {'path': 'out/evidence/T4_golden/export_smoke.json'},
            {'path': 'out/evidence/T4_golden/validator_report.json'}
        ]
    }
    scorecard_path.write_text(json.dumps(scorecard, indent=2), encoding='utf-8')
    if not report['validator'].get('passed', False):
        sys.exit(1)

if __name__ == '__main__':
    main()
