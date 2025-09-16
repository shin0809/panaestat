import logging
import csv
import os
import zipfile
import datetime
import textwrap
from constants import LOG_DIR, LOGS_ZIP_PATH, MAX_LOGS_DIR_SIZE_MB

# ======== カスタムログレベル定義 ========
CSV_INFO_LEVEL = 15
CSV_ERROR_LEVEL = 45
logging.addLevelName(CSV_INFO_LEVEL, "INFO")
logging.addLevelName(CSV_ERROR_LEVEL, "ERROR")

def csv_info_log(self, message, *args, **kwargs):
    if self.isEnabledFor(CSV_INFO_LEVEL):
        self._log(CSV_INFO_LEVEL, message, args, **kwargs)

def csv_error_log(self, message, *args, **kwargs):
    if self.isEnabledFor(CSV_ERROR_LEVEL):
        self._log(CSV_ERROR_LEVEL, message, args, **kwargs)

logging.Logger.csv_info = csv_info_log
logging.Logger.csv_error = csv_error_log

def csv_info_root(message, *args, **kwargs):
    logging.getLogger().csv_info(message, *args, **kwargs)

def csv_error_root(message, *args, **kwargs):
    logging.getLogger().csv_error(message, *args, **kwargs)

logging.csv_info = csv_info_root
logging.csv_error = csv_error_root
# ======================================

# 日本時間（JST）の設定
JST = datetime.timezone(datetime.timedelta(hours=9))

os.makedirs(LOG_DIR, exist_ok=True)

def get_logs_dir_size():
    total_size = sum(
        os.path.getsize(os.path.join(LOG_DIR, file))
        for file in os.listdir(LOG_DIR)
        if os.path.isfile(os.path.join(LOG_DIR, file))
    )
    return total_size / (1024 * 1024)

def _cleanup_old_logs():
    total_size = get_logs_dir_size()
    log_files = []

    for root, _, files in os.walk(LOG_DIR):
        for file in files:
            file_path = os.path.join(root, file)
            if file != "logs.zip":
                log_files.append((file_path, os.path.getmtime(file_path)))

    while total_size > MAX_LOGS_DIR_SIZE_MB:
        if not log_files:
            break
        log_files.sort(key=lambda x: x[1])
        oldest_file, _ = log_files.pop(0)
        total_size -= os.path.getsize(oldest_file) / (1024 * 1024)
        os.remove(oldest_file)

def _get_log_file(prefix):
    base_name = f"{prefix}_{datetime.datetime.now(JST).strftime('%Y-%m-%d')}"
    index = 1
    while True:
        file_name = os.path.join(LOG_DIR, f"{base_name}_{index}.csv")
        if not os.path.exists(file_name):
            with open(file_name, "a", encoding="utf-8-sig"):
                pass
            return file_name
        elif os.path.getsize(file_name) < 10 * 1024 * 1024:
            return file_name
        index += 1

def zip_logs():
    if not os.path.exists(LOG_DIR):
        return None

    _cleanup_old_logs()

    if os.path.exists(LOGS_ZIP_PATH):
        os.remove(LOGS_ZIP_PATH)

    with zipfile.ZipFile(LOGS_ZIP_PATH, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(LOG_DIR):
            for file in files:
                if file == "logs.zip":
                    continue
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, LOG_DIR)
                zipf.write(file_path, arcname)

    return LOGS_ZIP_PATH if os.path.exists(LOGS_ZIP_PATH) else None

def get_log_files():
    return [
        os.path.join(LOG_DIR, file)
        for file in os.listdir(LOG_DIR)
        if os.path.isfile(os.path.join(LOG_DIR, file)) and file != "logs.zip"
    ]

def get_oldest_log():
    log_files = get_log_files()
    if log_files:
        log_files.sort(key=os.path.getmtime)
        return log_files[0]
    return None

def delete_oldest_log():
    oldest_file = get_oldest_log()
    if oldest_file:
        os.remove(oldest_file)
        return oldest_file
    return None

def delete_all_logs():
    for file in get_log_files():
        os.remove(file)

class DailyCSVLogger(logging.Handler):
    """CSVログ用の汎用ハンドラー（INFO・ERRORどちらも処理）"""
    def __init__(self):
        super().__init__(level=min(CSV_INFO_LEVEL, CSV_ERROR_LEVEL))
        self.addFilter(lambda record: record.levelno in (CSV_INFO_LEVEL, CSV_ERROR_LEVEL))

    def emit(self, record):
        _cleanup_old_logs()

        # 出力ファイルをログレベルで切り替え
        if record.levelno == CSV_ERROR_LEVEL:
            log_file = _get_log_file("error_logs")
        else:
            log_file = _get_log_file("logs")

        # 通常ログレベル名（INFO/ERROR）として扱う
        if record.levelno == CSV_INFO_LEVEL:
            level_name = "INFO"
        elif record.levelno == CSV_ERROR_LEVEL:
            level_name = "ERROR"
        else:
            level_name = record.levelname

        from session import get_user_name
        user_name = get_user_name() or "Unknown"

        # ログメッセージ（CSV用には levelname を含めない）
        log_message = record.getMessage()

        log_entry = [datetime.datetime.now(JST).isoformat(), level_name, user_name, log_message]

        existing_logs = []
        if os.path.exists(log_file):
            with open(log_file, mode='r', encoding='utf-8-sig') as f:
                reader = csv.reader(f)
                existing_logs = list(reader)

        max_line_length = 100
        wrapped_message = textwrap.wrap(log_message, max_line_length)

        new_entries = [[log_entry[0], log_entry[1], log_entry[2], wrapped_message[0]]]
        for extra_line in wrapped_message[1:]:
            new_entries.append(["", "", "", extra_line])

        existing_logs = new_entries + existing_logs

        with open(log_file, mode='w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerows(existing_logs)
            f.flush()
            os.fsync(f.fileno())

# ======== ログ設定 ========
# CSVにはレベル名含めない
csv_formatter = logging.Formatter('%(message)s')
csv_handler = DailyCSVLogger()
csv_handler.setFormatter(csv_formatter)

# ターミナル出力（全レベル表示）
console_formatter = logging.Formatter('%(levelname)s - %(message)s')
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(console_formatter)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.handlers.clear()
logger.addHandler(csv_handler)
logger.addHandler(console_handler)
logger.propagate = False