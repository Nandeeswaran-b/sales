from flask import Flask, jsonify, request, render_template, Response
from flask_cors import CORS
import sqlite3
import os
import random
import datetime
import math
import statistics
import csv
import io
import logging

# NumPy for linear regression & analytics
import numpy as np

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sales.db')

PRODUCTS_CATALOG = [
    # Laptops
    ("Laptop (MacBook Pro)", "Laptops", 89999),
    ("Laptop (MacBook Air M3)", "Laptops", 114999),
    ("Laptop (Dell XPS 15)", "Laptops", 74999),
    ("Laptop (HP Pavilion)", "Laptops", 55999),
    ("Laptop (Lenovo ThinkPad X1)", "Laptops", 129999),
    ("Laptop (ASUS ROG Zephyrus)", "Laptops", 109999),
    ("Laptop (Acer Predator Helios)", "Laptops", 89999),
    ("Laptop (HP Spectre x360)", "Laptops", 99999),

    # Smartphones
    ("Smartphone (iPhone 15)", "Smartphones", 79999),
    ("Smartphone (iPhone 15 Pro Max)", "Smartphones", 159999),
    ("Smartphone (Samsung S24)", "Smartphones", 64999),
    ("Smartphone (Samsung Galaxy Fold 5)", "Smartphones", 149999),
    ("Smartphone (OnePlus 12)", "Smartphones", 44999),
    ("Smartphone (OnePlus Open)", "Smartphones", 139999),
    ("Smartphone (Google Pixel 8 Pro)", "Smartphones", 75999),
    ("Smartphone (Xiaomi 14 Ultra)", "Smartphones", 69999),
    ("Smartphone (Nothing Phone 2)", "Smartphones", 39999),
    ("Smartphone (Vivo X100 Pro)", "Smartphones", 79999),
    ("Smartphone (Realme GT 5)", "Smartphones", 34999),
    ("Smartphone (Motorola Edge 50)", "Smartphones", 32999),

    # Tablets
    ("Tablet (iPad Air)", "Tablets", 54999),
    ("Tablet (iPad Pro M4)", "Tablets", 99999),
    ("Tablet (Galaxy Tab S9)", "Tablets", 44999),
    ("Tablet (Lenovo Tab P12)", "Tablets", 29999),

    # Wearables
    ("Smartwatch (Apple Watch)", "Wearables", 34999),
    ("Smartwatch (Samsung Galaxy)", "Wearables", 24999),
    ("Smartwatch (Garmin Fenix 7)", "Wearables", 64999),
    ("Smartwatch (Fitbit Sense 2)", "Wearables", 19999),

    # Audio
    ("Wireless Earbuds (AirPods Pro)", "Audio", 24999),
    ("Wireless Earbuds (Samsung Buds 2 Pro)", "Audio", 14999),
    ("Wireless Earbuds (Sony WF-1000XM5)", "Audio", 22999),
    ("Over-ear Headphones (Sony WH)", "Audio", 19999),
    ("Over-ear Headphones (Bose QuietComfort)", "Audio", 29999),

    # Televisions
    ("4K Television (LG OLED 55\")", "Televisions", 119999),
    ("4K Television (Samsung 50\")", "Televisions", 69999),
    ("Sony Bravia 65\" 4K Google TV", "Televisions", 89999),
    ("Xiaomi Smart TV 55\"", "Televisions", 34999),

    # Gaming
    ("Gaming Console (PS5)", "Gaming", 49999),
    ("Gaming Console (Xbox Series X)", "Gaming", 49999),
    ("Nintendo Switch OLED", "Gaming", 32999),
    ("Steam Deck OLED", "Gaming", 54999),

    # Monitors
    ("External Monitor (Dell 27\")", "Monitors", 29999),

    # Accessories
    ("Wireless Mouse/Keyboard Combo", "Accessories", 3999),
    ("Mechanical Keyboard (Keychron K2)", "Accessories", 7999),
    ("Wireless Gaming Mouse (Logitech G502)", "Accessories", 6999),
    ("USB-C Hub Adapter", "Accessories", 2999),
    ("Laptop Bag (Premium)", "Accessories", 4999),
]


# ═══════════════════════════════════════════════════════════════════════════════
#  DATABASE HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sale_date TEXT NOT NULL,
            product_name TEXT NOT NULL,
            category TEXT NOT NULL,
            customer_name TEXT NOT NULL,
            mobile_no TEXT,
            mode_of_payment TEXT DEFAULT 'Cash',
            total_price REAL NOT NULL,
            region TEXT DEFAULT 'North',
            salesperson TEXT DEFAULT 'Anjali Sharma',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Ensure region and salesperson columns exist if database was already initialized without them
    try:
        conn.execute("ALTER TABLE sales ADD COLUMN region TEXT DEFAULT 'North'")
    except sqlite3.OperationalError:
        pass
    try:
        conn.execute("ALTER TABLE sales ADD COLUMN salesperson TEXT DEFAULT 'Anjali Sharma'")
    except sqlite3.OperationalError:
        pass

    # Prediction History & Cache Tables
    conn.execute('''
        CREATE TABLE IF NOT EXISTS churn_predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            last_purchase_date TEXT,
            total_orders INTEGER,
            lifetime_value REAL,
            churn_risk_score REAL,
            risk_category TEXT,
            ai_reason TEXT,
            recommended_action TEXT,
            prediction_date TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS weather_predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city TEXT NOT NULL,
            weather_condition TEXT,
            temperature REAL,
            sales_impact TEXT,
            recommended_products TEXT,
            ai_insights TEXT,
            prediction_date TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS weather_cache (
            city TEXT PRIMARY KEY,
            weather_data TEXT,
            timestamp INTEGER
        )
    ''')
    conn.commit()

    cursor = conn.execute('SELECT COUNT(*) FROM sales')
    count = cursor.fetchone()[0]
    if count == 0:
        seed_data(conn)
    conn.close()



