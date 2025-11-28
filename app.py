from flask import Flask, request, jsonify
from flask_cors import CORS
from src.extraction.optimized_pipeline import create_extraction_pipeline
import logging
import time
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize pipeline - use mock only if explicitly set in environment
use_mock = os.getenv('USE_MOCK', 'false').lower() == 'true'
pipeline = create_extraction_pipeline(use_mock=use_mock)

logger.info(f"Bill Extraction API initialized - Use Mock: {use_mock}")

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for deployment monitoring"""
    return jsonify({
        "status": "healthy",
        "service": "Bill Extraction API",
        "version": "1.0.0",
        "mock_mode": use_mock
    })

@app.route('/extract-bill-data', methods=['POST'])
def extract_bill_data():
    """
    Main endpoint for bill data extraction
    Implements all competition hints:
    - Hint #1: Two-step approach (OCR → Extraction)
    - Hint #2: Guard against interpretation errors
    - Hint #3: JSON structure compliance
    """
    start_time = time.time()
    
    try:
        # Validate request
        if not request.is_json:
            return jsonify({
                "is_success": False,
                "error": "Content-Type must be application/json"
            }), 400
        
        data = request.get_json()
        
        if not data:
            return jsonify({
                "is_success": False,
                "error": "Empty request body"
            }), 400
        
        if 'document' not in data:
            return jsonify({
                "is_success": False,
                "error": "Missing 'document' URL in request body"
            }), 400
        
        document_url = data['document']
        
        # Validate URL format
        if not document_url.startswith(('http://', 'https://')):
            return jsonify({
                "is_success": False,
                "error": "Invalid document URL format"
            }), 400
        
        logger.info(f"Processing document: {document_url[:100]}...")
        
        # Process document through optimized pipeline
        result = pipeline.process_document(document_url)
        
        # Log processing time
        processing_time = time.time() - start_time
        logger.info(f"Request completed in {processing_time:.2f}s - Success: {result['is_success']}")
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Endpoint error: {str(e)}", exc_info=True)
        
        # Return structured error response
        return jsonify({
            "is_success": False,
            "error": f"Internal server error: {str(e)}"
        }), 500

@app.route('/extract-bill-data', methods=['GET'])
def method_not_allowed():
    """Handle GET requests to POST endpoint"""
    return jsonify({
        "is_success": False,
        "error": "Method not allowed. Use POST method."
    }), 405

@app.route('/')
def home():
    """Root endpoint with API information"""
    return jsonify({
        "message": "Medical Bill Extraction API",
        "version": "1.0.0",
        "endpoints": {
            "POST /extract-bill-data": "Extract bill data from document URL",
            "GET /health": "Health check"
        },
        "competition_hints_implemented": [
            "Hint #1: Two-step approach (OCR → Extraction)",
            "Hint #2: Guard against interpretation errors", 
            "Hint #3: JSON structure compliance"
        ]
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "is_success": False,
        "error": "Endpoint not found"
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "is_success": False,
        "error": "Internal server error"
    }), 500

if __name__ == '__main__':
    # Get port from environment variable or default to 5000
    port = int(os.getenv('PORT', 5000))
    
    # Run app - use debug mode only in development
    debug_mode = os.getenv('DEBUG', 'false').lower() == 'true'
    
    logger.info(f"Starting Flask server on port {port} - Debug: {debug_mode}")
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
