from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone
from functools import wraps
from pathlib import Path

from flask import Flask, abort, flash, redirect, render_template, request, session, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash

from seed_recipes import STARTER_RECIPES

BASE_DIR = Path(__file__).resolve().parent
INSTANCE_DIR = Path(os.getenv("INSTANCE_DIR", "/tmp/share-your-dish" if os.getenv("VERCEL") else BASE_DIR / "instance"))
INSTANCE_DIR.mkdir(exist_ok=True)

database_url = os.getenv("DATABASE_URL")
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql+psycopg://", 1)
elif database_url and database_url.startswith("postgresql://"):
    database_url = database_url.replace("postgresql://", "postgresql+psycopg://", 1)
if os.getenv("VERCEL") and (not database_url or not os.getenv("SECRET_KEY")):
    raise RuntimeError("Vercel requires SECRET_KEY and DATABASE_URL. See the deployment README.")

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "local-only-change-me")
app.config["MAX_CONTENT_LENGTH"] = 4 * 1024 * 1024
app.config["SQLALCHEMY_DATABASE_URI"] = database_url or f"sqlite:///{INSTANCE_DIR / 'share_your_dish.db'}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = INSTANCE_DIR / "uploads"
app.config["UPLOAD_FOLDER"].mkdir(exist_ok=True)

db = SQLAlchemy(app)

CATEGORIES = {
    "breakfast": "Breakfast",
    "lunch": "Lunch",
    "dinner": "Dinner",
    "snacks": "Snacks",
    "drinks": "Drinks",
    "desserts": "Desserts",
    "vegan": "Vegan",
}
FOOD_IMAGES = {
    "breakfast": "https://images.unsplash.com/photo-1533089860892-a7c6f0a88666?auto=format&fit=crop&w=900&q=82",
    "lunch": "https://images.unsplash.com/photo-1547592180-85f173990554?auto=format&fit=crop&w=900&q=82",
    "dinner": "https://images.unsplash.com/photo-1473093295043-cdd812d0e601?auto=format&fit=crop&w=900&q=82",
    "snacks": "https://images.unsplash.com/photo-1573080496219-bb080dd4f877?auto=format&fit=crop&w=900&q=82",
    "drinks": "https://images.unsplash.com/photo-1513558161293-cdab765edfd7?auto=format&fit=crop&w=900&q=82",
    "desserts": "https://images.unsplash.com/photo-1578985545062-69928b1d9587?auto=format&fit=crop&w=900&q=82",
    "vegan": "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?auto=format&fit=crop&w=900&q=82",
}
RECIPE_IMAGES = {
    "Peanut Butter Banana Oats": "photo-1517673132405-a56a62b18caf",
    "Crispy Potato and Egg Skillet": "photo-1525351484163-7529414344d8",
    "Apple Cinnamon Pancakes": "photo-1528207776546-365bb710ee93",
    "Chickpea Rice Lunch Bowl": "photo-1490645935967-10de6ba17061",
    "Tomato and Lentil Soup": "photo-1547592166-23ac45744acd",
    "Tuna and Sweetcorn Jacket Potato": "photo-1518977676601-b53f82aba655",
    "One-Pot Tomato Lentil Stew": "photo-1603105037880-880cd4edfb0d",
    "Cabbage and Egg Fried Rice": "photo-1512058564366-18510be2db19",
    "Creamy Pea Pasta": "https://images.pexels.com/photos/36868304/pexels-photo-36868304.jpeg?auto=compress&cs=tinysrgb&w=900",
    "Smoky Stovetop Popcorn": "photo-1578849278619-e73505e9610f",
    "Crispy Spiced Chickpeas": "photo-1625944525533-473f1a3d54e7",
    "Three-Ingredient Banana Oat Bites": "photo-1558961363-fa8fdf82db35",
    "Homemade Lemon Iced Tea": "photo-1556679343-c7306c1976bc",
    "Cozy Cinnamon Cocoa": "photo-1517701604599-bb29b565090c",
    "Peanut Butter Banana Smoothie": "photo-1505252585461-04db1eb84625",
    "Creamy Rice Pudding": "photo-1488477181946-6428a0291777",
    "Easy Apple Crumble": "https://images.pexels.com/photos/33400608/pexels-photo-33400608.jpeg?auto=compress&cs=tinysrgb&w=900",
    "One-Minute Chocolate Mug Cake": "photo-1578985545062-69928b1d9587",
    "Lentil Tomato Pasta": "photo-1551183053-bf91a1d81141",
    "Chickpea and Potato Curry": "photo-1603894584373-5ac82b2ae398",
    "Black Bean Cabbage Tacos": "photo-1551504734-5ee1c4a1479b",
}
RECIPE_IMAGES = {
    title: photo_id if photo_id.startswith("https://") else f"https://images.unsplash.com/{photo_id}?auto=format&fit=crop&w=900&q=82"
    for title, photo_id in RECIPE_IMAGES.items()
}


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    recipes = db.relationship("Recipe", backref="author", lazy=True)


