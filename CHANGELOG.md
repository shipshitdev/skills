# Changelog

## [2.2.3](https://github.com/shipshitdev/skills/compare/v2.2.2...v2.2.3) (2026-10-06)


### ⚠ BREAKING CHANGES

* advanced-evaluation, context-degradation, codebase-advisor and agent-browser are removed and no longer install through `npx skills add --skill <name>`; use evaluation, context-optimization and codebase-design.
* rename the grilling primitive to grill-me ([#211](https://github.com/shipshitdev/skills/issues/211))
* drop MongoDB/Mongoose skills and standardize on Prisma/Postgres and Vitest ([#208](https://github.com/shipshitdev/skills/issues/208))
* biome-validator, bun-validator, clerk-validator, nextjs-validator and tailwind-validator are removed; use stack-validator.
* **skills:** grill-me, refactor-dispatch, changelog-generator, github-address-comments, typescript-refactor, spec-first and fullstack-workspace-init are removed.
* grill-me, refactor-dispatch, changelog-generator, github-address-comments, typescript-refactor, spec-first and fullstack-workspace-init are removed.
* **commands:** the deploy skill and plugin are renamed deploy-app.
* systematic-debugging, execution-debugging, context-fundamentals, and ai-regression-testing are removed.
* release-pr-gates and release-dispatch are removed; use release.

### Features

* add grill-me alias for grilling ([#174](https://github.com/shipshitdev/skills/issues/174)) ([d97c8be](https://github.com/shipshitdev/skills/commit/d97c8beb285385f8a658a52de60c6c315c52a2ae)), closes [#172](https://github.com/shipshitdev/skills/issues/172)
* **commands:** add picker frontmatter and a standard help mode ([#170](https://github.com/shipshitdev/skills/issues/170)) ([4a5dbf3](https://github.com/shipshitdev/skills/commit/4a5dbf3bf9c591e90177cfaf69211d345c1f3c60))
* **executing-plans:** slim executor brief and deterministic plan-header check ([#156](https://github.com/shipshitdev/skills/issues/156)) ([a0f9899](https://github.com/shipshitdev/skills/commit/a0f9899c4254e9c000a390c00fbe5e11a52530bb))
* **pstack-sync:** declare ignored repo-only upstream paths ([#191](https://github.com/shipshitdev/skills/issues/191)) ([01d63a5](https://github.com/shipshitdev/skills/commit/01d63a5e93904060375e34d3778613a4f3f1707e))
* **pstack:** adopt open-pstack runner reliability bundle ([#200](https://github.com/shipshitdev/skills/issues/200)) ([86da8a6](https://github.com/shipshitdev/skills/commit/86da8a6b1dc4222a180d15c7f9a4aca8f6d4b3a6))
* **pstack:** sync upstream 0.15.x content and advance pinned sources ([#198](https://github.com/shipshitdev/skills/issues/198)) ([3dc4588](https://github.com/shipshitdev/skills/commit/3dc4588e92e8b4092824b405c659f86af3b620b7))
* **pstack:** weekly upstream drift check workflow ([#209](https://github.com/shipshitdev/skills/issues/209)) ([f49aa5f](https://github.com/shipshitdev/skills/commit/f49aa5f9f340a8286bcaaf62341ec26e79343985))
* **retro:** add session retrospective and fold pstack reflect into it ([#187](https://github.com/shipshitdev/skills/issues/187)) ([b0cc749](https://github.com/shipshitdev/skills/commit/b0cc749dbdfcb5e3e33a447e4586823f9e7c69b7))
* **skills:** add wayfinder, research, triage mode and interview send mode ([#199](https://github.com/shipshitdev/skills/issues/199)) ([cbd8bf3](https://github.com/shipshitdev/skills/commit/cbd8bf3f038f5e6d3f0d3554b77697265b685d1b))
* **skills:** fold Pocock duplicates into the catalog and unify the PR body template ([#193](https://github.com/shipshitdev/skills/issues/193)) ([2c49ff7](https://github.com/shipshitdev/skills/commit/2c49ff72962427f7753733cc945b34ece8fbdadd))
* **skills:** hide internal engines from the slash menu ([#173](https://github.com/shipshitdev/skills/issues/173)) ([1b6f248](https://github.com/shipshitdev/skills/commit/1b6f248cbc3f0321737e6e91fec78b0e542575e8))
* **skills:** port Pocock debug, routing and glossary upgrades ([#196](https://github.com/shipshitdev/skills/issues/196)) ([da8dcb7](https://github.com/shipshitdev/skills/commit/da8dcb7425d1924f1a565cfb65be8d25a5d1d9f2))
* **standup:** add all-author recap and merged-history audit ([#161](https://github.com/shipshitdev/skills/issues/161)) ([bea4c5d](https://github.com/shipshitdev/skills/commit/bea4c5db6948230ea673087df1893d65606da528))
* **upstream-drift:** one weekly drift check and aggregate issue for every upstream ([#227](https://github.com/shipshitdev/skills/issues/227)) ([332e092](https://github.com/shipshitdev/skills/commit/332e0927fae0cd189d82deb88416f2daf34fa704))


### Bug Fixes

* **artifacts-builder:** close the CSS injection, snapshot before inlining, and resync the CSS tokenizer ([#260](https://github.com/shipshitdev/skills/issues/260)) ([52221a6](https://github.com/shipshitdev/skills/commit/52221a6d190ccd3c803255d4a5729135c3f9a0df))
* **artifacts-builder:** decode HTML character references in inliner attribute values ([#250](https://github.com/shipshitdev/skills/issues/250)) ([bf54798](https://github.com/shipshitdev/skills/commit/bf5479842ab57d1f7db32e3578a4699e386e0767))
* **artifacts-builder:** guard existing destinations, preserve bundles, inline public assets, strict Node check ([#241](https://github.com/shipshitdev/skills/issues/241)) ([45fd2c7](https://github.com/shipshitdev/skills/commit/45fd2c7288a32ad27318d9d6b371c608445cd648)), closes [#239](https://github.com/shipshitdev/skills/issues/239)
* **artifacts-builder:** harden the asset inliner against symlink escapes and malformed HTML ([#245](https://github.com/shipshitdev/skills/issues/245)) ([53c794a](https://github.com/shipshitdev/skills/commit/53c794a2b69a73214d752f5e1c5f9d4726888ba5)), closes [#243](https://github.com/shipshitdev/skills/issues/243)
* **artifacts-builder:** harden the inliner with a CSS tokenizer, srcset descriptors, DOM-faithful output and file confinement ([#253](https://github.com/shipshitdev/skills/issues/253)) ([a0df314](https://github.com/shipshitdev/skills/commit/a0df314cab0733877f721ba05d2f5ffc0208856c))
* **commands:** route every command to a skill the model can load ([#177](https://github.com/shipshitdev/skills/issues/177)) ([7b2afbb](https://github.com/shipshitdev/skills/commit/7b2afbb8a24ae7378a0472cc3adcbc1093a321f0))
* **executing-plans:** run helper CLIs when invoked through a symlinked install ([#220](https://github.com/shipshitdev/skills/issues/220)) ([6f15d8b](https://github.com/shipshitdev/skills/commit/6f15d8b596a39f20ad19a73cdfc20e1b66c84d56)), closes [#218](https://github.com/shipshitdev/skills/issues/218)
* **git-cleanup:** align merged-head guidance and proof receipts ([#264](https://github.com/shipshitdev/skills/issues/264)) ([90f4131](https://github.com/shipshitdev/skills/commit/90f41312850800800febacb3fd5ea16d25cdefa5))
* **git-cleanup:** audit ancestor deletions that trunk restored ([#182](https://github.com/shipshitdev/skills/issues/182)) ([597ed96](https://github.com/shipshitdev/skills/commit/597ed961c22881404ce771beeefff5cde0daf5f4))
* **git-cleanup:** catch directory links inside the removed worktree in duplicate chains ([#221](https://github.com/shipshitdev/skills/issues/221)) ([796f27f](https://github.com/shipshitdev/skills/commit/796f27f5e5c738506d7dee54a2fff07937538ebb))
* **git-cleanup:** clear merged worktrees that real cleanup runs still kept ([#194](https://github.com/shipshitdev/skills/issues/194)) ([7a6ea0e](https://github.com/shipshitdev/skills/commit/7a6ea0e3b9b5db0fb4a637e0983b17223a14f8bb))
* **git-cleanup:** clear Studio test checkouts without manual handling ([#206](https://github.com/shipshitdev/skills/issues/206)) ([72b2935](https://github.com/shipshitdev/skills/commit/72b29350ebfa52b597cb1f517d5b811242f006a6))
* **git-cleanup:** remove merged exact PR heads that trunk later edited ([#186](https://github.com/shipshitdev/skills/issues/186)) ([8ccce1e](https://github.com/shipshitdev/skills/commit/8ccce1edbb52aa7898a225c10fa6e14454bb933b))
* **git-cleanup:** remove pointer branches, copied ignored files and worktree branches in one pass ([#184](https://github.com/shipshitdev/skills/issues/184)) ([dc8e38a](https://github.com/shipshitdev/skills/commit/dc8e38a68a80ed453bbff6fb1f25681ea0341e87))
* **git-cleanup:** resolve symlink targets in duplicate check; report supersession triage ([#217](https://github.com/shipshitdev/skills/issues/217)) ([ecfbd25](https://github.com/shipshitdev/skills/commit/ecfbd25e20feaa48921dc6c48e4a7dcd2166fd60))
* **git-cleanup:** treat an unfetched PR merge commit as missing evidence ([#159](https://github.com/shipshitdev/skills/issues/159)) ([c019c54](https://github.com/shipshitdev/skills/commit/c019c5482d6a19ffb111c04ea1d474b44f7f579e))
* **git-cleanup:** verify current trunk code and intent before deletion ([#163](https://github.com/shipshitdev/skills/issues/163)) ([9f80997](https://github.com/shipshitdev/skills/commit/9f809973bb0f5f773cfad25feb5b40a4048bfb60))
* **micro-landing-builder:** AA defaults, AA-safe text, template and CSV theme support ([#254](https://github.com/shipshitdev/skills/issues/254)) ([30cf8be](https://github.com/shipshitdev/skills/commit/30cf8be13935afcbbf3fab42e2a0c20c2e9c15b6))
* **micro-landing-builder:** confine slugs, pair theme foreground with background, unique input ids ([#246](https://github.com/shipshitdev/skills/issues/246)) ([5391e62](https://github.com/shipshitdev/skills/commit/5391e6222908d8c5150d18ea8c0e0e0f4a47e8e6))
* **micro-landing-builder:** infer theme mode from background brightness ([#249](https://github.com/shipshitdev/skills/issues/249)) ([15f6c18](https://github.com/shipshitdev/skills/commit/15f6c1874fcbf9fbb7241431865f34326a6229c6))
* **micro-landing-builder:** opaque hover, AA link text, robust batch input ([#259](https://github.com/shipshitdev/skills/issues/259)) ([85f0a59](https://github.com/shipshitdev/skills/commit/85f0a5915ff42962d81fab42dac2fa64ba6b33eb))
* **micro-landing-builder:** pick theme foregrounds by WCAG contrast and validate theme colors ([#252](https://github.com/shipshitdev/skills/issues/252)) ([c031873](https://github.com/shipshitdev/skills/commit/c031873bebf6456b68b1f5e44ba152f45e859ba6))
* **micro-landing-builder:** validate complete themes and rendered states ([#263](https://github.com/shipshitdev/skills/issues/263)) ([f75f53b](https://github.com/shipshitdev/skills/commit/f75f53b54de5ae4ced63186c9e15f7bcdaaf3760))
* **planning:** package executing-plans with the planning bundle ([#213](https://github.com/shipshitdev/skills/issues/213)) ([bd1b0e3](https://github.com/shipshitdev/skills/commit/bd1b0e30b565c76e60448eb5942592ff5d511ba4))
* **project-init-orchestrator:** accept several frontend origins and verify the API image in CI ([#229](https://github.com/shipshitdev/skills/issues/229)) ([ee3b80e](https://github.com/shipshitdev/skills/commit/ee3b80e5f5154db8d7a637d99a38fe08eff80d66))
* **project-init-orchestrator:** reject wildcard origins and inspect the builder stage in CI ([#233](https://github.com/shipshitdev/skills/issues/233)) ([7af8af8](https://github.com/shipshitdev/skills/commit/7af8af86f621a794981d7827041731883bb29b37))
* **project-init-orchestrator:** secure generated collections and Docker image, fix auth/session and setup bugs ([#228](https://github.com/shipshitdev/skills/issues/228)) ([709f7ab](https://github.com/shipshitdev/skills/commit/709f7abfdcc4828c3c1152a70eefb39a2e163b0f))
* **pstack-drift:** handle truncated compares, renames, governance token and issue lookup ([#215](https://github.com/shipshitdev/skills/issues/215)) ([dd3a6d4](https://github.com/shipshitdev/skills/commit/dd3a6d4d697c1c0578502044db4111ccfe9363d5))
* **pstack-drift:** scope truncated fallback by pin..head ancestry ([#219](https://github.com/shipshitdev/skills/issues/219)) ([52008e1](https://github.com/shipshitdev/skills/commit/52008e17847560c1cddf3c5aa2eaf90474ff951f))
* **release:** verify release PR base and uniquely attribute dispatch runs ([#214](https://github.com/shipshitdev/skills/issues/214)) ([89178a7](https://github.com/shipshitdev/skills/commit/89178a774b977782599c5482483274c37e3062e6))
* **retro:** route deep-mode findings to environment fixes ([#192](https://github.com/shipshitdev/skills/issues/192)) ([ff560ea](https://github.com/shipshitdev/skills/commit/ff560ea226b69ba48d0fb8951d893b13b9ec6e0c))
* **setup-dev-loop:** correct PROJECTS_TOKEN scope and permission guidance ([#212](https://github.com/shipshitdev/skills/issues/212)) ([cbd08cf](https://github.com/shipshitdev/skills/commit/cbd08cf7299a67de5038ab01d56877d7473bb419))
* **skills:** address independent review of [#240](https://github.com/shipshitdev/skills/issues/240) ([#247](https://github.com/shipshitdev/skills/issues/247)) ([6ad4e63](https://github.com/shipshitdev/skills/commit/6ad4e63f391adae3869d6eaa258406eadd72fbbc))
* **skills:** address post-merge review of [#195](https://github.com/shipshitdev/skills/issues/195) and [#201](https://github.com/shipshitdev/skills/issues/201) ([#203](https://github.com/shipshitdev/skills/issues/203)) ([10ec20d](https://github.com/shipshitdev/skills/commit/10ec20d377c2e35f5bea6f49622ca0bb6159935d))
* **skills:** address post-merge reviews of [#189](https://github.com/shipshitdev/skills/issues/189) and [#188](https://github.com/shipshitdev/skills/issues/188) PRs ([#202](https://github.com/shipshitdev/skills/issues/202)) ([1df610d](https://github.com/shipshitdev/skills/commit/1df610db16e906b7a9a5e0f27260ac419e1b92cb))
* **skills:** artifacts-builder on Bun with shadcn/ui; shadcn and tailwind on Tailwind v4; fold shadcn-setup ([#237](https://github.com/shipshitdev/skills/issues/237)) ([7e41833](https://github.com/shipshitdev/skills/commit/7e4183345ed871cd9cae12f2770ae2d0cb488d95)), closes [#235](https://github.com/shipshitdev/skills/issues/235)
* **skills:** keep the trusted Stripe userId authoritative and scan nested lockfiles ([#236](https://github.com/shipshitdev/skills/issues/236)) ([b0277f4](https://github.com/shipshitdev/skills/commit/b0277f4317579002badf48004f87b67194a29a4c))
* **skills:** replace the dead @agenticindiedev/ui package with shadcn/ui ([#242](https://github.com/shipshitdev/skills/issues/242)) ([2643062](https://github.com/shipshitdev/skills/commit/26430628295a17f630ef865bbee4bfb9823fa3e5))
* **skills:** restore argument hints and deploy-app contract checks after [#177](https://github.com/shipshitdev/skills/issues/177) ([#181](https://github.com/shipshitdev/skills/issues/181)) ([aaf976f](https://github.com/shipshitdev/skills/commit/aaf976f55dda8743eecc9dbb2d0be6577688e064))
* **standup:** bound PR enrichment to frozen window and document toolkit license discrepancy ([#216](https://github.com/shipshitdev/skills/issues/216)) ([fca0bbe](https://github.com/shipshitdev/skills/commit/fca0bbe4eaa835188307b102be8a65f90863002c))
* **upstream-drift:** keep tag resolution inside the tracked family; correct impeccable pins ([#231](https://github.com/shipshitdev/skills/issues/231)) ([46bf36f](https://github.com/shipshitdev/skills/commit/46bf36fe00b3d69658ab2bdc17013c0adcb00713))
* **upstream:** keep reports available when derived sources disappear ([#262](https://github.com/shipshitdev/skills/issues/262)) ([beaaf74](https://github.com/shipshitdev/skills/commit/beaaf74daf4c8bbb0ed331fab4d761d34272e083))
* **upstream:** reconcile tracked sources and port reviewed guidance ([#265](https://github.com/shipshitdev/skills/issues/265)) ([159cad7](https://github.com/shipshitdev/skills/commit/159cad7d06415b6064d670e1059fcc3889f2cc10))
* **validate:** fail command routes to skills without SKILL.md ([#210](https://github.com/shipshitdev/skills/issues/210)) ([be101ff](https://github.com/shipshitdev/skills/commit/be101ff2877e572610e7378cb2c2f422c8cba24f))


### Refactors

* **artifacts-builder:** rebuild the asset inliner on parse5 and postcss ([#251](https://github.com/shipshitdev/skills/issues/251)) ([7f681c5](https://github.com/shipshitdev/skills/commit/7f681c5c1e916185405caefe601de297cdb9fc1c))
* delete aliases and merge five overlapping skill pairs ([#195](https://github.com/shipshitdev/skills/issues/195)) ([c80ea6e](https://github.com/shipshitdev/skills/commit/c80ea6e389e72e90a73d11c4c6e3117aea5ff164))
* drop MongoDB/Mongoose skills and standardize on Prisma/Postgres and Vitest ([#208](https://github.com/shipshitdev/skills/issues/208)) ([9d43fb0](https://github.com/shipshitdev/skills/commit/9d43fb0550c1bb18849f7e81091fb77289532aed))
* finish scaffold modernization (Better Auth, Tailwind v4, current pins) ([#222](https://github.com/shipshitdev/skills/issues/222)) ([f69e672](https://github.com/shipshitdev/skills/commit/f69e672cbebd6b571b4a9d3a7424ac33ebad5ff2))
* fold advanced-evaluation, context-degradation, codebase-advisor; drop agent-browser ([#240](https://github.com/shipshitdev/skills/issues/240)) ([e428744](https://github.com/shipshitdev/skills/commit/e428744851580c823a03c42b41110742625c5df3)), closes [#235](https://github.com/shipshitdev/skills/issues/235)
* merge overlapping debug, context, and testing skills ([#169](https://github.com/shipshitdev/skills/issues/169)) ([73ae34c](https://github.com/shipshitdev/skills/commit/73ae34c4a12788d9e9fd602d4ca242c3fdd0591c))
* merge release-pr-gates and release-dispatch into release ([#167](https://github.com/shipshitdev/skills/issues/167)) ([5b2cf4f](https://github.com/shipshitdev/skills/commit/5b2cf4f91698a7d2d5360181686e34b70b2d8da3))
* merge the five stack validators into stack-validator ([#201](https://github.com/shipshitdev/skills/issues/201)) ([5012944](https://github.com/shipshitdev/skills/commit/5012944e4a1043b6c96135be3c87b7ff7b352983))
* rename the grilling primitive to grill-me ([#211](https://github.com/shipshitdev/skills/issues/211)) ([01e6f6c](https://github.com/shipshitdev/skills/commit/01e6f6c3bfeca7ff987454e840abbb8f4d4d2c69))
* **skills:** finish house-stack sweep (Better Auth, Tailwind v4, bun.lock, NestJS 12) ([#230](https://github.com/shipshitdev/skills/issues/230)) ([a1d07e3](https://github.com/shipshitdev/skills/commit/a1d07e38b7eddf47b84f0624da5644cabe93c6ba))
* **skills:** inline router tables into commands and make routers explicit ([#197](https://github.com/shipshitdev/skills/issues/197)) ([604b9dc](https://github.com/shipshitdev/skills/commit/604b9dcff3a896f921bc0d5470e9b7f4811be1a1))
* trim skill descriptions to the listing budget ([#176](https://github.com/shipshitdev/skills/issues/176)) ([574fe91](https://github.com/shipshitdev/skills/commit/574fe916c33402c1fe9854525e597bb5acc7eb6c))


### Chores

* align all skills with repository release 2.2.2 ([#165](https://github.com/shipshitdev/skills/issues/165)) ([b8213b0](https://github.com/shipshitdev/skills/commit/b8213b024e6e630670b7665762dc1c28385fac80))
* **release:** bump only the patch version on every release ([#180](https://github.com/shipshitdev/skills/issues/180)) ([0d0c46c](https://github.com/shipshitdev/skills/commit/0d0c46c6c1dc7103b735747d6b27d9f240953732))
* **skills:** remove unused context-engineering and allowlist a synthetic gitleaks fixture ([#204](https://github.com/shipshitdev/skills/issues/204)) ([0533dc0](https://github.com/shipshitdev/skills/commit/0533dc0708205d99ab413cab1574249214371769))

## [2.2.2](https://github.com/shipshitdev/skills/compare/v2.2.1...v2.2.2) (2026-09-14)


### Bug Fixes

* align dev-loop setup credential guidance ([#151](https://github.com/shipshitdev/skills/issues/151)) ([625e0d6](https://github.com/shipshitdev/skills/commit/625e0d6c9f4fa2df5e12fbb6893221b706cba207))

## [2.2.1](https://github.com/shipshitdev/skills/compare/v2.2.0...v2.2.1) (2026-09-14)


### Bug Fixes

* **board-sync:** detect the CLI entrypoint through symlinked skill installs ([#147](https://github.com/shipshitdev/skills/issues/147)) ([63fec2c](https://github.com/shipshitdev/skills/commit/63fec2cdf52ed329cf7cc42622b7fb5b39caeccd))
* **git-cleanup:** fetch trunk and prove squash landings by file content ([#145](https://github.com/shipshitdev/skills/issues/145)) ([73e6017](https://github.com/shipshitdev/skills/commit/73e6017ef3eab0258da24102e4e0ec6c2b4d582f))
* prepare complete issues and enforce delivery gates ([#149](https://github.com/shipshitdev/skills/issues/149)) ([b75b7f3](https://github.com/shipshitdev/skills/commit/b75b7f351b73ae5b81f81210eb6c724fcd0f13f4))

## [2.2.0](https://github.com/shipshitdev/skills/compare/v2.1.0...v2.2.0) (2026-09-05)


### Features

* consolidate Pstack with pinned upstream synchronization ([#142](https://github.com/shipshitdev/skills/issues/142)) ([17d3741](https://github.com/shipshitdev/skills/commit/17d37411045d3b0c4416b843d584a8b3443b2147))

## [2.1.0](https://github.com/shipshitdev/skills/compare/v2.0.0...v2.1.0) (2026-09-05)


### Features

* **weekly-review:** coordinate recurring engineering maintenance ([#139](https://github.com/shipshitdev/skills/issues/139)) ([e26b1bc](https://github.com/shipshitdev/skills/commit/e26b1bc40da7982aee67cfd801fae14afcbdb7bb))

## [2.0.0](https://github.com/shipshitdev/skills/compare/v1.3.1...v2.0.0) (2026-09-05)


### ⚠ BREAKING CHANGES

* unify GitHub names and provider-aware board workflows ([#137](https://github.com/shipshitdev/skills/issues/137))
* bind cleanup deletion to immutable scoped proof ([#134](https://github.com/shipshitdev/skills/issues/134))
* enforce skill repair and monitoring contracts ([#132](https://github.com/shipshitdev/skills/issues/132))

### Bug Fixes

* bind cleanup deletion to immutable scoped proof ([#134](https://github.com/shipshitdev/skills/issues/134)) ([51bebea](https://github.com/shipshitdev/skills/commit/51bebea40de3f4133142a7fcd1ecfdb36f69417c))
* enforce skill repair and monitoring contracts ([#132](https://github.com/shipshitdev/skills/issues/132)) ([1267d8f](https://github.com/shipshitdev/skills/commit/1267d8f72859965f9f0c9588ad9bf508e5a718a7))
* make workflow composition scoped and discoverable ([#136](https://github.com/shipshitdev/skills/issues/136)) ([60a5587](https://github.com/shipshitdev/skills/commit/60a558762db37e361470ba60f26ae33aeb40bda7))
* reconcile board evidence and native issue priority ([#133](https://github.com/shipshitdev/skills/issues/133)) ([0ee2886](https://github.com/shipshitdev/skills/commit/0ee28867b6c1f89e9760c691a82774109258cc75))


### Refactors

* unify GitHub names and provider-aware board workflows ([#137](https://github.com/shipshitdev/skills/issues/137)) ([9365897](https://github.com/shipshitdev/skills/commit/93658979383fdbf20679742f570d4bd30d8d3e7c))

## [1.3.1](https://github.com/shipshitdev/skills/compare/v1.3.0...v1.3.1) (2026-08-30)


### Features

* add gh-board-sync skill and expand /board into a full front door ([#126](https://github.com/shipshitdev/skills/issues/126)) ([7e30880](https://github.com/shipshitdev/skills/commit/7e30880753c9d9e2a8660e8ddaeac20b3ba9111f))
* consolidate test/scan/env/prompt/performance commands behind skills ([#127](https://github.com/shipshitdev/skills/issues/127)) ([9a403e2](https://github.com/shipshitdev/skills/commit/9a403e230cf0dfe9c8f3407fa7f9dde6049b6ca6))
* rename release-cleanup to git-cleanup behind /cleanup, retire /clean and /inbox ([#125](https://github.com/shipshitdev/skills/issues/125)) ([43d321a](https://github.com/shipshitdev/skills/commit/43d321a7f665583a785a0175d8aa3da46ec85351))

## [1.3.0](https://github.com/shipshitdev/skills/compare/v1.2.0...v1.3.0) (2026-08-28)


### ⚠ BREAKING CHANGES

* hard-rename deslop and monitor QA runtime errors ([#120](https://github.com/shipshitdev/skills/issues/120))

### Features

* hard-rename deslop and monitor QA runtime errors ([#120](https://github.com/shipshitdev/skills/issues/120)) ([1cac5d9](https://github.com/shipshitdev/skills/commit/1cac5d9455de92040fb869c4c63ffddb6f38098c))

## [1.2.0](https://github.com/shipshitdev/skills/compare/v1.1.1...v1.2.0) (2026-08-27)


### Features

* port Lauren Tan pstack skills and recut tdd/de-slop ([#119](https://github.com/shipshitdev/skills/issues/119)) ([e983aba](https://github.com/shipshitdev/skills/commit/e983abae69365fc68d346e311044e168c081eef7))


### Bug Fixes

* **skills:** write disposable scratch to the current repo .tmp ([#116](https://github.com/shipshitdev/skills/issues/116)) ([5d747b4](https://github.com/shipshitdev/skills/commit/5d747b4b10a6a82dc081ba95ed2fa09d29540575))

## [1.1.1](https://github.com/shipshitdev/skills/compare/v1.1.0...v1.1.1) (2026-08-18)


### Chores

* drop the no-op CI dispatch from the release workflow ([#113](https://github.com/shipshitdev/skills/issues/113)) ([9e6af98](https://github.com/shipshitdev/skills/commit/9e6af9852718d57ecb43ba580b2f3ed5d1e85b2a))
* open the release PR as a draft ([#115](https://github.com/shipshitdev/skills/issues/115)) ([ddeb8fe](https://github.com/shipshitdev/skills/commit/ddeb8fe66250b7b842c4935d08d8df74210c4581))

## [1.1.0](https://github.com/shipshitdev/skills/compare/v1.0.0...v1.1.0) (2026-08-17)


### Features

* add release-please for automated versioning and GitHub releases ([#110](https://github.com/shipshitdev/skills/issues/110)) ([90e47be](https://github.com/shipshitdev/skills/commit/90e47be70d76cc22e584b842d20b5635bc7e719b))


### Bug Fixes

* run release-please on GITHUB_TOKEN and dispatch CI on the release branch ([#111](https://github.com/shipshitdev/skills/issues/111)) ([4a063e6](https://github.com/shipshitdev/skills/commit/4a063e6ced1fdb5d7b9b790985c195d1f2f3dba7))
