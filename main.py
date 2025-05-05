
import re
import json
import requests
from flask import Flask, render_template, request, redirect, url_for, flash, session
import os
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

mongo_uri = os.environ.get('MONGO_URI')
client = MongoClient(mongo_uri)

db_name = "KITCHEN_IQ"
database = client[db_name]

collection_name = "user_details"
registerDetails = database[collection_name]

# New collection to store recipe inputs
userInputs = database["user_inputs"]

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')

def recipe_generator(dish_name, servings):
    headers = {
        "Authorization": f"Bearer {'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'}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "deepseek/deepseek-r1-distill-llama-70b:free",
        "messages": [
            {
                "role": "user",
                "content" : f'''Give me a structured JSON output for the {dish_name} recipe 
for {servings} servings with these keys: ingredients, instructions, 
grocery_list. I want it in exactly this format:

{{
  "ingredients": {{
    "rice": "1/2 cup (raw, preferably ponni or any short-grain rice)",
    "split_moong_dal": "1/4 cup (split green gram)",
    "ghee_or_oil": "2 tablespoons",
    "green_chillies": "2-3, slit (green chilies)",
    "ginger": "1 small piece, grated",
    "cumin_seeds": "1 teaspoon",
    "mustard_seeds": "1/2 teaspoon",
    "hing": "a pinch (asafoetida)",
    "curry_leaves": "10-12 leaves",
    "salt": "to taste",
    "water": "1 1/4 cups",
    "turmeric_powder": "a pinch (optional, for color)",
    "coriander_leaves": "for garnish (optional)"
  }},
  "instructions": [
    "Wash the rice and split moong dal together. Drain the water and keep it aside.",
    "In a heavy pan or pressure cooker, heat 1 tablespoon of ghee or oil.",
    "Add cumin seeds, mustard seeds, and let them sputter. Add hing, slit green chilies, curry leaves, and sauté for a few seconds.",
    "Add the chopped onion, minced garlic, and grated ginger. Sauté until the onion becomes translucent.",
    "Add the washed rice and moong dal, and roast them for 2-3 minutes.",
    "Add 1 1/4 cups of water, a pinch of turmeric powder (optional), and salt to taste. Stir well.",
    "Bring to a boil. Reduce the flame to medium-low, cover with a tight-fitting lid, and let it simmer for 12-15 minutes until the rice and dal are fully cooked and mushy.",
    "Once cooked, stir in the remaining tablespoon of ghee.",
    "Garnish with coriander leaves and serve hot."
  ],
  "grocery_list": [
    "Rice", "Split moong dal", "Ghee or oil", "Onion", "Green chilies", "Garlic", 
    "Ginger", "Cumin seeds", "Mustard seeds", "Hing (asafoetida)", "Curry leaves", 
    "Salt", "Water", "Turmeric powder", "Coriander leaves"
  ]
}}'''
            }
        ]
    }

    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)

    if response.status_code == 401:
        print("Error: Unauthorized (401). Check if your API key is correct.")
        return {}

    result = response.json()
    recipe_content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
    json_match = re.search(r'```json\n(.*?)\n```', recipe_content, re.DOTALL)

    if json_match:
        recipe_content = json_match.group(1)

    try:
        recipe_data = json.loads(recipe_content)
    except json.JSONDecodeError:
        print("Error: Invalid JSON response")
        return {}

    return {
        "ingredients": recipe_data.get("ingredients", []),
        "instructions": recipe_data.get("instructions", []),
        "grocery_list": recipe_data.get("grocery_list", []),
        "preparation_time": recipe_data.get("preparation_time", "Unknown"),
        "cuisine": recipe_data.get("cuisine", "Unknown"),
        "course_type": recipe_data.get("course_type", "Unknown")
    }

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register_submit():
    if request.method == 'POST':
        email = request.form.get("user_email")
        password = request.form.get("user_password")
        confirm_password = request.form.get('conform_user_password')

        if password != confirm_password:
            flash('Password and confirm password do not match!', "danger")
            return redirect('/register')

        if registerDetails.find_one({'email': email}):
            flash('Email already taken!', "danger")
            return redirect('/register')

        registerDetails.insert_one({'email': email, 'password': password})
        flash('Registration successful! Please log in.', "success")
        return redirect("/login")

    return render_template('register.html')

@app.route('/login', methods=['POST', 'GET'])
def login_submit():
    if request.method == 'POST':
        email = request.form.get("user_email")
        password = request.form.get("user_password")
        user = registerDetails.find_one({'email': email, 'password': password})

        if user:
            session['email'] = email
            flash('Login successful!', "success")
            return redirect('/')
        else:
            flash('Username and password do not match!', "danger")
            return redirect('/login')

    return render_template('login.html')

@app.route('/recipe', methods=['POST'])
def generate_recipe():
    dish_name = request.form.get("dish_name")
    servings = request.form.get("servings")

    if not dish_name or not servings:
        flash("Please provide both dish name and servings.", "danger")
        return redirect('/')

    if 'email' in session:
        userInputs.insert_one({
            "email": session['email'],
            "dish_name": dish_name,
            "servings": servings,
            'timestamp': datetime.now()
        })

    recipe = recipe_generator(dish_name, servings)
    ingredients = recipe.get("ingredients")
    if not isinstance(ingredients, list):
        ingredients = [ingredients]

    return render_template('recipe.html', recipe=recipe, ingredients=ingredients, dish_name=dish_name, servings=servings)

@app.route('/grocery', methods=['POST'])
def grocery_list():
    grocery_items = request.form.getlist("grocery_items")
    return render_template('grocery.html', groceries=grocery_items)

if __name__ == "__main__":
    app.run(debug=True)