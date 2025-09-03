import logging

import pandas as pd
import plotly.express as px
import streamlit as st
from constants import DISPLAY_OPTIONS


class StatDataViewer:
    """
    estat-apiから取得したデータを表示するクラス
    ユーザーの選択した表示形式に応じて表示する内容を変える
    """

    def __init__(self, response, index):
        self.response = response
        self.index = index
        self.key = index + 1
        self.df = None
        self.continuous_values = []  # 連続値のカラム名(時間などの連続する値。折れ線グラフのx軸などで使用)
        self.cattegory_columns = []  # カテゴリーのカラム名
        self.value_column = '値'  # 値のカラム名
        self.display_type = DISPLAY_OPTIONS[0]
        self.unit_types = ['なし']

    def process_data(self):
        # データ
        values = self.response['GET_STATS_DATA']['STATISTICAL_DATA']['DATA_INF']['VALUE']
        self.df = pd.DataFrame(values)
        # カラムの情報
        meta_info = self.response['GET_STATS_DATA']['STATISTICAL_DATA']['CLASS_INF']['CLASS_OBJ']

        for class_obj in meta_info:
            column_name = '@' + class_obj['@id']
            id_to_name_dict = {}
            if isinstance(class_obj['CLASS'], list):
                for obj in class_obj['CLASS']:
                    id_to_name_dict[obj['@code']] = obj['@name']
            else:
                id_to_name_dict[class_obj['CLASS']['@code']] = class_obj['CLASS']['@name']
            self.df[column_name] = self.df[column_name].replace(id_to_name_dict)

        col_replace_dict = {'$': '値', '@unit': '単位'}
        for class_obj in meta_info:
            org_col = '@' + class_obj['@id']
            new_col = class_obj['@name']
            col_replace_dict[org_col] = new_col

        # カラム名の変換前に、グラフ用のカラム名を保存
        self.category_columns = [value for key, value in col_replace_dict.items() if key.startswith('@cat')] + [col_replace_dict.get('@area')] + [col_replace_dict.get('@time')]
        self.category_columns = [col for col in self.category_columns if col is not None]  # カテゴリがない場合はNoneになるので、Noneを除外

        self.continuous_values = [
            col_replace_dict.get('@time')
        ] + [value for key, value in col_replace_dict.items() if key.startswith('@cat')]  # @timeがない場合に、他の値を選択できるように対応
        self.continuous_values = [col for col in self.continuous_values if col is not None]  # 連続値がない場合はNoneになるので、Noneを除外

        new_columns = [col_replace_dict.get(col, col) for col in self.df.columns]
        self.df.columns = new_columns

        # ユニークな単位のリストを取得
        if '単位' in self.df.columns:
            self.df['単位'].fillna('なし', inplace=True)  # 単位がない場合にデフォルト値を設定
            self.unit_types = self.df['単位'].unique()

    def display_data(self):
        self._display(display_type=self.display_type)

    def display_data_with_session_state(self):
        default_value = st.session_state.messages[self.index].get("display_type", DISPLAY_OPTIONS[0])  # デフォルトは最初の選択肢
        self._display(display_type=default_value)

    def _display(self, display_type: str):
        selected_display = st.selectbox(
            "データの表示形式を選択してください",
            DISPLAY_OPTIONS,
            index=DISPLAY_OPTIONS.index(display_type) if display_type in DISPLAY_OPTIONS else 0,  # デフォルト値のインデックス
            key=f"display_type_{self.key}",
            on_change=self._update_session_state,
        )

        selected_unit = st.selectbox(
            "単位を選択してください",
            self.unit_types,
            key=f"unit_type_{self.key}",
        )

        # 単位が存在する場合のみフィルタリング
        if '単位' in self.df.columns:
            filtered_df = self.df[self.df['単位'] == selected_unit]
        else:
            filtered_df = self.df

        try:
            if selected_display == DISPLAY_OPTIONS[0]:
                st.dataframe(filtered_df)
            elif selected_display == DISPLAY_OPTIONS[1]:
                self._line_chart(filtered_df)
            elif selected_display == DISPLAY_OPTIONS[2]:
                self._scatter_plot(filtered_df)
            elif selected_display == DISPLAY_OPTIONS[3]:
                self._bar_chart(filtered_df)
        except Exception as e:
            logging.error(f"failed to display data: {e}")
            st.error("グラフの表示に失敗しました。")

    def _update_session_state(self):
        # 対象メッセージがセッションに存在しない場合は処理しない
        if (len(st.session_state.messages) <= self.index):
            return
        # セッション状態を更新
        select_key = f"display_type_{self.key}"
        new_selected_display = st.session_state[select_key]
        st.session_state.messages[self.index]["display_type"] = new_selected_display

    def _line_chart(self, data):
        selected_x_column = st.selectbox(
            "x軸となるカテゴリを選択してください",
            self.continuous_values,
            key=f"x_column_for_line_chart_{self.key}",
        )
        selected_color_column = st.selectbox(
            "色分けして表示するカテゴリを選択してください",
            self.category_columns,
            key=f"color_column_for_line_chart_{self.key}",
        )
        fig = px.line(data, x=selected_x_column, y=self.value_column, color=selected_color_column)
        st.plotly_chart(fig, key=f"line_chart_{self.key}")

    def _scatter_plot(self, data):
        selected_x_column = st.selectbox(
            "x軸となるカテゴリを選択してください",
            self.category_columns,
            key=f"x_column_for_scatter_plot_{self.key}",
        )
        selected_color_column = st.selectbox(
            "色分けして表示するカテゴリを選択してください",
            self.category_columns,
            key=f"color_column_for_scatter_plot_{self.key}",
        )
        fig = px.scatter(data, x=selected_x_column, y=self.value_column, color=selected_color_column)
        st.plotly_chart(fig, key=f"scatter_plot_{self.key}")

    def _bar_chart(self, data):
        selected_x_column = st.selectbox(
            "x軸となるカテゴリを選択してください",
            self.category_columns,
            key=f"x_column_for_bar_chart_{self.key}",
        )
        selected_color_column = st.selectbox(
            "色分けして表示するカテゴリを選択してください",
            self.category_columns,
            key=f"color_column_for_bar_chart_{self.key}",
        )

        # x軸と色分けのカテゴリが同じ場合に警告メッセージの表示
        if selected_color_column == selected_x_column:
            st.warning("x軸と色分けのカテゴリは異なる値を選択してください")
            return

        # 合計を算出できるようにfloat型に変換
        data['値'] = pd.to_numeric(data['値'], errors='coerce').fillna(0).astype(float)
        # x軸および色分けによるグループ化した合計値を計算
        grouped_data = data.groupby([selected_x_column, selected_color_column])['値'].sum().reset_index()
        # x軸のカテゴリごとの合計値を算出
        total_by_x_column = data.groupby([selected_x_column])['値'].sum().reset_index()
        total_by_x_column_view = total_by_x_column.copy()
        # x軸のカテゴリごとの合計値を表示する際の数値変換
        if (total_by_x_column['値'] >= 1e6).any():
            total_by_x_column_view['値'] = total_by_x_column['値'].map(lambda x: f"{x / 1e6:.1f}M")
        elif (total_by_x_column['値'] >= 1e3).any():
            total_by_x_column_view['値'] = total_by_x_column['値'].map(lambda x: f"{x / 1e3:.1f}K")
        else:
            total_by_x_column_view['値'] = total_by_x_column['値'].map('{:.1f}'.format)
        # 棒グラフを作成
        fig = px.bar(grouped_data, x=selected_x_column, y=self.value_column, color=selected_color_column)
        # x軸のカテゴリごとの合計値を棒グラフの上に表示（streamlitの機能でカテゴリ別にグラフ表示させた際に合計値が残ってしまうのためコメントアウト）
        # for i, row in total_by_x_column_view.iterrows():
        #    fig.add_annotation(
        #        x=row[selected_x_column],
        #        y=total_by_x_column.loc[i, '値'],
        #        text=f"{row['値']}",
        #        showarrow=False,
        #        yshift=10,
        #        font=dict(size=12)
        #    )
        st.plotly_chart(fig, key=f"bar_chart_{self.key}")

    def set_df(self, df: pd.DataFrame):
        self.df = df
