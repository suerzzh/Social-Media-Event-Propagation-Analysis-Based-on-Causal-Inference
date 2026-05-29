"""
PCMCI/LPCMCI因果发现分析 - 毕设可跑版
"""

import argparse
import re
import sys
import warnings
from datetime import datetime
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

warnings.filterwarnings('ignore')
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial Unicode MS', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False

try:
    from tigramite import data_processing as pp
    from tigramite import plotting as tp
    from tigramite.independence_tests.cmiknn import CMIknn
    from tigramite.independence_tests.parcorr import ParCorr
    from tigramite.lpcmci import LPCMCI
    from tigramite.pcmci import PCMCI
    try:
        from tigramite.independence_tests.gpdc import GPDC
        GPDC_AVAILABLE = True
    except ImportError:
        GPDC_AVAILABLE = False
        print("[WARN] GPDC 不可用，将在需要时自动降级为 CMIknn")
    print("[OK] Tigramite 已加载")
except ImportError as e:
    print(f"[ERROR] Tigramite 导入失败: {e}")
    sys.exit(1)


DATASET_PRESETS = {
    'generic': {
        'method': 'pcmci',
        'test': 'parcorr',
        'tau_max': 3,
        'pc_alpha': 0.2,
        'max_p': 3,
        'max_q': 3,
        'max_conds': 3,
        'include_u': False,
    },
    'b1c': {
        'method': 'lpcmci',
        'test': 'parcorr',
        'tau_max': 3,
        'pc_alpha': 0.2,
        'max_p': 3,
        'max_q': 3,
        'max_conds': 3,
        'include_u': True,
    },
    'douyin': {
        'method': 'pcmci',
        'test': 'parcorr',
        'tau_max': 2,
        'pc_alpha': 0.25,
        'max_p': 2,
        'max_q': 2,
        'max_conds': 2,
        'include_u': False,
    },
}

FAST_OVERRIDES = {
    'test': 'parcorr',
    'tau_max_cap': 2,
    'max_p': 2,
    'max_q': 2,
    'max_conds': 2,
    'pc_alpha_b1c': 0.2,
    'pc_alpha_douyin': 0.25,
    'pc_alpha_generic': 0.2,
}


def read_columns(data_path):
    return list(pd.read_csv(data_path, nrows=0).columns)



def detect_dataset_from_path(data_path):
    path_str = str(data_path).lower()
    scores = {'b1c': 0, 'douyin': 0, 'generic': 0}
    reasons = []

    if 'douyin' in path_str:
        scores['douyin'] += 3
        reasons.append('path contains douyin')
    if 'b1c' in path_str or 'timegraph/b1c' in path_str.replace('\\', '/'):
        scores['b1c'] += 3
        reasons.append('path contains b1c')

    best_mode = max(scores, key=scores.get)
    if scores[best_mode] == 0:
        return 'generic', scores, 'no path hint'
    return best_mode, scores, '; '.join(reasons)



def detect_dataset_from_columns(columns):
    has_u = 'U' in columns
    x_columns = [col for col in columns if re.fullmatch(r'X\d+', str(col))]
    x_set = set(x_columns)
    scores = {'b1c': 0, 'douyin': 0, 'generic': 0}
    reasons = []

    if has_u:
        scores['b1c'] += 5
        reasons.append('contains U column')
    if all(f'X{i}' in x_set for i in range(1, 7)) and has_u:
        scores['b1c'] += 3
        reasons.append('matches X1-X6 plus U structure')
    if all(f'X{i}' in x_set for i in range(1, 8)) and not has_u:
        scores['douyin'] += 5
        reasons.append('matches X1-X7 without U structure')
    elif len(x_columns) >= 7 and not has_u:
        scores['douyin'] += 3
        reasons.append('has many X columns without U')

    best_mode = max(scores, key=scores.get)
    if scores[best_mode] == 0:
        return 'generic', scores, 'no strong column hint'
    return best_mode, scores, '; '.join(reasons)



