# 📊 Sales Data Analysis & Dashboard

A full-stack, production-grade sales analytics platform with real-time data visualization, secure authentication, and a premium glassmorphic UI.

🔗 **Live Demo**: [sales-henna-beta.vercel.app](https://sales-henna-beta.vercel.app)

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | HTML5, CSS3, Vanilla JavaScript, Chart.js |
| **Backend** | Python, Flask, Gunicorn |
| **Database** | PostgreSQL (Supabase) |
| **Auth** | Supabase Authentication |
| **Hosting** | Vercel (Frontend), Render (Backend) |

## ✨ Key Features

- **Real-time KPI Dashboard** — Revenue, Orders, Customers & AOV tracking
- **4 Interactive Charts** — Monthly Revenue, Sales Trends, Category Breakdown, Cumulative Growth
- **Secure Admin Login** — Protected by Supabase Auth with session management
- **Customer Deep Dive** — Click any customer to view full profile with order history
- **Advanced Search & Filters** — Search by name, phone, city + date range filtering
- **Customer Management** — Add customers with purchase category, payment mode & plan
- **CSV Export** — Download customer data for offline analysis
- **Dark/Light Mode** — Premium glassmorphic UI with persistent theme preference
- **Responsive Design** — Works seamlessly across all screen sizes
- **INR Currency** — All amounts displayed in Indian Rupees (₹)

## 🏗️ Architecture

```
sales-dashboard/
├── backend/
│   ├── app.py              # Flask application factory
│   ├── routes.py           # API endpoints with PostgreSQL analytics
│   └── requirements.txt    # Python dependencies
├── frontend/
│   ├── index.html          # Single Page Application
│   ├── style.css           # Glassmorphic design system
│   ├── app.js              # Core application logic & auth
│   ├── charts.js           # Chart.js visualizations
│   └── config.js           # Supabase client configuration
├── setup.sql               # Database schema & seed data
└── README.md
```

## 🚀 Getting Started

### Prerequisites
- Python 3.x
- A [Supabase](https://supabase.com) account (free tier)

### 1. Database Setup
1. Create a new Supabase project
2. Run `setup.sql` in the SQL Editor to create tables and seed data

### 2. Frontend Setup
1. Update `frontend/config.js` with your Supabase URL and Anon Key

### 3. Backend Setup
```bash
cd backend
pip install -r requirements.txt
python app.py
```

### 4. Run
Open `frontend/index.html` in your browser!

## 📸 Screenshots

- Premium glassmorphic dashboard with real-time analytics
- Interactive charts powered by Chart.js
- Secure admin authentication
- Customer profile deep dive with order history

## 👨‍💻 Author

**Nandeeswaran B**

---

⭐ Star this repo if you found it helpful!
