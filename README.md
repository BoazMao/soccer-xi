# World Cup XI

A static browser drafting game built with Next.js, TypeScript and Tailwind CSS. Draft a 4-3-3 from randomized World Cup champion squads, then reveal a hidden rating tier and an eight-match record.

## Included MVP data

- Spain — 2010 (23-player final squad)
- Germany — 2014 (23-player final squad)
- France — 2018 (23-player final squad)
- Argentina — 2022 (26-player final squad)

Squad membership, tournament clubs, primary positions, and game-edition ratings are maintained separately in `src/data/squads.ts`. The expandable career statistics are deterministic demo snapshots for the MVP and are explicitly structured for replacement by a verified import pipeline.

## Local development

```bash
npm install
npm run dev
```

## Architecture

- `src/data` — data schema and squad snapshots
- `src/lib` — drafting, positional-fit, randomization, scoring and tiers
- `src/components` — interactive game UI
- `.github/workflows` — static export and GitHub Pages deployment

The hidden `rating` field is never displayed during drafting. Players are only eligible for compatible empty 4-3-3 slots. The final average maps to S through D tiers and an eight-game record.

## GitHub Pages

In repository settings, select **GitHub Actions** as the Pages source. Every push to `main` will build and deploy the static export.
