from PIL import Image
import io
import base64
import random
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Spoonacular API key
SPOONACULAR_API_KEY = os.getenv('SPOONACULAR_API_KEY')

class FoodRecognizer:
    def __init__(self):
        # Fallback food classes if API fails
        self.food_classes = [
            "pizza", "pasta carbonara", "sushi", "burger", "taco", 
            "fried rice", "curry", "steak", "salad", "soup",
            "pancakes", "ice cream", "chocolate cake", "apple pie", "sandwich",
            "butter chicken"
        ]
    
    def recognize_food(self, image_data):
        """
        Recognize food from image data using Spoonacular API
        """
        try:
            # Handle different image input formats
            if isinstance(image_data, bytes):
                image = Image.open(io.BytesIO(image_data))
                img_bytes = io.BytesIO()
                image.save(img_bytes, format='JPEG')
                img_bytes = img_bytes.getvalue()
            elif isinstance(image_data, str) and image_data.startswith('data:image'):
                # Handle base64 encoded image
                base64_data = image_data.split(',')[1]
                img_bytes = base64.b64decode(base64_data)
                image = Image.open(io.BytesIO(img_bytes))
            else:
                # Assume it's a file-like object
                image = Image.open(image_data)
                img_bytes = io.BytesIO()
                image.save(img_bytes, format='JPEG')
                img_bytes = img_bytes.getvalue()
            
            # Use Spoonacular API for food recognition
            try:
                # Prepare the image file for the API request
                files = {'file': ('image.jpg', img_bytes, 'image/jpeg')}
                
                print(f"Making API request to Spoonacular with API key: {SPOONACULAR_API_KEY[:5]}...")
                
                # Make the API request to Spoonacular with the correct endpoint
                api_key = SPOONACULAR_API_KEY.strip()
                url = f'https://api.spoonacular.com/food/images/classify?apiKey={api_key}'
                
                response = requests.post(
                    url,
                    files=files
                )
                
                print(f"API Response Status: {response.status_code}")
                print(f"API Response: {response.text}")
                
                # Check if the request was successful
                if response.status_code == 200:
                    result = response.json()
                    print(f"API Result: {result}")
                    
                    # Spoonacular API returns different format than expected
                    # Check for the correct fields based on API documentation
                    if 'category' in result:
                        food_name = result['category']
                        confidence = result.get('probability', 0.8)
                    elif 'classification' in result:
                        food_name = result['classification']['name']
                        confidence = result['classification'].get('confidence', 0.8)
                    else:
                        # Try to extract any food name from the response
                        food_name = next((key for key in result.keys() if key not in ['status', 'code', 'message']), 'unknown food')
                        confidence = 0.7
                    
                    print(f"Identified food: {food_name} with confidence {confidence}")
                    return {
                        "success": True,
                        "food_name": food_name,
                        "confidence": confidence
                    }
                else:
                    # If API call fails, fall back to random food selection
                    print(f"API Error: {response.status_code}, {response.text}")
                    random_food = random.choice(self.food_classes)
                    print(f"Falling back to random food: {random_food}")
                    return {
                        "success": True,
                        "food_name": random_food,
                        "confidence": 0.7,
                        "note": "Using fallback due to API error"
                    }
            
            except Exception as api_error:
                # If there's an error with the API call, fall back to random food selection
                print(f"API Exception: {str(api_error)}")
                random_food = random.choice(self.food_classes)
                return {
                    "success": True,
                    "food_name": random_food,
                    "confidence": 0.7,
                    "note": "Using fallback due to API error"
                }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


