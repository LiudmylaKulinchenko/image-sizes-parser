import os
import configparser

import pandas as pd
from dotenv import load_dotenv

from logger_setup import logger

load_dotenv()

SHEET_ID = os.getenv("GOOGLE_SHEET_ID")

config = configparser.ConfigParser()
config.read("../config.ini")

SHEET_NAME = config["GoogleSheetConfig"]["sheet_name"]
IMAGE_SIZES_RESULT_FILE = config["GoogleSheetConfig"]["image_sizes_result_file"]
SIZE_COLUMN_NAME = config["GoogleSheetConfig"]["size_column_name"]


def get_sheet_data() -> pd.DataFrame:
    """Upload data from sheet"""
    url = (
        f"https://docs.google.com/spreadsheets/d/"
        f"{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}"
    )

    df = pd.read_csv(url)

    logger.info("Successfully retrieved Sheet data and created DataFrame")

    return df


def get_image_urls() -> tuple[pd.DataFrame, int]:
    """Return tuple with DataFrame of image_urls and DataFrame size"""
    images_df = get_sheet_data()
    image_urls_df = images_df["image_url"][1:]

    return image_urls_df, image_urls_df.size


def split_urls_into_package(df: pd.DataFrame, size: int) -> dict:
    """
    The generator divides the urls into dictionaries (packs) <= 10_000 each
    """
    pack_size = 10_000
    packs_amount = size // pack_size + 1

    for i in range(packs_amount):
        yield df[pack_size * i : pack_size * (i + 1)].to_dict()

    logger.info(f"Urls splitted into {packs_amount} packs")

    return df[pack_size * packs_amount :].to_dict()


def create_excel_file_with_image_sizes(sizes: dict):
    """Create excel fiel with image sizes data"""

    sizes_df = pd.DataFrame.from_dict(sizes, orient="index", columns=[SIZE_COLUMN_NAME])
    images_df = get_sheet_data()
    images_df.update({SIZE_COLUMN_NAME: sizes_df[SIZE_COLUMN_NAME]})

    with pd.ExcelWriter(
        f"../data/{IMAGE_SIZES_RESULT_FILE}", engine="openpyxl"
    ) as writer:
        images_df.to_excel(writer, sheet_name=SHEET_NAME, index=False)

    logger.info("Succesfully created sizes excel file")


if __name__ == "__main__":
    print(get_sheet_data())
