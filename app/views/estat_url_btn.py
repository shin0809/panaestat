import streamlit as st

from constants import DISPLAY_OPTIONS
from tools import get_estat_data_by_url
from utils import is_estat_data
from session import set_agent_message

class EstatUrlBtn:
    def __init__(self, urls, index):
        self.urls = urls
        self.key = index + 1
        
    def display_btns(self):
        """
        ボタンを表示する
        """
        if(len(self.urls) == 0):
            return;
        if ('statdisp_id' in self.urls[0]):
            self._fetch_estat_data_btn(self.urls)
        else:
            self._download_estat_data_btn(self.urls)
        
        
    def _fetch_estat_data_btn(self, urls):
        """
        データを取得するボタンを表示する
        """
        st.write("どちらのデータを取得しますか？")
        columns = st.columns(len(urls))
        for index, url in enumerate(urls):
            with columns[index]:
                button_label = f"{index + 1}"
                st.button(
                    button_label,
                    key=f"estat_url_btn_{self.key}_{index}",
                    use_container_width=True,
                    on_click=self._on_click_estat_url,
                    kwargs={"url": url}
                )
                
    def _download_estat_data_btn(self, urls):
        """
        データをダウンロードするボタンを表示する
        """
        st.write("どちらのデータをダウンロードしますか？")
        columns = st.columns(len(urls))
        for index, url in enumerate(urls):
            with columns[index]: 
                button_label = f"{index + 1}"
                st.link_button(button_label, url, use_container_width=True)
            
    def _on_click_estat_url(self, url):
        """
        ボタンがクリックされたときに関数を実行
        e-StatのURLからデータを取得する
        """
        response = get_estat_data_by_url(url)
        
        if is_estat_data(response):
            set_agent_message(
                content=response,
                display_type=DISPLAY_OPTIONS[0],
                is_stat_data=True,
            )
        else:
            set_agent_message(content=response)