class Recipe(db.Model):
    __table_args__ = (db.UniqueConstraint("category", "title", name="uq_recipe_category_title"),)

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    title = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(32), nullable=False, default="dinner", index=True)
    description = db.Column(db.Text, nullable=False)
    ingredients = db.Column(db.Text, nullable=False)
    instructions = db.Column(db.Text, nullable=False)
    image = db.Column(db.Text, nullable=True)
    is_budget_friendly = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), index=True)

    @property
    def image_url(self) -> str:
        return self.image or RECIPE_IMAGES.get(
            self.title, FOOD_IMAGES.get(self.category, FOOD_IMAGES["dinner"])
        )


@app.context_processor
def shared_template_data():
    return {"categories": CATEGORIES, "current_user": current_user(), "year": datetime.now().year}


def current_user() -> User | None:
    user_id = session.get("user_id")
    return db.session.get(User, user_id) if user_id else None


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not current_user():
            flash("Please log in to continue.", "notice")
            return redirect(url_for("login", next=request.path))
        return view(*args, **kwargs)

    return wrapped


def save_image(upload) -> str | None:
    if not upload or not upload.filename:
        return None
    content_type = upload.mimetype or ""
    extensions = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp", "image/gif": ".gif"}
    extension = extensions.get(content_type)
    if not extension:
        raise ValueError("Choose a JPG, PNG, WebP, or GIF image.")
    if os.getenv("VERCEL") and not (os.getenv("BLOB_STORE_ID") or os.getenv("BLOB_READ_WRITE_TOKEN")):
        raise ValueError("Connect a public Vercel Blob store before uploading recipe photos.")
    data = upload.read(4 * 1024 * 1024 + 1)
    if len(data) > 4 * 1024 * 1024:
        raise ValueError("Images must be 4 MB or smaller.")
    name = f"{uuid.uuid4().hex}{extension}"
    if os.getenv("BLOB_STORE_ID") or os.getenv("BLOB_READ_WRITE_TOKEN"):
        try:
            from vercel.blob import sync as blob

            result = blob.put_blob(
                f"recipe-images/{name}", data, access="public", content_type=content_type
            )
            return result.url
        except Exception as error:
            app.logger.exception("Vercel Blob upload failed")
            raise ValueError("Image upload failed. Check the connected Vercel Blob store.") from error
    (Path(app.config["UPLOAD_FOLDER"]) / name).write_bytes(data)
    return url_for("uploaded_image", filename=name)


@app.route("/uploads/<path:filename>")
def uploaded_image(filename: str):
    from flask import send_from_directory

    response = send_from_directory(app.config["UPLOAD_FOLDER"], filename)
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response


@app.get("/")
def home():
    breakfast_pick = Recipe.query.filter_by(title="Apple Cinnamon Pancakes").first()
    if not breakfast_pick:
        breakfast_pick = Recipe.query.filter_by(category="breakfast").order_by(Recipe.created_at.desc()).first()
    lunch_pick = Recipe.query.filter_by(title="Tomato and Lentil Soup").first()
    if not lunch_pick:
        lunch_pick = Recipe.query.filter_by(category="lunch").order_by(Recipe.created_at.desc()).first()
    featured_recipes = [recipe for recipe in (breakfast_pick, lunch_pick) if recipe]
    return render_template("home.html", featured_recipes=featured_recipes)