def seed_data(conn):
    """Insert realistic sample sales data spanning 8 months."""
    products = PRODUCTS_CATALOG

    customers = [
        ("Rahul Sharma", "9876543210"),
        ("Priya Patel", "9876543211"),
        ("Amit Kumar", "9876543212"),
        ("Sneha Reddy", "9876543213"),
        ("Vikram Singh", "9876543214"),
        ("Ananya Gupta", "9876543215"),
        ("Rohan Mehta", "9876543216"),
        ("Kavita Nair", "9876543217"),
        ("Arjun Das", "9876543218"),
        ("Meera Joshi", "9876543219"),
        ("Suresh Iyer", "9876543220"),
        ("Deepa Menon", "9876543221"),
        ("Karthik Rao", "9876543222"),
        ("Pooja Verma", "9876543223"),
        ("Nikhil Saxena", "9876543224"),
        ("Lakshmi Nair", "9876543225"),
        ("Rajesh Khanna", "9876543226"),
        ("Divya Krishnan", "9876543227"),
        ("Arun Pillai", "9876543228"),
        ("Sanya Malhotra", "9876543229"),
    ]

    payments = ["Cash", "Credit Card", "Debit Card", "UPI", "Bank Transfer"]

    today = datetime.date.today()
    records = []

    # Generate 200 records over 8 months with a realistic growth trend
    for i in range(200):
        days_back = random.randint(0, 240)
        sale_date = today - datetime.timedelta(days=days_back)

        # Bias towards more recent sales (growth trend)
        if random.random() < 0.3:
            days_back = random.randint(0, 60)
            sale_date = today - datetime.timedelta(days=days_back)

        product_name, category, base_price = random.choice(products)
        price_variation = base_price * random.uniform(0.88, 1.12)
        total_price = round(price_variation, 2)

        # Occasionally add anomalous high-value sales
        if random.random() < 0.03:
            total_price = round(total_price * random.uniform(2.5, 4.0), 2)

        customer_name, mobile_no = random.choice(customers)
        payment = random.choice(payments)
        
        regions = ["North", "South", "East", "West", "Central"]
        salespersons = ["Anjali Sharma", "Vikram Goel", "Sarah Jones", "David Miller", "Elena Rostova"]
        region = random.choice(regions)
        salesperson = random.choice(salespersons)

        records.append((
            sale_date.isoformat(),
            product_name,
            category,
            customer_name,
            mobile_no,
            payment,
            total_price,
            region,
            salesperson
        ))

    conn.executemany('''
        INSERT INTO sales (sale_date, product_name, category, customer_name, mobile_no, mode_of_payment, total_price, region, salesperson)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', records)
    conn.commit()
    logger.info(f"Seeded {len(records)} sales records.")



# ═══════════════════════════════════════════════════════════════════════════════
#  CORE ROUTES — Dashboard Data
# ═══════════════════════════════════════════════════════════════════════════════

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/summary', methods=['GET'])
def get_summary():
    conn = get_db()
    try:
        row = conn.execute('SELECT COALESCE(SUM(total_price), 0) as total_revenue, COUNT(*) as total_orders FROM sales').fetchone()
        top = conn.execute('''
            SELECT product_name, COUNT(*) as cnt
            FROM sales GROUP BY product_name ORDER BY cnt DESC LIMIT 1
        ''').fetchone()

        # Month-over-month growth
        growth_data = conn.execute('''
            SELECT strftime('%Y-%m', sale_date) as month, SUM(total_price) as revenue
            FROM sales GROUP BY month ORDER BY month DESC LIMIT 2
        ''').fetchall()

        mom_growth = 0
        if len(growth_data) >= 2:
            current = growth_data[0]['revenue']
            previous = growth_data[1]['revenue']
            if previous > 0:
                mom_growth = round(((current - previous) / previous) * 100, 1)

        avg_order = row['total_revenue'] / row['total_orders'] if row['total_orders'] > 0 else 0

        return jsonify({
            'total_revenue': row['total_revenue'],
            'total_orders': row['total_orders'],
            'top_product': top['product_name'] if top else '-',
            'avg_order_value': round(avg_order, 2),
            'mom_growth': mom_growth
        })
    finally:
        conn.close()


@app.route('/api/chart/monthly', methods=['GET'])
def chart_monthly():
    conn = get_db()
    try:
        rows = conn.execute('''
            SELECT strftime('%Y-%m', sale_date) as month, SUM(total_price) as revenue
            FROM sales GROUP BY month ORDER BY month
        ''').fetchall()
        return jsonify([{'month': r['month'], 'revenue': r['revenue']} for r in rows])
    finally:
        conn.close()


@app.route('/api/chart/category', methods=['GET'])
def chart_category():
    conn = get_db()
    try:
        rows = conn.execute('''
            SELECT category, SUM(total_price) as revenue, COUNT(*) as count
            FROM sales GROUP BY category ORDER BY revenue DESC
        ''').fetchall()
        return jsonify([{'category': r['category'], 'revenue': r['revenue'], 'count': r['count']} for r in rows])
    finally:
        conn.close()


@app.route('/api/chart/customers', methods=['GET'])
def chart_customers():
    conn = get_db()
    try:
        rows = conn.execute('''
            SELECT customer_name as name, SUM(total_price) as revenue, COUNT(*) as orders
            FROM sales GROUP BY customer_name ORDER BY revenue DESC LIMIT 5
        ''').fetchall()
        return jsonify([{'name': r['name'], 'revenue': r['revenue'], 'orders': r['orders']} for r in rows])
    finally:
        conn.close()


@app.route('/api/sales', methods=['GET'])
def get_sales():
    conn = get_db()
    try:
        rows = conn.execute('''
            SELECT id, sale_date, product_name, category, customer_name, mobile_no, mode_of_payment, total_price
            FROM sales ORDER BY sale_date DESC, id DESC
        ''').fetchall()
        return jsonify([dict(r) for r in rows])
    finally:
        conn.close()


@app.route('/api/sales/new', methods=['POST'])
def add_sale():
    data = request.json
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    for field in ['customer_name', 'product_name', 'total_price', 'sale_date']:
        if not data.get(field):
            return jsonify({'error': f'Missing field: {field}'}), 400

    category = guess_category(data['product_name'])
    conn = get_db()
    try:
        conn.execute('''
            INSERT INTO sales (sale_date, product_name, category, customer_name, mobile_no, mode_of_payment, total_price)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['sale_date'], data['product_name'], category,
            data['customer_name'], data.get('mobile_no', ''),
            data.get('mode_of_payment', 'Cash'), float(data['total_price'])
        ))
        conn.commit()
        return jsonify({'message': 'Sale added successfully'}), 201
    finally:
        conn.close()


# ═══════════════════════════════════════════════════════════════════════════════
#  ANALYTICS ROUTES — Data Science Features
# ═══════════════════════════════════════════════════════════════════════════════

