"""
Batch nonlinear Kernel Granger runner for B1C experiments.

The test compares a restricted nonlinear autoregressive model against a full
model that additionally contains the candidate source lag. The nonlinear model
uses an RBF Nystroem feature map plus ridge regression, and the p-value is
estimated by permutation of the candidate source-lag feature.
"""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.kernel_approximation import Nystroem
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import TimeSeriesSplit
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


PROJECT_ROOT = Path(__file__).resolve().parent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Batch Kernel Granger runner for B1C datasets.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--input-root", default="B1C", help="B1C input data directory")
    parser.add_argument("--output-root", default="run_data_kernel_granger", help="Output root directory")
    parser.add_argument("--lags", nargs="+", type=int, default=[2, 3], help="Dataset lag settings")
    parser.add_argument("--samples", nargs="+", type=int, default=[500, 1000, 3000], help="Sample sizes")
    parser.add_argument("--alpha", type=float, default=0.05, help="Significance level")
    parser.add_argument("--permutations", type=int, default=30, help="Permutation count for p-values")
    parser.add_argument("--components", type=int, default=120, help="Nystroem kernel feature count")
    parser.add_argument("--ridge-alpha", type=float, default=1.0, help="Ridge regularization")
    parser.add_argument("--gamma", type=float, default=None, help="RBF gamma; default is 1 / n_features")
    parser.add_argument("--cv-splits", type=int, default=3, help="TimeSeriesSplit folds")
    parser.add_argument("--max-rows", type=int, default=1500, help="Evenly subsample rows for speed; 0 disables")
    parser.add_argument("--include-u", action="store_true", help="Include confounder U if present")
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()


def input_path(input_root: Path, lag: int, sample_size: int) -> Path:
    folder = input_root / f"lag {lag}" / str(sample_size)
    matches = sorted(folder.glob("*.csv"))
    if not matches:
        raise FileNotFoundError(f"No csv found in {folder}")
    return matches[0]


def output_dir(output_root: Path, lag: int, sample_size: int) -> Path:
    return output_root / "B1C" / "Gaussian" / "6variable" / f"lag{lag}" / f"n{sample_size}"


def load_data(path: Path, include_u: bool):
    df = pd.read_csv(path)
    variables = sorted([col for col in df.columns if col.startswith("X")], key=lambda name: int(name[1:]))
    if include_u and "U" in df.columns:
        variables.append("U")
    return df[variables].to_numpy(dtype=float), variables, df


def build_lagged_matrix(data: np.ndarray, tau_max: int):
    rows = []
    targets = []
    feature_index = {}
    n_samples, n_vars = data.shape

    for var_idx in range(n_vars):
        for lag in range(1, tau_max + 1):
            feature_index[(var_idx, lag)] = len(feature_index)

    for t in range(tau_max, n_samples):
        features = []
        for var_idx in range(n_vars):
            for lag in range(1, tau_max + 1):
                features.append(data[t - lag, var_idx])
        rows.append(features)
        targets.append(data[t])

    return np.asarray(rows), np.asarray(targets), feature_index


def subsample_if_needed(X: np.ndarray, Y: np.ndarray, max_rows: int):
    if max_rows <= 0 or len(X) <= max_rows:
        return X, Y
    idx = np.linspace(0, len(X) - 1, max_rows).astype(int)
    return X[idx], Y[idx]


def make_model(n_features: int, components: int, ridge_alpha: float, gamma: float | None, seed: int):
    n_components = min(components, max(10, n_features * 5))
    actual_gamma = gamma if gamma is not None else 1.0 / max(n_features, 1)
    return make_pipeline(
        StandardScaler(),
        Nystroem(kernel="rbf", gamma=actual_gamma, n_components=n_components, random_state=seed),
        Ridge(alpha=ridge_alpha),
    )


def cv_mse(X: np.ndarray, y: np.ndarray, cv_splits: int, components: int, ridge_alpha: float, gamma: float | None, seed: int):
    if len(X) < cv_splits + 2:
        raise ValueError("Not enough rows for requested CV splits")
    splitter = TimeSeriesSplit(n_splits=cv_splits)
    losses = []
    for fold, (train_idx, test_idx) in enumerate(splitter.split(X)):
        model = make_model(X.shape[1], components, ridge_alpha, gamma, seed + fold)
        model.fit(X[train_idx], y[train_idx])
        pred = model.predict(X[test_idx])
        losses.append(mean_squared_error(y[test_idx], pred))
    return float(np.mean(losses))


