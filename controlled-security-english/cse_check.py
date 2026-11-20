#!/usr/bin/env python3
"""CSE surface checker, version 0.4.2 (Python standard library).

Check prose, not truth, authorization, scope, template completeness or compliance.
Usage: python3 cse_check.py FILE [--json] [--strict]; FILE '-' reads stdin.
Exit codes: 0=no errors (and no warnings in strict mode), 1=findings, 2=input error.
Diagnostics never intentionally echo detected secret values. Detection is incomplete.
"""
import argparse
import json
import re
import sys
from pathlib import Path

VERSION = "0.4.2"

# These are indicators, not a complete secret scanner. Scan excluded Markdown too.
SECRET_PATTERNS = (
    r"\bAKIA[0-9A-Z]{16}\b",
    r"-----BEGIN (?:[A-Z]+ )*PRIVATE KEY-----",
    r"\bgh[posu]_[A-Za-z0-9]{36,}\b",
    r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b",
    r"\bsk-[A-Za-z0-9_-]{20,}\b",
    r"\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]+\b",
    r"(?i)\bbearer[ \t]+[A-Za-z0-9._~+/=-]{16,}",
    r"(?i)\b(?:password|passwd|secret|api[_-]?key|token)\b[ \t]*[:=][ \t]*"
    r"[\"']?(?!\[REDACTED:|\$\{|<)[A-Za-z0-9_./+~=-]{8,}",
)
SECRETS = tuple(re.compile(p) for p in SECRET_PATTERNS)

# rule, expression, replacement advice; terms are matched only in prose.
WORD_RULES = (
    ("W2", r"secure[ds]?|securely|securing|safe|safely|robust|strong|weak", "Name the measurable property or control."),
    ("W2", r"issues?|problems?", "Name the finding, vulnerability, weakness, exposure, failure or error."),
    ("W2", r"leverag(?:e|es|ed|ing)|utiliz(?:e|es|ed|ing)", "Use 'use'."),
    ("W2", r"handl(?:e|es|ed|ing)|deal(?:s|t)? with|manag(?:e|es|ed|ing)|address(?:es|ed|ing)?", "Name the exact action and target."),
    ("W2", r"harden(?:s|ed|ing)?|lock(?:s|ed)? down|sanitiz\w+", "Name the exact transformation or configuration change."),
    ("W2", r"ensur(?:e|es|ed|ing)|make sure|mak(?:es|ing) sure", "Give the action and a verification step."),
    ("W2", r"hackers?|bad actors?|adversar(?:y|ies)|malicious users?", "Use attacker only when attack evidence supports it."),
    ("W2", r"whitelist\w*|blacklist\w*", "Use allowlist or denylist in authored prose; preserve literal identifiers."),
    ("W2", r"hallucinat\w+", "Distinguish unsupported claim, false claim and fabricated evidence."),
    ("W2", r"sophisticated|advanced|cutting-edge|state-of-the-art|seamless(?:ly)?", "Delete or state the supporting fact."),
    ("W2", r"very|extremely|highly|significant(?:ly)?|severe(?:ly)?|serious(?:ly)?", "Give a supported rating, quantity or effect."),
    ("W2", r"simply|just|obviously|clearly|easily|easy|trivial(?:ly)?", "State the necessary access and steps."),
    ("W2", r"appropriate(?:ly)?|proper(?:ly)?|adequate(?:ly)?|sufficient(?:ly)?|reasonable|relevant", "State the criterion."),
    ("W2", r"as needed|as necessary|if applicable|where possible|as soon as possible|ASAP", "State the condition or deadline."),
    ("W2", r"regularly|periodically|frequently|often|sometimes|occasionally", "State the interval or count."),
    ("W2", r"best practices?", "Name the control or standard identifier."),
    ("W2", r"etc\.?|e\.g\.|i\.e\.|and/or", "Use a full list, 'for example', 'that is', or 'A or B or both'."),
    ("W2", r"auth|creds|vulns?|prod|infra|perms|config", "Use the full unambiguous term in prose."),
    ("W5", r"might|could|perhaps|maybe|seems?|seemed|appears?|appeared|apparently|possibly|potentially|potential|presumably|likely|unlikely|probably|believed|suspected", "Give claim status and evidence; preserve conditions and uncertainty."),
    ("L3", r"recently|soon|currently|yesterday|today|tomorrow|tonight|last (?:week|month|night|year)|next (?:week|month|year)|at the moment|nowadays", "Use a supported absolute UTC time, date, or explicit duration."),
    ("A3", r"\b(?:the )?model\s+(?:thinks?|wants?|knows?|decides? to deceive)\b", "Describe model output rather than human mental properties."),
)
COMPILED_WORD_RULES = tuple((rule, re.compile(r"(?<!\w)(?:" + expr + r")(?!\w)", re.I), msg)
                            for rule, expr, msg in WORD_RULES)
