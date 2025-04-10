import unittest
from ETL.data_transformation.cleaning_utils import Cleaner


class TestCleaner(unittest.TestCase):
    def test_remove_item_markers(self):
        cleaner = Cleaner()
        text = "ITEM 1 BUSINESS OVERVIEW This is the business overview."
        expected = " This is the business overview."
        self.assertEqual(cleaner.remove_item_markers(text), expected)

        text = "Item 4. Submission of Matters to a Vote of Security Holders. This is a vote."
        expected = "This is a vote."
        self.assertEqual(cleaner.remove_item_markers(text), expected)

        text = "No item marker here."
        expected = "No item marker here."
        self.assertEqual(cleaner.remove_item_markers(text), expected)

    def test_replace_empty_fields(self):
        cleaner = Cleaner()
        text = ""
        expected = "lorem ipsum"
        self.assertEqual(cleaner.replace_empty_fields(text), expected)

        text = None
        expected = "lorem ipsum"
        self.assertEqual(cleaner.replace_empty_fields(text), expected)

        text = "Non-empty text"
        expected = "Non-empty text"
        self.assertEqual(cleaner.replace_empty_fields(text), expected)

    def test_to_lowercase(self):
        cleaner = Cleaner()
        text = "THIS SHOULD BE LOWERCASE"
        expected = "this should be lowercase"
        self.assertEqual(cleaner.to_lowercase(text), expected)

        text = "Already lowercase"
        expected = "already lowercase"
        self.assertEqual(cleaner.to_lowercase(text), expected)

    def test_remove_table_strings(self):
        cleaner = Cleaner()
        text = "This has unicode trash like &#8221 and &#8203."
        expected = "This has unicode trash like  and ."
        self.assertEqual(cleaner.remove_table_strings(text), expected)

        text = "This text is clean."
        expected = "This text is clean."
        self.assertEqual(cleaner.remove_table_strings(text), expected)


if __name__ == "__main__":
    unittest.main()