def resolve_dataset_mode(requested_dataset, data_path, columns):
    path_hint, path_scores, path_reason = detect_dataset_from_path(data_path)
    column_hint, column_scores, column_reason = detect_dataset_from_columns(columns)

    combined_scores = {
        mode: path_scores.get(mode, 0) + column_scores.get(mode, 0)
        for mode in DATASET_PRESETS.keys()
    }
    auto_detected = max(combined_scores, key=combined_scores.get)
    if combined_scores[auto_detected] == 0:
        auto_detected = 'generic'

    detection_reason = (
        f"path_hint={path_hint} ({path_reason}); "
        f"column_hint={column_hint} ({column_reason}); "
        f"combined_scores={combined_scores}"
    )

    if requested_dataset != 'auto':
        return {
            'dataset_mode': requested_dataset,
            'auto_detected_dataset': auto_detected,
            'path_hint': path_hint,
            'column_hint': column_hint,
            'detection_reason': detection_reason + f"; explicit_override={requested_dataset}",
            'x_column_count': len([col for col in columns if re.fullmatch(r'X\d+', str(col))]),
        }

    return {
        'dataset_mode': auto_detected,
        'auto_detected_dataset': auto_detected,
        'path_hint': path_hint,
        'column_hint': column_hint,
        'detection_reason': detection_reason,
        'x_column_count': len([col for col in columns if re.fullmatch(r'X\d+', str(col))]),
    }



def resolve_data_path(cli_data_path=None):
    if cli_data_path:
        return Path(cli_data_path)

    preferred = [
        Path('douyin_pcmci_12H_optimized.csv'),
        Path('test.csv'),
    ]
    for candidate in preferred:
        if candidate.exists():
            return candidate

    csv_candidates = sorted(Path('.').glob('*.csv'))
    if csv_candidates:
        return csv_candidates[0]
    return None



def load_data(data_path, include_u=False):
    print(f"\n[LOAD] 加载数据: {data_path}")
    df = pd.read_csv(data_path)
    print(f"[LOAD] 原始形状: {df.shape}")
    print(f"[LOAD] 列名: {list(df.columns)}")

    observed_vars = [col for col in df.columns if re.fullmatch(r'X\d+', str(col))]
    observed_vars = sorted(observed_vars, key=lambda name: int(name[1:]))

    if include_u:
        if 'U' in df.columns:
            observed_vars.append('U')
            print("[LOAD] 已纳入混杂变量 U")
        else:
            print("[WARN] 请求 include_u=True，但数据中不存在 U 列，将忽略")

    if not observed_vars:
        raise ValueError("未找到可用于分析的变量列。期望列名形如 X1、X2，或可选 U。")

    data = df[observed_vars].values
    print(f"[LOAD] 分析变量: {observed_vars}")
    print(f"[LOAD] 数据维度: {data.shape}")
    return data, observed_vars, df



def parse_dataset_info(data_path):
    path_str = str(data_path)
    dataset_type = next(
        (ds for ds in ['B1C', 'B1', 'A1C', 'A1', 'A2C', 'A2', 'C1C', 'C1', 'C2C', 'C2', 'D1C', 'D1', 'D2C', 'D2', 'D3C', 'D3'] if ds in path_str),
        'Unknown'
    )
    if 'Gaussian' in path_str or 'gaussian' in path_str.lower():
        noise_type = 'Gaussian'
    elif 'student' in path_str.lower():
        noise_type = 'Students_t'
    elif 'laplace' in path_str.lower():
        noise_type = 'Mixed_Laplace'
    else:
        noise_type = 'Unknown'

    match = re.search(r'(\d+)\s*[Vv]ariable', path_str)
    var_count = match.group(1) if match else 'Unknown'
    match = re.search(r'[Ll]ag\s*(\d+)', path_str)
    lag = match.group(1) if match else 'Unknown'
    match = re.search(r'_n(\d+)(?:_|\.|/|\\)', path_str)
    if match:
        sample_size = match.group(1)
    else:
        sample_size = next((n for n in ['5000', '3000', '1000', '500'] if f'n{n}' in path_str), 'Unknown')

    return {
        'dataset_type': dataset_type,
        'noise_type': noise_type,
        'var_count': var_count,
        'lag': lag,
        'sample_size': sample_size,
    }



def create_output_directory(data_path, dataset_mode=None):
    info = parse_dataset_info(data_path)
    parts = [
        info['dataset_type'],
        info['noise_type'],
        f"{info['var_count']}variable",
        f"lag{info['lag']}",
        f"n{info['sample_size']}",
    ]
    parts = [p for p in parts if 'Unknown' not in p]

    out = Path('run_data')
    if parts:
        for part in parts:
            out = out / part
    elif dataset_mode:
        out = out / dataset_mode
    else:
        out = out / Path(data_path).stem

    out.mkdir(parents=True, exist_ok=True)
    return out



