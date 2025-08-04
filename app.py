from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "your_secret_key"

def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE,
                    password TEXT)""")
    conn.commit()
    conn.close()

init_db()

plans = {
    "starter": {"name": "Starter Plan", "min_age": 18, "min_amount": 500, "rate": 5},
    "growth": {"name": "Growth Plan", "min_age": 21, "min_amount": 1000, "rate": 8},
    "retirement": {"name": "Retirement Plan", "min_age": 50, "min_amount": 2000, "rate": 10},
}

@app.route('/')
def home():
    if 'username' in session:
        return redirect(url_for('invest'))
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        try:
            conn = sqlite3.connect('database.db')
            c = conn.cursor()
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            conn.close()
            flash("Signup successful! Please login.")
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash("Username already exists.")
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=?", (username,))
        user = c.fetchone()
        conn.close()

        if user and check_password_hash(user[2], password):
            session['username'] = user[1]
            return redirect(url_for('invest'))
        else:
            flash("Invalid credentials.")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

@app.route('/invest', methods=['GET', 'POST'])
def invest():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        try:
            age = int(request.form['age'])
            amount = float(request.form['amount'])
            plan_key = request.form['plan']
            plan = plans.get(plan_key)

            if age < plan["min_age"]:
                return render_template("result.html", error=f"Minimum age for {plan['name']} is {plan['min_age']}.")

            if amount < plan["min_amount"]:
                return render_template("result.html", error=f"Minimum amount is R{plan['min_amount']}.")

            final_return = amount + (amount * plan["rate"] / 100)
            return render_template("result.html", plan=plan, amount=amount, final_return=final_return)
        except ValueError:
            return render_template("result.html", error="Enter valid numbers.")

    return render_template("invest.html", plans=plans)

if __name__ == "__main__":
    app.run(debug=True)