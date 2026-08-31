# Natural Language Processing for the Humanities

A hands-on NLP course that uses a corpus of philosophical texts to teach computational text analysis, from corpus construction to semantic shift detection.

---

## What this repository contains

This repository hosts all materials for a 15-session graduate course in Natural Language Processing designed for third-year BA Humanities students. It contains:

- **Jupyter notebooks** (one per session) which are the primary learning objects, combining code, explanation, and exercises.
 from [Project Gutenberg](https://www.gutenberg.org/) and the analysis.
- **Helper scripts** for annotation, evaluation, and data processing.
- **Empty folders** to store the notebooks outputs.

Everything is designed to run locally with Python and JupyterLab, or on a cloud compute instance.

---

## Course overview

This course introduces Humanities students to Natural Language Processing by applying it to a concrete research problem: **How do philosophical ideas emerge, spread, and change over more than two millennia?**

The corpus is drawn from Project Gutenberg and spans roughly 400 BCE to the mid-20th century. Rather than treating the history of philosophy as a fixed sequence of texts and authors, the course models it as a **dynamic semantic network**: a map of concepts, the communities of thought that shape them, and the trajectories along which they are adopted, transformed, or abandoned over time. Philosophy's exceptionally long timespan and its dense web of recurring, contested terms make it a distinctive case for studying how ideas move, merge, and change.

Students learn NLP not as an abstract toolkit, but as a way of **finding answers to real research questions** about their corpus.

---

## Research questions

The corpus and the course are organised around a set of guiding questions:

- **Emergence.** When and how do core philosophical concepts (e.g. *substance*, *will*, *consciousness*) first stabilise into recognisable, recurrent terms — and what distinguishes concepts that take hold from those that don't?
- **Semantic drift.** How does the meaning of a persistent term (e.g. *nature*, *reason*, *freedom*) shift across two and a half millennia, and can these shifts be linked to identifiable intellectual ruptures or transitions between periods and schools?
- **Terminological survival vs. conceptual persistence.** Are there concepts that survive terminologically but undergo substantial semantic drift, versus concepts where the term itself falls out of use while the underlying idea persists under a new name?
- **Bridging concepts.** Which concepts function as "bridges" connecting otherwise distinct communities of philosophical thought, and what happens to a concept's meaning when it crosses such a bridge?
- **Historical impact.** Can we assess the impact of historical events on the life cycle of philosophical concepts?
- **Method and limits.** To what extent can unsupervised methods (topic modelling, embedding-based shift detection) recover a defensible history of philosophical ideas without supervision from existing historiography — and where do they fail or mislead?

---

## Course structure

The syllabus builds progressively from foundational techniques to more independent research:

| Part | Sessions | Focus |
|---|---|---|
| **I — Corpus building and analysis** | 0–4 | NLP as research practice; building and curating the corpus; Pre-processing, exploratory analysis, lexical diversity, TF–IDF |
| **II — Linguistic Annotation** | 5–6 | spaCy pipelines, conceptual relations, Named Entity Recognition |
| **III — Representations for Modelling** | 7–8 | Count vectors, TF–IDF features, word embeddings |
| **IV — Models and interpretation** | 9–12 | Text classification, custom NER for domain-specific entities; Topic modelling, semantic shift detection 

Each session has a corresponding Jupyter notebook. Earlier notebooks produce outputs (processed corpora, annotation tables, trained models) that later notebooks consume — the sequence forms a coherent research pipeline.

---

## Learning philosophy

Students learn NLP by using it to ask real questions of a real corpus: which philosophical concepts recur, how they cluster into communities of ideas, and how their meaning and prominence shift across millennia of authorship. Individual notebooks, submitted progressively after each part of the course, build technical competence step by step.

---

## Requirements

- Python 3.10+ (3.11 recommended)
- JupyterLab
- Core libraries: `spacy`, `scikit-learn`, `pandas`, `numpy`, `matplotlib`
- Additional dependencies are installed per-notebook as needed

## Setup

Most dependencies are installed automatically in each notebook via `!pip install`.
If you prefer to install everything at once:

_with conda_

    conda env create -f environment-conda.yml
    conda activate nlp

_with conda and pip_

    conda env create -f environment-pip.yml
    conda activate nlp

---

## Licence

This project is licensed under the [GNU Affero General Public License v3.0](LICENSE). The course materials are shared for educational purposes. The philosophical texts in the corpus are sourced from [Project Gutenberg](https://www.gutenberg.org/) and are in the public domain. They are not stored with the course materials, but they can be extracted with notebook 01b.
