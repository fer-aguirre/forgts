import pandas as pd
import numpy as np
from typing import Optional


"""
A class to translate Excel formatting specifications into a structured DataFrame.

This class processes a DataFrame containing Excel formatting information,
transforming it into a format suitable for further processing or application.
It includes methods to map format types to styling arguments, categorize
formatting types, generate argument values, update border styles, and add
border properties.

Attributes:
    format_long (pd.DataFrame): The input DataFrame containing Excel formatting
        specifications.
    translated_data (pd.DataFrame): The processed DataFrame with translated
        formatting information.

Methods:
    translate(): Translates the input DataFrame by applying a series of
        transformations to generate a structured output.
"""


class ExcelFormattingTranslator:
    def __init__(self, format_long: pd.DataFrame):
        """
        Initializes the translation class with the given Excel formatting DataFrame.

        Args:
            format_long (pd.DataFrame): The input DataFrame containing Excel formatting
                specifications to be translated.
        """
        self.format_long = format_long.copy()
        self.translated_data = None

    def translate(self) -> pd.DataFrame:
        """
        Translates the formatting of the DataFrame by applying a series of transformations.

        This method processes the `format_long` DataFrame by sequentially applying
        styling arguments, helper categories, argument values, and border styles.
        It returns the transformed DataFrame with updated formatting properties.

        Returns:
            pd.DataFrame: The DataFrame with translated formatting.
        """    
        self.translated_data = self.format_long.copy()
        self.translated_data = self._add_styling_arguments(self.translated_data)
        self.translated_data = self._add_helper_categories(self.translated_data)
        self.translated_data = self._add_argument_values(self.translated_data)
        self.translated_data = self._update_border_styles(self.translated_data)
        self.translated_data = self._add_border_properties(self.translated_data)
        return self.translated_data

    @staticmethod
    def _add_styling_arguments(df: pd.DataFrame) -> pd.DataFrame:
        """
        Add a 'styling_arg' column to the DataFrame by mapping format types
        to corresponding styling arguments.

        Args:
            df (pd.DataFrame): DataFrame containing a 'format' column with
                Excel formatting specifications.

        Returns:
            pd.DataFrame: Updated DataFrame with an additional 'styling_arg'
                column representing the mapped styling arguments.
        """
        mapping_conditions = [
            (df['format'] == 'bold'),
            (df['format'] == 'italic'),
            (df['format'] == 'underlined'),
            (df['format'] == 'strikethrough'),
            (df['format'].str.contains('color')),
            (df['format'].str.contains('top_style')),
            (df['format'].str.contains('right_style')),
            (df['format'].str.contains('bottom_style')),
            (df['format'].str.contains('left_style')),
            (df['format'].str.contains('clr'))
        ]

        mapping_values = [
            'weight', 'style', 'decorate', 'decorate', 'color',
            'top', 'right', 'bottom', 'left', 'color'
        ]

        df['styling_arg'] = np.select(mapping_conditions, mapping_values, default=df['format'])
        return df

    @staticmethod
    def _add_helper_categories(df: pd.DataFrame) -> pd.DataFrame:
        """
        Adds a 'helper' column to the DataFrame categorizing formatting types.

        This method evaluates the 'format' column of the input DataFrame and assigns
        a category to each row based on predefined conditions. The categories include
        'cell_text', 'cell_fill', and 'cell_borders', which are used to facilitate
        further processing of formatting information.

        Args:
            df (pd.DataFrame): The DataFrame containing a 'format' column with
                formatting specifications.

        Returns:
            pd.DataFrame: The input DataFrame with an additional 'helper' column
            categorizing the formatting types.
        """
        category_conditions = [
            (df['format'] == 'bold'),
            (df['format'] == 'italic'),
            (df['format'] == 'underlined'),
            (df['format'] == 'strikethrough'),
            (df['format'] == 'text_clr'),
            (df['format'] == 'hl_color'),
            (df['format'].str.contains('border'))
        ]

        category_values = [
            'cell_text', 'cell_text', 'cell_text', 'cell_text',
            'cell_text', 'cell_fill', 'cell_borders'
        ]

        df['helper'] = np.select(category_conditions, category_values, default=df['format'])
        return df

    @staticmethod
    def _normalize_color(color_value: Optional[str]) -> Optional[str]:
        """
        Normalize a color value to a standard RGB hex format.

        This method processes a given color value, which may be in ARGB or RGB
        hex string format, and returns it in a standardized RGB hex format.
        If the color value is invalid or represents black in ARGB format, it
        returns None.

        Args:
            color_value (Optional[str]): The color value in hex string format.

        Returns:
            Optional[str]: The normalized RGB hex string or None if the input
            is invalid or represents black.
        """
        if not color_value or color_value == "00000000":
            return None

        # Check if color_value is a valid hex string
        try:
            int(color_value, 16)
        except ValueError:
            return None

        # If color_value is an 8-character ARGB string, return the RGB part
        if len(color_value) == 8:
            return f"#{color_value[2:]}"

        # If color_value is a 6-character RGB string, return it as is
        if len(color_value) == 6:
            return f"#{color_value}"

    def _add_argument_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add argument values to the DataFrame based on formatting conditions.

        This method evaluates specific conditions on the 'format' and 'val'
        columns of the input DataFrame to determine the appropriate argument
        values for styling. It assigns these values to a new 'arg_value'
        column. Additionally, it normalizes color values for relevant formats.

        Args:
            df (pd.DataFrame): The DataFrame containing formatting information
            with 'format' and 'val' columns.

        Returns:
            pd.DataFrame: The updated DataFrame with an added 'arg_value'
            column containing the determined argument values.
        """    
        value_conditions = [
            ((df['format'] == 'bold') & (df['val'] == 'True')),
            ((df['format'] == 'italic') & (df['val'] == 'True')),
            ((df['format'] == 'underlined') & (df['val'] != 'False')),
            ((df['format'] == 'strikethrough') & (df['val'] != 'False')),
            ((df['format'] == 'hl_color') & (df['val'] != 'None')),
            ((df['format'] == 'text_clr') & (df['val'] != 'None')),
            (df['format'].str.contains('border_.+_clr') & (df['val'] != 'None')),
            (df['format'].str.contains('border_.+_style') & (df['val'] != 'None'))
        ]

        value_choices = [
            'bold',
            'italic',
            'underline',
            'line-through',
            df['val'].copy(),
            df['val'].copy(),
            df['val'].copy(),
            df['val']
        ]

        df['arg_value'] = np.select(value_conditions, value_choices, default=None)

        # Normalize color values where needed
        color_mask = (
            ((df['format'] == 'hl_color') & (df['val'] != 'None')) |
            ((df['format'] == 'text_clr') & (df['val'] != 'None')) |
            (df['format'].str.contains('border_.+_clr') & (df['val'] != 'None'))
        )

        df.loc[color_mask, 'arg_value'] = df.loc[color_mask, 'arg_value'].apply(self._normalize_color)

        return df

    @staticmethod
    def _update_border_styles(df: pd.DataFrame) -> pd.DataFrame:
        """
        Updates the border styles in the DataFrame based on specified conditions.

        This method modifies the 'arg_value' column in the input DataFrame by
        mapping specific border style strings ('thin', 'thick', 'medium') to
        corresponding numeric codes ('1', '3', '2'). If no condition is met,
        the original value is retained.

        Args:
            df (pd.DataFrame): The DataFrame containing a column 'arg_value'
                with border style specifications.

        Returns:
            pd.DataFrame: The updated DataFrame with modified 'arg_value' entries.
        """
        border_conditions = [
            (df['arg_value'] == 'thin'),
            (df['arg_value'] == 'thick'),
            (df['arg_value'] == 'medium')
        ]

        border_choices = ['1', '3', '2']

        df['arg_value'] = np.select(
            border_conditions,
            border_choices,
            default=df['arg_value']
        )

        return df

    @staticmethod
    def _add_border_properties(df: pd.DataFrame) -> pd.DataFrame:
        """
        Adds border properties to a DataFrame containing Excel formatting information.

        This method processes the input DataFrame to add columns for border sides
        and border properties based on specific formatting conditions. It filters
        out rows related to cell borders where the argument value is None, ensuring
        only relevant formatting information is retained.

        Args:
            df (pd.DataFrame): The input DataFrame with Excel formatting details.

        Returns:
            pd.DataFrame: A DataFrame with additional columns for border sides and
            properties, filtered to exclude irrelevant cell border entries.
        """
        # Create a copy to avoid modifying the input
        df_copy = df.copy()

        # Add border_side column
        border_side_mask = (
            df_copy['format'].str.contains('border_.+_style', regex=True) &
            (df_copy['helper'] == 'cell_borders') &
            (df_copy['val'] != 'None')
        )

        df_copy['border_side'] = None
        df_copy.loc[border_side_mask, 'border_side'] = df_copy.loc[border_side_mask, 'styling_arg']

        # Add border_property column
        border_prop_conditions = [
            (df_copy['format'].str.contains('border_.+_style', regex=True) &
             (df_copy['helper'] == 'cell_borders')),
            (df_copy['format'].str.contains('border_.+_clr', regex=True) &
             (df_copy['helper'] == 'cell_borders'))
        ]

        border_prop_choices = ['sides', 'color']

        df_copy['border_property'] = np.select(border_prop_conditions, border_prop_choices, default=None)

        # Filter out cell_borders rows where arg_value is None
        cell_borders_mask = (df_copy['helper'] == 'cell_borders')
        valid_borders_mask = (df_copy['arg_value'].notna())

        # Keep rows that are either not cell_borders OR are cell_borders with non-None arg_value
        df_filtered = df_copy[~cell_borders_mask | (cell_borders_mask & valid_borders_mask)]

        return df_filtered