"""
Inter-Annotator Agreement (IAA) — Token-Level Comparison
=========================================================
Compares BIO-tagged annotation files produced by two different annotators.

Each annotator's files live in a separate folder. The script:
  1. Loads all annotated .txt files from both folders.
  2. Matches files across folders by document ID (extracted from filename).
  3. Computes per-document and overall token-level agreement.
  4. Prints a summary table and highlights disagreements for inspection.

Usage (command line):
    python nb10_inter_annotator_agreement.py --folder_a /path/to/student_A --folder_b /path/to/student_B

Usage (notebook):
    from nb10_inter_annotator_agreement import compare_annotations

    results = compare_annotations("/path/to/student_A", "/path/to/student_B")

    or:

    summary = compare_annotations(
                folder_a="/path/to/student_A",
                folder_b="/path/to/student_B",
                ext=".tsv",
)

Expected TSV columns: doc_id, sentence_id, token_id, token, tag
"""

import argparse
import os
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd


# ─────────────────────────────────────────────
# 1.  FILE LOADING
# ─────────────────────────────────────────────

def _extract_doc_key(filename_stem: str) -> str:
    """
    Extract a canonical document ID from a filename stem.

    Handles several common naming patterns:
      - annotation_doc_1016A  →  annotation_doc_1016
      - annotation_doc_1016   →  annotation_doc_1016
      - doc_1016_annotated    →  doc_1016_annotated

    The function strips a single trailing 'A' (case-sensitive) that the
    annotate_concepts.py script appends, so that both the original and
    annotated versions of a file resolve to the same key.
    """
    key = filename_stem
    # Strip a trailing 'A' added by the annotation script
    if key.endswith("A"):
        key = key[:-1]
    return key


def load_annotations(folder: str, ext: str = ".txt") -> dict[str, pd.DataFrame]:
    """
    Load all annotation files from *folder* and return a dict
    keyed by document ID → DataFrame.

    The document ID is extracted from the filename by stripping the extension
    and any trailing 'A' (so both 'annotation_doc_1016A.txt' and
    'annotation_doc_1016.txt' resolve to the same ID).
    """
    folder = Path(folder)
    if not folder.is_dir():
        raise FileNotFoundError(f"Folder not found: {folder}")

    annotations: dict[str, pd.DataFrame] = {}
    skipped = []

    for fpath in sorted(folder.glob(f"*{ext}")):
        doc_key = _extract_doc_key(fpath.stem)

        df = pd.read_csv(
            fpath,
            sep="\t",
            quoting=3,           # QUOTE_NONE — avoid issues with quotes in tokens
            dtype=str,
            keep_default_na=False,
        )
        # Normalise column names (lowercase, stripped)
        df.columns = [c.strip().lower() for c in df.columns]

        required = {"doc_id", "sentence_id", "token_id", "token", "tag"}
        if not required.issubset(df.columns):
            skipped.append((fpath.name, required - set(df.columns)))
            continue

        annotations[doc_key] = df

    if skipped:
        for name, missing in skipped:
            print(f"  ⚠  Skipping {name}: missing columns {missing}")

    return annotations


# ─────────────────────────────────────────────
# 2.  AGREEMENT METRICS
# ─────────────────────────────────────────────

def token_level_agreement(df_a: pd.DataFrame, df_b: pd.DataFrame) -> dict:
    """
    Compute token-level agreement between two BIO annotation DataFrames
    for a single document. Returns a dict with:
      - total:      number of aligned tokens
      - agree:      number of tokens where tags match
      - disagree:   number of tokens where tags differ
      - accuracy:   proportion of matching tags (agree / total)
      - disagreements:  DataFrame of mismatched rows (for inspection)
    """
    merged = df_a.merge(
        df_b,
        on=["doc_id", "sentence_id", "token_id", "token"],
        suffixes=("_a", "_b"),
    )

    if len(merged) == 0:
        return {
            "total": 0,
            "agree": 0,
            "disagree": 0,
            "accuracy": np.nan,
            "disagreements": pd.DataFrame(),
        }

    match = merged["tag_a"] == merged["tag_b"]

    return {
        "total": len(merged),
        "agree": int(match.sum()),
        "disagree": int((~match).sum()),
        "accuracy": float(match.mean()),
        "disagreements": merged.loc[
            ~match, ["doc_id", "sentence_id", "token_id", "token", "tag_a", "tag_b"]
        ].reset_index(drop=True),
    }


