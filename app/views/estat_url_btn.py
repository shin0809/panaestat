import streamlit as st

from constants import DISPLAY_OPTIONS
from tools import get_estat_data_by_url
from utils import is_estat_data
from session import set_agent_message

class EstatUrlBtn:
    def __init__(self, urls, index, start_data_index, total_data_count, see_more_btn=False):
        self.urls = urls
        self.key = index + 1
        self.start_data_index = start_data_index
        self.total_data_count = total_data_count
        self.see_more_btn = see_more_btn
        
        if self.start_data_index + 5 > self.total_data_count:
            # 次に表示する5件のデータが存在しない場合は、もっと見るボタンを表示しない表示フラグを上書きする
            self.see_more_btn = False
        
        
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
                button_label = f"{index + self.start_data_index}"
                st.button(
                    button_label,
                    key=f"estat_url_btn_{self.key}_{index}",
                    use_container_width=True,
                    on_click=self._on_click_estat_url,
                    kwargs={"url": url}
                )
                
        if self.see_more_btn:
            from views import SeeMoreBtn
            SeeMoreBtn(
                key=f"see_more_btn_{self.key}_{index}",
                next_data_index=self.start_data_index + len(urls),
                total_data_count=self.total_data_count
            ).display_btn()
                
    def _download_estat_data_btn(self, urls):
        """
        データをダウンロードするボタンを表示する
        """
        st.write("どちらのデータをダウンロードしますか？")
        columns = st.columns(len(urls))
        for index, url in enumerate(urls):
            with columns[index]: 
                button_label = f"{index + self.start_data_index}"
                st.link_button(button_label, url, use_container_width=True)
                
        if self.see_more_btn:
            from views import SeeMoreBtn
            SeeMoreBtn(
                key=f"see_more_btn_{self.key}_{index}",
                next_data_index=self.start_data_index + len(urls),
                total_data_count=self.total_data_count
            ).display_btn()
            
    def _on_click_estat_url(self, url):
        """
        ボタンがクリックされたときに関数を実行
        e-StatのURLからデータを取得する
        """
        response = get_estat_data_by_url.invoke({"url": url})
        
        if is_estat_data(response):
            set_agent_message(
                content=response,
                display_type=DISPLAY_OPTIONS[0],
                is_stat_data=True,
            )
        else:
            set_agent_message(content=response)
