# Sales Data Analysis & Dashboard

A high-fidelity sales analytics platform built with Supabase, Flask, and Chart.js.

## 🚀 Getting Started

### 1. Supabase Setup (Database)
1.  Go to [supabase.com](https://supabase.com) and create a new project.
2.  Open the **SQL Editor** in your Supabase dashboard.
3.  Copy and paste the contents of `setup.sql` (found in the root directory) and run it. This will:
    *   Create `customers`, `products`, and `orders` tables.
    *   Enable Row Level Security (RLS).
    *   Setup public access policies for this demo.
    *   Seed the database with sample data.

### 2. Frontend Configuration
1.  Open `frontend/config.js`.
2.  Replace the placeholders with your actual **Supabase URL** and **Anon Key** (found in Project Settings -> API).

### 3. Backend Configuration
1.  Navigate to `backend/`.
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Open `backend/routes.py`.
4.  Replace `DB_CONNECTION_STRING` with your project's connection URI (found in Project Settings -> Database -> Connection string -> URI).
    *   *Note: Use the port 5432 and don't forget your database password.*
5.  Run the Flask server:
    ```bash
    python app.py
    ```

### 4. Run the Dashboard
Simply open `frontend/index.html` in your web browser!

## ✨ Features
*   **KPI Summary**: Real-time stats on Revenue, Orders, and Customers.
*   **Interactive Charts**: Monthly trends, category breakdowns, and growth tracking.
*   **Customer Management**: Add new customers via modal with validation.
*   **Real-time Clock**: Keeps track of local time in the header.
*   **Dark/Light Mode**: Premium glassmorphic UI that persists your preference.
*   **CSV Export**: Download customer data for offline analysis.
*   **Advanced Analytics**: Complex growth rates powered by the Flask-Supabase bridge.

## 📁 Project Structure
```
sales-dashboard/
├── backend/
│   ├── app.py          # Flask Entry
│   ├── routes.py       # Analytic Endpoints
│   └── requirements.txt
├── frontend/
│   ├── index.html      # Main SPA
│   ├── style.css       # Premium Styling
│   ├── app.js          # Core Logic
│   ├── charts.js       # Visualization Logic
│   └── config.js       # Supabase Config
├── setup.sql           # Database Setup Script
└── README.md
```
