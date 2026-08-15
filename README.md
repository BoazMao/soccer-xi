# World Cup XI

A browser drafting game built with Next.js, TypeScript and Tailwind CSS. Choose a formation, spin for a randomized country and World Cup year, then find out if your XI can win 8 games straight.

## Included MVP data

The static MVP contains 63 final-squad pools and 1,500 player-tournament records across the 2010, 2014, 2018, and 2022 World Cups. It covers Argentina, Australia, Belgium, Brazil, Colombia, Croatia, Denmark, England, France, Germany, Japan, Morocco, Peru, Poland, Portugal, Senegal, South Korea, Spain, Sweden, and Uruguay whenever they qualified.

Squad membership, broad position, tournament club, caps, available international-goal totals, and Chinese display names are imported from English and Simplified Chinese historical squad tables. Historical FIFA 10, FIFA 14, FIFA 18, and FIFA 23 overall ratings are matched from archived SoFIFA snapshots: 1,360 of 1,500 player-tournament records currently have a sourced rating. Unmatched ratings are recorded as provisional in `src/data/ratingCoverage.json`.

Club goals, club assists, and trophy totals are shown as unavailable rather than estimated because a consistent, auditable "as of World Cup kickoff" source has not yet been imported. Detailed position eligibility also remains provisional.
