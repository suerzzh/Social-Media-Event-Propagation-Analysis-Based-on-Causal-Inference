"""
Batch LPCMCI runner for B1C experiments.

Default behavior matches the project evaluation protocol:
- input: B1C/lag {2,3}/{500,1000,3000}/*.csv
- variables: X1-X6 only, U excluded by default
- output: run_data_lpcmci/B1C/Gaussian/6variable/lag*/n*/
"""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

import pandas as pd

from tigramite import data_processing as pp
from tigramite.independence_tests.cmiknn import CMIknn
from tigramite.independence_tests.parcorr import ParCorr
from tigramite.lpcmci import LPCMCI

try:
    from tigramite.independence_tests.gpdc import GPDC

    GPDC_AVAILABLE = True
except Exception:
    GPDC_AVAILABLE = False


PROJECT_ROOT = Path(__file__).resolve().parent

# Set SINGLE_DATA_PATH to run one dataset with:
#   python run_lpcmci_b1c.py
# Set it to None to use the batch configuration from command-line arguments.
SINGLE_DATA_PATH = PROJECT_ROOT / "B1C" / "lag 2" / "1000" / "nonlinear_confounded_n1000_vars6_lag2_gaussian.csv"
SINGLE_TAU_MAX = 3
SINGLE_OUTPUT_DIR = None
SINGLE_TEST = "cmiknn"
SINGLE_ALPHA = 0.05
SINGLE_PC_ALPHA = 0.2
SINGLE_MAX_P = 3
SINGLE_MAX_Q = 3
SINGLE_INCLUDE_U = False
SINGLE_VERBOSITY = 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Batch LPCMCI runner for B1C datasets.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--input-root", default="B1C", help="B1C input data directory")
    parser.add_argument("--output-root", default="run_data_lpcmci", help="Output root directory")
    parser.add_argument("--data", default=None, help="Run one explicit CSV file instead of batch mode")
    parser.add_argument("--output-dir", default=None, help="Explicit output directory for --data mode")
    parser.add_argument("--lags", nargs="+", type=int, default=[2, 3], help="Dataset lag settings")
    parser.add_argument("--samples", nargs="+", type=int, default=[500, 1000, 3000], help="Sample sizes")
    parser.add_argument("--test", choices=["gpdc", "cmiknn", "parcorr"], default="gpdc")
    parser.add_argument("--alpha", type=float, default=0.05, help="Significance level")
    parser.add_argument("--pc-alpha", type=float, default=0.2, help="LPCMCI PC alpha")
    parser.add_argument("--max-p", type=int, default=3, help="LPCMCI max_p_global")
    parser.add_argument("--max-q", type=int, default=3, help="LPCMCI max_q_global")
    parser.add_argument("--include-u", action="store_true", help="Include confounder U if present")
    parser.add_argument("--verbosity", type=int, default=0)
    return parser.parse_args()


def build_test(name: str):
    if name == "gpdc":
        if GPDC_AVAILABLE:
            return GPDC(significance="analytic", gp_params=None), "gpdc"
        print("[WARN] GPDC import failed. Falling back to CMIknn.")
        return build_test("cmiknn")
    if name == "cmiknn":
        return CMIknn(significance="shuffle_test", knn=10, shuffle_neighbors=5, transform="ranks"), "cmiknn"
    if name == "parcorr":
        return ParCorr(significance="analytic"), "parcorr"
    raise ValueError(f"Unknown test: {name}")


def input_path(input_root: Path, lag: int, sample_size: int) -> Path:
    folder = input_root / f"lag {lag}" / str(sample_size)
    matches = sorted(folder.glob("*.csv"))
    if not matches:
        raise FileNotFoundError(f"No csv found in {folder}")
    return matches[0]


def resolve_data_path(path: Path) -> Path:
    if path.exists():
        return path

    parent = path.parent
    if parent.exists():
        matches = sorted(parent.glob("*.csv"))
        if len(matches) == 1:
            print(f"[WARN] Configured file does not exist. Using the only CSV in the folder: {matches[0]}")
            return matches[0]
        if len(matches) > 1:
            candidates = "\n".join(f"  - {candidate}" for candidate in matches)
            raise FileNotFoundError(
                f"Data file not found: {path}\n"
                f"Multiple CSV files exist in the same folder. Please set SINGLE_DATA_PATH to one of:\n{candidates}"
            )

    raise FileNotFoundError(f"Data file not found: {path}")


