#!/usr/bin/env python3
"""
Standalone analysis CLI for autoresearch and autoskill experiments.

Usage:
    python analyze.py results.tsv                        # Autoresearch analysis
    python analyze.py --autoskill log.md run.json        # Autoskill analysis
    python analyze.py results.tsv --autoskill log.md run.json  # Both
    python analyze.py --help

Charts saved as PNG to ./output/ directory.
"""

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

plt.rcParams.update({
    'figure.facecolor': 'white',
    'axes.facecolor': 'white',
    'font.size': 11,
    'axes.titlesize': 14,
    'axes.labelsize': 12,
})


def ensure_output_dir(output_dir):
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


# ============================================================
# Part A: Autoskill Optimization Analysis
# ============================================================

def parse_optimization_log(log_path):
    text = Path(log_path).read_text(encoding='utf-8')
    cycles = []
    blocks = re.split(r'## Cycle (\d+)', text)

    for i in range(1, len(blocks), 2):
        cycle_num = int(blocks[i])
        body = blocks[i + 1]

        def extract_field(name, body=body):
            m = re.search(rf'\| {name} \| (.+?) \|', body)
            return m.group(1).strip() if m else ''

        def parse_score(s):
            m = re.match(r'([\d.]+)%\s*\((\d+)/(\d+)\)', s)
            if m:
                return float(m.group(1)), int(m.group(2)), int(m.group(3))
            return 0.0, 0, 0

        sb_pct, sb_pass, sb_total = parse_score(extract_field('Score before'))
        sa_pct, sa_pass, sa_total = parse_score(extract_field('Score after'))

        cycles.append({
            'cycle': cycle_num,
            'hypothesis': extract_field('Hypothesis'),
            'score_before': sb_pct,
            'score_after': sa_pct,
            'pass_before': sb_pass,
            'pass_after': sa_pass,
            'total': sa_total,
            'decision': extract_field('Decision'),
            'notes': extract_field('Notes'),
        })

    return pd.DataFrame(cycles)


def parse_latest_run(run_path):
    with open(run_path, 'r', encoding='utf-8') as f:
        run_data = json.load(f)

    summary = run_data['summary']
    test_results = run_data['test_results']
    assertion_names = list(summary['per_assertion_pass_rates'].keys())

    rows = []
    for tc in test_results:
        row = {
            'id': tc['id'],
            'function': tc['metadata']['function'],
            'level': tc['metadata']['level'],
            'location_type': tc['metadata'].get('location_type', ''),
            'contract_type': tc['metadata'].get('contract_type', ''),
            'passed_all': tc['passed_all'],
        }
        for a in assertion_names:
            row[a] = tc['assertion_scores'].get(a, True)
        rows.append(row)

    return pd.DataFrame(rows), summary, assertion_names


def autoskill_cycle_chart(cycles_df, output_dir):
    fig, ax = plt.subplots(figsize=(14, 6))
    x = cycles_df['cycle'].values
    y = cycles_df['score_after'].values
    decisions = cycles_df['decision'].values
    hypotheses = cycles_df['hypothesis'].values

    ax.plot(x, y, color='#555555', linewidth=1.5, alpha=0.5, zorder=1)

    for cx, cy, dec, hyp in zip(x, y, decisions, hypotheses):
        color = '#2ecc71' if dec == 'Kept' else '#e74c3c'
        marker = 'o' if dec == 'Kept' else 'x'
        size = 120 if dec == 'Kept' else 80
        ax.scatter(cx, cy, c=color, s=size, marker=marker, zorder=3,
                   edgecolors='black' if dec == 'Kept' else color, linewidths=1)
        label = hyp[:50] + '...' if len(hyp) > 50 else hyp
        offset_y = 12 if dec == 'Kept' else -18
        ax.annotate(label, (cx, cy), textcoords='offset points',
                    xytext=(0, offset_y), fontsize=7.5, ha='center',
                    color='#1a7a3a' if dec == 'Kept' else '#c0392b', alpha=0.85)

    ax.axhline(y=90, color='#3498db', linestyle='--', alpha=0.6, linewidth=1.5, label='90% target')

    kept_mask = cycles_df['decision'] == 'Kept'
    if kept_mask.any():
        best_score = 0
        running_best = []
        for _, row in cycles_df.iterrows():
            if row['decision'] == 'Kept':
                best_score = max(best_score, row['score_after'])
            running_best.append(best_score)
        ax.step(x, running_best, where='post', color='#27ae60', linewidth=2,
                alpha=0.4, zorder=2, label='Running best')

    ax.set_xlabel('Optimization Cycle')
    ax.set_ylabel('Score (%)')
    ax.set_title('Autoskill Optimization: Skill Improvement')
    ax.set_ylim(0, 105)
    ax.set_xticks(x)
    ax.legend(loc='lower right')
    ax.grid(True, alpha=0.2)
    plt.tight_layout()

    path = output_dir / 'autoskill_progression.png'
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    return path


