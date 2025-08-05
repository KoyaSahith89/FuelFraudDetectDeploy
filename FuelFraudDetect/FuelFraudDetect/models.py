from app import db
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy


class Transaction(db.Model):
    """Model for storing fuel transaction data and fraud detection results"""
    
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    fuel_quantity = db.Column(db.Float, nullable=False)
    rate_per_liter = db.Column(db.Float, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    pump_id = db.Column(db.Integer, nullable=False)
    employee_id = db.Column(db.Integer, nullable=False)
    
    # Fraud detection results
    is_fraud = db.Column(db.Boolean, nullable=False, default=False)
    fraud_score = db.Column(db.Float, nullable=True)  # Raw model output score
    
    # Metadata
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Transaction {self.id}: {self.fuel_quantity}L @ {self.rate_per_liter}/L = {self.total_amount}>'


class FraudAlert(db.Model):
    """Model for storing fraud alerts for suspicious transactions"""
    
    __tablename__ = 'fraud_alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transactions.id'), nullable=False)
    alert_level = db.Column(db.String(20), nullable=False)  # 'HIGH', 'MEDIUM', 'LOW'
    alert_message = db.Column(db.Text, nullable=False)
    
    # Alert metadata
    reviewed = db.Column(db.Boolean, nullable=False, default=False)
    reviewed_by = db.Column(db.String(100), nullable=True)
    reviewed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationship
    transaction = db.relationship('Transaction', backref='fraud_alerts', lazy=True)
    
    def __repr__(self):
        return f'<FraudAlert {self.id}: {self.alert_level} for Transaction {self.transaction_id}>'


class PumpMetrics(db.Model):
    """Model for tracking pump-specific metrics and statistics"""
    
    __tablename__ = 'pump_metrics'
    
    id = db.Column(db.Integer, primary_key=True)
    pump_id = db.Column(db.Integer, nullable=False, unique=True)
    
    # Statistical data
    total_transactions = db.Column(db.Integer, nullable=False, default=0)
    fraud_count = db.Column(db.Integer, nullable=False, default=0)
    fraud_percentage = db.Column(db.Float, nullable=False, default=0.0)
    
    # Volume metrics
    total_fuel_dispensed = db.Column(db.Float, nullable=False, default=0.0)
    total_revenue = db.Column(db.Float, nullable=False, default=0.0)
    
    # Timestamps
    last_updated = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def update_metrics(self):
        """Update pump metrics based on current transaction data"""
        from sqlalchemy import func
        
        # Get transaction statistics for this pump
        stats = db.session.query(
            func.count(Transaction.id).label('total'),
            func.sum(Transaction.fuel_quantity).label('fuel'),
            func.sum(Transaction.total_amount).label('revenue'),
            func.sum(db.case((Transaction.is_fraud == True, 1), else_=0)).label('fraud')
        ).filter(Transaction.pump_id == self.pump_id).first()
        
        self.total_transactions = getattr(stats, 'total', 0) or 0
        self.total_fuel_dispensed = getattr(stats, 'fuel', 0.0) or 0.0
        self.total_revenue = getattr(stats, 'revenue', 0.0) or 0.0
        self.fraud_count = getattr(stats, 'fraud', 0) or 0
        
        # Calculate fraud percentage
        if self.total_transactions > 0:
            self.fraud_percentage = (self.fraud_count / self.total_transactions) * 100
        else:
            self.fraud_percentage = 0.0
            
        self.last_updated = datetime.utcnow()
    
    def __repr__(self):
        return f'<PumpMetrics Pump {self.pump_id}: {self.total_transactions} transactions, {self.fraud_percentage:.1f}% fraud>'