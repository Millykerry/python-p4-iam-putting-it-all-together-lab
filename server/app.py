from flask import Flask, request, session, jsonify
from flask_restful import Api, Resource
from flask_cors import CORS

from config import db, migrate, bcrypt, Config

from models.user import User
from models.recipe import Recipe

app = Flask(__name__)

app.config.from_object(Config)

db.init_app(app)
migrate.init_app(app, db)
bcrypt.init_app(app)

api = Api(app)

CORS(app)

# -------------------------
# SIGNUP
# -------------------------

class Signup(Resource):

    def post(self):

        data = request.get_json()

        try:

            user = User(
                username=data["username"],
                image_url=data.get("image_url"),
                bio=data.get("bio")
            )

            user.password_hash = data["password"]

            db.session.add(user)

            db.session.commit()

            session["user_id"] = user.id

            return {
                "id": user.id,
                "username": user.username,
                "image_url": user.image_url,
                "bio": user.bio
            }, 201

        except Exception as e:

            return {"errors": [str(e)]}, 422


# -------------------------
# CHECK SESSION
# -------------------------

class CheckSession(Resource):

    def get(self):

        user_id = session.get("user_id")

        if user_id:

            user = User.query.get(user_id)

            return {
                "id": user.id,
                "username": user.username,
                "image_url": user.image_url,
                "bio": user.bio
            }, 200

        return {"error": "Unauthorized"}, 401


# -------------------------
# LOGIN
# -------------------------

class Login(Resource):

    def post(self):

        data = request.get_json()

        user = User.query.filter_by(
            username=data["username"]
        ).first()

        if user and user.authenticate(data["password"]):

            session["user_id"] = user.id

            return {
                "id": user.id,
                "username": user.username,
                "image_url": user.image_url,
                "bio": user.bio
            }, 200

        return {"error": "Invalid username or password"}, 401


# -------------------------
# LOGOUT
# -------------------------

class Logout(Resource):

    def delete(self):

        if session.get("user_id"):

            session.pop("user_id")

            return {}, 204

        return {"error": "Unauthorized"}, 401


# -------------------------
# RECIPES
# -------------------------

class RecipeIndex(Resource):

    def get(self):

        if not session.get("user_id"):

            return {"error": "Unauthorized"}, 401

        recipes = Recipe.query.all()

        result = []

        for recipe in recipes:

            result.append({
                "id": recipe.id,
                "title": recipe.title,
                "instructions": recipe.instructions,
                "minutes_to_complete": recipe.minutes_to_complete,
                "user": {
                    "id": recipe.user.id,
                    "username": recipe.user.username
                }
            })

        return result, 200


    def post(self):

        if not session.get("user_id"):

            return {"error": "Unauthorized"}, 401

        data = request.get_json()

        try:

            recipe = Recipe(
                title=data["title"],
                instructions=data["instructions"],
                minutes_to_complete=data["minutes_to_complete"],
                user_id=session["user_id"]
            )

            db.session.add(recipe)

            db.session.commit()

            return {
                "id": recipe.id,
                "title": recipe.title,
                "instructions": recipe.instructions,
                "minutes_to_complete": recipe.minutes_to_complete,
                "user": {
                    "id": recipe.user.id,
                    "username": recipe.user.username
                }
            }, 201

        except Exception as e:

            return {"errors": [str(e)]}, 422


# -------------------------
# ROUTES
# -------------------------

api.add_resource(Signup, "/signup")

api.add_resource(CheckSession, "/check_session")

api.add_resource(Login, "/login")

api.add_resource(Logout, "/logout")

api.add_resource(RecipeIndex, "/recipes")


if __name__ == "__main__":

    app.run(port=5555, debug=True)