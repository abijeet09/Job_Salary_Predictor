# 💼 SalaryAI Pro — Full-Stack ML Salary Prediction App

A complete, production-ready Streamlit application with 15 pages for salary prediction, EDA, resume analysis, and more.

## 🚀 How to Run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Place your model files in the same folder as app.py
#    knn_model.pkl, scaler.pkl, columns.pkl

# 3. Run the app
streamlit run app.py
```

## 🔐 Admin Login
- **Username:** `admin`
- **Password:** `admin123`
> ⚠️ Change `ADMIN_PASS` in app.py before deploying to production!

## 📄 Pages Included

| # | Page | Description |
|---|------|-------------|
| 1 | 🏠 Home | Project intro, features, dataset info |
| 2 | 🔮 Salary Prediction | ML prediction form |
| 3 | 📊 EDA Dashboard | 6 interactive charts |
| 4 | 📂 Dataset | Dataset preview, stats, download |
| 5 | 📈 Model Performance | R², MAE, RMSE, Actual vs Predicted |
| 6 | 💡 Salary Insights | Role, country, remote/onsite analysis |
| 7 | 🛠️ Skills Demand | Top 20 skills bar chart |
| 8 | 📄 Resume Analyzer | Upload resume, extract skills, predict salary |
| 9 | 💼 Job Recommendations | Profile-based job role suggestions |
| 10 | ℹ️ About Project | Objective, tech stack, future scope |
| 11 | 👨‍💻 About Developer | Developer profile and links |
| 12 | ❓ FAQ | 8 common questions answered |
| 13 | 📬 Contact | Contact form (saves to contact_messages.json) |
| 14 | 🛡️ Admin Analytics | Prediction stats, top roles, daily chart |
| 15 | 👥 User Management | Add/delete/reset users |
| 16 | 📋 Prediction Logs | View, filter, download, clear logs |

## 🌗 Dark / Light Theme
Toggle in the sidebar — persists for your session.

## 📁 Files Created Automatically
- `users.json` — registered users (hashed passwords)
- `prediction_logs.json` — all salary predictions
- `contact_messages.json` — contact form submissions
