# Tetrixa — Game Discovery

A multilingual static website for **Tetrixa**, the Android block-puzzle arcade game by **DevImpact**.

- Google Play: https://play.google.com/store/apps/details?id=com.game.tetrixa.devimpact
- Android application ID: com.game.tetrixa.devimpact
- Website: https://shelternewlife.github.io/tetrixa/

## What this repository provides

- Pre-rendered HTML pages for the published English, French, German, Italian, Spanish and Portuguese market locales.
- About, features, download, FAQ and gameplay resource pages.
- Real Google Play screenshots, canonical URLs, hreflang, Open Graph metadata and Schema.org JSON-LD.
- Generated sitemap.xml, sitemap.txt, robots.txt and llms.txt.
- Python standard-library build, validation and automated tests.
- GitHub Actions build, test, GitHub Pages deployment and Lighthouse audit.

## Verified product scope

The Google Play listing describes Tetrixa as a mobile block-puzzle game with piece movement and rotation, row clearing, scoring, gradually increasing difficulty, touch controls and offline play. The listing also identifies the app as containing ads. Website copy is limited to those published details and visible store screenshots.

## Build and test locally

```bash
python -m unittest discover -s tests -v
python scripts/build.py
python scripts/validate.py
```

Generated pages are written to `dist/` and are not committed.

## GitHub Pages

In repository Settings → Pages → Build and deployment, select **GitHub Actions** as the source. The workflow deploys the generated `dist/` artifact on pushes to `main` and on manual dispatch.

## Content maintenance

Edit `content/app.json`, `content/features.json`, `content/faq.json`, `content/screenshots.json`, locale content and market keyword strategy. Keep claims aligned with the current Google Play listing. Review the store link, privacy policy and support details periodically.

## Scope and limitations

The site is static and does not provide game accounts, leaderboards, multiplayer services, game APIs or server-side features. Search engines decide independently whether and when to crawl or index pages; publishing a sitemap does not guarantee indexing.
