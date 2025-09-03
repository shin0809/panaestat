from enum import Enum

from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_anthropic import ChatAnthropic

class GenerativeAIModel(Enum):
    GPT_4O = "gpt-5-nano"
    GEMINI_PRO = "gemini-2.5-pro"
    CLAUDE_SONNET = "claude-3-7-sonnet-20250219"

def set_llm(llm_name):
    if llm_name == GenerativeAIModel.GPT_4O.value:
        return ChatOpenAI(
            model=llm_name,
            temperature=0
        )
    elif llm_name == GenerativeAIModel.GEMINI_PRO.value:
        return ChatGoogleGenerativeAI(
            model=llm_name,
            temperature=0
        )
    elif llm_name == GenerativeAIModel.CLAUDE_SONNET.value:
        return ChatAnthropic(
            model=llm_name,
            temperature=0
        )
