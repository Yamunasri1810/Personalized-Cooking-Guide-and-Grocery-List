# Personalized-Cooking-Guide-and-Grocery-Store

Personalized Cooking Guide and Grocry Store is a smart, AI-powered web application that allows users to generate personalized recipes and grocery lists by simply entering a dish name and preferred number of servings. The application leverages Natural Language Processing (NLP) and a fine-tuned GPT-2 model to produce dynamic cooking instructions and scaled ingredient lists. It bridges the gap between traditional recipe sources and the real-world usability of scalable, interactive cooking.

🔍 Problem Statement
Traditional online recipes often lack clarity on portion control or serving sizes. Manually adjusting ingredient quantities can lead to leftover food or insufficient ingredients — especially for inexperienced cooks. Additionally, generating a grocery list manually from a recipe can be tedious.

✅ Solution Overview
KitchenIQ solves this by:

Dynamically generating ingredients and instructions based on servings input.

Automatically creating a grocery list from recipe components.

Providing a simple, intuitive web interface for interaction.

Allowing users to log in and store their activity history.

🚀 Features
🔐 User Authentication: Register and log in to save your recipe history.

🍲 Recipe Generation: Fine-tuned GPT-2 model generates recipe instructions and ingredients.

📏 Serving-based Ingredient Scaling: Ingredient quantities auto-adjust based on the number of servings.

🛍️ Grocery List Generation: Instantly create a shopping list based on the recipe.

🌐 Web Interface: User-friendly frontend built with HTML, CSS, and Flask.

💾 Database Integration: MongoDB stores user data and search history.

🧠 How It Works
Input: User enters a dish name and number of servings.

Model Invocation: The input is passed to the GPT-2 model (via OpenRouter API), which generates:

Ingredients (with quantity)

Cooking instructions

Grocery list

Ingredient Scaling: Quantities are scaled dynamically using an adjustment algorithm.

Output: All information is displayed on a clean web page and can be saved to the user’s profile.

⚙️ Tech Stack
Area	                                        Tools/Technologies
Programming Language	                        Python
NLP Framework	                                Hugging Face Transformers
ML Model	                                    GPT-2 (Fine-tuned on RecipeNLG Dataset)
Backend	                                      Flask
Frontend	                                    HTML, CSS, Jinja
Database	                                    MongoDB
Deployment	                                  OpenRouter API (Model serving), Localhost for testing
Libraries	                                     Pandas, Torch, Requests, Regex, Flask Sessions