def autoskill_heatmap(cases_df, assertion_names, summary, output_dir):
    level_order = {'associate': 0, 'manager': 1, 'director': 2, 'vp': 3, 'c_suite': 4}
    cases_sorted = cases_df.copy()
    cases_sorted['level_ord'] = cases_sorted['level'].map(level_order).fillna(5)
    cases_sorted = cases_sorted.sort_values(['function', 'level_ord'])

    matrix = cases_sorted[assertion_names].values.astype(float)
    labels = [f"{r['id']} ({r['function']}/{r['level']})" for _, r in cases_sorted.iterrows()]

    fig, ax = plt.subplots(figsize=(14, 10))
    cmap = mcolors.ListedColormap(['#e74c3c', '#2ecc71'])
    ax.imshow(matrix, cmap=cmap, aspect='auto', vmin=0, vmax=1)

    ax.set_xticks(range(len(assertion_names)))
    ax.set_xticklabels([a.replace('_', '\n') for a in assertion_names], fontsize=9)
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, fontsize=8.5)

    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            ax.text(j, i, 'P' if matrix[i, j] else 'F',
                    ha='center', va='center', fontsize=8, fontweight='bold', color='white')

    funcs = cases_sorted['function'].values
    for i in range(1, len(funcs)):
        if funcs[i] != funcs[i - 1]:
            ax.axhline(y=i - 0.5, color='white', linewidth=2)

    ax.set_title(f'Assertion Heatmap: {summary["overall_pass_count"]}/{summary["total_cases"]} '
                 f'Passing ({summary["overall_pass_rate"]:.1%})')
    plt.tight_layout()

    path = output_dir / 'autoskill_heatmap.png'
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    return path


def autoskill_coverage(cases_df, output_dir):
    coverage = cases_df.groupby(['function', 'level']).size().unstack(fill_value=0)
    level_cols = [l for l in ['associate', 'manager', 'director', 'vp', 'c_suite'] if l in coverage.columns]
    coverage = coverage[level_cols]

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.imshow(coverage.values, cmap=plt.cm.YlGn, aspect='auto', vmin=0)

    ax.set_xticks(range(len(coverage.columns)))
    ax.set_xticklabels(coverage.columns, fontsize=10)
    ax.set_yticks(range(len(coverage.index)))
    ax.set_yticklabels(coverage.index, fontsize=10)

    for i in range(coverage.shape[0]):
        for j in range(coverage.shape[1]):
            val = coverage.values[i, j]
            color = 'red' if val == 0 else ('white' if val >= 2 else 'black')
            ax.text(j, i, str(val), ha='center', va='center',
                    fontsize=14, fontweight='bold', color=color)

    ax.set_title('Test Suite Coverage: Function x Level (0 = gap)')
    ax.set_xlabel('Seniority Level')
    ax.set_ylabel('Functional Area')
    plt.tight_layout()

    path = output_dir / 'autoskill_coverage.png'
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    return path


def run_autoskill_analysis(log_path, run_path, output_dir):
    print('=' * 60)
    print('PART A: AUTOSKILL OPTIMIZATION ANALYSIS')
    print('=' * 60)

    cycles_df = parse_optimization_log(log_path)
    print(f'\nParsed {len(cycles_df)} optimization cycles')

    kept = cycles_df[cycles_df['decision'] == 'Kept']
    print(f'Kept {len(kept)}/{len(cycles_df)} cycles')
    print(f'Starting score: {cycles_df.iloc[0]["score_before"]}%')
    print(f'Final score: {cycles_df.iloc[-1]["score_after"]}%')

    # Chart
    chart_path = autoskill_cycle_chart(cycles_df, output_dir)
    print(f'\nSaved: {chart_path}')

    # Parse test results
    cases_df, summary, assertion_names = parse_latest_run(run_path)
    print(f'\nOverall pass rate: {summary["overall_pass_rate"]:.1%} '
          f'({summary["overall_pass_count"]}/{summary["total_cases"]})')
    print('\nPer-assertion pass rates:')
    for a in assertion_names:
        rate = summary['per_assertion_pass_rates'][a]
        count = summary['per_assertion_pass_counts'][a]
        status = 'PASS' if rate == 1.0 else 'FAIL'
        print(f'  {a:25s} {rate:6.1%}  ({count}/{summary["total_cases"]})  {status}')

    # Heatmap
    heatmap_path = autoskill_heatmap(cases_df, assertion_names, summary, output_dir)
    print(f'\nSaved: {heatmap_path}')

    # Coverage
    coverage_path = autoskill_coverage(cases_df, output_dir)
    print(f'Saved: {coverage_path}')

    # Remaining gaps
    failed = cases_df[~cases_df['passed_all']]
    if len(failed) == 0:
        print('\nAll test cases passing!')
    else:
        print(f'\nRemaining failures: {len(failed)} test case(s)')
        for _, tc in failed.iterrows():
            failing = [a for a in assertion_names if not tc[a]]
            print(f"  {tc['id']} ({tc['function']}/{tc['level']}): {', '.join(failing)}")

    return cycles_df, cases_df, summary


