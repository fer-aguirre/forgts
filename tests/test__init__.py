import unittest
import pandas as pd
from forgts import format_gt_from_excel
from great_tables import GT
import os


class TestFormatGTFromExcel(unittest.TestCase):

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.test_excel_path = "valid_test_file.xlsx"

        # Optionally, create a valid test Excel file here
        df = pd.DataFrame({"A": [1, 2], "B": [3, 4]})
        df.to_excel(self.test_excel_path, index=False)

    def tearDown(self):
        """Clean up actions after each test method."""
        if os.path.exists(self.test_excel_path):
            os.remove(self.test_excel_path)

    # Test with non-existent Excel file path to verify FileNotFoundError is raised
    def test_nonexistent_file_raises_error(self):
        # Define a non-existent file path
        non_existent_path = "non_existent_file.xlsx"

        # Ensure the file doesn't actually exist
        if os.path.exists(non_existent_path):
            os.remove(non_existent_path)

        # Check that FileNotFoundError is raised
        with self.assertRaises(FileNotFoundError):
            format_gt_from_excel(non_existent_path)

    # Test with empty Excel sheet to verify ValueError is raised
    def test_empty_sheet_raises_error(self):
        # Create an empty Excel file
        empty_excel_path = "empty_test_file.xlsx"
        import pandas as pd

        df = pd.DataFrame()
        df.to_excel(empty_excel_path, index=False)

        try:
            # Check that ValueError is raised
            with self.assertRaises(ValueError):
                format_gt_from_excel(empty_excel_path)
        finally:
            # Clean up the temporary file
            if os.path.exists(empty_excel_path):
                os.remove(empty_excel_path)
