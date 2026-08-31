from __future__ import annotations

from pathlib import Path
import re
import pandas as pd

CATALOG_PATH = Path("./analysis/tables/pg_catalog.csv")

QUESTIONS = {
    "q1": "Q1. Create a string variable called `course_name` and set its value to `'NLP Bootcamp'`.",
    "q2": "Q2. Create a list called `favorite_columns` with exactly these three strings: `'title'`, `'language'`, `'authors'`.",
    "q3": "Q3. Write a function `count_missing(series)` that returns the number of missing values in a pandas Series as an integer.",
    "q4": "Q4. Load `./analysis/tables/pg_catalog.csv` into a dataframe called `catalog_raw`.",
    "q5": "Q5. Create a cleaned dataframe called `catalog` by running `bc.standardize_catalog(catalog_raw)`.",
    "q6": "Q6. Store the number of rows and columns of `catalog` in two variables called `n_rows` and `n_cols`.",
    "q7": "Q7. Create `short_table` containing only the columns `pg_id`, `title`, and `language`, and keep only the first 10 rows.",
    "q8": "Q8. Create `english_books` by filtering `catalog` to rows where `language == 'en'`.",
    "q9": "Q9. Create `top_languages` as the top 10 language counts from `catalog['language']` using `value_counts()`.",
    "q10": "Q10. Create `recent_catalog` by filtering `catalog` to rows where `issued_year >= 2000`.",
    "q11": "Q11. Save the first 20 rows of `recent_catalog[['pg_id', 'title', 'language', 'issued_year']]` to `./analysis/tables/nb00-bootcamp_catalog_sample.csv`."
}

HINTS = {
    "q1": "You need a plain Python string variable: `name = 'text'`.",
    "q2": "Use square brackets to build a list, for example `['a', 'b']`.",
    "q3": "A pandas Series has an `.isna()` method. You can sum the True values.",
    "q4": "Use `pd.read_csv(...)` with `bc.CATALOG_PATH`.",
    "q5": "The helper file already contains the cleaning function you need.",
    "q6": "A dataframe shape is available through `.shape` and returns `(rows, columns)`.",
    "q7": "Select columns with double brackets: `df[['col1', 'col2']]`.",
    "q8": "Boolean filtering looks like `df[df['column'] == value]`.",
    "q9": "Start from the `language` column and then call `.value_counts().head(10)`.",
    "q10": "Filter rows with a numeric condition on `issued_year`.",
    "q11": "Use `.to_csv(path, index=False)` after selecting the four requested columns and the first 20 rows."
}

REQUIRED_COLUMNS = ["pg_id", "title", "language", "authors", "subjects", "issued_year"]


def ask(qid: str) -> None:
    """Print one exercise prompt."""
    if qid not in QUESTIONS:
        raise KeyError(f"Unknown question id: {qid}")
    print(QUESTIONS[qid])


def show_hint(qid: str) -> None:
    """Print one hint."""
    if qid not in HINTS:
        raise KeyError(f"Unknown question id: {qid}")
    print(f"Hint for {qid}: {HINTS[qid]}")


def show_questions() -> None:
    """Print all prompts."""
    for qid in sorted(QUESTIONS):
        print(QUESTIONS[qid])


def _ok(message: str = "Correct.") -> None:
    print(f"✅ {message}")


def _fail(message: str) -> None:
    print(f"❌ {message}")


def _normalize_col(name: str) -> str:
    """Normalize a column name and map a few known catalog names to stable labels."""
    text = str(name).strip().lower()
    text = text.replace("#", "_number")
    text = re.sub(r"[^a-z0-9]+", "_", text).strip("_")
    rename_map = {
        "text_number": "pg_id",
        "text_no": "pg_id",
        "text_id": "pg_id",
        "gutenberg_id": "pg_id",
        "book_id": "pg_id",
        "issued": "issued",
        "title": "title",
        "language": "language",
        "authors": "authors",
        "author": "authors",
        "subjects": "subjects",
        "subject": "subjects",
        "type": "type",
        "bookshelves": "bookshelves",
        "locc": "locc",
    }
    return rename_map.get(text, text)


