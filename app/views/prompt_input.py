import streamlit as st

from constants import PROMPT_WITH_FILE
from session import set_user_message

class PromptInput:
    def __init__(self, file):
        self.file = file

    def handle_prompt_input(self):
        """
        ファイルありで質問を入力している場合は、ファイル名を表示する
        agentへのプロンプトにはファイル名を含めない
        """
        if prompt := st.chat_input("入力してください"):
            prompt_for_display = prompt
            if self.file is not None:
                # ファイルがある場合、改行を追加し、ファイル名を保存
                prompt_for_display = PROMPT_WITH_FILE.format(prompt=prompt, file=self.file.name)
            set_user_message(prompt_for_display)
            
            with st.chat_message("user"):
                st.markdown(prompt_for_display)
        return prompt