# Controlled Security English (CSE)

Controlled Security English is a controlled language for cybersecurity and AI-system writing: findings, advisories, incident reports, runbooks, threat models, control requirements, and agent handoffs. CSE is a set of writing rules, a dictionary, and templates, with a small surface checker. CSE is packaged as an agent skill. Human writers can use the same rules.

CSE takes its approach from controlled languages such as ASD-STE100 Simplified Technical English: a fixed set of writing rules plus a dictionary. **CSE is independent of STE100.** CSE does not use the STE100 specification or word list, does not claim STE100 compliance, and is not affiliated with or endorsed by ASD.

## What CSE does

- **Preserves meaning.** No invented scope, severity, actor, version, date, or test result. Ambiguity stays explicit until evidence resolves it.
- **Makes evidence visible.** Claim status (Confirmed, Probable, Possible, Refuted, Unknown) and evidence verbs (Observed, Reported, Inferred, Assumed) replace hedges.
- **Keeps literals exact.** Commands, paths, identifiers, and hashes stay unchanged. Secrets are redacted and malicious indicators are defanged in delivered copies.
- **Separates instruction from data.** Untrusted content is quoted as data, not restated as an instruction. A handoff proposes work and grants no permission.
- **Uses one term for one concept.** Security and AI dictionaries define finding, vulnerability, exposure, incident, prompt injection, and related terms.

## Repository layout

```text
controlled-security-english/     The skill: SKILL.md, cse_check.py, tests, VALIDATION.md
docs/known-model-failure-modes.md   Failures observed in agent testing, and the rule for each
docs/acceptance-prompts.md          Synthetic prompts and pass criteria for testing an agent
docs/agent-platform-notes.md        Notes for loading CSE into hosted agent platforms
```

## Quick start

Use the skill directory with an agent runtime that supports skill folders, or paste SKILL.md sections 0–7 into an agent's instructions.

Run the checker (Python 3 standard library only):

```sh
cd controlled-security-english
python3 -B cse_check.py /absolute/path/to/draft.md
python3 -B cse_check.py /absolute/path/to/draft.md --json
python3 -B -m unittest discover -s tests -v
```

## Example

Input:

> We recently found a critical auth issue in prod that could easily let a hacker grab creds.

A CSE rewrite keeps the ambiguity and the missing evidence:

```text
A finding concerns authentication or authorization in the production environment. The source does not establish which.
Severity: Not assessed. The source provides no assessment.
Discovery time: Unknown. The source says recently.
Credential exposure is Possible. No evidence of credential access is supplied.
```

The rewrite does not add an endpoint, an attacker, a CVSS score, or a patch.

## Limits

- The checker detects surface patterns only. A passing result does not establish factual accuracy, absence of secrets, authorization, full CSE conformance, or security approval.
- Most CSE failures are meaning failures, such as dropped qualifications or invented specifics. Only a reviewer who compares the output with its source can find them.
- Models do not follow every rule on every run. See docs/known-model-failure-modes.md.
- No accuracy or false-positive rate is claimed. See VALIDATION.md.

## Licence

- Rules, dictionary, templates, and documentation: Creative Commons Attribution 4.0 International (`CC-BY-4.0`). See LICENSE-docs.
- `cse_check.py` and the tests: Apache License 2.0 (`Apache-2.0`). See LICENSE.

See NOTICE for attribution and provenance.

## Contributing

See CONTRIBUTING.md. Do not submit real secrets, customer data, or non-public incident details in issues, fixtures, or examples.
