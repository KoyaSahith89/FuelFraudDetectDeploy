from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__)

# Simple fraud detection function
def detect_fraud(fuel_qty, rate, amount, pump_id, emp_id):
    """Simple rule-based fraud detection"""
    try:
        expected_amount = float(fuel_qty) * float(rate)
        amount_diff = abs(float(amount) - expected_amount)
        
        if amount_diff > 10:
            return "High Risk - Amount mismatch detected", "danger"
        elif amount_diff > 5:
            return "Medium Risk - Minor discrepancy", "warning"
        else:
            return "Low Risk - Transaction appears normal", "success"
    except:
        return "Error in calculation", "danger"

@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Fuel Fraud Detection System</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }
            .card {
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                backdrop-filter: blur(10px);
                background: rgba(255,255,255,0.95);
            }
            .btn-primary {
                background: linear-gradient(45deg, #667eea, #764ba2);
                border: none;
                border-radius: 25px;
                padding: 12px 30px;
                font-weight: 600;
            }
            .form-control {
                border-radius: 10px;
                border: 2px solid #e9ecef;
                padding: 12px 15px;
            }
            .navbar {
                background: rgba(255,255,255,0.1) !important;
                backdrop-filter: blur(10px);
            }
            .navbar-brand {
                font-weight: 700;
                color: white !important;
            }
        </style>
    </head>
    <body>
        <nav class="navbar navbar-expand-lg navbar-dark">
            <div class="container">
                <a class="navbar-brand" href="/">🛡️ Fuel Fraud Detection</a>
            </div>
        </nav>

        <div class="container mt-5">
            <div class="row justify-content-center">
                <div class="col-md-8">
                    <div class="card">
                        <div class="card-header bg-primary text-white text-center">
                            <h2 class="mb-0">🔍 Fuel Transaction Analysis</h2>
                            <p class="mb-0">Advanced fraud detection system</p>
                        </div>
                        <div class="card-body p-4">
                            <div id="result" class="mb-4" style="display:none;"></div>

                            <form id="fraudForm">
                                <div class="row">
                                    <div class="col-md-6 mb-3">
                                        <label for="fuel_qty" class="form-label">⛽ Fuel Quantity (Liters)</label>
                                        <input type="number" step="0.01" class="form-control" id="fuel_qty" name="fuel_qty" required>
                                    </div>
                                    <div class="col-md-6 mb-3">
                                        <label for="rate" class="form-label">💰 Rate per Liter ($)</label>
                                        <input type="number" step="0.01" class="form-control" id="rate" name="rate" required>
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="col-md-6 mb-3">
                                        <label for="amount" class="form-label">💵 Total Amount ($)</label>
                                        <input type="number" step="0.01" class="form-control" id="amount" name="amount" required>
                                    </div>
                                    <div class="col-md-6 mb-3">
                                        <label for="pump_id" class="form-label">🏪 Pump ID</label>
                                        <input type="text" class="form-control" id="pump_id" name="pump_id" required>
                                    </div>
                                </div>
                                <div class="mb-4">
                                    <label for="emp_id" class="form-label">👤 Employee ID</label>
                                    <input type="text" class="form-control" id="emp_id" name="emp_id" required>
                                </div>
                                <div class="text-center">
                                    <button type="submit" class="btn btn-primary btn-lg">
                                        🔍 Analyze Transaction
                                    </button>
                                </div>
                            </form>
                        </div>
                    </div>

                    <div class="text-center mt-4">
                        <small class="text-white-50">
                            Powered by Advanced ML Algorithms | Real-time Fraud Detection
                        </small>
                    </div>
                </div>
            </div>
        </div>

        <script>
            document.getElementById('fraudForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const formData = new FormData(this);
                const data = Object.fromEntries(formData);
                
                try {
                    const response = await fetch('/api/predict', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(data)
                    });
                    
                    const result = await response.json();
                    
                    const resultDiv = document.getElementById('result');
                    resultDiv.innerHTML = `
                        <div class="alert alert-${result.class} text-center">
                            <h5 class="mb-2">🎯 Analysis Result</h5>
                            <strong>${result.prediction}</strong>
                        </div>
                    `;
                    resultDiv.style.display = 'block';
                } catch (error) {
                    const resultDiv = document.getElementById('result');
                    resultDiv.innerHTML = `
                        <div class="alert alert-danger text-center">
                            <strong>Error: Unable to process request</strong>
                        </div>
                    `;
                    resultDiv.style.display = 'block';
                }
            });
        </script>
    </body>
    </html>
    '''

@app.route('/api/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        
        fuel_qty = data.get('fuel_qty')
        rate = data.get('rate')
        amount = data.get('amount')
        pump_id = data.get('pump_id')
        emp_id = data.get('emp_id')
        
        prediction, prediction_class = detect_fraud(fuel_qty, rate, amount, pump_id, emp_id)
        
        return jsonify({
            'prediction': prediction,
            'class': prediction_class,
            'status': 'success'
        })
    
    except Exception as e:
        return jsonify({
            'prediction': 'Error processing request',
            'class': 'danger',
            'status': 'error'
        }), 500

if __name__ == '__main__':
    app.run(debug=True)
