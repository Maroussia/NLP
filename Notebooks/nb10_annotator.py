"""
Philosophical Concept Annotator (BIO tagging)
==============================================
Reads token-per-line TSV/TXT files from a folder, annotates philosophical
concepts with B-CONCEPT / I-CONCEPT tags (longest match first), and writes
annotated copies to the same folder with 'A' appended to the filename.

Usage:
    python nb10_annotator.py --input_dir ./data/processed/annotations/

Optional flags:
    --ext           File extension to process (default: .txt)
    --case_sensitive  Enable case-sensitive matching (default: case-insensitive)

Expected TSV columns: doc_id, sentence_id, token_id, token, tag
"""

import argparse
import csv
import os
import sys
from pathlib import Path

# ─────────────────────────────────────────────
# 1.  CONCEPT DICTIONARY
# ─────────────────────────────────────────────
# Each entry is a tuple of tokens (lowercased for matching).
# Multi-word concepts MUST come before their sub-phrases — the list
# is sorted longest-first at runtime, so order here doesn't matter.

CONCEPTS = [
    # ── Metaphysics & Ontology ──
    "substance dualism",
    "property dualism",
    "modal realism",
    "personal identity",
    "possible world",
    "possible worlds",
    "thing in itself",
    "things in themselves",
    "free will",
    "substance",
    "essence",
    "existence",
    "being",
    "becoming",
    "phenomenon",
    "phenomena",
    "noumenon",
    "noumena",
    "determinism",
    "compatibilism",
    "causation",
    "causality",
    "universals",
    "particulars",
    "nominalism",
    "realism",
    "idealism",
    "materialism",
    "physicalism",
    "dualism",
    "monism",
    "pluralism",
    "panpsychism",
    "emergence",
    "supervenience",
    "essentialism",
    "potentiality",
    "actuality",

    # ── Epistemology ──
    "justified true belief",
    "a priori",
    "a posteriori",
    "epistemic justification",
    "epistemic virtue",
    "epistemic closure",
    "epistemic humility",
    "Gettier problem",
    "tabula rasa",
    "sense data",
    "innate ideas",
    "knowledge",
    "empiricism",
    "rationalism",
    "skepticism",
    "scepticism",
    "foundationalism",
    "coherentism",
    "reliabilism",
    "internalism",
    "externalism",
    "testimony",
    "perception",
    "intuition",
    "phenomenalism",
    "underdetermination",
    "fallibilism",

    # ── Logic & Philosophy of Language ──
    "logical positivism",
    "logical empiricism",
    "analytic statement",
    "synthetic statement",
    "analytic-synthetic distinction",
    "principle of verification",
    "truth conditions",
    "sense and reference",
    "definite description",
    "speech act",
    "performative utterance",
    "illocutionary act",
    "language game",
    "private language",
    "meaning holism",
    "radical interpretation",
    "rigid designator",
    "possible world semantics",
    "modal logic",
    "propositional logic",
    "predicate logic",
    "law of excluded middle",
    "law of non-contradiction",
    "modus ponens",
    "modus tollens",
    "reductio ad absurdum",
    "indeterminacy of translation",
    "principle of charity",
    "proposition",
    "predicate",
    "syllogism",
    "deduction",
    "induction",
    "abduction",
    "validity",
    "soundness",
    "compositionality",
    "paradox",

    # ── Ethics & Moral Philosophy ──
    "virtue ethics",
    "categorical imperative",
    "hypothetical imperative",
    "moral realism",
    "moral relativism",
    "moral anti-realism",
    "natural law",
    "social contract",
    "original position",
    "veil of ignorance",
    "reflective equilibrium",
    "trolley problem",
    "moral luck",
    "moral obligation",
    "moral responsibility",
    "moral sentimentalism",
    "care ethics",
    "distributive justice",
    "retributive justice",
    "restorative justice",
    "practical wisdom",
    "the good life",
    "greatest happiness principle",
    "hedonic calculus",
    "prima facie duty",
    "golden mean",
    "moral particularism",
    "deontology",
    "consequentialism",
    "utilitarianism",
    "emotivism",
    "expressivism",
    "prescriptivism",
    "supererogation",
    "autonomy",
    "dignity",
    "justice",
    "eudaimonia",
    "phronesis",
    "akrasia",

    # ── Political Philosophy ──
    "state of nature",
    "general will",
    "political obligation",
    "civil disobedience",
    "political authority",
    "negative liberty",
    "positive liberty",
    "public reason",
    "overlapping consensus",
    "false consciousness",
    "class struggle",
    "dialectical materialism",
    "historical materialism",
    "sovereignty",
    "legitimacy",
    "liberalism",
    "libertarianism",
    "communitarianism",
    "republicanism",
    "cosmopolitanism",
    "egalitarianism",
    "meritocracy",
    "democracy",
    "totalitarianism",
    "authoritarianism",
    "hegemony",
    "alienation",
    "ideology",

    # ── Philosophy of Mind ──
    "hard problem of consciousness",
    "the hard problem",
    "eliminative materialism",
    "multiple realizability",
    "mental causation",
    "folk psychology",
    "propositional attitude",
    "phenomenal consciousness",
    "access consciousness",
    "embodied cognition",
    "extended mind",
    "theory of mind",
    "other minds",
    "knowledge argument",
    "explanatory gap",
    "philosophical zombie",
    "Chinese room",
    "mental representation",
    "consciousness",
    "qualia",
    "intentionality",
    "functionalism",
    "behaviorism",
    "behaviourism",
    "identity theory",
    "epiphenomenalism",
    "enactivism",
    "self-consciousness",
    "belief",
    "desire",

    # ── Philosophy of Science ──
    "paradigm shift",
    "normal science",
    "scientific revolution",
    "research programme",
    "inference to the best explanation",
    "constructive empiricism",
    "scientific realism",
    "demarcation problem",
    "Bayesian confirmation",
    "hypothetico-deductive method",
    "thought experiment",
    "crucial experiment",
    "natural kind",
    "laws of nature",
    "Occam's razor",
    "falsifiability",
    "verifiability",
    "paradigm",
    "instrumentalism",
    "reductionism",
    "confirmation",
    "simplicity",
    "unification",

    # ── Aesthetics ──
    "the sublime",
    "the beautiful",
    "aesthetic judgment",
    "aesthetic experience",
    "aesthetic value",
    "artistic expression",
    "intentional fallacy",
    "institutional theory of art",
    "form and content",
    "aesthetic attitude",
    "disinterestedness",
    "mimesis",
    "catharsis",
    "taste",

    # ── Phenomenology & Existentialism ──
    "being-in-the-world",
    "existential angst",
    "bad faith",
    "radical freedom",
    "lived experience",
    "hermeneutic circle",
    "horizon of understanding",
    "phenomenology",
    "bracketing",
    "epoché",
    "lifeworld",
    "Dasein",
    "thrownness",
    "authenticity",
    "absurdity",
    "the absurd",
    "facticity",
    "intersubjectivity",
    "the Other",
    "transcendence",
    "immanence",

    # ── Continental & Critical Theory ──
    "thesis-antithesis-synthesis",
    "thesis–antithesis–synthesis",
    "archaeology of knowledge",
    "power/knowledge",
    "communicative action",
    "lifeworld colonization",
    "instrumental reason",
    "critical theory",
    "ideology critique",
    "commodity fetishism",
    "culture industry",
    "binary opposition",
    "deconstruction",
    "différance",
    "logocentrism",
    "genealogy",
    "discourse",
    "episteme",
    "biopower",
    "biopolitics",
    "governmentality",
    "panopticism",
    "dialectic",
    "dialectics",
    "sublation",
    "Aufhebung",
    "reification",
    "simulacrum",
    "hyperreality",
    "rhizome",
    "deterritorialization",
]