def build_cond_ind_test(method):
    method = method.lower()
    if method == 'parcorr':
        print("[TEST] ParCorr（线性，最快）")
        return ParCorr(significance='analytic'), 'parcorr'
    if method == 'cmiknn':
        print("[TEST] CMIknn（非线性，更稳健）")
        return CMIknn(significance='shuffle_test', knn=10, shuffle_neighbors=5, transform='ranks'), 'cmiknn'
    if method == 'gpdc':
        if not GPDC_AVAILABLE:
            print("[WARN] GPDC 不可用，自动降级为 CMIknn")
            return build_cond_ind_test('cmiknn')
        print("[TEST] GPDC（非线性，较慢）")
        return GPDC(significance='analytic', gp_params=None), 'gpdc'
    raise ValueError(f"未知检验方法: {method}")



def infer_tau_max(data_path, fallback=3):
    path_str = str(data_path).lower()
    for lag_val in [4, 3, 2, 1]:
        if f'lag{lag_val}' in path_str or f'lag {lag_val}' in path_str:
            return lag_val
    return fallback



def choose_effective_config(args, data_path, columns):
    detection = resolve_dataset_mode(args.dataset, data_path, columns)
    dataset_mode = detection['dataset_mode']
    auto_detected_dataset = detection['auto_detected_dataset']
    preset = DATASET_PRESETS.get(dataset_mode, DATASET_PRESETS['generic']).copy()

    method = args.method if args.method is not None else preset['method']
    test_name = args.test if args.test is not None else preset['test']
    tau_max = args.tau_max if args.tau_max is not None else infer_tau_max(data_path, fallback=preset['tau_max'])
    pc_alpha = args.pc_alpha if args.pc_alpha is not None else preset['pc_alpha']
    max_p = args.max_p if args.max_p is not None else preset['max_p']
    max_q = args.max_q if args.max_q is not None else preset['max_q']
    max_conds = args.max_conds if args.max_conds is not None else preset['max_conds']

    if args.include_u:
        include_u = True
    elif args.exclude_u:
        include_u = False
    else:
        include_u = preset['include_u'] and ('U' in columns)

    if args.fast:
        test_name = 'parcorr' if args.test is None else args.test
        tau_max = min(tau_max, FAST_OVERRIDES['tau_max_cap'])
        if args.max_p is None:
            max_p = FAST_OVERRIDES['max_p']
        if args.max_q is None:
            max_q = FAST_OVERRIDES['max_q']
        if args.max_conds is None:
            max_conds = FAST_OVERRIDES['max_conds']
        if args.pc_alpha is None:
            pc_alpha_key = f'pc_alpha_{dataset_mode}' if f'pc_alpha_{dataset_mode}' in FAST_OVERRIDES else 'pc_alpha_generic'
            pc_alpha = FAST_OVERRIDES[pc_alpha_key]
        if method == 'lpcmci':
            print("[FAST] 快速模式已启用：LPCMCI 将使用更小的搜索空间")
        print("[FAST] 当前为快速探索模式，适合先跑通流程；正式实验建议使用更强配置复跑")

    return {
        'dataset_mode': dataset_mode,
        'auto_detected_dataset': auto_detected_dataset,
        'path_hint': detection['path_hint'],
        'column_hint': detection['column_hint'],
        'detection_reason': detection['detection_reason'],
        'x_column_count': detection['x_column_count'],
        'method': method,
        'test': test_name,
        'tau_max': tau_max,
        'pc_alpha': pc_alpha,
        'max_p': max_p,
        'max_q': max_q,
        'max_conds': max_conds,
        'include_u': include_u,
    }



def run_pcmci(data, var_names, tau_max, cond_ind_test, alpha_level, pc_alpha, max_conds_py=None, max_conds_px=None):
    print(f"\n[RUN] PCMCI | tau_max={tau_max} | alpha={alpha_level} | pc_alpha={pc_alpha}")
    df = pp.DataFrame(data, var_names=var_names)
    pcmci_obj = PCMCI(dataframe=df, cond_ind_test=cond_ind_test, verbosity=1)
    results = pcmci_obj.run_pcmci(
        tau_max=tau_max,
        pc_alpha=pc_alpha,
        alpha_level=alpha_level,
        max_conds_py=max_conds_py,
        max_conds_px=max_conds_px,
    )
    print("[RUN] PCMCI 完成")
    return results, pcmci_obj



