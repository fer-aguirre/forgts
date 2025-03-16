import pandas as pd
from great_tables import GT
from great_tables import style, loc, px


"""
A class to apply styling to a great_tables GT object using formatting definitions.

The GTStyler class processes a DataFrame containing styling instructions and applies
text, fill, and border styles to a GT object. It supports various text properties
like weight, style, color, and border properties such as color, weight, and sides.

Attributes:
-----------
gt_object : GT
    The GT object to which styles will be applied.
format_ready : pandas.DataFrame
    A DataFrame containing formatting definitions.
border_styles : dict
    A dictionary to store border styling information.
text_styles : dict
    A dictionary to store text styling information.
row_mapping : dict
    A mapping of rowid values to positional indices.

Methods:
--------
apply_formatting():
    Applies all styles to the GT object based on the formatting definitions.
"""


class GTStyler:

    def __init__(self, gt_object: GT, format_ready: pd.DataFrame):
        """
        Initialize the GTStyler with a GT object and formatting definitions.

        Parameters:
        -----------
        gt_object : GT
            The GT object to which styles will be applied.
        format_ready : pandas.DataFrame
            A DataFrame containing formatting definitions.
        """
        self.gt_object = gt_object
        self.format_ready = format_ready
        self.border_styles = {}
        self.text_styles = {}
        self.row_mapping = self._create_row_mapping()

    def _create_row_mapping(self):
        """
        Create a mapping of row IDs to positional indices.

        This method processes the 'rowid' column from the format_ready DataFrame,
        converting each unique row ID to a zero-based positional index. If a row ID
        is numeric, it is converted to an integer and decremented by one to create
        the mapping. Non-numeric row IDs are mapped to themselves.

        Returns:
        --------
        dict
            A dictionary mapping each row ID to its corresponding positional index.
        """
        unique_rowids = self.format_ready['rowid'].dropna().unique()
        row_mapping = {}
        for rowid in unique_rowids:
            try:
                numeric_rowid = int(rowid)
                row_mapping[numeric_rowid] = numeric_rowid - 1
            except (ValueError, TypeError):
                row_mapping[rowid] = rowid
        return row_mapping

    def _apply_text_styles(self):
        """
        Applies text styles to the GT object.

        Iterates over the text styling definitions and applies the specified
        text properties to the corresponding cells in the GT object using
        the great_tables styling functions.
        """
        for cell_key, cell_style in self.text_styles.items():
            if cell_style['props']:
                text_style = style.text(**cell_style['props'])
                self.gt_object = self.gt_object.tab_style(
                    style=text_style,
                    locations=loc.body(
                        columns=[cell_style['target_var']],
                        rows=[cell_style['rowid']]
                    )
                )

    def _apply_border_styles(self):
        """
        Apply border styles to the GT object based on the defined border styles.

        Iterates over the border styles dictionary and applies the specified
        border properties such as sides, color, style, and weight to the
        corresponding cells in the GT object.

        Modifies the GT object in place by setting the tab style for the
        specified cell locations.
        """
        for cell_key, cell_style in self.border_styles.items():
            sides = ['top', 'right', 'bottom', 'left'] if cell_style['sides'] == "all" else cell_style['sides']
            border_style = style.borders(
                sides=sides,
                color=cell_style['color'],
                style=cell_style['style'],
                weight=cell_style['weight']
            )
            self.gt_object = self.gt_object.tab_style(
                style=border_style,
                locations=loc.body(
                    columns=[cell_style['target_var']],
                    rows=[cell_style['rowid']]
                )
            )

    def _process_row(self, row):
        """
        Processes a single row of styling instructions and updates the internal
        styling dictionaries and GT object accordingly.

        Parameters:
        -----------
        row : pandas.Series
            A series containing styling instructions for a specific cell, including
            target variable, row ID, and styling properties.

        Updates:
        --------
        - text_styles : dict
            Updates text styling properties such as weight, style, decorate, color,
            and other text-related attributes.
        - gt_object : GT
            Applies fill color styles to the GT object.
        - border_styles : dict
            Updates border styling properties including color, weight, style, and sides.
        """
        if pd.isna(row['arg_value']):
            return

        original_rowid = row['rowid']
        try:
            numeric_rowid = int(original_rowid)
            mapped_rowid = self.row_mapping.get(numeric_rowid, numeric_rowid - 1)
        except (ValueError, TypeError):
            mapped_rowid = original_rowid

        cell_key = f"{row['target_var']}_{original_rowid}"

        # Text styling
        if row['helper'] == "cell_text" and pd.notna(row['arg_value']):
            if cell_key not in self.text_styles:
                self.text_styles[cell_key] = {
                    'target_var': row['target_var'],
                    'rowid': mapped_rowid,
                    'props': {}
                }
            if row['styling_arg'] == "weight":
                self.text_styles[cell_key]['props']['weight'] = row['arg_value']
            elif row['styling_arg'] == "style":
                self.text_styles[cell_key]['props']['style'] = row['arg_value']
            elif row['styling_arg'] == "decorate":
                self.text_styles[cell_key]['props']['decorate'] = row['arg_value']
            elif row['styling_arg'] == "color":
                self.text_styles[cell_key]['props']['color'] = row['arg_value']
            elif row['styling_arg'] in ["font", "size", "align", "v_align", "transform", "whitespace", "stretch"]:
                self.text_styles[cell_key]['props'][row['styling_arg']] = row['arg_value']

        # Fill color
        if row['helper'] == "cell_fill" and pd.notna(row['arg_value']):
            fill_style = style.fill(row['arg_value'])
            self.gt_object = self.gt_object.tab_style(
                style=fill_style,
                locations=loc.body(
                    columns=[row['target_var']],
                    rows=[mapped_rowid]
                )
            )

        # Border styling
        if row['helper'] == "cell_borders" and pd.notna(row['arg_value']):
            if cell_key not in self.border_styles:
                self.border_styles[cell_key] = {
                    'target_var': row['target_var'],
                    'rowid': mapped_rowid,
                    'sides': [],
                    'color': "#000000",
                    'style': "solid",
                    'weight': px(1)
                }
            if row['border_property'] == "color":
                self.border_styles[cell_key]['color'] = row['arg_value']
            elif row['border_property'] == "weight":
                self.border_styles[cell_key]['weight'] = px(float(row['arg_value'])) if row['arg_value'] else px(1)
            elif row['border_property'] == "style":
                self.border_styles[cell_key]['style'] = row['arg_value']
            elif row['border_property'] == "sides":
                side = row.get('border_side')
                if side == "all" or not side:
                    self.border_styles[cell_key]['sides'] = "all"
                elif self.border_styles[cell_key]['sides'] != "all":
                    if side not in self.border_styles[cell_key]['sides']:
                        self.border_styles[cell_key]['sides'].append(side)

    def apply_formatting(self):
        """
        Applies formatting to the GT object by processing each row of
        formatting instructions and updating the internal styling dictionaries.

        Iterates over the rows in the format_ready DataFrame, processes each
        row to update text and border styles, and applies these styles to the
        GT object.

        Returns:
        --------
        GT
            The GT object with applied text and border styles.
        """
        for _, row in self.format_ready.iterrows():
            self._process_row(row)

        self._apply_text_styles()
        self._apply_border_styles()

        return self.gt_object