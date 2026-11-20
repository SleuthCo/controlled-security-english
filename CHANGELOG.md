# Changelog

All notable changes to CSE. Versions follow MAJOR.MINOR.PATCH. A rule change that can change a compliant rewrite is at least a MINOR change after 1.0.

## 0.4.2 — 2026-11-19

### Added

- **G1:** Map every source sentence to a revised sentence or to a disclosed removal. Do not drop a qualification, negation, scope limit, or "not a claim of" statement. Do not copy wording from skill examples into a rewrite unless the source supports it.
- **W2:** Replace issue or problem with a security term only when the word names a defect. Otherwise write the plain meaning, such as the question or the concern.
- **W3:** Keep proposal status when removing a lowercase modal. Do not convert a proposal into a present-tense fact or into an uppercase requirement unless the source states a requirement.
- **L5:** Defang an indicator everywhere in delivered text, including `UNTRUSTED DATA` quotes, evidence-gap notes, and validation notes, and disclose the transformation.
- **A6 (new):** Report write tools from their results. Call each write tool at most once per request. Do not report a successful write as skipped. List cancelled or declined calls.
- **A7 (new):** Do not present partial output as complete. Name the last section completed and each section not returned.
- **Checker:** each bullet item is a separate paragraph for S8, as numbered steps already were. Before 0.4.2, a bulleted list counted as one paragraph and caused false S8 errors.
- **Checker:** L5 warning when an `UNTRUSTED DATA` label line, or the quote block after it, contains a raw URL scheme. The warning does not echo the URL.
- **Tests:** eight new regression tests: L5 detection, defanged and ordinary-link exclusions, region end, bullet paragraphs, version consistency, and absence of internal references. Total: 27.
- **Docs:** known model failure modes, acceptance prompts, and agent-platform notes.

### Changed

- Version 0.4.1-local.1 is renamed 0.4.2. Workspace-specific provenance, local paths, and message identifiers are removed from the published files.
- VALIDATION.md is rewritten as a portable validation record.

### Not tested

- The 0.4.2 rule additions were not re-run through the full agent acceptance set.

## 0.4.1 — 2026

- Reimplemented the surface checker with the Python standard library and added 19 regression tests.
- Added the sentence-to-source comparison in G1 and the instruction and data distinctions in section 5.
- See VALIDATION.md for the full list.

## 0.4.0

- Earlier draft of the rules, dictionary, templates, and embedded checker. Not published in this repository.
