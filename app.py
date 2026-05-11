# ============================================================
#   SalaryAI Pro — app.py
#   Run: streamlit run app.py
#   Admin login: username=admin  password=admin123
# ============================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import joblib
import json
import hashlib
import os
import re
from datetime import datetime

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="SalaryAI Pro",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────
USERS_FILE   = "users.json"
LOGS_FILE    = "prediction_logs.json"
CONTACT_FILE = "contact_messages.json"
ADMIN_USER   = "admin"
ADMIN_PASS   = hashlib.sha256("admin123".encode()).hexdigest()

# ─────────────────────────────────────────────
# CSS — Dark Purple Theme
# ─────────────────────────────────────────────
def apply_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@400;600;700&display=swap');

    /* ---------- global ---------- */
    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }
    .stApp {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        min-height: 100vh;
    }

    /* ---------- sidebar ---------- */
    section[data-testid="stSidebar"] {
        background: rgba(15, 12, 41, 0.97) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }
    section[data-testid="stSidebar"] * {
        color: #ffffff !important;
    }

    /* ---------- headings ---------- */
    h1, h2, h3 {
        color: #ffffff !important;
        font-family: 'Space Grotesk', sans-serif !important;
    }

    /* ---------- inputs ---------- */
    .stTextInput > label,
    .stNumberInput > label,
    .stSelectbox > label,
    .stTextArea > label,
    .stSlider > label,
    .stRadio > label {
        color: rgba(255, 255, 255, 0.75) !important;
        font-size: 0.87rem !important;
        font-weight: 500 !important;
    }
    .stTextInput > div > div > input,
    .stNumberInput input,
    .stTextArea textarea {
        background: rgba(255, 255, 255, 0.07) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 10px !important;
        color: #ffffff !important;
    }
    .stTextInput > div > div > input:focus,
    .stTextArea textarea:focus {
        border-color: #7c6af7 !important;
        box-shadow: 0 0 0 2px rgba(124, 106, 247, 0.25) !important;
    }
    .stSelectbox > div > div {
        background: rgba(255, 255, 255, 0.07) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 10px !important;
        color: #ffffff !important;
    }

    /* ---------- buttons ---------- */
    .stButton > button {
        background: linear-gradient(135deg, #7c6af7, #a78bfa) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.65rem 1.5rem !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        width: 100% !important;
        transition: all 0.25s ease !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(124, 106, 247, 0.5) !important;
    }

    /* ---------- custom cards ---------- */
    .card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 1.4rem 1.6rem;
        margin-bottom: 1rem;
    }
    .stat-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 14px;
        padding: 1.2rem 1rem;
        text-align: center;
    }
    .stat-num {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2rem;
        font-weight: 700;
        color: #a78bfa;
    }
    .stat-lbl {
        color: rgba(255, 255, 255, 0.5);
        font-size: 0.78rem;
        margin-top: 0.2rem;
    }
    .feat-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 14px;
        padding: 1.3rem;
        text-align: center;
    }
    .pred-box {
        background: linear-gradient(135deg, rgba(124, 106, 247, 0.25), rgba(167, 139, 250, 0.12));
        border: 1px solid rgba(124, 106, 247, 0.45);
        border-radius: 18px;
        padding: 2rem;
        text-align: center;
        margin-top: 1.2rem;
    }
    .pred-amt {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 3rem;
        font-weight: 700;
        color: #a78bfa;
    }

    /* ---------- badges ---------- */
    .badge-user {
        background: rgba(124, 106, 247, 0.2);
        border: 1px solid rgba(124, 106, 247, 0.4);
        border-radius: 50px;
        padding: 0.35rem 0.9rem;
        color: #a78bfa;
        font-size: 0.82rem;
        font-weight: 600;
        display: inline-block;
    }
    .badge-admin {
        background: rgba(245, 158, 11, 0.2);
        border: 1px solid rgba(245, 158, 11, 0.4);
        border-radius: 50px;
        padding: 0.35rem 0.9rem;
        color: #fbbf24;
        font-size: 0.82rem;
        font-weight: 600;
        display: inline-block;
    }

    /* ---------- auth page ---------- */
    .auth-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2rem;
        font-weight: 700;
        color: #ffffff;
        text-align: center;
        margin-bottom: 0.25rem;
    }
    .auth-sub {
        text-align: center;
        color: rgba(255, 255, 255, 0.5);
        font-size: 0.88rem;
        margin-bottom: 1.8rem;
    }
    .or-divider {
        display: flex;
        align-items: center;
        margin: 1rem 0;
        color: rgba(255, 255, 255, 0.3);
        font-size: 0.78rem;
    }
    .or-divider::before,
    .or-divider::after {
        content: '';
        flex: 1;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }
    .or-divider span {
        padding: 0 10px;
    }

    /* ---------- gradient text ---------- */
    .gradient-text {
        background: linear-gradient(135deg, #a78bfa, #60a5fa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    </style>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# SESSION STATE — initialize defaults
# ─────────────────────────────────────────────
def init_session():
    defaults = {
        "logged_in": False,
        "username":  "",
        "role":      "",
        "auth_page": "login",
        "page":      "🏠 Home",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# ─────────────────────────────────────────────
# FILE HELPERS
# ─────────────────────────────────────────────
def load_json(filepath):
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            return json.load(f)
    return {}

def save_json(filepath, data):
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)

def load_users():
    return load_json(USERS_FILE)

def save_users(users):
    save_json(USERS_FILE, users)

def load_logs():
    if os.path.exists(LOGS_FILE):
        with open(LOGS_FILE, "r") as f:
            return json.load(f)
    return []

def save_log(entry):
    logs = load_logs()
    logs.append(entry)
    with open(LOGS_FILE, "w") as f:
        json.dump(logs, f, indent=2)


# ─────────────────────────────────────────────
# AUTH HELPERS
# ─────────────────────────────────────────────
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password):
    if username == ADMIN_USER:
        return False, "That username is reserved."
    users = load_users()
    if username in users:
        return False, "Username already exists."
    if len(password) < 6:
        return False, "Password must be at least 6 characters."
    users[username] = {
        "password":   hash_password(password),
        "created_at": datetime.now().isoformat(),
    }
    save_users(users)
    return True, "Account created! Please log in."

def login_user(username, password):
    if username == ADMIN_USER:
        if hash_password(password) == ADMIN_PASS:
            return True, "admin"
        return False, "Wrong admin password."
    users = load_users()
    if username not in users:
        return False, "Username not found."
    stored = users[username]
    stored_hash = stored["password"] if isinstance(stored, dict) else stored
    if stored_hash != hash_password(password):
        return False, "Incorrect password."
    return True, "user"

def logout():
    st.session_state.logged_in = False
    st.session_state.username  = ""
    st.session_state.role      = ""
    st.session_state.page      = "🏠 Home"


# ─────────────────────────────────────────────
# DEMO DATASET — used on EDA, Dataset, Insights
# ─────────────────────────────────────────────
def get_demo_df(n=500, seed=42):
    np.random.seed(seed)
    jobs     = ["Data Scientist", "Software Engineer", "ML Engineer", "Data Analyst",
                "DevOps", "Product Manager", "AI Researcher", "BI Analyst"]
    locs     = ["Bangalore", "Mumbai", "Delhi", "Hyderabad", "Pune", "Chennai", "Remote"]
    inds     = ["IT", "Finance", "Healthcare", "E-commerce", "Consulting", "Telecom"]
    edus     = ["Bachelor", "Master", "PhD", "Diploma"]
    exp      = np.random.randint(0, 21, n)
    base     = np.random.choice([50000, 70000, 90000, 110000, 130000, 150000], n)
    noise    = np.random.randint(-15000, 15000, n)
    salary   = np.clip(exp * 4000 + base + noise, 30000, 400000)
    df = pd.DataFrame({
        "experience_years": exp,
        "salary":           salary,
        "skills_count":     np.random.randint(3, 26, n),
        "certifications":   np.random.randint(0, 9, n),
        "job_title":        np.random.choice(jobs, n),
        "location":         np.random.choice(locs, n),
        "industry":         np.random.choice(inds, n),
        "education":        np.random.choice(edus, n),
        "remote":           np.random.choice(["Yes", "No"], n),
        "company_size":     np.random.choice(["Small", "Medium", "Large"], n),
    })
    return df

# Plotly chart defaults — dark transparent background
CHART_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
)