def run_lpcmci(data, var_names, tau_max, cond_ind_test, alpha_level, pc_alpha, max_p_global=None, max_q_global=None):
    print(f"\n[RUN] LPCMCI | tau_max={tau_max} | alpha={alpha_level} | pc_alpha={pc_alpha}")
    print(f"[RUN] max_p_global={max_p_global} | max_q_global={max_q_global}")
    df = pp.DataFrame(data, var_names=var_names)
    lpcmci_obj = LPCMCI(dataframe=df, cond_ind_test=cond_ind_test, verbosity=1)
    run_kwargs = {
        'tau_max': tau_max,
        'pc_alpha': pc_alpha,
    }
    if max_p_global is not None:
        run_kwargs['max_p_global'] = max_p_global
    if max_q_global is not None:
        run_kwargs['max_q_global'] = max_q_global
    results = lpcmci_obj.run_lpcmci(**run_kwargs)
    print("[RUN] LPCMCI 完成")
    return results, lpcmci_obj



def summarize_significant_links(df_all):
    df_sig = df_all[df_all['Significant']].copy()
    lag_counts = {}
    if not df_sig.empty:
        lag_counts = df_sig.groupby('Lag').size().sort_index().to_dict()
    return df_sig, lag_counts



def save_summary(output_dir, summary):
    summary_txt_path = output_dir / 'run_summary.txt'
    lines = [
        f"dataset_mode={summary['dataset_mode']}",
        f"auto_detected_dataset={summary['auto_detected_dataset']}",
        f"data_path={summary['data_path']}",
        f"n_samples={summary['n_samples']}",
        f"n_vars={summary['n_vars']}",
        f"include_u={summary['include_u']}",
        f"method={summary['method']}",
        f"test={summary['test']}",
        f"tau_max={summary['tau_max']}",
        f"alpha={summary['alpha']}",
        f"pc_alpha={summary['pc_alpha']}",
        f"fast_mode={summary['fast_mode']}",
        f"significant_links={summary['significant_links']}",
        f"lag_counts={summary['lag_counts']}",
        f"elapsed_seconds={summary['elapsed_seconds']:.2f}",
    ]
    summary_txt_path.write_text('\n'.join(lines), encoding='utf-8')

    summary_csv_path = output_dir / 'run_summary.csv'
    pd.DataFrame([{**summary, 'lag_counts': str(summary['lag_counts'])}]).to_csv(summary_csv_path, index=False, encoding='utf-8-sig')
    return summary_txt_path, summary_csv_path



def print_and_save_results(results, var_names, tau_max, alpha_level, output_dir):
    p_matrix = results['p_matrix']
    val_matrix = results['val_matrix']
    rows = []

    print(f"\n[RESULT] 显著因果关系 (p < {alpha_level}):")
    print('=' * 70)

    count = 0
    for i, target in enumerate(var_names):
        for j, source in enumerate(var_names):
            for tau in range(tau_max + 1):
                pval = p_matrix[i, j, tau]
                effect_val = val_matrix[i, j, tau]
                is_significant = pval < alpha_level
                if is_significant:
                    count += 1
                    tag = 'Simultaneous' if tau == 0 else f'Lag{tau}'
                    print(f"  {source} --[{tag}]--> {target} | p={pval:.4f} | val={effect_val:.4f}")
                rows.append({
                    'From': source,
                    'To': target,
                    'Lag': tau,
                    'P_value': pval,
                    'Correlation': effect_val,
                    'Significant': is_significant,
                    'Type': 'Simultaneous' if tau == 0 else f'Lag{tau}',
                })

    print(f"\n[RESULT] 共 {count} 条显著关系")

    df_all = pd.DataFrame(rows).sort_values(['Significant', 'P_value'], ascending=[False, True])
    df_all.to_csv(output_dir / 'pcmci_results.csv', index=False, encoding='utf-8-sig')
    df_all.to_csv(output_dir / 'results_all.csv', index=False, encoding='utf-8-sig')

    df_sig, lag_counts = summarize_significant_links(df_all)
    if not df_sig.empty:
        df_sig.to_csv(output_dir / 'pcmci_significant_links.csv', index=False, encoding='utf-8-sig')
        df_sig.to_csv(output_dir / 'results_significant.csv', index=False, encoding='utf-8-sig')
    else:
        empty_df = df_all.head(0)
        empty_df.to_csv(output_dir / 'pcmci_significant_links.csv', index=False, encoding='utf-8-sig')
        empty_df.to_csv(output_dir / 'results_significant.csv', index=False, encoding='utf-8-sig')

    print(f"[SAVE] 完整结果: {output_dir / 'pcmci_results.csv'}")
    print(f"[SAVE] 显著关系: {output_dir / 'pcmci_significant_links.csv'}")
    return df_all, df_sig, lag_counts



