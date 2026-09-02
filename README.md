# Sales Intelligence & Predictive Analytics Platform 📈🔮

A modern, full-stack **Sales Intelligence & Data Science Platform** designed to turn raw transactional logs into predictive business insights. Built with a Flask (Python) backend, SQLite database, NumPy analytics engine, and a premium glassmorphic frontend. 

This platform serves as a complete portfolio project showing end-to-end integration of predictive modeling, customer segmentation, statistical anomaly detection, and custom database engineering.

---

## 🌟 Key Features

### 🔮 1. Sales Forecasting (NumPy Regressions)
* Uses Ordinary Least Squares (OLS) **Linear and Polynomial (2nd Degree) regressions** implemented using `numpy.polyfit`.
* Fits models dynamically to historical monthly sales trends and projects predictions into the future.
* Lets users interactively toggle between linear (straight trajectory) and quadratic (accelerating/decelerating) curves.

### 👥 2. RFM Customer Segmentation
* Groups customers dynamically by evaluating three behaviors:
  * **Recency:** Time elapsed since the last purchase.
  * **Frequency:** Number of total purchases.
  * **Monetary:** Total value of spent currency.
* Generates a 3D scoring profile to categorize customers into strategic cohorts: **Champions** (VIP), **Loyal Customers**, and **At-Risk** customers.

### 🚨 3. Statistical Anomaly Detection
* Implements the **Interquartile Range (IQR)** method ($Q3 - Q1$) on transaction values.
* Automatically flags transactions that fall beyond bounds ($1.5 \times IQR$) to catch outliers, data-entry errors, or potential fraud in real-time.

### 🔒 4. Safe SQL Query Sandbox
* Features an interactive query editor allowing users to run custom SQLite statements.
* Incorporates regex-based security filters to restrict commands exclusively to `SELECT` operations, preventing any database write or deletion actions.

### 💾 5. Enterprise-Ready Data Exporting
* **Excel Safeguards:** Prepend UTF-8 BOM (`\ufeff`) to ensure clean character decoding.
* **Numeric Integrity:** Formats large IDs/mobile numbers into safe Excel text formulas (`="[number]"`) so Excel doesn't convert them to scientific notation (e.g. `9.88E+09`).
* **Print Styling:** Custom CSS `@media print` rules clean up the dashboard interface, providing tidy layouts when exporting reports to physical PDFs.

---

## 🛠️ Tech Stack

* **Frontend:** HTML5, Vanilla JavaScript, CSS3 (Custom Glassmorphism design system)
* **Backend:** Python, Flask, Flask-CORS
* **Calculations:** NumPy
* **Database:** SQLite3
* **Production Deployment:** Vercel (Frontend) & Render (Backend)

---

## 🚀 Setup & Installation

### Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the backend local server:
   ```bash
   python app.py
   ```
   *The backend will run on `http://127.0.0.1:5000`.*

### Frontend Setup
* Open `frontend/index.html` directly in your browser, or serve it using any local server (e.g. VS Code Live Server).
* The frontend automatically switches to the production backend URL when deployed, and targets `localhost:5000` during local development.

---

## 📁 Repository Structure

```
├── backend/
│   ├── app.py             # Flask application server & DS/ML endpoint handlers
│   ├── requirements.txt   # Python dependencies (Flask, NumPy, gunicorn, etc.)
│   ├── sales.db           # Seeded SQLite database
│   └── templates/         # Backend-served HTML views
├── frontend/
│   ├── index.html         # Premium Glassmorphic Dashboard UI
├── README.md              # Project Documentation
└── .gitignore             # Git exclusion guidelines
```
