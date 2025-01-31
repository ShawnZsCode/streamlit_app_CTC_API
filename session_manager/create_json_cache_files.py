"""Helper functions to generate the local cache files using the APICore Connection"""

# import time
import json
from datetime import datetime
# from multiprocessing import Pool, cpu_count


# from Logging.ctc_logging import CTCLog
from utils.file_utils import read_file_json, write_file_json

JSON_SETTINGS = read_file_json("session_manager\\Settings.json")

CURRENT_DATE_TIME = datetime.now().strftime("%Y-%m-%d_%H-%M")

# PROC_ALLOWED = int(round(cpu_count() / 2.5, 0))


def get_base_json(file_name: str, function, date_time: str = CURRENT_DATE_TIME) -> None:
    records = function()
    records_json = json.loads(records.model_dump_json())
    write_file_json(
        stream=records_json,
        file_name=file_name.title(),
        folder=date_time,
    )


def get_detailed_json(key: str, get_function, item, date_time: str = CURRENT_DATE_TIME):
    record = get_function(item=item)
    record_json = json.loads(record.model_dump_json())
    write_file_json(
        stream=record_json,
        file_name=f"{key.title()}_{record.id}",
        folder=date_time,
    )


# Prevent running from this file
if __name__ == "__main__":
    pass
