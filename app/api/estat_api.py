import logging
import requests
import json
import os

from session import get_estat_data_limit

def fetch_estat_data(statsDataId: str):
    """
    e-Statの統計データを取得します。
    
    Args:
        statsDataId: 統計データID
    
    Returns:
        統計データのJSON
    """
    
    endpoint = "https://api.e-stat.go.jp/rest/3.0/app/json/getStatsData"
    # appIdを取得して利用する
    app_id = os.getenv("APP_ID")
    
    max_number = get_estat_data_limit()
    
    params = {
        "appId": app_id,
        "statsDataId": statsDataId,
        "startPosition": 1,
        "limit": max_number,
        "lang": "J"
    }
    try:
        logging.csv_info(f"Fetching data for statsDataId: {statsDataId}")
        response = requests.get(endpoint, params=params)
        response.raise_for_status()
        data = response.json()
        #logging.csv_info(f"Fetched data: {data}")
        
        # ステータスチェックを行う
        # estatの統計データ取得APIではデータが見つからなかった場合でもHTTP Statusは200で返却される。
        # 返却データ　内のSTATUSが0であることで取得成功となっている。
        if data.get("GET_STATS_DATA", {}).get("RESULT", {}).get("STATUS") == 0:
            total_data_count = data.get("GET_STATS_DATA", {}).get("STATISTICAL_DATA", {}).get("RESULT_INF", {}).get("TOTAL_NUMBER")
            logging.csv_info(f"Total data count: {total_data_count}")
            if total_data_count > max_number:
                return (
                    f"データが**{max_number:,}**件以上({total_data_count:,}件)あるため、この機能では扱えません。  \n"
                    "e-Statのデータ取得上限を上げるか、ExcelやCSVなどでのデータの取得をご検討ください。  \n"
                    "※取得するデータ量が多い場合、通信に時間がかかったり、ブラウザの動作が重くなることがあるため、ご注意ください。"
                )
            
            return data
        else:
            error_msg = data.get("GET_STATS_DATA", {}).get("RESULT", {}).get("ERROR_MSG")
            raise Exception(error_msg)
    except requests.exceptions.RequestException as e:
        logging.csv_error(f"APIリクエストでエラーが発生しました: {str(e)}")
        raise Exception(f"APIリクエストエラー: {str(e)}")
    except json.JSONDecodeError:
        logging.csv_error(f"JSONのデコードでエラーが発生しました: {str(e)}")
        raise Exception(f"JSONデコードエラー: {str(e)}")
    except Exception as e:
        logging.csv_error(f"予期せぬエラーが発生しました: {str(e)}")
        raise Exception(f"その他のエラー: {str(e)}")

def get_estat_data_count(statsDataId: str):
    """
    e-Statの統計データの数を取得します。
    """
    
    endpoint = "https://api.e-stat.go.jp/rest/3.0/app/json/getMetaInfo"
    # appIdを取得して利用する
    app_id = os.getenv("APP_ID")
    
    params = {
        "appId": app_id,
        "statsDataId": statsDataId,
        "explanationGetFlg": "N",
        "lang": "J"
    }
    
    try:
        logging.csv_info(f"Fetching meta info for statsDataId: {statsDataId}")
        response = requests.get(endpoint, params=params)
        response.raise_for_status()
        data = response.json()
    
        # ステータスチェックを行う
        # estatの統計データ取得APIではデータが見つからなかった場合でもHTTP Statusは200で返却される。
        # 返却データ　内のSTATUSが0であることで取得成功となっている。
        if data.get("GET_META_INFO", {}).get("RESULT", {}).get("STATUS") == 0:
            return data.get("GET_META_INFO", {}).get("METADATA_INF", {}).get("TABLE_INF", {}).get("OVERALL_TOTAL_NUMBER")
        else:
            error_msg = data.get("GET_META_INFO", {}).get("RESULT", {}).get("ERROR_MSG")
            raise Exception(error_msg)
    except requests.exceptions.RequestException as e:
        logging.csv_error(f"APIリクエストでエラーが発生しました: {str(e)}")
        raise Exception(f"APIリクエストエラー: {str(e)}")
    except json.JSONDecodeError:
        logging.csv_error(f"JSONのデコードでエラーが発生しました: {str(e)}")
        raise Exception(f"JSONデコードエラー: {str(e)}")
    except Exception as e:
        logging.csv_error(f"予期せぬエラーが発生しました: {str(e)}")
        raise Exception(f"その他のエラー: {str(e)}")
