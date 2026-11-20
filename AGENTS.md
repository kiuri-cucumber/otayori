# Instructions for agents working on otayori

## What this is

otayori reads the paper a family gets from school, the hospital and city hall, and turns it into a shared calendar and checklist. The people who depend on it are not engineers. One of them is a grandmother reading it at 7am. A wrong date means a child shows up without what they need.

## What matters, in order

1. **A date is never wrong silently.** If you are not sure, surface it for a human to confirm. A missing item is bad. A wrong date that looks right is worse.
2. **Family documents never leave the box.** You only see this repo. Never ask for real documents, never add them to the repo, never send text to a cloud OCR or any third-party service.
3. **Boring technology.** Python 3.12, SQLite, the standard library first. Add a dependency only when the task cannot be done without it, and say why in the PR.

## How you work

- Work on a branch and open a PR. Never push to `main`.
- Every bug fix starts with a failing test that reproduces it. Then fix it.
- Never loosen or delete a test to make it pass. If a test is wrong, say so in the PR and wait.
- Run `python -m unittest discover -s tests -t .` before you open the PR. CI runs the same command.
- Keep PRs small: one issue, one PR.
- In the PR, show the before and after output for the input that was wrong.

## Where the work comes from

- Issues labeled `bot`. Take the oldest first.
- "Misread" issues filed by the app. Each carries one line of text and the date a family member said was correct. Turn that line into a test case in `tests/`, then fix `app/extract.py`.
- Tickets posted in Slack.

## Things that are easy to get wrong here

- Dates use the imperial era (令和9年4月8日), full-width digits (4月8日), or no year at all. A date with no year means the next time that date comes around.
- "までに" and "提出" mean a deadline, not an event.
- One notice often holds several events. Do not stop at the first date.
- OCR output has stray spaces inside dates ("4 月 8 日"). Normalize before matching.

## Do not

- Change the SQLite schema or the `.ics` format without an issue that asks for it.
- Add accounts, analytics, telemetry or any network call that is not in the issue.
- Commit anything under `data/` or `tests/fixtures/private/`.
- Guess. If the issue is unclear, ask in the issue and stop.
