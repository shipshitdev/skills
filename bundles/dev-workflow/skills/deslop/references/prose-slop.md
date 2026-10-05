# Prose slop catalog

Patterns that make writing read as machine-generated. Preserve meaning. Match
the intended tone. After the strip, add a human voice: opinions, varied
rhythm, specific facts, and the occasional first person.

Adapted from Lauren Tan's pstack `unslop` skill (MIT).

## Adding soul

Removing patterns is half the job. Sterile, voiceless writing is just as
obvious.

- Have opinions. React to facts instead of neutrally listing pros and cons.
- Vary rhythm. Short sentences. Then longer ones that take their time.
- Acknowledge complexity. "Impressive but also kind of unsettling" beats
  "impressive."
- Use "I" when it fits.
- Let some mess in. Perfect structure looks machine-made.
- Be specific. Not "this is concerning" but the concrete thing that happened.

## Content

- **1. Puffery.** "pivotal moment", "testament to", "evolving landscape",
   "setting the stage for", "indelible mark", "deeply rooted". Cut puffery,
   state what happened.
- **2. Name-dropping.** Listing media outlets without context. Pick one, say
   what was said.
- **3. Superficial -ing phrases.** "highlighting...", "ensuring...",
   "reflecting...", "showcasing...", "fostering...". Delete or expand with
   real sources.
- **4. Promotional language.** "nestled", "vibrant", "breathtaking",
   "groundbreaking", "renowned", "stunning", "must-visit". Use neutral
   descriptions.
- **5. Vague attributions.** "Experts believe", "Industry reports suggest",
   "Some critics argue". Name the source or delete.
- **6. Formulaic challenges.** "Despite challenges... continues to thrive."
   Replace with specific facts.

## Language

- **7. AI vocabulary.** Additionally, crucial, delve, enduring, enhance,
   fostering, garner, interplay, intricate, landscape (abstract), pivotal,
   showcase, tapestry (abstract), testament, underscore, vibrant. Replace
   with plain words.
- **8. Fancy ways to say "is".** "serves as", "stands as", "boasts",
   "features". Just say "is" or "has".
- **9. "Not just X, but Y."** State the point directly instead.
- **10. Rule of three.** Forcing ideas into groups of three. Use the natural
    number.
- **11. Synonym cycling.** Protagonist, main character, central figure, hero
    all in one paragraph. Pick one, repeat it.
- **12. False ranges.** "from X to Y" where X and Y aren't on a meaningful
    scale. List topics directly.

## Style

- **13. Em dash overuse.** Prefer periods or commas. If a thought needs
    separation, end the sentence.
- **14. Colon overuse.** Colons are fine before a list or example. Not as
    mid-sentence connectors.
- **15. Boldface overuse.** Don't bold every proper noun or acronym.
- **16. Inline-header lists.** The tell is a bold label and colon that restates
    the line: "**Performance:** Performance improved...". Convert those to
    prose. A bold lead-in that ends in a period, names the item, and is
    followed by genuinely new detail is fine.
- **17. Title case headings.** Use sentence case.
- **18. Decorative emojis.** Remove from headings and bullets.
- **19. Curly quotes.** Replace with straight quotes.

## Communication artifacts

- **20. Chatbot phrases.** "I hope this helps!", "Let me know if...",
    "Of course!", "Certainly!", "Found the smoking gun!" Remove.
- **21. Cutoff disclaimers.** "While specific details are limited..." Find
    sources or remove.
- **22. Sycophantic tone.** "Great question! You're absolutely right!" Respond
    directly.

## Filler

- **23. Filler phrases.** "In order to" becomes "To". "Due to the fact that"
    becomes "Because". "It is important to note that" gets deleted.
- **24. Excessive hedging.** "could potentially possibly be argued that it
    might" becomes "may".
- **25. Generic conclusions.** "The future looks bright." State specific plans
    or facts.

## Jargon

- **26. Vague metaphor nouns.** Flag substrate, wedge, vector, locus, vantage,
    nexus, surface, bedrock, modality, paradigm, primitive, harness, scaffolding,
    gold-plating, ratchet, evacuate,
    endgame, north star, and flywheel when
    used as vague metaphors without a concrete referent. Preserve established
    technical meanings, including API surface, embedding vector, attack vector,
    primitive types, and a test harness, when they precisely name the concept.
    Judge the sentence rather than substituting a banned-word list. For vague
    metaphors, "substrate" can become "base" and "wedge in" can become "add".
    "A vector for growth" can become "a way to increase paid signups" when that
    is the intended meaning. "Compare embedding vectors with cosine similarity"
    and "Reduce the public API surface to three methods" already name concrete
    technical operations. Keep them unless the surrounding explanation is unclear.

## Plain speech

- **27. Say what it does, not how it feels.** "the database stays close at
    hand" names a feeling. The fix names the mechanism or a number. If the
    sentence could appear unchanged in another project's docs, it says
    nothing about this one. Cut it.
- **28. Shorten or split dense sentences.** If the reader has to backtrack,
    break it in two. One idea per sentence.
- **29. Active voice.** Prefer it. Catch "is/are/was/were + past participle"
    and name the actor. Passive is fine only when the actor is unknown or
    genuinely doesn't matter.
- **30. Cut adverbs, or use a stronger verb.** "runs quickly" becomes "is
    fast" or the number. "significantly improves" becomes the measured
    delta.
- **31. Prefer the plain word.** "utilize" becomes "use", "leverage" becomes
    "use", "facilitate" becomes "help", "numerous" becomes "many", "in the
    event that" becomes "if".
- **32. Mannered prose.** Metaphor or flourish where a literal phrase
    exists: aphorisms ("wire it or delete it"), rhetorical fragments for
    effect, personified code ("the plan holds it"), figurative verbs ("rides
    along", "stands on"), stock framing phrases. "A dial worth turning"
    becomes "a parameter worth varying". Say what you mean. Rule 26 covers
    the metaphor nouns.
- **33. Over-compression.** Dropped articles, verbless fragments,
    symbol-speak, and abbreviations that make the reader decode instead of
    read. "Parser rejects bad date → exit 2, no write" becomes "The parser
    rejects a bad date, exits with code 2, and writes nothing." Write whole
    sentences with their articles and verbs, and spell out arrows and
    abbreviations.
