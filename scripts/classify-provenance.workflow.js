export const meta = {
  name: 'classify-provenance',
  description: 'Classify each unclassified skill as external/internal-port/in-house, verifying any external upstream by fetching the real file before claiming it',
  phases: [
    { title: 'Classify', detail: 'one verifier agent per skill — fingerprint, search, fetch-verify' },
  ],
}

// Supply the canonical skill directory and an explicit selected name list from
// the current catalog. The harness owns discovery, model choice, and capacity.
if (typeof SKILLS_ROOT !== 'string' || !SKILLS_ROOT.trim() ||
    typeof SKILL_NAMES === 'undefined' || !Array.isArray(SKILL_NAMES) || !SKILL_NAMES.length ||
    SKILL_NAMES.some((name) => typeof name !== 'string' || !/^[a-z][a-z0-9-]*$/.test(name))) {
  throw new Error('Supply SKILLS_ROOT and a nonempty canonical SKILL_NAMES list.');
}
const SKILLS = [...new Set(SKILL_NAMES)]
const BASE = SKILLS_ROOT.replace(/\/$/, '')

const SCHEMA = {
  type: 'object',
  additionalProperties: false,
  properties: {
    skill: { type: 'string' },
    classification: { enum: ['external', 'internal-port', 'in-house', 'uncertain'] },
    upstream_repo: { type: 'string', description: 'owner/repo, or empty string if none' },
    upstream_path: { type: 'string', description: 'path to the upstream file within the repo, or empty' },
    upstream_url: { type: 'string', description: 'full https blob URL you actually fetched and verified, or empty' },
    license: { type: 'string', description: 'SPDX id of the upstream repo if known, else empty' },
    confidence: { enum: ['high', 'medium', 'low'] },
    verified: { type: 'boolean', description: 'true only if you fetched the upstream_url and its content clearly matches this skill' },
    evidence: { type: 'string', description: 'one or two sentences: what specifically matched or why in-house' },
  },
  required: ['skill', 'classification', 'upstream_repo', 'upstream_url', 'license', 'confidence', 'verified', 'evidence'],
}

const KNOWN = `Known upstream families in this marketplace (for reference — do NOT force-fit):
- pbakaus/impeccable (Apache-2.0): design-quality skills (audit, critique, polish, layout, quieter, shape, clarify).
- obra/superpowers (MIT): agent workflow skills (writing-plans, systematic-debugging, etc.).
- anthropics/skills (Apache-2.0): artifacts, mcp-builder, skill-creator, theme-factory.
- Dimillian/Skills (MIT): react-component-performance, plus swift/ios skills.
- snarktank/ai-dev-tasks: the classic create-prd / generate-tasks / process-task-list pattern — CHECK if 'prd-task-creator' derives from it.
- Internal ports require evidence supplied by the owner; do not infer a private source from similar names.`

phase('Classify')

const results = await parallel(SKILLS.map((skill) => () =>
  agent(
    `You are classifying the provenance of ONE Agent Skill in a vendored marketplace, so the owner can later check whether the original author shipped improvements worth porting back.

Skill: "${skill}"
Local file to read FIRST: ${BASE}/${skill}/SKILL.md  (also glance at ${BASE}/${skill}/README.md and ${BASE}/${skill}/references/ if present)

Your job: decide if this skill was IMPORTED from a public open-source upstream, ported from the owner's own private repo, or written in-house — and if external, VERIFY the upstream by actually fetching it.

Method:
1. Read the local SKILL.md. Note the exact skill name, the description, distinctive section headings, signature phrases, any embedded URLs/credits/license lines, and any tell-tale wording.
2. Decide whether this looks like a generic/original skill or a port. Most skills in this marketplace are the owner's OWN work (solo founder's GTM + engineering toolkit). DEFAULT to in-house.
3. If — and only if — the content smells imported, web-search for the origin: try the skill name + a distinctive verbatim phrase + "SKILL.md github", and the known families below.
4. If you find a candidate public file, you MUST fetch it (WebFetch the raw/blob URL) and confirm its content genuinely matches this skill (same name/structure, substantial verbatim or near-verbatim overlap). Only then set classification="external" and verified=true with the EXACT url you fetched.
5. If owner-supplied evidence establishes a private internal port with no public repo, use classification="internal-port", upstream_repo="", verified=false.
6. If you cannot verify a real matching upstream, DO NOT invent one. Use "in-house" (original) or "uncertain" (smells imported but unconfirmed), upstream_url="", verified=false.

${KNOWN}

HARD RULES:
- NEVER output an upstream_url you did not actually fetch and see matching content for. A fabricated or guessed URL is the worst possible outcome.
- "external" REQUIRES verified=true. If verified=false, classification must be in-house, internal-port, or uncertain.
- Be conservative. A same-name skill is NOT proof; the content must match.
- confidence: "high" only when verified=true OR you are certain it is original in-house work. Otherwise "medium"/"low".

Return the structured object for skill="${skill}".`,
    { label: skill, phase: 'Classify', schema: SCHEMA }
  )
))

return { results: results.filter(Boolean) }