def visualize(pcmci_obj, results, var_names, tau_max, alpha_level, save_path):
    try:
        p_matrix = results['p_matrix']
        val_matrix = results['val_matrix']
        graph = (p_matrix < alpha_level).astype(int)
        tp.plot_time_series_graph(graph=graph, val_matrix=val_matrix, var_names=var_names)
        plt.title('因果图', fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.close()
        print(f"[SAVE] 因果图已保存: {save_path}")
    except Exception as e:
        print(f"[WARN] 可视化失败: {e}")



def parse_args():
    parser = argparse.ArgumentParser(
        description='PCMCI/LPCMCI因果发现 - 毕设可跑版',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument('--data', type=str, default=None, help='数据文件路径；若不传则自动在当前目录搜索 CSV')
    parser.add_argument('--dataset', choices=['auto', 'b1c', 'douyin'], default='auto', help='数据集模式；auto 将根据表头自动识别')
    parser.add_argument('--method', choices=['pcmci', 'lpcmci'], default=None, help='因果发现方法；默认按数据集推荐')
    parser.add_argument('--test', choices=['parcorr', 'cmiknn', 'gpdc'], default=None, help='条件独立性检验器；默认按数据集推荐')
    parser.add_argument('--alpha', type=float, default=0.05, help='显著性阈值')
    parser.add_argument('--pc_alpha', type=float, default=None, help='PC 阶段 alpha；默认按数据集推荐')
    parser.add_argument('--tau_max', type=int, default=None, help='最大滞后阶数；默认按数据集推荐/路径推断')
    parser.add_argument('--max_p', type=int, default=None, help='LPCMCI 的 max_p_global；默认按数据集推荐')
    parser.add_argument('--max_q', type=int, default=None, help='LPCMCI 的 max_q_global；默认按数据集推荐')
    parser.add_argument('--max_conds', type=int, default=None, help='PCMCI 的最大条件集大小；默认按数据集推荐')
    parser.add_argument('--include_u', action='store_true', help='强制纳入 U 列（若存在）')
    parser.add_argument('--exclude_u', action='store_true', help='即使存在 U 列也不纳入分析')
    parser.add_argument('--fast', '--quick', action='store_true', dest='fast', help='快速探索模式：优先使用更快配置以先跑通流程')
    return parser.parse_args()



def main():
    args = parse_args()
    t0 = datetime.now()

    print('=' * 70)
    print('PCMCI/LPCMCI 因果发现分析（毕设可跑版）')
    print('=' * 70)

    data_path = resolve_data_path(args.data)
    if data_path is None:
        print('[ERROR] 未找到数据文件，请使用 --data 指定路径')
        return
    if not data_path.exists():
        print(f'[ERROR] 文件不存在: {data_path}')
        return

    columns = read_columns(data_path)
    config = choose_effective_config(args, data_path, columns)

    print(f"[INFO] 数据文件: {data_path}")
    print(f"[INFO] 数据集模式: {config['dataset_mode']}（自动识别: {config['auto_detected_dataset']}）")
    print(f"[INFO] path_hint={config['path_hint']} | column_hint={config['column_hint']}")
    print(f"[INFO] detection_reason: {config['detection_reason']}")
    print(f"[INFO] include_u: {config['include_u']}")
    print(f"[INFO] 方法/检验器: {config['method']} / {config['test']}")

    data, var_names, raw_df = load_data(data_path, include_u=config['include_u'])
    n_samples, n_vars = data.shape

    output_dir = create_output_directory(data_path, dataset_mode=config['dataset_mode'])
    print(f"[INFO] 输出目录: {output_dir}")

    tau_max = config['tau_max']
    print(f"[INFO] 样本量={n_samples} | 变量数={n_vars} | tau_max={tau_max}")

    cond_ind_test, actual_test = build_cond_ind_test(config['test'])

    if config['method'] == 'lpcmci':
        results, model = run_lpcmci(
            data,
            var_names,
            tau_max=tau_max,
            cond_ind_test=cond_ind_test,
            alpha_level=args.alpha,
            pc_alpha=config['pc_alpha'],
            max_p_global=config['max_p'],
            max_q_global=config['max_q'],
        )
    else:
        results, model = run_pcmci(
            data,
            var_names,
            tau_max=tau_max,
            cond_ind_test=cond_ind_test,
            alpha_level=args.alpha,
            pc_alpha=config['pc_alpha'],
            max_conds_py=config['max_conds'],
            max_conds_px=config['max_conds'],
        )

    df_all, df_sig, lag_counts = print_and_save_results(results, var_names, tau_max, args.alpha, output_dir)
    visualize(model, results, var_names, tau_max, args.alpha, output_dir / 'causal_graph.png')

    info = parse_dataset_info(data_path)
    info.update({
        'resolved_dataset_mode': config['dataset_mode'],
        'auto_detected_dataset': config['auto_detected_dataset'],
        'data_path': str(Path(data_path).resolve()),
        'file_name': Path(data_path).name,
        'path_hint': config['path_hint'],
        'column_hint': config['column_hint'],
        'detection_reason': config['detection_reason'],
        'x_column_count': config['x_column_count'],
        'n_rows_raw': len(raw_df),
        'n_samples_used': n_samples,
        'n_vars_used': n_vars,
        'columns': ','.join(map(str, raw_df.columns)),
        'variables_used': ','.join(var_names),
        'has_u_column': 'U' in raw_df.columns,
        'include_u_used': config['include_u'],
        'method': config['method'],
        'test': actual_test,
        'tau_max': tau_max,
        'alpha': args.alpha,
        'pc_alpha': config['pc_alpha'],
        'fast_mode': args.fast,
    })
    pd.DataFrame([info]).to_csv(output_dir / 'dataset_info.csv', index=False, encoding='utf-8-sig')

    elapsed = datetime.now() - t0
    elapsed_seconds = elapsed.total_seconds()
    summary = {
        'dataset_mode': config['dataset_mode'],
        'auto_detected_dataset': config['auto_detected_dataset'],
        'data_path': str(data_path),
        'n_samples': n_samples,
        'n_vars': n_vars,
        'include_u': config['include_u'],
        'method': config['method'],
        'test': actual_test,
        'tau_max': tau_max,
        'alpha': args.alpha,
        'pc_alpha': config['pc_alpha'],
        'fast_mode': args.fast,
        'significant_links': len(df_sig),
        'lag_counts': lag_counts,
        'elapsed_seconds': elapsed_seconds,
    }
    summary_txt_path, summary_csv_path = save_summary(output_dir, summary)

    print('\n' + '=' * 70)
    print('[SUMMARY] 运行摘要')
    print(f"[SUMMARY] 数据集类型: {config['dataset_mode']}（自动识别: {config['auto_detected_dataset']}）")
    print(f"[SUMMARY] 样本量/变量数/tau_max: {n_samples} / {n_vars} / {tau_max}")
    print(f"[SUMMARY] 方法/检验器: {config['method']} / {actual_test}")
    print(f"[SUMMARY] 显著边总数: {len(df_sig)}")
    if lag_counts:
        for lag, lag_count in lag_counts.items():
            print(f"[SUMMARY] Lag {lag}: {lag_count} 条显著边")
    else:
        print('[SUMMARY] 无显著边')
    print(f"[SUMMARY] 总耗时: {elapsed}")
    if args.fast:
        print('[SUMMARY] 当前结果来自快速探索模式，正式实验建议关闭 --fast 或改用更强配置复跑')

    print('\n[FILES] 输出文件:')
    print(f"[FILES] - {output_dir / 'pcmci_results.csv'}")
    print(f"[FILES] - {output_dir / 'pcmci_significant_links.csv'}")
    print(f"[FILES] - {output_dir / 'dataset_info.csv'}")
    print(f"[FILES] - {output_dir / 'causal_graph.png'}")
    print(f"[FILES] - {summary_txt_path}")
    print(f"[FILES] - {summary_csv_path}")
    print(f"[FILES] - {output_dir / 'results_all.csv'} (兼容旧命名)")
    print(f"[FILES] - {output_dir / 'results_significant.csv'} (兼容旧命名)")


if __name__ == '__main__':
    main()
