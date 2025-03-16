from typing import Union
import pandas as pd
from great_tables import GT
import logging
from forgts.get_formatting import ExcelFormatter
from forgts.translate_formatting import ExcelFormattingTranslator
from forgts.styling import GTStyler

"""
forgts - Format Great Tables from Spreadsheets

A package that extracts formatting from Excel files and applies it to great_tables objects.
"""

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def format_gt_from_excel(excel_path: str, sheet: Union[str, int, None] = 0) -> GT:
    """
    Reads an Excel file, extracts formatting information, translates it into a compatible format for a GT object,
    and applies this formatting to the GT object.

    :param excel_path: Path to the Excel file.
    :param sheet: Optional sheet name or index. Defaults to the first sheet if not provided.
    :return: Formatted GT object.
    :raises FileNotFoundError: If the Excel file is not found.
    :raises ValueError: If the Excel sheet is empty or malformed.
    :raises Exception: For other errors during file reading or formatting initialization.
    """
    logger.info("Starting the formatting process from Excel.")

    if sheet is not None and not isinstance(sheet, (str, int)):
        raise ValueError("The sheet parameter must be a string or an integer.")

    try:
        with pd.ExcelFile(excel_path) as xls:
            df = pd.read_excel(xls, sheet_name=sheet)
    except FileNotFoundError:
        raise FileNotFoundError(f"The file at {excel_path} was not found.")
    except ValueError as e:
        raise ValueError(f"Value error while reading the Excel file: {e}")
    except pd.errors.EmptyDataError:
        raise ValueError("The Excel sheet is empty or malformed.")
    except pd.errors.ParserError as e:
        raise ValueError(f"Parser error while reading the Excel file: {e}")
    except Exception as e:
        raise Exception(f"An unexpected error occurred while reading the Excel file: {e}")

    if df.empty:
        raise ValueError("The Excel sheet is empty or malformed.")

    gt_object = GT(df)

    try:
        formatter = ExcelFormatter(excel_path, sheet)
    except ValueError as e:
        raise ValueError(f"Value error while initializing the ExcelFormatter: {e}")
    except Exception as e:
        raise Exception(f"An unexpected error occurred while initializing the ExcelFormatter: {e}")

    logger.info("Extracting formatting information.")
    raw_formatting = formatter.run()

    translator = ExcelFormattingTranslator(raw_formatting)
    logger.info("Translating formatting to great_tables format.")
    gt_formatting = translator.translate()

    styler = GTStyler(gt_object, gt_formatting)
    logger.info("Applying formatting to the GT object.")
    formatted_gt = styler.apply_formatting()

    logger.info("Formatting process completed.")
    return formatted_gt


# Export main function and module components
__all__ = [
    'format_gt_from_excel',
    'ExcelFormatter',
    'ExcelFormattingTranslator',
    'GTStyler'
]