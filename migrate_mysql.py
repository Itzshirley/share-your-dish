from __future__ import annotations

import os
import shutil
from pathlib import Path

import pymysql

from app import BASE_DIR, CATEGORIES, Recipe, User, app, db


MYSQL_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "localhost"),
    "user": os.getenv("MYSQL_USER", "root"),
    "password": os.getenv("MYSQL_PASSWORD", ""),
    "database": os.getenv("MYSQL_DATABASE", "share-your-dish"),
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor,
}


def migrate() -> tuple[int, int]:
    connection = pymysql.connect(**MYSQL_CONFIG)
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, username, email, password FROM users ORDER BY id")
            legacy_users = cursor.fetchall()
            cursor.execute(
                "SELECT id, user_id, title, category, description, ingredients, instructions, image, "
                "is_budget_friendly, created_at FROM recipes ORDER BY id"
            )
            legacy_recipes = cursor.fetchall()
    finally:
        connection.close()

    user_map: dict[int, int] = {}
    user_count = 0
    recipe_count = 0
    legacy_uploads = BASE_DIR / "uploads"
    static_uploads = BASE_DIR / "static" / "images"
    static_uploads.mkdir(exist_ok=True)

    with app.app_context():
        db.create_all()
        for old_user in legacy_users:
            user = User.query.filter_by(email=old_user["email"].lower()).first()
            if not user:
                user = User.query.filter_by(username=old_user["username"]).first()
            if not user:
                user = User(
                    username=old_user["username"],
                    email=old_user["email"].lower(),
                    password_hash=old_user["password"],
                )
                db.session.add(user)
                db.session.flush()
                user_count += 1
            user_map[old_user["id"]] = user.id

        for old_recipe in legacy_recipes:
            category = old_recipe["category"] if old_recipe["category"] in CATEGORIES else "dinner"
            existing = Recipe.query.filter_by(
                title=old_recipe["title"], category=category
            ).first()
            image_value = old_recipe["image"] or None
            needs_image_migration = not existing or not existing.image or existing.image.startswith("/uploads/")
            if image_value and needs_image_migration and not image_value.startswith(("http://", "https://", "/")):
                source = legacy_uploads / Path(image_value).name
                if not source.is_file():
                    source = static_uploads / Path(image_value).name
                destination = static_uploads / Path(image_value).name
                if source.is_file():
                    if os.getenv("BLOB_STORE_ID") or os.getenv("BLOB_READ_WRITE_TOKEN"):
                        from vercel.blob import sync as blob

                        uploaded = blob.put_blob(
                            f"recipe-images/legacy-{destination.name}",
                            source.read_bytes(),
                            access="public",
                            content_type="image/jpeg",
                        )
                        image_value = uploaded.url
                    else:
                        if not destination.exists():
                            shutil.copy2(source, destination)
                        image_value = f"/static/images/{destination.name}"

            if existing:
                if image_value and needs_image_migration:
                    existing.image = image_value
                continue

            created_at = old_recipe["created_at"]
            recipe = Recipe(
                user_id=user_map.get(old_recipe["user_id"]),
                title=old_recipe["title"],
                category=category,
                description=old_recipe["description"],
                ingredients=old_recipe["ingredients"],
                instructions=old_recipe["instructions"],
                image=image_value,
                is_budget_friendly=bool(old_recipe["is_budget_friendly"]),
                created_at=created_at,
            )
            db.session.add(recipe)
            recipe_count += 1

        db.session.commit()
    return user_count, recipe_count


if __name__ == "__main__":
    users, recipes = migrate()
    print(f"Imported {users} users and {recipes} recipes into the Python app database.")
