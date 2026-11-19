# Setting Up `/qa prod`

A one-time checklist for the person who owns the product. `/qa prod` is only as safe
as the account and secrets you give it. Nothing here is committed to a repository.

## 1. A dedicated production QA account

- Create a real account on production used only for QA, with an address you control and
  a recognizable name (for example `qa-bot+prod@<your-domain>`). Never reuse a person's account.
- Put it in its own tenant, workspace, or organization with no access to real users' data.
  Give it the same role an ordinary paying user has, never admin.
- Seed fixtures it owns (a project, a sample record, a file) and write them down in the
  repository's QA notes. The skill treats the fixtures as the baseline cleanup returns to.
- Use the cheapest plan that unlocks the features under test. Anything that charges real
  money or messages real people stays untested unless you add a sandbox path
  (a test recipient, a dry-run flag) and say so in the repository's QA notes.
- If sign-in uses email codes, MFA, or a CAPTCHA, create a saved browser session
  (a Playwright storage-state file) once by hand, keep it outside the repository, and
  refresh it when it expires. The skill never bypasses MFA or CAPTCHA.

## 2. Supply the credentials as environment variables

| Variable | Meaning |
|---|---|
| `QA_BASE_URL` | Production origin, for example `https://app.example.com` |
| `QA_USER_EMAIL` | The QA account email |
| `QA_USER_PASSWORD` | The QA account password (omit when using a session file) |
| `QA_STORAGE_STATE` | Absolute path to a saved browser session file (alternative to the password) |

Provide them from a secret store, never from a tracked file: the agent harness's own
secret or environment settings, a password-manager CLI that injects variables into the
agent's process, or CI secrets. A `.env` file is acceptable only when it is gitignored and
outside any directory the agent commits from. Rotate the password if it ever appears in
output.

## 3. Name the board column

`/qa prod` reads cards from a GitHub Projects v2 board's `Status` column. The default name
is `Human Review`, which is the column ShipCode writes. Pass `--owner`, `--project`, and,
for another name, `--status "<name>"`. The `gh` token needs the `project` scope
(`gh auth refresh -s project`). Only cards whose change has merged and deployed can be
proven on production; the rest are reported as not-tested.

## 4. Decide how a release starts the run

The skill takes a tag as input and does not decide when it runs. Pick one trigger:

- **By hand, per release.** After the release workflow finishes, run `$qa prod <tag>`
  in Codex or `/qa prod <tag>` in Claude Code.
- **From CI, after the deploy.** A workflow listens for the published release, waits
  for the deploy workflow for that tag to succeed, then starts the agent non-interactively.
  The sketch below is an untested example. Adapt the deploy-workflow name and the agent
  command to your setup, and keep the QA secrets in the repository or environment secrets.

  ```yaml
  on:
    workflow_run:
      workflows: ["Publish"]
      types: [completed]
  jobs:
    qa:
      if: github.event.workflow_run.conclusion == 'success' && startsWith(github.event.workflow_run.head_branch, 'v')
      runs-on: ubuntu-latest
      environment: prod-qa
      env:
        QA_BASE_URL: ${{ secrets.QA_BASE_URL }}
        QA_USER_EMAIL: ${{ secrets.QA_USER_EMAIL }}
        QA_USER_PASSWORD: ${{ secrets.QA_USER_PASSWORD }}
        GH_TOKEN: ${{ secrets.QA_GH_TOKEN }}
      steps:
        - uses: actions/checkout@v4
        # Install the agent CLI and the skills, then run the skill non-interactively
        # with the tag from github.event.workflow_run.head_branch.
  ```

  Use an environment with required reviewers if you want a human to approve each production run.
- **From a scheduled agent.** Poll for a new published release and run the skill once per tag.

## 5. Where fixes go

`/qa prod --fix` and `/verify loop` change code on a branch and open a pull request. They
never edit production. Decide whether you want them to open the PR for you; the default
is to stop at a local commit and ask. A fix reaches production only through your normal
merge and release path, then `/qa prod <tag> --only <items> --build <fix tag>` confirms it there.
