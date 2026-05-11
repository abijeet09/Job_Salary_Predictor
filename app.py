# =========================
# IMPORT LIBRARIES
# =========================
import streamlit as st
import pandas as pd
import joblib
import json
import hashlib
import os

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="💼 Salary Predictor",
    page_icon="💼",
    layout="centered"
)

# =========================
# CUSTOM CSS
# =========================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }

    .stApp {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        min-height: 100vh;
    }

    .auth-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 2.5rem;
        margin: 2rem auto;
        max-width: 420px;
        box-shadow: 0 25px 60px rgba(0,0,0,0.4);
    }

    .auth-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2rem;
        font-weight: 700;
        color: #ffffff;
        text-align: center;
        margin-bottom: 0.3rem;
    }

    .auth-subtitle {
        text-align: center;
        color: rgba(255,255,255,0.5);
        font-size: 0.9rem;
        margin-bottom: 2rem;
    }

    .stTextInput > label {
        color: rgba(255,255,255,0.8) !important;
        font-size: 0.85rem !important;
        font-weight: 500 !important;
    }

    .stTextInput > div > div > input {
        background: rgba(255,255,255,0.08) !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        border-radius: 10px !important;
        color: white !important;
        padding: 0.6rem 1rem !important;
    }

    .stTextInput > div > div > input:focus {
        border-color: #7c6af7 !important;
        box-shadow: 0 0 0 2px rgba(124,106,247,0.25) !important;
    }

    .stButton > button {
        background: linear-gradient(135deg, #7c6af7, #a78bfa) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.7rem 2rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        width: 100% !important;
        transition: all 0.3s ease !important;
        cursor: pointer !important;
    }

    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(124,106,247,0.5) !important;
    }

    .stNumberInput > label, .stSelectbox > label {
        color: rgba(255,255,255,0.8) !important;
        font-size: 0.85rem !important;
        font-weight: 500 !important;
    }

    .stNumberInput input {
        background: rgba(255,255,255,0.08) !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        border-radius: 10px !important;
        color: white !important;
    }

    .stSelectbox > div > div {
        background: rgba(255,255,255,0.08) !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        border-radius: 10px !important;
        color: white !important;
    }

    h1, h2, h3 {
        color: white !important;
        font-family: 'Space Grotesk', sans-serif !important;
    }

    .divider {
        display: flex;
        align-items: center;
        margin: 1.2rem 0;
        color: rgba(255,255,255,0.3);
        font-size: 0.8rem;
    }

    .divider::before, .divider::after {
        content: '';
        flex: 1;
        border-bottom: 1px solid rgba(255,255,255,0.1);
    }

    .divider span {
        padding: 0 10px;
    }

    .switch-link {
        text-align: center;
        margin-top: 1.2rem;
        color: rgba(255,255,255,0.5);
        font-size: 0.88rem;
    }

    .user-badge {
        background: rgba(124,106,247,0.2);
        border: 1px solid rgba(124,106,247,0.4);
        border-radius: 50px;
        padding: 0.4rem 1rem;
        color: #a78bfa;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-block;
        margin-bottom: 1rem;
    }

    .prediction-box {
        background: linear-gradient(135deg, rgba(124,106,247,0.2), rgba(167,139,250,0.1));
        border: 1px solid rgba(124,106,247,0.4);
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
        margin-top: 1rem;
    }

    .prediction-amount {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2.5rem;
        font-weight: 700;
        color: #a78bfa;
    }

    .stSuccess {
        background: rgba(16, 185, 129, 0.15) !important;
        border: 1px solid rgba(16, 185, 129, 0.3) !important;
        border-radius: 10px !important;
        color: #6ee7b7 !important;
    }

    .stError {
        background: rgba(239, 68, 68, 0.15) !important;
        border: 1px solid rgba(239, 68, 68, 0.3) !important;
        border-radius: 10px !important;
        color: #fca5a5 !important;
    }

    .stWarning {
        background: rgba(245, 158, 11, 0.15) !important;
        border: 1px solid rgba(245, 158, 11, 0.3) !important;
        border-radius: 10px !important;
    }
