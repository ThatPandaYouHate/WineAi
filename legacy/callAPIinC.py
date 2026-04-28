import subprocess
import json
import requests

def get_non_agent_stores():
    # Run the SSH command and capture output
    # cmd = ["ssh", "musen", "systembolaget-api/build/systembolaget", "stores"]

    try:
        with open('assortments/stores.json', 'r', encoding='utf-8') as f:
            stores = json.load(f)
        
        
        # Filter stores where isAgent is False
        non_agent_stores = [store for store in stores if store.get("isAgent") == False]
        
        # Return the filtered stores instead of printing them
        return non_agent_stores

    except FileNotFoundError:
        print("stores.json not found")
        return []
    except json.JSONDecodeError:
        print("Error decoding stores.json")
        return []

def read_assortment(site_ids):
    if isinstance(site_ids, str):
        site_ids = [site_ids]  # Convert single siteId to list
    
    all_products = []  # Use list instead of set
    formatted_wines = []  # List to store formatted wine information
    
    for site_id in site_ids:
        try:
            with open(f'assortments/{site_id}.json', 'r', encoding='utf-8') as f:
                products = json.load(f)
            # Add new products if they're not already in the list
            for product in products:
                if product not in all_products:
                    all_products.append(product)
                    
        except subprocess.CalledProcessError as e:
            print(f"Command failed for store {site_id}:", e)
        except json.JSONDecodeError as e:
            print(f"Failed to decode JSON for store {site_id}:", e)
    return all_products
    

def filter_assortment(site_ids, filters=None):
    # Default filter values
    default_filters = {
        "Vintage": [0, 100000],
        "Price": [0, 100000],
        "Volume": [0, 100000]
    }

    # Update default filters with any provided filters
    if filters is None:
        filters = {}
    filters = {**default_filters, **filters}

    # Get all products
    products = read_assortment(site_ids)
    formatted_wines = []

    for product in products:
        # Create wine info dictionary
        wine_info = {
            "Vintage": product.get("vintage", ""),
            "ProducerNameBold": product.get("productNameBold", ""),
            "ProducerNameThin": product.get("productNameThin", ""),
            "ProducerName": product.get("producerName", ""),                        
            "OriginLevel1": product.get("originLevel1", ""),
            "Country": product.get("country", ""),
            "CategoryLevel2": product.get("categoryLevel2", ""),
            "ProductNumberShort": product.get("productNumberShort", ""),
            "Price": product.get("price", ""),
            "Volume": product.get("volume", ""),
            "ProductLaunchDate": product.get("productLaunchDate", "")
        }

        # Check if wine matches all filters
        matches_filters = True
        for key, value in filters.items():
            if isinstance(value, list):
                if all(isinstance(x, (int, float)) for x in value) and len(value) == 2:
                    # Handle numeric range filters
                    try:
                        product_value = float(wine_info[key])
                        if not (value[0] <= product_value <= value[1]):
                            matches_filters = False
                            break
                    except (ValueError, TypeError):
                        matches_filters = False
                        break
                else:
                    # Handle list of possible values
                    if wine_info[key] not in value:
                        matches_filters = False
                        break
            elif isinstance(value, str):
                # Handle single string value
                if wine_info[key] != value:
                    matches_filters = False
                    break

        if matches_filters and wine_info not in formatted_wines:
            formatted_wines.append(wine_info)

    return formatted_wines

def promtAI(filtered_wines, user_prompt):
    prompt = f"""Given the following list of wines and user request, select exactly 3 wines that best match the request.
Only output the wine names in this format:
1. [ProducerNameBold] [ProducerNameThin] ([Vintage])
2. [ProducerNameBold] [ProducerNameThin] ([Vintage])
3. [ProducerNameBold] [ProducerNameThin] ([Vintage])

Available wines: {json.dumps(filtered_wines, indent=2)}
User request: {user_prompt}

Output only the 3 wines, nothing else."""

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "mistral",
            "prompt": prompt
        }
    )

    # Collect the full response
    full_response = ""
    for line in response.iter_lines():
        if line:
            json_response = json.loads(line)
            if 'response' in json_response:
                full_response += json_response['response']

    try:
        # Try to parse the response as JSON
        return json.loads(full_response)
    except json.JSONDecodeError:
        # If the response isn't valid JSON, return it as is
        print(full_response)
        return full_response

def print_wines(wines):
    print(f"\nFound {len(wines)} wines:")
    print("-" * 50)
    for wine in wines:
        print(f"""
Name: {wine['ProducerNameBold']} {wine['ProducerNameThin']}
Vintage: {wine['Vintage']}
Country: {wine['Country']} - {wine['OriginLevel1']}
Category: {wine['CategoryLevel2']}
Price: {wine['Price']} kr
Volume: {wine['Volume']} ml
Product Number: {wine['ProductNumberShort']}
Launch Date: {wine['ProductLaunchDate']}
""")
        print("-" * 50)

# Example usage:
store_ids = ["0106"]  # Add the store IDs you want to check
result = filter_assortment(store_ids, {"Country": ["Tyskland", "Italien"]})
print_wines(result)
awnser = promtAI(result, "i am making a pasta bolognese what wines do you recommend")
print(awnser)
#print(get_non_agent_stores())