def standardize_catalog(df: pd.DataFrame) -> pd.DataFrame:
    """
    Return a lightly cleaned Project Gutenberg catalog dataframe.

    - normalizes column names
    - creates `issued_year` from the `issued` column when possible
    - lowercases the `language` column
    """
    out = df.copy()
    out.columns = [_normalize_col(c) for c in out.columns]

    if "language" in out.columns:
        lang = out["language"].astype("string").str.strip().str.lower()
        out["language"] = lang.mask(lang.isin(["", "nan", "none"]))

    if "pg_id" in out.columns:
        out["pg_id"] = pd.to_numeric(out["pg_id"], errors="coerce").astype("Int64")

    if "issued" in out.columns:
        issued_dt = pd.to_datetime(out["issued"], errors="coerce")
        out["issued_year"] = issued_dt.dt.year.astype("Int64")
    elif "issued_year" not in out.columns:
        out["issued_year"] = pd.Series([pd.NA] * len(out), dtype="Int64")

    return out


def load_catalog(path: Path | None = None) -> pd.DataFrame:
    """Load and standardize the course catalog."""
    catalog_path = path or CATALOG_PATH
    if not catalog_path.exists():
        raise FileNotFoundError(
            f"Could not find the course catalog at {catalog_path}. "
            "Make sure you run the notebook from the project root."
        )
    return standardize_catalog(pd.read_csv(catalog_path))


def check_q1(course_name) -> None:
    if isinstance(course_name, str) and course_name == "NLP Bootcamp":
        _ok("`course_name` is a correct string.")
    else:
        _fail("Create a string variable exactly equal to 'NLP Bootcamp'.")


def check_q2(favorite_columns) -> None:
    target = ["title", "language", "authors"]
    if isinstance(favorite_columns, list) and favorite_columns == target:
        _ok("`favorite_columns` is the right list.")
    else:
        _fail("Use a Python list with exactly ['title', 'language', 'authors'].")


def check_q3(func) -> None:
    if not callable(func):
        _fail("`count_missing` should be a function.")
        return

    test = pd.Series([1, None, 3, pd.NA, 5])
    try:
        result = func(test)
    except Exception as exc:
        _fail(f"Your function raised an error: {exc}")
        return

    if result == 2:
        _ok("Your function correctly counts missing values.")
    else:
        _fail("Your function should return the number of missing values as an integer.")


def check_q4(catalog_raw) -> None:
    if not isinstance(catalog_raw, pd.DataFrame):
        _fail("`catalog_raw` should be a pandas DataFrame.")
        return
    if catalog_raw.empty:
        _fail("The dataframe is empty. Check the file path or loading step.")
        return
    _ok(f"`catalog_raw` loaded successfully with shape {catalog_raw.shape}.")


def check_q5(catalog_raw, catalog) -> None:
    if not isinstance(catalog, pd.DataFrame):
        _fail("`catalog` should be a pandas DataFrame.")
        return
    if len(catalog) != len(catalog_raw):
        _fail("`catalog` should keep the same number of rows as `catalog_raw`.")
        return

    missing = [c for c in REQUIRED_COLUMNS if c not in catalog.columns]
    if missing:
        _fail(
            "Your cleaned dataframe is missing expected columns: "
            + ", ".join(missing)
            + ". Did you use `bc.standardize_catalog(catalog_raw)`?"
        )
        return

    _ok("`catalog` looks good and has the expected cleaned columns.")


def check_q6(catalog, n_rows, n_cols) -> None:
    expected_rows, expected_cols = catalog.shape
    if n_rows == expected_rows and n_cols == expected_cols:
        _ok("`n_rows` and `n_cols` match `catalog.shape`.")
    else:
        _fail(
            f"Expected ({expected_rows}, {expected_cols}), "
            f"but got ({n_rows}, {n_cols})."
        )