</style>
""", unsafe_allow_html=True)


# =========================
# USER STORAGE (JSON file)
# =========================
USERS_FILE = "users.json"

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password):
    users = load_users()
    if username in users:
        return False, "Username already exists."
    if len(password) < 6:
        return False, "Password must be at least 6 characters."
    users[username] = hash_password(password)
    save_users(users)
    return True, "Account created successfully! Please log in."

def login_user(username, password):
    users = load_users()
    if username not in users:
        return False, "Username not found."
    if users[username] != hash_password(password):
        return False, "Incorrect password."
    return True, "Login successful!"


# =========================
# SESSION STATE INIT
# =========================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "auth_page" not in st.session_state:
    st.session_state.auth_page = "login"  # "login" or "signup"


# =========================
# AUTH PAGES
# =========================
def show_login():
    st.markdown('<div class="auth-title">👋 Welcome Back</div>', unsafe_allow_html=True)
    st.markdown('<div class="auth-subtitle">Sign in to predict your salary</div>', unsafe_allow_html=True)

    username = st.text_input("Username", placeholder="Enter your username", key="login_user")
    password = st.text_input("Password", type="password", placeholder="Enter your password", key="login_pass")

    if st.button("Sign In", key="btn_login"):
        if not username or not password:
            st.error("Please fill in all fields.")
        else:
            success, msg = login_user(username.strip(), password)
            if success:
                st.session_state.logged_in = True
                st.session_state.username = username.strip()
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)

    st.markdown('<div class="divider"><span>OR</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="switch-link">Don\'t have an account?</div>', unsafe_allow_html=True)

    if st.button("Create Account →", key="btn_go_signup"):
        st.session_state.auth_page = "signup"
        st.rerun()


def show_signup():
    st.markdown('<div class="auth-title">🚀 Get Started</div>', unsafe_allow_html=True)
    st.markdown('<div class="auth-subtitle">Create an account to continue</div>', unsafe_allow_html=True)

    new_user = st.text_input("Choose a Username", placeholder="e.g. john_doe", key="signup_user")
    new_pass = st.text_input("Create Password", type="password", placeholder="Min. 6 characters", key="signup_pass")
    confirm_pass = st.text_input("Confirm Password", type="password", placeholder="Repeat your password", key="signup_confirm")

    if st.button("Create Account", key="btn_signup"):
        if not new_user or not new_pass or not confirm_pass:
            st.error("Please fill in all fields.")
        elif new_pass != confirm_pass:
            st.error("Passwords do not match.")
        else:
            success, msg = register_user(new_user.strip(), new_pass)
            if success:
                st.success(msg)
                st.session_state.auth_page = "login"
                st.rerun()
            else:
                st.error(msg)

    st.markdown('<div class="divider"><span>OR</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="switch-link">Already have an account?</div>', unsafe_allow_html=True)

    if st.button("← Back to Sign In", key="btn_go_login"):
        st.session_state.auth_page = "login"
        st.rerun()


# =========================
# MAIN APP (after login)
# =========================
def show_app():
    # Load model
    try:
        model = joblib.load("knn_model.pkl")
        scaler = joblib.load("scaler.pkl")
        columns = joblib.load("columns.pkl")
    except Exception as e:
        st.error(f"⚠️ Model files not found: {e}")
        st.stop()

    def get_options(prefix):
        opts = [col.replace(prefix, "") for col in columns if col.startswith(prefix)]
        return sorted(list(set(opts)))

    job_options    = ["Other"] + get_options("job_title_")
    edu_options    = ["Other"] + get_options("education_level_")
    loc_options    = ["Other"] + get_options("location_")
    ind_options    = ["Other"] + get_options("industry_")
    company_options = ["Other"] + get_options("company_size_")
    remote_options = ["Other"] + get_options("remote_work_")

    # Header
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown(f'<div class="user-badge">👤 {st.session_state.username}</div>', unsafe_allow_html=True)
        st.title("💼 Salary Prediction App")
        st.caption("Powered by KNN · Fill in your details below")
    with col2:
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.rerun()

    st.markdown("---")

    # Inputs
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        exp = st.number_input("Experience (years)", 0, 30)
    with col_b:
        skills = st.number_input("Skills Count", 0, 50)
    with col_c:
        cert = st.number_input("Certifications", 0, 20)

    col_d, col_e = st.columns(2)
    with col_d:
        job = st.selectbox("Job Role", job_options)
        edu = st.selectbox("Education", edu_options)
        loc = st.selectbox("Location", loc_options)
    with col_e:
        ind = st.selectbox("Industry", ind_options)
        company = st.selectbox("Company Size", company_options)
        remote = st.selectbox("Remote Work", remote_options)

    st.markdown("---")

    # Build input
    input_dict = {
        "experience_years": exp,
        "skills_count": skills,
        "certifications": cert,
        "job_title": job,
        "education_level": edu,
        "location": loc,
        "industry": ind,
        "company_size": company,
        "remote_work": remote
    }
    input_df = pd.DataFrame([input_dict])

    # Feature Engineering
    input_df['exp_squared'] = input_df['experience_years'] ** 2
    input_df['skill_per_exp'] = input_df['skills_count'] / (input_df['experience_years'] + 1)
    input_df['cert_per_skill'] = input_df['certifications'] / (input_df['skills_count'] + 1)
    input_df['seniority'] = pd.cut(
        input_df['experience_years'],
        bins=[0, 2, 5, 10, 20],
        labels=['Fresher', 'Junior', 'Mid', 'Senior']
    )

    # Dummies + Align
    input_df = pd.get_dummies(input_df)
    input_df = input_df.reindex(columns=columns, fill_value=0)

    # Scale
    num_cols = ['experience_years', 'skills_count', 'certifications',
                'exp_squared', 'skill_per_exp', 'cert_per_skill']
    input_df[num_cols] = scaler.transform(input_df[num_cols])

    # Predict
    if st.button("🔮 Predict Salary"):
        prediction = model.predict(input_df)
        salary = int(prediction[0])
        st.markdown(f"""
        <div class="prediction-box">
            <div style="color: rgba(255,255,255,0.6); font-size: 0.9rem; margin-bottom: 0.3rem;">Estimated Annual Salary</div>
            <div class="prediction-amount">₹ {salary:,}</div>
            <div style="color: rgba(255,255,255,0.4); font-size: 0.78rem; margin-top: 0.5rem;">Based on your profile using KNN model</div>
        </div>
        """, unsafe_allow_html=True)
        st.balloons()


# =========================
# ROUTER
# =========================
if not st.session_state.logged_in:
    # Center the auth card
    _, center, _ = st.columns([1, 2, 1])
    with center:
        if st.session_state.auth_page == "login":
            show_login()
        else:
            show_signup()
else:
    show_app()
