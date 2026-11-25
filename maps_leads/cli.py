import argparse
import csv
import sys

from .core import process, write_csv
from .readers import read_rows

COUNT_KEYS = ("in", "out", "dropped_duplicate", "dropped_no_name", "filtered")


def build_parser():
    parser = argparse.ArgumentParser(
        prog="maps_leads",
        description="Clean Google Maps scraper output into an 8-field lead CSV.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    clean = subparsers.add_parser(
        "clean",
        help="Clean a gosom/google-maps-scraper JSON or CSV export.",
    )
    clean.add_argument("input", help="Input CSV, JSON, or JSONL file.")
    clean.add_argument("-o", "--output", required=True, help="Output CSV path.")
    clean.add_argument(
        "--country",
        default="IN",
        help="ISO country code used to build E.164 phone numbers (default: IN).",
    )
    clean.add_argument(
        "--min-reviews",
        type=int,
        default=None,
        metavar="N",
        help="Keep only rows with at least N reviews.",
    )
    website = clean.add_mutually_exclusive_group()
    website.add_argument(
        "--has-website",
        action="store_true",
        help="Keep only rows with a website.",
    )
    website.add_argument(
        "--no-website",
        action="store_true",
        help="Keep only rows without a website.",
    )
    clean.add_argument(
        "--format",
        choices=("auto", "csv", "json"),
        default="auto",
        help="Input format (default: auto).",
    )
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        rows = read_rows(args.input, args.format)
    except (OSError, ValueError, csv.Error) as error:
        print(f"maps_leads: cannot read {args.input}: {error}", file=sys.stderr)
        return 2

    website_filter = None
    if args.has_website:
        website_filter = "yes"
    elif args.no_website:
        website_filter = "no"

    output, counts = process(
        rows,
        country=args.country,
        min_reviews=args.min_reviews,
        website=website_filter,
    )

    try:
        write_csv(output, args.output)
    except OSError as error:
        print(f"maps_leads: cannot write {args.output}: {error}", file=sys.stderr)
        return 2

    for key in COUNT_KEYS:
        print(f"{key}: {counts[key]}", file=sys.stderr)
    return 0