def kernel_granger_test(
    X_all: np.ndarray,
    y: np.ndarray,
    candidate_col: int,
    cv_splits: int,
    permutations: int,
    components: int,
    ridge_alpha: float,
    gamma: float | None,
    rng: np.random.Generator,
    seed: int,
):
    mask = np.ones(X_all.shape[1], dtype=bool)
    mask[candidate_col] = False
    X_restricted = X_all[:, mask]

    restricted_mse = cv_mse(X_restricted, y, cv_splits, components, ridge_alpha, gamma, seed)
    full_mse = cv_mse(X_all, y, cv_splits, components, ridge_alpha, gamma, seed + 1000)
    improvement = restricted_mse - full_mse

    if improvement <= 0:
        return 1.0, improvement, restricted_mse, full_mse

    null_improvements = []
    for perm_idx in range(permutations):
        X_perm = X_all.copy()
        X_perm[:, candidate_col] = X_perm[rng.permutation(len(X_perm)), candidate_col]
        perm_mse = cv_mse(X_perm, y, cv_splits, components, ridge_alpha, gamma, seed + 2000 + perm_idx)
        null_improvements.append(restricted_mse - perm_mse)

    null_arr = np.asarray(null_improvements)
    p_value = (np.sum(null_arr >= improvement) + 1.0) / (permutations + 1.0)
    return float(p_value), float(improvement), float(restricted_mse), float(full_mse)


def run_one(
    data_path: Path,
    out_dir: Path,
    tau_max: int,
    alpha: float,
    permutations: int,
    components: int,
    ridge_alpha: float,
    gamma: float | None,
    cv_splits: int,
    max_rows: int,
    include_u: bool,
    seed: int,
) -> dict:
    start = datetime.now()
    out_dir.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(seed)

    data, variables, raw_df = load_data(data_path, include_u=include_u)
    X_all, Y_all, feature_index = build_lagged_matrix(data, tau_max=tau_max)
    X_all, Y_all = subsample_if_needed(X_all, Y_all, max_rows=max_rows)

    rows = []
    for target_idx, target in enumerate(variables):
        y = Y_all[:, target_idx]
        for source_idx, source in enumerate(variables):
            for lag in range(1, tau_max + 1):
                candidate_col = feature_index[(source_idx, lag)]
                p_value, improvement, restricted_mse, full_mse = kernel_granger_test(
                    X_all=X_all,
                    y=y,
                    candidate_col=candidate_col,
                    cv_splits=cv_splits,
                    permutations=permutations,
                    components=components,
                    ridge_alpha=ridge_alpha,
                    gamma=gamma,
                    rng=rng,
                    seed=seed + target_idx * 100 + source_idx * 10 + lag,
                )
                causal = p_value < alpha and improvement > 0
                rows.append(
                    {
                        "From": source,
                        "To": target,
                        "Lag": lag,
                        "P_value": p_value,
                        "Value": improvement,
                        "Causal": bool(causal),
                        "Type": f"Lag{lag}",
                        "Edge_Type": "Lagged",
                        "Restricted_MSE": restricted_mse,
                        "Full_MSE": full_mse,
                    }
                )

    all_df = pd.DataFrame(rows).sort_values(["Causal", "P_value", "Value"], ascending=[False, True, False])
    sig_df = all_df[all_df["Causal"]].copy()
    all_df.to_csv(out_dir / "kernel_granger_results.csv", index=False, encoding="utf-8-sig")
    sig_df.to_csv(out_dir / "kernel_granger_significant_links.csv", index=False, encoding="utf-8-sig")

    info = {
        "dataset_type": "B1C",
        "noise_type": "Gaussian",
        "var_count": 6,
        "lag": tau_max,
        "sample_size": len(raw_df),
        "method": "Kernel_Granger",
        "alpha": alpha,
        "permutations": permutations,
        "components": components,
        "ridge_alpha": ridge_alpha,
        "gamma": gamma if gamma is not None else "auto",
        "cv_splits": cv_splits,
        "max_rows": max_rows,
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
    }


def main() -> None:
    args = parse_args()
    input_root = PROJECT_ROOT / args.input_root
    output_root = PROJECT_ROOT / args.output_root
    summaries = []

    for lag in args.lags:
        for sample_size in args.samples:
            data_path = input_path(input_root, lag, sample_size)
            out_dir = output_dir(output_root, lag, sample_size)
            print(f"[RUN] Kernel Granger lag{lag} n{sample_size}: {data_path}")
            summary = run_one(
                data_path=data_path,
                out_dir=out_dir,
                tau_max=lag,
                alpha=args.alpha,
                permutations=args.permutations,
                components=args.components,
                ridge_alpha=args.ridge_alpha,
                gamma=args.gamma,
                cv_splits=args.cv_splits,
                max_rows=args.max_rows,
                include_u=args.include_u,
                seed=args.seed,
            )
            summaries.append(summary)
            print(f"[DONE] links={summary['significant_links']} elapsed={summary['elapsed_seconds']:.2f}s")

    summary_df = pd.DataFrame(summaries)
    output_root.mkdir(parents=True, exist_ok=True)
    summary_df.to_csv(output_root / "kernel_granger_batch_summary.csv", index=False, encoding="utf-8-sig")
    print(f"[SAVE] {output_root / 'kernel_granger_batch_summary.csv'}")


if __name__ == "__main__":
    main()
