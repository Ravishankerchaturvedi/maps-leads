# Changelog

## 0.1.0 — 2026-11-25

Initial release.

- `maps-leads clean INPUT -o OUTPUT`: reads the CSV, JSON or JSONL that gosom/google-maps-scraper writes and
  cleans it into the 8 columns `name, category, phone, website, address, city, rating, reviews`.
- Phone normalisation to E.164 for 43 countries (`--country`, default `IN`), never inventing digits; website
  normalisation to scheme plus lowercase host; rating and review-count normalisation; city derived from the
  address when the data has none.
- Deduplication by shared phone or normalised name plus city, keeping the row with more filled fields; run
  counts (`in`, `out`, `dropped_duplicate`, `dropped_no_name`, `filtered`) on stderr.
- `--min-reviews`, `--has-website`/`--no-website` and `--format` options.
- Standard library only; the tests never fetch anything.