def infer_lag_from_path(path: Path) -> int:
    text = str(path).lower()
    for lag in [4, 3, 2, 1]:
        if f"lag {lag}" in text or f"lag{lag}" in text:
            return lag
    raise ValueError(f"Cannot infer lag from path: {path}. Please use --lags <lag>.")


def infer_sample_size_from_path(path: Path) -> int:
    for part in [path.parent.name, path.stem]:
        lowered = part.lower()
        if lowered.isdigit():
            return int(lowered)
        if lowered.startswith("n") and lowered[1:].isdigit():
            return int(lowered[1:])

    import re

    match = re.search(r"_n(\d+)(?:_|$)", path.stem.lower())
    if match:
        return int(match.group(1))

    raise ValueError(f"Cannot infer sample size from path: {path}.")


def output_dir(output_root: Path, lag: int, sample_size: int) -> Path:
    return output_root / "B1C" / "Gaussian" / "6variable" / f"lag{lag}" / f"n{sample_size}"


def load_data(path: Path, include_u: bool):
    df = pd.read_csv(path)
    variables = sorted([col for col in df.columns if col.startswith("X")], key=lambda name: int(name[1:]))
    if include_u and "U" in df.columns:
        variables.append("U")
    data = df[variables].to_numpy()
    return data, variables, df


def matrix_to_tables(results: dict, var_names: list[str], tau_max: int, alpha: float):
    p_matrix = results["p_matrix"]
    val_matrix = results["val_matrix"]
    graph = results.get("graph")
    rows = []

    for target_idx, target in enumerate(var_names):
        for source_idx, source in enumerate(var_names):
            for tau in range(tau_max + 1):
                p_value = float(p_matrix[target_idx, source_idx, tau])
                value = float(val_matrix[target_idx, source_idx, tau])
                causal = p_value < alpha
                graph_mark = ""
                if graph is not None:
                    graph_mark = str(graph[target_idx, source_idx, tau])
                rows.append(
                    {
                        "From": source,
                        "To": target,
                        "Lag": tau,
                        "P_value": p_value,
                        "Value": value,
                        "Causal": bool(causal),
                        "Type": "Simultaneous" if tau == 0 else f"Lag{tau}",
                        "Edge_Type": "Simultaneous" if tau == 0 else "Lagged",
                        "Graph": graph_mark,
                    }
                )

    all_df = pd.DataFrame(rows).sort_values(["Causal", "P_value"], ascending=[False, True])
    sig_df = all_df[all_df["Causal"]].copy()
    return all_df, sig_df


def run_one(
    data_path: Path,
    out_dir: Path,
    tau_max: int,
    test_name: str,
    alpha: float,
    pc_alpha: float,
    max_p: int,
    max_q: int,
    include_u: bool,
    verbosity: int,
) -> dict:
    start = datetime.now()
    out_dir.mkdir(parents=True, exist_ok=True)

    data, variables, raw_df = load_data(data_path, include_u=include_u)
    cond_ind_test, actual_test = build_test(test_name)
    dataframe = pp.DataFrame(data, var_names=variables)
    model = LPCMCI(dataframe=dataframe, cond_ind_test=cond_ind_test, verbosity=verbosity)
    results = model.run_lpcmci(
        tau_max=tau_max,
        pc_alpha=pc_alpha,
        max_p_global=max_p,
        max_q_global=max_q,
    )

    all_df, sig_df = matrix_to_tables(results, variables, tau_max=tau_max, alpha=alpha)
    all_df.to_csv(out_dir / "lpcmci_results.csv", index=False, encoding="utf-8-sig")
    sig_df.to_csv(out_dir / "lpcmci_significant_links.csv", index=False, encoding="utf-8-sig")

    info = {
        "dataset_type": "B1C",
        "noise_type": "Gaussian",
        "var_count": 6,
        "lag": tau_max,
        "sample_size": len(raw_df),
        "method": "LPCMCI",
        "requested_test": test_name,
        "actual_test": actual_test,
        "alpha": alpha,
        "pc_alpha": pc_alpha,
        "max_p_global": max_p,
        "max_q_global": max_q,
        "include_u": include_u,
        "variables_used": ",".join(variables),
        "input_file": str(data_path.resolve()),
        "elapsed_seconds": (datetime.now() - start).total_seconds(),
    }
    pd.DataFrame([info]).to_csv(out_dir / "dataset_info.csv", index=False, encoding="utf-8-sig")

    return {
        "input": str(data_path),
        "output": str(out_dir),
        "variables": ",".join(variables),
        "significant_links": len(sig_df),
        "elapsed_seconds": info["elapsed_seconds"],
        "actual_test": actual_test,
    }


