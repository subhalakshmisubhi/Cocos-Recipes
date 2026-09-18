from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    conn = get_db_connection()
    search = request.args.get('search', '')
    if search:
        recipes = conn.execute('SELECT * FROM recipes WHERE title LIKE ? OR ingredients LIKE ?', 
                             ('%' + search + '%', '%' + search + '%')).fetchall()
    else:
        recipes = conn.execute('SELECT * FROM recipes').fetchall()
    conn.close()
    return render_template('index.html', recipes=recipes, search=search)

@app.route('/add', methods=('GET', 'POST'))
def add_recipe():
    if request.method == 'POST':
        title = request.form['title']
        category = request.form['category']
        prep_steps = request.form['prep_steps']
        cooking_time = request.form['cooking_time']
        calories = request.form['calories']
        ingredients = request.form['ingredients']

        conn = get_db_connection()
        conn.execute('INSERT INTO recipes (title, category, prep_steps, cooking_time, calories, ingredients) VALUES (?, ?, ?, ?, ?, ?)',
                     (title, category, prep_steps, cooking_time, calories, ingredients))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('add_recipe.html')

if __name__ == '__main__':
    # Auto-initialize database table if it doesn't exist
    conn = get_db_connection()
    conn.execute('''CREATE TABLE IF NOT EXISTS recipes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    category TEXT NOT NULL,
                    prep_steps TEXT NOT NULL,
                    cooking_time TEXT NOT NULL,
                    calories INTEGER,
                    ingredients TEXT NOT NULL)''')
    conn.commit()
    conn.close()
    app.run(debug=True)