# ============================================================
# Part B: Autoresearch Experiment Analysis
# ============================================================

PATTERNS = {
    'WINDOW_PATTERN': r'(?i)window|WINDOW_PATTERN|attention.*pattern',
    'DEPTH': r'(?i)depth|\blayer',
    'MATRIX_LR': r'(?i)matrix.*lr|matrix.*learning|MATRIX_LR|muon.*lr',
    'EMBEDDING_LR': r'(?i)embedding.*lr|EMBEDDING_LR',
    'WARMDOWN_RATIO': r'(?i)warmdown|WARMDOWN_RATIO',
    'WEIGHT_DECAY': r'(?i)weight.?decay|WEIGHT_DECAY',
    'BATCH_SIZE': r'(?i)batch.*size|TOTAL_BATCH|DEVICE_BATCH',
    'ASPECT_RATIO': r'(?i)aspect|ASPECT_RATIO|\bwiden\b|model_dim',
    'ACTIVATION': r'(?i)activation|\brelu\b|\bsilu\b|\bgelu\b|F\.',
    'SOFTCAP': r'(?i)softcap',
    'GQA': r'(?i)gqa|grouped.*query|n_kv_head',
    'X0_LAMBDAS': r'(?i)x0_lambda|lambda.*init',
}


def categorize_experiment(desc):
    desc = str(desc).strip().lower()
    if desc == 'baseline' or desc.startswith('baseline'):
        return 'BASELINE'
    for category, pattern in PATTERNS.items():
        if re.search(pattern, desc):
            return category
    return 'OTHER'