# L5: a raw URL scheme inside an UNTRUSTED DATA excerpt is probably an undefanged indicator.
RAW_URL = re.compile(r'(?i)\b(?:https?|ftp)://')
STATE_WORDS = set("authenticated unauthenticated authorized unauthorized encrypted unencrypted enabled disabled exposed affected required allowed denied blocked confirmed signed unsigned trusted untrusted patched unpatched compromised isolated redacted defanged completed failed installed connected located related supported limited expired revoked configured misconfigured refuted".split())
KNOWN = set("API URL URI IP DNS TLS SSH HTTP HTTPS TCP UDP CVE CWE CVSS CPE ID UTC MUST NOT SHOULD MAY OS CPU GPU JSON YAML SQL HTML XML MFA SSO IAM VPN LLM AI ML MCP RAG SIEM EDR DLP MDM PII TLP IOC CSE WARNING CAUTION NOTE DONE PARTIAL FAILED BLOCKED APPROVAL REQUIRED UNTRUSTED DATA CLI SDK JWT SAML RBAC AWS GCP PDF KMS HSM PKI XSS CSRF SSRF RCE NIST MITRE OWASP ISO RFC SOC AES RSA SHA VM LAN SMTP LDAP RDP SMB ATLAS STATUS TASK ACTIONS RESULT EVIDENCE NEXT NONE AUTHORITY IT ERROR WARN TRUE FALSE NULL GET POST PUT DELETE".split())


def secret_spans(text):
    spans = []
    for pattern in SECRETS:
        spans.extend((m.start(), m.end()) for m in pattern.finditer(text))
    merged = []
    for start, end in sorted(spans):
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(end, merged[-1][1]))
        else:
            merged.append((start, end))
    return merged


def prose_lines(text):
    """Yield (source line, text, kind). Markdown parsing is deliberately heuristic."""
    fence = None
    frontmatter = False
    quote = False
    for number, raw in enumerate(text.splitlines(), 1):
        stripped = raw.strip()
        if number == 1 and stripped == '---':
            frontmatter = True
            continue
        if frontmatter:
            if stripped in ('---', '...'):
                frontmatter = False
            continue
        marker = re.match(r'^\s*(?:>\s*)?(`{3,}|~{3,})(.*)$', raw)
        if marker:
            token, tail = marker.groups()
            if fence is None:
                fence = (token[0], len(token))
            elif token[0] == fence[0] and len(token) >= fence[1] and not tail.strip():
                fence = None
            continue
        if fence:
            continue
        if not stripped:
            quote = False
            yield number, '', 'blank'
            continue
        if re.match(r'^\s*>', raw):
            quote = True
            continue
        # Skip lazy quote continuation until a blank line or a new Markdown block.
        if quote and not re.match(r'^\s*(?:#{1,6}\s|[-+*]\s|\d+[.)]\s)', raw):
            continue
        quote = False
        if raw.startswith('    ') or raw.startswith('\t'):
            continue
        if re.match(r'^\s*(?:\|?\s*:?-{3,}:?\s*)+\|?\s*$', raw):
            continue
        if re.match(r'^\s*\d+[.)]\s+', raw):
            kind = 'step'
        elif re.match(r'^\s*[-+*]\s+', raw):
            kind = 'item'  # each bullet is its own paragraph for S8
        else:
            kind = 'prose'
        if re.match(r'^\s*#{1,6}\s+', raw):
            kind = 'heading'
        cleaned = re.sub(r'^\s*(?:#{1,6}\s+|\d+[.)]\s+|[-+*]\s+)', '', raw)
        # Keep link labels but do not rewrite or interpret their destinations.
        cleaned = re.sub(r'!?\[([^\]]+)\]\([^\s)]*(?:\s+"[^"]*")?\)', r'\1', cleaned)
        cleaned = re.sub(r'<(?:https?://|mailto:)[^>]+>', ' ', cleaned)
        cleaned = re.sub(r'(?<!\w)https?://\S+', ' ', cleaned)
        yield number, cleaned, kind


def untrusted_lines(text):
    """Yield (line, text) for an UNTRUSTED DATA label line and the quote block after it."""
    active = False
    for number, raw in enumerate(text.splitlines(), 1):
        if 'UNTRUSTED DATA' in raw:
            active = True
            yield number, raw
            continue
        if active and (not raw.strip() or re.match(r'^\s*>', raw)):
            yield number, raw
            continue
        active = False


def mask_inline(text, replacement=' '):
    return re.sub(r'(`+)(.+?)\1', lambda m: replacement, text)


