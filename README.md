# AI Culinary Chatbot

This project is an AI-powered culinary assistant that can identify food from images and provide ingredients and preparation methods.

## Features

- Upload food images for identification
- Get detailed ingredients list
- Receive step-by-step cooking instructions
- Simple and intuitive user interface

## Setup Instructions

### Backend Setup

1. Install Python dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Create a `.env` file with your API keys:
   ```
   VISION_API_KEY=your-vision-api-key
   RECIPE_API_KEY=your-recipe-api-key
   ```

3. Run the Flask server:
   ```
   python app.py
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```
   cd frontend
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Start the development server:
   ```
   npm start
   ```

## Usage

1. Open the application in your browser
2. Upload a food image or take a photo
3. View the identified food, ingredients, and cooking instructions

## Technologies Used

- Backend: Flask (Python)
- Frontend: React
- Image Recognition: AI Vision API
- Recipe Data: Recipe API