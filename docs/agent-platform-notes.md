# Agent platform notes

These notes come from loading CSE into one hosted agent platform. Behaviour differs between platforms. Verify each point on the platform you use.

## Loading the rules

- **Skill folder:** If the runtime supports skill folders with a SKILL.md file, use the `controlled-security-english/` directory unchanged.
- **Agent instructions:** Otherwise, paste SKILL.md sections 0–7 into the agent's always-applied instructions. Sections 0–7 are about 20,000 characters. Above the rules, add a short role statement that names CSE and the version.
- **Verify the saved text.** Rich-text instruction editors can convert Markdown. After saving and reloading, compare the letters of the saved text with the source. Code-fence language labels such as `text` can disappear when fences become code blocks; that is expected. Any other difference means truncation or corruption.
- **Knowledge retrieval is not equivalent to instructions.** If the rules live in a search index or knowledge source, the agent can receive only excerpts. Prefer always-loaded instructions.

## Least privilege

- Start with no tools, no web search, and no organization-wide knowledge.
- Restrict agent access to named users until testing is complete.
- If document tools are needed, add read tools first. Add write tools only for a stated need. Keep human approval enabled for every write.
- Do not add sharing or permission-change tools to a writing agent.
- A document connector can require each user to authorize their own account. An unauthenticated connector can cause the agent to report that no read tool exists. The agent's report is correct behaviour in that case. The fix is user authorization, not a configuration change.

## Reasoning modes and long output

Extended reasoning modes can exhaust the response budget before a long rewrite finishes. In testing, a full rewrite of a document of about 11,000 characters completed in standard mode. The same rewrite stopped early in extended mode, with no disclosure. If long documents matter, test the deployed mode. Otherwise, divide the work by section (A7).

## Checker execution

Uploading or quoting `cse_check.py` does not install an executable tool. If no connected tool runs the checker, the agent states the following text. "Manual CSE review only; the Python checker was not run." Do not let an agent simulate checker output.

## Tool reporting

When an agent can create files, approve one write at a time. Before you approve a second write for the same item, check whether the first write succeeded. Verify results in the document store, not only in the agent's reply (A6).
