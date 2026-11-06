import io
import os
import tempfile
import unittest
from pathlib import Path

TEST_STORAGE = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
os.environ["DATABASE_URL"] = f"sqlite:///{Path(TEST_STORAGE.name, 'test.db').as_posix()}"

from app import FOOD_IMAGES, Recipe, app, db


class ShareYourDishTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        app.config.update(
            TESTING=True,
            SECRET_KEY="test-secret",
            UPLOAD_FOLDER=Path(self.temp_dir.name) / "uploads",
        )
        app.config["UPLOAD_FOLDER"].mkdir()
        self.context = app.app_context()
        self.context.push()
        db.create_all()
        self.client = app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        db.engine.dispose()
        self.context.pop()
        self.temp_dir.cleanup()

    def test_fresh_database_starts_with_three_budget_recipes_per_category(self):
        from app import CATEGORIES

        for category in CATEGORIES:
            count = Recipe.query.filter_by(category=category, is_budget_friendly=True).count()
            self.assertEqual(count, 3, category)
        starter_images = {
            recipe.image_url for recipe in Recipe.query.filter_by(is_budget_friendly=True).all()
        }
        self.assertEqual(len(starter_images), 21)

    def test_seeded_budget_recipes_cover_every_category(self):
        from app import CATEGORIES

        for category in CATEGORIES:
            recipe = Recipe(
                title=f"{category} starter",
                category=category,
                description="A budget meal",
                ingredients="Pantry ingredients",
                instructions="Cook and serve",
                is_budget_friendly=True,
            )
            db.session.add(recipe)
        db.session.commit()
        for category in CATEGORIES:
            response = self.client.get(f"/category/{category}")
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"Easy on the budget", response.data)

    def test_homepage_shows_only_breakfast_and_lunch_recipes(self):
        db.session.add_all(
            [
                Recipe(
                    title="Apple Cinnamon Pancakes",
                    category="breakfast",
                    description="Apple pancakes.",
                    ingredients="Flour\nApple",
                    instructions="Mix and cook.",
                    is_budget_friendly=True,
                ),
                Recipe(
                    title="Tomato and Lentil Soup",
                    category="lunch",
                    description="Tomato lentil soup.",
                    ingredients="Tomatoes\nLentils",
                    instructions="Simmer until tender.",
                    is_budget_friendly=True,
                ),
            ]
        )
        db.session.commit()
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.count(b'class="recipe-card"'), 2)
        self.assertIn(b"Apple Cinnamon Pancakes", response.data)
        self.assertIn(b"Tomato and Lentil Soup", response.data)
        self.assertIn(b"photo-1528207776546-365bb710ee93", response.data)
        self.assertIn(b"photo-1547592166-23ac45744acd", response.data)

    def test_missing_deployment_auth_config_keeps_catalog_available(self):
        app.config["IS_VERCEL"] = True
        app.config["AUTH_ENABLED"] = False
        try:
            home_response = self.client.get("/")
            signup_response = self.client.get("/signup")
            login_response = self.client.get("/login")
            self.assertEqual(home_response.status_code, 200)
            self.assertIn(b"temporary mode", home_response.data)
            self.assertEqual(signup_response.status_code, 503)
            self.assertIn(b"DATABASE_URL", signup_response.data)
            self.assertEqual(login_response.status_code, 503)
        finally:
            app.config["IS_VERCEL"] = False
            app.config["AUTH_ENABLED"] = True

    def test_signup_login_and_private_recipe_submission(self):
        response = self.client.post(
            "/signup",
            data={"username": "cook", "email": "cook@example.com", "password": "long-password"},
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        response = self.client.post(
            "/recipe/new",
            data={
                "title": "Pantry Pasta",
                "category": "dinner",
                "description": "A quick cheap supper.",
                "ingredients": "Pasta\nTomato",
                "instructions": "Boil pasta.\nAdd tomato.",
                "is_budget_friendly": "1",
            },
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Pantry Pasta", response.data)
        recipe = Recipe.query.filter_by(title="Pantry Pasta").one()
        self.assertTrue(recipe.is_budget_friendly)
        self.assertEqual(recipe.image_url, FOOD_IMAGES["dinner"])

    def test_photo_upload_is_saved_and_served_locally(self):
        self.client.post(
            "/signup",
            data={"username": "photo", "email": "photo@example.com", "password": "long-password"},
        )
        response = self.client.post(
            "/recipe/new",
            data={
                "title": "Photo Dish",
                "category": "lunch",
                "description": "A pictured dish.",
                "ingredients": "Bread",
                "instructions": "Toast it.",
                "image": (io.BytesIO(b"fake-image-data"), "dish.png", "image/png"),
            },
            content_type="multipart/form-data",
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        recipe = Recipe.query.filter_by(title="Photo Dish").one()
        self.assertTrue(recipe.image.startswith("/uploads/"))
        image_response = self.client.get(recipe.image)
        self.assertEqual(image_response.status_code, 200)
        self.assertEqual(image_response.data, b"fake-image-data")
        image_response.close()


if __name__ == "__main__":
    unittest.main()
