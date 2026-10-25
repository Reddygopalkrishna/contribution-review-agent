# GitHub Action

The composite action runs only static checks. It writes findings to the GitHub job summary and workflow annotations; it does not create pull-request comments, issues, reviews, or commits.

Copy this workflow and replace `path/to/contribution` with the project directory to audit:

```yaml
name: Contribution audit
on: pull_request
permissions:
  contents: read
jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          persist-credentials: false
      - uses: actions/setup-python@v5
        with:
          python-version: "3.10"
      - uses: Reddygopalkrishna/contribution-review-agent@main
        with:
          path: path/to/contribution
          repo-root: .
          config: generic
```

## Security model

- The trigger is `pull_request`, never `pull_request_target`.
- Workflow permission is limited to `contents: read`.
- Checkout disables persisted credentials.
- The action does not execute the audited contribution's code. It invokes only `python3 -m contrib_audit`.
- No PR comments are made by default. If API triage is added later, it must inspect GitHub API patch data rather than run or trust contributed code.

The action uses no token directly and makes no network request from the deterministic auditor.
