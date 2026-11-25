---
name: maps-leads
description: Turn a raw gosom/google-maps-scraper export (CSV, JSON or JSONL) into a deduplicated 8-column lead CSV with E.164 phones, normalised websites and cities derived from the address. Use when someone has scraped Google Maps listings and needs a tidy lead list without inventing data.
---

# maps-leads

## When to use
- Someone has output from gosom/google-maps-scraper (or a similar Maps export) and needs a clean, deduplicated
  lead list with a fixed set of columns.
- A CRM import or an agent pipeline needs typed rows (E.164 phone, host-only website, integer review count)
  instead of the scraper's raw text.

## Steps
1. Run `maps-leads clean <export> -o leads.csv` (add `--country IN` for +91 numbers, the default, or another
   ISO code; `--min-reviews N` and `--has-website`/`--no-website` to filter). The counts
   (`in`, `out`, `dropped_duplicate`, `dropped_no_name`, `filtered`) are printed to stderr.
   Exit code 0 = the CSV was written; 2 = the input could not be read or the output path is not writable.
2. Read `leads.csv`: the 8 columns are `name, category, phone, website, address, city, rating, reviews`.
3. If the counts show heavy deduplication or filtering, clean the original export again with adjusted flags
   rather than editing the output by hand.

## Rules
- Never invent data: a phone that cannot be converted unambiguously stays as written; an unparseable rating or
  review count stays empty.
- The tool reads files and makes no network requests. Scraping itself is a separate, polite, logged-out activity
  with no CAPTCHA or bot-check bypass.
- Say it plainly when the city was derived from the address text and may be a district, not the postal city.
