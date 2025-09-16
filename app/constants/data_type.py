from enum import Enum
class FetchDataType(Enum):
    ESTAT_API = "チャット表示用データ"
    EXCEL = "Excel"
    CSV = "CSV"
    PDF = "PDF"
    
FETCH_DATA_TYPE = [
    FetchDataType.ESTAT_API.value,
    FetchDataType.EXCEL.value,
    FetchDataType.CSV.value,
    FetchDataType.PDF.value
]