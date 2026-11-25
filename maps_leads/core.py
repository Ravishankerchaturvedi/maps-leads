import csv
import json
import math
import re
from pathlib import Path
from urllib.parse import urlsplit

COLUMNS = [
    "name",
    "category",
    "phone",
    "website",
    "address",
    "city",
    "rating",
    "reviews",
]

COUNTRY_CODES = {
    "AE": "971",
    "AU": "61",
    "BD": "880",
    "BH": "973",
    "BR": "55",
    "CA": "1",
    "CH": "41",
    "CN": "86",
    "DE": "49",
    "DK": "45",
    "EG": "20",
    "ES": "34",
    "FI": "358",
    "FR": "33",
    "GB": "44",
    "ID": "62",
    "IE": "353",
    "IN": "91",
    "IT": "39",
    "JP": "81",
    "KE": "254",
    "KR": "82",
    "KW": "965",
    "LK": "94",
    "MX": "52",
    "MY": "60",
    "NG": "234",
    "NL": "31",
    "NO": "47",
    "NP": "977",
    "NZ": "64",
    "OM": "968",
    "PH": "63",
    "PK": "92",
    "PL": "48",
    "PT": "351",
    "QA": "974",
    "SA": "966",
    "SE": "46",
    "SG": "65",
    "TH": "66",
    "TR": "90",
    "US": "1",
    "VN": "84",
    "ZA": "27",
}

NATIONAL_LENGTHS = {
    "AE": {9},
    "AU": {9},
    "BD": {10},
    "BH": {8},
    "BR": {10, 11},
    "CA": {10},
    "CH": {9},
    "CN": {11},
    "DE": {10, 11},
    "DK": {8},
    "EG": {10},
    "ES": {9},
    "FI": {9, 10},
    "FR": {9},
    "GB": {9, 10},
    "ID": {9, 10, 11, 12},
    "IE": {9},
    "IN": {10},
    "IT": {9, 10},
    "JP": {10},
    "KE": {9},
    "KR": {9, 10},
    "KW": {8},
    "LK": {9},
    "MX": {10},
    "MY": {9, 10},
    "NG": {10},
    "NL": {9},
    "NO": {8},
    "NP": {10},
    "NZ": {8, 9},
    "OM": {8},
    "PH": {10},
    "PK": {10},
    "PL": {9},
    "PT": {9},
    "QA": {8},
    "SA": {9},
    "SE": {9},
    "SG": {8},
    "TH": {9},
    "TR": {10},
    "US": {10},
    "VN": {9, 10},
    "ZA": {9},
}

COUNTRY_NAMES = {
    "india",
    "republic of india",
    "united states",
    "united states of america",
    "usa",
    "us",
    "united kingdom",
    "uk",
    "great britain",
    "england",
    "scotland",
    "wales",
    "canada",
    "australia",
    "singapore",
    "uae",
    "united arab emirates",
    "germany",
    "france",
    "italy",
    "spain",
    "netherlands",
    "new zealand",
    "south africa",
    "saudi arabia",
    "qatar",
    "kuwait",
    "bahrain",
    "oman",
    "malaysia",
    "indonesia",
    "philippines",
    "thailand",
    "vietnam",
    "sri lanka",
    "nepal",
    "bangladesh",
    "pakistan",
    "china",
    "japan",
    "south korea",
    "korea",
    "brazil",
    "mexico",
    "ireland",
    "portugal",
    "switzerland",
    "sweden",
    "norway",
    "denmark",
    "finland",
    "poland",
    "turkey",
    "egypt",
    "nigeria",
    "kenya",
}

