import pandas as pd
import streamlit as st

from constants import PANDAS_AI_IMG_OUTPUT_PATH

class PandasDataViewer:
    """
    pandasのデータを表示するクラス
    """
    def __init__(self, data):
        self.data = data

    def display_data(self):
        if isinstance(self.data, pd.DataFrame):
            st.plotly_chart(self.data)
        elif self.data == PANDAS_AI_IMG_OUTPUT_PATH:
            st.write("出力中にエラーが発生しました。")
        else:
            st.write(self.data)