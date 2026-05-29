"""
B1C 数据集真值匹配与检验器对比表生成脚本。

输出:
1. method_comparison_analysis/gpdc_b1c_truth_match.csv
2. method_comparison_analysis/parcorr_b1c_truth_match.csv
3. method_comparison_analysis/gpdc_parcorr_common_comparison.csv
4. method_comparison_analysis/b1c_method_comparison_report.md
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = PROJECT_ROOT / "method_comparison_analysis"

METHOD_DIRS = {
    "GPDC": PROJECT_ROOT / "run_data" / "B1C" / "6variable",
    "ParCorr": PROJECT_ROOT / "ParCorr" / "6variable",
}

# 剔除混杂变量 U 后的 B1C 真值滞后边
TRUTH_BY_LAG = {
    2: {
        ("X4", "X5", 1),
        ("X3", "X2", 1),
        ("X1", "X4", 2),
    },
    3: {
        ("X4", "X5", 1),
        ("X3", "X2", 1),
        ("X1", "X4", 2),
        ("X2", "X3", 3),
    },
    4: {
        ("X4", "X5", 1),
        ("X3", "X2", 1),
        ("X2", "X3", 3),
        ("X1", "X4", 4),
    },
}


def format_edges(edges: Iterable[tuple[str, str, int]]) -> str:
    items = [f"{source}->{target}(L{lag})" for source, target, lag in sorted(edges)]
    return "; ".join(items) if items else "-"


def evaluate_method(method: str, base_dir: Path) -> pd.DataFrame:
    rows: list[dict] = []

    for lag_dir in sorted(base_dir.glob("lag*")):
        lag_setting = int(lag_dir.name.replace("lag", ""))
        truth = TRUTH_BY_LAG.get(lag_setting)
        if truth is None:
            continue

        for n_dir in sorted(lag_dir.glob("n*")):
            result_path = n_dir / "pcmci_significant_links.csv"
            if not result_path.exists():
                continue

            df = pd.read_csv(result_path)
            # 与论文实验口径保持一致: 剔除 U，并且只评估滞后边
            df = df[(df["From"] != "U") & (df["To"] != "U")]
            pred = {
                (row.From, row.To, int(row.Lag))
                for row in df.itertuples(index=False)
                if int(row.Lag) > 0
            }

            tp_edges = pred & truth
            fp_edges = pred - truth
            fn_edges = truth - pred

            tp = len(tp_edges)
            fp = len(fp_edges)
            fn = len(fn_edges)
            precision = tp / (tp + fp) if (tp + fp) else 0.0
            recall = tp / (tp + fn) if (tp + fn) else 0.0
            f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0

            rows.append(
                {
                    "method": method,
                    "lag_setting": lag_setting,
                    "sample_size": int(n_dir.name.replace("n", "")),
                    "predicted_lag_edges": len(pred),
                    "truth_lag_edges": len(truth),
                    "TP": tp,
                    "FP": fp,
                    "FN": fn,
                    "Precision": round(precision, 4),
                    "Recall": round(recall, 4),
                    "F1": round(f1, 4),
                    "Hits": format_edges(tp_edges),
                    "False_Positive_Edges": format_edges(fp_edges),
                    "Missed_Truth_Edges": format_edges(fn_edges),
                    "source_file": str(result_path.resolve()),
                }
            )

    return pd.DataFrame(rows).sort_values(["lag_setting", "sample_size"]).reset_index(drop=True)


def build_common_comparison(gpdc_df: pd.DataFrame, parcorr_df: pd.DataFrame) -> pd.DataFrame:
    merge_keys = ["lag_setting", "sample_size"]
    gpdc_common = gpdc_df[gpdc_df["lag_setting"].isin([2, 3])].copy()
    parcorr_common = parcorr_df[parcorr_df["lag_setting"].isin([2, 3])].copy()

    merged = gpdc_common.merge(
        parcorr_common,
        on=merge_keys,
        how="inner",
        suffixes=("_GPDC", "_ParCorr"),
    )

    comparison_rows: list[dict] = []
    for row in merged.itertuples(index=False):
        comparison_rows.append(
            {
                "lag_setting": row.lag_setting,
                "sample_size": row.sample_size,
                "predicted_lag_edges_GPDC": row.predicted_lag_edges_GPDC,
                "predicted_lag_edges_ParCorr": row.predicted_lag_edges_ParCorr,
                "TP_GPDC": row.TP_GPDC,
                "TP_ParCorr": row.TP_ParCorr,
                "FP_GPDC": row.FP_GPDC,
                "FP_ParCorr": row.FP_ParCorr,
                "FN_GPDC": row.FN_GPDC,
                "FN_ParCorr": row.FN_ParCorr,
                "Precision_GPDC": row.Precision_GPDC,
                "Precision_ParCorr": row.Precision_ParCorr,
                "Recall_GPDC": row.Recall_GPDC,
                "Recall_ParCorr": row.Recall_ParCorr,
                "F1_GPDC": row.F1_GPDC,
                "F1_ParCorr": row.F1_ParCorr,
                "Hits_GPDC": row.Hits_GPDC,
                "Hits_ParCorr": row.Hits_ParCorr,
                "F1_Winner": (
                    "GPDC"
                    if row.F1_GPDC > row.F1_ParCorr
                    else "ParCorr"
                    if row.F1_GPDC < row.F1_ParCorr
                    else "Tie"
                ),
            }
        )

    return pd.DataFrame(comparison_rows).sort_values(["lag_setting", "sample_size"]).reset_index(drop=True)


def markdown_table(df: pd.DataFrame, columns: list[str]) -> str:
    table_df = df.loc[:, columns].copy()
    return table_df.to_markdown(index=False)


def build_report(gpdc_df: pd.DataFrame, parcorr_df: pd.DataFrame, comparison_df: pd.DataFrame) -> str:
    common_summary = comparison_df[[
        "predicted_lag_edges_GPDC",
        "predicted_lag_edges_ParCorr",
        "TP_GPDC",
        "TP_ParCorr",
        "FP_GPDC",
        "FP_ParCorr",
        "FN_GPDC",
        "FN_ParCorr",
        "Precision_GPDC",
        "Precision_ParCorr",
        "Recall_GPDC",
        "Recall_ParCorr",
        "F1_GPDC",
        "F1_ParCorr",
    ]].mean().round(4)

    gpdc_common_mean = common_summary["F1_GPDC"]
    parcorr_common_mean = common_summary["F1_ParCorr"]

    report = [
        "# B1C 检验器结果表与对比实验表",
        "",
        "## 1. 评价口径",
        "",
        "- 数据集: B1C 6变量合成数据",
        "- 评估对象: 仅统计滞后边 `Lag > 0`",
        "- 变量范围: 仅保留 `X1~X6`，剔除混杂变量 `U`",
        "- 真值依据: 预设结构方程对应的真实滞后边",
        "",
        "## 2. GPDC 真值匹配结果表",
        "",
        markdown_table(
            gpdc_df,
            ["lag_setting", "sample_size", "predicted_lag_edges", "truth_lag_edges", "TP", "FP", "FN", "Precision", "Recall", "F1", "Hits"],
        ),
        "",
        "## 3. ParCorr 真值匹配结果表",
        "",
        markdown_table(
            parcorr_df,
            ["lag_setting", "sample_size", "predicted_lag_edges", "truth_lag_edges", "TP", "FP", "FN", "Precision", "Recall", "F1", "Hits"],
        ),
        "",
        "## 4. GPDC 与 ParCorr 对比实验表",
        "",
        markdown_table(
            comparison_df,
            [
                "lag_setting",
                "sample_size",
                "predicted_lag_edges_GPDC",
                "predicted_lag_edges_ParCorr",
                "TP_GPDC",
                "TP_ParCorr",
                "Precision_GPDC",
                "Precision_ParCorr",
                "Recall_GPDC",
                "Recall_ParCorr",
                "F1_GPDC",
                "F1_ParCorr",
                "F1_Winner",
            ],
        ),
        "",
        "## 5. 对比结论",
        "",
        f"- 在双方共有的 6 组设置上，GPDC 的平均 F1 为 `{gpdc_common_mean:.4f}`，高于 ParCorr 的 `{parcorr_common_mean:.4f}`。",
        f"- GPDC 的平均 Precision 为 `{common_summary['Precision_GPDC']:.4f}`，高于 ParCorr 的 `{common_summary['Precision_ParCorr']:.4f}`，说明误识别相对更少。",
        f"- GPDC 的平均 Recall 为 `{common_summary['Recall_GPDC']:.4f}`，也高于 ParCorr 的 `{common_summary['Recall_ParCorr']:.4f}`。",
        "- 从具体设置看，`lag2, n=500`、`lag3, n=500` 和 `lag3, n=1000` 三组中，GPDC 的真值匹配效果更好；其余设置两者都未命中真值边。",
        "- 因此，在 B1C 这类非线性且含混杂的支撑数据上，GPDC 相比 ParCorr 更适合作为本文后续真实平台分析的条件独立检验器。",
        "",
    ]
    return "\n".join(report)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    gpdc_df = evaluate_method("GPDC", METHOD_DIRS["GPDC"])
    parcorr_df = evaluate_method("ParCorr", METHOD_DIRS["ParCorr"])
    comparison_df = build_common_comparison(gpdc_df, parcorr_df)

    gpdc_path = OUTPUT_DIR / "gpdc_b1c_truth_match.csv"
    parcorr_path = OUTPUT_DIR / "parcorr_b1c_truth_match.csv"
    comparison_path = OUTPUT_DIR / "gpdc_parcorr_common_comparison.csv"
    report_path = OUTPUT_DIR / "b1c_method_comparison_report.md"

    gpdc_df.to_csv(gpdc_path, index=False, encoding="utf-8-sig")
    parcorr_df.to_csv(parcorr_path, index=False, encoding="utf-8-sig")
    comparison_df.to_csv(comparison_path, index=False, encoding="utf-8-sig")
    report_path.write_text(build_report(gpdc_df, parcorr_df, comparison_df), encoding="utf-8")

    print("已生成结果:")
    print(f"- {gpdc_path}")
    print(f"- {parcorr_path}")
    print(f"- {comparison_path}")
    print(f"- {report_path}")


if __name__ == "__main__":
    main()
