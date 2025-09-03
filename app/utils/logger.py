import logging
import csv
import os
import zipfile
import datetime
import textwrap
from constants import LOG_DIR, LOGS_ZIP_PATH, MAX_LOGS_DIR_SIZE_MB

# 日本時間（JST）の設定
JST = datetime.timezone(datetime.timedelta(hours=9))

os.makedirs(LOG_DIR, exist_ok=True)

def get_logs_dir_size():
    """logs フォルダの現在の総容量（MB）を取得"""
    total_size = sum(
        os.path.getsize(os.path.join(LOG_DIR, file))
        for file in os.listdir(LOG_DIR)
        if os.path.isfile(os.path.join(LOG_DIR, file))
    )
    return total_size / (1024 * 1024)  # MB単位で返す

def _cleanup_old_logs():
    """logsフォルダの総容量が制限を超えたら、古いファイルから削除する"""
    total_size = get_logs_dir_size()
    log_files = []

    for root, _, files in os.walk(LOG_DIR):
        for file in files:
            file_path = os.path.join(root, file)
            if file != "logs.zip":  # ZIPファイルは削除しない
                log_files.append((file_path, os.path.getmtime(file_path)))

    while total_size > MAX_LOGS_DIR_SIZE_MB:
        if not log_files:
            break

        log_files.sort(key=lambda x: x[1])  # 最終更新日時でソート
        oldest_file, _ = log_files.pop(0)
        total_size -= os.path.getsize(oldest_file) / (1024 * 1024)
        os.remove(oldest_file)

def _get_log_file():
    """日本時間の現在の日付でログファイルを取得（サイズ超過で分割）"""
    base_name = f"logs_{datetime.datetime.now(JST).strftime('%Y-%m-%d')}"

    index = 1
    while True:
        file_name = os.path.join(LOG_DIR, f"{base_name}_{index}.csv")
        if not os.path.exists(file_name):
            with open(file_name, "a", encoding="utf-8-sig"):
                pass
            return file_name
        elif os.path.getsize(file_name) < 10 * 1024 * 1024:  # 10MB未満なら使用
            return file_name
        index += 1

def zip_logs():
    """logs.zip を作成"""
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
    """logsフォルダ内のログファイル一覧を取得（logs.zip を除外）"""
    return [
        os.path.join(LOG_DIR, file)
        for file in os.listdir(LOG_DIR)
        if os.path.isfile(os.path.join(LOG_DIR, file)) and file != "logs.zip"
    ]

def get_oldest_log():
    """最も古いログファイルを取得（logs.zip を除外）"""
    log_files = get_log_files()
    if log_files:
        log_files.sort(key=os.path.getmtime)
        return log_files[0]
    return None

def delete_oldest_log():
    """最も古いログファイルを削除（logs.zip は削除しない）"""
    oldest_file = get_oldest_log()
    if oldest_file:
        os.remove(oldest_file)
        return oldest_file
    return None

def delete_all_logs():
    """すべてのログを削除（logs.zip を除外）"""
    for file in get_log_files():
        os.remove(file)

class DailyCSVLogger(logging.Handler):
    """日付ごとのCSVログを管理するハンドラー"""
    def emit(self, record):
        _cleanup_old_logs()

        log_file = _get_log_file()
        log_message = self.format(record)
        
        from session import get_user_name
        user_name = get_user_name() or "Unknown"

        log_entry = [datetime.datetime.now(JST).isoformat(), record.levelname, user_name, log_message]

        # 既存のログを読み込み（なければ空リスト）
        existing_logs = []
        if os.path.exists(log_file):
            with open(log_file, mode='r', encoding='utf-8-sig') as f:
                reader = csv.reader(f)
                existing_logs = list(reader)

        # **長いログを複数行に分割**
        max_line_length = 100  # 1行の最大文字数
        wrapped_message = textwrap.wrap(log_message, max_line_length)

        # **分割されたログエントリを作成**
        new_entries = [[log_entry[0], log_entry[1], log_entry[2], wrapped_message[0]]]
        for extra_line in wrapped_message[1:]:
            new_entries.append(["", "", "", extra_line])

        # 新しいログを先頭に追加
        existing_logs = new_entries + existing_logs

        # CSVファイルを上書きして、新しい順に保存（utf-8-sig）
        with open(log_file, mode='w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerows(existing_logs)
            f.flush()
            os.fsync(f.fileno())

# ログ設定
formatter = logging.Formatter('%(levelname)s - %(message)s')

# CSVログハンドラー
csv_handler = DailyCSVLogger()
csv_handler.setFormatter(formatter)

# コンソールログハンドラー
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.handlers.clear()
logger.addHandler(csv_handler)
logger.addHandler(console_handler)
logger.propagate = False