def main() -> None:
    args = parse_args()
    input_root = PROJECT_ROOT / args.input_root
    output_root = PROJECT_ROOT / args.output_root

    if SINGLE_DATA_PATH is not None and args.data is None:
        data_path = Path(SINGLE_DATA_PATH)
        if not data_path.is_absolute():
            data_path = PROJECT_ROOT / data_path
        data_path = resolve_data_path(data_path)

        tau_max = SINGLE_TAU_MAX if SINGLE_TAU_MAX is not None else infer_lag_from_path(data_path)
        sample_size = infer_sample_size_from_path(data_path)
        out_dir = Path(SINGLE_OUTPUT_DIR) if SINGLE_OUTPUT_DIR else output_dir(output_root, tau_max, sample_size)
        if not out_dir.is_absolute():
            out_dir = PROJECT_ROOT / out_dir

        print(f"[RUN] LPCMCI configured single file lag{tau_max} n{sample_size}: {data_path}")
        summary = run_one(
            data_path=data_path,
            out_dir=out_dir,
            tau_max=tau_max,
            test_name=SINGLE_TEST,
            alpha=SINGLE_ALPHA,
            pc_alpha=SINGLE_PC_ALPHA,
            max_p=SINGLE_MAX_P,
            max_q=SINGLE_MAX_Q,
            include_u=SINGLE_INCLUDE_U,
            verbosity=SINGLE_VERBOSITY,
        )
        print(
            f"[DONE] links={summary['significant_links']} "
            f"test={summary['actual_test']} elapsed={summary['elapsed_seconds']:.2f}s"
        )
        return

    if args.data:
        data_path = Path(args.data)
        if not data_path.is_absolute():
            data_path = PROJECT_ROOT / data_path
        data_path = resolve_data_path(data_path)

        tau_max = args.lags[0] if args.lags else infer_lag_from_path(data_path)
        sample_size = infer_sample_size_from_path(data_path)
        out_dir = Path(args.output_dir) if args.output_dir else output_dir(output_root, tau_max, sample_size)
        if not out_dir.is_absolute():
            out_dir = PROJECT_ROOT / out_dir

        print(f"[RUN] LPCMCI single file lag{tau_max} n{sample_size}: {data_path}")
        summary = run_one(
            data_path=data_path,
            out_dir=out_dir,
            tau_max=tau_max,
            test_name=args.test,
            alpha=args.alpha,
            pc_alpha=args.pc_alpha,
            max_p=args.max_p,
            max_q=args.max_q,
            include_u=args.include_u,
            verbosity=args.verbosity,
        )
        print(
            f"[DONE] links={summary['significant_links']} "
            f"test={summary['actual_test']} elapsed={summary['elapsed_seconds']:.2f}s"
        )
        return

    summaries = []
    for lag in args.lags:
        for sample_size in args.samples:
            data_path = input_path(input_root, lag, sample_size)
            out_dir = output_dir(output_root, lag, sample_size)
            print(f"[RUN] LPCMCI lag{lag} n{sample_size}: {data_path}")
            summary = run_one(
                data_path=data_path,
                out_dir=out_dir,
                tau_max=lag,
                test_name=args.test,
                alpha=args.alpha,
                pc_alpha=args.pc_alpha,
                max_p=args.max_p,
                max_q=args.max_q,
                include_u=args.include_u,
                verbosity=args.verbosity,
            )
            summaries.append(summary)
            print(
                f"[DONE] links={summary['significant_links']} "
                f"test={summary['actual_test']} elapsed={summary['elapsed_seconds']:.2f}s"
            )

    summary_df = pd.DataFrame(summaries)
    output_root.mkdir(parents=True, exist_ok=True)
    summary_df.to_csv(output_root / "lpcmci_batch_summary.csv", index=False, encoding="utf-8-sig")
    print(f"[SAVE] {output_root / 'lpcmci_batch_summary.csv'}")


if __name__ == "__main__":
    main()
