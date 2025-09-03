import logging

from langchain_core.tools import tool

from api import fetch_estat_data
from utils import delete_newlines

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

    logging.info(f"Fetching estat data by URL: {url}")
    
    # URLに'statdisp_id='が含まれているか確認
    statsDataId = _extract_statdisp_id(url)
    if statsDataId is None:
        return "指定されたe-statのURLから統計表IDを取得することに失敗しました。"
    
    try:
        response = fetch_estat_data(statsDataId)
        return response
    except Exception:
        return "指定されたe-statのURLから統計データを取得することに失敗しました。"
    

def _extract_statdisp_id(url: str) -> str:
    """
    e-Stat URLからstatdisp_idを抽出します
    
    Args:
        url: e-StatのURL
        
    Returns:
        statdisp_id: 抽出されたstatdisp_id
    """
    # URLに'statdisp_id='が含まれているか確認
    if 'statdisp_id=' not in url:
        return None
    
    # 'statdisp_id='以降の文字列を取得
    statdisp_id = url.split('statdisp_id=')[1]
    
    # '&'で区切られている場合は、最初の部分だけを取得
    if '&' in statdisp_id:
        statdisp_id = statdisp_id.split('&')[0]
        
    # 改行コードを削除
    statdisp_id = delete_newlines(statdisp_id)
        
    return statdisp_id