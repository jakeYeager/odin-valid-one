"""
Case 0: Visualization - Blind Study (Approach Two)
Generates 3 histograms and 6 heatmaps for population exploration.
All outputs saved to output/ directory.
"""

import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'record_vals.csv')
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'output')


def load_data(path=DATA_PATH):
    return pd.read_csv(path)


def bin_column(series, n_bins=16):
    """Bin a series into n_bins equal-width bins based on [0, max].
    Returns bin labels (1-indexed) for each value."""
    max_val = series.max()
    bin_edges = np.linspace(0, max_val, n_bins + 1)
    labels = list(range(1, n_bins + 1))
    binned = pd.cut(series, bins=bin_edges, labels=labels, include_lowest=True)
    return binned, bin_edges


def make_histogram(df, col, output_dir):
    """Create a histogram with 16 equal bins for the given column."""
    binned, bin_edges = bin_column(df[col])
    counts = binned.value_counts().sort_index()

    fig, ax = plt.subplots(figsize=(10, 6))
    labels = [str(i) for i in range(1, 17)]
    values = [counts.get(i, 0) for i in range(1, 17)]
    ax.bar(labels, values, color='steelblue', edgecolor='black')
    ax.set_xlabel('Bin')
    ax.set_ylabel('Event Count')
    ax.set_title(f'Distribution of {col} (16 equal bins)')
    plt.tight_layout()

    path = os.path.join(output_dir, f'case_0_histogram_{col}.png')
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"  Saved: {path}")


def make_heatmap_binned_vs_categorical(df, x_col, y_col_categorical, title, cmap, output_path):
    """Heatmap: binned x_col (x-axis) vs categorical y_col (y-axis)."""
    binned_x, _ = bin_column(df[x_col])
    df_work = df.copy()
    df_work['x_bin'] = binned_x

    pivot = df_work.groupby([y_col_categorical, 'x_bin']).size().unstack(fill_value=0)

    # Ensure all 16 bins present
    for b in range(1, 17):
        if b not in pivot.columns:
            pivot[b] = 0
    pivot = pivot[sorted(pivot.columns)]

    fig, ax = plt.subplots(figsize=(12, 6))
    im = ax.imshow(pivot.values, aspect='auto', cmap=cmap)
    ax.set_xticks(range(16))
    ax.set_xticklabels([str(i) for i in range(1, 17)])
    # Label y-axis every 10th value to avoid crowding
    y_labels = pivot.index.tolist()
    tick_positions = [i for i, v in enumerate(y_labels) if v % 10 == 0]
    tick_labels = [str(y_labels[i]) for i in tick_positions]
    ax.set_yticks(tick_positions)
    ax.set_yticklabels(tick_labels)
    ax.set_xlabel(f'{x_col} bin')
    ax.set_ylabel(y_col_categorical)
    ax.set_title(title)
    plt.colorbar(im, ax=ax, label='Count')
    plt.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    print(f"  Saved: {output_path}")


def make_heatmap_binned_vs_binned(df, x_col, y_col, title, cmap, output_path):
    """Heatmap: binned x_col (x-axis) vs binned y_col (y-axis)."""
    binned_x, _ = bin_column(df[x_col])
    binned_y, _ = bin_column(df[y_col])
    df_work = df.copy()
    df_work['x_bin'] = binned_x
    df_work['y_bin'] = binned_y

    pivot = df_work.groupby(['y_bin', 'x_bin']).size().unstack(fill_value=0)

    # Ensure all 16 bins present on both axes
    for b in range(1, 17):
        if b not in pivot.columns:
            pivot[b] = 0
        if b not in pivot.index:
            pivot.loc[b] = 0
    pivot = pivot[sorted(pivot.columns)]
    pivot = pivot.sort_index()

    fig, ax = plt.subplots(figsize=(10, 8))
    im = ax.imshow(pivot.values, aspect='auto', cmap=cmap, origin='lower')
    ax.set_xticks(range(16))
    ax.set_xticklabels([str(i) for i in range(1, 17)])
    ax.set_yticks(range(16))
    ax.set_yticklabels([str(i) for i in range(1, 17)])
    ax.set_xlabel(f'{x_col} bin')
    ax.set_ylabel(f'{y_col} bin')
    ax.set_title(title)
    plt.colorbar(im, ax=ax, label='Count')
    plt.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    print(f"  Saved: {output_path}")


def main():
    df = load_data()
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # --- Histograms ---
    print("Generating histograms...")
    for col in ['x_val', 'y_val', 'z_val']:
        make_histogram(df, col, OUTPUT_DIR)

    # --- Heatmaps ---
    print("Generating heatmaps...")

    # 4. x_val vs a_val (all)
    make_heatmap_binned_vs_categorical(
        df, 'x_val', 'a_val',
        title='x_val bins vs a_val groups (all records)',
        cmap='viridis',
        output_path=os.path.join(OUTPUT_DIR, 'case_0_heatmap_x_vs_a_all.png')
    )

    # 5. x_val vs a_val (v_val >= 7.0)
    df_v7 = df[df['v_val'] >= 7.0]
    make_heatmap_binned_vs_categorical(
        df_v7, 'x_val', 'a_val',
        title='x_val bins vs a_val groups (v_val >= 7.0)',
        cmap='Blues',
        output_path=os.path.join(OUTPUT_DIR, 'case_0_heatmap_x_vs_a_v7.png')
    )

    # 6. x_val vs y_val (all)
    make_heatmap_binned_vs_binned(
        df, 'x_val', 'y_val',
        title='x_val bins (16) vs y_val bins (16) (all records)',
        cmap='viridis',
        output_path=os.path.join(OUTPUT_DIR, 'case_0_heatmap_x_vs_y_all.png')
    )

    # 7. x_val vs y_val (v_val >= 7.0)
    make_heatmap_binned_vs_binned(
        df_v7, 'x_val', 'y_val',
        title='x_val bins (16) vs y_val bins (16) (v_val >= 7.0)',
        cmap='Blues',
        output_path=os.path.join(OUTPUT_DIR, 'case_0_heatmap_x_vs_y_v7.png')
    )

    # 8. y_val vs z_val (all)
    make_heatmap_binned_vs_binned(
        df, 'y_val', 'z_val',
        title='y_val bins (16) vs z_val bins (16) (all records)',
        cmap='viridis',
        output_path=os.path.join(OUTPUT_DIR, 'case_0_heatmap_y_vs_z_all.png')
    )

    # 9. y_val vs z_val (v_val >= 7.0)
    make_heatmap_binned_vs_binned(
        df_v7, 'y_val', 'z_val',
        title='y_val bins (16) vs z_val bins (16) (v_val >= 7.0)',
        cmap='Blues',
        output_path=os.path.join(OUTPUT_DIR, 'case_0_heatmap_y_vs_z_v7.png')
    )

    print("All visualizations complete.")


if __name__ == '__main__':
    main()
