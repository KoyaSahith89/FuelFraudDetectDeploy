import os
import logging
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
import joblib
import numpy as np

# Configure logging for debugging
logging.basicConfig(level=logging.DEBUG)


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///fuel_fraud.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize the app with the extension
db.init_app(app)

# Load enhanced fraud predictor
try:
    from enhanced_predictor import enhanced_predictor
    logging.info("Enhanced fraud detection model loaded successfully")
    model = enhanced_predictor
except Exception as e:
    logging.error(f"Error loading enhanced model: {str(e)}")
    # Fallback to basic model
    try:
        model = joblib.load("model/fraud_model.pkl")
        logging.info("Fallback to basic fraud detection model")
    except Exception as e2:
        logging.error(f"Error loading fallback model: {str(e2)}")
        model = None

# Initialize database tables
with app.app_context():
    # Import models to ensure tables are created
    import models
    db.create_all()
    logging.info("Database tables created successfully")

@app.route("/")
def home():
    """Render the main page with the fraud detection form"""
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    """Handle fraud prediction requests"""
    try:
        if model is None:
            return render_template("index.html", 
                                 prediction="Error: Model not loaded", 
                                 prediction_class="danger")
        
        # Get and validate form data
        fuel_qty = float(request.form["fuel_qty"])
        rate = float(request.form["rate"])
        amount = float(request.form["amount"])
        pump_id = int(request.form["pump_id"])
        emp_id = int(request.form["emp_id"])
        
        # Basic validation
        if fuel_qty <= 0 or rate <= 0 or amount <= 0:
            return render_template("index.html", 
                                 prediction="Error: Quantities and rates must be positive", 
                                 prediction_class="danger")
        
        if pump_id <= 0 or emp_id <= 0:
            return render_template("index.html", 
                                 prediction="Error: Pump ID and Employee ID must be positive integers", 
                                 prediction_class="danger")
        
        # Make prediction using enhanced predictor
        if hasattr(model, 'predict_fraud'):
            # Use enhanced predictor
            is_fraud, fraud_confidence, explanation = model.predict_fraud(
                fuel_qty, rate, amount, pump_id, emp_id
            )
            fraud_score = fraud_confidence
            
            if is_fraud:
                prediction = f"🚨 Fraud Detected"
                prediction_class = "danger"
                prediction_details = explanation
            else:
                prediction = f"✅ Transaction Normal"
                prediction_class = "success"
                prediction_details = explanation
        else:
            # Fallback to basic model
            data = np.array([[fuel_qty, rate, amount, pump_id, emp_id]])
            result = model.predict(data)[0]
            fraud_score = float(model.decision_function(data)[0])
            
            is_fraud = result == -1
            if is_fraud:
                prediction = "🚨 Fraud Detected"
                prediction_class = "danger"
                prediction_details = "Basic fraud detection analysis"
            else:
                prediction = "✅ Transaction Normal"
                prediction_class = "success"
                prediction_details = "Basic fraud detection analysis"
        
        # Save transaction to database
        from models import Transaction, FraudAlert, PumpMetrics
        
        transaction = Transaction(
            fuel_quantity=fuel_qty,
            rate_per_liter=rate,
            total_amount=amount,
            pump_id=pump_id,
            employee_id=emp_id,
            is_fraud=is_fraud,
            fraud_score=fraud_score
        )
        
        db.session.add(transaction)
        db.session.commit()
        
        # Create fraud alert if needed
        if is_fraud:
            alert = FraudAlert(
                transaction_id=transaction.id,
                alert_level='HIGH',
                alert_message=f'Suspicious transaction detected: {fuel_qty}L @ ${rate}/L = ${amount} (Pump {pump_id}, Employee {emp_id})'
            )
            db.session.add(alert)
            db.session.commit()
        
        # Update pump metrics
        pump_metrics = PumpMetrics.query.filter_by(pump_id=pump_id).first()
        if not pump_metrics:
            pump_metrics = PumpMetrics(pump_id=pump_id)
            db.session.add(pump_metrics)
        
        pump_metrics.update_metrics()
        db.session.commit()
        
        logging.info(f"Prediction made: {prediction} for transaction: {fuel_qty}L @ ${rate}/L = ${amount}, saved as transaction ID: {transaction.id}")
        
        return render_template("index.html", 
                             prediction=prediction, 
                             prediction_class=prediction_class,
                             prediction_details=prediction_details,
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

# Import dashboard routes
import dashboard

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
