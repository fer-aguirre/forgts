import unittest
import pandas as pd
from forgts.translate_formatting import ExcelFormattingTranslator


class TestExcelFormattingTranslator(unittest.TestCase):

    # Translating a DataFrame with basic formatting (bold, italic, underline) correctly
    def test_translate_basic_formatting(self):
        # Create a sample DataFrame with basic formatting
        format_data = {
            "row": [1, 1, 1],
            "col": [1, 1, 1],
            "format": ["bold", "italic", "underlined"],
            "val": ["True", "True", "True"],
        }
        format_df = pd.DataFrame(format_data)

        # Initialize the translator and translate
        translator = ExcelFormattingTranslator(format_df)
        result = translator.translate()

        # Verify the translation results
        self.assertEqual(len(result), 3)

        # Check bold formatting
        bold_row = result[result["format"] == "bold"].iloc[0]
        self.assertEqual(bold_row["styling_arg"], "weight")
        self.assertEqual(bold_row["helper"], "cell_text")
        self.assertEqual(bold_row["arg_value"], "bold")

        # Check italic formatting
        italic_row = result[result["format"] == "italic"].iloc[0]
        self.assertEqual(italic_row["styling_arg"], "style")
        self.assertEqual(italic_row["helper"], "cell_text")
        self.assertEqual(italic_row["arg_value"], "italic")

        # Check underline formatting
        underline_row = result[result["format"] == "underlined"].iloc[0]
        self.assertEqual(underline_row["styling_arg"], "decorate")
        self.assertEqual(underline_row["helper"], "cell_text")
        self.assertEqual(underline_row["arg_value"], "underline")

    # Processing an empty DataFrame
    def test_translate_empty_dataframe(self):
        # Create an empty DataFrame
        empty_df = pd.DataFrame(columns=["row", "col", "format", "val"])

        # Initialize the translator with the empty DataFrame
        translator = ExcelFormattingTranslator(empty_df)

        # Translate the empty DataFrame
        result = translator.translate()

        # Verify the result is also an empty DataFrame with the expected columns
        self.assertTrue(result.empty)
        self.assertEqual(len(result), 0)

        # Check that all expected columns are present in the result
        expected_columns = [
            "row",
            "col",
            "format",
            "val",
            "styling_arg",
            "helper",
            "arg_value",
            "border_side",
            "border_property",
        ]
        for col in expected_columns:
            self.assertIn(col, result.columns)

    # Processing color values and converting them to proper hex format
    def test_normalize_color_values(self):
        # Create a sample DataFrame with color formatting
        format_data = {
            "row": [1, 2, 3],
            "col": [1, 2, 3],
            "format": ["hl_color", "text_clr", "border_top_clr"],
            "val": ["FF5733", "00000000", "123456"],
        }
        format_df = pd.DataFrame(format_data)

        # Initialize the translator and translate
        translator = ExcelFormattingTranslator(format_df)
        result = translator.translate()

        # Verify the translation results
        self.assertEqual(len(result), 3)

        # Check highlight color normalization
        hl_color_row = result[result["format"] == "hl_color"].iloc[0]
        self.assertEqual(hl_color_row["arg_value"], "#FF5733")

        # Check text color normalization for transparent value
        text_clr_row = result[result["format"] == "text_clr"].iloc[0]
        self.assertIsNone(text_clr_row["arg_value"])

        # Check border color normalization
        border_clr_row = result[result["format"] == "border_top_clr"].iloc[0]
        self.assertEqual(border_clr_row["arg_value"], "#123456")

    # Converting border styles (thin, thick, medium) to numeric values
    def test_convert_border_styles_to_numeric_values(self):
        # Create a sample DataFrame with border styles
        format_data = {
            "row": [1, 2, 3],
            "col": [1, 1, 1],
            "format": ["border_top_style", "border_right_style", "border_bottom_style"],
            "val": ["thin", "thick", "medium"],
        }
        format_df = pd.DataFrame(format_data)

        # Initialize the translator and translate
        translator = ExcelFormattingTranslator(format_df)
        result = translator.translate()

        # Verify the translation results
        self.assertEqual(len(result), 3)

        # Check thin border style conversion
        thin_row = result[result["val"] == "thin"].iloc[0]
        self.assertEqual(thin_row["arg_value"], "1")

        # Check thick border style conversion
        thick_row = result[result["val"] == "thick"].iloc[0]
        self.assertEqual(thick_row["arg_value"], "3")

        # Check medium border style conversion
        medium_row = result[result["val"] == "medium"].iloc[0]
        self.assertEqual(medium_row["arg_value"], "2")

    # Correctly categorizing formatting types into helper categories
    def test_helper_category_assignment(self):
        # Create a sample DataFrame with various formatting types
        format_data = {
            "row": [1, 2, 3, 4, 5, 6, 7],
            "col": [1, 1, 1, 1, 1, 1, 1],
            "format": [
                "bold",
                "italic",
                "underlined",
                "strikethrough",
                "text_clr",
                "hl_color",
                "border_top_style",
            ],
            "val": ["True", "True", "True", "True", "#FF0000", "#00FF00", "solid"],
        }
        format_df = pd.DataFrame(format_data)

        # Initialize the translator and translate
        translator = ExcelFormattingTranslator(format_df)
        result = translator.translate()

        # Verify the helper category assignment
        self.assertEqual(
            result[result["format"] == "bold"].iloc[0]["helper"], "cell_text"
        )
        self.assertEqual(
            result[result["format"] == "italic"].iloc[0]["helper"], "cell_text"
        )
        self.assertEqual(
            result[result["format"] == "underlined"].iloc[0]["helper"], "cell_text"
        )
        self.assertEqual(
            result[result["format"] == "strikethrough"].iloc[0]["helper"], "cell_text"
        )
        self.assertEqual(
            result[result["format"] == "text_clr"].iloc[0]["helper"], "cell_text"
        )
        self.assertEqual(
            result[result["format"] == "hl_color"].iloc[0]["helper"], "cell_fill"
        )
        self.assertEqual(
            result[result["format"] == "border_top_style"].iloc[0]["helper"],
            "cell_borders",
        )

    # Ensure that invalid or malformed color values are handled correctly by filtering them out or setting their argument values to None.
    def test_invalid_color_values_handling(self):
        # Create a sample DataFrame with invalid color values
        format_data = {
            "row": [1, 2, 3],
            "col": [1, 2, 3],
            "format": ["hl_color", "text_clr", "border_top_clr"],
            "val": ["ZZZZZZ", "00000000", "12345G"],
        }
        format_df = pd.DataFrame(format_data)

        # Initialize the translator and translate
        translator = ExcelFormattingTranslator(format_df)
        result = translator.translate()

        # Verify the translation results for invalid color values
        hl_color_row = result[result["format"] == "hl_color"]
        if not hl_color_row.empty:
            self.assertIsNone(hl_color_row.iloc[0]["arg_value"])

        text_clr_row = result[result["format"] == "text_clr"]
        if not text_clr_row.empty:
            self.assertIsNone(text_clr_row.iloc[0]["arg_value"])

        border_top_clr_row = result[result["format"] == "border_top_clr"]
        if not border_top_clr_row.empty:
            self.assertIsNone(border_top_clr_row.iloc[0]["arg_value"])

    # Handling None or empty values in the 'val' column
    def test_handle_none_or_empty_values(self):
        # Create a sample DataFrame with None and empty values in 'val' column
        format_data = {
            "row": [1, 2, 3],
            "col": [1, 2, 3],
            "format": ["bold", "italic", "hl_color"],
            "val": [None, "", "00000000"],
        }
        format_df = pd.DataFrame(format_data)

        # Initialize the translator and translate
        translator = ExcelFormattingTranslator(format_df)
        result = translator.translate()

        # Verify the translation results
        self.assertEqual(len(result), 3)

        # Check bold formatting with None value
        bold_row = result[result["format"] == "bold"].iloc[0]
        self.assertEqual(bold_row["styling_arg"], "weight")
        self.assertEqual(bold_row["helper"], "cell_text")
        self.assertIsNone(bold_row["arg_value"])

        # Check italic formatting with empty value
        italic_row = result[result["format"] == "italic"].iloc[0]
        self.assertEqual(italic_row["styling_arg"], "style")
        self.assertEqual(italic_row["helper"], "cell_text")
        self.assertIsNone(italic_row["arg_value"])

        # Check hl_color formatting with transparent value
        hl_color_row = result[result["format"] == "hl_color"].iloc[0]
        self.assertEqual(hl_color_row["styling_arg"], "color")
        self.assertEqual(hl_color_row["helper"], "cell_fill")
        self.assertIsNone(hl_color_row["arg_value"])

    # Dealing with unexpected format types not covered in the mapping conditions
    def test_unexpected_format_types(self):
        # Create a sample DataFrame with unexpected format types
        format_data = {
            "row": [1, 2],
            "col": [1, 2],
            "format": ["unexpected_format", "another_unknown"],
            "val": ["True", "False"],
        }
        format_df = pd.DataFrame(format_data)

        # Initialize the translator and translate
        translator = ExcelFormattingTranslator(format_df)
        result = translator.translate()

        # Verify the translation results for unexpected formats
        self.assertEqual(len(result), 2)

        # Check unexpected_format handling
        unexpected_row = result[result["format"] == "unexpected_format"].iloc[0]
        self.assertEqual(unexpected_row["styling_arg"], "unexpected_format")
        self.assertEqual(unexpected_row["helper"], "unexpected_format")
        self.assertIsNone(unexpected_row["arg_value"])

        # Check another_unknown handling
        unknown_row = result[result["format"] == "another_unknown"].iloc[0]
        self.assertEqual(unknown_row["styling_arg"], "another_unknown")
        self.assertEqual(unknown_row["helper"], "another_unknown")
        self.assertIsNone(unknown_row["arg_value"])

    # Processing border styles that aren't 'thin', 'thick', or 'medium'
    def test_non_standard_border_styles(self):
        # Create a sample DataFrame with non-standard border styles
        format_data = {
            "row": [1, 2],
            "col": [1, 2],
            "format": ["border_top_style", "border_bottom_style"],
            "val": ["dashed", "dotted"],
        }
        format_df = pd.DataFrame(format_data)

        # Initialize the translator and translate
        translator = ExcelFormattingTranslator(format_df)
        result = translator.translate()

        # Verify the translation results
        self.assertEqual(len(result), 2)

        # Check non-standard border styles remain unchanged
        top_border_row = result[result["format"] == "border_top_style"].iloc[0]
        self.assertEqual(top_border_row["arg_value"], "dashed")

        bottom_border_row = result[result["format"] == "border_bottom_style"].iloc[0]
        self.assertEqual(bottom_border_row["arg_value"], "dotted")

    # Normalizing 8-character ARGB strings to 6-character RGB format
    def test_normalize_color_argb_to_rgb(self):
        # Create a sample DataFrame with ARGB color values
        format_data = {
            "row": [1, 2],
            "col": [1, 2],
            "format": ["hl_color", "text_clr"],
            "val": ["FF123456", "FF654321"],  # ARGB values
        }
        format_df = pd.DataFrame(format_data)

        # Initialize the translator and translate
        translator = ExcelFormattingTranslator(format_df)
        result = translator.translate()

        # Verify the normalization of ARGB to RGB
        hl_color_row = result[result["format"] == "hl_color"].iloc[0]
        self.assertEqual(hl_color_row["arg_value"], "#123456")

        text_clr_row = result[result["format"] == "text_clr"].iloc[0]
        self.assertEqual(text_clr_row["arg_value"], "#654321")

    # Correctly identifying and processing border-related formatting
    def test_translate_border_formatting(self):
        # Create a sample DataFrame with border-related formatting
        format_data = {
            "row": [1, 1, 1, 1],
            "col": [1, 1, 1, 1],
            "format": [
                "border_top_style",
                "border_right_style",
                "border_bottom_style",
                "border_left_style",
            ],
            "val": ["thin", "medium", "thick", "thin"],
        }
        format_df = pd.DataFrame(format_data)

        # Initialize the translator and translate
        translator = ExcelFormattingTranslator(format_df)
        result = translator.translate()

        # Verify the translation results
        self.assertEqual(len(result), 4)

        # Check top border style
        top_border_row = result[result["format"] == "border_top_style"].iloc[0]
        self.assertEqual(top_border_row["styling_arg"], "top")
        self.assertEqual(top_border_row["helper"], "cell_borders")
        self.assertEqual(top_border_row["arg_value"], "1")

        # Check right border style
        right_border_row = result[result["format"] == "border_right_style"].iloc[0]
        self.assertEqual(right_border_row["styling_arg"], "right")
        self.assertEqual(right_border_row["helper"], "cell_borders")
        self.assertEqual(right_border_row["arg_value"], "2")

        # Check bottom border style
        bottom_border_row = result[result["format"] == "border_bottom_style"].iloc[0]
        self.assertEqual(bottom_border_row["styling_arg"], "bottom")
        self.assertEqual(bottom_border_row["helper"], "cell_borders")
        self.assertEqual(bottom_border_row["arg_value"], "3")

        # Check left border style
        left_border_row = result[result["format"] == "border_left_style"].iloc[0]
        self.assertEqual(left_border_row["styling_arg"], "left")
        self.assertEqual(left_border_row["helper"], "cell_borders")
        self.assertEqual(left_border_row["arg_value"], "1")
