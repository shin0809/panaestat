import logging

import pandas as pd
import streamlit as st
from langchain_core.tools import tool
from pandasai import Agent
from pandasai.llm import OpenAI
from pandasai.helpers.openai_info import get_openai_callback

from constants import PANDAS_AI_ERROR_MESSAGE, SAVE_DATA_OPTIONS, FORMAT_ESTAT_DATA_PROMPT
from views import StatDataViewer
from utils import is_estat_data, GenerativeAIModel
from session import set_agent_message, get_save_data_option, set_llm_input_cost, set_llm_output_cost

@tool
def format_estat_data(user_query: str) -> str:
    """
    e-Statの統計データを整形します。

    Args:
        data (str): estatの統計データ

    Returns:
        str: 整形した統計データ
    """
    
    if get_save_data_option() is SAVE_DATA_OPTIONS[1]:
        return "過去に表示した統計データを整形したい場合は、「統計データの保存（セッション内）」で「保存する」を選択してください。"

    data = None
    for message in reversed(st.session_state.messages):
        if is_estat_data(message['content']):
            data = message['content']
            break
    
    if data is None:
        return "統計するデータが見つかりませんでした。"

    viewer = StatDataViewer(data, len(st.session_state.messages))
    viewer.process_data()
    
    # ユーザーが選択した表示形式を設定
    display_type = message.get("display_type")
    if display_type is not None:
        viewer.display_type = display_type

    agent = Agent(
        viewer.df,
        config={
            "llm": OpenAI(),
            "custom_whitelisted_dependencies": ["plotly"],
        }
    )
    with get_openai_callback() as cb:
        result = agent.chat(FORMAT_ESTAT_DATA_PROMPT.format(user_query=user_query))
        
        # logging.info(f"response: {result}")
        
        prompt_tokens = cb.prompt_tokens
        completion_tokens = cb.completion_tokens
        
        from services import calc_input_cost, calc_output_cost
        # 入力コストを計算
        # OpenAIのどのモデルを使用しているか不明なため、GPT_4Oを計算
        input_cost = calc_input_cost(prompt_tokens, GenerativeAIModel.GPT_4O.value)
        set_llm_input_cost(input_cost, GenerativeAIModel.GPT_4O.value)
                
        output_cost = calc_output_cost(completion_tokens, GenerativeAIModel.GPT_4O.value)
        set_llm_output_cost(output_cost, GenerativeAIModel.GPT_4O.value)
    
    if PANDAS_AI_ERROR_MESSAGE in result or not isinstance(result, pd.DataFrame):
        return "ファイルの分析中にエラーが発生しました。"
    else:
        viewer.set_df(result)
        set_agent_message(
            content=viewer,
            is_formatted=True,
            is_stat_data=True,
        )
        return "stat_data_viewer"