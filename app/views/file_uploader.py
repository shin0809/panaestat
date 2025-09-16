import streamlit as st

class FileUploader:
    def upload_file(self):
        uploaded_file, header = None, 0,
        with st._bottom:
            uploaded_file = st.file_uploader(
                "Excel, CSVファイルを分析したい場合は、ファイルをアップロードしてください",
                type=["csv", "xlsx", "xls"],
            )
            if uploaded_file is not None:
                # ヘッダー行,列を選択するセレクトボックスを表示
                header = st.selectbox("ヘッダーを含むデータの開始行", list(range(1, 100)))
        return uploaded_file, header