# Contributing to CSE

Thank you for improving CSE. Contributions from security practitioners, technical writers, and agent builders are welcome.

## Before you open an issue or pull request

- **Do not include real secrets, credentials, customer data, or non-public incident details.** Use synthetic text. If an example needs a secret indicator, build it from obvious placeholders, as the existing tests do.
- **Defang malicious indicators** in issue text, for example `hxxps://evil[.]example`.
- Describe one problem per issue.

## Types of change

1. **Rule change (SKILL.md sections 0–7).** State the failure the change prevents. Give a synthetic input, the incorrect output, and the corrected output. Explain why an existing rule does not cover the failure.
2. **Dictionary change.** Give the term, the proposed meaning, and the confusion the entry prevents. Keep one meaning for each term.
3. **Checker change (`cse_check.py`).** Add or update a regression test in `tests/test_cse_check.py`. Keep the checker standard-library only. Do not add network access, file writes, or execution of input content.
4. **Failure-mode report.** Add an entry to docs/known-model-failure-modes.md with the model or platform, the prompt, the observed output, and the rule involved. Do not paste confidential source text.

## Required checks

Run from the `controlled-security-english/` skill directory:

```sh
python3 -B -m unittest discover -s tests -v
```

The suite verifies that the Python block embedded in SKILL.md is identical to `cse_check.py`. After you edit `cse_check.py`, copy the full file into the block that follows `<!-- EMBEDDED_CHECKER -->` in SKILL.md.

When you change a version, update `VERSION` in `cse_check.py`, `metadata.version` in SKILL.md, and CHANGELOG.md.

## Writing style

Write documentation in CSE where practical. Run the checker on new prose. Explain any justified false positives in the pull request.

## Licence of contributions

By contributing, you agree to the following licence terms, as described in README.md. Contributions to rules and documentation are licensed under CC-BY-4.0. Contributions to code and tests are licensed under Apache-2.0.