def progress_chart(df, output_dir):
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 12), height_ratios=[3, 1],
                                   gridspec_kw={'hspace': 0.3})

    valid = df[df['status'] != 'CRASH'].copy().reset_index(drop=True)
    crashes = df[df['status'] == 'CRASH'].copy()
    n_keep = len(df[df['status'] == 'KEEP'])

    if len(valid) > 0:
        baseline_bpb = valid.loc[0, 'val_bpb']

        disc = valid[valid['status'] == 'DISCARD']
        ax1.scatter(disc.index, disc['val_bpb'], c='#cccccc', s=12, alpha=0.5, zorder=2, label='Discarded')

        kept_v = valid[valid['status'] == 'KEEP']
        ax1.scatter(kept_v.index, kept_v['val_bpb'], c='#2ecc71', s=50, zorder=4,
                    label='Kept', edgecolors='black', linewidths=0.5)

        if len(crashes) > 0:
            crash_y = baseline_bpb + 0.001
            ax1.scatter(crashes.index, [crash_y] * len(crashes), c='#e74c3c', s=40,
                        marker='x', zorder=4, label='Crashed', linewidths=1.5)

        kept_mask = valid['status'] == 'KEEP'
        if kept_mask.any():
            kept_idx = valid.index[kept_mask]
            kept_bpb = valid.loc[kept_mask, 'val_bpb']
            running_min = kept_bpb.cummin()
            ax1.step(kept_idx, running_min, where='post', color='#27ae60',
                     linewidth=2, alpha=0.7, zorder=3, label='Running best')

            for idx, bpb in zip(kept_idx, kept_bpb):
                desc = str(valid.loc[idx, 'description']).strip()
                if len(desc) > 40:
                    desc = desc[:37] + '...'
                ax1.annotate(desc, (idx, bpb), textcoords='offset points',
                             xytext=(6, 6), fontsize=7.5, color='#1a7a3a',
                             alpha=0.85, rotation=25, ha='left', va='bottom')

        ax1.axhline(y=baseline_bpb, color='#e67e22', linestyle='--', alpha=0.5,
                    linewidth=1, label=f'Baseline ({baseline_bpb:.6f})')
        ax1.set_xlabel('Experiment #')
        ax1.set_ylabel('Validation BPB (lower is better)')
        ax1.set_title(f'Autoresearch Progress: {len(df)} Experiments, {n_keep} Kept')
        ax1.legend(loc='upper right', fontsize=9)
        ax1.grid(True, alpha=0.2)

    # Improvement velocity
    kept_all = df[df['status'] == 'KEEP'].copy()
    if len(kept_all) > 1:
        kept_all = kept_all.reset_index()
        kept_all['prev_bpb'] = kept_all['val_bpb'].shift(1)
        kept_all['delta'] = kept_all['prev_bpb'] - kept_all['val_bpb']
        deltas = kept_all.iloc[1:]

        if len(deltas) > 0:
            colors = ['#2ecc71' if d > 0 else '#e74c3c' for d in deltas['delta']]
            ax2.bar(range(len(deltas)), deltas['delta'], color=colors, alpha=0.7)
            if len(deltas) >= 3:
                window = min(5, len(deltas))
                ma = deltas['delta'].rolling(window=window, min_periods=1).mean()
                ax2.plot(range(len(deltas)), ma, color='#e67e22', linewidth=2,
                         alpha=0.8, label=f'{window}-exp moving avg')
                ax2.legend(fontsize=9)
            ax2.set_xlabel('Kept Experiment #')
            ax2.set_ylabel('BPB Delta')
            ax2.set_title('Improvement Velocity')
            ax2.axhline(y=0, color='black', linewidth=0.5)
            ax2.grid(True, alpha=0.2)
    else:
        ax2.text(0.5, 0.5, 'Not enough kept experiments for velocity analysis',
                 ha='center', va='center', transform=ax2.transAxes)

    plt.tight_layout()
    path = output_dir / 'autoresearch_progress.png'
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    return path


def impact_chart(df, output_dir):
    categories = [c for c in df['category'].unique() if c not in ('BASELINE', 'CRASH')]
    impact_rows = []

    for cat in categories:
        subset = df[df['category'] == cat]
        n_total = len(subset)
        n_keep = len(subset[subset['status'] == 'KEEP'])
        n_discard = len(subset[subset['status'] == 'DISCARD'])
        n_crash = len(subset[subset['status'] == 'CRASH'])

        kept_cat = df[df['status'] == 'KEEP'].copy()
        kept_cat['prev_bpb'] = kept_cat['val_bpb'].shift(1)
        kept_cat['delta'] = kept_cat['prev_bpb'] - kept_cat['val_bpb']
        kept_in_cat = kept_cat[(kept_cat['category'] == cat) & (kept_cat['delta'].notna())]

        keep_rate = n_keep / max(n_total, 1)
        mean_delta = kept_in_cat['delta'].mean() if len(kept_in_cat) > 0 else 0
        best_delta = kept_in_cat['delta'].max() if len(kept_in_cat) > 0 else 0
        total_impact = kept_in_cat['delta'].sum() if len(kept_in_cat) > 0 else 0

        impact_rows.append({
            'category': cat, 'attempted': n_total, 'kept': n_keep,
            'discarded': n_discard, 'crashed': n_crash, 'keep_rate': keep_rate,
            'mean_delta': mean_delta, 'best_delta': best_delta, 'total_impact': total_impact,
        })

    impact_df = pd.DataFrame(impact_rows).sort_values('total_impact', ascending=True)

    if len(impact_df) > 0 and impact_df['total_impact'].sum() > 0:
        fig, ax = plt.subplots(figsize=(12, max(6, len(impact_df) * 0.8)))
        colors = ['#2ecc71' if v > 0 else '#cccccc' for v in impact_df['total_impact']]
        ax.barh(impact_df['category'], impact_df['total_impact'], color=colors,
                edgecolor='black', linewidth=0.5)
        ax.set_xlabel('Total BPB Impact')
        ax.set_title('Hyperparameter Impact Ranking')
        ax.grid(True, alpha=0.2, axis='x')
        plt.tight_layout()
        path = output_dir / 'autoresearch_impact.png'
        plt.savefig(path, dpi=150, bbox_inches='tight')
        plt.close()
        print(f'Saved: {path}')

    # Print table
    print(f'\n{"Category":>20s} {"Tried":>6s} {"Kept":>5s} {"Rate":>6s} '
          f'{"Mean Delta":>11s} {"Best Delta":>11s} {"Total Impact":>13s}')
    print('-' * 85)
    for _, row in impact_df.sort_values('total_impact', ascending=False).iterrows():
        print(f'{row["category"]:>20s} {row["attempted"]:6d} {row["kept"]:5d} '
              f'{row["keep_rate"]:6.0%} {row["mean_delta"]:+11.6f} '
              f'{row["best_delta"]:+11.6f} {row["total_impact"]:+13.6f}')

    return impact_df


