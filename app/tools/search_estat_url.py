import re
import json
from typing import Union

from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from constants import FETCH_DATA_TYPE, SerpApiQuery, SEARCH_ESTAT_URL_PROMPT, FILTER_ESTAT_URL_PROMPT
from api import fetch_estat_urls
from session import get_fetch_data_type, get_model_name, set_llm_input_cost, set_llm_output_cost
from utils import set_llm

@tool
def search_estat_url(user_query: str) -> Union[dict, str]:
    """
    e-Statのサイト内検索を行い、検索結果上位のサイト20件から、
    ユーザーの意図に最も合致する上位5件を選んで内容を整形して返却します。
  
    用途：
        ユーザーが何かの統計データを探しているときに使用します。
        （ユーザーから特定のestatのURLを指定された時や統計表IDを指定された時には、このツールを使用しないでください）
    Args:
        user_query (str): ユーザーの検索キーワード

    Returns:
        str: 説明文
    """
    
    # 検索クエリの生成
    prompt = ChatPromptTemplate.from_template(SEARCH_ESTAT_URL_PROMPT)
    chain = prompt | set_llm(get_model_name()) | StrOutputParser()
    search_query = chain.invoke({"user_query": user_query}).strip()
    
    from services import calc_input_cost_from_prompt, calc_output_cost_from_result
    # 入力コストを計算
    input_cost = calc_input_cost_from_prompt(user_query, get_model_name())
    set_llm_input_cost(input_cost, get_model_name())
    
    # 出力コストを計算
    output_cost = calc_output_cost_from_result(search_query, get_model_name())
    set_llm_output_cost(output_cost, get_model_name())
    
    serp_api_query = _set_serp_api_query(get_fetch_data_type(), search_query)
  
    # serp_apiを呼び出す
    try:
        response = fetch_estat_urls(serp_api_query)
    except Exception:
        return "検索中にエラーが発生しました。"
  
    if len(response) == 0:
        return "検索結果が見つかりませんでした。"

    # 検索結果を関連度上位5件に絞り込む
    prompt = ChatPromptTemplate.from_template(FILTER_ESTAT_URL_PROMPT)
    chain = prompt | set_llm(get_model_name()) | StrOutputParser()
    filtered_results = chain.invoke({"user_query": user_query, "search_results": json.dumps(response, ensure_ascii=False)})

    # 検索結果からURLを抽出
    urls = _extract_urls(filtered_results)

    # 入力コストを計算
    input_cost = calc_input_cost_from_prompt(user_query, get_model_name())
    set_llm_input_cost(input_cost, get_model_name())
    
    # 出力コストを計算
    output_cost = calc_output_cost_from_result(filtered_results, get_model_name())
    set_llm_output_cost(output_cost, get_model_name())

    return {
        "search_results": filtered_results,
        "urls": urls
    }

def _set_serp_api_query(fetch_data_type: str, search_query: str) -> str:
    """
    serp_apiのクエリを生成します。
    """
    if fetch_data_type == FETCH_DATA_TYPE[0]:
        return f"{SerpApiQuery.API_URL.value} {search_query}"
    elif fetch_data_type == FETCH_DATA_TYPE[1]:
        return f"{SerpApiQuery.EXCEL_URL.value} {search_query}"
    elif fetch_data_type == FETCH_DATA_TYPE[2]:
        return f"{SerpApiQuery.CSV_URL.value} {search_query}"
    elif fetch_data_type == FETCH_DATA_TYPE[3]:
        return f"{SerpApiQuery.PDF_URL.value} {search_query}"
    else:
        return None

def _extract_urls(text: str) -> list:
    """
    テキストからURLを抽出します。
    """
    # Markdownリンク形式と単純なURL形式の両方に対応
    urls = re.findall(r'URL:\s*(?:\[.*?\]\((http[s]?://\S+)\)|(http[s]?://\S+))', text)
    # URLをフラットなリストにする
    return [url[0] or url[1] for url in urls]