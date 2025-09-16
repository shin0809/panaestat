from typing import List, Union

from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from constants import FetchDataType, SerpApiQuery, SEARCH_ESTAT_URL_PROMPT
from api import fetch_estat_urls
from session import get_fetch_data_type, get_model_name, set_llm_input_cost, set_llm_output_cost
from utils import set_llm

@tool
def search_estat_url(user_query: str) -> Union[List[List[dict]], str]:
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
    prompt_text = SEARCH_ESTAT_URL_PROMPT.format(user_query=user_query)
    input_cost = calc_input_cost_from_prompt(prompt_text, get_model_name())
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

    grouped_results = []
    for i in range(0, len(response), 5):
        group = response[i:i+5]
        grouped_results.append(group)

    return grouped_results

def _set_serp_api_query(fetch_data_type: str, search_query: str) -> str:
    """
    serp_apiのクエリを生成します。
    """
    if fetch_data_type == FetchDataType.ESTAT_API.value:
        return f"{SerpApiQuery.API_URL.value} {search_query}"
    elif fetch_data_type == FetchDataType.EXCEL.value:
        return f"{SerpApiQuery.EXCEL_URL.value} {search_query}"
    elif fetch_data_type == FetchDataType.CSV.value:
        return f"{SerpApiQuery.CSV_URL.value} {search_query}"
    elif fetch_data_type == FetchDataType.PDF.value:
        return f"{SerpApiQuery.PDF_URL.value} {search_query}"
    else:
        return None