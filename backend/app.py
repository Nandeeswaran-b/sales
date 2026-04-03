from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from simulation import SimulationManager
import logging

app = Flask(__name__)
CORS(app) # Enable CORS for all routes

# Initialize Simulation
sim_manager = SimulationManager()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/')
def index():
    """Serve the main page."""
    return render_template('index.html')

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get all shelves current status without triggering a new scan."""
    logger.info("API Request: GET /api/status")
    return jsonify(sim_manager.get_state())

@app.route('/api/scan', methods=['POST'])
def trigger_scan():
    """Trigger the 'robot' to scan again, potentially updating shelf statuses."""
    logger.info("API Request: POST /api/scan")
    updated_state = sim_manager.perform_scan()
    return jsonify(updated_state)

@app.route('/api/env', methods=['POST'])
def set_environment():
    """Switch environment (Supermarket, Museum, Library)."""
    data = request.json
    env_name = data.get('environment', 'Supermarket')
    logger.info(f"API Request: POST /api/env - Switching to {env_name}")
    
    sim_manager.initialize_environment(env_name)
    return jsonify({"message": f"Environment switched to {env_name}", "data": sim_manager.get_state()})

if __name__ == '__main__':
    print("Starting Smart Shelf Backend on port 5000...")
    app.run(debug=True, host='0.0.0.0', port=5000)
