#!/usr/bin/env python3
import argparse
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

def read_fields(path: Path) -> Dict[str, Any]:
    with path.open('r', encoding='utf-8') as fh:
        return json.load(fh)

def read_payload(path: Path) -> Any:
    with path.open('r', encoding='utf-8') as fh:
        return json.load(fh)

def eval_path(payload: Any, path_expr: str) -> Any:
    if not path_expr.startswith('$.'):
        raise ValueError(f'Unsupported path: {path_expr}')
    current = payload
    tokens: List[str] = []
    buffer = ''
    i = 2
    while i < len(path_expr):
        ch = path_expr[i]
        if ch == '.':
            if buffer:
                tokens.append(buffer)
                buffer = ''
        else:
            buffer += ch
        i += 1
    if buffer:
        tokens.append(buffer)
    for token in tokens:
        if '[' in token and token.endswith(']'):
            key, idx = token[:-1].split('[')
            current = current.get(key)
            if current is None:
                return None
            current = current[int(idx)]
        else:
            if not isinstance(current, dict):
                return None
            current = current.get(token)
        if current is None:
            return None
    return current

def apply_transforms(value: Any, transforms):
    for transform in transforms or []:
        name = transform['name']
        args = transform.get('args', {})
        if name == 'trim' and isinstance(value, str):
            value = value.strip()
        elif name == 'lower' and isinstance(value, str):
            value = value.lower()
        elif name == 'upper' and isinstance(value, str):
            value = value.upper()
        elif name == 'parse_float':
            value = float(value)
        elif name == 'parse_int':
            value = int(value)
        elif name == 'parse_date' and isinstance(value, str):
            value = datetime.fromisoformat(value.replace('Z', '+00:00')).isoformat()
        elif name == 'coalesce':
            options = args.get('options', [])
            if value is None:
                value = next((opt for opt in options if opt is not None), value)
        elif name == 'regex_extract' and isinstance(value, str):
            pattern = args.get('pattern')
            if not pattern:
                raise ValueError('regex_extract missing pattern')
            match = re.search(pattern, value)
            value = match.group(1) if match else None
        elif name == 'split' and isinstance(value, str):
            sep = args.get('sep', ',')
            value = value.split(sep)
        elif name == 'join' and isinstance(value, list):
            sep = args.get('sep', ',')
            value = sep.join(value)
        elif name == 'to_enum' and isinstance(value, str):
            allowed = [v.lower() for v in args.get('allow', [])]
            val = value.lower()
            if val not in allowed:
                raise ValueError(f'value {value} not allowed')
            value = val
    return value

def validate_type(value: Any, field_type: str):
    if field_type == 'string' and not isinstance(value, str):
        raise TypeError('expected string')
    if field_type == 'number' and not isinstance(value, (int, float)):
        raise TypeError('expected number')
    if field_type == 'integer' and not isinstance(value, int):
        raise TypeError('expected integer')
    if field_type == 'boolean' and not isinstance(value, bool):
        raise TypeError('expected boolean')
    if field_type == 'timestamp':
        if not isinstance(value, str):
            raise TypeError('expected timestamp string')
        datetime.fromisoformat(value.replace('Z', '+00:00'))
    if field_type == 'enum' and not isinstance(value, str):
        raise TypeError('expected enum string')
    if field_type == 'array' and not isinstance(value, list):
        raise TypeError('expected array')

def main():
    parser = argparse.ArgumentParser(description='Field Designer dry-run validator')
    parser.add_argument('--fields', required=True, type=Path)
    parser.add_argument('--payload', required=True, type=Path)
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()

    config = read_fields(args.fields)
    payload = read_payload(args.payload)

    results = []
    for field in config.get('fields', []):
        entry = {
            'name': field['name'],
            'path': field['path'],
            'type': field['type'],
            'status': 'ok'
        }
        try:
            value = eval_path(payload, field['path'])
            value = apply_transforms(value, field.get('transforms'))
            validate_type(value, field['type'])
            entry['value'] = value
        except Exception as exc:
            entry['status'] = 'error'
            entry['error'] = str(exc)
        results.append(entry)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open('w', encoding='utf-8') as fh:
        json.dump({'fields': results}, fh, indent=2)

if __name__ == '__main__':
    main()