@app.route('/api/analytics/forecast', methods=['GET'])
@app.route('/api/analytics/forecast', methods=['GET'])
def analytics_forecast():
    """
    Sales forecasting using Linear/Quadratic Polynomial Regression (NumPy).
    Fits a curve to monthly revenue data and projects 3 months forward.
    Returns historical data + forecast with confidence intervals.
    """
    degree = request.args.get('degree', default=1, type=int)
    if degree not in [1, 2]:
        degree = 1

    conn = get_db()
    try:
        rows = conn.execute('''
            SELECT strftime('%Y-%m', sale_date) as month, SUM(total_price) as revenue
            FROM sales GROUP BY month ORDER BY month
        ''').fetchall()

        months = [r['month'] for r in rows]
        revenues = [r['revenue'] for r in rows]
        n = len(revenues)

        if n < (degree + 1):
            # Fallback to linear if not enough data points
            degree = 1
            if n < 2:
                return jsonify({'error': 'Not enough data for forecasting'}), 400

        # Regression using NumPy
        x = np.arange(n, dtype=float)
        y = np.array(revenues, dtype=float)

        coefficients = np.polyfit(x, y, degree)
        y_pred = np.polyval(coefficients, x)

        # R-squared
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r_squared = float(1 - (ss_res / ss_tot)) if ss_tot > 0 else 0

        # Standard error for confidence interval
        dof = n - degree - 1
        std_error = float(np.sqrt(ss_res / dof)) if dof > 0 else 0

        # Construct fitted model metadata
        if degree == 1:
            slope = float(coefficients[0])
            intercept = float(coefficients[1])
            equation = f'Revenue = {slope:.2f} × month + {intercept:.2f}'
        else:
            a = float(coefficients[0])
            b = float(coefficients[1])
            c = float(coefficients[2])
            equation = f'Revenue = {a:.2f} × month² + {b:.2f} × month + {c:.2f}'

        # Historical fitted values
        historical = []
        for i in range(n):
            historical.append({
                'month': months[i],
                'actual': revenues[i],
                'fitted': round(float(y_pred[i]), 2)
            })

        # Forecast next 3 months
        forecast = []
        last_date = datetime.datetime.strptime(months[-1], '%Y-%m')
        for i in range(1, 4):
            future_date = last_date + datetime.timedelta(days=30 * i)
            future_month = future_date.strftime('%Y-%m')
            future_x = n + i - 1
            predicted = float(np.polyval(coefficients, future_x))
            lower = predicted - 1.96 * std_error
            upper = predicted + 1.96 * std_error

            forecast.append({
                'month': future_month,
                'predicted': round(max(0, predicted), 2),
                'lower_bound': round(max(0, lower), 2),
                'upper_bound': round(upper, 2)
            })

        return jsonify({
            'historical': historical,
            'forecast': forecast,
            'model': {
                'degree': degree,
                'r_squared': round(r_squared, 4),
                'std_error': round(std_error, 2),
                'equation': equation
            }
        })
    finally:
        conn.close()


