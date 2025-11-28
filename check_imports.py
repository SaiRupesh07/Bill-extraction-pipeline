import sys
import importlib

# List of required packages
required_packages = [
    'uvicorn',
    'fastapi',
    'python_dotenv',
    'requests',
    'PIL',
    'numpy',
    'pydantic',
    'cv2',
    'azure',
    'boto3'
]

print("🔍 Checking all required packages...")
print("=" * 50)

all_imports_ok = True

for package in required_packages:
    try:
        if package == 'PIL':
            import PIL
            version = PIL.__version__
        elif package == 'cv2':
            import cv2
            version = cv2.__version__
        else:
            module = importlib.import_module(package)
            version = getattr(module, '__version__', 'Unknown')
        
        print(f"✅ {package:20} - Version: {version}")
        
    except ImportError as e:
        print(f"❌ {package:20} - MISSING: {e}")
        all_imports_ok = False

print("=" * 50)

if all_imports_ok:
    print("🎉 All packages imported successfully!")
else:
    print("⚠️ Some packages are missing. Let's install them...")

# Test our custom modules
print("\n🔧 Testing custom module imports...")
try:
    from config.settings import settings
    print("✅ config.settings - OK")
except ImportError as e:
    print(f"❌ config.settings - FAILED: {e}")

try:
    from src.preprocessing.document_processor import DocumentProcessor
    print("✅ DocumentProcessor - OK")
except ImportError as e:
    print(f"❌ DocumentProcessor - FAILED: {e}")

try:
    from src.extraction.mock_extractor import MockExtractor
    print("✅ MockExtractor - OK")
except ImportError as e:
    print(f"❌ MockExtractor - FAILED: {e}")

try:
    from src.reconciliation.validator import ReconciliationEngine
    print("✅ ReconciliationEngine - OK")
except ImportError as e:
    print(f"❌ ReconciliationEngine - FAILED: {e}")

try:
    from src.extraction.pipeline import BillExtractionPipeline
    print("✅ BillExtractionPipeline - OK")
except ImportError as e:
    print(f"❌ BillExtractionPipeline - FAILED: {e}")

try:
    from src.api.main import app
    print("✅ FastAPI app - OK")
except ImportError as e:
    print(f"❌ FastAPI app - FAILED: {e}")