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
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
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

        records.append((
            sale_date.isoformat(),
            product_name,
            category,
            customer_name,
            mobile_no,
            payment,
            total_price
        ))

    conn.executemany('''
        INSERT INTO sales (sale_date, product_name, category, customer_name, mobile_no, mode_of_payment, total_price)
        VALUES (?, ?, ?, ?, ?, ?, ?)
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
#  INITIALIZE & RUN
# ═══════════════════════════════════════════════════════════════════════════════

init_db()

if __name__ == '__main__':
    print("Starting Sales Analytics Dashboard on port 5000...")
    app.run(debug=True, host='0.0.0.0', port=5000)