def check(text):
    """Return bounded, content-minimized diagnostics. Never change the input."""
    findings = []
    def add(line, rule, severity, message):
        findings.append({'line': line, 'rule': rule, 'severity': severity, 'message': message})
    for start, _ in secret_spans(text):
        add(text.count('\n', 0, start) + 1, 'L6', 'ERROR', 'Possible secret detected; redact before sharing. Value omitted.')
    # Redact before any other scanning, even though messages omit matched text.
    safe = text
    for start, end in reversed(secret_spans(text)):
        safe = safe[:start] + ' ' * (end - start) + safe[end:]
    for line, raw in untrusted_lines(safe):
        if RAW_URL.search(raw):
            add(line, 'L5', 'WARN', 'Defang the indicator in the untrusted excerpt, or label a required raw value defanged: false. Value omitted.')
    paragraph = []
    paragraph_line = 1
    defined = set(KNOWN)
    def flush():
        if len(paragraph) > 6:
            add(paragraph_line, 'S8', 'ERROR', 'Paragraph exceeds six detected sentences; divide by topic.')
        paragraph.clear()
    for line, content, kind in prose_lines(safe):
        if not content or kind == 'heading':
            flush()
            if not content:
                continue
        lexical = mask_inline(content)
        lexical = re.sub(r'\bSecure Boot\b', ' ', lexical)
        for rule, pattern, message in COMPILED_WORD_RULES:
            candidate = re.sub(r'\b(?:Confirmed|Probable|Possible|Refuted|Unknown)\b', ' ', lexical) if rule == 'W5' else lexical
            if pattern.search(candidate):
                add(line, rule, 'ERROR', message)
        if re.search(r"\b\w+(?:n't|'(?:re|ve|ll|d|m))\b|\b(?:it|that|there|what|who|here)'s\b", lexical, re.I):
            add(line, 'W8', 'ERROR', 'Expand the contraction.')
        for match in re.finditer(r'\b(?:should|must|may|shall)\b', lexical):
            # A capitalized month is not a modal; only lowercase modals match.
            add(line, 'W3', 'ERROR', 'Use an uppercase requirement keyword, an imperative, or ability wording.')
            break
        severity_prose = re.sub(r'\bSeverity:\s*(?:Critical|High|Medium|Low|None)\s*\([^)]*\)', '', lexical)
        if re.search(r'\b(?:critical|high|medium|low)\b', severity_prose, re.I):
            add(line, 'W4', 'WARN', 'Review severity wording; state a supported rating with scale, or use a non-rating term.')
        for match in re.finditer(r'\b[A-Z][A-Z0-9]{1,}\b', lexical):
            token = match.group()
            if re.search(r'\(' + re.escape(token) + r'\)', lexical[:match.end()+1]):
                defined.add(token)
            if token not in defined:
                add(line, 'S9', 'WARN', 'Define an unfamiliar acronym on first use; review manually.')
                defined.add(token)
        if kind == 'heading':
            continue
        counted = mask_inline(content, 'LITERAL')
        counted = re.sub(r'[*_#|]', ' ', counted)
        # Keep dotted identifiers and decimal values together.
        sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+(?=[A-Z0-9"\[])', counted) if s.strip()]
        if kind in ('step', 'item'):
            flush()
        for sentence in sentences:
            words = re.findall(r"\b[\w]+(?:[-'/][\w]+)*\b", sentence)
            maximum = 20 if kind == 'step' else 25
            if len(words) > maximum:
                add(line, 'S1', 'ERROR', f'Detected sentence has {len(words)} words; limit is {maximum}. Preserve qualifiers when dividing.')
            if re.match(r'^(?:This|That|It|They)\b', sentence):
                add(line, 'S5', 'ERROR', 'Name the noun instead of an ambiguous sentence-opening pronoun.')
            passive = re.search(r'\b(?:is|are|was|were|be|been|being)\s+(\w+(?:ed|en)|sent|run|taken|given|done|made|found|seen|known|kept|held|set|put|read|stolen|hidden|shown|left|lost|built)\b', sentence, re.I)
            if passive and passive.group(1).lower() not in STATE_WORDS:
                add(line, 'S3', 'WARN', 'Review possible passive voice and identify the actor if evidence supports it.')
            if not paragraph:
                paragraph_line = line
            paragraph.append(sentence)
        if kind in ('step', 'item') or content.lstrip().startswith('|'):
            flush()
    flush()
    return sorted(findings, key=lambda f: (f['line'], f['rule'], f['severity']))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('file', help="UTF-8 input path, or '-' for stdin")
    parser.add_argument('--json', action='store_true', help='Emit content-minimized JSON diagnostics')
    parser.add_argument('--strict', action='store_true', help='Fail on warnings as well as errors')
    args = parser.parse_args(argv)
    try:
        text = sys.stdin.read() if args.file == '-' else Path(args.file).read_text(encoding='utf-8')
    except (OSError, UnicodeError):
        if args.json:
            print(json.dumps({'status': 'input_error', 'message': 'Cannot read input as UTF-8; no content included.'}))
        else:
            print('Cannot read input as UTF-8; no content included.', file=sys.stderr)
        return 2
    findings = check(text)
    errors = sum(f['severity'] == 'ERROR' for f in findings)
    warnings = len(findings) - errors
    if args.json:
        print(json.dumps({'checker_version': VERSION, 'errors': errors, 'warnings': warnings, 'findings': findings}, indent=2))
    else:
        for f in findings:
            print(f"{f['line']}: {f['severity']} {f['rule']}: {f['message']}")
        print(f'CSE check: {errors} error(s), {warnings} warning(s). Surface checks only.')
    return int(bool(errors or (args.strict and warnings)))


if __name__ == '__main__':
    sys.exit(main())
