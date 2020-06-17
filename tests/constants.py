import os

# import constants from src
from src.constants import (
    REPO_PATH,
    INPUT_FOLDER,
    OUTPUT_FOLDER,
    OUTPUT_SUFFIX,
    DEFAULT_INPUT_PATH,
    DEFAULT_OUTPUT_PATH,
    PATH_INPUT_FILE,
    PATH_INPUT_FOLDER,
    PATH_OUTPUT_FOLDER,
    PATH_OUTPUT_FOLDER_INPUTS,
    INPUT_TYPE,
    OVERWRITE,
    DISPLAY_OUTPUT,
    JSON_FNAME,
    JSON_EXT,
    CSV_ELEMENTS,
    INPUTS_COPY,
    CSV_FNAME,
    CSV_EXT,
    REQUIRED_CSV_FILES,
    REQUIRED_CSV_PARAMETERS,
    KPI_SCALARS,
    PDF_REPORT,
    DICT_PLOTS,
    TYPE_DATETIMEINDEX,
    TYPE_DATAFRAME,
    TYPE_SERIES,
    TYPE_TIMESTAMP,
    TYPE_BOOL,
    TYPE_STR,
    TYPE_NONE,
    PATHS_TO_PLOTS,
)

TESTS_ON_MASTER = "master"
TESTS_ON_DEV = "dev"

EXECUTE_TESTS_ON = os.environ.get("EXECUTE_TESTS_ON", "skip")
CI_TESTS = os.environ.get("CI_TESTS", False)
TEST_REPO_PATH = os.path.dirname(__file__)

DUMMY_CSV_PATH = os.path.join(TEST_REPO_PATH, "test_data")

CSV_PATH = os.path.join(TEST_REPO_PATH, INPUT_FOLDER, CSV_ELEMENTS)
JSON_PATH = os.path.join(TEST_REPO_PATH, INPUT_FOLDER, JSON_FNAME)

# path of the file created automatically by
JSON_CSV_PATH = os.path.join(TEST_REPO_PATH, INPUT_FOLDER, CSV_ELEMENTS, CSV_FNAME)

# folder to store input directory for tests
TEST_INPUT_DIRECTORY = "test_data"
