# chwebsite
A website for the Critical Hit weekly tournament.

## Upcoming tournaments

The site displays upcoming Canterbury tournaments from `events.json`. The snapshot is refreshed every six hours by `.github/workflows/update-events.yml` using the start.gg GraphQL API; the browser does not need an API token. The checked-in snapshot includes the verified [Critical Hit Freshers Event 2026](https://www.start.gg/tournament/critical-hit-freshers-event-2026/details) (1 October 2026), so it is visible even before the first refresh. Past events are hidden by the browser.

To enable automatic updates:

1. Create a new start.gg API token (the token previously embedded in `index.html` has expired). Revoke the old token if it is still listed in your account.
2. Add the new token as a repository Actions secret named `START_GG_TOKEN` under **Settings → Secrets and variables → Actions**. Do not put it in the website source.
3. Ensure GitHub Actions has **Read and write permissions** under **Settings → Actions → General → Workflow permissions** and that scheduled workflows are enabled. Run **Update upcoming tournaments** manually once using **Actions → Run workflow** to verify it commits `events.json`.

If the secret expires, the workflow fails without overwriting the last snapshot. Replace the secret and rerun the workflow. `python update_events.py` can also be run locally with `START_GG_TOKEN` set in the environment.