def concept_level_agreement(df_a: pd.DataFrame, df_b: pd.DataFrame) -> dict:
    """
    Compute agreement restricted to tokens where at least one annotator
    assigned a concept tag (B-CONCEPT or I-CONCEPT). This focuses the
    comparison on the interesting cases and ignores bulk 'O' agreement.
    """
    merged = df_a.merge(
        df_b,
        on=["doc_id", "sentence_id", "token_id", "token"],
        suffixes=("_a", "_b"),
    )

    if len(merged) == 0:
        return {"total": 0, "agree": 0, "disagree": 0, "accuracy": np.nan}

    # Keep only rows where at least one annotator tagged a concept
    concept_mask = (merged["tag_a"] != "O") | (merged["tag_b"] != "O")
    concept_rows = merged[concept_mask]

    if len(concept_rows) == 0:
        return {"total": 0, "agree": 0, "disagree": 0, "accuracy": np.nan}

    match = concept_rows["tag_a"] == concept_rows["tag_b"]

    return {
        "total": len(concept_rows),
        "agree": int(match.sum()),
        "disagree": int((~match).sum()),
        "accuracy": float(match.mean()),
    }


# ─────────────────────────────────────────────
# 3.  MAIN COMPARISON PIPELINE
# ─────────────────────────────────────────────

def compare_annotations(
    folder_a: str,
    folder_b: str,
    ext: str = ".txt",
    show_disagreements: int = 20,
    label_a: str = "Annotator A",
    label_b: str = "Annotator B",
) -> pd.DataFrame:
    """
    Full comparison pipeline:
      1. Load files from both folders.
      2. Match by document ID.
      3. Compute per-document and overall agreement.
      4. Print a summary table and sample disagreements.
      5. Return the summary DataFrame.

    Parameters
    ----------
    folder_a, folder_b : str or Path
        Paths to each annotator's folder.
    ext : str
        File extension to look for (default '.txt').
    show_disagreements : int
        Max disagreement rows to display per document (0 = skip).
    label_a, label_b : str
        Human-readable names for the two annotators (used in output).

    Returns
    -------
    pd.DataFrame
        Per-document summary with columns: doc_id, tokens, token_agree,
        token_accuracy, concept_tokens, concept_agree, concept_accuracy.
    """
    print(f"Loading {label_a} files from: {folder_a}")
    annots_a = load_annotations(folder_a, ext)
    print(f"  → {len(annots_a)} document(s) loaded")
    if annots_a:
        print(f"    Keys: {', '.join(sorted(annots_a.keys()))}")
    print()

    print(f"Loading {label_b} files from: {folder_b}")
    annots_b = load_annotations(folder_b, ext)
    print(f"  → {len(annots_b)} document(s) loaded")
    if annots_b:
        print(f"    Keys: {', '.join(sorted(annots_b.keys()))}")
    print()

    # ── Diagnostics if no files loaded ──
    if not annots_a and not annots_b:
        print(f"❌ No {ext} files found in either folder.")
        print(f"   Check that both folders contain annotation files with the '{ext}' extension.")
        return pd.DataFrame()
    elif not annots_a:
        print(f"❌ No {ext} files found in {label_a}'s folder: {folder_a}")
        return pd.DataFrame()
    elif not annots_b:
        print(f"❌ No {ext} files found in {label_b}'s folder: {folder_b}")
        return pd.DataFrame()

    # Find common documents
    common_ids = sorted(set(annots_a.keys()) & set(annots_b.keys()))
    only_a = set(annots_a.keys()) - set(annots_b.keys())
    only_b = set(annots_b.keys()) - set(annots_a.keys())

    if only_a:
        print(f"  ⚠  Documents only in {label_a} ({len(only_a)}): {', '.join(sorted(only_a))}")
    if only_b:
        print(f"  ⚠  Documents only in {label_b} ({len(only_b)}): {', '.join(sorted(only_b))}")

    if not common_ids:
        print("\n❌ No matching documents found between the two folders.")
        print("   The document keys extracted from filenames did not overlap.")
        print()
        print("   Debugging info:")
        print(f"     {label_a} keys: {sorted(annots_a.keys())}")
        print(f"     {label_b} keys: {sorted(annots_b.keys())}")
        print()
        print("   Common causes:")
        print("     • One folder has original files (doc_1016.txt) and the")
        print("       other has annotated files (doc_1016A.txt) with a")
        print("       different naming convention.")
        print("     • Files in the two folders refer to different documents.")
        print("     • Unexpected characters in filenames.")
        return pd.DataFrame()

    print(f"\n✓ {len(common_ids)} document(s) matched for comparison.\n")
    print("=" * 80)

    # Per-document comparison
    rows = []
    all_disagreements = []

    for doc_id in common_ids:
        tok = token_level_agreement(annots_a[doc_id], annots_b[doc_id])
        con = concept_level_agreement(annots_a[doc_id], annots_b[doc_id])

        rows.append({
            "doc_id": doc_id,
            "tokens": tok["total"],
            "token_agree": tok["agree"],
            "token_accuracy": tok["accuracy"],
            "concept_tokens": con["total"],
            "concept_agree": con["agree"],
            "concept_accuracy": con["accuracy"],
        })

        if not tok["disagreements"].empty:
            all_disagreements.append(tok["disagreements"])

    summary = pd.DataFrame(rows)

    # ── Print per-document table ──
    print(f"\n{'Document':<35} {'Tokens':>7} {'Agree':>7} {'Acc %':>7}  │ {'Concept':>8} {'Agree':>7} {'Acc %':>7}")
    print("─" * 35 + " " + "─" * 23 + "─┼─" + "─" * 25)

    for _, r in summary.iterrows():
        tok_pct = f"{r['token_accuracy']*100:.1f}" if not np.isnan(r["token_accuracy"]) else "  n/a"
        con_pct = f"{r['concept_accuracy']*100:.1f}" if not np.isnan(r["concept_accuracy"]) else "  n/a"
        print(
            f"{r['doc_id']:<35} {r['tokens']:>7} {r['token_agree']:>7} {tok_pct:>7}  │ "
            f"{r['concept_tokens']:>8} {r['concept_agree']:>7} {con_pct:>7}"
        )

    # ── Overall aggregates ──
    total_tok = summary["tokens"].sum()
    total_agree = summary["token_agree"].sum()
    total_con = summary["concept_tokens"].sum()
    total_con_agree = summary["concept_agree"].sum()

    overall_tok_acc = total_agree / total_tok if total_tok > 0 else np.nan
    overall_con_acc = total_con_agree / total_con if total_con > 0 else np.nan

    print("─" * 35 + " " + "─" * 23 + "─┼─" + "─" * 25)
    tok_pct = f"{overall_tok_acc*100:.1f}" if not np.isnan(overall_tok_acc) else "  n/a"
    con_pct = f"{overall_con_acc*100:.1f}" if not np.isnan(overall_con_acc) else "  n/a"
    print(
        f"{'OVERALL':<35} {total_tok:>7} {total_agree:>7} {tok_pct:>7}  │ "
        f"{total_con:>8} {total_con_agree:>7} {con_pct:>7}"
    )
    print()

    # ── Sample disagreements ──
    if show_disagreements > 0 and all_disagreements:
        disagreements = pd.concat(all_disagreements, ignore_index=True)
        n = min(show_disagreements, len(disagreements))
        print(f"Sample disagreements ({n} of {len(disagreements)} total):")
        print("─" * 80)
        print(
            disagreements.head(n).to_string(
                index=False,
                columns=["doc_id", "sentence_id", "token_id", "token", "tag_a", "tag_b"],
                header=["doc_id", "sent", "tok", "token", label_a, label_b],
            )
        )
        print()

    return summary


