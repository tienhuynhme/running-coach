
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import date, timedelta

st.set_page_config(page_title="Running Coach Tien", layout="centered")

@st.cache_data
def load_data():
    try:
        df = pd.read_csv("data.csv")
        df["Ngày"] = pd.to_datetime(df["Ngày"])
    except:
        df = pd.DataFrame(columns=["Ngày", "Buổi", "Pace", "HR", "SpO2 trước", "SpO2 sau", "RPE", "Tổng điểm", "Đánh giá"])
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

def generate_schedule(start_date):
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
    schedule = []
    for i, (buoi, noidung, zone) in enumerate(sessions):
        ngay = start_date + timedelta(days=i * 2)
        schedule.append({"Ngày": ngay, "Buổi": buoi, "Nội dung": noidung, "Target HR Zone": zone})
    return pd.DataFrame(schedule)

# Load data
st.title("🏃‍♂️ Running Coach Tien")
tab1, tab2, tab3 = st.tabs(["📅 Hôm nay tập gì", "📝 Nhật ký chạy", "📊 Biểu đồ"])

with tab1:
    st.subheader("Thiết lập kế hoạch luyện tập")
    start_day = st.date_input("Chọn ngày bắt đầu kế hoạch luyện tập", value=date.today())
    schedule_df = generate_schedule(start_day)
    today = pd.to_datetime(date.today())
    today_plan = schedule_df[schedule_df["Ngày"].dt.date == today.date()]
    if not today_plan.empty:
        st.success("Buổi tập hôm nay:")
        st.write(today_plan.iloc[0][["Buổi", "Nội dung", "Target HR Zone"]])
    else:
        st.info("Hôm nay không nằm trong lịch 16 buổi luyện tập.")

with tab2:
    st.subheader("Nhập kết quả buổi chạy")
    df = load_data()
    with st.form("log_run"):
        col1, col2 = st.columns(2)
        with col1:
            day = st.date_input("Ngày chạy", value=date.today())
            session = st.selectbox("Buổi", ["Tempo", "Interval", "Long run"])
            pace = st.number_input("Pace (min/km)", step=0.1)
            hr = st.number_input("HR trung bình", step=1)
        with col2:
            spo2_before = st.number_input("SpO2 trước chạy", step=1)
            spo2_after = st.number_input("SpO2 sau chạy", step=1)
            rpe = st.slider("RPE (1–10)", 1, 10, 5)

        submitted = st.form_submit_button("Lưu kết quả")
        if submitted:
            new_row = {
                "Ngày": pd.to_datetime(day),
                "Buổi": session,
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
            st.success("Đã lưu kết quả!")

    st.dataframe(df.sort_values("Ngày", ascending=False))

with tab3:
    st.subheader("Hiệu quả luyện tập theo tuần")
    df = load_data()
    if not df.empty:
        df["Tuần"] = df["Ngày"].dt.isocalendar().week
        weekly = df.groupby("Tuần")["Tổng điểm"].mean().reset_index()
        fig, ax = plt.subplots()
        ax.bar(weekly["Tuần"], weekly["Tổng điểm"], color='skyblue')
        ax.axhline(80, color='green', linestyle='--', label="Tốt")
        ax.axhline(60, color='orange', linestyle='--', label="Trung bình")
        ax.set_ylabel("Tổng điểm")
        ax.set_title("Điểm trung bình mỗi tuần")
        ax.legend()
        st.pyplot(fig)
    else:
        st.info("Chưa có dữ liệu để hiển thị biểu đồ.")
