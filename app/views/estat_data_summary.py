import streamlit as st

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from api import get_estat_data_count
from utils import extract_statdisp_id, set_llm
from session import get_fetch_data_type, get_model_name, set_llm_input_cost, set_llm_output_cost
from constants import FetchDataType, SUMMARIZE_ESTAT_DATA_URL_PROMPT

class EstatDataSummary:
    def __init__(self, data, stat_data_index):
        self.summary = ""
        for i, item in enumerate(data, stat_data_index):
            
            prompt = ChatPromptTemplate.from_template(SUMMARIZE_ESTAT_DATA_URL_PROMPT)
            chain = prompt | set_llm(get_model_name()) | StrOutputParser()
            outline = chain.invoke({"title": item['title'], "snippet": item['snippet']}).strip()
            
            from services import calc_input_cost_from_prompt, calc_output_cost_from_result
            # 入力コストを計算
            prompt_text = SUMMARIZE_ESTAT_DATA_URL_PROMPT.format(title=item['title'], snippet=item['snippet'])
            input_cost = calc_input_cost_from_prompt(prompt_text, get_model_name())
            set_llm_input_cost(input_cost, get_model_name())
            
            # 出力コストを計算
            output_cost = calc_output_cost_from_result(prompt_text, get_model_name())
            set_llm_output_cost(output_cost, get_model_name())
            
            
            self.summary += f"**{i}. {item['title']}**  \n"
            self.summary += f"        **URL:** {item['link']}  \n"
            self.summary += f"        **概要:** {outline}  \n"
            
            if get_fetch_data_type() == FetchDataType.ESTAT_API.value:
                try:
                    data_count = get_estat_data_count(extract_statdisp_id(item['link']))
                    self.summary += f"        **データ件数:** {data_count:,}件  \n\n"
                except Exception as e:
                    self.summary += f"        **データ件数:** 取得に失敗しました。  \n\n"
            else:
                self.summary += "\n"
        
    def display_summary(self):
        st.markdown(self.summary)

    def get_summary(self):
        return self.summary