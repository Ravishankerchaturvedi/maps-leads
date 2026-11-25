import unittest

from maps_leads.core import (
    COLUMNS,
    clean_phone,
    clean_rating,
    clean_reviews,
    clean_row,
    clean_website,
    dedupe,
    extract_city,
    process,
)


class PhoneTests(unittest.TestCase):
    def test_indian_mobile_with_trunk_zero(self):
        self.assertEqual(clean_phone("098765 43210", "IN"), "+919876543210")

    def test_indian_mobile_without_trunk_zero(self):
        self.assertEqual(clean_phone("98765 43210", "IN"), "+919876543210")

    def test_indian_number_with_country_code(self):
        self.assertEqual(clean_phone("+91 98765 43210", "IN"), "+919876543210")

    def test_indian_number_with_00_prefix(self):
        self.assertEqual(clean_phone("0091 98765 43210", "IN"), "+919876543210")

    def test_indian_landline(self):
        self.assertEqual(clean_phone("080 4123 4567", "IN"), "+918041234567")

    def test_us_number(self):
        self.assertEqual(clean_phone("(415) 555-2671", "US"), "+14155552671")

    def test_ambiguous_number_is_kept_raw(self):
        self.assertEqual(clean_phone("12345", "IN"), "12345")

    def test_letters_are_kept_raw(self):
        self.assertEqual(clean_phone("98765ABC", "IN"), "98765ABC")

    def test_unknown_country_keeps_raw(self):
        self.assertEqual(clean_phone("98765 43210", "XX"), "98765 43210")

    def test_empty_phone(self):
        self.assertEqual(clean_phone("", "IN"), "")
        self.assertEqual(clean_phone(None, "IN"), "")


class WebsiteTests(unittest.TestCase):
    def test_scheme_is_added(self):
        self.assertEqual(clean_website("WWW.Example.COM/menu"), "https://www.example.com")

    def test_http_scheme_is_preserved(self):
        self.assertEqual(clean_website("http://ChennaiSilks.example/"), "http://chennaisilks.example")

    def test_https_scheme_is_lowercased(self):
        self.assertEqual(
            clean_website("HTTPS://WWW.KolkataKati.Example/order"),
            "https://www.kolkatakati.example",
        )

    def test_port_and_path_are_dropped(self):
        self.assertEqual(clean_website("example.com:8080/path?q=1"), "https://example.com")

    def test_invalid_website_is_kept_raw(self):
        self.assertEqual(clean_website("not a url"), "not a url")

    def test_empty_website(self):
        self.assertEqual(clean_website(""), "")


class RatingTests(unittest.TestCase):
    def test_trailing_zeros_are_trimmed(self):
        self.assertEqual(clean_rating("4.500000"), "4.5")

    def test_whole_number(self):
        self.assertEqual(clean_rating("5"), "5")

    def test_zero_is_valid(self):
        self.assertEqual(clean_rating("0"), "0")

    def test_two_decimals(self):
        self.assertEqual(clean_rating("4.25"), "4.25")

    def test_out_of_range_is_empty(self):
        self.assertEqual(clean_rating("5.1"), "")
        self.assertEqual(clean_rating("-1"), "")

    def test_non_numeric_is_empty(self):
        self.assertEqual(clean_rating("abc"), "")
        self.assertEqual(clean_rating("nan"), "")
        self.assertEqual(clean_rating(""), "")


class ReviewTests(unittest.TestCase):
    def test_thousands_separator(self):
        self.assertEqual(clean_reviews("1,234"), "1234")

    def test_integral_float(self):
        self.assertEqual(clean_reviews("1234.0"), "1234")

    def test_fractional_float_is_empty(self):
        self.assertEqual(clean_reviews("1234.5"), "")

    def test_negative_is_empty(self):
        self.assertEqual(clean_reviews("-2"), "")

    def test_non_numeric_is_empty(self):
        self.assertEqual(clean_reviews("abc"), "")
        self.assertEqual(clean_reviews(""), "")

    def test_zero_is_valid(self):
        self.assertEqual(clean_reviews("0"), "0")


class CityTests(unittest.TestCase):
    def test_city_before_state_and_pin(self):
        self.assertEqual(
            extract_city("12, MG Road, Bengaluru, Karnataka 560001, India"),
            "Bengaluru",
        )

    def test_city_with_pin_attached(self):
        self.assertEqual(extract_city("MG Road, Bengaluru 560001"), "Bengaluru")

    def test_city_from_us_address(self):
        self.assertEqual(extract_city("1 Congress Ave, Austin, TX 78701, United States"), "Austin")

    def test_city_from_uk_address(self):
        self.assertEqual(extract_city("221B Baker Street, London NW1 6XE, United Kingdom"), "London")

    def test_explicit_city_wins(self):
        self.assertEqual(
            extract_city("12, MG Road, Bengaluru, Karnataka 560001, India", "Mysuru"),
            "Mysuru",
        )

    def test_no_city(self):
        self.assertEqual(extract_city("Karnataka 560001, India"), "")