@app.route('/api/simulation/generate', methods=['POST'])
def simulation_generate():
    """Generates custom simulated datasets based on trend bias and outlier rate."""
    data = request.json or {}
    n_records = int(data.get('n_records', 200))
    trend = data.get('trend', 'positive')
    anomaly_rate = float(data.get('anomaly_rate', 0.03))

    # Clamp parameters
    n_records = max(50, min(1000, n_records))
    anomaly_rate = max(0.0, min(0.2, anomaly_rate))

    products = PRODUCTS_CATALOG

    customers = [
        ("Rahul Sharma", "9876543210"),
        ("Priya Patel", "9876543211"),
        ("Amit Kumar", "9876543212"),
        ("Sneha Reddy", "9876543213"),
        ("Vikram Singh", "9876543214"),
        ("Ananya Gupta", "9876543215"),
        ("Rohan Mehta", "9876543216"),
        ("Kavita Nair", "9876543217"),
        ("Arjun Das", "9876543218"),
        ("Meera Joshi", "9876543219"),
        ("Suresh Iyer", "9876543220"),
        ("Deepa Menon", "9876543221"),
        ("Karthik Rao", "9876543222"),
        ("Pooja Verma", "9876543223"),
        ("Nikhil Saxena", "9876543224"),
        ("Lakshmi Nair", "9876543225"),
        ("Rajesh Khanna", "9876543226"),
        ("Divya Krishnan", "9876543227"),
        ("Arun Pillai", "9876543228"),
        ("Sanya Malhotra", "9876543229"),
    ]

    payments = ["Cash", "Credit Card", "Debit Card", "UPI", "Bank Transfer"]
    today = datetime.date.today()
    records = []

    for i in range(n_records):
        if trend == 'positive':
            days_back = int(random.triangular(0, 240, 0))
        elif trend == 'negative':
            days_back = int(random.triangular(0, 240, 240))
        else:
            days_back = random.randint(0, 240)

        sale_date = today - datetime.timedelta(days=days_back)
        product_name, category, base_price = random.choice(products)
        price_variation = base_price * random.uniform(0.88, 1.12)
        total_price = round(price_variation, 2)

        # Apply simulation anomalies
        if random.random() < anomaly_rate:
            total_price = round(total_price * random.uniform(2.5, 4.0), 2)

        customer_name, mobile_no = random.choice(customers)
        payment = random.choice(payments)

        records.append((
            sale_date.isoformat(),
            product_name,
            category,
            customer_name,
            mobile_no,
            payment,
            total_price
        ))

    conn = get_db()
    try:
        conn.execute('DELETE FROM sales')
        conn.executemany('''
            INSERT INTO sales (sale_date, product_name, category, customer_name, mobile_no, mode_of_payment, total_price)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', records)
        conn.commit()
    finally:
        conn.close()

    return jsonify({
        'message': f'Simulated {n_records} sales records successfully!',
        'records_count': n_records,
        'trend': trend,
        'anomaly_rate': anomaly_rate
    }), 200


@app.route('/api/analytics/stats', methods=['GET'])
def analytics_stats():
    """
    Descriptive statistics for sales data.
    Returns mean, median, mode, std dev, variance, skewness, kurtosis, quartiles.
    """
    conn = get_db()
    try:
        rows = conn.execute('SELECT total_price FROM sales ORDER BY total_price').fetchall()
        prices = [r['total_price'] for r in rows]
        n = len(prices)

        if n == 0:
            return jsonify({'error': 'No data'}), 400

        np_prices = np.array(prices)

        # Quartiles
        q1 = float(np.percentile(np_prices, 25))
        q2 = float(np.percentile(np_prices, 50))
        q3 = float(np.percentile(np_prices, 75))
        iqr = q3 - q1

        # Skewness: (3 * (mean - median)) / std_dev
        mean_val = float(np.mean(np_prices))
        std_val = float(np.std(np_prices, ddof=1))
        median_val = float(np.median(np_prices))
        skewness = 0
        if std_val > 0:
            skewness = float(np.mean(((np_prices - mean_val) / std_val) ** 3))

        # Kurtosis
        kurtosis = 0
        if std_val > 0:
            kurtosis = float(np.mean(((np_prices - mean_val) / std_val) ** 4) - 3)

        # Mode (most common price range, binned to nearest 1000)
        binned = [round(p / 1000) * 1000 for p in prices]
        mode_val = max(set(binned), key=binned.count)

        return jsonify({
            'count': n,
            'mean': round(mean_val, 2),
            'median': round(median_val, 2),
            'mode_range': mode_val,
            'std_dev': round(std_val, 2),
            'variance': round(float(np.var(np_prices, ddof=1)), 2),
            'min': round(float(np.min(np_prices)), 2),
            'max': round(float(np.max(np_prices)), 2),
            'range': round(float(np.max(np_prices) - np.min(np_prices)), 2),
            'q1': round(q1, 2),
            'q2': round(q2, 2),
            'q3': round(q3, 2),
            'iqr': round(iqr, 2),
            'skewness': round(skewness, 4),
            'kurtosis': round(kurtosis, 4),
            'coefficient_of_variation': round((std_val / mean_val) * 100, 2) if mean_val > 0 else 0
        })
    finally:
        conn.close()


@app.route('/api/analytics/rfm', methods=['GET'])
def analytics_rfm():
    """
    RFM (Recency, Frequency, Monetary) Customer Segmentation.
    Scores customers on 3 dimensions and assigns segments.
    """
    conn = get_db()
    try:
        today = datetime.date.today().isoformat()
        rows = conn.execute('''
            SELECT
                customer_name,
                mobile_no,
                julianday(?) - julianday(MAX(sale_date)) as recency,
                COUNT(*) as frequency,
                SUM(total_price) as monetary,
                AVG(total_price) as avg_order
            FROM sales
            GROUP BY customer_name
        ''', (today,)).fetchall()

        if not rows:
            return jsonify([])

        customers = [dict(r) for r in rows]

        # Calculate RFM scores (1-5 scale using quintiles)
        recencies = [c['recency'] for c in customers]
        frequencies = [c['frequency'] for c in customers]
        monetaries = [c['monetary'] for c in customers]

        def score_quintile(values, reverse=False):
            """Assign 1-5 score based on quintiles. reverse=True means lower is better (recency)."""
            arr = np.array(values, dtype=float)
            percentiles = [np.percentile(arr, p) for p in [20, 40, 60, 80]]
            scores = []
            for v in values:
                if v <= percentiles[0]:
                    scores.append(5 if reverse else 1)
                elif v <= percentiles[1]:
                    scores.append(4 if reverse else 2)
                elif v <= percentiles[2]:
                    scores.append(3)
                elif v <= percentiles[3]:
                    scores.append(2 if reverse else 4)
                else:
                    scores.append(1 if reverse else 5)
            return scores

        r_scores = score_quintile(recencies, reverse=True)  # Lower recency = better
        f_scores = score_quintile(frequencies, reverse=False)
        m_scores = score_quintile(monetaries, reverse=False)

        result = []
        for i, c in enumerate(customers):
            r, f, m = r_scores[i], f_scores[i], m_scores[i]
            rfm_score = r + f + m
            segment = classify_rfm(r, f, m)

            result.append({
                'customer_name': c['customer_name'],
                'mobile_no': c['mobile_no'],
                'recency_days': round(c['recency'], 1),
                'frequency': c['frequency'],
                'monetary': round(c['monetary'], 2),
                'avg_order': round(c['avg_order'], 2),
                'r_score': r,
                'f_score': f,
                'm_score': m,
                'rfm_score': rfm_score,
                'segment': segment
            })

        # Sort by RFM score descending
        result.sort(key=lambda x: x['rfm_score'], reverse=True)
        return jsonify(result)
    finally:
        conn.close()


def classify_rfm(r, f, m):
    """Classify customer into segments based on RFM scores."""
    total = r + f + m
    if r >= 4 and f >= 4 and m >= 4:
        return 'Champions'
    elif r >= 3 and f >= 3 and m >= 3:
        return 'Loyal Customers'
    elif r >= 4 and f <= 2:
        return 'New Customers'
    elif r >= 3 and f >= 2 and m >= 2:
        return 'Potential Loyalists'
    elif r <= 2 and f >= 3 and m >= 3:
        return 'At Risk'
    elif r <= 2 and f <= 2 and m >= 3:
        return 'Cannot Lose'
    elif r <= 2 and f <= 2 and m <= 2:
        return 'Lost'
    elif total >= 10:
        return 'Loyal Customers'
    elif total >= 7:
        return 'Potential Loyalists'
    else:
        return 'Need Attention'


@app.route('/api/analytics/anomalies', methods=['GET'])
def analytics_anomalies():
    """
    Anomaly Detection using IQR (Interquartile Range) method.
    Flags sales that fall outside 1.5×IQR from Q1/Q3.
    """
    conn = get_db()
    try:
        rows = conn.execute('''
            SELECT id, sale_date, product_name, category, customer_name, total_price
            FROM sales ORDER BY sale_date DESC
        ''').fetchall()

        prices = [r['total_price'] for r in rows]
        np_prices = np.array(prices)

        q1 = float(np.percentile(np_prices, 25))
        q3 = float(np.percentile(np_prices, 75))
        iqr = q3 - q1
        lower_fence = q1 - 1.5 * iqr
        upper_fence = q3 + 1.5 * iqr

        # Z-scores
        mean_price = float(np.mean(np_prices))
        std_price = float(np.std(np_prices, ddof=1))

        anomalies = []
        normal = []

        for r in rows:
            price = r['total_price']
            z_score = (price - mean_price) / std_price if std_price > 0 else 0
            is_anomaly = price < lower_fence or price > upper_fence
            entry = {
                'id': r['id'],
                'sale_date': r['sale_date'],
                'product_name': r['product_name'],
                'category': r['category'],
                'customer_name': r['customer_name'],
                'total_price': price,
                'z_score': round(z_score, 3),
                'is_anomaly': is_anomaly,
                'anomaly_type': 'high' if price > upper_fence else ('low' if price < lower_fence else 'normal')
            }
            if is_anomaly:
                anomalies.append(entry)
            else:
                normal.append(entry)

        return jsonify({
            'thresholds': {
                'q1': round(q1, 2),
                'q3': round(q3, 2),
                'iqr': round(iqr, 2),
                'lower_fence': round(max(0, lower_fence), 2),
                'upper_fence': round(upper_fence, 2),
                'mean': round(mean_price, 2),
                'std_dev': round(std_price, 2)
            },
            'anomaly_count': len(anomalies),
            'total_count': len(rows),
            'anomaly_rate': round(len(anomalies) / len(rows) * 100, 1) if rows else 0,
            'anomalies': anomalies
        })
    finally:
        conn.close()


@app.route('/api/analytics/correlation', methods=['GET'])
def analytics_correlation():
    """
    Correlation analysis between numeric features.
    Computes Pearson correlation matrix.
    """
    conn = get_db()
    try:
        rows = conn.execute('''
            SELECT
                total_price,
                CAST(strftime('%m', sale_date) AS INTEGER) as sale_month,
                CAST(strftime('%w', sale_date) AS INTEGER) as day_of_week,
                CASE mode_of_payment
                    WHEN 'Cash' THEN 1
                    WHEN 'UPI' THEN 2
                    WHEN 'Credit Card' THEN 3
                    WHEN 'Debit Card' THEN 4
                    WHEN 'Bank Transfer' THEN 5
                    ELSE 0
                END as payment_encoded
            FROM sales
        ''').fetchall()

        if not rows:
            return jsonify({'error': 'No data'}), 400

        features = {
            'Price': [r['total_price'] for r in rows],
            'Month': [r['sale_month'] for r in rows],
            'Day of Week': [r['day_of_week'] for r in rows],
            'Payment Type': [r['payment_encoded'] for r in rows],
        }

        feature_names = list(features.keys())
        data_matrix = np.array([features[name] for name in feature_names])

        # Compute correlation matrix
        corr_matrix = np.corrcoef(data_matrix)

        result = {
            'features': feature_names,
            'matrix': [[round(float(corr_matrix[i][j]), 4) for j in range(len(feature_names))] for i in range(len(feature_names))]
        }

        return jsonify(result)
    finally:
        conn.close()


@app.route('/api/analytics/distribution', methods=['GET'])
def analytics_distribution():
    """
    Price distribution data for histogram visualization.
    Returns bin counts, bin edges, and normal distribution overlay data.
    """
    conn = get_db()
    try:
        rows = conn.execute('SELECT total_price FROM sales ORDER BY total_price').fetchall()
        prices = [r['total_price'] for r in rows]
        np_prices = np.array(prices)

        # Create histogram bins
        num_bins = 15
        counts, bin_edges = np.histogram(np_prices, bins=num_bins)

        bins = []
        for i in range(len(counts)):
            bins.append({
                'bin_start': round(float(bin_edges[i]), 2),
                'bin_end': round(float(bin_edges[i + 1]), 2),
                'count': int(counts[i]),
                'label': f'₹{int(bin_edges[i] / 1000)}K - ₹{int(bin_edges[i + 1] / 1000)}K'
            })

        # Normal distribution overlay
        mean = float(np.mean(np_prices))
        std = float(np.std(np_prices, ddof=1))
        x_range = np.linspace(float(np.min(np_prices)), float(np.max(np_prices)), 50)
        normal_curve = []
        for x_val in x_range:
            y_val = (1 / (std * math.sqrt(2 * math.pi))) * math.exp(-0.5 * ((x_val - mean) / std) ** 2)
            # Scale to match histogram counts
            bin_width = float(bin_edges[1] - bin_edges[0])
            y_scaled = y_val * len(prices) * bin_width
            normal_curve.append({'x': round(float(x_val), 2), 'y': round(y_scaled, 4)})

        return jsonify({
            'bins': bins,
            'normal_curve': normal_curve,
            'stats': {
                'mean': round(mean, 2),
                'std': round(std, 2),
                'n': len(prices)
            }
        })
    finally:
        conn.close()


@app.route('/api/analytics/growth', methods=['GET'])
def analytics_growth():
    """
    Month-over-month growth analysis.
    Returns growth rates, cumulative revenue, and trend direction.
    """
    conn = get_db()
    try:
        rows = conn.execute('''
            SELECT
                strftime('%Y-%m', sale_date) as month,
                SUM(total_price) as revenue,
                COUNT(*) as orders,
                AVG(total_price) as avg_order
            FROM sales
            GROUP BY month
            ORDER BY month
        ''').fetchall()

        data = [dict(r) for r in rows]
        cumulative = 0
        result = []

        for i, d in enumerate(data):
            cumulative += d['revenue']
            growth_rate = 0
            if i > 0 and data[i - 1]['revenue'] > 0:
                growth_rate = ((d['revenue'] - data[i - 1]['revenue']) / data[i - 1]['revenue']) * 100

            result.append({
                'month': d['month'],
                'revenue': round(d['revenue'], 2),
                'orders': d['orders'],
                'avg_order': round(d['avg_order'], 2),
                'growth_rate': round(growth_rate, 1),
                'cumulative_revenue': round(cumulative, 2),
                'trend': 'up' if growth_rate > 0 else ('down' if growth_rate < 0 else 'flat')
            })

        # Overall metrics
        revenues = [d['revenue'] for d in data]
        overall_growth = 0
        if len(revenues) >= 2 and revenues[0] > 0:
            overall_growth = ((revenues[-1] - revenues[0]) / revenues[0]) * 100

        return jsonify({
            'monthly': result,
            'summary': {
                'overall_growth': round(overall_growth, 1),
                'best_month': max(data, key=lambda x: x['revenue'])['month'] if data else None,
                'worst_month': min(data, key=lambda x: x['revenue'])['month'] if data else None,
                'avg_monthly_revenue': round(sum(revenues) / len(revenues), 2) if revenues else 0,
                'total_months': len(data)
            }
        })
    finally:
        conn.close()


# ═══════════════════════════════════════════════════════════════════════════════
#  EXPORT — CSV Download
# ═══════════════════════════════════════════════════════════════════════════════

@app.route('/api/export/csv', methods=['GET'])
def export_csv():
    """Export all sales data as downloadable CSV."""
    conn = get_db()
    try:
        rows = conn.execute('''
            SELECT id, sale_date, product_name, category, customer_name, mobile_no, mode_of_payment, total_price
            FROM sales ORDER BY sale_date DESC
        ''').fetchall()

        output = io.StringIO()
        # Add UTF-8 BOM for Excel compatibility
        output.write('\ufeff')
        writer = csv.writer(output)
        writer.writerow(['ID', 'Date', 'Product', 'Category', 'Customer', 'Mobile', 'Payment', 'Price'])
        for r in rows:
            # Escape mobile number as an Excel formula to force it as text format
            excel_mobile = f'="{r["mobile_no"]}"' if r["mobile_no"] else ''
            writer.writerow([r['id'], r['sale_date'], r['product_name'], r['category'],
                           r['customer_name'], excel_mobile, r['mode_of_payment'], r['total_price']])

        csv_content = output.getvalue()
        return Response(
            csv_content,
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment; filename=sales_data_export.csv'}
        )
    finally:
        conn.close()


# ═══════════════════════════════════════════════════════════════════════════════
#  UTILITIES
# ═══════════════════════════════════════════════════════════════════════════════

def guess_category(product_name):
    name_lower = product_name.lower()
    mapping = {
        'laptop': 'Laptops', 'macbook': 'Laptops', 'dell': 'Laptops', 'hp ': 'Laptops',
        'smartphone': 'Smartphones', 'phone': 'Smartphones', 'iphone': 'Smartphones', 'samsung s': 'Smartphones', 'oneplus': 'Smartphones',
        'tablet': 'Tablets', 'ipad': 'Tablets', 'galaxy tab': 'Tablets',
        'watch': 'Wearables',
        'earbuds': 'Audio', 'headphone': 'Audio', 'airpods': 'Audio',
        'television': 'Televisions', ' tv': 'Televisions',
        'console': 'Gaming', 'ps5': 'Gaming', 'xbox': 'Gaming',
        'monitor': 'Monitors',
        'mouse': 'Accessories', 'keyboard': 'Accessories', 'hub': 'Accessories', 'bag': 'Accessories',
    }
    for keyword, cat in mapping.items():
        if keyword in name_lower:
            return cat
    return 'Other'


# ═══════════════════════════════════════════════════════════════════════════════
#  NEW DS FEATURES: SQL CONSOLE & GOAL SEEK PLANNER
# ═══════════════════════════════════════════════════════

@app.route('/api/query', methods=['POST'])
def execute_query():
    """Run a safe SELECT query on the SQLite sales database and return rows/columns."""
    data = request.json or {}
    query = data.get('query', '')

    query_clean = query.strip().lower()
    if not query_clean.startswith('select'):
        return jsonify({'error': 'Security restriction: Only SELECT queries are permitted in this console.'}), 400

    conn = get_db()
    try:
        cursor = conn.execute(query)
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        result = [dict(r) for r in rows]
        return jsonify({
            'columns': columns,
            'rows': result
        }), 200
    except sqlite3.Error as e:
        return jsonify({'error': f'Database Error: {str(e)}'}), 400
    finally:
        conn.close()


@app.route('/api/analytics/goalseek', methods=['GET'])
def analytics_goalseek():
    """Predicts required metrics (order volume, target AOV) to hit a custom revenue target."""
    target = request.args.get('target', type=float)
    if not target or target <= 0:
        return jsonify({'error': 'Target revenue must be a positive number.'}), 400

    conn = get_db()
    try:
        row = conn.execute('SELECT COALESCE(SUM(total_price), 0) as total_rev, COUNT(*) as total_orders FROM sales').fetchone()
        total_rev = row['total_rev']
        total_orders = row['total_orders']

        if total_orders == 0:
            return jsonify({'error': 'Empty database. Seed data first.'}), 400

        aov = total_rev / total_orders

        # Calculate months count in DB
        months_data = conn.execute("SELECT strftime('%Y-%m', sale_date) as month, SUM(total_price) as rev FROM sales GROUP BY month").fetchall()
        n_months = len(months_data)
        avg_monthly_rev = total_rev / n_months if n_months > 0 else total_rev
        avg_orders_per_month = total_orders / n_months if n_months > 0 else total_orders

        # prescriptive values
        orders_needed = math.ceil(target / aov)
        aov_needed = round(target / avg_orders_per_month, 2) if avg_orders_per_month > 0 else target
        diff_amount = target - avg_monthly_rev
        growth_needed = round((diff_amount / avg_monthly_rev) * 100, 1) if avg_monthly_rev > 0 else 0

        return jsonify({
            'target_revenue': target,
            'avg_monthly_revenue': round(avg_monthly_rev, 2),
            'current_aov': round(aov, 2),
            'orders_needed': orders_needed,
            'aov_needed': aov_needed,
            'avg_monthly_orders': round(avg_orders_per_month, 1),
            'difference_amount': round(diff_amount, 2),
            'percent_change_needed': growth_needed
        }), 200
    finally:
        conn.close()


# ═══════════════════════════════════════════════════════════════════════════════
#  AI-POWERED CHURN & WEATHER SALES PREDICTIONS (SUPABASE INTEGRATED)
# ═══════════════════════════════════════════════════════════════════════════════

import requests
import json
import time

SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY')
OPENWEATHER_API_KEY = os.environ.get('OPENWEATHER_API_KEY')

def get_supabase_client():
    if SUPABASE_URL and SUPABASE_KEY:
        return {
            'url': SUPABASE_URL.rstrip('/'),
            'headers': {
                'apikey': SUPABASE_KEY,
                'Authorization': f'Bearer {SUPABASE_KEY}',
                'Content-Type': 'application/json',
                'Prefer': 'return=representation'
            }
        }
    return None

def store_churn_prediction(customer_name, last_purchase_date, total_orders, lifetime_value, churn_risk_score, risk_category, ai_reason, recommended_action):
    client = get_supabase_client()
    if client:
        try:
            url = f"{client['url']}/rest/v1/churn_predictions"
            payload = {
                'customer_name': customer_name,
                'last_purchase_date': last_purchase_date,
                'total_orders': int(total_orders),
                'lifetime_value': float(lifetime_value),
                'churn_risk_score': float(churn_risk_score),
                'risk_category': risk_category,
                'ai_reason': ai_reason,
                'recommended_action': recommended_action
            }
            res = requests.post(url, json=payload, headers=client['headers'], timeout=5)
            if res.status_code in [200, 201]:
                return True
        except Exception as e:
            logger.error(f"Supabase churn insert failed: {e}")
            
    # SQLite fallback
    try:
        conn = get_db()
        conn.execute('''
            INSERT INTO churn_predictions (customer_name, last_purchase_date, total_orders, lifetime_value, churn_risk_score, risk_category, ai_reason, recommended_action)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (customer_name, last_purchase_date, total_orders, lifetime_value, churn_risk_score, risk_category, ai_reason, recommended_action))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"SQLite churn insert failed: {e}")
        return False

