from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from reportlab.pdfgen import canvas

app = Flask(__name__)
app.secret_key = "secretkey"

# DATABASE CONFIG
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# LOGIN CONFIG
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# ================= MODELS =================

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(50))

class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer = db.Column(db.String(100))
    product = db.Column(db.String(100))
    qty = db.Column(db.Integer)
    price = db.Column(db.Float)
    gst = db.Column(db.Float)
    total = db.Column(db.Float)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ================= ROUTES =================

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(
            username=request.form["username"],
            password=request.form["password"]
        ).first()

        if user:
            login_user(user)
            return redirect("/dashboard")

    return render_template("login.html")

@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    if request.method == "POST":
        customer = request.form["customer"]
        product = request.form["product"]
        qty = int(request.form["qty"])
        price = float(request.form["price"])

        subtotal = qty * price
        gst = subtotal * 0.18
        total = subtotal + gst

        invoice = Invoice(
            customer=customer,
            product=product,
            qty=qty,
            price=price,
            gst=gst,
            total=total
        )

        db.session.add(invoice)
        db.session.commit()

        generate_pdf(invoice)

        return render_template("invoice.html", invoice=invoice)

    return render_template("dashboard.html")

@app.route("/logout")
def logout():
    logout_user()
    return redirect("/")

# ================= PDF =================

def generate_pdf(invoice):
    c = canvas.Canvas(f"Invoice_{invoice.id}.pdf")
    c.drawString(50, 800, "INVOICE")
    c.drawString(50, 760, f"Customer: {invoice.customer}")
    c.drawString(50, 740, f"Product: {invoice.product}")
    c.drawString(50, 720, f"Quantity: {invoice.qty}")
    c.drawString(50, 700, f"Price: ₹{invoice.price}")
    c.drawString(50, 680, f"GST (18%): ₹{invoice.gst}")
    c.drawString(50, 660, f"Total: ₹{invoice.total}")
    c.save()

# ================= MAIN =================

    with app.app_context():
        db.create_all()

        # CREATE DEFAULT USER ONCE
        if not User.query.first():
            admin = User(username="admin", password="admin")
            db.session.add(admin)
            db.session.commit()
if _name_== "_main_":
    app.run(host="0.0.0.0", port=10000)


