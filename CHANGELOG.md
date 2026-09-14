# Changelog

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