def store_weather_prediction(city, weather_condition, temperature, sales_impact, recommended_products, ai_insights):
    client = get_supabase_client()
    if client:
        try:
            url = f"{client['url']}/rest/v1/weather_predictions"
            payload = {
                'city': city,
                'weather_condition': weather_condition,
                'temperature': float(temperature),
                'sales_impact': sales_impact,
                'recommended_products': recommended_products,
                'ai_insights': ai_insights
            }
            res = requests.post(url, json=payload, headers=client['headers'], timeout=5)
            if res.status_code in [200, 201]:
                return True
        except Exception as e:
            logger.error(f"Supabase weather insert failed: {e}")
            
    # SQLite fallback
    try:
        conn = get_db()
        conn.execute('''
            INSERT INTO weather_predictions (city, weather_condition, temperature, sales_impact, recommended_products, ai_insights)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (city, weather_condition, temperature, sales_impact, recommended_products, ai_insights))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"SQLite weather insert failed: {e}")
        return False


@app.route('/api/analytics/churn', methods=['GET'])
def get_churn_predictions():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    region = request.args.get('region')
    salesperson = request.args.get('salesperson')

    conn = get_db()
    try:
        # Get reference date for Recency (max sale date in system or today)
        ref_row = conn.execute("SELECT COALESCE(MAX(sale_date), date('now')) as max_date FROM sales").fetchone()
        ref_date_str = ref_row['max_date']
        ref_date = datetime.datetime.strptime(ref_date_str.split('T')[0], '%Y-%m-%d').date()

        # Fetch records based on filters
        query = "SELECT sale_date, customer_name, total_price, region, salesperson FROM sales WHERE 1=1"
        params = []
        if start_date:
            query += " AND sale_date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND sale_date <= ?"
            params.append(end_date)
        if region:
            query += " AND region = ?"
            params.append(region)
        if salesperson:
            query += " AND salesperson = ?"
            params.append(salesperson)

        rows = conn.execute(query, params).fetchall()
        
        # Group by customer
        customer_data = {}
        for row in rows:
            name = row['customer_name']
            s_date_str = row['sale_date'].split('T')[0]
            s_date = datetime.datetime.strptime(s_date_str, '%Y-%m-%d').date()
            price = row['total_price']
            
            if name not in customer_data:
                customer_data[name] = {
                    'last_purchase': s_date,
                    'orders': 0,
                    'total_spend': 0.0
                }
            
            customer_data[name]['orders'] += 1
            customer_data[name]['total_spend'] += price
            if s_date > customer_data[name]['last_purchase']:
                customer_data[name]['last_purchase'] = s_date

        results = []
        low_count = 0
        med_count = 0
        high_count = 0
        
        # Calculate scores
        for name, data in customer_data.items():
            last_date = data['last_purchase']
            recency_days = (ref_date - last_date).days
            orders = data['orders']
            ltv = round(data['total_spend'], 2)
            
            # Risk calculation: weight recency (70%) and frequency (30%)
            recency_score = min(100, (recency_days / 150.0) * 100)
            frequency_score = max(0, 100 - (orders * 12))
            risk_score = round(0.7 * recency_score + 0.3 * frequency_score, 1)
            
            if risk_score <= 30:
                risk_cat = "Low Risk"
                low_count += 1
                ai_reason = "Customer shows consistent purchasing behavior and active engagement."
                action = "Loyalty rewards"
            elif risk_score <= 70:
                risk_cat = "Medium Risk"
                med_count += 1
                ai_reason = "Activity has slowed down. Gap since last purchase exceeds historical average."
                action = "Recommend products"
            else:
                risk_cat = "High Risk"
                high_count += 1
                if ltv > 100000:
                    ai_reason = "High-value VIP shopper has been inactive for an extended period."
                    action = "Schedule follow-up"
                else:
                    ai_reason = "Prolonged inactivity and low buying frequency indicate imminent churn."
                    action = "Send discount coupon"
            
            results.append({
                'customer_name': name,
                'last_purchase_date': last_date.isoformat(),
                'total_orders': orders,
                'lifetime_value': ltv,
                'churn_risk_score': risk_score,
                'risk_category': risk_cat,
                'ai_reason': ai_reason,
                'recommended_action': action
            })

            # Save to prediction history
            store_churn_prediction(name, last_date.isoformat(), orders, ltv, risk_score, risk_cat, ai_reason, action)

        # Sort by risk score descending
        results = sorted(results, key=lambda x: x['churn_risk_score'], reverse=True)

        # Generate average LTV for chart
        low_ltv = np.mean([c['lifetime_value'] for c in results if c['risk_category'] == 'Low Risk']) if low_count > 0 else 0
        med_ltv = np.mean([c['lifetime_value'] for c in results if c['risk_category'] == 'Medium Risk']) if med_count > 0 else 0
        high_ltv = np.mean([c['lifetime_value'] for c in results if c['risk_category'] == 'High Risk']) if high_count > 0 else 0

        # Risk trend calculation by month of last purchase
        trend_buckets = {}
        for c in results:
            m = c['last_purchase_date'][:7]  # YYYY-MM
            if m not in trend_buckets:
                trend_buckets[m] = []
            trend_buckets[m].append(c['churn_risk_score'])
        
        sorted_months = sorted(trend_buckets.keys())
        trend_data = {
            'labels': sorted_months,
            'values': [round(np.mean(trend_buckets[m]), 1) for m in sorted_months]
        }

        return jsonify({
            'customers': results,
            'summary': {
                'total': len(results),
                'low_risk': low_count,
                'med_risk': med_count,
                'high_risk': high_count
            },
            'charts': {
                'pie': [low_count, med_count, high_count],
                'bar_ltv': [round(float(low_ltv), 2), round(float(med_ltv), 2), round(float(high_ltv), 2)],
                'trend': trend_data
            }
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()


@app.route('/api/analytics/weather-predict', methods=['GET'])
def get_weather_prediction():
    city = request.args.get('city', 'New York')
    
    # Try fetching from cache
    conn = get_db()
    cached = conn.execute("SELECT weather_data, timestamp FROM weather_cache WHERE city = ?", (city,)).fetchone()
    now_ts = int(time.time())
    
    weather_info = None
    # Cache duration: 30 minutes (1800 seconds)
    if cached and (now_ts - cached['timestamp'] < 1800):
        weather_info = json.loads(cached['weather_data'])
    else:
        # Fetch from OpenWeather if API Key exists, otherwise use realistic simulation
        if OPENWEATHER_API_KEY:
            try:
                url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
                res = requests.get(url, timeout=5)
                if res.status_code == 200:
                    data = res.json()
                    weather_info = {
                        'condition': data['weather'][0]['main'],
                        'temp': round(data['main']['temp'], 1),
                        'forecast': data['weather'][0]['description'].capitalize()
                    }
                    conn.execute("INSERT OR REPLACE INTO weather_cache (city, weather_data, timestamp) VALUES (?, ?, ?)",
                                 (city, json.dumps(weather_info), now_ts))
                    conn.commit()
            except Exception as e:
                logger.error(f"OpenWeather fetch error: {e}")
        
        if not weather_info:
            # Simulated weather engine based on region/month
            month = datetime.datetime.now().month
            simulated = {
                'New York': {'condition': 'Clear' if month in [6,7,8] else 'Clouds', 'temp': 24 if month in [6,7,8] else 8, 'forecast': 'Sunny' if month in [6,7,8] else 'Overcast'},
                'London': {'condition': 'Rain' if month in [10,11,12,1,2] else 'Clouds', 'temp': 12 if month in [5,6,7] else 6, 'forecast': 'Light rain' if month in [10,11,12] else 'Partly cloudy'},
                'Delhi': {'condition': 'Clear' if month in [4,5,6] else 'Clouds', 'temp': 38 if month in [4,5,6] else 18, 'forecast': 'Haze' if month in [4,5,6] else 'Cool breeze'},
                'Mumbai': {'condition': 'Rain' if month in [6,7,8,9] else 'Clear', 'temp': 28 if month in [6,7,8,9] else 31, 'forecast': 'Heavy monsoon' if month in [6,7,8,9] else 'Humid and sunny'},
                'Tokyo': {'condition': 'Clouds' if month in [6,7] else 'Clear', 'temp': 22 if month in [6,7,8] else 10, 'forecast': 'Cloudy' if month in [6,7] else 'Chilly sunny day'},
                'Sydney': {'condition': 'Clear' if month in [11,12,1,2] else 'Clouds', 'temp': 25 if month in [11,12,1,2] else 15, 'forecast': 'Bright and sunny' if month in [11,12,1,2] else 'Breezy'}
            }
            weather_info = simulated.get(city, {'condition': 'Clear', 'temp': 20, 'forecast': 'Clear sky'})
            conn.execute("INSERT OR REPLACE INTO weather_cache (city, weather_data, timestamp) VALUES (?, ?, ?)",
                         (city, json.dumps(weather_info), now_ts))
            conn.commit()
    conn.close()

    cond = weather_info['condition']
    temp = weather_info['temp']
    
    # Predict impact based on category rules
    impact = "Neutral (+0%)"
    recs = []
    insight = ""
    
    if cond == 'Rain':
        impact = "Positive (+18%) for Indoor entertainment & tech"
        recs = ["Laptop (MacBook Pro)", "Gaming Console (PS5)", "Nintendo Switch OLED"]
        insight = f"Rainy weather in {city} is expected to drive indoor activities. Laptop sales and gaming console demand may increase by up to 25%."
    elif cond == 'Clear' and temp > 30:
        impact = "Positive (+15%) for home appliances & portable gadgets"
        recs = ["4K Television (Samsung 50\")", "Wireless Earbuds (AirPods Pro)", "Tablet (iPad Air)"]
        insight = f"High temperatures ({temp}°C) in {city} will increase demand for home entertainment systems like 4K Televisions by 15%."
    elif temp < 15:
        impact = "Positive (+22%) for Smart Wearables"
        recs = ["Smartwatch (Apple Watch)", "Smartwatch (Garmin Fenix 7)", "Over-ear Headphones (Sony WH)"]
        insight = f"Cooler temperatures ({temp}°C) tend to boost activity tracking and audio accessory demand. Smartwatches expected to rise by 22%."
    else:
        impact = "Stable (+5%) across overall catalog"
        recs = ["Smartphone (iPhone 15)", "Mechanical Keyboard (Keychron K2)", "Wireless Mouse/Keyboard Combo"]
        insight = "Mild and comfortable weather conditions. Stable consumer electronics traffic predicted across all core categories."

    # Store history
    store_weather_prediction(city, cond, temp, impact, ", ".join(recs), insight)

    # Historical chart data
    chart_weather_sales = {
        'labels': ['Clear', 'Clouds', 'Rain', 'Snow'],
        'values': [124000, 98000, 142000, 78000]
    }
    chart_temp_revenue = {
        'temps': [5, 10, 15, 20, 25, 30, 35, 40],
        'revenues': [85000, 92000, 105000, 118000, 134000, 126000, 110000, 95000]
    }
    chart_seasonal_demand = {
        'seasons': ['Spring', 'Summer', 'Autumn', 'Winter'],
        'electronics': [42000, 58000, 39000, 68000],
        'wearables': [31000, 24000, 36000, 48000]
    }

    return jsonify({
        'city': city,
        'current_weather': cond,
        'temperature': temp,
        'forecast': weather_info['forecast'],
        'sales_impact': impact,
        'recommended_products': recs,
        'ai_insights': insight,
        'charts': {
            'weather_vs_sales': chart_weather_sales,
            'temp_vs_revenue': chart_temp_revenue,
            'seasonal_demand': chart_seasonal_demand
        }
    }), 200

#  INITIALIZE & RUN
# ═══════════════════════════════════════════════════════════════════════════════

init_db()

if __name__ == '__main__':
    print("Starting Sales Analytics Dashboard on port 5000...")
    app.run(debug=True, host='0.0.0.0', port=5000)
