import streamlit as st
import folium
from streamlit_folium import st_folium
from PIL import Image
import base64
from io import BytesIO
import json
import os

#　背景画像
def set_bg(image_file):
    with open(image_file, "rb") as f:
        data = f.read()
    b64 = base64.b64encode(data).decode()

    page_bg_img = f"""
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{b64}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }}

    /* 中央コンテンツを白っぽくする */
    .block-container {{
        background-color: rgba(255,255,255,0.85);
        padding: 20px;
        border-radius: 15px;
    }}
    </style>
    """
    st.markdown(page_bg_img, unsafe_allow_html=True)

# 画像を置く
set_bg("/workspaces/test-g2430188/leaves_BG_01_green.png")

# タイトル
st.markdown("""
    <h1 style='text-align: center; color: #7FB77E;'>
    自然スポットマップ
    </h1>
    <p style='text-align: center;'>
    熊本の自然スポットを記録しよう📸
    </p>
""", unsafe_allow_html=True)

# データ読み込み
if "pins" not in st.session_state:
    if os.path.exists("pins.json"):
        with open("pins.json", "r") as f:
            st.session_state.pins = json.load(f)
    else:
        st.session_state.pins = []

# 熊本中心
kumamoto_lat = 32.7898
kumamoto_lon = 130.7417

# マップ
m = folium.Map(
    location=[kumamoto_lat, kumamoto_lon],
    zoom_start=9,
    min_zoom=8,
    max_zoom=13,
    tiles="CartoDB positron",
    max_bounds=True
)

# 範囲制限
m.fit_bounds([
    [31.0, 129.5],
    [33.5, 131.5]
])

# 画像→base64
def image_to_base64(img):
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

# ピン表示
for pin in st.session_state.pins:
    html = f"""
    <div style="text-align:center;">
        <img src="data:image/png;base64,{pin['img']}" width="150"><br>
        <p>{pin['comment']}</p>
    </div>
    """

    folium.Marker(
        location=[pin["lat"], pin["lon"]],
        popup=folium.Popup(html, max_width=200),
        icon=folium.Icon(color="green", icon="leaf")
    ).add_to(m)

# 地図表示
st_data = st_folium(m, width=700, height=500)

# クリック座標
clicked_lat = kumamoto_lat
clicked_lon = kumamoto_lon

if st_data and st_data["last_clicked"]:
    clicked_lat = st_data["last_clicked"]["lat"]
    clicked_lon = st_data["last_clicked"]["lng"]

# 入力フォーム
st.subheader("📍 スポット追加")

uploaded_file = st.file_uploader("写真をアップロード", type=["png", "jpg", "jpeg"])
lat = st.number_input("緯度", value=clicked_lat)
lon = st.number_input("経度", value=clicked_lon)
comment = st.text_input("コメント")

# 追加
if st.button("追加する"):
    if uploaded_file is not None:
        img = Image.open(uploaded_file)
        img_base64 = image_to_base64(img)

        st.session_state.pins.append({
            "lat": lat,
            "lon": lon,
            "img": img_base64,
            "comment": comment
        })

        with open("pins.json", "w") as f:
            json.dump(st.session_state.pins, f)

        st.success("追加できたよ！✨")
        st.rerun()
    else:
        st.error("写真をアップしてね！")

# 🗑️ 削除機能
st.subheader("🗑️ ピン削除")

for i, pin in enumerate(st.session_state.pins):
    st.write(f"📍 {pin['comment']}（{round(pin['lat'],2)}, {round(pin['lon'],2)}）")

    if st.button(f"削除 {i}"):
        st.session_state.pins.pop(i)

        with open("pins.json", "w") as f:
            json.dump(st.session_state.pins, f)

        st.success("削除できました")
        st.rerun()