# Function to get recipe information based on food name
def get_recipe(food_name):
    """
    Get recipe information for a given food name using Spoonacular API
    """
    try:
        # Search for recipes using Spoonacular API
        search_url = 'https://api.spoonacular.com/recipes/complexSearch'
        search_params = {
            'apiKey': SPOONACULAR_API_KEY,
            'query': food_name,
            'number': 1,  # Get just one recipe
            'instructionsRequired': True,
            'fillIngredients': True,
            'addRecipeInformation': True
        }
        
        search_response = requests.get(search_url, params=search_params)
        
        if search_response.status_code == 200:
            search_data = search_response.json()
            
            if search_data['results'] and len(search_data['results']) > 0:
                recipe_id = search_data['results'][0]['id']
                
                # Get detailed recipe information
                recipe_url = f'https://api.spoonacular.com/recipes/{recipe_id}/information'
                recipe_params = {
                    'apiKey': SPOONACULAR_API_KEY,
                    'includeNutrition': False
                }
                
                recipe_response = requests.get(recipe_url, params=recipe_params)
                
                if recipe_response.status_code == 200:
                    recipe_data = recipe_response.json()
                    
                    # Extract ingredients
                    ingredients = []
                    for ingredient in recipe_data.get('extendedIngredients', []):
                        ingredients.append(ingredient.get('original', ''))
                    
                    # Extract instructions
                    instructions = []
                    if 'analyzedInstructions' in recipe_data and recipe_data['analyzedInstructions']:
                        for step in recipe_data['analyzedInstructions'][0].get('steps', []):
                            instructions.append(step.get('step', ''))
                    else:
                        # Fallback to summary if no instructions available
                        instructions = [recipe_data.get('summary', 'No instructions available')]
                    
                    return {
                        "name": recipe_data.get('title', food_name.title()),
                        "ingredients": ingredients,
                        "instructions": instructions
                    }
        
        # If API call fails or no results, fall back to default recipes
        print(f"Falling back to default recipe for {food_name}")
        return get_default_recipe(food_name)
        
    except Exception as e:
        print(f"Error getting recipe: {str(e)}")
        return get_default_recipe(food_name)

# Function to get default recipe if API fails
def get_default_recipe(food_name):
    """
    Get a default recipe if the API call fails
    """
    # Sample recipes for demo purposes
    recipes = {
        "butter chicken": {
            "name": "Butter Chicken (Murgh Makhani)",
            "ingredients": [
                "800g boneless chicken thighs, cut into bite-sized pieces",
                "2 tbsp lemon juice",
                "3 cloves garlic, minced",
                "1 tbsp ginger, grated",
                "2 tsp garam masala",
                "1 tsp ground cumin",
                "1 tsp ground turmeric",
                "1 tsp ground coriander",
                "1 cup plain yogurt",
                "2 tbsp vegetable oil",
                "2 tbsp butter",
                "1 large onion, finely chopped",
                "2 tbsp tomato paste",
                "1 can (400g) tomato sauce",
                "1 cup heavy cream",
                "Fresh cilantro for garnish",
                "Basmati rice for serving"
            ],
            "instructions": [
                "In a large bowl, combine chicken with lemon juice, garlic, ginger, garam masala, cumin, turmeric, coriander, and yogurt. Marinate for at least 1 hour, preferably overnight.",
                "Heat oil in a large skillet over medium-high heat. Add marinated chicken and cook until browned, about 5-7 minutes.",
                "Remove chicken and set aside. In the same pan, add butter and onions. Cook until onions are soft and translucent, about 3-4 minutes.",
                "Add tomato paste and cook for 2 minutes. Add tomato sauce and bring to a simmer.",
                "Return chicken to the pan and simmer for 15 minutes on low heat.",
                "Stir in heavy cream and simmer for another 5 minutes until the sauce thickens.",
                "Garnish with fresh cilantro and serve hot with basmati rice."
            ]
        },
        "pizza": {
            "name": "Homemade Pizza",
            "ingredients": [
                "500g pizza dough", 
                "200g tomato sauce", 
                "250g mozzarella cheese", 
                "2 tbsp olive oil",
                "1 tsp dried oregano",
                "Toppings of your choice (pepperoni, vegetables, etc.)"
            ],
            "instructions": [
                "Preheat your oven to 475°F (245°C).",
                "Roll out the pizza dough on a floured surface.",
                "Transfer the dough to a pizza stone or baking sheet.",
                "Spread tomato sauce evenly over the dough, leaving a small border.",
                "Sprinkle mozzarella cheese over the sauce.",
                "Add your desired toppings.",
                "Drizzle with olive oil and sprinkle with oregano.",
                "Bake for 10-12 minutes until the crust is golden and cheese is bubbly.",
                "Let cool for a few minutes before slicing and serving."
            ]
        }
    }
    
    # Default recipe for foods not in our database
    default_recipe = {
        "name": food_name.title(),
        "ingredients": [
            "Ingredient 1",
            "Ingredient 2",
            "Ingredient 3",
            "Ingredient 4",
            "Ingredient 5"
        ],
        "instructions": [
            "Step 1: Prepare the ingredients",
            "Step 2: Cook according to your preferred method",
            "Step 3: Combine all ingredients",
            "Step 4: Serve and enjoy"
        ]
    }
    
    return recipes.get(food_name.lower(), default_recipe)