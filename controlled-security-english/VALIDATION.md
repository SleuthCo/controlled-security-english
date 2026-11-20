# Validation record

The validation record lists what was tested and what was not. The record does not claim accuracy, a false-positive rate, or conformance for any model or platform.

## Version history in brief

- **0.4.0:** earlier draft of the rules, dictionary, and an embedded checker. A byte-exact copy of the 0.4.0 package and its test suite was not available when 0.4.1 was prepared. Its checksum and its reported test count are not reproduced or claimed here.
- **0.4.1:** reimplemented the checker from the readable 0.4.0 rules and added local regression tests. Editorial changes are listed below.
- **0.4.2:** added rules and checker coverage from agent acceptance testing. See CHANGELOG.md in the repository.

## 0.4.1 editorial changes

- Add a precise skill trigger, scope boundary, supported command-line invocation, and operational limitations.
- Add a sentence-to-source comparison before delivery. Prevent expansion from ambiguous authentication or authorization wording to an invented endpoint or successful credential access.
- Replace an illustrative rewrite that added tenant scope, severity, versions, and deadlines with an example that preserves missing evidence.
- Clarify instruction hierarchy and bounded delegation.
- Distinguish attempted prompt injection from demonstrated success.
- Distinguish a public certificate from confidential credential secret material.
- Clarify unknown versus not performed. Require disclosure of transformations applied to delivered malicious excerpts.
- Return content-minimized diagnostics, including for secret indicators and input errors. The checker is not a complete secret scanner.

## Checker tests

Run from the skill directory:

```sh
python3 -B -m unittest discover -s tests -v
```

The suite covers:

- compliant and noncompliant fixtures
- quoted and fenced data, including mixed fence delimiters
- exact inline literals
- several secret indicators, with secret values omitted from diagnostics
- sentence, step, and paragraph limits
- state words versus passive voice
- month names and conditionals versus modals and hedges
- claim status capitalization
- command-line JSON output, strict warning exit, and unreadable input
- equality of the embedded checker and `cse_check.py`
- allowed standard-library imports only
- (0.4.2) L5 warnings for raw URLs in `UNTRUSTED DATA` excerpts, without echoing the URL
- (0.4.2) bullet items counted as separate paragraphs for S8
- (0.4.2) version consistency and absence of internal references in published files

A test run establishes checker behaviour on these inputs only.

## Agent acceptance testing (0.4.1 rules, one hosted agent platform)

A private, unpublished agent on one hosted agent platform used the 0.4.1 rules as its full instructions. A reviewer ran synthetic acceptance prompts in the platform preview. The reviewer compared each response with its source and did not use the model's self-assessment. The file `docs/acceptance-prompts.md` contains the prompts and pass criteria. The file `docs/known-model-failure-modes.md` lists the failures observed and the 0.4.2 rule written for each.

Observed summary:

- Most prompts passed on at least one run. Results varied between runs with near-identical instructions.
- The ambiguous-finding prompt (T1) passed once and failed once. The failing run added a demonstrated weakness and an attacker that the source did not support.
- Malicious indicators inside quoted untrusted excerpts were left undefanged until an explicit instruction was added.
- Wording from a rule example (cross-tenant) entered a rewrite whose source said accounts.
- Long strategy rewrites converted proposals into present-tense facts or uppercase requirements and dropped qualifying sentences.
- A long rewrite stopped before the end of the source without disclosure. The cutoff occurred with the platform's extended reasoning mode and not with its standard mode.
- With write tools enabled, the agent requested the same file creation three times and first reported a successful write as skipped.

The trials are smoke tests on synthetic prompts and one long strategy document. The trials are not an accuracy measurement and do not demonstrate reliable compliance. A model can fail to follow a valid skill. The surface checker cannot detect most meaning failures.

## Not tested

- No representative production corpus was evaluated.
- No false-positive or missed-violation rate was measured for the checker.
- No CI gate, automatic hook, or enforcement integration was evaluated.
- The 0.4.2 rule additions were not re-run through the full agent acceptance set after they were written.

Do not use a passing checker result as authorization, evidence, or a deployment decision.
