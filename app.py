# =========================
# IMPORT LIBRARIES
# =========================
import streamlit as st
import pandas as pd
import joblib
import json
import hashlib
import os
from datetime import datetime

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="💼 Salary Predictor",
    page_icon="💼",
    layout="wide"
)

# =========================
# CONSTANTS
# =========================
USERS_FILE = "users.json"
LOGS_FILE  = "prediction_logs.json"
ADMIN_USER = "admin"
ADMIN_PASS = hashlib.sha256("admin123".encode()).hexdigest()   # change in production!

# =========================
# CUSTOM CSS
# =========================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@400;600;700&display=swap');

    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

    .stApp {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        min-height: 100vh;
    }

    .auth-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2rem; font-weight: 700;
        color: #fff; text-align: center; margin-bottom: .3rem;
    }
    .auth-subtitle {
        text-align: center; color: rgba(255,255,255,.5);
        font-size: .9rem; margin-bottom: 2rem;
    }

    .stTextInput > label,
    .stNumberInput > label,
    .stSelectbox > label {
        color: rgba(255,255,255,.8) !important;
        font-size: .85rem !important; font-weight: 500 !important;
    }
    .stTextInput > div > div > input,
    .stNumberInput input {
        background: rgba(255,255,255,.08) !important;
        border: 1px solid rgba(255,255,255,.15) !important;
        border-radius: 10px !important; color: white !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #7c6af7 !important;
        box-shadow: 0 0 0 2px rgba(124,106,247,.25) !important;
    }
    .stSelectbox > div > div {
        background: rgba(255,255,255,.08) !important;
        border: 1px solid rgba(255,255,255,.15) !important;
        border-radius: 10px !important; color: white !important;
    }

    .stButton > button {
        background: linear-gradient(135deg, #7c6af7, #a78bfa) !important;
        color: white !important; border: none !important;
        border-radius: 10px !important; padding: .7rem 2rem !important;
        font-weight: 600 !important; font-size: 1rem !important;
        width: 100% !important; transition: all .3s ease !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(124,106,247,.5) !important;
    }

    h1, h2, h3 {
        color: white !important;
        font-family: 'Space Grotesk', sans-serif !important;
    }

    .divider {
        display: flex; align-items: center;
        margin: 1.2rem 0; color: rgba(255,255,255,.3); font-size: .8rem;
    }
    .divider::before, .divider::after {
        content:''; flex:1; border-bottom: 1px solid rgba(255,255,255,.1);
    }
    .divider span { padding: 0 10px; }

    .switch-link {
        text-align: center; margin-top: 1.2rem;
        color: rgba(255,255,255,.5); font-size: .88rem;
    }

    .user-badge {
        background: rgba(124,106,247,.2);
        border: 1px solid rgba(124,106,247,.4);
        border-radius: 50px; padding: .4rem 1rem;
        color: #a78bfa; font-size: .85rem; font-weight: 600;
        display: inline-block; margin-bottom: 1rem;
    }
    .admin-badge {
        background: rgba(245,158,11,.2);
        border: 1px solid rgba(245,158,11,.4);
        border-radius: 50px; padding: .4rem 1rem;
        color: #fbbf24; font-size: .85rem; font-weight: 600;
        display: inline-block; margin-bottom: 1rem;
    }

    .prediction-box {
        background: linear-gradient(135deg,rgba(124,106,247,.2),rgba(167,139,250,.1));
        border: 1px solid rgba(124,106,247,.4);
        border-radius: 16px; padding: 1.5rem;
        text-align: center; margin-top: 1rem;
    }
    .prediction-amount {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2.5rem; font-weight: 700; color: #a78bfa;
    }

    .stat-card {
        background: rgba(255,255,255,.06);
        border: 1px solid rgba(255,255,255,.12);
        border-radius: 14px; padding: 1.3rem 1.5rem; text-align: center;
    }
    .stat-number {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2.2rem; font-weight: 700; color: #a78bfa;
    }
    .stat-label { color: rgba(255,255,255,.5); font-size: .82rem; margin-top: .2rem; }

    .stSuccess {
        background: rgba(16,185,129,.15) !important;
        border: 1px solid rgba(16,185,129,.3) !important;
        border-radius: 10px !important; color: #6ee7b7 !important;
    }
    .stError {
        background: rgba(239,68,68,.15) !important;
        border: 1px solid rgba(239,68,68,.3) !important;
        border-radius: 10px !important; color: #fca5a5 !important;
    }
    .stWarning {
        background: rgba(245,158,11,.15) !important;
        border: 1px solid rgba(245,158,11,.3) !important;
        border-radius: 10px !important;
    }
</style>
""", unsafe_allow_html=True)


# =========================
# DATA HELPERS
# =========================
def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE) as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

def hash_password(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def register_user(username, password):
    if username == ADMIN_USER:
        return False, "That username is reserved."
    users = load_users()
    if username in users:
        return False, "Username already exists."
    if len(password) < 6:
        return False, "Password must be at least 6 characters."
    users[username] = {"password": hash_password(password), "created_at": datetime.now().isoformat()}
    save_users(users)
    return True, "Account created successfully! Please log in."

def login_user(username, password):
    if username == ADMIN_USER:
        return (True, "admin") if hash_password(password) == ADMIN_PASS else (False, "Incorrect admin password.")
    users = load_users()
    if username not in users:
        return False, "Username not found."
    stored = users[username]
    stored_hash = stored["password"] if isinstance(stored, dict) else stored
    if stored_hash != hash_password(password):
        return False, "Incorrect password."
    return True, "user"

def load_logs():
    if os.path.exists(LOGS_FILE):
        with open(LOGS_FILE) as f:
            return json.load(f)
    return []

def save_log(entry):
    logs = load_logs()
    logs.append(entry)
    with open(LOGS_FILE, "w") as f:
        json.dump(logs, f, indent=2)


# =========================
# SESSION STATE INIT
# =========================
for k, v in {"logged_in": False, "username": "", "role": "", "auth_page": "login"}.items():
    if k not in st.session_state:
        st.session_state[k] = v


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
            success, result = login_user(username.strip(), password)
            if success:
                st.session_state.logged_in = True
                st.session_state.username  = username.strip()
                st.session_state.role      = result
                st.rerun()
            else:
                st.error(result)

    st.markdown('<div class="divider"><span>OR</span></div>', unsafe_allow_html=True)
    st.markdown("<div class='switch-link'>Don't have an account?</div>", unsafe_allow_html=True)
    if st.button("Create Account →", key="btn_go_signup"):
        st.session_state.auth_page = "signup"
        st.rerun()


def show_signup():
    st.markdown('<div class="auth-title">🚀 Get Started</div>', unsafe_allow_html=True)
    st.markdown('<div class="auth-subtitle">Create an account to continue</div>', unsafe_allow_html=True)

    new_user     = st.text_input("Choose a Username", placeholder="e.g. john_doe", key="signup_user")
    new_pass     = st.text_input("Create Password", type="password", placeholder="Min. 6 characters", key="signup_pass")
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
    st.markdown("<div class='switch-link'>Already have an account?</div>", unsafe_allow_html=True)
    if st.button("← Back to Sign In", key="btn_go_login"):
        st.session_state.auth_page = "login"
        st.rerun()


# =========================
# ADMIN PAGE
# =========================
def show_admin():
    users = load_users()
    logs  = load_logs()

    col1, col2 = st.columns([5, 1])
    with col1:
        st.markdown('<div class="admin-badge">🛡️ Admin Panel</div>', unsafe_allow_html=True)
        st.title("Admin Dashboard")
        st.caption("Manage users · View prediction logs · Monitor activity")
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.username  = ""
            st.session_state.role      = ""
            st.rerun()

    st.markdown("---")

    tab1, tab2, tab3 = st.tabs(["📊 Overview", "👥 Users", "📋 Prediction Logs"])

    # ── Overview ──
    with tab1:
        total_users = len(users)
        total_preds = len(logs)
        avg_salary  = int(sum(l.get("predicted_salary", 0) for l in logs) / total_preds) if total_preds else 0
        today       = datetime.now().date().isoformat()
        preds_today = sum(1 for l in logs if l.get("timestamp", "").startswith(today))

        c1, c2, c3, c4 = st.columns(4)
        for col, val, label, icon in [
            (c1, total_users,        "Registered Users",     "👥"),
            (c2, total_preds,        "Total Predictions",    "🔮"),
            (c3, f"₹{avg_salary:,}", "Avg Predicted Salary", "💰"),
            (c4, preds_today,        "Predictions Today",    "📅"),
        ]:
            with col:
                st.markdown(f"""
                <div class="stat-card">
                    <div style="font-size:1.6rem">{icon}</div>
                    <div class="stat-number">{val}</div>
                    <div class="stat-label">{label}</div>
                </div>""", unsafe_allow_html=True)

        if logs:
            df_logs = pd.DataFrame(logs)
            st.markdown("#### 📈 Salary Distribution")
            if "predicted_salary" in df_logs.columns:
                st.bar_chart(df_logs["predicted_salary"].dropna().astype(int))

            st.markdown("#### 🕐 Recent Predictions")
            cols_show = [c for c in ["timestamp","username","predicted_salary","experience_years","job_title"] if c in df_logs.columns]
            recent = df_logs[cols_show].tail(5).iloc[::-1].copy()
            recent.columns = [c.replace("_", " ").title() for c in cols_show]
            st.dataframe(recent, use_container_width=True, hide_index=True)
        else:
            st.info("No predictions yet.")

    # ── Users ──
    with tab2:
        st.markdown("#### 👥 Registered Users")
        if not users:
            st.info("No users registered yet.")
        else:
            rows = []
            for uname, udata in users.items():
                created = udata.get("created_at", "N/A")[:10] if isinstance(udata, dict) else "N/A"
                count   = sum(1 for l in logs if l.get("username") == uname)
                rows.append({"Username": uname, "Joined": created, "Predictions": count})
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

        st.markdown("---")

        with st.expander("➕ Add New User"):
            nu  = st.text_input("New Username", key="admin_new_user")
            np_ = st.text_input("Password", type="password", key="admin_new_pass")
            if st.button("Add User", key="admin_add_btn"):
                if nu and np_:
                    ok, msg = register_user(nu.strip(), np_)
                    st.success(msg) if ok else st.error(msg)
                    if ok:
                        st.rerun()
                else:
                    st.error("Fill both fields.")

        with st.expander("🗑️ Delete a User"):
            if users:
                del_user = st.selectbox("Select user to delete", list(users.keys()), key="admin_del_select")
                if st.button("Delete User", key="admin_del_btn"):
                    users.pop(del_user, None)
                    save_users(users)
                    st.success(f"User '{del_user}' deleted.")
                    st.rerun()
            else:
                st.info("No users to delete.")

        with st.expander("🔑 Reset User Password"):
            if users:
                reset_user = st.selectbox("Select user", list(users.keys()), key="admin_reset_select")
                new_pw     = st.text_input("New Password", type="password", key="admin_reset_pw")
                if st.button("Reset Password", key="admin_reset_btn"):
                    if new_pw and len(new_pw) >= 6:
                        created_at = users[reset_user].get("created_at", "N/A") if isinstance(users[reset_user], dict) else "N/A"
                        users[reset_user] = {"password": hash_password(new_pw), "created_at": created_at}
                        save_users(users)
                        st.success(f"Password reset for '{reset_user}'.")
                    else:
                        st.error("Password must be at least 6 characters.")
            else:
                st.info("No users available.")

    # ── Prediction Logs ──
    with tab3:
        st.markdown("#### 📋 All Prediction Logs")
        if not logs:
            st.info("No predictions logged yet.")
        else:
            df_logs = pd.DataFrame(logs)
            fc1, fc2 = st.columns(2)
            with fc1:
                user_filter = st.selectbox("Filter by user", ["All"] + sorted(df_logs["username"].unique().tolist()), key="log_user_filter")
            with fc2:
                sort_order = st.selectbox("Sort", ["Newest first", "Highest salary", "Lowest salary"], key="log_sort")

            df_view = df_logs.copy()
            if user_filter != "All":
                df_view = df_view[df_view["username"] == user_filter]

            if sort_order == "Highest salary":
                df_view = df_view.sort_values("predicted_salary", ascending=False)
            elif sort_order == "Lowest salary":
                df_view = df_view.sort_values("predicted_salary", ascending=True)
            else:
                df_view = df_view.iloc[::-1]

            st.dataframe(df_view, use_container_width=True, hide_index=True)

            csv = df_view.to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ Download Logs as CSV", csv, "prediction_logs.csv", "text/csv")

            st.markdown("---")
            if st.button("🗑️ Clear All Logs", key="clear_logs"):
                with open(LOGS_FILE, "w") as f:
                    json.dump([], f)
                st.success("All logs cleared.")
                st.rerun()


# =========================
# USER APP
# =========================
def show_app():
    try:
        model   = joblib.load("knn_model.pkl")
        scaler  = joblib.load("scaler.pkl")
        columns = joblib.load("columns.pkl")
    except Exception as e:
        st.error(f"⚠️ Model files not found: {e}")
        st.stop()

    def get_options(prefix):
        opts = [col.replace(prefix, "") for col in columns if col.startswith(prefix)]
        return sorted(list(set(opts)))

    job_options     = ["Other"] + get_options("job_title_")
    edu_options     = ["Other"] + get_options("education_level_")
    loc_options     = ["Other"] + get_options("location_")
    ind_options     = ["Other"] + get_options("industry_")
    company_options = ["Other"] + get_options("company_size_")
    remote_options  = ["Other"] + get_options("remote_work_")

    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown(f'<div class="user-badge">👤 {st.session_state.username}</div>', unsafe_allow_html=True)
        st.title("💼 Salary Prediction App")
        st.caption("Powered by KNN · Fill in your details below")
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.username  = ""
            st.session_state.role      = ""
            st.rerun()

    st.markdown("---")

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        exp    = st.number_input("Experience (years)", 0, 30)
    with col_b:
        skills = st.number_input("Skills Count", 0, 50)
    with col_c:
        cert   = st.number_input("Certifications", 0, 20)

    col_d, col_e = st.columns(2)
    with col_d:
        job     = st.selectbox("Job Role", job_options)
        edu     = st.selectbox("Education", edu_options)
        loc     = st.selectbox("Location", loc_options)
    with col_e:
        ind     = st.selectbox("Industry", ind_options)
        company = st.selectbox("Company Size", company_options)
        remote  = st.selectbox("Remote Work", remote_options)

    st.markdown("---")

    input_dict = {
        "experience_years": exp, "skills_count": skills, "certifications": cert,
        "job_title": job, "education_level": edu, "location": loc,
        "industry": ind, "company_size": company, "remote_work": remote,
    }
    input_df = pd.DataFrame([input_dict])

    input_df['exp_squared']    = input_df['experience_years'] ** 2
    input_df['skill_per_exp']  = input_df['skills_count'] / (input_df['experience_years'] + 1)
    input_df['cert_per_skill'] = input_df['certifications'] / (input_df['skills_count'] + 1)
    input_df['seniority'] = pd.cut(
        input_df['experience_years'], bins=[0, 2, 5, 10, 20],
        labels=['Fresher', 'Junior', 'Mid', 'Senior']
    )

    input_df = pd.get_dummies(input_df)
    input_df = input_df.reindex(columns=columns, fill_value=0)

    num_cols = ['experience_years', 'skills_count', 'certifications',
                'exp_squared', 'skill_per_exp', 'cert_per_skill']
    input_df[num_cols] = scaler.transform(input_df[num_cols])

    if st.button("🔮 Predict Salary"):
        prediction = model.predict(input_df)
        salary = int(prediction[0])

        save_log({
            "username": st.session_state.username,
            "timestamp": datetime.now().isoformat(),
            "predicted_salary": salary,
            "experience_years": exp, "skills_count": skills,
            "certifications": cert, "job_title": job,
            "education_level": edu, "location": loc,
            "industry": ind, "company_size": company, "remote_work": remote,
        })

        st.markdown(f"""
        <div class="prediction-box">
            <div style="color:rgba(255,255,255,.6);font-size:.9rem;margin-bottom:.3rem;">Estimated Annual Salary</div>
            <div class="prediction-amount">₹ {salary:,}</div>
            <div style="color:rgba(255,255,255,.4);font-size:.78rem;margin-top:.5rem;">Based on your profile using KNN model</div>
        </div>""", unsafe_allow_html=True)
        st.balloons()


# =========================
# ROUTER
# =========================
if not st.session_state.logged_in:
    _, center, _ = st.columns([1, 2, 1])
    with center:
        if st.session_state.auth_page == "login":
            show_login()
        else:
            show_signup()
elif st.session_state.role == "admin":
    show_admin()
else:
    show_app()
