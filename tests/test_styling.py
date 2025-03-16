import unittest
import pandas as pd
from great_tables import GT
from forgts.styling import GTStyler


class TestGTStyler(unittest.TestCase):

    # Initializing GTStyler with valid GT object and formatRdy DataFrame
    def test_init_with_valid_inputs(self):
        # Create a sample dataframe
        data = {"col1": [1, 2, 3], "col2": ["a", "b", "c"]}
        df = pd.DataFrame(data)

        # Create a GT object
        gt_obj = GT(df)

        # Create a formatRdy DataFrame
        format_data = {
            "rowid": [1, 2, 3],
            "target_var": ["col1", "col2", "col1"],
            "helper": ["cell_text", "cell_fill", "cell_borders"],
            "styling_arg": ["weight", None, None],
            "arg_value": ["bold", "#EEEEEE", "solid"],
            "border_property": [None, None, "style"],
            "border_side": [None, None, "all"],
        }
        format_df = pd.DataFrame(format_data)

        # Act
        styler = GTStyler(gt_obj, format_df)

        # Assert
        self.assertEqual(styler.gt_object, gt_obj)
        self.assertTrue(format_df.equals(styler.formatRdy))
        self.assertEqual(styler.row_mapping, {1: 0, 2: 1, 3: 2})
        self.assertEqual(styler.text_styles, {})
        self.assertEqual(styler.border_styles, {})

    # Handling empty or NaN arg_value in formatting definitions
    def test_process_row_with_nan_arg_value(self):
        # Arrange
        import pandas as pd
        import numpy as np
        from great_tables import GT
        from forgts.styling import GTStyler

        # Create a sample dataframe
        data = {"col1": [1, 2, 3], "col2": ["a", "b", "c"]}
        df = pd.DataFrame(data)

        # Create a GT object
        gt_obj = GT(df)

        # Create a formatRdy DataFrame with NaN values
        format_data = {
            "rowid": [1, 2, 3],
            "target_var": ["col1", "col2", "col1"],
            "helper": ["cell_text", "cell_fill", "cell_borders"],
            "styling_arg": ["weight", None, None],
            "arg_value": ["bold", np.nan, None],  # NaN and None values
            "border_property": [None, None, "style"],
            "border_side": [None, None, "all"],
        }
        format_df = pd.DataFrame(format_data)

        # Create a styler
        styler = GTStyler(gt_obj, format_df)

        # Get the row with NaN arg_value
        nan_row = format_df.iloc[1]

        # Act
        # Process the row with NaN arg_value
        styler._process_row(nan_row)

        # Assert
        # Verify that no styling was applied for the NaN row
        self.assertEqual(len(styler.text_styles), 0)
        self.assertEqual(len(styler.border_styles), 0)

        # Now process a valid row to confirm the method works with valid data
        valid_row = format_df.iloc[0]
        styler._process_row(valid_row)

        # Verify that styling was applied for the valid row
        self.assertEqual(len(styler.text_styles), 1)
        cell_key = f"{valid_row['target_var']}_{valid_row['rowid']}"
        self.assertIn(cell_key, styler.text_styles)
        self.assertEqual(styler.text_styles[cell_key]["props"]["weight"], "bold")

    # Creating row mapping from rowid values to positional indices
    def test_create_row_mapping_with_various_rowid_types(self):
        # Arrange
        import pandas as pd
        from great_tables import GT
        from forgts.styling import GTStyler

        # Create a sample dataframe
        data = {"col1": [1, 2, 3], "col2": ["a", "b", "c"]}
        df = pd.DataFrame(data)

        # Create a GT object
        gt_obj = GT(df)

        # Create a formatRdy DataFrame with various rowid types
        format_data = {
            "rowid": [1, "2", "three", None],
            "target_var": ["col1", "col2", "col1", "col2"],
            "helper": ["cell_text", "cell_fill", "cell_borders", "cell_text"],
            "styling_arg": ["weight", None, None, "style"],
            "arg_value": ["bold", "#EEEEEE", "solid", "italic"],
            "border_property": [None, None, "style", None],
            "border_side": [None, None, "all", None],
        }
        format_df = pd.DataFrame(format_data)

        # Act
        styler = GTStyler(gt_obj, format_df)

        # Assert
        expected_row_mapping = {1: 0, 2: 1, "three": "three"}
        self.assertEqual(styler.row_mapping, expected_row_mapping)

    # Processing rows with cell_text helper for various styling arguments
    def test_process_row_with_cell_text_helper(self):
        # Arrange
        import pandas as pd
        from great_tables import GT
        from forgts.styling import GTStyler

        # Create a sample dataframe
        data = {"col1": [1, 2, 3], "col2": ["a", "b", "c"]}
        df = pd.DataFrame(data)

        # Create a GT object
        gt_obj = GT(df)

        # Create a formatRdy DataFrame with cell_text helper
        format_data = {
            "rowid": [1, 2],
            "target_var": ["col1", "col2"],
            "helper": ["cell_text", "cell_text"],
            "styling_arg": ["weight", "color"],
            "arg_value": ["bold", "#FF0000"],
            "border_property": [None, None],
            "border_side": [None, None],
        }
        format_df = pd.DataFrame(format_data)

        # Act
        styler = GTStyler(gt_obj, format_df)
        for _, row in format_df.iterrows():
            styler._process_row(row)

        # Assert
        expected_text_styles = {
            "col1_1": {"target_var": "col1", "rowid": 0, "props": {"weight": "bold"}},
            "col2_2": {"target_var": "col2", "rowid": 1, "props": {"color": "#FF0000"}},
        }
        self.assertEqual(styler.text_styles, expected_text_styles)

    # Accumulating multiple text style properties for the same cell
    def test_accumulate_text_styles_for_same_cell(self):
        # Arrange
        import pandas as pd
        from great_tables import GT
        from forgts.styling import GTStyler

        # Create a sample dataframe
        data = {"col1": [1, 2, 3], "col2": ["a", "b", "c"]}
        df = pd.DataFrame(data)

        # Create a GT object
        gt_obj = GT(df)

        # Create a formatRdy DataFrame with multiple text styles for the same cell
        format_data = {
            "rowid": [1, 1],
            "target_var": ["col1", "col1"],
            "helper": ["cell_text", "cell_text"],
            "styling_arg": ["weight", "color"],
            "arg_value": ["bold", "#FF0000"],
            "border_property": [None, None],
            "border_side": [None, None],
        }
        format_df = pd.DataFrame(format_data)

        # Act
        styler = GTStyler(gt_obj, format_df)
        styler.apply_formatting()

        # Assert
        expected_text_styles = {
            "col1_1": {
                "target_var": "col1",
                "rowid": 0,
                "props": {"weight": "bold", "color": "#FF0000"},
            }
        }
        self.assertEqual(styler.text_styles, expected_text_styles)

    # Mapping between 1-based rowids in input and 0-based indices required by GT
    def test_rowid_mapping(self):
        # Arrange
        import pandas as pd
        from great_tables import GT
        from forgts.styling import GTStyler

        # Create a sample dataframe
        data = {"col1": [1, 2, 3], "col2": ["a", "b", "c"]}
        df = pd.DataFrame(data)

        # Create a GT object
        gt_obj = GT(df)

        # Create a formatRdy DataFrame with rowids
        format_data = {
            "rowid": [1, 2, 3, "A", None],
            "target_var": ["col1", "col2", "col1", "col2", "col1"],
            "helper": [
                "cell_text",
                "cell_fill",
                "cell_borders",
                "cell_text",
                "cell_fill",
            ],
            "styling_arg": ["weight", None, None, "color", None],
            "arg_value": ["bold", "#EEEEEE", "solid", "red", None],
            "border_property": [None, None, "style", None, None],
            "border_side": [None, None, "all", None, None],
        }
        format_df = pd.DataFrame(format_data)

        # Act
        styler = GTStyler(gt_obj, format_df)

        # Assert
        expected_mapping = {1: 0, 2: 1, 3: 2, "A": "A"}
        self.assertEqual(styler.row_mapping, expected_mapping)

    # Returning properly formatted GT object after applying all styles
    def test_apply_formatting_with_valid_styles(self):
        # Arrange
        import pandas as pd
        from great_tables import GT
        from forgts.styling import GTStyler
        from unittest.mock import MagicMock

        # Create a sample dataframe
        data = {"col1": [1, 2, 3], "col2": ["a", "b", "c"]}
        df = pd.DataFrame(data)

        # Create a GT object and mock its tab_style method
        gt_obj = GT(df)
        gt_obj.tab_style = MagicMock(return_value=gt_obj)

        # Create a formatRdy DataFrame with styling definitions
        format_data = {
            "rowid": [1, 2, 3],
            "target_var": ["col1", "col2", "col1"],
            "helper": ["cell_text", "cell_fill", "cell_borders"],
            "styling_arg": ["weight", None, None],
            "arg_value": ["bold", "#EEEEEE", "solid"],
            "border_property": [None, None, "style"],
            "border_side": [None, None, "all"],
        }
        format_df = pd.DataFrame(format_data)

        # Act
        styler = GTStyler(gt_obj, format_df)
        formatted_gt = styler.apply_formatting()

        # Assert
        self.assertEqual(formatted_gt, gt_obj)
        gt_obj.tab_style.assert_called()
