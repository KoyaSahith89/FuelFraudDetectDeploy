import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import joblib
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_realistic_fuel_data(n_samples=2000):
    """Generate realistic fuel transaction data for training"""
    np.random.seed(42)
    
    # Define realistic parameters for fuel transactions
    normal_data = []
    fraud_data = []
    
    # Generate normal transactions (80% of data)
    n_normal = int(n_samples * 0.8)
    for i in range(n_normal):
        # Normal fuel quantity: 10-80 liters
        fuel_qty = np.random.uniform(10, 80)
        
        # Normal rate: $1.20 - $2.00 per liter
        rate = np.random.uniform(1.20, 2.00)
        
        # Normal amount: fuel_qty * rate with small variance (±5%)
        amount = fuel_qty * rate * np.random.uniform(0.95, 1.05)
        
        # Pump IDs: 1-20
        pump_id = np.random.randint(1, 21)
        
        # Employee IDs: 100-300
        emp_id = np.random.randint(100, 301)
        
        # Additional features for better detection
        hour_of_day = np.random.randint(6, 22)  # Operating hours
        day_of_week = np.random.randint(1, 8)   # 1=Monday, 7=Sunday
        
        normal_data.append([fuel_qty, rate, amount, pump_id, emp_id, hour_of_day, day_of_week, 0])
    
    # Generate fraudulent transactions (20% of data)
    n_fraud = n_samples - n_normal
    for i in range(n_fraud):
        fraud_type = np.random.choice(['undercharge', 'overcharge', 'quantity_mismatch', 'rate_manipulation'])
        
        if fraud_type == 'undercharge':
            # Undercharging: amount significantly less than fuel_qty * rate
            fuel_qty = np.random.uniform(20, 80)
            rate = np.random.uniform(1.20, 2.00)
            amount = fuel_qty * rate * np.random.uniform(0.5, 0.8)  # 20-50% less
            
        elif fraud_type == 'overcharge':
            # Overcharging: amount significantly more than fuel_qty * rate
            fuel_qty = np.random.uniform(15, 60)
            rate = np.random.uniform(1.20, 2.00)
            amount = fuel_qty * rate * np.random.uniform(1.3, 2.0)  # 30-100% more
            
        elif fraud_type == 'quantity_mismatch':
            # Quantity manipulation: unrealistic fuel quantities
            fuel_qty = np.random.choice([
                np.random.uniform(1, 5),     # Suspiciously low
                np.random.uniform(100, 200)  # Suspiciously high
            ])
            rate = np.random.uniform(1.20, 2.00)
            amount = fuel_qty * rate * np.random.uniform(0.8, 1.2)
            
        elif fraud_type == 'rate_manipulation':
            # Rate manipulation: unusual rates
            fuel_qty = np.random.uniform(20, 60)
            rate = np.random.choice([
                np.random.uniform(0.5, 1.0),   # Suspiciously low rate
                np.random.uniform(3.0, 5.0)    # Suspiciously high rate
            ])
            amount = fuel_qty * rate * np.random.uniform(0.9, 1.1)
        
        pump_id = np.random.randint(1, 21)
        emp_id = np.random.randint(100, 301)
        
        # Fraudulent transactions often happen at unusual times
        hour_of_day = np.random.choice([
            np.random.randint(22, 24),  # Late night
            np.random.randint(0, 6),    # Early morning
            np.random.randint(6, 22)    # Normal hours (some fraud during normal times)
        ], p=[0.3, 0.3, 0.4])
        
        day_of_week = np.random.randint(1, 8)
        
        fraud_data.append([fuel_qty, rate, amount, pump_id, emp_id, hour_of_day, day_of_week, 1])
    
    # Combine normal and fraud data
    all_data = normal_data + fraud_data
    
    # Convert to DataFrame
    columns = ['fuel_quantity', 'rate_per_liter', 'total_amount', 'pump_id', 
               'employee_id', 'hour_of_day', 'day_of_week', 'is_fraud']
    df = pd.DataFrame(all_data, columns=columns)
    
    # Shuffle the data
    df = df.sample(frac=1).reset_index(drop=True)
    
    return df

