import os
import pandas as pd
import streamlit as st
import chardet

def extract_data_extension(uploaded_file):
    return os.path.splitext(uploaded_file.name)[1]

def _detect_encoding(uploaded_file):
    """ファイルのエンコーディングを自動判別する"""
    raw_data = uploaded_file.read()
    result = chardet.detect(raw_data)
    encoding = result["encoding"]
    uploaded_file.seek(0)
    return encoding

def read_file(uploaded_file, extension: str, header: int):
    skiprows = header - 1
    encoding = _detect_encoding(uploaded_file)

    if extension == ".csv":
        try:
            return pd.read_csv(uploaded_file, encoding=encoding, skiprows=skiprows)
        except UnicodeDecodeError:
            st.error(f"エンコーディング {encoding} で読み込めませんでした。")
            return None
    elif extension in [".xlsx", ".xls"]:
        return pd.read_excel(uploaded_file, skiprows=skiprows)
    else:
        st.error("対応していないファイル形式です。")
        return None
