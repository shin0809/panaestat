import streamlit as st
import streamlit_authenticator as stauth
# import yaml
# from yaml.loader import SafeLoader
import pandas as pd
from session import (
    get_authentication_status,
    set_authentication_status,
    get_user_name,
    set_user_data,
    set_page,
    set_messages
)

# yamlファイルでユーザ管理する場合
# def get_authenticator():
#     with open("settings/users.yaml") as file:
#         config = yaml.load(file, Loader=SafeLoader)

#     authenticator = stauth.Authenticate(
#         credentials=config['credentials'],
#         cookie_name=config['cookie']['name'],
#         cookie_key=config['cookie']['key'],
#         cookie_expiry_days=config['cookie']['expiry_days'],
#         prehashed=True
#     )
#     return authenticator

# csvファイルでユーザ管理する場合
def get_authenticator_from_csv(csv_file):
    df = pd.read_csv(csv_file)
    credentials = {"usernames": {}}
    for _, row in df.iterrows():
        email = row["email"]
        credentials["usernames"][email] = {
            "name": row["name"],
            "email": email,
            "password": row["password"]
        }
    
    cookie_config = {
        "name": "authentication",
        "key": "auth_key",
        "expiry_days": 1
    }
    
    authenticator = stauth.Authenticate(
        credentials=credentials,
        cookie_name=cookie_config["name"],
        cookie_key=cookie_config["key"],
        cookie_expiry_days=cookie_config["expiry_days"],
        prehashed=True
    )
    return authenticator

def login():
    # yamlファイルでユーザ管理する場合
    # authenticator = get_authenticator()
    
    # csvファイルでユーザ管理する場合
    authenticator = get_authenticator_from_csv("settings/users.csv")
    authenticator.login(location='main')

    set_authentication_status(st.session_state['authentication_status'])

    set_user_data(
        name=st.session_state.get("name"),
        email=st.session_state.get("email"),
    )

    if get_authentication_status():
        st.success(f"ようこそ {get_user_name()} さん！")
    elif get_authentication_status() is False:
        st.error("名前またはパスワードが間違っています。")
    else:
        st.warning("名前とパスワードを入力してください。")

def logout():
    # セッションのキーをリセットしてログインページへ遷移
    set_authentication_status(None)
    set_user_data(name=None, email=None)
    set_page("login")
    set_messages([])

def check_is_authenticated():
    return get_authentication_status() is True

def move_to_login():
    st.warning("ログインが必要です。")
    set_page("login")
    st.stop()

def move_to_main():
    st.button("メインページへ進む", on_click=_go_to_main)
    st.stop()

def _go_to_main():
    set_page("main")