class RowTests(unittest.TestCase):
    def test_maps_gosom_json_fields(self):
        row = clean_row(
            {
                "title": "Third Wave Coffee",
                "categories": ["Cafe", "Coffee shop"],
                "web_site": "https://WWW.ThirdWave.example/about",
                "phone": "+91-80-1234-5678",
                "address": "14, 80 Feet Road, Koramangala, Bengaluru, Karnataka 560034, India",
                "review_count": 456,
                "review_rating": 4.6,
            }
        )
        self.assertEqual(row["name"], "Third Wave Coffee")
        self.assertEqual(row["category"], "Cafe")
        self.assertEqual(row["phone"], "+918012345678")
        self.assertEqual(row["website"], "https://www.thirdwave.example")
        self.assertEqual(row["city"], "Bengaluru")
        self.assertEqual(row["rating"], "4.6")
        self.assertEqual(row["reviews"], "456")

    def test_complete_address_is_used_when_address_is_missing(self):
        row = clean_row(
            {
                "title": "Complete Address Cafe",
                "category": "Cafe",
                "complete_address": {
                    "street": "5, Church Street",
                    "city": "Bengaluru",
                    "state": "Karnataka",
                    "postal_code": "560001",
                    "country": "India",
                },
            }
        )
        self.assertEqual(row["address"], "5, Church Street, Bengaluru, Karnataka, 560001, India")
        self.assertEqual(row["city"], "Bengaluru")

    def test_numeric_zero_rating_and_reviews_are_kept(self):
        row = clean_row(
            {
                "title": "Zero Cafe",
                "category": "Cafe",
                "review_count": 0,
                "review_rating": 0.0,
            }
        )
        self.assertEqual(row["rating"], "0")
        self.assertEqual(row["reviews"], "0")

    def test_empty_row_has_all_columns(self):
        row = clean_row({})
        self.assertEqual(list(row.keys()), COLUMNS)
        self.assertTrue(all(value == "" for value in row.values()))


class DedupeTests(unittest.TestCase):
    def _row(self, name, phone="", city="", website="", category="", address="", rating="", reviews=""):
        return {
            "name": name,
            "category": category,
            "phone": phone,
            "website": website,
            "address": address,
            "city": city,
            "rating": rating,
            "reviews": reviews,
        }

    def test_same_phone_keeps_row_with_more_fields(self):
        sparse = self._row("Cafe One", phone="+919876543210", city="Pune")
        rich = self._row(
            "Cafe One",
            phone="+919876543210",
            city="Pune",
            website="https://cafeone.example",
            category="Cafe",
            reviews="10",
        )
        output, dropped = dedupe([sparse, rich])
        self.assertEqual(dropped, 1)
        self.assertEqual(len(output), 1)
        self.assertEqual(output[0]["website"], "https://cafeone.example")

    def test_same_name_and_city_is_duplicate(self):
        first = self._row("Spice Garden", phone="+919111111111", city="Bengaluru", website="https://a.example")
        second = self._row("Spice Garden", phone="+912222222222", city="Bengaluru")
        output, dropped = dedupe([first, second])
        self.assertEqual(dropped, 1)
        self.assertEqual(output[0]["phone"], "+919111111111")

    def test_legal_suffix_is_ignored_in_name(self):
        first = self._row("Acme Foods Pvt Ltd", phone="+919111111111", city="Pune")
        second = self._row("Acme Foods", phone="+912222222222", city="Pune")
        output, dropped = dedupe([first, second])
        self.assertEqual(dropped, 1)
        self.assertEqual(len(output), 1)

    def test_different_city_is_not_duplicate(self):
        first = self._row("Cafe One", phone="+919111111111", city="Pune")
        second = self._row("Cafe One", phone="+912222222222", city="Mumbai")
        output, dropped = dedupe([first, second])
        self.assertEqual(dropped, 0)
        self.assertEqual(len(output), 2)

    def test_no_phone_and_no_name_are_not_matched(self):
        first = self._row("", phone="", city="Pune")
        second = self._row("", phone="", city="Pune")
        output, dropped = dedupe([first, second])
        self.assertEqual(dropped, 0)
        self.assertEqual(len(output), 2)


class ProcessTests(unittest.TestCase):
    def _raw(self, name, phone="", website="", reviews="", city="Pune"):
        return {
            "title": name,
            "phone": phone,
            "web_site": website,
            "review_count": reviews,
            "address": "MG Road, " + city + ", Maharashtra 411001, India",
        }

    def test_counts(self):
        rows = [
            self._raw("Cafe One", phone="9876543210", reviews="10"),
            self._raw("Cafe One", phone="09876543210", reviews="10"),
            self._raw("", phone="9999999999"),
            self._raw("Cafe Two", phone="9123456780", reviews="2"),
        ]
        output, counts = process(rows)
        self.assertEqual(counts["in"], 4)
        self.assertEqual(counts["out"], 2)
        self.assertEqual(counts["dropped_duplicate"], 1)
        self.assertEqual(counts["dropped_no_name"], 1)
        self.assertEqual(counts["filtered"], 0)
        self.assertEqual(len(output), 2)

    def test_min_reviews_filter(self):
        rows = [
            self._raw("Cafe One", phone="9876543210", reviews="10"),
            self._raw("Cafe Two", phone="9123456780", reviews="2"),
            self._raw("Cafe Three", phone="9000000001", reviews=""),
        ]
        output, counts = process(rows, min_reviews=5)
        self.assertEqual(counts["filtered"], 2)
        self.assertEqual([row["name"] for row in output], ["Cafe One"])

    def test_has_website_filter(self):
        rows = [
            self._raw("Cafe One", phone="9876543210", website="https://one.example"),
            self._raw("Cafe Two", phone="9123456780"),
        ]
        output, counts = process(rows, website="yes")
        self.assertEqual(counts["filtered"], 1)
        self.assertEqual([row["name"] for row in output], ["Cafe One"])

    def test_no_website_filter(self):
        rows = [
            self._raw("Cafe One", phone="9876543210", website="https://one.example"),
            self._raw("Cafe Two", phone="9123456780"),
        ]
        output, counts = process(rows, website="no")
        self.assertEqual(counts["filtered"], 1)
        self.assertEqual([row["name"] for row in output], ["Cafe Two"])


if __name__ == "__main__":
    unittest.main()