def create_enhanced_features(df):
    """Create additional features for better fraud detection"""
    
    # Calculate expected amount
    df['expected_amount'] = df['fuel_quantity'] * df['rate_per_liter']
    
    # Amount deviation (key fraud indicator)
    df['amount_deviation'] = abs(df['total_amount'] - df['expected_amount']) / df['expected_amount']
    
    # Rate deviation from normal range
    normal_rate_min, normal_rate_max = 1.20, 2.00
    df['rate_deviation'] = np.where(
        (df['rate_per_liter'] < normal_rate_min) | (df['rate_per_liter'] > normal_rate_max),
        abs(df['rate_per_liter'] - ((normal_rate_min + normal_rate_max) / 2)) / ((normal_rate_max - normal_rate_min) / 2),
        0
    )
    
    # Quantity anomaly
    normal_qty_min, normal_qty_max = 10, 80
    df['quantity_anomaly'] = np.where(
        (df['fuel_quantity'] < normal_qty_min) | (df['fuel_quantity'] > normal_qty_max),
        1, 0
    )
    
    # Time-based features
    df['is_unusual_hour'] = np.where(
        (df['hour_of_day'] < 6) | (df['hour_of_day'] > 22), 1, 0
    )
    
    # Employee transaction frequency (simplified)
    emp_counts = df['employee_id'].value_counts()
    df['emp_transaction_count'] = df['employee_id'].map(emp_counts)
    
    # Pump transaction frequency
    pump_counts = df['pump_id'].value_counts()
    df['pump_transaction_count'] = df['pump_id'].map(pump_counts)
    
    return df

def train_advanced_fraud_model():
    """Train an advanced fraud detection model"""
    
    logger.info("Generating realistic training data...")
    df = generate_realistic_fuel_data(3000)
    
    logger.info("Creating enhanced features...")
    df = create_enhanced_features(df)
    
    # Select features for training
    feature_columns = [
        'fuel_quantity', 'rate_per_liter', 'total_amount', 'pump_id', 'employee_id',
        'hour_of_day', 'day_of_week', 'amount_deviation', 'rate_deviation',
        'quantity_anomaly', 'is_unusual_hour', 'emp_transaction_count', 'pump_transaction_count'
    ]
    
    X = df[feature_columns].values
    y = df['is_fraud'].values
    
    # Split data for validation
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train Isolation Forest model
    logger.info("Training Isolation Forest model...")
    
    # Use only normal transactions for training (unsupervised learning)
    X_normal = X_train_scaled[y_train == 0]
    
    # Train multiple models with different parameters and select the best
    best_model = None
    best_score = 0
    
    contamination_values = [0.1, 0.15, 0.2, 0.25]
    
    for contamination in contamination_values:
        model = IsolationForest(
            contamination=contamination,
            random_state=42,
            n_estimators=200,
            max_samples='auto',
            max_features=1.0,
            bootstrap=False
        )
        
        model.fit(X_normal)
        
        # Predict on test set
        y_pred = model.predict(X_test_scaled)
        y_pred_binary = (y_pred == -1).astype(int)  # Convert to binary
        
        # Calculate accuracy
        accuracy = np.mean(y_pred_binary == y_test)
        
        logger.info(f"Contamination {contamination}: Accuracy = {accuracy:.3f}")
        
        if accuracy > best_score:
            best_score = accuracy
            best_model = model
    
    logger.info(f"Best model accuracy: {best_score:.3f}")
    
    # Final evaluation
    y_pred_final = best_model.predict(X_test_scaled)
    y_pred_binary_final = (y_pred_final == -1).astype(int)
    
    logger.info("Classification Report:")
    print(classification_report(y_test, y_pred_binary_final, target_names=['Normal', 'Fraud']))
    
    logger.info("Confusion Matrix:")
    print(confusion_matrix(y_test, y_pred_binary_final))
    
    # Save the trained model and scaler
    logger.info("Saving trained model and scaler...")
    joblib.dump(best_model, 'model/fraud_model.pkl')
    joblib.dump(scaler, 'model/scaler.pkl')
    joblib.dump(feature_columns, 'model/feature_columns.pkl')
    
    # Save training statistics
    training_stats = {
        'total_samples': len(df),
        'fraud_samples': sum(df['is_fraud']),
        'normal_samples': len(df) - sum(df['is_fraud']),
        'test_accuracy': best_score,
        'feature_columns': feature_columns
    }
    
    joblib.dump(training_stats, 'model/training_stats.pkl')
    
    logger.info("Model training completed successfully!")
    logger.info(f"Training statistics: {training_stats}")
    
    return best_model, scaler, feature_columns, training_stats

if __name__ == "__main__":
    train_advanced_fraud_model()