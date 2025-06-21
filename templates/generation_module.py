
import torch
import re
from transformers import GPT2Tokenizer, GPT2LMHeadModel

model_path = r"D:\yamuna\practise_file\fine_tuned_recipe_gpt2"
tokenizer = GPT2Tokenizer.from_pretrained(model_path)
model = GPT2LMHeadModel.from_pretrained(model_path)

tokenizer.pad_token = tokenizer.eos_token
model.config.pad_token_id = tokenizer.eos_token_id
model.eval()

def scale_ingredients(ingredients, original_servings, desired_servings):
    scaled_ingredients = []
    scale_factor = float(desired_servings) / float(original_servings)
    pattern = re.compile(r'(\d*\.?\d+)([^\d]*)')

    for item in ingredients:
        match = pattern.match(item.strip())
        if match:
            quantity = float(match.group(1))
            unit_and_name = match.group(2).strip()
            scaled_quantity = round(quantity * scale_factor, 2)
            scaled_ingredients.append(f"{scaled_quantity} {unit_and_name}")
        else:
            scaled_ingredients.append(item)

    return scaled_ingredients

def generate_recipe(dish_name, servings, max_length=300):
    prompt = f"""Title: {dish_name}
Servings: {servings}
Ingredients:"""

    inputs = tokenizer(prompt, return_tensors="pt", padding=True, truncation=True, max_length=512)

    with torch.no_grad():
        output = model.generate(
            inputs["input_ids"],
            attention_mask=inputs["attention_mask"],
            max_length=max_length,
            num_return_sequences=1,
            temperature=0.6,
            top_k=40,
            top_p=0.85,
            repetition_penalty=1.7,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id
        )

    result = tokenizer.decode(output[0], skip_special_tokens=True)

    try:
        ingredients_section = re.search(r"Ingredients:(.*?)Instructions:", result, re.DOTALL).group(1).strip()
        instructions_section = re.search(r"Instructions:(.*)", result, re.DOTALL).group(1).strip()
    except AttributeError:
        ingredients_section = ""
        instructions_section = result

    ingredients = [line.strip('- ').strip() for line in ingredients_section.split('\n') if line.strip()]
    scaled_ingredients = scale_ingredients(ingredients, original_servings=2, desired_servings=servings)  # Assuming original is 2

    return {
        "ingredients": scaled_ingredients,
        "instructions": instructions_section.split('\n'),
        "grocery_list": scaled_ingredients
    }
