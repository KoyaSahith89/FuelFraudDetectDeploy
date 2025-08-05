from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Fuel Fraud Detection System</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body { 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                min-height: 100vh; 
            }
            .card { 
                border-radius: 15px; 
                box-shadow: 0 10px 30px rgba(0,0,0,0.2); 
            }
        </style>
    </head>
    <body>
        <div class="container mt-5">
            <div class="row justify-content-center">
                <div class="col-md-8">
                    <div class="card">
                        <div class="card-header bg-primary text-white text-center">
                            <h2>🛡️ Fuel Fraud Detection System</h2>
                            <p class="mb-0">Advanced fraud detection system</p>
                        </div>
                        <div class="card-body p-4">
                            <div id="result" style="display:none;"></div>
                            <form id="fraudForm">
                                <div class="row">
                                    <div class="col-md-6 mb-3">
                                        <label class="form-label">⛽ Fuel Quantity (Liters)</label>
                                        <input type="number" step="0.01" class="form-control" id="fuel_qty" required>
                                    </div>
                                    <div class="col-md-6 mb-3">
                                        <label class="form-label">💰 Rate per Liter ($)</label>
                                        <input type="number" step="0.01" class="form-control" id="rate" required>
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="col-md-6 mb-3">
                                        <label class="form-label">💵 Total Amount ($)</label>
                                        <input type="number" step="0.01" class="form-control" id="amount" required>
                                    </div>
                                    <div class="col-md-6 mb-3">
                                        <label class="form-label">🏪 Pump ID</label>
                                        <input type="text" class="form-control" id="pump_id" required>
                                    </div>
                                </div>
                                <div class="mb-4">
                                    <label class="form-label">👤 Employee ID</label>
                                    <input type="text" class="form-control" id="emp_id" required>
                                </div>
                                <div class="text-center">
                                    <button type="submit" class="btn btn-primary btn-lg">🔍 Analyze Transaction</button>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            document.getElementById('fraudForm').addEventListener('submit', function(e) {
                e.preventDefault();
                
                const fuel_qty = parseFloat(document.getElementById('fuel_qty').value);
                const rate = parseFloat(document.getElementById('rate').value);
                const amount = parseFloat(document.getElementById('amount').value);
                
                const expected = fuel_qty * rate;
                const diff = Math.abs(amount - expected);
                
                let prediction, alertClass;
                if (diff > 10) {
                    prediction = "High Risk - Amount mismatch detected";
                    alertClass = "danger";
                } else if (diff > 5) {
                    prediction = "Medium Risk - Minor discrepancy";
                    alertClass = "warning";
                } else {
                    prediction = "Low Risk - Transaction appears normal";
                    alertClass = "success";
                }
                
                document.getElementById('result').innerHTML = `
                    <div class="alert alert-${alertClass} text-center mb-4">
                        <h5>🎯 Analysis Result</h5>
                        <strong>${prediction}</strong>
                        <br><small>Expected: $${expected.toFixed(2)} | Actual: $${amount.toFixed(2)} | Difference: $${diff.toFixed(2)}</small>
                    </div>
                `;
                document.getElementById('result').style.display = 'block';
            });
        </script>
    </body>
    </html>
    '''

if __name__ == '__main__':
    app.run(debug=True)