REGIONS = {
    "andaman and nicobar islands",
    "andhra pradesh",
    "arunachal pradesh",
    "assam",
    "bihar",
    "chandigarh",
    "chhattisgarh",
    "dadra and nagar haveli and daman and diu",
    "delhi",
    "goa",
    "gujarat",
    "haryana",
    "himachal pradesh",
    "jammu and kashmir",
    "jharkhand",
    "karnataka",
    "kerala",
    "ladakh",
    "lakshadweep",
    "madhya pradesh",
    "maharashtra",
    "manipur",
    "meghalaya",
    "mizoram",
    "nagaland",
    "national capital territory of delhi",
    "ncr",
    "odisha",
    "orissa",
    "puducherry",
    "pondicherry",
    "punjab",
    "rajasthan",
    "sikkim",
    "tamil nadu",
    "telangana",
    "tripura",
    "uttar pradesh",
    "uttarakhand",
    "west bengal",
    "alabama",
    "al",
    "alaska",
    "ak",
    "arizona",
    "az",
    "arkansas",
    "ar",
    "california",
    "ca",
    "colorado",
    "co",
    "connecticut",
    "ct",
    "delaware",
    "de",
    "florida",
    "fl",
    "georgia",
    "ga",
    "hawaii",
    "hi",
    "idaho",
    "id",
    "illinois",
    "il",
    "indiana",
    "in",
    "iowa",
    "ia",
    "kansas",
    "ks",
    "kentucky",
    "ky",
    "louisiana",
    "la",
    "maine",
    "me",
    "maryland",
    "md",
    "massachusetts",
    "ma",
    "michigan",
    "mi",
    "minnesota",
    "mn",
    "mississippi",
    "ms",
    "missouri",
    "mo",
    "montana",
    "mt",
    "nebraska",
    "ne",
    "nevada",
    "nv",
    "new hampshire",
    "nh",
    "new jersey",
    "nj",
    "new mexico",
    "nm",
    "new york",
    "ny",
    "north carolina",
    "nc",
    "north dakota",
    "nd",
    "ohio",
    "oh",
    "oklahoma",
    "ok",
    "oregon",
    "or",
    "pennsylvania",
    "pa",
    "rhode island",
    "ri",
    "south carolina",
    "sc",
    "south dakota",
    "sd",
    "tennessee",
    "tn",
    "texas",
    "tx",
    "utah",
    "ut",
    "vermont",
    "vt",
    "virginia",
    "va",
    "washington",
    "wa",
    "west virginia",
    "wv",
    "wisconsin",
    "wi",
    "wyoming",
    "wy",
    "alberta",
    "ab",
    "british columbia",
    "bc",
    "manitoba",
    "mb",
    "new brunswick",
    "nb",
    "newfoundland and labrador",
    "nl",
    "nova scotia",
    "ns",
    "ontario",
    "on",
    "prince edward island",
    "pe",
    "quebec",
    "qc",
    "saskatchewan",
    "sk",
    "new south wales",
    "nsw",
    "queensland",
    "qld",
    "south australia",
    "tasmania",
    "tas",
    "victoria",
    "vic",
    "western australia",
    "australian capital territory",
    "act",
    "northern territory",
    "nt",
}

LEGAL_SUFFIXES = {
    "co",
    "company",
    "corp",
    "corporation",
    "gmbh",
    "inc",
    "incorporated",
    "limited",
    "llp",
    "ltd",
    "plc",
    "private",
    "pvt",
}

PHONE_ALLOWED = re.compile(r"^[0-9+\-()./\s]+$")
POSTAL_ONLY = re.compile(
    r"^(?:\d{4,8}(?:-\d{4})?|[A-Z]{1,2}\d[A-Z\d]?\s*\d[A-Z]{2})$",
    re.IGNORECASE,
)
TRAILING_POSTAL = re.compile(
    r"(?:\s+|,\s*)(?:\d{4,8}(?:-\d{4})?|[A-Z]{1,2}\d[A-Z\d]?\s*\d[A-Z]{2})\s*$",
    re.IGNORECASE,
)


def _text(value):
    if value is None:
        return ""
    return str(value).strip()


def _collapse(value):
    return " ".join(_text(value).split())


def _pick(raw, *keys):
    for key in keys:
        if key not in raw:
            continue
        value = raw[key]
        if value is None:
            continue
        if isinstance(value, str) and not value.strip():
            continue
        return value
    return None


