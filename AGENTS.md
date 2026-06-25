# AGENTS.md

## Project workflow

- This is a Quarto textbook project. Reader-facing content lives in `index.qmd`, `chapters/*.qmd`, and `appendices/*.qmd`.
- Before finishing any content update, run a de-AI pass on every touched reader-facing file. Use the `humanizer` standard: remove formulaic transitions, over-bolded emphasis, em/en dash padding, generic upbeat conclusions, and mechanical "key insight" phrasing; then read exposed paragraphs for natural Chinese sentence flow.
- Keep generated files out of content-only commits unless the user explicitly asks to update build artifacts. This includes rendered HTML, TeX, logs, caches, and test bytecode.
- Before committing content edits, run `git diff --check` and the existing test suite with the project root on `PYTHONPATH`.