# ─────────────────────────────────────────────
# 2.  BUILD LOOKUP STRUCTURE
# ─────────────────────────────────────────────

def build_concept_trie(concepts: list[str]) -> dict:
    """
    Build a prefix-trie keyed on lowercased tokens.
    Each node is a dict; the key '__END__' marks a complete concept.
    This allows efficient longest-match-first lookup.
    """
    trie = {}
    for concept in concepts:
        tokens = concept.lower().split()
        node = trie
        for tok in tokens:
            node = node.setdefault(tok, {})
        node["__END__"] = True
    return trie


def longest_match(trie: dict, tokens: list[str], start: int,
                  case_sensitive: bool = False) -> int:
    """
    From position `start`, find the longest sequence of tokens
    that matches a concept in the trie. Returns the length of
    the match (0 if no match).
    """
    node = trie
    match_len = 0
    i = start
    while i < len(tokens):
        tok = tokens[i] if case_sensitive else tokens[i].lower()
        if tok in node:
            node = node[tok]
            if "__END__" in node:
                match_len = i - start + 1
            i += 1
        else:
            break
    return match_len


# ─────────────────────────────────────────────
# 3.  ANNOTATION LOGIC
# ─────────────────────────────────────────────

def annotate_sentence(rows: list[dict], trie: dict,
                      case_sensitive: bool = False) -> list[dict]:
    """
    Given the rows for a single sentence, apply BIO concept tagging.
    Modifies the 'tag' field in-place and returns the rows.
    """
    tokens = [r["token"] for r in rows]
    n = len(tokens)
    i = 0
    while i < n:
        m = longest_match(trie, tokens, i, case_sensitive)
        if m > 0:
            rows[i]["tag"] = "B-CONCEPT"
            for j in range(1, m):
                rows[i + j]["tag"] = "I-CONCEPT"
            i += m
        else:
            # keep original tag (O)
            i += 1
    return rows


