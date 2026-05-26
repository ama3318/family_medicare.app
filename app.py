# ==========================================
# 個人パスワード対応 家族受診記録システム
# スマホ安定版
# ==========================================

import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime

FILE_NAME = "family_records.json"
PASSWORD_FILE = "password_config.json"

st.set_page_config(
    page_title="家族受診記録システム",
    layout="wide"
)

# ==========================================
# パスワード管理
# ==========================================

def load_passwords():
    if os.path.exists(PASSWORD_FILE):
        with open(PASSWORD_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except:
                return {}
    return {}

def save_new_password(new_password):
    pw_dict = load_passwords()
    pw_dict[new_password] = True

    with open(PASSWORD_FILE, "w", encoding="utf-8") as f:
        json.dump(
            pw_dict,
            f,
            indent=4,
            ensure_ascii=False
        )

# ==========================================
# ログイン処理
# ==========================================

def check_password():

    if "current_user_room" not in st.session_state:
        st.session_state.current_user_room = None

    if st.session_state.current_user_room is not None:
        return True

    st.title("🏥 家族受診記録システム")

    tab1, tab2 = st.tabs([
        "🔒 ログイン",
        "🔑 新規登録"
    ])

    # ----------------------------
    # ログイン
    # ----------------------------
    with tab1:

        login_pwd = st.text_input(
            "パスワード",
            type="password",
            key="login_pwd"
        )

        if st.button("ログイン"):

            registered_pws = load_passwords()

            if login_pwd in registered_pws:
                st.session_state.current_user_room = login_pwd
                st.success("ログイン成功")
                st.rerun()

            else:
                st.error("パスワードが違います")

    # ----------------------------
    # 新規登録
    # ----------------------------
    with tab2:

        new_pwd = st.text_input(
            "新しいパスワード",
            type="password",
            key="new_pwd"
        )

        confirm_pwd = st.text_input(
            "確認用パスワード",
            type="password",
            key="confirm_pwd"
        )

        if st.button("新規登録"):

            registered_pws = load_passwords()

            if new_pwd == "":
                st.error("パスワード未入力")

            elif new_pwd in registered_pws:
                st.error("そのパスワードは使用済み")

            elif new_pwd != confirm_pwd:
                st.error("確認用と一致しません")

            else:
                save_new_password(new_pwd)

                st.session_state.current_user_room = new_pwd

                st.success("登録完了")

                st.rerun()

    return False


if not check_password():
    st.stop()

# ==========================================
# データ読み込み
# ==========================================

MY_ROOM = st.session_state.current_user_room

def load_all_data():

    if os.path.exists(FILE_NAME):

        with open(FILE_NAME, "r", encoding="utf-8") as f:

            try:
                return json.load(f)

            except:
                return {}

    return {}

def save_all_data(all_data):

    with open(FILE_NAME, "w", encoding="utf-8") as f:

        json.dump(
            all_data,
            f,
            indent=4,
            ensure_ascii=False
        )

all_records = load_all_data()

if MY_ROOM not in all_records:
    all_records[MY_ROOM] = {}

my_records = all_records[MY_ROOM]

# ==========================================
# session_state 初期化
# ==========================================

if "selected_family" not in st.session_state:
    st.session_state.selected_family = None

if "selected_hospital" not in st.session_state:
    st.session_state.selected_hospital = None

if "selected_no" not in st.session_state:
    st.session_state.selected_no = None

# ==========================================
# タイトル
# ==========================================

st.title("🏥 家族受診記録システム")

st.caption("スマホ安定版")

# ==========================================
# ログアウト
# ==========================================

if st.button("🔒 ログアウト"):

    st.session_state.current_user_room = None

    st.rerun()

st.write("---")

# ==========================================
# 3カラム
# ==========================================

col1, col2, col3 = st.columns([1,1,2])

# ==========================================
# 家族一覧
# ==========================================

with col1:

    st.subheader("👨‍👩‍👧‍👦 家族")

    family_list = list(my_records.keys())

    if family_list:

        selected_family = st.radio(
            "家族",
            options=family_list,
            key="selected_family",
            label_visibility="collapsed"
        )

    else:

        selected_family = None

        st.info("家族データなし")

# ==========================================
# 医療機関一覧
# ==========================================

with col2:

    st.subheader("🏢 医療機関")

    if selected_family:

        hospital_list = list(
            my_records[selected_family].keys()
        )

        if hospital_list:

            selected_hospital = st.radio(
                "病院",
                options=hospital_list,
                key="selected_hospital",
                label_visibility="collapsed"
            )

        else:

            selected_hospital = None

            st.info("医療機関なし")

    else:

        selected_hospital = None

        st.info("家族を選択")

# ==========================================
# 履歴表示
# ==========================================

with col3:

    st.subheader("📝 受診履歴")

    current_rec = None

    if selected_family and selected_hospital:

        raw_history = my_records[selected_family][selected_hospital]

        history_data = []

        for i, rec in enumerate(raw_history):

            history_data.append({
                "No": i,
                "日付": rec.get("日付", ""),
                "内容": rec.get("内容", ""),
                "備考": rec.get("備考", "")
            })

        if history_data:

            df = pd.DataFrame(history_data)

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )

            selected_no = st.selectbox(
                "修正・削除対象",
                options=[d["No"] for d in history_data],
                key="selected_no"
            )

            current_rec = raw_history[selected_no]

        else:

            st.info("履歴なし")

