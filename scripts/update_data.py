import subprocess
import json
import os

def get_non_agent_stores():
    # Run the SSH command and capture output
    cmd = ["ssh", "musen", "systembolaget-api/build/systembolaget", "stores"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        output = result.stdout

        # Parse JSON
        data = json.loads(output)
        
        # Filter out agent stores
        non_agent_stores = [store for store in data if not store.get('isAgent', True)]
        
        # Create assortments directory if it doesn't exist
        if not os.path.exists('assortments'):
            os.makedirs('assortments')
            
        # Save filtered data to JSON file
        with open('assortments/stores.json', 'w') as f:
            json.dump(non_agent_stores, f, indent=4)
            
    except subprocess.CalledProcessError as e:
        print("Command failed:", e)
    except json.JSONDecodeError as e:
        print("Failed to decode JSON:", e)
        
def read_assortment():
    try:
        with open('assortments/stores.json', 'r') as f:
            stores = json.load(f)
            site_ids = [store['siteId'] for store in stores]
    except FileNotFoundError:
        print("stores.json not found")
        return []
    except json.JSONDecodeError:
        print("Error decoding stores.json")
        return []

    for site_id in site_ids:
        print(site_id)
        cmd = ["ssh", "musen", "systembolaget-api/build/systembolaget", "assortment", 
               "--store", site_id, "--category", "Vin"]
        
        try:
            # Specify UTF-8 encoding for the subprocess
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', check=True)
            output = result.stdout
            
            if output is None:
                print(f"No output received for store {site_id}")
                continue
                
            # Parse JSON
            products = json.loads(output)
            print(f"Found {len(products)} products for store {site_id}")
            
            with open(f'assortments/{site_id}.json', 'w', encoding='utf-8') as f:
                json.dump(products, f, indent=4)
                
        except subprocess.CalledProcessError as e:
            print(f"Command failed for store {site_id}:", e)
        except json.JSONDecodeError as e:
            print(f"Failed to decode JSON for store {site_id}:", e)
        except UnicodeDecodeError as e:
            print(f"Unicode decode error for store {site_id}:", e)


get_non_agent_stores()
read_assortment()
