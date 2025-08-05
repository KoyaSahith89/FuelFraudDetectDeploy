import joblib
import numpy as np
import pandas as pd
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class EnhancedFraudPredictor:
    """Enhanced fraud prediction with feature engineering and improved accuracy"""
    
    def __init__(self):
        self.model = None
        self.scaler = None
        self.feature_columns = None
        self.training_stats = None
        self.load_model()
    
    def load_model(self):
        """Load the trained model and preprocessing components"""
        try:
            self.model = joblib.load('model/fraud_model.pkl')
            self.scaler = joblib.load('model/scaler.pkl')
            self.feature_columns = joblib.load('model/feature_columns.pkl')
            self.training_stats = joblib.load('model/training_stats.pkl')
            logger.info("Enhanced fraud detection model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading enhanced model: {e}")
            # Fallback to basic model if enhanced model is not available
            try:
                self.model = joblib.load('model/fraud_model.pkl')
                logger.info("Fallback to basic model")
            except:
                logger.error("No model available")
                self.model = None
    
    def create_features(self, fuel_quantity, rate_per_liter, total_amount, pump_id, employee_id):
        """Create enhanced features from input data"""
        
        # Get current time for time-based features
        now = datetime.now()
        hour_of_day = now.hour
        day_of_week = now.weekday() + 1  # Monday = 1
        
        # Calculate expected amount
        expected_amount = fuel_quantity * rate_per_liter
        
        # Amount deviation (key fraud indicator)
        amount_deviation = abs(total_amount - expected_amount) / expected_amount if expected_amount > 0 else 0
        
        # Rate deviation from normal range
        normal_rate_min, normal_rate_max = 1.20, 2.00
        if rate_per_liter < normal_rate_min or rate_per_liter > normal_rate_max:
            rate_deviation = abs(rate_per_liter - ((normal_rate_min + normal_rate_max) / 2)) / ((normal_rate_max - normal_rate_min) / 2)
        else:
            rate_deviation = 0
        
        # Quantity anomaly
        normal_qty_min, normal_qty_max = 10, 80
        quantity_anomaly = 1 if (fuel_quantity < normal_qty_min or fuel_quantity > normal_qty_max) else 0
        
        # Time-based features
        is_unusual_hour = 1 if (hour_of_day < 6 or hour_of_day > 22) else 0
        
        # Mock employee and pump transaction counts (in real system, get from database)
        emp_transaction_count = np.random.randint(50, 200)  # This would be from database
        pump_transaction_count = np.random.randint(100, 500)  # This would be from database
        
        # Create feature array in the same order as training
        features = [
            fuel_quantity, rate_per_liter, total_amount, pump_id, employee_id,
            hour_of_day, day_of_week, amount_deviation, rate_deviation,
            quantity_anomaly, is_unusual_hour, emp_transaction_count, pump_transaction_count
        ]
        
        return np.array(features).reshape(1, -1)
    
    def predict_fraud(self, fuel_quantity, rate_per_liter, total_amount, pump_id, employee_id):
        """Predict fraud with enhanced features and confidence scoring"""
        
        if self.model is None:
            return False, 0.0, "Model not available"
        
        try:
            # Create enhanced features
            if hasattr(self, 'feature_columns') and self.feature_columns is not None:
                # Use enhanced model
                features = self.create_features(fuel_quantity, rate_per_liter, total_amount, pump_id, employee_id)
                
                if self.scaler is not None:
                    features_scaled = self.scaler.transform(features)
                else:
                    features_scaled = features
                
                # Get prediction and anomaly score
                prediction = self.model.predict(features_scaled)[0]
                anomaly_score = self.model.decision_function(features_scaled)[0]
                
                is_fraud = prediction == -1
                confidence = abs(anomaly_score)
                
                # Generate explanation
                explanation = self._generate_explanation(
                    fuel_quantity, rate_per_liter, total_amount, 
                    features[0], is_fraud, confidence
                )
                
            else:
                # Use basic model
                features = np.array([[fuel_quantity, rate_per_liter, total_amount, pump_id, employee_id]])
                prediction = self.model.predict(features)[0]
                anomaly_score = self.model.decision_function(features)[0]
                
                is_fraud = prediction == -1
                confidence = abs(anomaly_score)
                explanation = "Basic fraud detection analysis"
            
            return is_fraud, float(confidence), explanation
            
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return False, 0.0, f"Prediction error: {str(e)}"
    
    def _generate_explanation(self, fuel_quantity, rate_per_liter, total_amount, features, is_fraud, confidence):
        """Generate human-readable explanation for the prediction"""
        
        expected_amount = fuel_quantity * rate_per_liter
        amount_difference = abs(total_amount - expected_amount)
        amount_deviation_pct = (amount_difference / expected_amount * 100) if expected_amount > 0 else 0
        
        explanations = []
        
        if is_fraud:
            explanations.append("⚠ FRAUD DETECTED:")
            
            # Check amount deviation
            if amount_deviation_pct > 20:
                if total_amount < expected_amount:
                    explanations.append(f"• Undercharged by ${amount_difference:.2f} ({amount_deviation_pct:.1f}%)")
                else:
                    explanations.append(f"• Overcharged by ${amount_difference:.2f} ({amount_deviation_pct:.1f}%)")
            
            # Check rate anomalies
            if rate_per_liter < 1.20:
                explanations.append(f"• Unusually low fuel rate: ${rate_per_liter:.2f}/L")
            elif rate_per_liter > 2.00:
                explanations.append(f"• Unusually high fuel rate: ${rate_per_liter:.2f}/L")
            
            # Check quantity anomalies
            if fuel_quantity < 10:
                explanations.append(f"• Suspiciously low fuel quantity: {fuel_quantity:.2f}L")
            elif fuel_quantity > 80:
                explanations.append(f"• Suspiciously high fuel quantity: {fuel_quantity:.2f}L")
            
            # Time-based analysis
            now = datetime.now()
            if now.hour < 6 or now.hour > 22:
                explanations.append("• Transaction during unusual hours")
            
        else:
            explanations.append("✓ NORMAL TRANSACTION:")
            explanations.append(f"• Amount matches expected: ${total_amount:.2f} ≈ ${expected_amount:.2f}")
            explanations.append(f"• Normal fuel rate: ${rate_per_liter:.2f}/L")
            explanations.append(f"• Reasonable quantity: {fuel_quantity:.2f}L")
        
        explanations.append(f"• Confidence: {confidence:.3f}")
        
        return " ".join(explanations)
    
    def get_model_info(self):
        """Get information about the loaded model"""
        if self.training_stats:
            return self.training_stats
        else:
            return {"status": "Basic model loaded", "enhanced_features": False}

# Global instance
enhanced_predictor = EnhancedFraudPredictor()