def check_q7(catalog, short_table) -> None:
    expected = catalog[["pg_id", "title", "language"]].head(10).reset_index(drop=True)
    if not isinstance(short_table, pd.DataFrame):
        _fail("`short_table` should be a DataFrame.")
        return

    actual = short_table.reset_index(drop=True)
    if list(actual.columns) != ["pg_id", "title", "language"]:
        _fail("Keep exactly these columns, in this order: pg_id, title, language.")
        return
    if len(actual) != 10:
        _fail("`short_table` should contain the first 10 rows only.")
        return
    if actual.equals(expected):
        _ok("`short_table` is correct.")
    else:
        _fail("The columns or rows do not match the requested selection.")


def check_q8(catalog, english_books) -> None:
    expected = catalog[catalog["language"] == "en"].reset_index(drop=True)
    if not isinstance(english_books, pd.DataFrame):
        _fail("`english_books` should be a DataFrame.")
        return

    actual = english_books.reset_index(drop=True)
    if actual.equals(expected):
        _ok(f"`english_books` is correct with {len(actual):,} rows.")
    else:
        _fail("Filter `catalog` to rows where `language == 'en'`.")


def check_q9(catalog, top_languages) -> None:
    expected = catalog["language"].value_counts().head(10)
    if not isinstance(top_languages, pd.Series):
        _fail("`top_languages` should be a pandas Series.")
        return

    actual = top_languages.copy()
    if actual.equals(expected):
        _ok("`top_languages` matches the expected top 10 counts.")
    else:
        _fail("Use `catalog['language'].value_counts().head(10)`.")


def check_q10(catalog, recent_catalog) -> None:
    expected = catalog[catalog["issued_year"] >= 2000].reset_index(drop=True)
    if not isinstance(recent_catalog, pd.DataFrame):
        _fail("`recent_catalog` should be a DataFrame.")
        return

    actual = recent_catalog.reset_index(drop=True)
    if actual.equals(expected):
        _ok(f"`recent_catalog` is correct with {len(actual):,} rows.")
    else:
        _fail("Filter `catalog` to rows where `issued_year >= 2000`.")
        

def check_q11(sample_path, recent_catalog) -> None:
    path = Path(sample_path)
    
    # 1. Check that the file exists
    if not path.exists():
        _fail(f"I could not find the saved file at {path}.")
        return

    # 2. Try reading the CSV
    try:
        saved = pd.read_csv(sample_path)
    except Exception as exc:
        _fail(f"The file exists but could not be read as CSV: {exc}")
        return

    # 3. Build the expected DataFrame
    expected = recent_catalog[["pg_id", "title", "language", "issued_year"]].head(20).reset_index(drop=True)

    # 4. Quick shape check (20 rows, 4 columns)
    if saved.shape != expected.shape:
        _fail(
            f"Shape mismatch: expected {expected.shape} (20 rows, 4 columns), "
            f"but got {saved.shape}."
        )
        return

    # 5. Quick column check (order matters)
    if saved.columns.tolist() != expected.columns.tolist():
        _fail(
            f"Column names mismatch: expected {expected.columns.tolist()}, "
            f"but got {saved.columns.tolist()}."
        )
        return

    # 6. Compare the actual data values, ignoring data types (dtypes)
    try:
        pd.testing.assert_frame_equal(
            expected, 
            saved, 
            check_dtype=False,        # Ignore Int64 vs int64, string vs str
            check_index_type=False,   
            check_column_type=False   # Column names are strings either way
        )
        _ok(f"The CSV was saved correctly to {path}.")
    except AssertionError as e:
        _fail(
            "The saved file does not match the requested first 20 rows and four columns.\n"
            f"Details from pandas comparison:\n{e}"
        )