@app.get("/recipes")
def recipes():
    category = request.args.get("category", "")
    query = Recipe.query
    if category in CATEGORIES:
        query = query.filter_by(category=category)
    if request.args.get("budget") == "1":
        query = query.filter_by(is_budget_friendly=True)
    items = query.order_by(Recipe.created_at.desc()).all()
    return render_template("recipes.html", recipes=items, selected_category=category)


@app.get("/category/<category>")
def category_page(category: str):
    if category not in CATEGORIES:
        abort(404)
    items = Recipe.query.filter_by(category=category).order_by(Recipe.created_at.desc()).all()
    return render_template("category.html", recipes=items, category=category)


@app.route("/recipe/new", methods=["GET", "POST"])
@login_required
def add_recipe():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        category = request.form.get("category", "dinner")
        description = request.form.get("description", "").strip()
        ingredients = request.form.get("ingredients", "").strip()
        instructions = request.form.get("instructions", "").strip()
        if not title or not description or not ingredients or not instructions:
            flash("Please complete all recipe details.", "error")
        elif category not in CATEGORIES:
            flash("Choose a valid recipe category.", "error")
        else:
            try:
                image_url = save_image(request.files.get("image"))
            except ValueError as error:
                flash(str(error), "error")
                return render_template("recipe_form.html", recipe=request.form)
            recipe = Recipe(
                user_id=current_user().id,
                title=title,
                category=category,
                description=description,
                ingredients=ingredients,
                instructions=instructions,
                image=image_url,
                is_budget_friendly=request.form.get("is_budget_friendly") == "1",
            )
            db.session.add(recipe)
            db.session.commit()
            flash("Your recipe is on the table!", "success")
            return redirect(url_for("recipe_detail", recipe_id=recipe.id))
    return render_template("recipe_form.html", recipe={})


@app.get("/recipe/<int:recipe_id>")
def recipe_detail(recipe_id: int):
    recipe = db.get_or_404(Recipe, recipe_id)
    return render_template("recipe_detail.html", recipe=recipe)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        if not username or not email or len(password) < 8:
            flash("Enter a username and email, and use a password with at least 8 characters.", "error")
        elif User.query.filter(func.lower(User.email) == email).first() or User.query.filter_by(username=username).first():
            flash("That username or email is already registered.", "error")
        else:
            user = User(username=username, email=email, password_hash=generate_password_hash(password))
            db.session.add(user)
            db.session.commit()
            session["user_id"] = user.id
            flash("Welcome to the table!", "success")
            return redirect(url_for("account"))
    return render_template("auth.html", mode="signup")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = User.query.filter(func.lower(User.email) == email).first()
        if user and verify_password(user.password_hash, password):
            session["user_id"] = user.id
            next_url = request.args.get("next", "")
            if next_url.startswith("/") and not next_url.startswith("//"):
                return redirect(next_url)
            return redirect(url_for("account"))
        flash("Email or password was not recognized.", "error")
    return render_template("auth.html", mode="login")


def verify_password(stored: str, password: str) -> bool:
    if stored.startswith(("$2y$", "$2a$", "$2b$")):
        try:
            import bcrypt

            return bcrypt.checkpw(password.encode(), stored.replace("$2y$", "$2b$", 1).encode())
        except (ImportError, ValueError):
            return False
    try:
        return check_password_hash(stored, password)
    except (ValueError, TypeError):
        return False


@app.get("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "notice")
    return redirect(url_for("home"))


@app.get("/account")
@login_required
def account():
    user = current_user()
    items = Recipe.query.filter_by(user_id=user.id).order_by(Recipe.created_at.desc()).all()
    return render_template("account.html", recipes=items)


@app.get("/about")
def about():
    return render_template("about.html")


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        if not all(request.form.get(key, "").strip() for key in ("name", "email", "message")):
            flash("Please complete each field before sending.", "error")
        else:
            flash("Thanks for reaching out. Your message has been received.", "success")
            return redirect(url_for("contact"))
    return render_template("contact.html")


@app.errorhandler(413)
def upload_too_large(_error):
    flash("Images must be 4 MB or smaller.", "error")
    return redirect(url_for("add_recipe"))


with app.app_context():
    db.create_all()
    if not db.session.query(Recipe.id).first():
        db.session.add_all(
            Recipe(**recipe, is_budget_friendly=True) for recipe in STARTER_RECIPES
        )
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=os.getenv("FLASK_DEBUG") == "1")