def run_autoresearch_analysis(results_path, output_dir):
    print('\n' + '=' * 60)
    print('PART B: AUTORESEARCH EXPERIMENT ANALYSIS')
    print('=' * 60)

    df = pd.read_csv(results_path, sep='\t')
    df['val_bpb'] = pd.to_numeric(df['val_bpb'], errors='coerce')
    if 'memory_gb' in df.columns:
        df['memory_gb'] = pd.to_numeric(df['memory_gb'], errors='coerce')
    df['status'] = df['status'].str.strip().str.upper()
    df['description'] = df['description'].fillna('').str.strip()

    # Filter out crash-only datasets
    valid_rows = df[(df['status'] != 'CRASH') | (df['val_bpb'] > 0)]
    if len(valid_rows) == 0:
        print('\nNo valid experiment data (only crashes with 0 val_bpb).')
        print('Run experiments on Lambda first, then re-analyze.')
        return None

    n_keep = len(df[df['status'] == 'KEEP'])
    n_discard = len(df[df['status'] == 'DISCARD'])
    n_crash = len(df[df['status'] == 'CRASH'])
    n_decided = n_keep + n_discard

    print(f'\nTotal experiments: {len(df)}')
    print(f'  KEEP:    {n_keep}')
    print(f'  DISCARD: {n_discard}')
    print(f'  CRASH:   {n_crash}')
    if n_decided > 0:
        print(f'  Keep rate: {n_keep}/{n_decided} = {n_keep / n_decided:.1%}')

    # Categorize
    df['category'] = df['description'].apply(categorize_experiment)
    cat_counts = df['category'].value_counts()
    print('\nExperiment categories:')
    for cat, count in cat_counts.items():
        print(f'  {cat:20s} {count:3d}')

    # Progress chart
    chart_path = progress_chart(df, output_dir)
    print(f'\nSaved: {chart_path}')

    # Impact ranking
    impact_chart(df, output_dir)

    # Summary stats
    kept_all = df[df['status'] == 'KEEP']
    if len(kept_all) > 0:
        baseline_bpb = kept_all.iloc[0]['val_bpb']
        best_bpb = kept_all['val_bpb'].min()
        print(f'\nBaseline BPB: {baseline_bpb:.6f}')
        print(f'Best BPB:     {best_bpb:.6f}')
        improvement = baseline_bpb - best_bpb
        print(f'Improvement:  {improvement:.6f} ({improvement / baseline_bpb * 100:.2f}%)')

    return df


# ============================================================
# Main
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description='Analyze autoresearch and autoskill experiments.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument('results', nargs='?', help='Path to results.tsv (autoresearch)')
    parser.add_argument('--autoskill', nargs=2, metavar=('LOG', 'RUN'),
                        help='Autoskill analysis: optimization_log.md and latest_run.json')
    parser.add_argument('-o', '--output', default='output',
                        help='Output directory for charts (default: ./output)')

    args = parser.parse_args()

    if not args.results and not args.autoskill:
        parser.print_help()
        print('\nError: provide results.tsv and/or --autoskill files')
        sys.exit(1)

    output_dir = ensure_output_dir(Path(args.output))
    print(f'Output directory: {output_dir.resolve()}\n')

    if args.autoskill:
        log_path, run_path = args.autoskill
        if not Path(log_path).exists():
            print(f'Error: {log_path} not found')
            sys.exit(1)
        if not Path(run_path).exists():
            print(f'Error: {run_path} not found')
            sys.exit(1)
        run_autoskill_analysis(log_path, run_path, output_dir)

    if args.results:
        if not Path(args.results).exists():
            print(f'Error: {args.results} not found')
            sys.exit(1)
        run_autoresearch_analysis(args.results, output_dir)

    print('\n' + '=' * 60)
    print('ANALYSIS COMPLETE')
    print(f'Charts saved to: {output_dir.resolve()}')
    print('=' * 60)


if __name__ == '__main__':
    main()
