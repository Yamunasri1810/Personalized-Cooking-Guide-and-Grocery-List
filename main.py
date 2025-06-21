from generation_module import generate_recipe
from flask import Flask, render_template, request, redirect, url_for, flash, session
import os
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

load_dotenv()

uri = os.environ.get('uri')
client = MongoClient(uri, server_api=ServerApi('1'))

try:
    client.admin.command('ping')
    print("Pinged your deployment. Successfully connected to MongoDB!")
except Exception as e:
    print(e)

db_name = "KITCHEN_IQ"
database = client[db_name]

registerDetails = database["user_details"]
userInputs = database["user_inputs"]

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')


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
    dish_names = request.form.getlist("dish_name")
    servings_list = request.form.getlist("servings")

    if not dish_names or not servings_list or len(dish_names) != len(servings_list):
        flash("Please provide valid dish names and servings.", "danger")
        return redirect('/')

    all_recipes = []

    for dish_name, servings in zip(dish_names, servings_list):
        if 'email' in session:
            userInputs.insert_one({
                "email": session['email'],
                "dish_name": dish_name,
                "servings": servings,
                'timestamp': datetime.now()
            })
        recipe = generate_recipe(dish_name, servings)
        recipe['dish_name'] = dish_name
        recipe['servings'] = servings
        ingredients = recipe.get("ingredients")
        if not isinstance(ingredients, list):
            ingredients = [ingredients]
        all_recipes.append(recipe)

    return render_template('multi_recipe.html', all_recipes=all_recipes)

@app.route('/grocery', methods=['POST'])
def grocery_list():
    grocery_items = request.form.getlist("grocery_items")
    return render_template('grocery.html', groceries=grocery_items)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
