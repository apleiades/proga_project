from flask import Flask, request, render_template
import pandas as pd
from pymystem3 import Mystem

df = pd.read_csv('recipes.csv')


def find_matching_dishes(df, new_ingr):
    appr_recipes = []
    for index, row in df.iterrows():
        ingredients = row['ingr']

        if pd.isna(ingredients):
            continue

        if all(ingredient in ingredients for ingredient in new_ingr):
            instructions = row['instructions']

            if isinstance(instructions, str):
                try:
                    instructions = eval(instructions)
                except:
                    pass

            if isinstance(instructions, list):
                instructions = ' '.join(instructions)

            appr_recipes.append({
                'id': index,
                'recipe_name': row['name'],
                'image': row['image'],
                'description': row['description'],
                'instructions': instructions,
                'ingredients': ', '.join(ingredients)
            })

    return appr_recipes


app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/search_recipes', methods=['GET'])
def search_recipes():
    return render_template('search_recipes.html')

@app.route('/search', methods=['POST'])
def search():
    m_stem = Mystem()
    ingredients = request.form.get('ingredients').strip().split(',')
    ingredients2 = ' '.join(ingredients)
    lemmas = set(m_stem.lemmatize(ingredients2))
    new_ingr = {lemma for lemma in lemmas if lemma.strip()}

    appr_recipes = find_matching_dishes(df, new_ingr)

    return render_template(
        'results.html',
        appr_recipes=appr_recipes,
        ingredients=', '.join(ingredients)
    )

@app.route('/recipe/<int:recipe_id>')
def recipe(recipe_id):
    recipe = df.iloc[recipe_id].to_dict()
    recipe['ingredients'] = ', '.join(eval(recipe['ingr']))
    recipe['instructions'] = ' '.join(eval(recipe['instructions']))
    return render_template('recipe.html', recipe=recipe)


@app.route('/add_recipe', methods=['GET', 'POST'])
def add_recipe():
    global df

    if request.method == 'POST':
        name = request.form.get('name')
        instructions = request.form.get('instructions')
        ingredients = request.form.get('ingredients')
        description = request.form.get('description', '')
        link = request.form.get('link', '')
        image = request.form.get('image', '')

        if name and instructions and ingredients:
            new_id = len(df) + 1
            new_recipe = pd.DataFrame({
                'id': [new_id],
                'link': [link],
                'name': [name],
                'ingr': [ingredients],
                'description': [description],
                'image': [image],
                'instructions': [str(instructions.split('. '))]
            })
            new_recipe.to_csv('recipes.csv', mode='a', header=False, index=False)

            df = pd.read_csv('recipes.csv')

    return render_template('add_recipe.html')


@app.route('/recipe_of_the_day')
def recipe_of_the_day():
    random_recipe = df.sample().to_dict(orient='records')[0]
    random_recipe['ingredients'] = ', '.join(eval(random_recipe['ingr']))
    random_recipe['instructions'] = ' '.join(eval(random_recipe['instructions']))
    return render_template('recipe_of_the_day.html', recipe=random_recipe)


if __name__ == '__main__':
    app.run(debug=True)