def _as_list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return [_text(item) for item in value if _text(item)]
    text = _text(value)
    if not text:
        return []
    if text.startswith("[") and text.endswith("]"):
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            return [text]
        if isinstance(parsed, list):
            return [_text(item) for item in parsed if _text(item)]
    return [text]


def clean_phone(raw, country="IN"):
    text = _text(raw)
    if not text:
        return ""
    if not PHONE_ALLOWED.match(text):
        return text

    country = _text(country).upper()
    digits = re.sub(r"\D", "", text)
    if not digits:
        return text

    if text.startswith("+"):
        if 8 <= len(digits) <= 15:
            return "+" + digits
        return text

    if text.startswith("00"):
        digits = digits[2:]
        if 8 <= len(digits) <= 15:
            return "+" + digits
        return text

    code = COUNTRY_CODES.get(country)
    lengths = NATIONAL_LENGTHS.get(country)
    if not code or not lengths:
        return text

    if len(digits) in lengths and not digits.startswith("0"):
        return "+" + code + digits

    if digits.startswith("0") and (len(digits) - 1) in lengths:
        return "+" + code + digits[1:]

    if digits.startswith(code) and (len(digits) - len(code)) in lengths:
        return "+" + digits

    if digits.startswith("0" + code) and (len(digits) - 1 - len(code)) in lengths:
        return "+" + digits[1:]

    return text


def clean_website(raw):
    text = _text(raw)
    if not text:
        return ""

    if "://" in text:
        scheme, rest = text.split("://", 1)
        scheme = scheme.lower()
        if scheme not in {"http", "https"}:
            scheme = "https"
    else:
        scheme = "https"
        rest = text

    candidate = scheme + "://" + rest
    try:
        parts = urlsplit(candidate)
    except ValueError:
        return text

    host = (parts.hostname or "").strip().lower().rstrip(".")
    if not host or any(char.isspace() for char in host):
        return text

    return scheme + "://" + host


def clean_rating(raw):
    text = _text(raw)
    if not text:
        return ""
    try:
        value = float(text)
    except ValueError:
        return ""
    if not math.isfinite(value) or value < 0 or value > 5:
        return ""
    return format(value, ".2f").rstrip("0").rstrip(".")


def clean_reviews(raw):
    text = _text(raw)
    if not text:
        return ""
    text = text.replace(",", "").replace(" ", "")
    try:
        value = int(text)
    except ValueError:
        try:
            number = float(text)
        except ValueError:
            return ""
        if not math.isfinite(number) or not number.is_integer():
            return ""
        value = int(number)
    if value < 0:
        return ""
    return str(value)


def _is_country(part):
    return part.strip().lower() in COUNTRY_NAMES


def _strip_postal(part):
    return TRAILING_POSTAL.sub("", part).strip(" -,.")


def extract_city(address, explicit_city="", country="IN"):
    city = _collapse(explicit_city)
    if city:
        return city

    parts = [part.strip() for part in _text(address).split(",") if part.strip()]
    for part in reversed(parts):
        if _is_country(part):
            continue
        if POSTAL_ONLY.match(part):
            continue
        candidate = _strip_postal(part)
        if not candidate:
            continue
        lowered = candidate.lower()
        if lowered in COUNTRY_NAMES or lowered in REGIONS:
            continue
        return candidate
    return ""


def _address_from_complete(value):
    if isinstance(value, dict):
        fields = ["street", "borough", "city", "state", "postal_code", "country"]
        parts = []
        for field in fields:
            part = _text(value.get(field))
            if part and (not parts or parts[-1].lower() != part.lower()):
                parts.append(part)
        return ", ".join(parts)
    text = _text(value)
    if not text:
        return ""
    if text.startswith("{") and text.endswith("}"):
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            return text
        if isinstance(parsed, dict):
            return _address_from_complete(parsed)
    return text