# ==========================================
# 入力欄
# ==========================================

st.write("---")

st.subheader("📥 入力")

init_family = selected_family if selected_family else ""
init_hospital = selected_hospital if selected_hospital else ""

if current_rec:

    init_date = current_rec["日付"]
    init_content = current_rec["内容"]
    init_note = current_rec["備考"]

else:

    init_date = datetime.now().strftime("%Y-%m-%d")
    init_content = ""
    init_note = ""

c1, c2 = st.columns(2)

with c1:
    input_family = st.text_input(
        "家族名",
        value=init_family
    )

with c2:
    input_hospital = st.text_input(
        "医療機関",
        value=init_hospital
    )

c3, c4, c5 = st.columns([1,2,2])

with c3:
    input_date = st.text_input(
        "日付",
        value=init_date
    )

with c4:
    input_content = st.text_input(
        "内容",
        value=init_content
    )

with c5:
    input_note = st.text_input(
        "備考",
        value=init_note
    )

# ==========================================
# ボタン
# ==========================================

b1, b2, b3 = st.columns(3)

# ==========================================
# 追加
# ==========================================

with b1:

    if st.button("➕ 追加"):

        if (
            input_family == "" or
            input_hospital == "" or
            input_date == "" or
            input_content == ""
        ):

            st.error("必須項目未入力")

        else:

            my_records.setdefault(input_family, {})

            my_records[input_family].setdefault(
                input_hospital,
                []
            )

            my_records[input_family][input_hospital].append({

                "日付": input_date,
                "内容": input_content,
                "備考": input_note

            })

            all_records[MY_ROOM] = my_records

            save_all_data(all_records)

            st.success("追加しました")

            st.rerun()

# ==========================================
# 修正
# ==========================================

with b2:

    if st.button("📝 修正"):

        if current_rec is None:

            st.error("履歴を選択してください")

        else:

            selected_no = st.session_state.selected_no

            my_records[selected_family][selected_hospital][selected_no] = {

                "日付": input_date,
                "内容": input_content,
                "備考": input_note

            }

            all_records[MY_ROOM] = my_records

            save_all_data(all_records)

            st.success("修正しました")

            st.rerun()

# ==========================================
# 削除
# ==========================================

with b3:

    if st.button("🗑️ 削除"):

        if current_rec is None:

            st.error("履歴を選択してください")

        else:

            selected_no = st.session_state.selected_no

            my_records[selected_family][selected_hospital].pop(selected_no)

            all_records[MY_ROOM] = my_records

            save_all_data(all_records)

            st.success("削除しました")

            st.rerun()
