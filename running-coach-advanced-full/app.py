
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import date

st.set_page_config(page_title="Running Coach - Tùy chọn buổi", layout="centered")

@st.cache_data
def load_data():
    try:
        return pd.read_csv("data.csv")
    except:
        return pd.DataFrame(columns=["Buổi", "Ngày chạy", "Pace", "HR", "SpO2 trước", "SpO2 sau", "RPE", "Tổng điểm", "Đánh giá"])

def save_data(df):
    df.to_csv("data.csv", index=False)

def score_tempo(row):
    score = 0
    if 135 <= row["HR"] <= 160: score += 30
    if 4 <= row["RPE"] <= 6: score += 30
    if 6.20 <= row["Pace"] <= 6.45: score += 30
    if row["SpO2 sau"] >= 94: score += 10
    return score

def score_interval(row):
    score = 0
    if row["HR"] > 155: score += 35
    if 7 <= row["RPE"] <= 9: score += 35
    if row["SpO2 sau"] >= 93 and row["SpO2 trước"] - row["SpO2 sau"] <= 3: score += 20
    if 6.10 <= row["Pace"] <= 6.30: score += 10
    return score

def score_longrun(row):
    score = 0
    if 125 <= row["HR"] <= 145: score += 30
    if row["SpO2 sau"] >= 94 and abs(row["SpO2 trước"] - row["SpO2 sau"]) <= 2: score += 30
    if 3 <= row["RPE"] <= 5: score += 30
    if 6.45 <= row["Pace"] <= 7.20: score += 10
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

st.title("🏃‍♂️ Running Coach – Tuỳ chọn nhập & lịch sử")

tab1, tab2, tab3, tab4 = st.tabs(["📥 Nhập kết quả", "📋 Lịch sử buổi chạy", "📊 Biểu đồ", "🧹 Reset dữ liệu"])

with tab1:
    df = load_data()
    session_choice = st.selectbox("Chọn buổi để nhập kết quả", range(1, 17))
    session_index = session_choice - 1
    buoi_type, noidung, zone = sessions[session_index]
    st.write(f"**Loại buổi:** {buoi_type}")
    st.write(f"**Nội dung:** {noidung}")
    st.write(f"**Target HR Zone:** {zone}")

    with st.form("log_run_form"):
        day = st.date_input("Ngày chạy", value=date.today())
        pace = st.number_input("Pace (min/km)", step=0.1)
        hr = st.number_input("HR trung bình", step=1)
        spo2_before = st.number_input("SpO2 trước chạy", step=1)
        spo2_after = st.number_input("SpO2 sau chạy", step=1)
        rpe = st.slider("RPE (1–10)", 1, 10, 5)
        submit = st.form_submit_button("Lưu kết quả")

        if submit:
            new_row = {
                "Buổi": session_choice,
                "Ngày chạy": day,
                "Pace": pace,
                "HR": hr,
                "SpO2 trước": spo2_before,
                "SpO2 sau": spo2_after,
                "RPE": rpe
            }

            if buoi_type == "Tempo":
                score = score_tempo(new_row)
            elif buoi_type == "Interval":
                score = score_interval(new_row)
            else:
                score = score_longrun(new_row)

            new_row["Tổng điểm"] = score
            new_row["Đánh giá"] = rate(score)

            df = df[df["Buổi"] != session_choice]  # xoá nếu đã có buổi này
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            save_data(df)
            st.success(f"✅ Đã lưu kết quả Buổi #{session_choice}")

with tab2:
    df = load_data()
    st.subheader("📋 Lịch sử 16 buổi luyện tập")
    table = pd.DataFrame([
        {
            "Buổi": i+1,
            "Loại buổi": sessions[i][0],
            "Đánh giá": df[df["Buổi"] == i+1]["Đánh giá"].values[0] if (df["Buổi"] == i+1).any() else "⏳ Chưa nhập",
            "Tổng điểm": df[df["Buổi"] == i+1]["Tổng điểm"].values[0] if (df["Buổi"] == i+1).any() else ""
        }
        for i in range(16)
    ])
    st.dataframe(table)

with tab3:
    df = load_data()
    if not df.empty:
        df = df.sort_values("Buổi")
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

with tab4:
    if st.button("🧹 Xoá toàn bộ dữ liệu (reset chu kỳ)"):
        save_data(pd.DataFrame(columns=["Buổi", "Ngày chạy", "Pace", "HR", "SpO2 trước", "SpO2 sau", "RPE", "Tổng điểm", "Đánh giá"]))
        st.success("🎉 Đã xoá toàn bộ dữ liệu! Chu kỳ mới đã sẵn sàng.")
