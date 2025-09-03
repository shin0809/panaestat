import logging

import streamlit as st
from pandasai.llm import OpenAI

class FileUploader:
    def __init__(self):
        self.llm = OpenAI()
        self.chart_img_path = "exports/charts/temp_chart.png"

    def upload_file(self):
        uploaded_file, header = None, 0,
        with st._bottom:
            uploaded_file = st.file_uploader(
                "Excel, CSVファイルを分析したい場合は、ファイルをアップロードしてください",
                type=["csv", "xlsx", "xls"],
            )
            if uploaded_file is not None:
                logging.info(f"file uploaded: {uploaded_file.name}")
                # ヘッダー行,列を選択するセレクトボックスを表示
                header = st.selectbox("ヘッダーを含むデータの開始行", list(range(1, 100)))
        return uploaded_file, header