# ─────────────────────────────────────────────
# 4.  CLI ENTRY POINT
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Compare BIO annotations from two annotators (folder-based).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python inter_annotator_agreement.py \\
      --folder_a ./student_alice/ --folder_b ./student_bob/

  python inter_annotator_agreement.py \\
      --folder_a ./my_annotations/ --folder_b ./partner_annotations/ \\
      --label_a "Me" --label_b "Partner" --show_disagreements 50
        """,
    )
    parser.add_argument("--folder_a", required=True, help="Path to first annotator's folder")
    parser.add_argument("--folder_b", required=True, help="Path to second annotator's folder")
    parser.add_argument("--ext", default=".txt", help="File extension (default: .txt)")
    parser.add_argument("--label_a", default="Annotator A", help="Label for first annotator")
    parser.add_argument("--label_b", default="Annotator B", help="Label for second annotator")
    parser.add_argument("--show_disagreements", type=int, default=20,
                        help="Max disagreement rows to show (0 = hide)")

    args = parser.parse_args()

    compare_annotations(
        folder_a=args.folder_a,
        folder_b=args.folder_b,
        ext=args.ext,
        show_disagreements=args.show_disagreements,
        label_a=args.label_a,
        label_b=args.label_b,
    )


if __name__ == "__main__":
    main()
