import streamlit as st

class SeeMoreBtn:
    def __init__(self, next_data_index, total_data_count, key=None):
        self.next_data_index = next_data_index
        self.total_data_count = total_data_count
        self.key = key
        
    def display_btn(self):
        st.button("もっと見る", on_click=self.on_click_see_more, use_container_width=True, key=self.key)
        
    def on_click_see_more(self):
        from session import get_serp_api_results, set_agent_message
        from views import EstatDataSummary
        
        serp_api_results = get_serp_api_results()
        
        if len(serp_api_results) == 0:
            st.error("予期せぬエラーが発生しました。")
            return
        
        next_data = serp_api_results[self.next_data_index // 5]
        
        estat_data_summary = EstatDataSummary(next_data, self.next_data_index)
        set_agent_message(content=estat_data_summary.get_summary())
        
        urls = [item['link'] for item in next_data]
        
        content = {
            "urls": urls,
            "next_data_index": self.next_data_index,
            "total_data_count": self.total_data_count,
        }

        # ボタン
        if urls and len(urls) > 0:
            set_agent_message(
                content=content,
                with_btns=True,
            )