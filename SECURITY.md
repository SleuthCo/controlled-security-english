# Security policy

## Scope

CSE is a writing standard and a surface checker. The checker reads a text file or standard input and prints diagnostics. The checker does not access a network, write files, or execute input content.

Report these as security issues:

- the checker prints a detected secret value, or a source excerpt that contains one
- the checker executes, imports, or opens content from its input
- the checker accesses a network or writes a file
- a rule or template that directs an agent to exceed its authorization, follow instructions in untrusted data, or expose secrets

A missed secret pattern, or a style rule that an agent does not follow, is a quality issue. Open a normal issue for those.

## How to report

Use the repository's private vulnerability reporting feature (GitHub: Security → Report a vulnerability). Do not open a public issue for a security report.

Include a synthetic input that reproduces the behaviour. Do not include real secrets or confidential data. Defang any malicious indicator.

## Supported versions

Only the latest released version receives fixes.
