from flask import render_template, jsonify, request
from app import app, db
from models import Transaction, FraudAlert, PumpMetrics
from sqlalchemy import func, desc
from datetime import datetime, timedelta


@app.route("/dashboard")
def dashboard():
    """Display fraud detection dashboard with statistics"""
    
    # Get recent statistics
    total_transactions = db.session.query(func.count(Transaction.id)).scalar() or 0
    fraud_count = db.session.query(func.count(Transaction.id)).filter(Transaction.is_fraud == True).scalar() or 0
    fraud_percentage = (fraud_count / total_transactions * 100) if total_transactions > 0 else 0
    
    # Get recent transactions
    recent_transactions = Transaction.query.order_by(desc(Transaction.created_at)).limit(10).all()
    
    # Get active fraud alerts
    active_alerts = FraudAlert.query.filter_by(reviewed=False).order_by(desc(FraudAlert.created_at)).limit(5).all()
    
    # Get pump statistics
    pump_stats = PumpMetrics.query.order_by(desc(PumpMetrics.fraud_percentage)).limit(5).all()
    
    # Get daily statistics for the last 7 days
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    daily_stats = db.session.query(
        func.date(Transaction.created_at).label('date'),
        func.count(Transaction.id).label('total'),
        func.sum(db.case((Transaction.is_fraud == True, 1), else_=0)).label('fraud')
    ).filter(Transaction.created_at >= seven_days_ago).group_by(
        func.date(Transaction.created_at)
    ).order_by('date').all()
    
    return render_template("dashboard.html",
                         total_transactions=total_transactions,
                         fraud_count=fraud_count,
                         fraud_percentage=fraud_percentage,
                         recent_transactions=recent_transactions,
                         active_alerts=active_alerts,
                         pump_stats=pump_stats,
                         daily_stats=daily_stats)


@app.route("/api/transactions")
def api_transactions():
    """API endpoint for transaction data"""
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    
    transactions = Transaction.query.order_by(desc(Transaction.created_at)).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'transactions': [{
            'id': t.id,
            'fuel_quantity': t.fuel_quantity,
            'rate_per_liter': t.rate_per_liter,
            'total_amount': t.total_amount,
            'pump_id': t.pump_id,
            'employee_id': t.employee_id,
            'is_fraud': t.is_fraud,
            'fraud_score': t.fraud_score,
            'created_at': t.created_at.isoformat()
        } for t in transactions.items],
        'pagination': {
            'page': transactions.page,
            'pages': transactions.pages,
            'per_page': transactions.per_page,
            'total': transactions.total
        }
    })


@app.route("/api/alerts/<int:alert_id>/review", methods=["POST"])
def review_alert(alert_id):
    """Mark a fraud alert as reviewed"""
    alert = FraudAlert.query.get_or_404(alert_id)
    alert.reviewed = True
    alert.reviewed_at = datetime.utcnow()
    alert.reviewed_by = "System User"  # In a real app, this would be the current user
    
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Alert marked as reviewed'})


@app.route("/model-info")
def model_info():
    """Display model performance and information"""
    from enhanced_predictor import enhanced_predictor
    
    model_info = enhanced_predictor.get_model_info()
    model_training_date = "July 27, 2025"  # In production, get from model metadata
    
    return render_template("model_info.html", 
                         model_info=model_info,
                         model_training_date=model_training_date)


@app.route("/api/retrain-model", methods=["POST"])
def retrain_model():
    """API endpoint to retrain the fraud detection model"""
    try:
        # In production, this would be a background task
        import subprocess
        result = subprocess.run(['python', 'train_model.py'], 
                              capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            return jsonify({
                'success': True, 
                'message': 'Model retrained successfully',
                'output': result.stdout
            })
        else:
            return jsonify({
                'success': False, 
                'message': 'Model retraining failed',
                'error': result.stderr
            })
    except Exception as e:
        return jsonify({
            'success': False, 
            'message': f'Error retraining model: {str(e)}'
        })


@app.route("/test-model")
def test_model():
    """Run model performance tests"""
    try:
        import subprocess
        result = subprocess.run(['python', 'test_enhanced_model.py'], 
                              capture_output=True, text=True, timeout=60)
        
        test_output = result.stdout if result.returncode == 0 else result.stderr
        
        return render_template("test_results.html", 
                             test_output=test_output,
                             success=result.returncode == 0)
    except Exception as e:
        return render_template("test_results.html", 
                             test_output=f"Error running tests: {str(e)}",
                             success=False)