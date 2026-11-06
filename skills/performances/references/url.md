# URL Parsing

Removes URL parsing that does no work worth its cost, and keeps every parse that
validates or normalizes untrusted input.

## Authorized Scope

Loading this playbook grants no new authority.

## Contract

Inputs:

- Optional scope (modules)

Outputs:

- List of removed parses with measurements
- List of parses kept, with the reason

Creates/Modifies:

- Application code and tests on `perf/url`

External Side Effects:

- Push and PR

Confirmation Required:

- Before touching any parse near a redirect, fetch of a user-supplied address,
  allowlist, or auth flow

Delegates To:

- `/git pr` playbook when installed

## Detect

Language and idiom: `new URL`, `URL.parse`, `URL.canParse`, legacy `url.parse`,
`URLSearchParams` in JavaScript, `urlparse` in Python, `url.Parse` in Go,
`URI` and `URL` in Java, `Uri` in C#, `Url::parse` in Rust. Detect framework
request objects that already expose parsed parts (`req.nextUrl`, `req.path`,
`request.url`, `request.query_params`, `r.URL`). If the stack has no parsing
cost worth measuring, say so.

## Candidates

- Parsing only to read a part the framework already parsed
- Parsing a process-constant string on every call (hoist it, or use the string
  directly). Keep the parse at the read site when the configuration can reload or
  vary by tenant or request
- Parsing the same string several times in one request (parse once, pass the result)
- Parsing and immediately re-serializing with no change
- Joining a trusted base and a trusted path where concatenation is exact
- Parsing to test a prefix, suffix, or scheme of a trusted internal value

## Keep the parse when it

- Validates or normalizes untrusted input: redirect and callback targets, fetch
  or webhook targets (SSRF checks), host or origin allowlists, user-supplied
  links stored or rendered, OAuth redirect URIs
- Resolves relative references against anything user-influenced
- Relies on its thrown error for control flow
- Depends on normalization such as dot segments, percent-encoding, case, default
  ports, userinfo, or backslash handling, which string operations get wrong

When in doubt, keep it and list it. A parser and a string check differ on inputs
like `//host`, `\`, `@`, and mixed-case schemes.

## Measure

Count parses per request on the hot path with a counter or the profiler, and
time a microbenchmark of each removed site with realistic inputs over at least 20
samples. Use `compare.py`. If a parse is absent from profiles and cheap, remove it
only when the change is trivially safe, and say that is why.

## Tests

Characterization tests for each changed site, including odd inputs (empty,
relative, protocol-relative, unicode, trailing slash, query-only) that the old
code handled.

## PR

Include the removed and kept lists.
