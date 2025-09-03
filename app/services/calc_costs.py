import json
import logging
import tiktoken
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_anthropic import ChatAnthropic

from utils import GenerativeAIModel
from constants import MODEL_PRICES

def calc_input_cost(tokens: int, model_name: str):
    input_price = MODEL_PRICES["input"].get(model_name, 0)
    # モデルがGemini 1.5 Proの場合、128000トークン以上の場合はコストが2倍になる
    if model_name == GenerativeAIModel.GEMINI_PRO.value and tokens > 128000:
        input_price *= 2
    input_cost = _convert_usd_to_jpy(tokens * input_price)
    logging.info(f"input_cost: {input_cost:.5f}円")
    return input_cost

def calc_output_cost(tokens: int, model_name: str):
    output_price = MODEL_PRICES["output"].get(model_name, 0)
    # モデルがGemini 1.5 Proの場合、128000トークン以上の場合はコストが2倍になる
    if model_name == GenerativeAIModel.GEMINI_PRO.value and tokens > 128000:
        output_price *= 2
    output_cost = _convert_usd_to_jpy(tokens * output_price)
    logging.info(f"output_cost: {output_cost:.5f}円")
    return output_cost

def calc_input_cost_from_prompt(query: str, model_name: str):
    input_count = _get_token_counts(query, model_name)
    return calc_input_cost(input_count, model_name)
    
def calc_output_cost_from_result(result: str, model_name: str):
    output_count = _get_token_counts(result, model_name)
    return calc_output_cost(output_count, model_name)

def _convert_usd_to_jpy(amount):
    from session import get_usd_jpy_rate
    usd_jpy_rate = get_usd_jpy_rate()
    return amount * usd_jpy_rate

def _get_token_counts(text: str, model_name: str) -> int:
    if model_name == GenerativeAIModel.GEMINI_PRO.value:  # GEMINI_PRO
        if isinstance(text, dict):
            text = json.dumps(text, ensure_ascii=False)
        llm = ChatGoogleGenerativeAI(model=model_name)
        return llm.get_num_tokens(text)
    elif model_name == GenerativeAIModel.GPT_4O.value:  # GPT_4O
        encoding = tiktoken.encoding_for_model(model_name)
        if isinstance(text, dict):
            text = json.dumps(text, ensure_ascii=False)
        return len(encoding.encode(text))
    elif model_name == GenerativeAIModel.CLAUDE_SONNET.value:  # CLAUDE_SONNET        
        if isinstance(text, dict):
            text = json.dumps(text, ensure_ascii=False)
        llm = ChatAnthropic(model=GenerativeAIModel.CLAUDE_SONNET.value)
        return llm.get_num_tokens(text)