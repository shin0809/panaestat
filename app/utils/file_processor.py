import os
import pandas as pd
import streamlit as st


def extract_data_extension(uploaded_file):
    return os.path.splitext(uploaded_file.name)[1]

def read_file(uploaded_file, extension:str, header: int):
    skiprows = header - 1;
    if extension == ".csv":
        return pd.read_csv(uploaded_file, encoding="shift-jis", skiprows=skiprows)
    elif extension == ".xlsx":
        return pd.read_excel(uploaded_file, skiprows=skiprows)
    elif extension == ".xls":
        return pd.read_excel(uploaded_file, skiprows=skiprows)
    else:
        st.error("対応していないファイル形式です。")
        return None