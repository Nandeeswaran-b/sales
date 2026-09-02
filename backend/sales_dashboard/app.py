from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
import psycopg
from psycopg.rows import dict_row
import os

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests from the frontend

# Database configuration — reads from environment variables (set these in Render dashboard)
# On Render, set DATABASE_URL (e.g. postgres://user:pass@host/dbname)
DATABASE_URL = os.environ.get(
    'DATABASE_URL',
    'postgresql://{user}:{password}@{host}/{dbname}'.format(
        user=os.environ.get('DB_USER', 'postgres'),
        password=os.environ.get('DB_PASSWORD', 'root'),
        host=os.environ.get('DB_HOST', 'localhost'),
        dbname=os.environ.get('DB_NAME', 'sales_db'),
    )
)

def get_db_connection():
    conn = psycopg.connect(DATABASE_URL)
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/sales', methods=['GET'])
def get_sales():
    conn = get_db_connection()
    cursor = conn.cursor(row_factory=dict_row)
    query = """
    SELECT s.id, p.name as product_name, p.category,
           c.name as customer_name, c.mobile_no,
           s.quantity, TO_CHAR(s.sale_date, 'YYYY-MM-DD') as sale_date, s.total_price,
           s.mode_of_payment
    FROM sales s
    JOIN products p ON s.product_id = p.id
    JOIN customers c ON s.customer_id = c.id
    ORDER BY s.sale_date DESC
    """
    cursor.execute(query)
    sales = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(sales)

@app.route('/api/summary', methods=['GET'])
def get_summary():
    conn = get_db_connection()
    cursor = conn.cursor(row_factory=dict_row)

    # Monthly Revenue
    cursor.execute("""
        SELECT SUM(total_price) as total_revenue FROM sales
        WHERE EXTRACT(MONTH FROM sale_date) = EXTRACT(MONTH FROM CURRENT_DATE)
          AND EXTRACT(YEAR  FROM sale_date) = EXTRACT(YEAR  FROM CURRENT_DATE)
    """)
    rev_row = cursor.fetchone()
    total_revenue = rev_row['total_revenue'] if rev_row['total_revenue'] else 0

    # Total Orders
    cursor.execute("SELECT COUNT(id) as total_orders FROM sales")
    total_orders = cursor.fetchone()['total_orders']

    # Top Product
    query_top_product = """
    SELECT p.name, SUM(s.quantity) as total_sold
    FROM sales s
    JOIN products p ON s.product_id = p.id
    GROUP BY p.name
    ORDER BY total_sold DESC
    LIMIT 1
    """
    cursor.execute(query_top_product)
    top_product_row = cursor.fetchone()
    top_product = top_product_row['name'] if top_product_row else 'None'

    cursor.close()
    conn.close()

    return jsonify({
        'total_revenue': float(total_revenue),
        'total_orders': total_orders,
        'top_product': top_product
    })

@app.route('/api/chart/monthly', methods=['GET'])
def get_monthly_chart():
    conn = get_db_connection()
    cursor = conn.cursor(row_factory=dict_row)
    query = """
    SELECT TO_CHAR(sale_date, 'YYYY-MM') as month, SUM(total_price) as revenue
    FROM sales
    GROUP BY month
    ORDER BY month ASC
    """
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify([dict(row) for row in results])

@app.route('/api/chart/category', methods=['GET'])
def get_category_chart():
    conn = get_db_connection()
    cursor = conn.cursor(row_factory=dict_row)
    query = """
    SELECT p.category, SUM(s.total_price) as revenue
    FROM sales s
    JOIN products p ON s.product_id = p.id
    GROUP BY p.category
    """
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify([dict(row) for row in results])

@app.route('/api/chart/customers', methods=['GET'])
def get_customers_chart():
    conn = get_db_connection()
    cursor = conn.cursor(row_factory=dict_row)
    query = """
    SELECT c.name, SUM(s.total_price) as revenue
    FROM sales s
    JOIN customers c ON s.customer_id = c.id
    GROUP BY c.name
    ORDER BY revenue DESC
    LIMIT 5
    """
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify([dict(row) for row in results])

@app.route('/api/chart/country', methods=['GET'])
def get_country_chart():
    conn = get_db_connection()
    cursor = conn.cursor(row_factory=dict_row)
    query = """
    SELECT c.country, SUM(s.total_price) as revenue
    FROM sales s
    JOIN customers c ON s.customer_id = c.id
    GROUP BY c.country
    ORDER BY revenue DESC
    """
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify([dict(row) for row in results])

@app.route('/api/sales/new', methods=['POST'])
def add_new_sale():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO customers (name, mobile_no) VALUES (%s, %s) RETURNING id",
            (data['customer_name'], data.get('mobile_no', ''))
        )
        customer_id = cursor.fetchone()[0]

        cursor.execute(
            "INSERT INTO products (name, category, price) VALUES (%s, %s, %s) RETURNING id",
            (data['product_name'], 'Custom', data['total_price'])
        )
        product_id = cursor.fetchone()[0]

        cursor.execute(
            "INSERT INTO sales (product_id, customer_id, quantity, sale_date, total_price, mode_of_payment) VALUES (%s, %s, %s, %s, %s, %s)",
            (product_id, customer_id, 1, data['sale_date'], data['total_price'], data.get('mode_of_payment', 'Cash'))
        )
        conn.commit()
        return jsonify({'status': 'success', 'message': 'Data saved successfully'}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
