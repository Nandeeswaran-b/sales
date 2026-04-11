from flask import Blueprint, jsonify, request
import psycopg2
from psycopg2.extras import RealDictCursor
import os

api_blueprint = Blueprint('api', __name__)

# Reads your Supabase Connection String from the Render Environment Variables
# Key should be an environment variable named DATABASE_URL
_raw_db_url = os.environ.get('DATABASE_URL', "postgresql://postgres:[YOUR_PASSWORD]@db.[YOUR_PROJECT_ID].supabase.co:5432/postgres")
# Supabase pooler requires SSL - append if not already present
DB_CONNECTION_STRING = _raw_db_url if 'sslmode' in _raw_db_url else _raw_db_url + '?sslmode=require'

def get_db_connection():
    try:
        conn = psycopg2.connect(DB_CONNECTION_STRING, cursor_factory=RealDictCursor)
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

@api_blueprint.route('/sales/cumulative', methods=['GET'])
def get_cumulative_revenue():
    """Calculates running total revenue over time."""
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Could not connect to database"}), 500
    
    try:
        cur = conn.cursor()
        query = """
            SELECT 
                order_date,
                SUM(order_amount) OVER (ORDER BY order_date) as cumulative_revenue
            FROM public.orders
            ORDER BY order_date ASC
        """
        cur.execute(query)
        results = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_blueprint.route('/sales/growth-rate', methods=['GET'])
def get_growth_rate():
    """Calculates month-over-month growth percentage."""
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Could not connect to database"}), 500
    
    try:
        cur = conn.cursor()
        query = """
            WITH monthly_sales AS (
                SELECT 
                    DATE_TRUNC('month', order_date) as month,
                    SUM(order_amount) as total_revenue
                FROM public.orders
                GROUP BY 1
                ORDER BY 1
            )
            SELECT 
                month,
                total_revenue,
                LAG(total_revenue) OVER (ORDER BY month) as prev_month_revenue,
                CASE 
                    WHEN LAG(total_revenue) OVER (ORDER BY month) IS NULL THEN 0
                    ELSE ROUND(((total_revenue - LAG(total_revenue) OVER (ORDER BY month)) / LAG(total_revenue) OVER (ORDER BY month) * 100)::numeric, 2)
                END as growth_rate
            FROM monthly_sales
        """
        cur.execute(query)
        results = cur.fetchall()
        
        # Convert datetime objects to string for JSON serialization
        for row in results:
            row['month'] = row['month'].strftime('%Y-%m')
            
        cur.close()
        conn.close()
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_blueprint.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200
