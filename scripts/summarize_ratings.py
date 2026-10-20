"""Summarize only actual user-supplied evaluation CSV files."""
import argparse
import csv
import math
from statistics import mean
from pathlib import Path

def main():
    p=argparse.ArgumentParser()
    p.add_argument('csv_path',type=Path)
    args=p.parse_args()
    with args.csv_path.open(newline='',encoding='utf-8-sig') as f:
        reader=csv.DictReader(f)
        columns=reader.fieldnames or []
        expected={'intelligibility','naturalness','voice_similarity','tone_match',
                  'overall_preference','latency_seconds'}
        missing=expected-set(columns)
        if missing:
            raise SystemExit('CSV is missing expected columns: '+', '.join(sorted(missing)))
        rows=list(reader)
    if not rows: raise SystemExit('No user ratings available; no metrics to compute.')
    print(f'Observed rows: {len(rows)}')
    invalid=0
    rating_columns=('intelligibility','naturalness','voice_similarity','tone_match','overall_preference')
    for col in (*rating_columns,'latency_seconds','audio_duration_seconds'):
        valid=[]
        for row in rows:
            try:
                raw=row.get(col)
                if raw is None or not raw.strip(): continue
                value=float(raw)
                if not math.isfinite(value) or (col in rating_columns and not 1 <= value <= 5) or (col not in rating_columns and value < 0):
                    invalid+=1
                    continue
                valid.append(value)
            except (TypeError,ValueError):
                invalid+=1
        if valid: print(f'{col}: n={len(valid)}; exploratory mean={mean(valid):.3f}')
    if invalid: print(f'Ignored invalid/non-finite/out-of-range values: {invalid}')
if __name__=='__main__': main()
