import streamlit as st
import pandas as pd
import datetime
import os
import json

st.set_page_config(
    page_title="Healthy Lifestyle Tracker",
    layout="wide",
    page_icon="🥗"
)

# ------------------ FILE PATHS (FIXED) ------------------
DATA_FILE = "data.csv"
GOALS_FILE = "goals.json"

# ------------------ DATA FUNCTIONS ------------------
def load_data():
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)

        # Ensure optional columns exist
        if "Calories (kcal)" not in df.columns:
            df["Calories (kcal)"] = 2000
        if "Meditation (Mins)" not in df.columns:
            df["Meditation (Mins)"] = 10

        return df
    else:
        return pd.DataFrame(columns=[
            "Date", "Water (L)", "Sleep (Hrs)", "Exercise (Mins)",
            "Mood", "Notes", "Calories (kcal)", "Meditation (Mins)"
        ])


def save_data(df):
    df.to_csv(DATA_FILE, index=False)


def load_goals():
    default_goals = {
        "daily_water_l": 3.0,
        "daily_sleep_hrs": 8.0,
        "weekly_exercise_mins": 150,
        "daily_calories_kcal": 2000,
        "daily_meditation_mins": 10
    }

    if os.path.exists(GOALS_FILE):
        try:
            with open(GOALS_FILE, "r") as f:
                saved = json.load(f)
            return {**default_goals, **saved}
        except:
            return default_goals

    return default_goals


def save_goals(goals):
    with open(GOALS_FILE, "w") as f:
        json.dump(goals, f)

# ------------------ UI ------------------
st.title("🥗 Healthy Lifestyle Tracker")
st.markdown("Track your daily habits and stay healthy!")

st.sidebar.header("Log Today's Habits")

today = datetime.date.today()
date_input = st.sidebar.date_input("Date", today)

water = st.sidebar.slider("Water Intake (Liters)", 0.0, 5.0, 2.0, 0.1)
sleep = st.sidebar.slider("Sleep (Hours)", 0.0, 12.0, 7.0, 0.5)
exercise = st.sidebar.number_input("Exercise (Minutes)", 0, 300, 30, 10)
mood = st.sidebar.selectbox("Mood", ["Happy", "Neutral", "Stressed", "Tired", "Energetic"])
notes = st.sidebar.text_area("Notes (Optional)")
calories = st.sidebar.number_input("Calories (kcal)", 0, 10000, 2000, 50)
meditation = st.sidebar.number_input("Meditation (Minutes)", 0, 300, 10, 5)

if st.sidebar.button("Save Entry"):
    df = load_data()
    date_str = date_input.strftime("%Y-%m-%d")

    df = df[df["Date"] != date_str]

    new_row = pd.DataFrame([{
        "Date": date_str,
        "Water (L)": water,
        "Sleep (Hrs)": sleep,
        "Exercise (Mins)": exercise,
        "Mood": mood,
        "Notes": notes,
        "Calories (kcal)": calories,
        "Meditation (Mins)": meditation
    }])

    df = pd.concat([df, new_row], ignore_index=True)
    save_data(df)

    st.sidebar.success("Entry saved successfully!")

# ------------------ GOALS ------------------
st.sidebar.header("Goals")
goals = load_goals()

with st.sidebar.expander("Set Goals"):
    g_water = st.number_input("Daily Water (L)", 0.0, 10.0, goals["daily_water_l"], 0.1)
    g_sleep = st.number_input("Daily Sleep (Hrs)", 0.0, 24.0, goals["daily_sleep_hrs"], 0.5)
    g_ex = st.number_input("Weekly Exercise (Mins)", 0, 2000, goals["weekly_exercise_mins"], 10)
    g_cal = st.number_input("Daily Calories (kcal)", 0, 10000, goals["daily_calories_kcal"], 50)
    g_med = st.number_input("Daily Meditation (Mins)", 0, 300, goals["daily_meditation_mins"], 5)

    if st.button("Save Goals"):
        save_goals({
            "daily_water_l": g_water,
            "daily_sleep_hrs": g_sleep,
            "weekly_exercise_mins": g_ex,
            "daily_calories_kcal": g_cal,
            "daily_meditation_mins": g_med
        })
        st.success("Goals saved successfully!")

# ------------------ DASHBOARD ------------------
df = load_data()

if not df.empty:
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date")

    st.subheader("Lifestyle Trends")
    st.line_chart(df.set_index("Date")[["Water (L)", "Sleep (Hrs)", "Calories (kcal)", "Meditation (Mins)"]])
    st.bar_chart(df.set_index("Date")["Exercise (Mins)"])

    st.subheader("Recent History")
    st.dataframe(df.sort_values("Date", ascending=False).head(10))
else:
    st.info("No data available. Start tracking from the sidebar.")
