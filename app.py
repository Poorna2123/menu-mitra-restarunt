from flask import Flask, render_template, request, redirect, url_for, session
from config import users_collection, orders_collection

app = Flask(__name__)
app.secret_key = "your_secret_key"

# ======================
# Menu items with images
# ======================
veg_items = [
    {"name": "Paneer Butter Masala", "price": 200, "image": "images/paneer.jpg"},
    {"name": "Veg Biryani", "price": 150, "image": "images/vegbiryani.jpg"},
    {"name": "Dal Tadka", "price": 120, "image": "images/daltadka.jpeg"}
]

non_veg_items = [
    {"name": "Chicken Curry", "price": 250, "image": "images/chciken.jpg"},
    {"name": "Mutton Biryani", "price": 300, "image": "images/mutton.jpeg"},
    {"name": "Fish Fry", "price": 220, "image": "images/fish.jpg"}
]

# ======================
# Routes
# ======================

@app.route('/')
def index():
    return redirect(url_for('signup'))


# ---------- USER SIGNUP ----------
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if users_collection.find_one({'username': username}):
            return "Username already exists!"

        users_collection.insert_one({'username': username, 'password': password})
        return redirect(url_for('login'))

    return render_template('signup.html')


# ---------- USER LOGIN ----------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = users_collection.find_one({'username': username, 'password': password})
        if user:
            session['username'] = username
            return redirect(url_for('home'))
        else:
            return "Invalid credentials!"

    return render_template('login.html')


# ---------- HOME PAGE ----------
@app.route('/home')
def home():
    if "username" not in session:
        return redirect(url_for('login'))

    return render_template('home.html',
                           veg_items=veg_items,
                           non_veg_items=non_veg_items)


# ---------- ORDER PAGE ----------
@app.route('/order', methods=['POST', 'GET'])
def order():
    if "username" not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        selected_items = request.form.getlist('item')
        quantities = request.form.getlist('quantity')

        table_no = request.form['table_no']
        num_people = request.form['num_people']

        order_items = []
        total_amount = 0

        for i in range(len(selected_items)):
            name = selected_items[i]
            qty = int(quantities[i])

            if qty <= 0:
                continue

            price = next((item['price'] for item in (veg_items + non_veg_items)
                          if item['name'] == name), 0)

            total = price * qty
            total_amount += total

            order_items.append({
                "item": name,
                "quantity": qty,
                "price": price,
                "total": total
            })

        order_data = {
            "username": session['username'],
            "table_no": table_no,
            "num_people": num_people,
            "items": order_items,
            "total_amount": total_amount
        }

        orders_collection.insert_one(order_data)

        return render_template('bill.html', order=order_data)

    return redirect(url_for('home'))


# ======================
# ADMIN LOGIN
# ======================
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        admin_username = request.form['username']
        admin_password = request.form['password']

        # Set your admin login username/password
        if admin_username == "admin" and admin_password == "admin123":
            session['admin'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            return "Invalid admin credentials!"

    return render_template('admin_login.html')


# =============== ADMIN DASHBOARD ===============
@app.route('/admin_dashboard')
def admin_dashboard():
    if "admin" not in session:
        return redirect(url_for('admin_login'))

    all_orders = list(orders_collection.find())
    return render_template('admin.html', orders=all_orders)


# ---------- ADMIN LOGOUT ----------
@app.route('/admin_logout')
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for('admin_login'))


# ---------- USER LOGOUT ----------
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))


# ---------- RUN APP ----------
if __name__ == "__main__":
    app.run(debug=True)
