# Hoist Regex

Computes regexes once at module level instead of inside functions and loops,
without changing what they match.

## Authorized Scope

Follow `protocol.md`. Loading this playbook grants no new authority.

## Contract

Inputs:

- Optional scope (modules)

Outputs:

- List of hoisted patterns with measurements
- List of patterns left in place, with the reason

Creates/Modifies:

- Application code and tests on `perf/regex`

External Side Effects:

- Push and PR

Confirmation Required:

- None beyond `protocol.md`

Delegates To:

- `/git pr` playbook when installed

## Detect

The cost depends on the language, so profile before assuming. Examples: Go
`regexp.MustCompile` and Rust `Regex::new` inside functions compile on every
call and are expensive; Java `Pattern.compile`, `String.matches`, `replaceAll`,
and `split` recompile; Python's `re` caches compiled patterns, so the gain is
small; JavaScript regex literals allocate a new object on each evaluation while
the engine caches compiled code; C# static `Regex` methods cache, constructed
ones may not. Report the real expected gain for the detected language, and say
when it is negligible.

## Candidates

- Literal patterns inside functions, loops, callbacks, or request handlers
- Pattern constructors with constant strings inside the same places
- Constructors with interpolated parts drawn from a small fixed set

## Pitfalls to check at every site

- **Stateful flags.** In JavaScript, `g` and `y` give a regex `lastIndex` state
  used by `test` and `exec`. A shared one skips matches on the next call, and
  async code can interleave between uses. In a loop, a literal made fresh each
  iteration starts at zero and a hoisted one does not. Fixes: drop the flag when
  only one match is needed, use `matchAll` or `replace` (they reset state), or set
  `lastIndex = 0` before each use. Pick the one that keeps behavior identical.
- **Dynamic patterns.** Never hoist a pattern built from user input into an
  unbounded cache. Hoist only when the variable parts come from a fixed set, or
  memoize with a bounded cache keyed by the escaped input, and only when the same
  input recurs. Keep escaping exactly as it was.
- **Thread and task safety.** Go `Regexp` and Java `Pattern` are safe to share;
  Java `Matcher` is not, so hoist the pattern and create matchers per use.
- **Pattern and flags unchanged.** Do not rewrite the pattern. If hoisting
  exposes catastrophic backtracking, report it separately and do not fix it here.

## Fix

Move each pattern to a named module-level constant near its use, with the same
flags. Keep one definition when several functions use the same pattern.

## Measure

Microbenchmark each site, and the enclosing function, with realistic inputs over
at least 20 samples, and use `compare.py`. Prefer sites that appear in profiles
or run in loops. Report patterns whose gain is within noise.

## Tests

Characterization tests that call each function repeatedly and in different
orders, with inputs that match, do not match, and match twice, so state leaks
show up.

## PR

Follow `protocol.md`. Include the hoisted list with any flag handling and the
patterns left in place.
