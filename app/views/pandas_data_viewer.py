import pandas as pd
import streamlit as st
from plotly.graph_objs import Figure

from constants import PANDAS_AI_IMG_OUTPUT_PATH
class PandasDataViewer:
    """
    pandasのデータを表示するクラス
    """
    def __init__(self, data, index):
        self.data = data
        self.index = index

    def display_data(self):
        if isinstance(self.data, pd.DataFrame):
            st.dataframe(self.data,  key=f"pandas_dataframe_{self.index}")
        elif isinstance(self.data, Figure):
            st.plotly_chart(self.data, key=f"pandas_plotly_chart_{self.index}")
        elif self.data == PANDAS_AI_IMG_OUTPUT_PATH:
            st.write("出力中にエラーが発生しました。")
        else:
            st.write(self.data)