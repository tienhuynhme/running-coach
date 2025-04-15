
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import date

st.set_page_config(page_title="Running Coach - Buổi linh hoạt", layout="centered")

@st.cache_data
def load_data():
    try:
        df = pd.read_csv("data.csv")
    except:
        df = pd.DataFrame(columns=["Buổi", "Ngày chạy", "Pace", "HR", "SpO2 trước", "SpO2 sau", "RPE", "Tổng điểm", "Đánh giá"])
    return df

def calculate_score(row):
    score = 0
    if 130 <= row["HR"] <= 168: score += 40
    if row["SpO2 sau"] >= 94 and row["SpO2 trước"] - row["SpO2 sau"] <= 2: score += 30
    if row["RPE"] <= 6: score += 20
    if 5.85 <= row["Pace"] <= 7.15: score += 10
    return score

def rate(score):
    if score >= 80: return "Tốt"
    elif score >= 60: return "Trung bình"
    else: return "Cần điều chỉnh"

sessions = [
    ("Tempo", "5–8km @ pace 6:45", "Zone 3–4"),
    ("Interval", "6x800m @ pace 6:30", "Zone 4–5"),
    ("Long run", "10km @ pace 7:00–7:30", "Zone 2"),
    ("Tempo", "6km @ pace 6:40", "Zone 3–4"),
    ("Interval", "8x400m @ pace 6:20", "Zone 4–5"),
    ("Long run", "12km @ pace 7:00", "Zone 2"),
    ("Tempo", "7km @ pace 6:35", "Zone 3–4"),
    ("Interval", "4x1km @ pace 6:25", "Zone 4–5"),
    ("Long run", "14km @ pace 6:55", "Zone 2"),
    ("Tempo", "8km @ pace 6:30", "Zone 3–4"),
    ("Interval", "10x300m @ pace 6:10", "Zone 4–5"),
    ("Long run", "16km @ pace 6:50", "Zone 2"),
    ("Tempo", "9km @ pace 6:25", "Zone 3–4"),
    ("Interval", "5x1km @ pace 6:20", "Zone 4–5"),
    ("Long run", "18km @ pace 6:45", "Zone 2"),
    ("Tempo", "10km @ pace 6:20", "Zone 3–4")
]

st.title("🏃‍♂️ Running Coach – Linh hoạt theo buổi")
tab1, tab2, tab3 = st.tabs(["📋 Buổi kế tiếp", "📝 Ghi kết quả", "📊 Biểu đồ"])

with tab1:
    df = load_data()
    current_session = len(df) + 1
    if current_session <= 16:
        st.success(f"🎯 Buổi kế tiếp: Buổi #{current_session}")
        buoi, noidung, zone = sessions[current_session - 1]
        st.write(f"**Loại buổi**: {buoi}")
        st.write(f"**Nội dung**: {noidung}")
        st.write(f"**Target HR Zone**: {zone}")
    else:
        st.info("🎉 Bạn đã hoàn thành toàn bộ 16 buổi luyện tập!")

with tab2:
    st.subheader("Nhập kết quả buổi chạy")
    df = load_data()
    current_session = len(df) + 1
    if current_session > 16:
        st.warning("Bạn đã hoàn thành tất cả các buổi!")
    else:
        with st.form("log_run"):
            day = st.date_input("Ngày chạy", value=date.today())
            pace = st.number_input("Pace (min/km)", step=0.1)
            hr = st.number_input("HR trung bình", step=1)
            spo2_before = st.number_input("SpO2 trước chạy", step=1)
            spo2_after = st.number_input("SpO2 sau chạy", step=1)
            rpe = st.slider("RPE (1–10)", 1, 10, 5)

            submitted = st.form_submit_button("Lưu kết quả")
            if submitted:
                new_row = {
                    "Buổi": current_session,
                    "Ngày chạy": day,
                    "Pace": pace,
                    "HR": hr,
                    "SpO2 trước": spo2_before,
                    "SpO2 sau": spo2_after,
                    "RPE": rpe
                }
                new_row["Tổng điểm"] = calculate_score(new_row)
                new_row["Đánh giá"] = rate(new_row["Tổng điểm"])
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                df.to_csv("data.csv", index=False)
                st.success("✅ Đã lưu kết quả buổi chạy!")

    if not df.empty:
        st.dataframe(df.sort_values("Buổi"))

with tab3:
    df = load_data()
    if not df.empty:
        fig, ax = plt.subplots()
        ax.plot(df["Buổi"], df["Tổng điểm"], marker="o", linestyle="--")
        ax.axhline(80, color='green', linestyle='--', label="Tốt")
        ax.axhline(60, color='orange', linestyle='--', label="Trung bình")
        ax.set_xlabel("Buổi chạy")
        ax.set_ylabel("Tổng điểm")
        ax.set_title("Biểu đồ hiệu quả luyện tập theo buổi")
        ax.legend()
        st.pyplot(fig)
    else:
        st.info("Chưa có dữ liệu để hiển thị biểu đồ.")
