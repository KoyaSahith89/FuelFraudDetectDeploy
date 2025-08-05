import os
import logging
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
import tempfile

# Configure logging for debugging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

# Configure the database for Vercel (use temporary SQLite)
db_path = os.path.join(tempfile.gettempdir(), "fuel_fraud.db")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize the app with the extension
db.init_app(app)

# Simple fraud detection model
def simple_fraud_detector(fuel_qty, rate, amount, pump_id, emp_id):
    """Simple rule-based fraud detection"""
    expected_amount = fuel_qty * rate
    amount_diff = abs(amount - expected_amount)
    
    if amount_diff > 10:
        return "High Risk - Amount mismatch detected", "danger"
    elif amount_diff > 5:
        return "Medium Risk - Minor discrepancy", "warning"
    else:
        return "Low Risk - Transaction appears normal", "success"

# Database Models
class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fuel_qty = db.Column(db.Float, nullable=False)
    rate = db.Column(db.Float, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    pump_id = db.Column(db.String(50), nullable=False)
    emp_id = db.Column(db.String(50), nullable=False)
    prediction = db.Column(db.String(200))
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())

# Initialize database tables
with app.app_context():
    db.create_all()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    try:
        fuel_qty = float(request.form["fuel_qty"])
        rate = float(request.form["rate"])
        amount = float(request.form["amount"])
        pump_id = request.form["pump_id"]
        emp_id = request.form["emp_id"]
        
        # Make prediction
        prediction, prediction_class = simple_fraud_detector(fuel_qty, rate, amount, pump_id, emp_id)
        
        # Save to database
        transaction = Transaction(
            fuel_qty=fuel_qty,
            rate=rate,
            amount=amount,
            pump_id=pump_id,
            emp_id=emp_id,
            prediction=prediction
        )
        db.session.add(transaction)
        db.session.commit()
        
        logging.info(f"Prediction made: {prediction} for transaction ID: {transaction.id}")
        
        return render_template("index.html", 
                             prediction=prediction, 
                             prediction_class=prediction_class,
                             transaction_id=transaction.id,
                             form_data={
                                 'fuel_qty': fuel_qty,
                                 'rate': rate,
                                 'amount': amount,
                                 'pump_id': pump_id,
                                 'emp_id': emp_id
                             })
    
    except ValueError as e:
        return render_template("index.html", 
                             prediction="Error: Please enter valid numeric values", 
                             prediction_class="danger")
    except Exception as e:
        logging.error(f"Prediction error: {str(e)}")
        return render_template("index.html", 
                             prediction=f"Error: {str(e)}", 
                             prediction_class="danger")

@app.route("/dashboard")
def dashboard():
    try:
        transactions = Transaction.query.order_by(Transaction.timestamp.desc()).limit(10).all()
        return render_template("dashboard.html", transactions=transactions)
    except Exception as e:
        logging.error(f"Dashboard error: {str(e)}")
        return render_template("dashboard.html", transactions=[])

# Vercel handler
def handler(request):
    return app(request.environ, lambda status, headers: None)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