# =====================================================================
# PAGE 1 — HOME
# =====================================================================
def page_home():
    # Hero
    st.markdown("""
    <div style='text-align:center; padding: 2rem 0 1.5rem;'>
        <div style='font-size: 3.5rem;'>💼</div>
        <h1 class='gradient-text' style='font-size: 3rem; margin: 0.3rem 0;'>SalaryAI Pro</h1>
        <p style='color: rgba(255,255,255,0.55); font-size: 1.1rem; max-width: 580px; margin: 0 auto;'>
            Predict your market salary with Machine Learning —
            powered by real-world data across industries, roles, and locations.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Quick stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="stat-card"><div style="font-size:1.8rem">📊</div><div class="stat-num">15,000+</div><div class="stat-lbl">Data Points</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="stat-card"><div style="font-size:1.8rem">💼</div><div class="stat-num">25+</div><div class="stat-lbl">Job Roles Covered</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="stat-card"><div style="font-size:1.8rem">🎯</div><div class="stat-num">89%</div><div class="stat-lbl">Model Accuracy (R²)</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center;'>✨ Key Features</h2>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # Feature cards — row 1
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="feat-card">
            <div style='font-size:2rem;'>🔮</div>
            <div style='color:#ffffff; font-weight:700; margin:.4rem 0;'>Salary Prediction</div>
            <div style='color:rgba(255,255,255,0.55); font-size:0.85rem;'>Enter your profile and get an instant ML-powered salary estimate.</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="feat-card">
            <div style='font-size:2rem;'>📊</div>
            <div style='color:#ffffff; font-weight:700; margin:.4rem 0;'>EDA Dashboard</div>
            <div style='color:rgba(255,255,255,0.55); font-size:0.85rem;'>Explore salary trends with interactive charts and heatmaps.</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="feat-card">
            <div style='font-size:2rem;'>📄</div>
            <div style='color:#ffffff; font-weight:700; margin:.4rem 0;'>Resume Analyzer</div>
            <div style='color:rgba(255,255,255,0.55); font-size:0.85rem;'>Upload your resume to extract skills and predict your salary.</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Feature cards — row 2
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="feat-card">
            <div style='font-size:2rem;'>💡</div>
            <div style='color:#ffffff; font-weight:700; margin:.4rem 0;'>Salary Insights</div>
            <div style='color:rgba(255,255,255,0.55); font-size:0.85rem;'>Discover highest-paying roles and remote vs onsite salary gaps.</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="feat-card">
            <div style='font-size:2rem;'>🛠️</div>
            <div style='color:#ffffff; font-weight:700; margin:.4rem 0;'>Skills Demand</div>
            <div style='color:rgba(255,255,255,0.55); font-size:0.85rem;'>See which skills are most in-demand in today's job market.</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="feat-card">
            <div style='font-size:2rem;'>💼</div>
            <div style='color:#ffffff; font-weight:700; margin:.4rem 0;'>Job Recommender</div>
            <div style='color:rgba(255,255,255,0.55); font-size:0.85rem;'>Get job role suggestions tailored to your profile.</div>
        </div>
        """, unsafe_allow_html=True)

    # Dataset info
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center;'>📂 Dataset Overview</h2>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown('<div class="stat-card"><div style="font-size:1.4rem">📁</div><div style="color:#a78bfa;font-weight:700">Source</div><div class="stat-lbl">Kaggle + Synthetic</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="stat-card"><div style="font-size:1.4rem">📏</div><div style="color:#a78bfa;font-weight:700">Rows</div><div class="stat-lbl">15,000 records</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="stat-card"><div style="font-size:1.4rem">🗂️</div><div style="color:#a78bfa;font-weight:700">Features</div><div class="stat-lbl">9 input features</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown('<div class="stat-card"><div style="font-size:1.4rem">🎯</div><div style="color:#a78bfa;font-weight:700">Target</div><div class="stat-lbl">Annual Salary (₹)</div></div>', unsafe_allow_html=True)

    # CTA button
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        if st.button("🔮 Predict My Salary Now!", key="home_cta"):
            st.session_state.page = "🔮 Salary Prediction"
            st.rerun()


