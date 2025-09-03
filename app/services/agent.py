from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import AgentExecutor, create_tool_calling_agent, Tool

from constants import INITIAL_PROMPT
from session import get_model_name
from utils import set_llm
from tools import get_estat_data_by_id, get_estat_data_by_url, search_estat_url, format_estat_data

def setup_agent():
    llm = set_llm(get_model_name())

    tools = [
        Tool(
            name="search_estat_url",
            func=search_estat_url,
            description="e-Statのサイト内検索を行い、検索結果上位のサイト20件から、ユーザーの意図に最も合致する上位5件を選んで内容を整形して返却します。 ユーザーが何かの統計データを探しているときに使用します。",
            return_direct=True
        ),
        Tool(
            name="get_estat_data_by_id",
            func=get_estat_data_by_id,
            description="e-Statの統計データを取得します。ユーザーが統計表IDを指定した時に使用します。",
            return_direct=True
        ),
        Tool(
            name="get_estat_data_by_url",
            func=get_estat_data_by_url,
            description="e-Statの統計データを取得します。ユーザーがestatのURLを指定した時に使用します。",
            return_direct=True
        ),
        Tool(
            name="format_estat_data",
            func=format_estat_data,
            description="ユーザーが統計データを整形したいときに使用します。セッションにデータが蓄積されているので、データの絞り込みや整形の指示があった場合にこの関数を使用してください。データは関数内で自動的に最新のデータを特定して対応するので、ユーザーがデータを指定する必要はないです。",
            return_direct=True
        )
    ]
    
    template = ChatPromptTemplate.from_messages(
        [
            ("system", INITIAL_PROMPT),
            # MessagesPlaceholder(variable_name="chat_history"),　#　チャット履歴を読み込む場合は使用する
            ("user", "{user_input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ]
    )
    tool_calling_agent = create_tool_calling_agent(llm, tools, template)
    
    agent = AgentExecutor(agent=tool_calling_agent, tools=tools, verbose=True)

    return agent