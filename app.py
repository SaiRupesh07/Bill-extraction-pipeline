from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests
import threading
import time

app = Flask(__name__)
CORS(app)

def process_bill_async(document_url, webhook_url):
    """
    Process bill extraction asynchronously and send results to webhook
    """
    try:
        # Simulate processing time
        time.sleep(2)
        
        # Your bill processing logic here
        result = {
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
                            }
                        ]
                    }
                ],
                "total_item_count": 4,
                "reconciled_amount": 1560.95
            }
        }
        
        # Send results to webhook URL
        requests.post(webhook_url, json=result, timeout=10)
        
    except Exception as e:
        # Send error to webhook
        error_result = {
            "is_success": False,
            "error": f"Processing failed: {str(e)}"
        }
        requests.post(webhook_url, json=error_result, timeout=10)

@app.route('/extract-bill-data-webhook', methods=['POST'])
def extract_bill_data_webhook():
    """
    Asynchronous bill extraction with webhook support
    """
    try:
        data = request.get_json()
        
        if not data or 'document' not in data or 'webhook_url' not in data:
            return jsonify({
                "is_success": False,
                "error": "Missing 'document' or 'webhook_url' in request"
            }), 400
        
        document_url = data['document']
        webhook_url = data['webhook_url']
        
        # Start async processing
        thread = threading.Thread(
            target=process_bill_async,
            args=(document_url, webhook_url)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({
            "is_success": True,
            "message": "Bill processing started",
            "processing_id": f"proc_{int(time.time())}",
            "status": "processing"
        })
        
    except Exception as e:
        return jsonify({
            "is_success": False,
            "error": f"Failed to start processing: {str(e)}"
        }), 500

# ... (keep your existing routes)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)
