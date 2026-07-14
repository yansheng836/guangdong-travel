"""Tests for geocoding query context."""

import os
import unittest

os.environ.setdefault("AMAP_KEY", "test-key")

from scripts.geocode_update import resolve_city_name


class ResolveCityNameTests(unittest.TestCase):
    """Verify city constraints are never lost for legacy documents."""

    def test_falls_back_to_scanned_city_directory(self):
        self.assertEqual(resolve_city_name("", "潮州市"), "潮州市")

    def test_prefers_explicit_document_city(self):
        self.assertEqual(resolve_city_name("汕头市", "潮州市"), "汕头市")


if __name__ == "__main__":
    unittest.main()
