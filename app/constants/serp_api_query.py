from enum import Enum

class SerpApiQuery(Enum):
    API_URL = "site:https://www.e-stat.go.jp/stat-search? inurl:statdisp_id="
    EXCEL_URL = "site:https://www.e-stat.go.jp/stat-search/file-download? inurl:fileKind=0"
    CSV_URL = "site:https://www.e-stat.go.jp/stat-search/file-download? inurl:fileKind=1"
    PDF_URL = "site:https://www.e-stat.go.jp/stat-search/file-download? inurl:fileKind=2"