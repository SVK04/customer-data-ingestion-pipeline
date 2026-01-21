from flask import Flask, jsonify, request
import json
import os
from logger import get_logger

logger = get_logger("mock-server")

app = Flask(__name__)

DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "customers.json")

def load_customers():
    """Load customer data from JSON file."""
    logger.debug(f"Attempting to load data from {DATA_PATH}")
    try:
        if not os.path.exists(DATA_PATH):
            logger.error(f"Data file not found at {DATA_PATH}")
            return []
        with open(DATA_PATH, "r") as f:
            data = json.load(f)
            logger.info(f"Successfully loaded {len(data)} customers from JSON")
            return data
    except Exception as e:
        logger.exception(f"Unexpected error loading customer data: {e}")
        return []

customers_list = load_customers()

@app.route("/api/health", methods=["GET"])
def health():
    """Health check endpoint."""
    logger.info("Health check endpoint hit")
    return jsonify({"status": "healthy"}), 200

@app.route("/api/customers", methods=["GET"])
def get_customers():
    """Get paginated list of customers."""
    page = request.args.get("page", default=1, type=int)
    limit = request.args.get("limit", default=10, type=int)
    
    logger.debug(f"Fetching customers: page={page}, limit={limit}")
    
    start = (page - 1) * limit
    end = start + limit
    
    paginated_data = customers_list[start:end]
    
    return jsonify({
        "data": paginated_data,
        "total": len(customers_list),
        "page": page,
        "limit": limit
    }), 200

@app.route("/api/customers/<string:customer_id>", methods=["GET"])
def get_customer_by_id(customer_id):
    """Get a single customer by their ID."""
    logger.debug(f"Fetching customer by ID: {customer_id}")
    customer = next((c for c in customers_list if c.get("customer_id") == customer_id), None)
    
    if customer:
        logger.info(f"Customer {customer_id} found")
        return jsonify(customer), 200
    
    logger.warning(f"Customer {customer_id} not found")
    return jsonify({"error": "Customer not found"}), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
