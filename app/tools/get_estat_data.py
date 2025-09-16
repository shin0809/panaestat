import logging

from langchain_core.tools import tool

from api import fetch_estat_data
from utils import delete_newlines, extract_statdisp_id

@tool
def get_estat_data_by_id(statsDataId: str) -> str:
    """
    e-Statの統計データを取得します。
    
    用途：
        ユーザーが統計表IDを指定した時に使用します。
    Args:
        statsDataId: 統計データID
    
    Returns:
        統計データのJSON
    """

    # 改行コードを削除
    statsDataId = delete_newlines(statsDataId)
    
    try:
        response = fetch_estat_data(statsDataId)
        return response
    except Exception:
        return "指定された統計表IDから統計データを取得することに失敗しました。"
    
@tool
def get_estat_data_by_url(url: str) -> str:
    """
    e-Statの統計データを取得します。
    
    用途：
        ユーザーがestatのURLを指定した時に使用します。
    Args:
        url: 統計データURL
    
    Returns:
        統計データのJSON
    """

    logging.csv_info(f"Fetching estat data by URL: {url}")
    
    # URLに'statdisp_id='が含まれているか確認
    statsDataId = extract_statdisp_id(url)
    if statsDataId is None:
        return "指定されたe-statのURLから統計表IDを取得することに失敗しました。"
    
    try:
        response = fetch_estat_data(statsDataId)
        return response
    except Exception:
        return "指定されたe-statのURLから統計データを取得することに失敗しました。"