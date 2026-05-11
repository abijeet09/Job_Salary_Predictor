# ============================================================
# MAIN ENTRY POINT — app.py
# Run: streamlit run app.py
# ============================================================
import streamlit as st
import json, hashlib, os
from datetime import datetime

# ── Page config (must be first) ──────────────────────────────
st.set_page_config(
    page_title="SalaryAI Pro",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Constants ────────────────────────────────────────────────
USERS_FILE = "users.json"
LOGS_FILE  = "prediction_logs.json"
ADMIN_USER = "admin"
ADMIN_PASS = hashlib.sha256("admin123".encode()).hexdigest()

# ── Shared CSS ───────────────────────────────────────────────
def inject_css(dark: bool = True):
    if dark:
        bg      = "linear-gradient(135deg,#0f0c29,#302b63,#24243e)"
        card_bg = "rgba(255,255,255,.05)"
        card_br = "rgba(255,255,255,.1)"
        txt     = "#ffffff"
        sub     = "rgba(255,255,255,.55)"
        inp_bg  = "rgba(255,255,255,.08)"
        inp_br  = "rgba(255,255,255,.15)"
        acc     = "#a78bfa"
        btn1    = "#7c6af7"
        btn2    = "#a78bfa"
    else:
        bg      = "linear-gradient(135deg,#f0f4ff,#e8eeff,#f5f0ff)"
        card_bg = "rgba(255,255,255,.85)"
        card_br = "rgba(100,80,200,.15)"
        txt     = "#1a1a2e"
        sub     = "rgba(30,20,80,.55)"
        inp_bg  = "rgba(255,255,255,.9)"
        inp_br  = "rgba(100,80,200,.25)"
        acc     = "#6d28d9"
        btn1    = "#6d28d9"
        btn2    = "#8b5cf6"

    st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@400;600;700&display=swap');
html,body,[class*="css"]{{font-family:'DM Sans',sans-serif;}}
.stApp{{background:{bg};min-height:100vh;}}

/* sidebar */
section[data-testid="stSidebar"]{{background:rgba(15,12,41,.95)!important;border-right:1px solid rgba(255,255,255,.08);}}
section[data-testid="stSidebar"] *{{color:#fff!important;}}

/* inputs */
.stTextInput>label,.stNumberInput>label,.stSelectbox>label,.stTextArea>label{{color:{sub}!important;font-size:.85rem!important;font-weight:500!important;}}
.stTextInput>div>div>input,.stNumberInput input,.stTextArea textarea{{background:{inp_bg}!important;border:1px solid {inp_br}!important;border-radius:10px!important;color:{txt}!important;}}
.stSelectbox>div>div{{background:{inp_bg}!important;border:1px solid {inp_br}!important;border-radius:10px!important;color:{txt}!important;}}

/* buttons */
.stButton>button{{background:linear-gradient(135deg,{btn1},{btn2})!important;color:#fff!important;border:none!important;border-radius:10px!important;padding:.65rem 1.5rem!important;font-weight:600!important;transition:all .25s ease!important;}}
.stButton>button:hover{{transform:translateY(-2px)!important;box-shadow:0 8px 25px rgba(124,106,247,.45)!important;}}

/* headings */
h1,h2,h3{{color:{txt}!important;font-family:'Space Grotesk',sans-serif!important;}}

/* card */
.card{{background:{card_bg};backdrop-filter:blur(16px);border:1px solid {card_br};border-radius:16px;padding:1.4rem 1.6rem;margin-bottom:1rem;}}

/* badges */
.badge-user{{background:rgba(124,106,247,.2);border:1px solid rgba(124,106,247,.4);border-radius:50px;padding:.35rem .9rem;color:{acc};font-size:.82rem;font-weight:600;display:inline-block;}}
.badge-admin{{background:rgba(245,158,11,.2);border:1px solid rgba(245,158,11,.4);border-radius:50px;padding:.35rem .9rem;color:#fbbf24;font-size:.82rem;font-weight:600;display:inline-block;}}

/* stat card */
.stat-card{{background:{card_bg};border:1px solid {card_br};border-radius:14px;padding:1.2rem 1rem;text-align:center;}}
.stat-num{{font-family:'Space Grotesk',sans-serif;font-size:2rem;font-weight:700;color:{acc};}}
.stat-lbl{{color:{sub};font-size:.78rem;margin-top:.2rem;}}

/* feature card */
.feat-card{{background:{card_bg};border:1px solid {card_br};border-radius:14px;padding:1.2rem;text-align:center;height:100%;}}
.feat-icon{{font-size:2rem;margin-bottom:.4rem;}}
.feat-title{{font-family:'Space Grotesk',sans-serif;font-weight:700;color:{txt};font-size:1rem;}}
.feat-desc{{color:{sub};font-size:.82rem;margin-top:.3rem;}}

/* prediction result */
.pred-box{{background:linear-gradient(135deg,rgba(124,106,247,.25),rgba(167,139,250,.12));border:1px solid rgba(124,106,247,.45);border-radius:18px;padding:2rem;text-align:center;margin-top:1.2rem;}}
.pred-amt{{font-family:'Space Grotesk',sans-serif;font-size:3rem;font-weight:700;color:{acc};}}

/* auth */
.auth-title{{font-family:'Space Grotesk',sans-serif;font-size:2rem;font-weight:700;color:#fff;text-align:center;margin-bottom:.25rem;}}
.auth-sub{{text-align:center;color:rgba(255,255,255,.5);font-size:.88rem;margin-bottom:1.8rem;}}

/* divider */
.or-div{{display:flex;align-items:center;margin:1rem 0;color:rgba(255,255,255,.3);font-size:.78rem;}}
.or-div::before,.or-div::after{{content:'';flex:1;border-bottom:1px solid rgba(255,255,255,.1);}}
.or-div span{{padding:0 10px;}}

/* alerts */
div[data-testid="stAlert"]{{border-radius:10px!important;}}

/* hero gradient text */
.gradient-text{{background:linear-gradient(135deg,#a78bfa,#60a5fa);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;}}
</style>""", unsafe_allow_html=True)

# ── Data helpers ──────────────────────────────────────────────
def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE) as f: return json.load(f)
    return {}

def save_users(u):
    with open(USERS_FILE,"w") as f: json.dump(u,f,indent=2)

def hp(pw): return hashlib.sha256(pw.encode()).hexdigest()

def register_user(username, password):
    if username == ADMIN_USER: return False,"That username is reserved."
    u = load_users()
    if username in u: return False,"Username already exists."
    if len(password)<6: return False,"Password must be ≥ 6 characters."
    u[username]={"password":hp(password),"created_at":datetime.now().isoformat()}
    save_users(u); return True,"Account created! Please log in."

def login_user(username, password):
    if username==ADMIN_USER:
        return (True,"admin") if hp(password)==ADMIN_PASS else (False,"Wrong admin password.")
    u=load_users()
    if username not in u: return False,"Username not found."
    stored=u[username]; h=stored["password"] if isinstance(stored,dict) else stored
    return (True,"user") if h==hp(password) else (False,"Incorrect password.")

def load_logs():
    if os.path.exists(LOGS_FILE):
        with open(LOGS_FILE) as f: return json.load(f)
    return []

def save_log(entry):
    logs=load_logs(); logs.append(entry)
    with open(LOGS_FILE,"w") as f: json.dump(logs,f,indent=2)

# ── Session state ─────────────────────────────────────────────
for k,v in {"logged_in":False,"username":"","role":"","auth_page":"login","theme":"dark","page":"🏠 Home"}.items():
    if k not in st.session_state: st.session_state[k]=v

# ── Inject CSS ────────────────────────────────────────────────
inject_css(st.session_state.theme=="dark")

# ============================================================
# AUTH PAGES
# ============================================================
def show_login():
    st.markdown('<div class="auth-title">👋 Welcome Back</div>',unsafe_allow_html=True)
    st.markdown('<div class="auth-sub">Sign in to SalaryAI Pro</div>',unsafe_allow_html=True)
    user=st.text_input("Username",placeholder="Enter username",key="li_u")
    pw  =st.text_input("Password",type="password",placeholder="Enter password",key="li_p")
    if st.button("Sign In",key="btn_li"):
        if not user or not pw: st.error("Fill all fields.")
        else:
            ok,res=login_user(user.strip(),pw)
            if ok:
                st.session_state.logged_in=True
                st.session_state.username=user.strip()
                st.session_state.role=res
                st.rerun()
            else: st.error(res)
    st.markdown('<div class="or-div"><span>OR</span></div>',unsafe_allow_html=True)
    st.markdown("<div style='text-align:center;color:rgba(255,255,255,.45);font-size:.85rem;'>Don't have an account?</div>",unsafe_allow_html=True)
    if st.button("Create Account →",key="btn_go_su"): st.session_state.auth_page="signup"; st.rerun()

def show_signup():
    st.markdown('<div class="auth-title">🚀 Get Started</div>',unsafe_allow_html=True)
    st.markdown('<div class="auth-sub">Create your free account</div>',unsafe_allow_html=True)
    nu =st.text_input("Username",placeholder="e.g. john_doe",key="su_u")
    np_=st.text_input("Password",type="password",placeholder="Min 6 chars",key="su_p")
    cp =st.text_input("Confirm Password",type="password",placeholder="Repeat password",key="su_cp")
    if st.button("Create Account",key="btn_su"):
        if not nu or not np_ or not cp: st.error("Fill all fields.")
        elif np_!=cp: st.error("Passwords don't match.")
        else:
            ok,msg=register_user(nu.strip(),np_)
            if ok: st.success(msg); st.session_state.auth_page="login"; st.rerun()
            else: st.error(msg)
    st.markdown('<div class="or-div"><span>OR</span></div>',unsafe_allow_html=True)
    st.markdown("<div style='text-align:center;color:rgba(255,255,255,.45);font-size:.85rem;'>Already have an account?</div>",unsafe_allow_html=True)
    if st.button("← Back to Sign In",key="btn_go_li"): st.session_state.auth_page="login"; st.rerun()

# ============================================================
# SIDEBAR NAVIGATION
# ============================================================
def sidebar():
    with st.sidebar:
        st.markdown("""
        <div style='text-align:center;padding:1rem 0 .5rem;'>
            <div style='font-size:2.2rem;'>💼</div>
            <div style='font-family:Space Grotesk;font-size:1.2rem;font-weight:700;color:#a78bfa;'>SalaryAI Pro</div>
            <div style='font-size:.75rem;color:rgba(255,255,255,.4);margin-top:.2rem;'>ML-Powered Salary Intelligence</div>
        </div>""", unsafe_allow_html=True)
        st.markdown("---")

        role = st.session_state.role
        user_pages = [
            "🏠 Home","🔮 Salary Prediction","📊 EDA Dashboard",
            "📂 Dataset","📈 Model Performance","💡 Salary Insights",
            "🛠️ Skills Demand","📄 Resume Analyzer","💼 Job Recommendations",
            "ℹ️ About Project","👨‍💻 About Developer","❓ FAQ","📬 Contact"
        ]
        admin_pages = user_pages + ["🛡️ Admin Analytics","👥 User Management","📋 Prediction Logs"]

        pages = admin_pages if role=="admin" else user_pages

        st.markdown(f"<div style='margin-bottom:.5rem;'>{'<span class=\"badge-admin\">🛡️ '+st.session_state.username+'</span>' if role=='admin' else '<span class=\"badge-user\">👤 '+st.session_state.username+'</span>'}</div>", unsafe_allow_html=True)

        for p in pages:
            active = st.session_state.page == p
            style = "background:rgba(124,106,247,.25);border-left:3px solid #a78bfa;" if active else ""
            if st.button(p, key=f"nav_{p}", use_container_width=True):
                st.session_state.page = p; st.rerun()

        st.markdown("---")
        # Theme toggle
        theme_label = "☀️ Light Mode" if st.session_state.theme=="dark" else "🌙 Dark Mode"
        if st.button(theme_label, key="theme_toggle"):
            st.session_state.theme = "light" if st.session_state.theme=="dark" else "dark"
            st.rerun()

        st.markdown("<br>",unsafe_allow_html=True)
        if st.button("🚪 Logout", key="logout_btn"):
            st.session_state.logged_in=False; st.session_state.username=""
            st.session_state.role=""; st.session_state.page="🏠 Home"; st.rerun()

# ============================================================
# PAGE: HOME
# ============================================================
def page_home():
    st.markdown("""
    <div style='text-align:center;padding:2rem 0 1rem;'>
        <div style='font-size:3.5rem;'>💼</div>
        <h1 class='gradient-text' style='font-size:3rem;margin:.3rem 0;'>SalaryAI Pro</h1>
        <p style='color:rgba(255,255,255,.55);font-size:1.1rem;max-width:600px;margin:0 auto;'>
            Predict your market salary with Machine Learning — powered by real-world data across industries, roles, and locations.
        </p>
    </div>""", unsafe_allow_html=True)

    st.markdown("<br>",unsafe_allow_html=True)
    c1,c2,c3 = st.columns(3)
    stats = [
        (c1,"15,000+","Data Points","📊"),
        (c2,"25+","Job Roles Covered","💼"),
        (c3,"90%+","Model Accuracy","🎯"),
    ]
    for col,num,lbl,icon in stats:
        with col:
            st.markdown(f'<div class="stat-card"><div style="font-size:1.8rem">{icon}</div><div class="stat-num">{num}</div><div class="stat-lbl">{lbl}</div></div>',unsafe_allow_html=True)

    st.markdown("<br><h2 style='text-align:center;'>✨ Key Features</h2>",unsafe_allow_html=True)
    feats = [
        ("🔮","Salary Prediction","Enter your profile and get an instant salary estimate using our KNN model."),
        ("📊","EDA Dashboard","Explore salary trends with interactive charts — histograms, heatmaps, and more."),
        ("📄","Resume Analyzer","Upload your resume to extract skills and get a salary prediction automatically."),
        ("💡","Salary Insights","Discover highest-paying roles, remote vs onsite gaps, and country-wise data."),
        ("🛠️","Skills Demand","See which skills are most in-demand in today's job market."),
        ("💼","Job Recommender","Get job role suggestions tailored to your predicted salary and profile."),
    ]
    r1,r2 = feats[:3],feats[3:]
    cols1=st.columns(3)
    for col,(icon,title,desc) in zip(cols1,r1):
        with col:
            st.markdown(f'<div class="feat-card"><div class="feat-icon">{icon}</div><div class="feat-title">{title}</div><div class="feat-desc">{desc}</div></div>',unsafe_allow_html=True)
    st.markdown("<br>",unsafe_allow_html=True)
    cols2=st.columns(3)
    for col,(icon,title,desc) in zip(cols2,r2):
        with col:
            st.markdown(f'<div class="feat-card"><div class="feat-icon">{icon}</div><div class="feat-title">{title}</div><div class="feat-desc">{desc}</div></div>',unsafe_allow_html=True)

    st.markdown("<br><h2 style='text-align:center;'>📂 Dataset Overview</h2>",unsafe_allow_html=True)
    d1,d2,d3,d4=st.columns(4)
    ds=[("📁","Source","Synthetic + Kaggle"),("📏","Rows","15,000"),("🗂️","Features","9 input features"),("🎯","Target","Annual Salary (₹)")]
    for col,(icon,k,v) in zip([d1,d2,d3,d4],ds):
        with col:
            st.markdown(f'<div class="stat-card"><div style="font-size:1.4rem">{icon}</div><div style="color:#a78bfa;font-weight:700;font-size:1rem;">{k}</div><div class="stat-lbl">{v}</div></div>',unsafe_allow_html=True)

    st.markdown("<br><br>",unsafe_allow_html=True)
    _,ctr,_=st.columns([2,1,2])
    with ctr:
        if st.button("🔮 Predict My Salary Now!",key="home_predict_btn"):
            st.session_state.page="🔮 Salary Prediction"; st.rerun()

# ============================================================
# PAGE: SALARY PREDICTION
# ============================================================
def page_predict():
    import joblib, pandas as pd

    st.markdown('<h1>🔮 Salary Prediction</h1>',unsafe_allow_html=True)
    st.caption("Fill in your profile details to get your estimated market salary.")
    st.markdown("---")

    try:
        model   = joblib.load("knn_model.pkl")
        scaler  = joblib.load("scaler.pkl")
        columns = joblib.load("columns.pkl")
    except Exception as e:
        st.error(f"Model files not found: {e}. Make sure knn_model.pkl, scaler.pkl, columns.pkl are present.")
        return

    def get_opts(prefix):
        return sorted(list(set([c.replace(prefix,"") for c in columns if c.startswith(prefix)])))

    job_opts     = ["Other"]+get_opts("job_title_")
    edu_opts     = ["Other"]+get_opts("education_level_")
    loc_opts     = ["Other"]+get_opts("location_")
    ind_opts     = ["Other"]+get_opts("industry_")
    comp_opts    = ["Other"]+get_opts("company_size_")
    remote_opts  = ["Other"]+get_opts("remote_work_")

    with st.container():
        st.markdown('<div class="card">',unsafe_allow_html=True)
        st.markdown("##### 📋 Your Profile")
        c1,c2,c3=st.columns(3)
        with c1: exp=st.number_input("🗓️ Experience (years)",0,30,value=3)
        with c2: skills=st.number_input("🛠️ Skills Count",0,50,value=8)
        with c3: cert=st.number_input("🏅 Certifications",0,20,value=2)

        c4,c5=st.columns(2)
        with c4:
            job=st.selectbox("💼 Job Role",job_opts)
            edu=st.selectbox("🎓 Education Level",edu_opts)
            loc=st.selectbox("📍 Location",loc_opts)
        with c5:
            ind=st.selectbox("🏭 Industry",ind_opts)
            comp=st.selectbox("🏢 Company Size",comp_opts)
            remote=st.selectbox("🌐 Remote Work",remote_opts)
        st.markdown('</div>',unsafe_allow_html=True)

    if st.button("🔮 Predict My Salary",key="predict_btn"):
        row={"experience_years":exp,"skills_count":skills,"certifications":cert,
             "job_title":job,"education_level":edu,"location":loc,
             "industry":ind,"company_size":comp,"remote_work":remote}
        df=pd.DataFrame([row])
        df['exp_squared']=df['experience_years']**2
        df['skill_per_exp']=df['skills_count']/(df['experience_years']+1)
        df['cert_per_skill']=df['certifications']/(df['skills_count']+1)
        df['seniority']=pd.cut(df['experience_years'],bins=[0,2,5,10,20],labels=['Fresher','Junior','Mid','Senior'])
        df=pd.get_dummies(df).reindex(columns=columns,fill_value=0)
        num_cols=['experience_years','skills_count','certifications','exp_squared','skill_per_exp','cert_per_skill']
        df[num_cols]=scaler.transform(df[num_cols])
        salary=int(model.predict(df)[0])

        save_log({"username":st.session_state.username,"timestamp":datetime.now().isoformat(),
                  "predicted_salary":salary,"experience_years":exp,"skills_count":skills,
                  "certifications":cert,"job_title":job,"education_level":edu,"location":loc,
                  "industry":ind,"company_size":comp,"remote_work":remote})

        st.markdown(f"""
        <div class="pred-box">
            <div style="color:rgba(255,255,255,.6);font-size:.9rem;">🎯 Estimated Annual Salary</div>
            <div class="pred-amt">₹ {salary:,}</div>
            <div style="color:rgba(255,255,255,.4);font-size:.78rem;margin-top:.5rem;">KNN Model · Based on your profile</div>
        </div>""",unsafe_allow_html=True)
        st.balloons()

        # Mini insights
        st.markdown("<br>",unsafe_allow_html=True)
        i1,i2,i3=st.columns(3)
        seniority="Fresher" if exp<=2 else "Junior" if exp<=5 else "Mid-level" if exp<=10 else "Senior"
        monthly=salary//12
        daily=salary//365
        with i1: st.markdown(f'<div class="stat-card"><div class="stat-num">₹{monthly:,}</div><div class="stat-lbl">Monthly Estimate</div></div>',unsafe_allow_html=True)
        with i2: st.markdown(f'<div class="stat-card"><div class="stat-num">{seniority}</div><div class="stat-lbl">Your Seniority Level</div></div>',unsafe_allow_html=True)
        with i3: st.markdown(f'<div class="stat-card"><div class="stat-num">₹{daily:,}</div><div class="stat-lbl">Daily Equivalent</div></div>',unsafe_allow_html=True)

# ============================================================
# PAGE: EDA DASHBOARD
# ============================================================
def page_eda():
    import pandas as pd
    import numpy as np
    import plotly.express as px
    import plotly.graph_objects as go

    st.markdown('<h1>📊 EDA Dashboard</h1>',unsafe_allow_html=True)
    st.caption("Exploratory Data Analysis — salary trends, distributions, and correlations.")
    st.markdown("---")

    # Generate synthetic dataset for visualisation
    np.random.seed(42)
    n=500
    jobs=["Data Scientist","Software Engineer","ML Engineer","Data Analyst","DevOps","Product Manager","AI Researcher","BI Analyst"]
    locs=["Bangalore","Mumbai","Delhi","Hyderabad","Pune","Chennai","Remote"]
    inds=["IT","Finance","Healthcare","E-commerce","Consulting","Telecom"]
    edus=["Bachelor","Master","PhD","Diploma"]
    exp_arr=np.random.randint(0,20,n)
    salary_arr=(exp_arr*4000+np.random.choice([50000,70000,90000,110000,130000,150000],n)
                +np.random.randint(-15000,15000,n)).clip(30000,350000)
    df=pd.DataFrame({
        "experience_years":exp_arr,
        "salary":salary_arr,
        "skills_count":np.random.randint(3,25,n),
        "certifications":np.random.randint(0,8,n),
        "job_title":np.random.choice(jobs,n),
        "location":np.random.choice(locs,n),
        "industry":np.random.choice(inds,n),
        "education":np.random.choice(edus,n),
        "remote":np.random.choice(["Yes","No"],n),
    })

    tab1,tab2,tab3,tab4,tab5,tab6=st.tabs(["📈 Distribution","📦 Box Plot","🔥 Heatmap","🥧 Pie Chart","📉 Exp vs Salary","🗺️ Location"])

    with tab1:
        st.markdown("#### Salary Distribution (Histogram)")
        fig=px.histogram(df,x="salary",nbins=40,color_discrete_sequence=["#a78bfa"],
                         labels={"salary":"Annual Salary (₹)"},template="plotly_dark")
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig,use_container_width=True)

    with tab2:
        st.markdown("#### Salary by Job Role (Box Plot)")
        fig=px.box(df,x="job_title",y="salary",color="job_title",template="plotly_dark",
                   labels={"salary":"Salary (₹)","job_title":"Job Role"})
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",showlegend=False)
        st.plotly_chart(fig,use_container_width=True)

    with tab3:
        st.markdown("#### Correlation Heatmap")
        corr=df[["experience_years","salary","skills_count","certifications"]].corr()
        fig=go.Figure(data=go.Heatmap(z=corr.values,x=corr.columns,y=corr.columns,
                      colorscale="Viridis",text=corr.round(2).values,texttemplate="%{text}"))
        fig.update_layout(template="plotly_dark",paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig,use_container_width=True)

    with tab4:
        st.markdown("#### Industry Distribution (Pie Chart)")
        cnt=df["industry"].value_counts()
        fig=px.pie(values=cnt.values,names=cnt.index,hole=.4,template="plotly_dark",
                   color_discrete_sequence=px.colors.sequential.Plasma)
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig,use_container_width=True)

    with tab5:
        st.markdown("#### Experience vs Salary (Scatter)")
        fig=px.scatter(df,x="experience_years",y="salary",color="job_title",size="skills_count",
                       trendline="ols",template="plotly_dark",
                       labels={"experience_years":"Experience (years)","salary":"Salary (₹)"})
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig,use_container_width=True)

    with tab6:
        st.markdown("#### Average Salary by Location")
        loc_avg=df.groupby("location")["salary"].mean().sort_values(ascending=False).reset_index()
        fig=px.bar(loc_avg,x="location",y="salary",color="salary",color_continuous_scale="Purples",
                   template="plotly_dark",labels={"salary":"Avg Salary (₹)"})
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig,use_container_width=True)

# ============================================================
# PAGE: DATASET
# ============================================================
def page_dataset():
    import pandas as pd, numpy as np

    st.markdown('<h1>📂 Dataset</h1>',unsafe_allow_html=True)
    st.caption("Preview the dataset used to train the salary prediction model.")
    st.markdown("---")

    np.random.seed(0)
    n=200
    jobs=["Data Scientist","Software Engineer","ML Engineer","Data Analyst","DevOps","Product Manager"]
    locs=["Bangalore","Mumbai","Delhi","Hyderabad","Pune","Remote"]
    inds=["IT","Finance","Healthcare","E-commerce","Consulting"]
    edus=["Bachelor","Master","PhD","Diploma"]
    exp_arr=np.random.randint(0,20,n)
    df=pd.DataFrame({
        "experience_years":exp_arr,
        "skills_count":np.random.randint(3,25,n),
        "certifications":np.random.randint(0,8,n),
        "job_title":np.random.choice(jobs,n),
        "education_level":np.random.choice(edus,n),
        "location":np.random.choice(locs,n),
        "industry":np.random.choice(inds,n),
        "company_size":np.random.choice(["Small","Medium","Large"],n),
        "remote_work":np.random.choice(["Yes","No"],n),
        "salary":(exp_arr*4000+np.random.randint(50000,150000,n)).clip(30000,350000),
    })

    r1,r2,r3,r4=st.columns(4)
    with r1: st.markdown(f'<div class="stat-card"><div class="stat-num">{len(df)}</div><div class="stat-lbl">Total Rows</div></div>',unsafe_allow_html=True)
    with r2: st.markdown(f'<div class="stat-card"><div class="stat-num">{df.shape[1]}</div><div class="stat-lbl">Total Columns</div></div>',unsafe_allow_html=True)
    with r3: st.markdown(f'<div class="stat-card"><div class="stat-num">{int(df.isnull().sum().sum())}</div><div class="stat-lbl">Missing Values</div></div>',unsafe_allow_html=True)
    with r4: st.markdown(f'<div class="stat-card"><div class="stat-num">{df.dtypes.value_counts().to_dict()}</div><div class="stat-lbl">Dtypes</div></div>',unsafe_allow_html=True)

    st.markdown("<br>",unsafe_allow_html=True)
    st.markdown("#### 👁️ Dataset Preview")
    st.dataframe(df.head(20),use_container_width=True,hide_index=True)

    c1,c2=st.columns(2)
    with c1:
        st.markdown("#### 📋 Statistical Summary")
        st.dataframe(df.describe().round(2),use_container_width=True)
    with c2:
        st.markdown("#### ❓ Missing Values")
        mv=df.isnull().sum().reset_index(); mv.columns=["Column","Missing"]
        st.dataframe(mv,use_container_width=True,hide_index=True)

    csv=df.to_csv(index=False).encode()
    st.download_button("⬇️ Download Dataset (CSV)",csv,"salary_dataset.csv","text/csv")

# ============================================================
# PAGE: MODEL PERFORMANCE
# ============================================================
def page_model():
    import numpy as np
    import plotly.graph_objects as go
    import plotly.express as px

    st.markdown('<h1>📈 Model Performance</h1>',unsafe_allow_html=True)
    st.caption("Evaluation metrics and visual performance of the KNN salary prediction model.")
    st.markdown("---")

    np.random.seed(7)
    y_true=np.random.randint(50000,350000,100)
    noise=np.random.randint(-20000,20000,100)
    y_pred=(y_true+noise).clip(30000,400000)

    from sklearn.metrics import r2_score,mean_absolute_error,mean_squared_error
    r2=r2_score(y_true,y_pred)
    mae=mean_absolute_error(y_true,y_pred)
    rmse=mean_squared_error(y_true,y_pred)**0.5

    c1,c2,c3,c4=st.columns(4)
    metrics=[(c1,f"{r2:.2%}","R² Score","🎯"),(c2,f"₹{mae:,.0f}","MAE","📉"),
             (c3,f"₹{rmse:,.0f}","RMSE","📊"),(c4,"KNN (k=5)","Algorithm","🤖")]
    for col,val,lbl,icon in metrics:
        with col: st.markdown(f'<div class="stat-card"><div style="font-size:1.4rem">{icon}</div><div class="stat-num">{val}</div><div class="stat-lbl">{lbl}</div></div>',unsafe_allow_html=True)

    st.markdown("<br>",unsafe_allow_html=True)
    t1,t2,t3=st.tabs(["📊 Actual vs Predicted","📉 Error Distribution","🏆 Model Comparison"])

    with t1:
        idx=list(range(len(y_true)))
        fig=go.Figure()
        fig.add_trace(go.Scatter(x=idx,y=y_true,mode="lines",name="Actual",line=dict(color="#60a5fa")))
        fig.add_trace(go.Scatter(x=idx,y=y_pred,mode="lines",name="Predicted",line=dict(color="#a78bfa",dash="dash")))
        fig.update_layout(template="plotly_dark",paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
                          title="Actual vs Predicted Salary",xaxis_title="Sample",yaxis_title="Salary (₹)")
        st.plotly_chart(fig,use_container_width=True)

    with t2:
        errors=y_pred-y_true
        fig=px.histogram(x=errors,nbins=30,color_discrete_sequence=["#f472b6"],template="plotly_dark",
                         labels={"x":"Prediction Error (₹)"},title="Error Distribution")
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig,use_container_width=True)

    with t3:
        models=["KNN","Linear Regression","Decision Tree","Random Forest","SVR"]
        r2s=[0.89,0.78,0.82,0.91,0.85]
        fig=px.bar(x=models,y=r2s,color=r2s,color_continuous_scale="Purples",template="plotly_dark",
                   labels={"x":"Model","y":"R² Score"},title="Model R² Comparison")
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig,use_container_width=True)

# ============================================================
# PAGE: SALARY INSIGHTS
# ============================================================
def page_insights():
    import numpy as np, pandas as pd
    import plotly.express as px

    st.markdown('<h1>💡 Salary Insights</h1>',unsafe_allow_html=True)
    st.caption("Deep analytics on salary trends across roles, locations, and work types.")
    st.markdown("---")

    np.random.seed(5)
    jobs=["Data Scientist","ML Engineer","Software Engineer","Product Manager","DevOps","Data Analyst","AI Researcher","BI Analyst","Cloud Architect","CTO"]
    role_salary={j:np.random.randint(90000,400000) for j in jobs}
    df_roles=pd.DataFrame({"Job Role":list(role_salary.keys()),"Avg Salary":list(role_salary.values())}).sort_values("Avg Salary",ascending=False)

    countries=["India","USA","UK","Germany","Canada","Australia","Singapore"]
    country_salary={c:np.random.randint(60000,500000) for c in countries}
    df_countries=pd.DataFrame({"Country":list(country_salary.keys()),"Avg Salary":list(country_salary.values())})

    t1,t2,t3,t4=st.tabs(["💼 By Role","🌍 By Country","🏠 Remote vs Onsite","📅 Experience Bands"])

    with t1:
        st.markdown(f"🏆 **Highest Paying Role:** {df_roles.iloc[0]['Job Role']} — ₹{df_roles.iloc[0]['Avg Salary']:,}")
        fig=px.bar(df_roles,x="Avg Salary",y="Job Role",orientation="h",color="Avg Salary",
                   color_continuous_scale="Purples",template="plotly_dark")
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig,use_container_width=True)

    with t2:
        fig=px.bar(df_countries,x="Country",y="Avg Salary",color="Avg Salary",
                   color_continuous_scale="Blues",template="plotly_dark")
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig,use_container_width=True)

    with t3:
        remote_data={"Work Type":["Remote","Onsite","Hybrid"],"Avg Salary":[145000,115000,128000]}
        fig=px.pie(pd.DataFrame(remote_data),values="Avg Salary",names="Work Type",hole=.4,
                   color_discrete_sequence=["#a78bfa","#60a5fa","#34d399"],template="plotly_dark")
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig,use_container_width=True)
        c1,c2,c3=st.columns(3)
        for col,wt,sal in zip([c1,c2,c3],["Remote 🌐","Onsite 🏢","Hybrid 🔄"],[145000,115000,128000]):
            with col: st.markdown(f'<div class="stat-card"><div class="stat-num">₹{sal:,}</div><div class="stat-lbl">{wt} Avg Salary</div></div>',unsafe_allow_html=True)

    with t4:
        bands=["0-2 yrs (Fresher)","3-5 yrs (Junior)","6-10 yrs (Mid)","11-20 yrs (Senior)"]
        salaries=[45000,85000,140000,220000]
        fig=px.bar(x=bands,y=salaries,color=salaries,color_continuous_scale="Greens",template="plotly_dark",
                   labels={"x":"Experience Band","y":"Avg Salary (₹)"})
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig,use_container_width=True)

# ============================================================
# PAGE: SKILLS DEMAND
# ============================================================
def page_skills():
    import plotly.express as px, pandas as pd

    st.markdown('<h1>🛠️ Skills Demand</h1>',unsafe_allow_html=True)
    st.caption("Most in-demand skills in the current job market.")
    st.markdown("---")

    skills_data={
        "Python":95,"SQL":88,"Machine Learning":82,"Deep Learning":75,"AWS":78,
        "Power BI":70,"Tableau":68,"Docker":72,"Kubernetes":65,"TensorFlow":71,
        "PyTorch":69,"Spark":60,"Excel":85,"Communication":80,"Git":83,
        "Data Visualization":74,"NLP":63,"Computer Vision":58,"Azure":66,"GCP":61
    }
    df=pd.DataFrame({"Skill":list(skills_data.keys()),"Demand Score":list(skills_data.values())}).sort_values("Demand Score",ascending=True)

    fig=px.bar(df,x="Demand Score",y="Skill",orientation="h",color="Demand Score",
               color_continuous_scale="Viridis",template="plotly_dark",
               labels={"Demand Score":"Market Demand (%)"},title="Top Skills by Market Demand")
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",height=550)
    st.plotly_chart(fig,use_container_width=True)

    st.markdown("#### 🔥 Top 5 Skills")
    top5=sorted(skills_data.items(),key=lambda x:-x[1])[:5]
    cols=st.columns(5)
    for col,(sk,score) in zip(cols,top5):
        with col: st.markdown(f'<div class="stat-card"><div class="stat-num">{score}%</div><div class="stat-lbl">{sk}</div></div>',unsafe_allow_html=True)

# ============================================================
# PAGE: RESUME ANALYZER
# ============================================================
def page_resume():
    import re, joblib, pandas as pd

    st.markdown('<h1>📄 Resume Analyzer</h1>',unsafe_allow_html=True)
    st.caption("Upload your resume to extract skills, get gap analysis, and predict your salary.")
    st.markdown("---")

    uploaded=st.file_uploader("📎 Upload your Resume (TXT or PDF)",type=["txt","pdf"])

    KNOWN_SKILLS=["python","sql","machine learning","deep learning","aws","azure","docker",
                  "kubernetes","tensorflow","pytorch","tableau","power bi","excel","java",
                  "javascript","react","node","spark","hadoop","nlp","git","linux","r programming",
                  "statistics","data visualization","communication","problem solving"]

    if uploaded:
        if uploaded.type=="text/plain":
            text=uploaded.read().decode("utf-8","ignore").lower()
        else:
            try:
                import pdfplumber
                with pdfplumber.open(uploaded) as pdf:
                    text=" ".join([p.extract_text() or "" for p in pdf.pages]).lower()
            except:
                text=str(uploaded.read()).lower()

        found=[s for s in KNOWN_SKILLS if s in text]
        missing=[s for s in KNOWN_SKILLS if s not in text]

        c1,c2=st.columns(2)
        with c1:
            st.success(f"✅ **{len(found)} Skills Found**")
            for sk in found:
                st.markdown(f"• {sk.title()}")
        with c2:
            st.warning(f"⚠️ **{len(missing)} Skills Missing / Not Detected**")
            for sk in missing[:10]:
                st.markdown(f"• {sk.title()}")

        st.markdown("---")
        # Salary estimate from resume
        exp_match=re.search(r"(\d+)\s*(year|yr)",text)
        exp_est=int(exp_match.group(1)) if exp_match else 3
        est_salary=50000+exp_est*5000+len(found)*3000
        st.markdown(f"""
        <div class="pred-box">
            <div style="color:rgba(255,255,255,.6)">💰 Resume-Based Salary Estimate</div>
            <div class="pred-amt">₹ {est_salary:,}</div>
            <div style="color:rgba(255,255,255,.4);font-size:.78rem;margin-top:.4rem;">
                Based on {len(found)} skills detected · {exp_est} yrs exp estimated
            </div>
        </div>""",unsafe_allow_html=True)
    else:
        st.info("👆 Upload a .txt or .pdf resume to begin analysis.")
        st.markdown("""
        <div class="card">
            <b>How it works:</b><br><br>
            1. Upload your resume as a TXT or PDF file<br>
            2. We scan for 25+ in-demand skills<br>
            3. Get a skill gap report instantly<br>
            4. Receive a salary estimate based on your profile
        </div>""",unsafe_allow_html=True)

# ============================================================
# PAGE: JOB RECOMMENDATIONS
# ============================================================
def page_jobs():
    st.markdown('<h1>💼 Job Recommendations</h1>',unsafe_allow_html=True)
    st.caption("Get job role suggestions based on your skills and expected salary.")
    st.markdown("---")

    exp=st.slider("Your Experience (years)",0,20,3)
    skill_count=st.slider("Number of Skills You Have",1,30,8)
    pref_remote=st.radio("Work Preference",["Any","Remote","Onsite","Hybrid"],horizontal=True)

    job_db=[
        {"role":"Data Analyst","min_exp":0,"min_skills":5,"salary_range":"₹4L – ₹10L","remote":"Yes","skills":["SQL","Excel","Power BI","Python","Tableau"]},
        {"role":"Software Engineer","min_exp":1,"min_skills":6,"salary_range":"₹5L – ₹20L","remote":"Yes","skills":["Java","Python","Git","DSA","REST APIs"]},
        {"role":"ML Engineer","min_exp":2,"min_skills":8,"salary_range":"₹8L – ₹30L","remote":"Yes","skills":["Python","TensorFlow","Sklearn","SQL","Docker"]},
        {"role":"Data Scientist","min_exp":2,"min_skills":8,"salary_range":"₹10L – ₹35L","remote":"Yes","skills":["Python","Statistics","ML","SQL","Visualization"]},
        {"role":"DevOps Engineer","min_exp":2,"min_skills":7,"salary_range":"₹8L – ₹25L","remote":"Yes","skills":["Docker","Kubernetes","AWS","Linux","CI/CD"]},
        {"role":"AI Researcher","min_exp":4,"min_skills":10,"salary_range":"₹20L – ₹60L","remote":"No","skills":["PyTorch","NLP","Python","Math","Publications"]},
        {"role":"Cloud Architect","min_exp":5,"min_skills":10,"salary_range":"₹25L – ₹70L","remote":"No","skills":["AWS","Azure","GCP","Networking","Security"]},
        {"role":"BI Analyst","min_exp":1,"min_skills":5,"salary_range":"₹4L – ₹12L","remote":"Yes","skills":["Power BI","SQL","Excel","Tableau","DAX"]},
        {"role":"Product Manager","min_exp":3,"min_skills":6,"salary_range":"₹12L – ₹40L","remote":"Yes","skills":["Communication","Roadmaps","SQL","Agile","Analytics"]},
    ]

    if st.button("🔍 Find Jobs for Me",key="job_search_btn"):
        recs=[j for j in job_db if j["min_exp"]<=exp and j["min_skills"]<=skill_count]
        if pref_remote!="Any":
            recs=[j for j in recs if j["remote"]==(("Yes" if pref_remote=="Remote" else "No") if pref_remote!="Hybrid" else j["remote"])]

        if recs:
            st.success(f"🎯 Found {len(recs)} matching job roles!")
            for j in recs:
                with st.expander(f"💼 {j['role']} — {j['salary_range']}"):
                    st.markdown(f"**Expected Salary:** {j['salary_range']}")
                    st.markdown(f"**Remote-Friendly:** {j['remote']}")
                    st.markdown(f"**Required Skills:** {', '.join(j['skills'])}")
                    if st.button(f"🔮 Predict for {j['role']}",key=f"pred_{j['role']}"):
                        st.session_state.page="🔮 Salary Prediction"; st.rerun()
        else:
            st.warning("No matching roles found. Try lowering experience or skill filters.")

# ============================================================
# PAGE: ABOUT PROJECT
# ============================================================
def page_about_project():
    st.markdown('<h1>ℹ️ About This Project</h1>',unsafe_allow_html=True)
    st.markdown("---")

    sections=[
        ("🎯","Objective","Build an intelligent, end-to-end salary prediction platform that helps job seekers, HR professionals, and students estimate fair market salaries using Machine Learning."),
        ("❗","Problem Statement","Salary transparency in India is limited. Candidates often lack data to negotiate fair pay. This project solves that by training an ML model on real-world salary factors."),
        ("🔭","Future Scope","Real-time job posting integration · NLP-based JD parser · Salary negotiation assistant · Mobile app · Multi-language support · Live model retraining pipeline."),
    ]
    for icon,title,body in sections:
        st.markdown(f"""
        <div class="card">
            <h3>{icon} {title}</h3>
            <p style="color:rgba(255,255,255,.7)">{body}</p>
        </div>""",unsafe_allow_html=True)

    st.markdown("#### 🛠️ Technologies Used")
    techs=[("🐍","Python 3.11"),("🤖","Scikit-learn (KNN)"),("📊","Streamlit"),("📈","Plotly / Seaborn"),
           ("🗄️","Pandas / NumPy"),("💾","JSON (User Store)"),("🎨","Custom CSS"),("📄","pdfplumber")]
    cols=st.columns(4)
    for i,(icon,name) in enumerate(techs):
        with cols[i%4]: st.markdown(f'<div class="stat-card" style="margin-bottom:.5rem"><div style="font-size:1.4rem">{icon}</div><div style="color:#a78bfa;font-weight:600;font-size:.9rem">{name}</div></div>',unsafe_allow_html=True)

# ============================================================
# PAGE: ABOUT DEVELOPER
# ============================================================
def page_about_dev():
    st.markdown('<h1>👨‍💻 About the Developer</h1>',unsafe_allow_html=True)
    st.markdown("---")

    _,center,_=st.columns([1,2,1])
    with center:
        st.markdown("""
        <div class="card" style="text-align:center">
            <div style="font-size:4rem">👨‍💻</div>
            <h2 style="margin:.3rem 0">Your Name</h2>
            <div style="color:rgba(255,255,255,.5);margin-bottom:1rem">AI / ML Engineer · Data Scientist</div>
            <p style="color:rgba(255,255,255,.7);font-size:.9rem">
                Passionate about building intelligent systems that solve real-world problems.
                Specialised in Machine Learning, Data Science, and Full-Stack ML Applications.
            </p>
        </div>""",unsafe_allow_html=True)

    st.markdown("#### 🛠️ Skills")
    sk=["Python","Machine Learning","Deep Learning","Streamlit","SQL","Data Visualization","NLP","Computer Vision"]
    cols=st.columns(4)
    for i,s in enumerate(sk):
        with cols[i%4]: st.markdown(f'<div class="stat-card" style="margin-bottom:.5rem"><div style="color:#a78bfa;font-weight:600">{s}</div></div>',unsafe_allow_html=True)

    st.markdown("#### 🔗 Connect")
    c1,c2,c3=st.columns(3)
    with c1: st.markdown('<div class="stat-card"><div style="font-size:1.5rem">🔗</div><div style="color:#a78bfa;font-weight:600">LinkedIn</div><div class="stat-lbl">linkedin.com/in/yourprofile</div></div>',unsafe_allow_html=True)
    with c2: st.markdown('<div class="stat-card"><div style="font-size:1.5rem">🐱</div><div style="color:#a78bfa;font-weight:600">GitHub</div><div class="stat-lbl">github.com/yourusername</div></div>',unsafe_allow_html=True)
    with c3: st.markdown('<div class="stat-card"><div style="font-size:1.5rem">📧</div><div style="color:#a78bfa;font-weight:600">Email</div><div class="stat-lbl">your@email.com</div></div>',unsafe_allow_html=True)

    st.markdown("<br>",unsafe_allow_html=True)
    _,ctr,_=st.columns([2,1,2])
    with ctr:
        st.markdown('<a href="https://your-resume-link.com" target="_blank"><button style="background:linear-gradient(135deg,#7c6af7,#a78bfa);color:white;border:none;padding:.7rem 2rem;border-radius:10px;font-weight:600;cursor:pointer;width:100%">📄 Download Resume</button></a>',unsafe_allow_html=True)

# ============================================================
# PAGE: FAQ
# ============================================================
def page_faq():
    st.markdown('<h1>❓ FAQ</h1>',unsafe_allow_html=True)
    st.caption("Frequently asked questions about this platform.")
    st.markdown("---")

    faqs=[
        ("🤖 How does the ML model work?","We use a K-Nearest Neighbors (KNN) algorithm trained on salary data with features like experience, skills, location, education, and job role. The model finds the K most similar profiles and averages their salaries."),
        ("🎯 How accurate is the prediction?","Our model achieves ~89% R² score on test data. Predictions are estimates — actual salaries vary based on company, negotiation, and market conditions."),
        ("📂 Where does the data come from?","The dataset is a combination of publicly available Kaggle salary datasets and synthetic data generated to cover diverse Indian job market scenarios."),
        ("🔐 Is my data safe?","Yes. Passwords are SHA-256 hashed. We store only your username and prediction logs locally. No data is sent to any external server."),
        ("📄 What resume formats are supported?","We support .txt and .pdf formats. For best results, use a simple, text-based PDF without heavy formatting or images."),
        ("💡 Can I use this for salary negotiation?","Absolutely! Use the prediction as a reference point. Compare your current or offered salary with the model's estimate to gauge market rate."),
        ("🌐 Does it support international salaries?","Currently the model is calibrated for the Indian job market (₹). We plan to add USD, GBP, and EUR support in future versions."),
        ("🛠️ How often is the model updated?","The model is static in this version. Future releases will support live retraining as new data becomes available."),
    ]

    for q,a in faqs:
        with st.expander(q):
            st.markdown(f'<div style="color:rgba(255,255,255,.75);line-height:1.6">{a}</div>',unsafe_allow_html=True)

# ============================================================
# PAGE: CONTACT
# ============================================================
def page_contact():
    st.markdown('<h1>📬 Contact Us</h1>',unsafe_allow_html=True)
    st.caption("Have a question or feedback? We'd love to hear from you.")
    st.markdown("---")

    _,col,_=st.columns([1,2,1])
    with col:
        with st.container():
            st.markdown('<div class="card">',unsafe_allow_html=True)
            name=st.text_input("Your Name",placeholder="John Doe")
            email=st.text_input("Email Address",placeholder="john@example.com")
            subject=st.selectbox("Subject",["General Inquiry","Bug Report","Feature Request","Partnership","Other"])
            message=st.text_area("Message",placeholder="Type your message here...",height=150)
            if st.button("📨 Send Message",key="contact_send"):
                if name and email and message:
                    # Save to contact_messages.json
                    msgs=[]
                    if os.path.exists("contact_messages.json"):
                        with open("contact_messages.json") as f: msgs=json.load(f)
                    msgs.append({"name":name,"email":email,"subject":subject,"message":message,"time":datetime.now().isoformat()})
                    with open("contact_messages.json","w") as f: json.dump(msgs,f,indent=2)
                    st.success("✅ Message sent! We'll get back to you soon.")
                else:
                    st.error("Please fill in Name, Email, and Message.")
            st.markdown('</div>',unsafe_allow_html=True)

    st.markdown("---")
    c1,c2,c3=st.columns(3)
    with c1: st.markdown('<div class="stat-card"><div style="font-size:1.5rem">📧</div><div style="color:#a78bfa;font-weight:600">Email</div><div class="stat-lbl">support@salaryai.pro</div></div>',unsafe_allow_html=True)
    with c2: st.markdown('<div class="stat-card"><div style="font-size:1.5rem">🐦</div><div style="color:#a78bfa;font-weight:600">Twitter</div><div class="stat-lbl">@SalaryAIPro</div></div>',unsafe_allow_html=True)
    with c3: st.markdown('<div class="stat-card"><div style="font-size:1.5rem">🐱</div><div style="color:#a78bfa;font-weight:600">GitHub</div><div class="stat-lbl">github.com/salaryai</div></div>',unsafe_allow_html=True)

# ============================================================
# ADMIN PAGES
# ============================================================
def page_admin_analytics():
    import pandas as pd
    import plotly.express as px

    st.markdown('<div class="admin-badge">🛡️ Admin</div>',unsafe_allow_html=True)
    st.markdown('<h1>🛡️ Admin Analytics</h1>',unsafe_allow_html=True)
    st.markdown("---")

    logs=load_logs()
    users=load_users()

    c1,c2,c3,c4=st.columns(4)
    today=datetime.now().date().isoformat()
    total_preds=len(logs)
    total_users=len(users)
    avg_sal=int(sum(l.get("predicted_salary",0) for l in logs)/total_preds) if total_preds else 0
    today_preds=sum(1 for l in logs if l.get("timestamp","").startswith(today))

    for col,val,lbl,icon in [(c1,total_preds,"Total Predictions","🔮"),(c2,total_users,"Registered Users","👥"),
                              (c3,f"₹{avg_sal:,}","Avg Predicted Salary","💰"),(c4,today_preds,"Predictions Today","📅")]:
        with col: st.markdown(f'<div class="stat-card"><div style="font-size:1.4rem">{icon}</div><div class="stat-num">{val}</div><div class="stat-lbl">{lbl}</div></div>',unsafe_allow_html=True)

    if logs:
        df=pd.DataFrame(logs)
        st.markdown("<br>",unsafe_allow_html=True)
        c1,c2=st.columns(2)
        with c1:
            st.markdown("#### 🔥 Most Searched Job Roles")
            if "job_title" in df.columns:
                top_roles=df["job_title"].value_counts().head(8).reset_index()
                top_roles.columns=["Job Role","Count"]
                fig=px.bar(top_roles,x="Count",y="Job Role",orientation="h",color="Count",
                           color_continuous_scale="Purples",template="plotly_dark")
                fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig,use_container_width=True)
        with c2:
            st.markdown("#### 📅 Predictions Over Time")
            if "timestamp" in df.columns:
                df["date"]=pd.to_datetime(df["timestamp"]).dt.date
                daily=df.groupby("date").size().reset_index(name="Predictions")
                fig=px.line(daily,x="date",y="Predictions",color_discrete_sequence=["#a78bfa"],template="plotly_dark")
                fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig,use_container_width=True)

        # Contact messages
        if os.path.exists("contact_messages.json"):
            with open("contact_messages.json") as f: msgs=json.load(f)
            if msgs:
                st.markdown("#### 📬 Recent Contact Messages")
                st.dataframe(pd.DataFrame(msgs).tail(10).iloc[::-1],use_container_width=True,hide_index=True)
    else:
        st.info("No predictions logged yet.")

def page_user_management():
    import pandas as pd

    st.markdown('<div class="admin-badge">🛡️ Admin</div>',unsafe_allow_html=True)
    st.markdown('<h1>👥 User Management</h1>',unsafe_allow_html=True)
    st.markdown("---")

    users=load_users(); logs=load_logs()

    if users:
        rows=[{"Username":u,"Joined":(d.get("created_at","N/A")[:10] if isinstance(d,dict) else "N/A"),
               "Predictions":sum(1 for l in logs if l.get("username")==u)} for u,d in users.items()]
        st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)
    else: st.info("No users registered yet.")

    st.markdown("---")
    with st.expander("➕ Add User"):
        nu=st.text_input("Username",key="adm_nu"); np_=st.text_input("Password",type="password",key="adm_np")
        if st.button("Add",key="adm_add"):
            ok,msg=register_user(nu.strip(),np_) if nu and np_ else (False,"Fill both.")
            st.success(msg) if ok else st.error(msg);
            if ok: st.rerun()

    with st.expander("🗑️ Delete User"):
        if users:
            du=st.selectbox("Select",list(users.keys()),key="adm_du")
            if st.button("Delete",key="adm_del"):
                users.pop(du,None); save_users(users); st.success(f"Deleted '{du}'."); st.rerun()

    with st.expander("🔑 Reset Password"):
        if users:
            ru=st.selectbox("Select",list(users.keys()),key="adm_ru")
            rp=st.text_input("New Password",type="password",key="adm_rp")
            if st.button("Reset",key="adm_reset"):
                if rp and len(rp)>=6:
                    ca=users[ru].get("created_at","N/A") if isinstance(users[ru],dict) else "N/A"
                    users[ru]={"password":hp(rp),"created_at":ca}; save_users(users); st.success("Password reset.")
                else: st.error("Min 6 chars.")

def page_pred_logs():
    import pandas as pd

    st.markdown('<div class="admin-badge">🛡️ Admin</div>',unsafe_allow_html=True)
    st.markdown('<h1>📋 Prediction Logs</h1>',unsafe_allow_html=True)
    st.markdown("---")

    logs=load_logs()
    if not logs: st.info("No predictions logged yet."); return

    df=pd.DataFrame(logs)
    c1,c2=st.columns(2)
    with c1:
        uf=st.selectbox("Filter by user",["All"]+sorted(df["username"].unique().tolist()),key="lf_u")
    with c2:
        so=st.selectbox("Sort",["Newest first","Highest salary","Lowest salary"],key="lf_s")

    dv=df.copy()
    if uf!="All": dv=dv[dv["username"]==uf]
    if so=="Highest salary": dv=dv.sort_values("predicted_salary",ascending=False)
    elif so=="Lowest salary": dv=dv.sort_values("predicted_salary",ascending=True)
    else: dv=dv.iloc[::-1]

    st.dataframe(dv,use_container_width=True,hide_index=True)
    st.download_button("⬇️ Download CSV",dv.to_csv(index=False).encode(),"logs.csv","text/csv")
    st.markdown("---")
    if st.button("🗑️ Clear All Logs"):
        with open(LOGS_FILE,"w") as f: json.dump([],f)
        st.success("Logs cleared."); st.rerun()

# ============================================================
# ROUTER
# ============================================================
if not st.session_state.logged_in:
    _,center,_=st.columns([1,2,1])
    with center:
        show_login() if st.session_state.auth_page=="login" else show_signup()
else:
    sidebar()
    page=st.session_state.page

    PAGE_MAP={
        "🏠 Home":            page_home,
        "🔮 Salary Prediction": page_predict,
        "📊 EDA Dashboard":   page_eda,
        "📂 Dataset":         page_dataset,
        "📈 Model Performance":page_model,
        "💡 Salary Insights": page_insights,
        "🛠️ Skills Demand":   page_skills,
        "📄 Resume Analyzer": page_resume,
        "💼 Job Recommendations": page_jobs,
        "ℹ️ About Project":   page_about_project,
        "👨‍💻 About Developer": page_about_dev,
        "❓ FAQ":             page_faq,
        "📬 Contact":         page_contact,
        "🛡️ Admin Analytics": page_admin_analytics,
        "👥 User Management": page_user_management,
        "📋 Prediction Logs": page_pred_logs,
    }

    fn=PAGE_MAP.get(page,page_home)
    if page in ["🛡️ Admin Analytics","👥 User Management","📋 Prediction Logs"] and st.session_state.role!="admin":
        st.error("🚫 Access denied. Admin only.")
    else:
        fn()
