from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'super_secret_key_coco'  # Required for session management

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/login', methods=('GET', 'POST'))
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Hardcoded credentials check
        if username == 'admin' and password == 'coco123':
            session['user'] = username
            return redirect(url_for('index'))
        else:
            error = 'Invalid username or password!'
            
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/')
def index():
    if 'user' not in session:
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    search = request.args.get('search', '')
    if search:
        query = "SELECT * FROM recipes WHERE title LIKE ? OR ingredients LIKE ?"
        recipes = conn.execute(query, ('%' + search + '%', '%' + search + '%')).fetchall()
    else:
        recipes = conn.execute('SELECT * FROM recipes').fetchall()
    conn.close()
    return render_template('index.html', recipes=recipes, search=search)

@app.route('/add', methods=('GET', 'POST'))
def add_recipe():
    if 'user' not in session:
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        title = request.form['title']
        cooking_time = request.form['cooking_time']
        calories = request.form['calories']
        ingredients = request.form['ingredients']
        prep_steps = request.form['prep_steps']
        
        conn = get_db_connection()
        conn.execute('INSERT INTO recipes (title, cooking_time, calories, ingredients, prep_steps) VALUES (?, ?, ?, ?, ?)',
                     (title, cooking_time, calories, ingredients, prep_steps))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('add_recipe.html')

@app.route('/edit/<int:id>', methods=('GET', 'POST'))
def edit_recipe(id):
    if 'user' not in session:
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    recipe = conn.execute('SELECT * FROM recipes WHERE id = ?', (id,)).fetchone()
    
    if request.method == 'POST':
        title = request.form['title']
        cooking_time = request.form['cooking_time']
        calories = request.form['calories']
        ingredients = request.form['ingredients']
        prep_steps = request.form['prep_steps']
        
        conn.execute('UPDATE recipes SET title = ?, cooking_time = ?, calories = ?, ingredients = ?, prep_steps = ? WHERE id = ?',
                     (title, cooking_time, calories, ingredients, prep_steps, id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
        
    conn.close()
    return render_template('edit_recipe.html', recipe=recipe)

@app.route('/delete/<int:id>', methods=('POST',))
def delete_recipe(id):
    if 'user' not in session:
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    conn.execute('DELETE FROM recipes WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)

