import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from config import load_config
from services.lms_client import LMSClient

async def test():
    config = load_config()
    client = LMSClient(config.lms_api_base_url, config.lms_api_key)
    
    print("Getting pass rates for lab-04...")
    data = await client.get_pass_rates("lab-04")
    
    print("\nData type:", type(data))
    print("\nKeys:", data.keys() if isinstance(data, dict) else "Is list")
    
    if isinstance(data, dict):
        tasks = data.get('tasks', [])
        print(f"\nNumber of tasks: {len(tasks)}")
        if tasks:
            print("\nFirst task fields:")
            for key, value in tasks[0].items():
                print(f"  {key}: {value}")
    elif isinstance(data, list):
        print(f"\nNumber of items: {len(data)}")
        if data:
            print("\nFirst item fields:")
            for key, value in data[0].items():
                print(f"  {key}: {value}")

asyncio.run(test())