# ─────────────────────────────────────────────
# 4.  FILE PROCESSING
# ─────────────────────────────────────────────

def process_file(filepath: Path, trie: dict,
                 case_sensitive: bool = False) -> Path:
    """
    Read a TSV annotation file, apply concept tagging sentence
    by sentence, and write the result to a new file with 'A'
    appended before the extension.
    """
    # Build output path: annotation_doc_1016.txt → annotation_doc_1016A.txt
    out_name = filepath.stem + "A" + filepath.suffix
    out_path = filepath.parent / out_name

    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        fieldnames = reader.fieldnames
        rows = list(reader)

    # Group rows by (doc_id, sentence_id)
    sentences: dict[tuple, list[dict]] = {}
    order = []  # preserve insertion order
    for row in rows:
        key = (row["doc_id"], row["sentence_id"])
        if key not in sentences:
            sentences[key] = []
            order.append(key)
        sentences[key].append(row)

    # Annotate each sentence
    annotated_rows = []
    for key in order:
        sent_rows = sentences[key]
        annotated_rows.extend(
            annotate_sentence(sent_rows, trie, case_sensitive)
        )

    # Write output
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(annotated_rows)

    return out_path


# ─────────────────────────────────────────────
# 5.  MAIN
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Annotate philosophical concepts with BIO tags."
    )
    parser.add_argument(
        "--input_dir", type=str, required=True,
        help="Folder containing annotation TSV/TXT files."
    )
    parser.add_argument(
        "--ext", type=str, default=".txt",
        help="File extension to process (default: .txt)."
    )
    parser.add_argument(
        "--case_sensitive", action="store_true",
        help="Match concepts case-sensitively (default: case-insensitive)."
    )
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    if not input_dir.is_dir():
        print(f"Error: {input_dir} is not a valid directory.", file=sys.stderr)
        sys.exit(1)

    # Build trie
    trie = build_concept_trie(CONCEPTS)
    print(f"Loaded {len(CONCEPTS)} concept patterns into trie.\n")

    # Find files (exclude already-annotated files ending in 'A')
    files = sorted([
        f for f in input_dir.glob(f"*{args.ext}")
        if not f.stem.endswith("A")
    ])

    if not files:
        print(f"No {args.ext} files found in {input_dir}.")
        sys.exit(0)

    print(f"Found {len(files)} file(s) to annotate.\n")

    total_concepts = 0
    for filepath in files:
        out_path = process_file(filepath, trie, args.case_sensitive)

        # Quick stats
        with open(out_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter="\t")
            b_count = sum(1 for row in reader if row["tag"] == "B-CONCEPT")

        total_concepts += b_count
        print(f"  {filepath.name}  →  {out_path.name}  "
              f"({b_count} concept(s) found)")

    print(f"\nDone. {total_concepts} concept mention(s) annotated "
          f"across {len(files)} file(s).")


if __name__ == "__main__":
    main()
