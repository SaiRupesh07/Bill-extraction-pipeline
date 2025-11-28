import requests
import json

def test_live_api():
    base_url = "https://bill-extraction-pipeline.onrender.com"
    
    print("🚀 Testing LIVE Deployed API")
    print("=" * 50)
    
    # Test health endpoint
    print("1. Testing health endpoint...")
    health_response = requests.get(f"{base_url}/health")
    print(f"   Status: {health_response.status_code}")
    print(f"   Response: {health_response.json()}")
    
    # Test main extraction endpoint
    print("\n2. Testing bill extraction endpoint...")
    test_data = {
        "document": "https://hackrx.blob.core.windows.net/assets/datathon-IIT/simple_2.png"
    }
    
    api_response = requests.post(
        f"{base_url}/extract-bill-data",
        json=test_data,
        timeout=30
    )
    
    print(f"   Status: {api_response.status_code}")
    result = api_response.json()
    
    if result["is_success"]:
        data = result["data"]
        print(f"   ✅ SUCCESS: True")
        print(f"   📦 Items Extracted: {data['total_item_count']}")
        print(f"   💰 Reconciled Amount: ${data['reconciled_amount']:.2f}")
        print(f"   📄 Pages: {len(data['pagewise_line_items'])}")
        
        # Show extracted items
        for page in data['pagewise_line_items']:
            print(f"\n   Page {page['page_no']} Items:")
            for i, item in enumerate(page['bill_items'], 1):
                print(f"     {i}. {item['item_name']} - ${item['item_amount']:.2f}")
    else:
        print(f"   ❌ Error: {result.get('error')}")
    
    print("\n" + "=" * 50)
    print("🎉 YOUR HACKATHON SUBMISSION IS READY!")

if __name__ == "__main__":
    test_live_api()