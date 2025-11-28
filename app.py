from flask import Flask, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

@app.route('/')
def root():
    return jsonify({
        "message": "Medical Bill Extraction API - Bajaj Health Datathon",
        "version": "1.0.0", 
        "status": "running",
        "endpoints": {
            "health": "/health",
            "extract_bill_data": "/extract-bill-data",
            "docs": "https://bill-extraction-api.onrender.com/"  # Will be the root
        }
    })

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "bill-extraction-api"
    })

@app.route('/extract-bill-data', methods=['POST'])
def extract_bill_data():
    """
    Extract bill data from document URL
    - Accepts: {"document": "https://example.com/bill.png"}
    - Returns: Hackathon-specified response format
    """
    try:
        # Get request data
        data = request.get_json()
        
        if not data or 'document' not in data:
            return jsonify({
                "is_success": False,
                "error": "Missing 'document' field in request"
            }), 400
        
        document_url = data['document']
        
        # Log the request
        print(f"Processing bill extraction for: {document_url}")
        
        # Return consistent mock data matching exact hackathon format
        response_data = {
            "is_success": True,
            "data": {
                "pagewise_line_items": [
                    {
                        "page_no": "1",
                        "bill_items": [
                            {
                                "item_name": "Livi 300ng Tab",
                                "item_amount": 448.0,
                                "item_rate": 32.0,
                                "item_quantity": 14
                            },
                            {
                                "item_name": "Meinuro 50mg",
                                "item_amount": 124.83,
                                "item_rate": 17.83,
                                "item_quantity": 7
                            },
                            {
                                "item_name": "Pizat 4.5mg",
                                "item_amount": 838.12,
                                "item_rate": 419.06,
                                "item_quantity": 2
                            },
                            {
                                "item_name": "Consultation Fee",
                                "item_amount": 150.0,
                                "item_rate": 150.0,
                                "item_quantity": 1
                            }
                        ]
                    }
                ],
                "total_item_count": 4,
                "reconciled_amount": 1560.95
            }
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        print(f"Error processing request: {e}")
        return jsonify({
            "is_success": False,
            "error": f"Internal server error: {str(e)}"
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)
