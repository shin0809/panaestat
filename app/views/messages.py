import streamlit as st
import logging

from views import StatDataViewer, PandasDataViewer, EstatUrlBtn

def display_messages():
    for index, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            is_stat_data = message.get("is_stat_data") # 統計データかどうか
            with_file = message.get("with_file") # アップロードしたファイルに対する回答かどうか
            with_btns = message.get("with_btns") # ボタンの表示有無
            is_formatted = message.get("is_formatted") # PandasAIによって整形されたデータかどうか

            if not is_stat_data:
                if with_btns:
                    # urlボタンの表示
                    EstatUrlBtn(message["content"], index).display_btns()
                else:
                    # テキストデータの表示
                    st.markdown(message["content"])
                continue

            # 統計データの表示
            if with_file:
                # ユーザーがアップロードしたファイルの解析結果
                try:
                    PandasDataViewer(message["content"]).display_data()
                except Exception as e:
                    logging.error(f"failed to display data: {e}")
                    st.warning("データの表示に失敗しました。何度も失敗する場合はリロードしてください。")
            elif is_formatted:
                # pandasaiによって整形されたデータはStatDataViewerで保存しているのでそのまま表示
                message["content"].display_data()
            else:
                # estatから取得した未整形の統計データの表示
                viewer = StatDataViewer(message["content"], index)
                viewer.process_data()
                viewer.display_data_with_session_state()