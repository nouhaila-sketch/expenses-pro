from flask import Flask, render_template, request, redirect, session, Response
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"

def get_db():
    return sqlite3.connect("expenses.db")

def init_db():
    db = get_db()
    db.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)")
    db.execute("""CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY,
        name TEXT,
        amount REAL,
        category TEXT
    )""")
    db.commit()

init_db()

@app.route('/')
def dashboard():
    if 'user' not in session:
        return redirect('/login')

    db = get_db()
    data = db.execute("SELECT * FROM expenses").fetchall()

    total = sum([r[2] for r in data])

    categories = {}
    for r in data:
        categories[r[3]] = categories.get(r[3], 0) + r[2]

    return render_template("dashboard.html", total=total, categories=categories)

@app.route('/add', methods=['GET','POST'])
def add():
    if request.method == 'POST':
        name = request.form['name']
        amount = request.form['amount']
        category = request.form['category']

        db = get_db()
        db.execute("INSERT INTO expenses (name,amount,category) VALUES (?,?,?)",(name,amount,category))
        db.commit()

        return redirect('/list')

    return render_template("add.html")

@app.route('/list')
def list_expenses():
    db = get_db()
    data = db.execute("SELECT * FROM expenses").fetchall()
    return render_template("list.html", expenses=data)

@app.route('/delete/<int:id>')
def delete(id):
    db = get_db()
    db.execute("DELETE FROM expenses WHERE id=?", (id,))
    db.commit()
    return redirect('/list')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        u = request.form['username']
        p = request.form['password']

        db = get_db()
        user = db.execute("SELECT * FROM users WHERE username=? AND password=?", (u,p)).fetchone()

        if user:
            session['user'] = u
            return redirect('/')

    return render_template("login.html")

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        u = request.form['username']
        p = request.form['password']

        db = get_db()
        db.execute("INSERT INTO users (username,password) VALUES (?,?)",(u,p))
        db.commit()

        return redirect('/login')

    return render_template("register.html")

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/export')
def export():
    db = get_db()
    data = db.execute("SELECT * FROM expenses").fetchall()

    def generate():
        yield "name,amount,category\n"
        for r in data:
            yield f"{r[1]},{r[2]},{r[3]}\n"

    return Response(generate(), mimetype='text/csv',
        headers={"Content-Disposition":"attachment;filename=data.csv"})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)