def _complete_city(value):
    if isinstance(value, dict):
        return _collapse(value.get("city"))
    text = _text(value)
    if text.startswith("{") and text.endswith("}"):
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            return ""
        if isinstance(parsed, dict):
            return _collapse(parsed.get("city"))
    return ""


def clean_row(raw, country="IN"):
    if not isinstance(raw, dict):
        raw = {}

    name = _collapse(raw.get("title") or raw.get("name"))

    category = _text(raw.get("category"))
    if not category:
        categories = _as_list(raw.get("categories"))
        if categories:
            category = categories[0]

    address = _text(raw.get("address")) or _text(raw.get("full_address"))
    complete = raw.get("complete_address")
    if not address:
        address = _address_from_complete(complete)

    city = _collapse(raw.get("city")) or _complete_city(complete)
    city = extract_city(address, city, country)

    return {
        "name": name,
        "category": category,
        "phone": clean_phone(_pick(raw, "phone", "phone_number"), country),
        "website": clean_website(_pick(raw, "website", "web_site")),
        "address": address,
        "city": city,
        "rating": clean_rating(_pick(raw, "review_rating", "rating")),
        "reviews": clean_reviews(_pick(raw, "review_count", "reviews")),
    }


def filled_count(row):
    return sum(1 for column in COLUMNS if _text(row.get(column)))


def _normalise_name(name):
    text = _collapse(name).lower().replace("&", " and ")
    tokens = re.sub(r"[^a-z0-9]+", " ", text).split()
    while tokens and tokens[-1] in LEGAL_SUFFIXES:
        tokens.pop()
    return " ".join(tokens)


def _normalise_city(city):
    return re.sub(r"[^a-z0-9]+", " ", _collapse(city).lower()).strip()


def dedupe(rows):
    output = []
    phone_index = {}
    name_city_index = {}
    dropped = 0

    for row in rows:
        phone = _text(row.get("phone"))
        name_city = None
        name_key = _normalise_name(row.get("name"))
        if name_key:
            name_city = name_key + "|" + _normalise_city(row.get("city"))

        index = None
        if phone and phone in phone_index:
            index = phone_index[phone]
        elif name_city and name_city in name_city_index:
            index = name_city_index[name_city]

        if index is None:
            index = len(output)
            output.append(row)
        else:
            dropped += 1
            if filled_count(row) <= filled_count(output[index]):
                continue
            old = output[index]
            old_phone = _text(old.get("phone"))
            old_name_key = _normalise_name(old.get("name"))
            old_name_city = None
            if old_name_key:
                old_name_city = old_name_key + "|" + _normalise_city(old.get("city"))
            if old_phone and phone_index.get(old_phone) == index:
                del phone_index[old_phone]
            if old_name_city and name_city_index.get(old_name_city) == index:
                del name_city_index[old_name_city]
            output[index] = row

        if phone:
            phone_index[phone] = index
        if name_city:
            name_city_index[name_city] = index

    return output, dropped


def process(rows, country="IN", min_reviews=None, website=None):
    cleaned = []
    dropped_no_name = 0

    for raw in rows:
        row = clean_row(raw, country)
        if not row["name"]:
            dropped_no_name += 1
            continue
        cleaned.append(row)

    filtered = 0
    if min_reviews is not None or website in {"yes", "no"}:
        kept = []
        for row in cleaned:
            if min_reviews is not None:
                reviews = row["reviews"]
                if not reviews or int(reviews) < min_reviews:
                    filtered += 1
                    continue
            if website == "yes" and not row["website"]:
                filtered += 1
                continue
            if website == "no" and row["website"]:
                filtered += 1
                continue
            kept.append(row)
        cleaned = kept

    output, dropped_duplicate = dedupe(cleaned)
    counts = {
        "in": len(rows),
        "out": len(output),
        "dropped_duplicate": dropped_duplicate,
        "dropped_no_name": dropped_no_name,
        "filtered": filtered,
    }
    return output, counts


def write_csv(rows, path):
    target = Path(path)
    with target.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row.get(column, "") for column in COLUMNS})
