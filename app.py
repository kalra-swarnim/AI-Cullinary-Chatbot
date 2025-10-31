from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
import requests
from PIL import Image
import io
import base64
from food_recognition import FoodRecognizer, get_recipe

# Load environment variables
load_dotenv()

app = Flask(__name__, static_folder='frontend', static_url_path='')
CORS(app)

# Initialize the food recognizer
food_recognizer = FoodRecognizer()

# Get API keys from .env file
VISION_API_KEY = os.getenv('VISION_API_KEY', 'your-vision-api-key')
SPOONACULAR_API_KEY = os.getenv('SPOONACULAR_API_KEY', '4566c1995f554220a6e5db74e85a883b')

@app.route('/api/identify', methods=['POST'])
def identify_food():
    if 'image' not in request.files and 'image' not in request.json:
        return jsonify({'error': 'No image provided'}), 400
    
    try:
        # Handle file upload or base64 image
        if 'image' in request.files:
            image_file = request.files['image']
            recognition_result = food_recognizer.recognize_food(image_file)
        else:
            # Handle base64 encoded image
            base64_image = request.json.get('image', '')
            recognition_result = food_recognizer.recognize_food(base64_image)
        
        if not recognition_result['success']:
            return jsonify({'error': recognition_result['error']}), 500
            
        food_name = recognition_result['food_name']
        
        # Get recipe information
        recipe_info = get_recipe(food_name)
        
        return jsonify({
            'success': True,
            'food': food_name,
            'confidence': recognition_result['confidence'],
            'recipe': recipe_info
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return app.send_static_file(path)
    return app.send_static_file('index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)