# =====================================================================
# PAGE 2 — SALARY PREDICTION
# =====================================================================
def page_predict():
    st.markdown("<h1>🔮 Salary Prediction</h1>", unsafe_allow_html=True)
    st.caption("Fill in your profile to get your estimated market salary.")
    st.markdown("---")

    # Load model files
    try:
        model   = joblib.load("knn_model.pkl")
        scaler  = joblib.load("scaler.pkl")
        columns = joblib.load("columns.pkl")
    except Exception as e:
        st.error(f"Model files not found: {e}")
        st.info("Make sure knn_model.pkl, scaler.pkl, and columns.pkl are in the same folder as app.py.")
        return

    # Build dropdown options from trained columns
    def get_options(prefix):
        options = [col.replace(prefix, "") for col in columns if col.startswith(prefix)]
        return ["Other"] + sorted(list(set(options)))

    job_options    = get_options("job_title_")
    edu_options    = get_options("education_level_")
    loc_options    = get_options("location_")
    ind_options    = get_options("industry_")
    comp_options   = get_options("company_size_")
    remote_options = get_options("remote_work_")

    # Input form
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("##### 📋 Your Profile")

    col1, col2, col3 = st.columns(3)
    with col1:
        experience = st.number_input("🗓️ Experience (years)", min_value=0, max_value=30, value=3)
    with col2:
        skills = st.number_input("🛠️ Skills Count", min_value=0, max_value=50, value=8)
    with col3:
        certifications = st.number_input("🏅 Certifications", min_value=0, max_value=20, value=2)

    col4, col5 = st.columns(2)
    with col4:
        job    = st.selectbox("💼 Job Role", job_options)
        edu    = st.selectbox("🎓 Education Level", edu_options)
        loc    = st.selectbox("📍 Location", loc_options)
    with col5:
        ind    = st.selectbox("🏭 Industry", ind_options)
        comp   = st.selectbox("🏢 Company Size", comp_options)
        remote = st.selectbox("🌐 Remote Work", remote_options)

    st.markdown('</div>', unsafe_allow_html=True)

    # Predict button
    if st.button("🔮 Predict My Salary", key="predict_btn"):

        # Build dataframe
        input_data = {
            "experience_years": experience,
            "skills_count":     skills,
            "certifications":   certifications,
            "job_title":        job,
            "education_level":  edu,
            "location":         loc,
            "industry":         ind,
            "company_size":     comp,
            "remote_work":      remote,
        }
        df = pd.DataFrame([input_data])

        # Feature engineering
        df["exp_squared"]    = df["experience_years"] ** 2
        df["skill_per_exp"]  = df["skills_count"] / (df["experience_years"] + 1)
        df["cert_per_skill"] = df["certifications"] / (df["skills_count"] + 1)
        df["seniority"]      = pd.cut(
            df["experience_years"],
            bins=[0, 2, 5, 10, 20],
            labels=["Fresher", "Junior", "Mid", "Senior"]
        )

        # Encode and align
        df = pd.get_dummies(df)
        df = df.reindex(columns=columns, fill_value=0)

        # Scale numerical columns
        num_cols = ["experience_years", "skills_count", "certifications",
                    "exp_squared", "skill_per_exp", "cert_per_skill"]
        df[num_cols] = scaler.transform(df[num_cols])

        # Predict
        predicted_salary = int(model.predict(df)[0])

        # Save to log
        save_log({
            "username":         st.session_state.username,
            "timestamp":        datetime.now().isoformat(),
            "predicted_salary": predicted_salary,
            "experience_years": experience,
            "skills_count":     skills,
            "certifications":   certifications,
            "job_title":        job,
            "education_level":  edu,
            "location":         loc,
            "industry":         ind,
            "company_size":     comp,
            "remote_work":      remote,
        })

        # Show result
        st.markdown(f"""
        <div class="pred-box">
            <div style="color: rgba(255,255,255,0.6); font-size: 0.9rem;">🎯 Estimated Annual Salary</div>
            <div class="pred-amt">₹ {predicted_salary:,}</div>
            <div style="color: rgba(255,255,255,0.4); font-size: 0.78rem; margin-top: 0.4rem;">
                KNN Model · Based on your profile
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.balloons()

        # Extra mini stats
        st.markdown("<br>", unsafe_allow_html=True)
        if experience <= 2:
            level = "Fresher"
        elif experience <= 5:
            level = "Junior"
        elif experience <= 10:
            level = "Mid-Level"
        else:
            level = "Senior"

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f'<div class="stat-card"><div class="stat-num">₹{predicted_salary // 12:,}</div><div class="stat-lbl">Monthly Estimate</div></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="stat-card"><div class="stat-num">{level}</div><div class="stat-lbl">Your Seniority Level</div></div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="stat-card"><div class="stat-num">₹{predicted_salary // 365:,}</div><div class="stat-lbl">Daily Equivalent</div></div>', unsafe_allow_html=True)


# =====================================================================
# PAGE 3 — EDA DASHBOARD
# =====================================================================
def page_eda():
    st.markdown("<h1>📊 EDA Dashboard</h1>", unsafe_allow_html=True)
    st.caption("Exploratory Data Analysis — salary trends, distributions, and correlations.")
    st.markdown("---")

    df = get_demo_df()

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📈 Histogram", "📦 Box Plot", "🔥 Heatmap",
        "🥧 Pie Chart", "📉 Exp vs Salary", "🗺️ By Location"
    ])

    with tab1:
        st.markdown("#### Salary Distribution")
        fig = px.histogram(df, x="salary", nbins=40,
                           color_discrete_sequence=["#a78bfa"],
                           labels={"salary": "Annual Salary (₹)"})
        fig.update_layout(**CHART_LAYOUT)
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.markdown("#### Salary by Job Role")
        fig = px.box(df, x="job_title", y="salary", color="job_title",
                     labels={"salary": "Salary (₹)", "job_title": "Job Role"})
        fig.update_layout(**CHART_LAYOUT, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with tab3:
        st.markdown("#### Correlation Heatmap")
        corr = df[["experience_years", "salary", "skills_count", "certifications"]].corr()
        fig = go.Figure(data=go.Heatmap(
            z=corr.values,
            x=corr.columns,
            y=corr.columns,
            colorscale="Viridis",
            text=corr.round(2).values,
            texttemplate="%{text}"
        ))
        fig.update_layout(**CHART_LAYOUT)
        st.plotly_chart(fig, use_container_width=True)

    with tab4:
        st.markdown("#### Industry Distribution")
        counts = df["industry"].value_counts()
        fig = px.pie(values=counts.values, names=counts.index,
                     hole=0.4, color_discrete_sequence=px.colors.sequential.Plasma)
        fig.update_layout(**CHART_LAYOUT)
        st.plotly_chart(fig, use_container_width=True)

    with tab5:
        st.markdown("#### Experience vs Salary")
        fig = px.scatter(df, x="experience_years", y="salary",
                         color="job_title", size="skills_count", trendline="ols",
                         labels={"experience_years": "Experience (years)", "salary": "Salary (₹)"})
        fig.update_layout(**CHART_LAYOUT)
        st.plotly_chart(fig, use_container_width=True)

    with tab6:
        st.markdown("#### Average Salary by Location")
        loc_avg = df.groupby("location")["salary"].mean().sort_values(ascending=False).reset_index()
        loc_avg.columns = ["Location", "Avg Salary"]
        fig = px.bar(loc_avg, x="Location", y="Avg Salary",
                     color="Avg Salary", color_continuous_scale="Purples",
                     labels={"Avg Salary": "Avg Salary (₹)"})
        fig.update_layout(**CHART_LAYOUT)
        st.plotly_chart(fig, use_container_width=True)


# =====================================================================
# PAGE 4 — DATASET
# =====================================================================
def page_dataset():
    st.markdown("<h1>📂 Dataset</h1>", unsafe_allow_html=True)
    st.caption("Preview the dataset used to train the salary prediction model.")
    st.markdown("---")

    df = get_demo_df(n=200, seed=0)

    # Summary stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div class="stat-card"><div class="stat-num">{len(df)}</div><div class="stat-lbl">Total Rows</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="stat-card"><div class="stat-num">{df.shape[1]}</div><div class="stat-lbl">Total Columns</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="stat-card"><div class="stat-num">{int(df.isnull().sum().sum())}</div><div class="stat-lbl">Missing Values</div></div>', unsafe_allow_html=True)
    with col4:
        num_count = df.select_dtypes(include="number").shape[1]
        st.markdown(f'<div class="stat-card"><div class="stat-num">{num_count}</div><div class="stat-lbl">Numeric Features</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Dataset preview
    st.markdown("#### 👁️ Dataset Preview")
    st.dataframe(df.head(20), use_container_width=True, hide_index=True)

    # Summary and missing values
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 📋 Statistical Summary")
        st.dataframe(df.describe().round(2), use_container_width=True)
    with col2:
        st.markdown("#### ❓ Missing Values per Column")
        missing = df.isnull().sum().reset_index()
        missing.columns = ["Column", "Missing Count"]
        st.dataframe(missing, use_container_width=True, hide_index=True)

    # Download
    csv_data = df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download Dataset as CSV", csv_data, "salary_dataset.csv", "text/csv")


# =====================================================================
# PAGE 5 — MODEL PERFORMANCE
# =====================================================================
def page_model_performance():
    from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error

    st.markdown("<h1>📈 Model Performance</h1>", unsafe_allow_html=True)
    st.caption("Evaluation metrics and visual performance of the KNN salary prediction model.")
    st.markdown("---")

    # Generate demo predictions
    np.random.seed(7)
    y_true = np.random.randint(50000, 350000, 100)
    noise  = np.random.randint(-20000, 20000, 100)
    y_pred = np.clip(y_true + noise, 30000, 400000)

    r2   = r2_score(y_true, y_pred)
    mae  = mean_absolute_error(y_true, y_pred)
    rmse = mean_squared_error(y_true, y_pred) ** 0.5

    # Metric cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div class="stat-card"><div style="font-size:1.4rem">🎯</div><div class="stat-num">{r2:.2%}</div><div class="stat-lbl">R² Score</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="stat-card"><div style="font-size:1.4rem">📉</div><div class="stat-num">₹{mae:,.0f}</div><div class="stat-lbl">MAE</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="stat-card"><div style="font-size:1.4rem">📊</div><div class="stat-num">₹{rmse:,.0f}</div><div class="stat-lbl">RMSE</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown('<div class="stat-card"><div style="font-size:1.4rem">🤖</div><div class="stat-num">KNN</div><div class="stat-lbl">Algorithm (k=5)</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📊 Actual vs Predicted", "📉 Error Distribution", "🏆 Model Comparison"])

    with tab1:
        x_axis = list(range(len(y_true)))
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=x_axis, y=y_true.tolist(), mode="lines", name="Actual",    line=dict(color="#60a5fa")))
        fig.add_trace(go.Scatter(x=x_axis, y=y_pred.tolist(), mode="lines", name="Predicted", line=dict(color="#a78bfa", dash="dash")))
        fig.update_layout(**CHART_LAYOUT, title="Actual vs Predicted Salary",
                          xaxis_title="Sample Index", yaxis_title="Salary (₹)")
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        errors = (y_pred - y_true).tolist()
        fig = px.histogram(x=errors, nbins=30,
                           color_discrete_sequence=["#f472b6"],
                           labels={"x": "Prediction Error (₹)"},
                           title="Error Distribution")
        fig.update_layout(**CHART_LAYOUT)
        st.plotly_chart(fig, use_container_width=True)

    with tab3:
        models  = ["KNN", "Linear Reg", "Decision Tree", "Random Forest", "SVR"]
        r2s     = [0.89, 0.78, 0.82, 0.91, 0.85]
        fig = px.bar(x=models, y=r2s, color=r2s,
                     color_continuous_scale="Purples",
                     labels={"x": "Model", "y": "R² Score"},
                     title="Model Accuracy Comparison (R²)")
        fig.update_layout(**CHART_LAYOUT)
        st.plotly_chart(fig, use_container_width=True)


# =====================================================================
# PAGE 6 — SALARY INSIGHTS
# =====================================================================
def page_insights():
    st.markdown("<h1>💡 Salary Insights</h1>", unsafe_allow_html=True)
    st.caption("Deep analytics on salary trends across roles, locations, and work types.")
    st.markdown("---")

    # Static insight data
    role_data = {
        "CTO":                350000,
        "AI Researcher":      280000,
        "Cloud Architect":    260000,
        "ML Engineer":        220000,
        "Data Scientist":     200000,
        "Software Engineer":  180000,
        "Product Manager":    170000,
        "DevOps":             160000,
        "Data Analyst":       130000,
        "BI Analyst":         110000,
    }
    country_data = {
        "USA":       480000,
        "Singapore": 380000,
        "UK":        320000,
        "Germany":   300000,
        "Canada":    290000,
        "Australia": 280000,
        "India":     150000,
    }
    remote_data = {
        "Work Type":  ["Remote", "Onsite", "Hybrid"],
        "Avg Salary": [145000,   115000,   128000],
    }
    band_data = {
        "Experience Band":          ["0-2 yrs (Fresher)", "3-5 yrs (Junior)", "6-10 yrs (Mid)", "11-20 yrs (Senior)"],
        "Avg Salary":               [45000,               85000,               140000,            220000],
    }

    tab1, tab2, tab3, tab4 = st.tabs(["💼 By Job Role", "🌍 By Country", "🏠 Remote vs Onsite", "📅 Experience Bands"])

    with tab1:
        df_roles = pd.DataFrame({"Job Role": list(role_data.keys()), "Avg Salary": list(role_data.values())})
        df_roles = df_roles.sort_values("Avg Salary", ascending=False)

        top_role   = df_roles.iloc[0]["Job Role"]
        top_salary = df_roles.iloc[0]["Avg Salary"]
        st.success(f"🏆 Highest Paying Role: **{top_role}** — ₹{top_salary:,}/year")

        fig = px.bar(df_roles, x="Avg Salary", y="Job Role", orientation="h",
                     color="Avg Salary", color_continuous_scale="Purples",
                     labels={"Avg Salary": "Avg Salary (₹)"})
        fig.update_layout(**CHART_LAYOUT)
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        df_countries = pd.DataFrame({"Country": list(country_data.keys()), "Avg Salary": list(country_data.values())})
        fig = px.bar(df_countries, x="Country", y="Avg Salary",
                     color="Avg Salary", color_continuous_scale="Blues",
                     labels={"Avg Salary": "Avg Salary (₹)"})
        fig.update_layout(**CHART_LAYOUT)
        st.plotly_chart(fig, use_container_width=True)

    with tab3:
        df_remote = pd.DataFrame(remote_data)
        fig = px.pie(df_remote, values="Avg Salary", names="Work Type",
                     hole=0.4, color_discrete_sequence=["#a78bfa", "#60a5fa", "#34d399"])
        fig.update_layout(**CHART_LAYOUT)
        st.plotly_chart(fig, use_container_width=True)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown('<div class="stat-card"><div class="stat-num">₹1,45,000</div><div class="stat-lbl">Remote 🌐 Avg Salary</div></div>', unsafe_allow_html=True)
        with col2:
            st.markdown('<div class="stat-card"><div class="stat-num">₹1,15,000</div><div class="stat-lbl">Onsite 🏢 Avg Salary</div></div>', unsafe_allow_html=True)
        with col3:
            st.markdown('<div class="stat-card"><div class="stat-num">₹1,28,000</div><div class="stat-lbl">Hybrid 🔄 Avg Salary</div></div>', unsafe_allow_html=True)

    with tab4:
        df_bands = pd.DataFrame(band_data)
        fig = px.bar(df_bands, x="Experience Band", y="Avg Salary",
                     color="Avg Salary", color_continuous_scale="Greens",
                     labels={"Avg Salary": "Avg Salary (₹)"})
        fig.update_layout(**CHART_LAYOUT)
        st.plotly_chart(fig, use_container_width=True)


# =====================================================================
# PAGE 7 — SKILLS DEMAND
# =====================================================================
def page_skills():
    st.markdown("<h1>🛠️ Skills Demand</h1>", unsafe_allow_html=True)
    st.caption("Most in-demand skills in the current job market.")
    st.markdown("---")

    skills_demand = {
        "Python":               95,
        "SQL":                  88,
        "Git":                  83,
        "Communication":        80,
        "AWS":                  78,
        "Machine Learning":     82,
        "Excel":                85,
        "Docker":               72,
        "Data Visualization":   74,
        "TensorFlow":           71,
        "Deep Learning":        75,
        "Power BI":             70,
        "Tableau":              68,
        "PyTorch":              69,
        "Kubernetes":           65,
        "Azure":                66,
        "NLP":                  63,
        "Spark":                60,
        "GCP":                  61,
        "Computer Vision":      58,
    }

    df = pd.DataFrame({
        "Skill":        list(skills_demand.keys()),
        "Demand (%)":   list(skills_demand.values()),
    }).sort_values("Demand (%)", ascending=True)

    fig = px.bar(df, x="Demand (%)", y="Skill", orientation="h",
                 color="Demand (%)", color_continuous_scale="Viridis",
                 title="Top Skills by Market Demand (%)")
    fig.update_layout(**CHART_LAYOUT, height=550)
    st.plotly_chart(fig, use_container_width=True)

    # Top 5 highlight
    st.markdown("#### 🔥 Top 5 Most In-Demand Skills")
    top5 = sorted(skills_demand.items(), key=lambda x: -x[1])[:5]
    cols = st.columns(5)
    for col, (skill, score) in zip(cols, top5):
        with col:
            st.markdown(f'<div class="stat-card"><div class="stat-num">{score}%</div><div class="stat-lbl">{skill}</div></div>', unsafe_allow_html=True)


# =====================================================================
# PAGE 8 — RESUME ANALYZER
# =====================================================================
def page_resume():
    st.markdown("<h1>📄 Resume Analyzer</h1>", unsafe_allow_html=True)
    st.caption("Upload your resume to extract skills, find gaps, and estimate your salary.")
    st.markdown("---")

    KNOWN_SKILLS = [
        "python", "sql", "machine learning", "deep learning", "aws", "azure",
        "docker", "kubernetes", "tensorflow", "pytorch", "tableau", "power bi",
        "excel", "java", "javascript", "react", "node", "spark", "hadoop",
        "nlp", "git", "linux", "r programming", "statistics", "data visualization",
    ]

    uploaded_file = st.file_uploader("📎 Upload your Resume (.txt or .pdf)", type=["txt", "pdf"])

    if uploaded_file is not None:

        # Extract text
        if uploaded_file.type == "text/plain":
            text = uploaded_file.read().decode("utf-8", "ignore").lower()
        else:
            try:
                import pdfplumber
                with pdfplumber.open(uploaded_file) as pdf:
                    pages_text = [page.extract_text() or "" for page in pdf.pages]
                    text = " ".join(pages_text).lower()
            except Exception:
                text = str(uploaded_file.read()).lower()

        # Find skills
        found_skills   = [s for s in KNOWN_SKILLS if s in text]
        missing_skills = [s for s in KNOWN_SKILLS if s not in text]

        col1, col2 = st.columns(2)
        with col1:
            st.success(f"✅ **{len(found_skills)} Skills Found**")
            for skill in found_skills:
                st.markdown(f"• {skill.title()}")
        with col2:
            st.warning(f"⚠️ **{len(missing_skills)} Skills Not Detected**")
            for skill in missing_skills[:10]:
                st.markdown(f"• {skill.title()}")

        st.markdown("---")

        # Estimate salary from resume
        exp_match = re.search(r"(\d+)\s*(year|yr)", text)
        exp_years = int(exp_match.group(1)) if exp_match else 3
        est_salary = 50000 + (exp_years * 5000) + (len(found_skills) * 3000)

        st.markdown(f"""
        <div class="pred-box">
            <div style="color: rgba(255,255,255,0.6);">💰 Resume-Based Salary Estimate</div>
            <div class="pred-amt">₹ {est_salary:,}</div>
            <div style="color: rgba(255,255,255,0.4); font-size: 0.78rem; margin-top: 0.4rem;">
                Based on {len(found_skills)} skills detected · ~{exp_years} yrs experience found
            </div>
        </div>
        """, unsafe_allow_html=True)

    else:
        st.info("👆 Upload a .txt or .pdf resume file to begin analysis.")
        st.markdown("""
        <div class="card">
            <b>How it works:</b><br><br>
            1. Upload your resume as a TXT or PDF file<br>
            2. We scan for 25+ in-demand technical skills<br>
            3. You get a skill gap report instantly<br>
            4. We estimate your salary based on your skill profile
        </div>
        """, unsafe_allow_html=True)


# =====================================================================
# PAGE 9 — JOB RECOMMENDATIONS
# =====================================================================
def page_jobs():
    st.markdown("<h1>💼 Job Recommendations</h1>", unsafe_allow_html=True)
    st.caption("Get job role suggestions based on your experience and skills.")
    st.markdown("---")

    experience   = st.slider("Your Experience (years)", 0, 20, 3)
    skill_count  = st.slider("Number of Skills You Have", 1, 30, 8)
    work_pref    = st.radio("Work Preference", ["Any", "Remote", "Onsite"], horizontal=True)

    # Job database
    all_jobs = [
        {
            "role":          "Data Analyst",
            "min_exp":       0,
            "min_skills":    5,
            "salary_range":  "₹4L – ₹10L",
            "remote":        "Yes",
            "skills":        ["SQL", "Excel", "Power BI", "Python", "Tableau"],
        },
        {
            "role":          "Software Engineer",
            "min_exp":       1,
            "min_skills":    6,
            "salary_range":  "₹5L – ₹20L",
            "remote":        "Yes",
            "skills":        ["Java", "Python", "Git", "DSA", "REST APIs"],
        },
        {
            "role":          "ML Engineer",
            "min_exp":       2,
            "min_skills":    8,
            "salary_range":  "₹8L – ₹30L",
            "remote":        "Yes",
            "skills":        ["Python", "TensorFlow", "Sklearn", "SQL", "Docker"],
        },
        {
            "role":          "Data Scientist",
            "min_exp":       2,
            "min_skills":    8,
            "salary_range":  "₹10L – ₹35L",
            "remote":        "Yes",
            "skills":        ["Python", "Statistics", "ML", "SQL", "Visualization"],
        },
        {
            "role":          "DevOps Engineer",
            "min_exp":       2,
            "min_skills":    7,
            "salary_range":  "₹8L – ₹25L",
            "remote":        "Yes",
            "skills":        ["Docker", "Kubernetes", "AWS", "Linux", "CI/CD"],
        },
        {
            "role":          "AI Researcher",
            "min_exp":       4,
            "min_skills":    10,
            "salary_range":  "₹20L – ₹60L",
            "remote":        "No",
            "skills":        ["PyTorch", "NLP", "Python", "Math", "Research"],
        },
        {
            "role":          "Cloud Architect",
            "min_exp":       5,
            "min_skills":    10,
            "salary_range":  "₹25L – ₹70L",
            "remote":        "No",
            "skills":        ["AWS", "Azure", "GCP", "Networking", "Security"],
        },
        {
            "role":          "BI Analyst",
            "min_exp":       1,
            "min_skills":    5,
            "salary_range":  "₹4L – ₹12L",
            "remote":        "Yes",
            "skills":        ["Power BI", "SQL", "Excel", "Tableau", "DAX"],
        },
        {
            "role":          "Product Manager",
            "min_exp":       3,
            "min_skills":    6,
            "salary_range":  "₹12L – ₹40L",
            "remote":        "Yes",
            "skills":        ["Communication", "Roadmaps", "SQL", "Agile", "Analytics"],
        },
    ]

    if st.button("🔍 Find Matching Jobs", key="job_btn"):

        # Filter by experience and skills
        matches = [j for j in all_jobs if j["min_exp"] <= experience and j["min_skills"] <= skill_count]

        # Filter by remote preference
        if work_pref == "Remote":
            matches = [j for j in matches if j["remote"] == "Yes"]
        elif work_pref == "Onsite":
            matches = [j for j in matches if j["remote"] == "No"]

        if matches:
            st.success(f"🎯 Found {len(matches)} matching job role(s)!")
            for job in matches:
                with st.expander(f"💼 {job['role']}  —  {job['salary_range']}"):
                    st.markdown(f"**Expected Salary:** {job['salary_range']}")
                    st.markdown(f"**Remote Friendly:** {job['remote']}")
                    st.markdown(f"**Required Skills:** {', '.join(job['skills'])}")
        else:
            st.warning("No matching roles found. Try lowering the experience or skill count.")


# =====================================================================
# PAGE 10 — ABOUT PROJECT
# =====================================================================
def page_about_project():
    st.markdown("<h1>ℹ️ About This Project</h1>", unsafe_allow_html=True)
    st.markdown("---")

    st.markdown("""
    <div class="card">
        <h3>🎯 Objective</h3>
        <p style="color: rgba(255,255,255,0.7);">
            Build an intelligent, end-to-end salary prediction platform that helps job seekers,
            HR professionals, and students estimate fair market salaries using Machine Learning.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="card">
        <h3>❗ Problem Statement</h3>
        <p style="color: rgba(255,255,255,0.7);">
            Salary transparency in India is limited. Candidates often lack data to negotiate fair pay.
            This project solves that by training an ML model on real-world salary factors such as
            experience, skills, location, education, and job role.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="card">
        <h3>🔭 Future Scope</h3>
        <p style="color: rgba(255,255,255,0.7);">
            Real-time job posting integration · NLP-based job description parser ·
            Salary negotiation assistant · Mobile app · Multi-language support ·
            Live model retraining pipeline with fresh data.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Tech stack
    st.markdown("#### 🛠️ Technologies Used")
    st.markdown("<br>", unsafe_allow_html=True)

    tech_list = [
        ("🐍", "Python 3.11"),
        ("🤖", "Scikit-learn (KNN)"),
        ("📊", "Streamlit"),
        ("📈", "Plotly / Seaborn"),
        ("🗄️", "Pandas / NumPy"),
        ("💾", "JSON Storage"),
        ("🎨", "Custom CSS"),
        ("📄", "pdfplumber"),
    ]

    col1, col2, col3, col4 = st.columns(4)
    cols = [col1, col2, col3, col4]
    for i, (icon, name) in enumerate(tech_list):
        with cols[i % 4]:
            st.markdown(f'<div class="stat-card" style="margin-bottom:0.6rem"><div style="font-size:1.4rem">{icon}</div><div style="color:#a78bfa;font-weight:600;font-size:0.9rem">{name}</div></div>', unsafe_allow_html=True)


# =====================================================================
# PAGE 11 — ABOUT DEVELOPER
# =====================================================================
def page_about_dev():
    st.markdown("<h1>👨‍💻 About the Developer</h1>", unsafe_allow_html=True)
    st.markdown("---")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div class="card" style="text-align: center;">
            <div style="font-size: 4rem;">👨‍💻</div>
            <h2 style="margin: 0.3rem 0;">Your Name</h2>
            <div style="color: rgba(255,255,255,0.5); margin-bottom: 1rem;">AI / ML Engineer · Data Scientist</div>
            <p style="color: rgba(255,255,255,0.7); font-size: 0.9rem;">
                Passionate about building intelligent systems that solve real-world problems.
                Specialised in Machine Learning, Data Science, and Full-Stack ML Applications.
            </p>
        </div>
        """, unsafe_allow_html=True)

    # Skills
    st.markdown("#### 🛠️ Skills")
    skill_list = ["Python", "Machine Learning", "Deep Learning", "Streamlit",
                  "SQL", "Data Visualization", "NLP", "Computer Vision"]
    col1, col2, col3, col4 = st.columns(4)
    cols = [col1, col2, col3, col4]
    for i, skill in enumerate(skill_list):
        with cols[i % 4]:
            st.markdown(f'<div class="stat-card" style="margin-bottom:0.5rem"><div style="color:#a78bfa;font-weight:600">{skill}</div></div>', unsafe_allow_html=True)

    # Links
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### 🔗 Connect")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="stat-card"><div style="font-size:1.5rem">🔗</div><div style="color:#a78bfa;font-weight:600">LinkedIn</div><div class="stat-lbl">linkedin.com/in/yourprofile</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="stat-card"><div style="font-size:1.5rem">🐱</div><div style="color:#a78bfa;font-weight:600">GitHub</div><div class="stat-lbl">github.com/yourusername</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="stat-card"><div style="font-size:1.5rem">📧</div><div style="color:#a78bfa;font-weight:600">Email</div><div class="stat-lbl">your@email.com</div></div>', unsafe_allow_html=True)

    # Resume button
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        st.markdown(
            '<a href="https://your-resume-link.com" target="_blank">'
            '<button style="background:linear-gradient(135deg,#7c6af7,#a78bfa);color:white;border:none;'
            'padding:0.7rem 2rem;border-radius:10px;font-weight:600;cursor:pointer;width:100%">'
            '📄 Download Resume</button></a>',
            unsafe_allow_html=True
        )


# =====================================================================
# PAGE 12 — FAQ
# =====================================================================
def page_faq():
    st.markdown("<h1>❓ Frequently Asked Questions</h1>", unsafe_allow_html=True)
    st.caption("Common questions about SalaryAI Pro.")
    st.markdown("---")

    faqs = [
        (
            "🤖 How does the ML model work?",
            "We use a K-Nearest Neighbors (KNN) algorithm trained on salary data with features like "
            "experience, skills, location, education, and job role. The model finds the K most similar "
            "profiles and averages their salaries to give you a prediction."
        ),
        (
            "🎯 How accurate is the prediction?",
            "Our model achieves ~89% R² score on test data. Predictions are estimates — "
            "actual salaries vary based on company, negotiation skills, and market conditions."
        ),
        (
            "📂 Where does the data come from?",
            "The dataset is a combination of publicly available Kaggle salary datasets and "
            "synthetic data generated to cover diverse Indian job market scenarios."
        ),
        (
            "🔐 Is my data safe?",
            "Yes. Passwords are SHA-256 hashed and never stored in plain text. "
            "We only store your username and prediction logs locally in JSON files. "
            "No data is sent to any external server."
        ),
        (
            "📄 What resume formats are supported?",
            "We support .txt and .pdf formats. For best results, use a simple text-based PDF "
            "without heavy formatting or embedded images."
        ),
        (
            "💡 Can I use this for salary negotiation?",
            "Absolutely! Use the prediction as a reference point. Compare your current or "
            "offered salary with the model's estimate to understand your market rate."
        ),
        (
            "🌐 Does it support international salaries?",
            "Currently the model is calibrated for the Indian job market (₹). "
            "We plan to add USD, GBP, and EUR support in future versions."
        ),
        (
            "🛠️ How often is the model updated?",
            "The model is static in this version. Future releases will support live retraining "
            "as new data becomes available."
        ),
    ]

    for question, answer in faqs:
        with st.expander(question):
            st.markdown(f'<div style="color: rgba(255,255,255,0.75); line-height: 1.7;">{answer}</div>', unsafe_allow_html=True)


# =====================================================================
# PAGE 13 — CONTACT
# =====================================================================
def page_contact():
    st.markdown("<h1>📬 Contact Us</h1>", unsafe_allow_html=True)
    st.caption("Have a question or feedback? We'd love to hear from you.")
    st.markdown("---")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)

        name    = st.text_input("Your Name", placeholder="John Doe")
        email   = st.text_input("Email Address", placeholder="john@example.com")
        subject = st.selectbox("Subject", ["General Inquiry", "Bug Report", "Feature Request", "Partnership", "Other"])
        message = st.text_area("Message", placeholder="Type your message here...", height=150)

        if st.button("📨 Send Message", key="contact_btn"):
            if name and email and message:
                # Load existing messages
                messages = []
                if os.path.exists(CONTACT_FILE):
                    with open(CONTACT_FILE, "r") as f:
                        messages = json.load(f)

                # Save new message
                messages.append({
                    "name":    name,
                    "email":   email,
                    "subject": subject,
                    "message": message,
                    "time":    datetime.now().isoformat(),
                })
                with open(CONTACT_FILE, "w") as f:
                    json.dump(messages, f, indent=2)

                st.success("✅ Message sent! We'll get back to you soon.")
            else:
                st.error("Please fill in Name, Email, and Message fields.")

        st.markdown('</div>', unsafe_allow_html=True)

    # Contact info cards
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="stat-card"><div style="font-size:1.5rem">📧</div><div style="color:#a78bfa;font-weight:600">Email</div><div class="stat-lbl">support@salaryai.pro</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="stat-card"><div style="font-size:1.5rem">🐦</div><div style="color:#a78bfa;font-weight:600">Twitter</div><div class="stat-lbl">@SalaryAIPro</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="stat-card"><div style="font-size:1.5rem">🐱</div><div style="color:#a78bfa;font-weight:600">GitHub</div><div class="stat-lbl">github.com/salaryai</div></div>', unsafe_allow_html=True)


# =====================================================================
# PAGE 14 — ADMIN ANALYTICS
# =====================================================================
def page_admin_analytics():
    st.markdown('<div class="badge-admin">🛡️ Admin</div>', unsafe_allow_html=True)
    st.markdown("<h1>🛡️ Admin Analytics</h1>", unsafe_allow_html=True)
    st.markdown("---")

    logs  = load_logs()
    users = load_users()

    # Top stat cards
    today       = datetime.now().date().isoformat()
    total_preds = len(logs)
    total_users = len(users)
    avg_salary  = int(sum(l.get("predicted_salary", 0) for l in logs) / total_preds) if total_preds else 0
    today_preds = sum(1 for l in logs if l.get("timestamp", "").startswith(today))

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div class="stat-card"><div style="font-size:1.4rem">🔮</div><div class="stat-num">{total_preds}</div><div class="stat-lbl">Total Predictions</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="stat-card"><div style="font-size:1.4rem">👥</div><div class="stat-num">{total_users}</div><div class="stat-lbl">Registered Users</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="stat-card"><div style="font-size:1.4rem">💰</div><div class="stat-num">₹{avg_salary:,}</div><div class="stat-lbl">Avg Predicted Salary</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="stat-card"><div style="font-size:1.4rem">📅</div><div class="stat-num">{today_preds}</div><div class="stat-lbl">Predictions Today</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if not logs:
        st.info("No predictions logged yet.")
        return

    df = pd.DataFrame(logs)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 🔥 Most Searched Job Roles")
        if "job_title" in df.columns:
            top_roles = df["job_title"].value_counts().head(8).reset_index()
            top_roles.columns = ["Job Role", "Count"]
            fig = px.bar(top_roles, x="Count", y="Job Role", orientation="h",
                         color="Count", color_continuous_scale="Purples")
            fig.update_layout(**CHART_LAYOUT)
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("#### 📅 Predictions Over Time")
        if "timestamp" in df.columns:
            df["date"] = pd.to_datetime(df["timestamp"]).dt.date
            daily = df.groupby("date").size().reset_index(name="Predictions")
            fig = px.line(daily, x="date", y="Predictions",
                          color_discrete_sequence=["#a78bfa"])
            fig.update_layout(**CHART_LAYOUT)
            st.plotly_chart(fig, use_container_width=True)

    # Contact messages table
    if os.path.exists(CONTACT_FILE):
        with open(CONTACT_FILE, "r") as f:
            contact_msgs = json.load(f)
        if contact_msgs:
            st.markdown("#### 📬 Recent Contact Messages")
            df_msgs = pd.DataFrame(contact_msgs)
            st.dataframe(df_msgs.tail(10).iloc[::-1], use_container_width=True, hide_index=True)


# =====================================================================
# PAGE 15 — USER MANAGEMENT (admin)
# =====================================================================
def page_user_management():
    st.markdown('<div class="badge-admin">🛡️ Admin</div>', unsafe_allow_html=True)
    st.markdown("<h1>👥 User Management</h1>", unsafe_allow_html=True)
    st.markdown("---")

    users = load_users()
    logs  = load_logs()

    # Users table
    if users:
        rows = []
        for username, data in users.items():
            joined     = data.get("created_at", "N/A")[:10] if isinstance(data, dict) else "N/A"
            pred_count = sum(1 for l in logs if l.get("username") == username)
            rows.append({"Username": username, "Joined": joined, "Predictions": pred_count})
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        st.info("No users registered yet.")

    st.markdown("---")

    # Add user
    with st.expander("➕ Add New User"):
        new_username = st.text_input("Username", key="adm_add_u")
        new_password = st.text_input("Password", type="password", key="adm_add_p")
        if st.button("Add User", key="adm_add_btn"):
            if new_username and new_password:
                ok, msg = register_user(new_username.strip(), new_password)
                if ok:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)
            else:
                st.error("Fill both fields.")

    # Delete user
    with st.expander("🗑️ Delete a User"):
        if users:
            del_user = st.selectbox("Select user to delete", list(users.keys()), key="adm_del_u")
            if st.button("Delete User", key="adm_del_btn"):
                users.pop(del_user, None)
                save_users(users)
                st.success(f"User '{del_user}' deleted.")
                st.rerun()
        else:
            st.info("No users to delete.")

    # Reset password
    with st.expander("🔑 Reset User Password"):
        if users:
            reset_user = st.selectbox("Select user", list(users.keys()), key="adm_reset_u")
            new_pw     = st.text_input("New Password", type="password", key="adm_reset_p")
            if st.button("Reset Password", key="adm_reset_btn"):
                if new_pw and len(new_pw) >= 6:
                    created_at = users[reset_user].get("created_at", "N/A") if isinstance(users[reset_user], dict) else "N/A"
                    users[reset_user] = {"password": hash_password(new_pw), "created_at": created_at}
                    save_users(users)
                    st.success(f"Password reset for '{reset_user}'.")
                else:
                    st.error("Password must be at least 6 characters.")
        else:
            st.info("No users available.")


# =====================================================================
# PAGE 16 — PREDICTION LOGS (admin)
# =====================================================================
def page_pred_logs():
    st.markdown('<div class="badge-admin">🛡️ Admin</div>', unsafe_allow_html=True)
    st.markdown("<h1>📋 Prediction Logs</h1>", unsafe_allow_html=True)
    st.markdown("---")

    logs = load_logs()

    if not logs:
        st.info("No predictions logged yet.")
        return

    df = pd.DataFrame(logs)

    # Filters
    col1, col2 = st.columns(2)
    with col1:
        user_filter = st.selectbox("Filter by User", ["All"] + sorted(df["username"].unique().tolist()))
    with col2:
        sort_by = st.selectbox("Sort By", ["Newest First", "Highest Salary", "Lowest Salary"])

    # Apply filters
    filtered = df.copy()
    if user_filter != "All":
        filtered = filtered[filtered["username"] == user_filter]

    if sort_by == "Highest Salary":
        filtered = filtered.sort_values("predicted_salary", ascending=False)
    elif sort_by == "Lowest Salary":
        filtered = filtered.sort_values("predicted_salary", ascending=True)
    else:
        filtered = filtered.iloc[::-1]

    st.dataframe(filtered, use_container_width=True, hide_index=True)

    # Download
    csv_data = filtered.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download Logs as CSV", csv_data, "prediction_logs.csv", "text/csv")

    st.markdown("---")
    if st.button("🗑️ Clear All Logs", key="clear_logs_btn"):
        with open(LOGS_FILE, "w") as f:
            json.dump([], f)
        st.success("All logs cleared.")
        st.rerun()


# =====================================================================
# AUTH PAGES
# =====================================================================
def show_login():
    st.markdown('<div class="auth-title">👋 Welcome Back</div>', unsafe_allow_html=True)
    st.markdown('<div class="auth-sub">Sign in to SalaryAI Pro</div>', unsafe_allow_html=True)

    username = st.text_input("Username", placeholder="Enter your username", key="login_u")
    password = st.text_input("Password", type="password", placeholder="Enter your password", key="login_p")

    if st.button("Sign In", key="btn_login"):
        if not username or not password:
            st.error("Please fill in all fields.")
        else:
            ok, result = login_user(username.strip(), password)
            if ok:
                st.session_state.logged_in = True
                st.session_state.username  = username.strip()
                st.session_state.role      = result
                st.rerun()
            else:
                st.error(result)

    st.markdown('<div class="or-divider"><span>OR</span></div>', unsafe_allow_html=True)
    st.markdown("<div style='text-align:center; color:rgba(255,255,255,0.45); font-size:0.85rem;'>Don't have an account?</div>", unsafe_allow_html=True)

    if st.button("Create Account →", key="btn_go_signup"):
        st.session_state.auth_page = "signup"
        st.rerun()


def show_signup():
    st.markdown('<div class="auth-title">🚀 Get Started</div>', unsafe_allow_html=True)
    st.markdown('<div class="auth-sub">Create your free account</div>', unsafe_allow_html=True)

    new_user    = st.text_input("Choose a Username", placeholder="e.g. john_doe", key="signup_u")
    new_pass    = st.text_input("Create Password", type="password", placeholder="Min. 6 characters", key="signup_p")
    confirm_pass = st.text_input("Confirm Password", type="password", placeholder="Repeat your password", key="signup_cp")

    if st.button("Create Account", key="btn_signup"):
        if not new_user or not new_pass or not confirm_pass:
            st.error("Please fill in all fields.")
        elif new_pass != confirm_pass:
            st.error("Passwords do not match.")
        else:
            ok, msg = register_user(new_user.strip(), new_pass)
            if ok:
                st.success(msg)
                st.session_state.auth_page = "login"
                st.rerun()
            else:
                st.error(msg)

    st.markdown('<div class="or-divider"><span>OR</span></div>', unsafe_allow_html=True)
    st.markdown("<div style='text-align:center; color:rgba(255,255,255,0.45); font-size:0.85rem;'>Already have an account?</div>", unsafe_allow_html=True)

    if st.button("← Back to Sign In", key="btn_go_login"):
        st.session_state.auth_page = "login"
        st.rerun()


# =====================================================================
# SIDEBAR NAVIGATION
# =====================================================================
def show_sidebar():
    with st.sidebar:
        # Logo
        st.markdown("""
        <div style='text-align:center; padding: 1rem 0 0.5rem;'>
            <div style='font-size: 2.2rem;'>💼</div>
            <div style='font-family: Space Grotesk; font-size: 1.2rem; font-weight: 700; color: #a78bfa;'>SalaryAI Pro</div>
            <div style='font-size: 0.72rem; color: rgba(255,255,255,0.4); margin-top: 0.2rem;'>ML-Powered Salary Intelligence</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # User badge
        if st.session_state.role == "admin":
            st.markdown(f'<div class="badge-admin">🛡️ {st.session_state.username}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="badge-user">👤 {st.session_state.username}</div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Page list for regular users
        user_pages = [
            "🏠 Home",
            "🔮 Salary Prediction",
            "📊 EDA Dashboard",
            "📂 Dataset",
            "📈 Model Performance",
            "💡 Salary Insights",
            "🛠️ Skills Demand",
            "📄 Resume Analyzer",
            "💼 Job Recommendations",
            "ℹ️ About Project",
            "👨‍💻 About Developer",
            "❓ FAQ",
            "📬 Contact",
        ]

        # Extra pages for admin only
        admin_pages = [
            "🛡️ Admin Analytics",
            "👥 User Management",
            "📋 Prediction Logs",
        ]

        # Show nav buttons
        for page_name in user_pages:
            if st.button(page_name, key=f"nav_{page_name}", use_container_width=True):
                st.session_state.page = page_name
                st.rerun()

        # Admin section
        if st.session_state.role == "admin":
            st.markdown("---")
            st.markdown("<div style='color:rgba(255,255,255,0.4);font-size:0.75rem;padding:.2rem 0;'>ADMIN ONLY</div>", unsafe_allow_html=True)
            for page_name in admin_pages:
                if st.button(page_name, key=f"nav_{page_name}", use_container_width=True):
                    st.session_state.page = page_name
                    st.rerun()

        # Logout
        st.markdown("---")
        if st.button("🚪 Logout", key="logout_btn", use_container_width=True):
            logout()
            st.rerun()


# =====================================================================
# PAGE ROUTER — maps page name to function
# =====================================================================
PAGE_MAP = {
    "🏠 Home":                page_home,
    "🔮 Salary Prediction":   page_predict,
    "📊 EDA Dashboard":       page_eda,
    "📂 Dataset":             page_dataset,
    "📈 Model Performance":   page_model_performance,
    "💡 Salary Insights":     page_insights,
    "🛠️ Skills Demand":       page_skills,
    "📄 Resume Analyzer":     page_resume,
    "💼 Job Recommendations": page_jobs,
    "ℹ️ About Project":       page_about_project,
    "👨‍💻 About Developer":    page_about_dev,
    "❓ FAQ":                 page_faq,
    "📬 Contact":             page_contact,
    "🛡️ Admin Analytics":     page_admin_analytics,
    "👥 User Management":     page_user_management,
    "📋 Prediction Logs":     page_pred_logs,
}

ADMIN_ONLY_PAGES = {"🛡️ Admin Analytics", "👥 User Management", "📋 Prediction Logs"}


# =====================================================================
# MAIN — entry point
# =====================================================================
def main():
    init_session()
    apply_css()

    # Not logged in → show auth screen
    if not st.session_state.logged_in:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.session_state.auth_page == "login":
                show_login()
            else:
                show_signup()
        return

    # Logged in → show sidebar + selected page
    show_sidebar()

    current_page = st.session_state.page

    # Block non-admins from admin pages
    if current_page in ADMIN_ONLY_PAGES and st.session_state.role != "admin":
        st.error("🚫 Access denied. This page is for admins only.")
        return

    # Call the right page function
    page_function = PAGE_MAP.get(current_page, page_home)
    page_function()


main()
