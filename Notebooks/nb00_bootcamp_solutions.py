from __future__ import annotations

SOLUTIONS = {
    "q1": """course_name = \"NLP Bootcamp\"""",
    "q2": """favorite_columns = [\"title\", \"language\", \"authors\"]""",
    "q3": """def count_missing(series):
    return int(series.isna().sum())""",
    "q4": """catalog_raw = pd.read_csv(bc.CATALOG_PATH)""",
    "q5": """catalog = bc.standardize_catalog(catalog_raw)""",
    "q6": """n_rows, n_cols = catalog.shape""",
    "q7": """short_table = catalog[[\"pg_id\", \"title\", \"language\"]].head(10)""",
    "q8": """english_books = catalog[catalog[\"language\"] == \"en\"]""",
    "q9": """top_languages = catalog[\"language\"].value_counts().head(10)""",
    "q10": """recent_catalog = catalog[catalog[\"issued_year\"] >= 2000]""",
    "q11": """from pathlib import Path

sample_path = Path(\"./analysis/tables/bootcamp_catalog_sample.csv\")
recent_catalog[[\"pg_id\", \"title\", \"language\", \"issued_year\"]].head(20).to_csv(
    sample_path,
    index=False
)""",
}

NOTES = {
    "q1": "This is a simple string assignment.",
    "q2": "This checks whether you are comfortable with Python list syntax.",
    "q3": "The key pandas idea is that `.isna()` marks missing values and `.sum()` counts them.",
    "q4": "Later notebooks will repeatedly use `pd.read_csv(...)` and explicit file paths.",
    "q5": "In the course, small helper functions often standardize or enrich metadata tables.",
    "q6": "Remember that dataframe shape is returned as `(rows, columns)`.",
    "q7": "Double brackets select multiple columns in pandas.",
    "q8": "Boolean filtering is one of the most important pandas operations in the course.",
    "q9": "Frequency counts are a basic descriptive tool you will use often in NLP workflows.",
    "q10": "This mirrors the kind of year-based filtering used later for time-bin analysis.",
    "q11": "Saving a small output file is important because the course emphasizes reusable artifacts.",
}


def show_solution(qid: str) -> None:
    """Print one solution and a short note."""
    if qid not in SOLUTIONS:
        raise KeyError(f"Unknown question id: {qid}")

    print(f"Solution for {qid}:")
    print("-" * 40)
    print(SOLUTIONS[qid])
    print("-" * 40)
    if qid in NOTES:
        print("Why this matters:", NOTES[qid])


def show_all() -> None:
    """Print all solutions in order."""
    for qid in sorted(SOLUTIONS):
        show_solution(qid)
        print()
