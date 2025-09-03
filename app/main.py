import os

from dotenv import load_dotenv
from pathlib import Path

import streamlit as st

from session import initialize_session_state
from views import (
    init_sidebar,
    display_messages,
    display_login_page_title,
    display_main_page_title,
    FileUploader,
    PromptInput,
    AgentOutput,
)
from services import (
    login,
    move_to_login,
    move_to_main,
    check_is_authenticated,
    setup_agent,
)

# .envファイルのパスを構築
current_path = Path(__file__).resolve()
env_path = current_path.parent.parent / "config" / ".env"

load_dotenv(env_path)

# セッション状態の初期化
initialize_session_state()


# ページの表示を分岐
if st.session_state["page"] == "login":
    # ログインページのタイトルを表示
    display_login_page_title()
    login()  # ログイン処理

    # ログインが成功したらメインページへ移動
    if check_is_authenticated():
        move_to_main()


elif st.session_state["page"] == "main":
    # ログインしていない場合はログインページへ移動
    if not check_is_authenticated():
        move_to_login()

    # タイトル
    display_main_page_title()

    # Langエージェントの初期化
    agent = setup_agent()

    # ファイルのアップロード
    file, header = FileUploader().upload_file()

    # サイドバーの初期化と表示
    init_sidebar(file)

    # 過去のメッセージを表示
    display_messages()

    # プロンプトの入力と応答生成
    prompt = PromptInput(file).handle_prompt_input()
    AgentOutput(agent, prompt, file, header).handle_agent_output()
