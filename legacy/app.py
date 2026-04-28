from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from callAPIinC import filter_assortment, promtAI, get_non_agent_stores

app = Flask(__name__)
CORS(app)

# Store IDs to use for wine recommendations
STORE_IDS = ["0106"]  # Add more store IDs as needed

@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

@app.route('/get-stores')
def get_stores():
    try:
        # Get stores using your existing function
        stores = get_non_agent_stores()
        return jsonify(stores), 200, {'Content-Type': 'application/json; charset=utf-8'}
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/ask', methods=['POST'])
def ask():
    try:
        data = request.json
        user_prompt = data.get('prompt')
        store_ids = data.get('storeIds', [])
        countries = data.get('countries', [])
        price_range = data.get('priceRange', {'min': 0, 'max': 5000})
        volume_range = data.get('volumeRange', {'min': 0, 'max': 1500})
        
        if not store_ids:
            return jsonify({'error': 'At least one store ID is required'}), 400
        
        # Create filters dictionary
        filters = {
            "Price": [price_range['min'], price_range['max']],
            "Volume": [volume_range['min'], volume_range['max']]
        }
        if countries:
            filters["Country"] = countries
        
        # Get filtered wines
        filtered_wines = filter_assortment(store_ids, filters)
        
        # Get AI response
        response = promtAI(filtered_wines, user_prompt)
        
        return jsonify({'response': response})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0') 