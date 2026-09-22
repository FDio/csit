#!/usr/bin/env python3
import csv
import gzip
import json
import re
import sys
import urllib.request


def fetch_report(log_url):
    report_url = log_url.rstrip('/') + '/report.html.gz'
    try:
        with urllib.request.urlopen(report_url, timeout=30) as resp:
            data = resp.read()
        content = gzip.decompress(data).decode('utf-8', errors='replace')
        return content
    except Exception as e:
        print(f'  ERROR fetching {report_url}: {e}', file=sys.stderr)
        return None


def parse_all_tests_stats(content):
    m = re.search(r'window\.output\["stats"\]\s*=\s*(\[.*?\]);', content, re.DOTALL)
    if not m:
        return None, None, None
    stats = json.loads(m.group(1))
    all_tests = stats[0][0]
    total = all_tests['pass'] + all_tests['fail']
    return total, all_tests['pass'], all_tests['fail']


def parse_strings(content):
    strings = []
    for m in re.finditer(
        r'window\.output\["strings"\]\s*=\s*window\.output\["strings"\]\.concat\((\[.*?\])\);',
        content, re.DOTALL
    ):
        strings.extend(json.loads(m.group(1)))
    return strings


def get_str(strings, idx):
    if isinstance(idx, int) and 0 <= idx < len(strings):
        return strings[idx].lstrip('*')
    return str(idx)


def parse_failed_tests(content):
    strings = parse_strings(content)
    m = re.search(r'window\.output\["suite"\]\s*=\s*(.*?);$', content, re.MULTILINE | re.DOTALL)
    if not m:
        return []
    suite_raw = m.group(1)

    # Inline any window.sPart* references before JSON parsing
    for part_m in re.finditer(r'window\.(sPart\d+)\s*=\s*(.*?);$', content, re.MULTILINE | re.DOTALL):
        part_name = part_m.group(1)
        part_value = part_m.group(2)
        suite_raw = suite_raw.replace('window.' + part_name, part_value)

    try:
        suite_data = json.loads(suite_raw)
    except json.JSONDecodeError:
        return []

    failed = []

    def walk(data):
        if not data or not isinstance(data, list):
            return
        suites = data[6] if len(data) > 6 else []
        tests = data[7] if len(data) > 7 else []
        for suite in suites:
            walk(suite)
        for test in tests:
            status_arr = test[4] if len(test) > 4 else []
            status_num = status_arr[0] if status_arr else None
            if status_num == 0:
                failed.append(get_str(strings, test[0]))

    walk(suite_data)
    return failed


def process_csv(path):
    with open(path, newline='') as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames)
        rows = list(reader)

    new_fields = ['Total', 'Pass', 'Fail', 'Failed tests']
    for field in new_fields:
        if field not in fieldnames:
            fieldnames.append(field)

    # Ensure new fields exist in each row
    for row in rows:
        for field in new_fields:
            if field not in row:
                row[field] = ''

    total_rows = len(rows)
    for i, row in enumerate(rows):
        # Skip rows already processed (resume support)
        if row.get('Total', '').strip():
            print(f'[{i+1}/{total_rows}] Already processed, skipping')
            continue

        log_url = row.get('Log', '').strip()
        if not log_url:
            print(f'[{i+1}/{total_rows}] No log URL, skipping')
            continue

        print(f'[{i+1}/{total_rows}] Fetching {log_url}')
        content = fetch_report(log_url)
        if content is None:
            continue

        total, passed, failed = parse_all_tests_stats(content)
        if total is None:
            print(f'  Could not parse stats', file=sys.stderr)
            continue

        row['Total'] = total
        row['Pass'] = passed
        row['Fail'] = failed

        if failed and failed > 0:
            failed_names = parse_failed_tests(content)
            row['Failed tests'] = '; '.join(failed_names)
            print(f'  Total={total} Pass={passed} Fail={failed} -> {len(failed_names)} failed tests')
        else:
            print(f'  Total={total} Pass={passed} Fail={failed}')

        # Write incrementally after each row to preserve progress
        with open(path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    print(f'\nDone. Updated {path}')


if __name__ == '__main__':
    process_csv('data.csv')
