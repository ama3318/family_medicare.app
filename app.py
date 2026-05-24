import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime

FILE_NAME = 'family_records.json'
PASSWORD_FILE = 'password_config.json'

st.set_page_config(page_title="家族受診記録システム", layout="wide")

# =========================
# 🔒 パスワードデータの読み込み・保存
# =========================
def load_passwords():
    if os.path.exists(PASSWORD_FILE):
        with open(PASSWORD_FILE, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except:
                return {}
    return {}

def save_new_password(new_password):
    pw_dict = load_passwords()
    pw_dict[new_password] = True
    with open(PASSWORD_FILE, 'w', encoding='utf-8') as f:
        json.dump(pw_dict, f, indent=4, ensure_ascii=False)

# =========================
# 🔒 部屋ごとのパスワード認証・切り替え機能
# =========================
def check_password():
    if "current_user_room" not in st.session_state:
        st.session_state["current_user_room"] = None

    if st.session_state["current_user_room"] is not None:
        return True

    st.title("🏥 家族受診記録システム - ログイン・新規登録")
    st.caption("このアプリは個人ごとに独立した『個別ページ（部屋）』を作成してデータを管理します。")

    tab1, tab2 = st.tabs(["🔒 登録済みの部屋にログイン", "🔑 新しい部屋を作る（新規登録）"])

    with tab1:
        pwd_input = st.text_input("設定したパスワードを入力してください", type="password", key="login_pwd")
        if st.button("ログインする", key="login_btn"):
            registered_pws = load_passwords()
            if pwd_input in registered_pws:
                st.session_state["current_user_room"] = pwd_input
                st.success("ログイン成功！あなた専用の部屋を開きます。")
                st.rerun()
            else:
                st.error("🔑 パスワードが登録されていないか、間違っています。")

    with tab2:
        st.info("家族が初めて使う場合も、ここから自分専用のパスワードを登録してもらいます。")
        new_pwd = st.text_input("新しく設定するパスワード", type="password", key="reg_pwd")
        confirm_pwd = st.text_input("確認のためもう一度入力", type="password", key="confirm_reg_pwd")
        
        if st.button("新しく部屋を作成する", key="reg_btn"):
            registered_pws = load_passwords()
            if not new_pwd:
                st.error("パスワードが空欄です。")
            elif new_pwd in registered_pws:
                st.error("このパスワードはすでに使用されています。別のパスワードにしてください。")
            elif new_pwd != confirm_pwd:
                st.error("入力された2つのパスワードが一致しません。")
            else:
                save_new_password(new_pwd)
                st.session_state["current_user_room"] = new_pwd
                st.success("あなた専用の部屋が新しく作られました！")
                st.rerun()
                
    return False

if not check_password():
    st.stop()

MY_ROOM = st.session_state["current_user_room"]

# ==================================================
# 💾 データの読み込み・保存
# ==================================================
def load_all_data():
    if os.path.exists(FILE_NAME):
        with open(FILE_NAME, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except:
                return {}
    return {}

def save_all_data(all_data):
    with open(FILE_NAME, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, indent=4, ensure_ascii=False)

all_records = load_all_data()

if MY_ROOM not in all_records:
    all_records[MY_ROOM] = {}

my_records = all_records[MY_ROOM]

# =========================
# 🏥 画面表示
# =========================
st.title("🏥 家族受診記録システム")
st.caption(f"🔑 現在、あなた専用の部屋にログイン中（他の人にはこのデータは見えません）")

if st.button("🔒 安全にログアウトして画面をロックする"):
    st.session_state["current_user_room"] = None
    st.rerun()

st.write("---")

col_family, col_hospital, col_table = st.columns([1, 1, 2])

with col_family:
    st.subheader("👨‍👩‍👧‍👦 家族一覧")
    family_list = list(my_records.keys())
    selected_family = st.radio("家族を選択してください", options=family_list, key="-FAMILY-", label_visibility="collapsed")

with col_hospital:
    st.subheader("🏢 医療機関一覧")
    if selected_family:
        hospital_list = list(my_records.get(selected_family, {}).keys())
        selected_hospital = st.radio("医療機関を選択してください", options=hospital_list, key="-HOSPITAL-", label_visibility="collapsed")
    else:
        st.info("先に家族を選択してください")
        selected_hospital = None

with col_table:
    st.subheader("📝 受診履歴")
    history_data = []
    
    if selected_family and selected_hospital:
        raw_history = my_records.get(selected_family, {}).get(selected_hospital, [])
        for i, rec in enumerate(raw_history):
            history_data.append({
                "No": i,
                "日付": rec.get('日付', ''),
                "内容": rec.get('内容', ''),
                "備考": rec.get('備考', '')
            })
        
        if history_data:
            df = pd.DataFrame(history_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
            selected_no = st.selectbox("修正・削除するレコードNo", options=[d["No"] for d in history_data])
            current_rec = raw_history[selected_no]
        else:
            st.info("登録されている履歴がありません")
            current_rec = None
    else:
        st.info("家族と医療機関を選択すると履歴が表示されます")
        current_rec = None

st.write("---")

st.subheader("📥 入力フォーム")
init_family = selected_family if selected_family else ""
init_hospital = selected_hospital if selected_hospital else ""
init_date = current_rec['日付'] if current_rec else datetime.now().strftime("%Y-%m-%d")
init_content = current_rec['内容'] if current_rec else ""
init_note = current_rec['備考'] if current_rec else ""

with st.form(key="input_form", clear_on_submit=False):
    c1, c2 = st.columns(2)
    with c1:
        input_family = st.text_input("家族名", value=init_family)
    with c2:
        input_hospital = st.text_input("医療機関", value=init_hospital)
        
    c3, c4, c5 = st.columns([1, 2, 2])
    with c3:
        input_date = st.text_input("日付", value=init_date)
    with c4:
        input_content = st.text_input("内容", value=init_content)
    with c5:
        input_note = st.text_input("備考", value=init_note)
        
    btn_col1, btn_col2, btn_col3, _ = st.columns([1, 1, 1, 5])
    with btn_col1:
        add_btn = st.form_submit_button("➕ 追加")
    with btn_col2:
        edit_btn = st.form_submit_button("📝 修正")
    with btn_col3:
        delete_btn = st.form_submit_button("🗑️ 削除")

if add_btn:
    if not input_family or not input_hospital or not input_date or not input_content:
        st.error("備考以外のすべての項目を入力してください")
    else:
        my_records.setdefault(input_family, {})
        my_records[input_family].setdefault(input_hospital, [])
        my_records[input_family][input_hospital].append({
            '日付': input_date, '内容': input_content, '備考': input_note
        })
        all_records[MY_ROOM] = my_records
        save_all_data(all_records)
        st.success(f"{input_family} の記録を追加しました！")
        st.rerun()

if edit_btn:
    if current_rec is None:
        st.error("修正する記録を上の履歴一覧から選択してください")
    else:
        my_records[selected_family][selected_hospital][selected_no] = {
            '日付': input_date, '内容': input_content, '備考': input_note
        }
        all_records[MY_ROOM] = my_records
        save_all_data(all_records)
        st.success("記録を修正しました！")
        st.rerun()

if delete_btn:
    if current_rec is None:
        st.error("削除する記録を上の履歴一覧から選択してください")
    else:
        my_records[selected_family][selected_hospital].pop(selected_no)
        all_records[MY_ROOM] = my_records
        save_all_data(all_records)
        st.success("記録を削除しました")
        st.rerun()
