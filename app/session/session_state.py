import streamlit as st

from constants import (
    LLM_OPTIONS, 
    SAVE_DATA_OPTIONS,
    DEFAULT_ESTAT_DATA_LIMIT,
    DEFAULT_USD_JPY_RATE,
    FetchDataType
)
from utils import GenerativeAIModel

def initialize_session_state():
    if "page" not in st.session_state:
        st.session_state.page = "login"
    if "authentication_status" not in st.session_state:
        st.session_state.authentication_status = None
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "model_name" not in st.session_state:
        st.session_state.model_name = GenerativeAIModel.GPT_4O.value
    if "fetch_data_type" not in st.session_state:
        st.session_state.fetch_data_type = FetchDataType.ESTAT_API.value
    if "user_data" not in st.session_state:
        st.session_state.user_data = {
            "name": None,
            "email": None,
        }
    if "save_data_option" not in st.session_state:
        st.session_state.save_data_option = SAVE_DATA_OPTIONS[0]
    if "estat_data_limit" not in st.session_state:
        st.session_state.estat_data_limit = DEFAULT_ESTAT_DATA_LIMIT
    if "usd_jpy_rate" not in st.session_state:
        st.session_state.usd_jpy_rate = DEFAULT_USD_JPY_RATE
    if "llm_costs" not in st.session_state:
        st.session_state.llm_costs = {
            GenerativeAIModel.GPT_4O.value: {
                "input_cost": 0,
                "output_cost": 0,
            },
            GenerativeAIModel.GEMINI_PRO.value: {
                "input_cost": 0,
                "output_cost": 0,
            },
            GenerativeAIModel.CLAUDE_SONNET.value: {
                "input_cost": 0,
                "output_cost": 0,
            },
        }
    if "serp_api_results" not in st.session_state:
        st.session_state.serp_api_results = []

def set_model_name(model_name):
    if model_name == LLM_OPTIONS[0]:
        st.session_state.model_name = GenerativeAIModel.GPT_4O.value
    elif model_name == LLM_OPTIONS[1]:
        st.session_state.model_name = GenerativeAIModel.GEMINI_PRO.value
    elif model_name == LLM_OPTIONS[2]:
        st.session_state.model_name = GenerativeAIModel.CLAUDE_SONNET.value

def get_model_name():
    return st.session_state.model_name

def set_fetch_data_type(fetch_data_type):
    st.session_state.fetch_data_type = fetch_data_type

def get_fetch_data_type():
    return st.session_state.fetch_data_type

def set_user_data(name=None, email=None):
    if name is not None:
        st.session_state.user_data["name"] = name
    if email is not None:
        st.session_state.user_data["email"] = email

def get_user_name():
    if "user_data" not in st.session_state: return None
    return st.session_state.user_data.get("name")

def get_user_email():
    return st.session_state.user_data.get("email")

def get_authentication_status():
    return st.session_state.authentication_status

def set_authentication_status(status: bool):
    st.session_state.authentication_status = status

def get_page():
    return st.session_state.page

def set_page(page):
    st.session_state.page = page

def get_messages():
    return st.session_state.messages

def set_messages(messages):
    st.session_state.messages = messages

def get_save_data_option():
    return st.session_state.save_data_option

def set_save_data_option(save_data_option):
    st.session_state.save_data_option = save_data_option

def set_user_message(message):
    st.session_state.messages.append({
        "role": "user",
        "content": message,
    })

def set_agent_message(
    content,
    is_stat_data=False,
    with_file=False,
    with_btns=False,
    is_formatted=False,
    display_type=None,
):
    # 統計データでない場合
    if not is_stat_data:
        if with_btns:
            st.session_state.messages.append({
                "role": "assistant",
                "content": content,
                "with_btns": with_btns,
            })
        else:
            st.session_state.messages.append({
                "role": "assistant",
                "content": content,
            })
        return

    # 最新の統計データのみセッションに保存する場合
    if get_save_data_option() is SAVE_DATA_OPTIONS[1]:
        # 過去の統計データを削除する
        for message in st.session_state.messages:
            if message.get("is_stat_data"):
                message["content"] = "この統計データは保存されていません。"
                message["is_stat_data"] = False
    
    st.session_state.messages.append({
        "role": "assistant",
        "content": content,
        "is_stat_data": is_stat_data,
        "with_file": with_file,
        "with_btns": with_btns,
        "display_type": display_type,
        "is_formatted": is_formatted,
    })
    
def get_estat_data_limit():
    return st.session_state.estat_data_limit if st.session_state.estat_data_limit is not None else DEFAULT_ESTAT_DATA_LIMIT

def set_estat_data_limit(estat_data_limit: int):
    st.session_state.estat_data_limit = estat_data_limit
    
def get_usd_jpy_rate():
    return st.session_state.usd_jpy_rate

def set_usd_jpy_rate(usd_jpy_rate: int):
    previous_usd_jpy_rate = get_usd_jpy_rate() if get_usd_jpy_rate() is not None else DEFAULT_USD_JPY_RATE
    
    # レート変更によるコスト変更
    llm_costs = get_llm_costs()
    for model_name in llm_costs.keys():
        llm_costs[model_name]["input_cost"] = llm_costs[model_name]["input_cost"] / previous_usd_jpy_rate * usd_jpy_rate
        llm_costs[model_name]["output_cost"] = llm_costs[model_name]["output_cost"] / previous_usd_jpy_rate * usd_jpy_rate
    
    set_llm_costs(llm_costs)
    st.session_state.usd_jpy_rate = usd_jpy_rate

def get_llm_costs():
    return st.session_state.llm_costs

def set_llm_costs(llm_costs: dict):
    st.session_state.llm_costs = llm_costs

def set_llm_input_cost(cost: int, model_name: str):
    st.session_state.llm_costs[model_name]["input_cost"] += cost

def set_llm_output_cost(cost: int, model_name: str):
    st.session_state.llm_costs[model_name]["output_cost"] += cost

def set_serp_api_results(contents: list):
    st.session_state.serp_api_results = contents

def get_serp_api_results():
    return st.session_state.serp_api_results
