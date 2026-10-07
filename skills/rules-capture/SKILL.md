---
name: rules-capture
description: Detects user preferences and workflow rules in conversation and records them in .agents/memory/captured-rules.md for promotion. Use on always/never or corrections to the AI.
metadata:
  version: "2.2.4"
  tags: "preferences, rules, documentation, automation"
when_to_use: "from now on, I prefer, stop doing X, the rule is"
---

# Rules Capture Skill

## Contract

Inputs:

- User statement that expresses a reusable rule, preference, standard, or correction
- Optional target scope: user, repo, project, skill, or session

Outputs:

- Captured pending rule with a redacted supporting quote, extracted rule, scope,
  and status
- Recommendation for permanent storage location

Creates/Modifies:

- Pending capture appended to `.agents/memory/captured-rules.md` (marked `status: temporary`)
- Permanent rules only after explicit confirmation
- Secret-like values are never written verbatim. Redact tokens, passwords, API
  keys, cookies, and private credentials before saving or echoing a capture.

External Side Effects:

- None

Confirmation Required:

- Before promoting a pending rule into permanent project or user rules
- Before editing shared/public skills based on the captured rule

Delegates To:

- `skill-capture` when the rule is a reusable workflow that should become a skill
- `agent-config-audit` when the rule may affect multiple config files

---

## When This Skill Activates

Automatically activate when the user mentions ANY of these:

### Direct Rule Expressions

- "always do X" / "never do X"
- "I prefer X" / "I don't like X"
- "don't ever X" / "stop doing X"
- "from now on X" / "going forward X"
- "that's not how we do it" / "we do it this way"
- "the rule is X" / "the standard is X"

### Coding Style Expressions

- "use X pattern" / "don't use X pattern"
- "name things like X" / "format like X"
- "import from X" / "don't import from X"
- "the convention is X"
- "follow the X pattern"

### Frustration Indicators (Capture these especially!)

- "why did you X" / "stop doing X"
- "I told you before" / "I already said"
- "that's wrong" / "that's not right"
- "fix this" / "change this"
- Any profanity + instruction (strong signal!)

### Questions About Standards

- "what's the rule for X" / "how should I X"
- "is it X or Y" / "which way is correct"
- "what's the coding style for X"

---

## Capture Process

When a rule/preference is detected:

### 1. Acknowledge Detection

```
I noticed you expressed a preference/rule. Let me capture this.
```

### 2. Extract Rule Details

Parse the user's statement to identify:

- **Category**: What area does this apply to? (coding, naming, imports, patterns, tools, communication)
- **Rule Type**: ALWAYS, NEVER, PREFER, AVOID
- **Specific Action**: What exactly should/shouldn't be done
- **Context**: When does this apply
- **Example**: Good vs bad example if mentioned

### 3. Document to Capture File

Append to `.agents/memory/captured-rules.md` (create the file if absent, with a YAML front-matter block including `status: temporary`):

````markdown
### [YYYY-MM-DD HH:MM] - [Category]: [Short Title]

**User said (redacted):**

> "[Short supporting quote with secrets replaced by [REDACTED_SECRET]]"

**Rule extracted:**

- **Type**: [ALWAYS | NEVER | PREFER | AVOID]
- **Action**: [What to do/not do]
- **Context**: [When this applies]
- **Category**: [coding | naming | imports | patterns | tools | communication | workflow]

**Example:**

```[language]
// Good
[good example]

// Bad
[bad example]
```
````

**Status**: PENDING_REVIEW

```

### 4. Confirm with User
```

Captured this rule:

- [Brief summary of the rule]

Should I add this to the permanent rules? [Yes/No/Modify]

````

### 5. On Confirmation
- **Personal preferences** → append to the user's platform-level instruction file under the appropriate section
- **Shared project coding standards** → append to the applicable `AGENTS.md`
- **Scoped project overrides** → use `AGENTS.override.md` only when inherited guidance must be replaced for a subtree
- **Claude-specific behavior** → append to `CLAUDE.md`
- **Durable project facts** (architecture, deployment notes, gotchas) → add/update a file in `.agents/memory/`
- Remove the entry from `.agents/memory/captured-rules.md` (or mark it PROCESSED)

---

## Escalate Before Documenting

A rule that repeats, or that an agent keeps breaking, belongs in structure, not prose. Before recording it as permanent text, check whether architecture, types, a lint that names the fix, or a behavior test can make the mistake impossible. Read [correct procedure](references/correct-procedure.md) for the ladder, the proof that each check fails on a real past mistake, and the rule-to-enforcer table. Record the rule as text only for judgment calls nothing can enforce.

---

## Rule Categories

### Coding Rules
- Pattern preferences
- Import conventions
- Naming conventions
- File structure
- Component patterns

### Workflow Rules
- Build/test preferences
- Git workflow
- Documentation requirements
- Communication style

### Tool Rules
- CLI preferences
- IDE settings
- Terminal behavior
- Background processes

### Communication Rules
- Response style
- Verbosity preferences
- Explanation depth
- Acknowledgment patterns

---

## Storage Locations

| Rule Type | Storage Location |
|-----------|------------------|
| Personal preferences | User-level platform instruction file |
| Project coding standards | Repo-level agent instruction file |
| Durable project facts | `.agents/memory/<topic>.md` |
| Pending review | `.agents/memory/captured-rules.md` (`status: temporary`) |

---

## Redaction Rules

Before writing or displaying a captured quote:

- Replace API keys, tokens, passwords, cookies, private URLs, and credentials
  with `[REDACTED_SECRET]`.
- Keep only the shortest quote needed to justify the rule. Summarize the rest.
- If the rule itself is about handling a secret, capture the policy, not the
  secret value.

## Auto-Capture File Format

File: `.agents/memory/captured-rules.md`

```markdown
---
status: temporary
last_verified: YYYY-MM-DD
---

# Captured Rules - Pending Review

Rules automatically captured from conversations. Review and promote to permanent storage.

---

## Pending Rules

[Auto-captured rules appear here]

---

## Processed Rules

[Rules that have been promoted to CLAUDE.md or .agents/memory/]
```

---

## Integration with Other Skills

This skill works with:

- **docs**: For formatting captured rules properly

---

## Cleanup Command

When user says "clean up rules" or "process captured rules":

1. Read `.agents/memory/captured-rules.md`
2. Present each pending rule for review
3. User can: Approve, Modify, Delete
4. Approved rules get promoted to CLAUDE.md or `.agents/memory/` as appropriate
5. File is cleaned up

---

## Example Interaction

**User**: "stop using console.log for debugging, use the logger service"

**Agent**:

```
I noticed a new rule. Let me capture it:

Rule: Use logger service instead of console.log for debugging
Category: Coding
Type: NEVER (console.log) / ALWAYS (logger service)

Added to captured rules. Should I promote this to permanent coding rules?
```

---

## Activation Triggers

The skill activates on these regex patterns:

```regex
# Direct commands
(always|never|don't|stop|from now on|going forward)\s+.+
(prefer|like|want|need)\s+(you to|it to|this to)\s+.+
(the rule is|the standard is|the convention is)\s+.+

# Frustration signals
(why (did|do) you|stop doing|I told you|I already said)\s+.+
(that's (wrong|not right|incorrect)|fix this|change this)\s+.+

# Questions about standards
(what's the (rule|standard|convention) for|how should I|which way is)\s+.+
```
