# maps-leads

[![tests](https://github.com/Ravishankerchaturvedi/maps-leads/actions/workflows/tests.yml/badge.svg)](https://github.com/Ravishankerchaturvedi/maps-leads/actions/workflows/tests.yml)
![python](https://img.shields.io/badge/python-3.10%2B-blue)
![license](https://img.shields.io/badge/license-MIT-green)
![dependencies](https://img.shields.io/badge/dependencies-none-brightgreen)

**The step after scraping: turn a raw Google Maps export into a clean, deduplicated lead CSV you can hand to a person or an agent.**

[gosom/google-maps-scraper](https://github.com/gosom/google-maps-scraper) gives you raw listings: phones in six formats, uppercase URLs with tracking paths, no city unless you parse the address, and the same shop once per query. maps-leads reads that export (CSV, JSON or JSONL), cleans it into eight predictable columns, merges duplicates, and writes one tidy CSV. Standard library only, no network access, and it never invents data: a value it cannot parse is kept as written or left empty.

## Problem

A scrape is not a lead list. Before the rows are useful someone has to normalise phone numbers, lowercase hosts, pull the city out of the address, drop rows without a name, and merge the same business found twice - by hand, or with a fragile spreadsheet. That cleanup step is exactly what people ask for in the issue trackers of the popular Maps scrapers. maps-leads does it deterministically, offline, and reports exactly what it dropped.

## Install

Python 3.10 or newer. No dependencies beyond the standard library.

```bash
pip install -e .[test]
```

Or run it straight from a checkout:

```bash
python -m maps_leads --help
```

## Quickstart

```bash
maps-leads clean examples/sample_gosom.csv -o leads.csv
head -4 leads.csv
```

Real output of the quickstart above (run on 2026-11-25):

```
in: 11
out: 7
dropped_duplicate: 3
dropped_no_name: 1
filtered: 0
name,category,phone,website,address,city,rating,reviews
Spice Junction,Indian restaurant,+919876543210,https://www.spicejunction.example,"12, MG Road, Bengaluru, Karnataka 560001, India",Bengaluru,4.5,1234
Harbour Coffee Co,Cafe,+918041234567,https://harbourcoffee.example,"Shop 4, 100 Feet Road, Indiranagar, Bengaluru, Karnataka 560038, India",Bengaluru,3.8,3
City Tiffin Service,Tiffin service,12345,https://citytiffin.example,"Flat 2, Andheri West, Mumbai, Maharashtra 400053, India",Mumbai,,0
```

The counts go to stderr, the CSV to the file you name. The sample row `City Tiffin Service` keeps its phone as `12345`: too short to convert, so nothing is invented.

## The 8 columns

| Column | Meaning |
|---|---|
| `name` | Business name (`title` in gosom output) |
| `category` | Primary category (first of `categories` when needed) |
| `phone` | E.164 phone number when the country code is known, otherwise the trimmed raw value |
| `website` | Scheme plus lowercase host, e.g. `https://example.com` |
| `address` | Street address |
| `city` | City, taken from the data or derived from the address |
| `rating` | Review rating as a number from 0 to 5, or empty |
| `reviews` | Review count as an integer, or empty |

Rows with no business name are dropped. When two rows share a phone number, or the same normalised name and city, the row with more filled fields is kept.

## Use it with gosom/google-maps-scraper

Run the scraper as usual, then clean the result:

```bash
docker run \
  -v "$PWD/example-queries.txt:/queries.txt:ro" \
  -v "$PWD/gmaps-output:/out" \
  gosom/google-maps-scraper \
  -input /queries.txt \
  -results /out/results.csv \
  -depth 1

python -m maps_leads clean gmaps-output/results.csv -o leads.csv
```

JSON works the same way:

```bash
docker run \
  -v "$PWD/example-queries.txt:/queries.txt:ro" \
  -v "$PWD/gmaps-output:/out" \
  gosom/google-maps-scraper \
  -input /queries.txt \
  -json -results /out/results.json \
  -depth 1

python -m maps_leads clean gmaps-output/results.json -o leads.csv
```

Both the gosom CSV header (`website`, `review_count`, `review_rating`) and the gosom JSON keys
(`web_site`, `review_count`, `review_rating`, `complete_address`) are understood. JSONL and a JSON array
are both accepted.

### Options

```text
maps-leads clean INPUT -o OUTPUT [options]

  --country CODE        ISO country code used for E.164 phones (default: IN, which means +91)
  --min-reviews N       Keep only rows with at least N reviews
  --has-website         Keep only rows with a website
  --no-website          Keep only rows without a website
  --format {auto,csv,json}
                        Input format (default: auto)
```

Phone numbers are only converted when the result is unambiguous. A number that is too short, contains letters,
or belongs to an unsupported country is kept exactly as it was written. Digits are never invented.

`--min-reviews` drops rows with a missing review count, because their count cannot be checked.

## How it works

`clean` reads the export (format auto-detected, or forced with `--format`), then maps each row's fields onto the
8 columns: gosom's `title`, `category`/`categories`, `phone`, `website`/`web_site`, `address`/`complete_address`,
`review_count` and `review_rating`. Phones become E.164 when the `--country` code and the digit count are
unambiguous (trunk `0`, `00` and `+code` forms are handled; 43 countries are built in). Websites become scheme
plus lowercase host. Ratings are kept when they are between 0 and 5; review counts when they are integers.
When the data has no city, it is derived from the address: the last comma-separated part that is not a country,
a region, or a postal code. Deduplication keys on a shared phone or a normalised name plus city (legal suffixes
like Pvt and Ltd are ignored), keeping the row with more filled fields. Every run prints its counts
(`in`, `out`, `dropped_duplicate`, `dropped_no_name`, `filtered`) to stderr.

## Use it with AI agents

- Exit code `0` = the cleaned CSV was written; `2` = the input could not be read or the output path could not
  be written (the error names the path on stderr).
- The stderr counts are machine-parseable: an agent can clean a raw gosom export, read
  `dropped_duplicate` and `filtered`, and decide whether to widen the query or apply `--min-reviews` /
  `--has-website` and clean again.
- Output columns are fixed and typed, so the CSV can be loaded straight into a CRM import, a spreadsheet, or a
  JSON-mapping step in an agent pipeline.
- The repo ships a `SKILL.md`, so coding agents that read skills (for example Claude Code) can run the cleanup
  on a scrape themselves.

## Limits

- Phones convert only for the 43 countries in the table; anything ambiguous stays exactly as written.
- No geocoding, no enrichment, no network access: the city comes from the address text, not a map service.
- `--min-reviews` drops rows whose review count is missing, because the filter cannot check them.
- Only gosom-style exports are mapped; a spreadsheet with different headers needs a mapping step first.
- Email addresses, opening hours and photos in the source export are not carried into the 8 columns.

## Polite use

This tool only reformats data you already have. It does not scrape, does not log in, and makes no requests. If
you collect that data yourself:

- scrape public listings only;
- keep volume low and be gentle with the site;
- stay polite and logged-out; do not use an account to get around limits;
- do not bypass CAPTCHAs or bot checks (this tool does no CAPTCHA bypass);
- respect the website's terms and applicable law.

If a site blocks you, stop. Do not try to look human or dodge detection.

## About

Built by Ravi Shanker Chaturvedi at RAD Media, Mumbai. We build AI systems for growing businesses; this is one of
our starter agents. Questions, bugs or a custom build: open an issue.
