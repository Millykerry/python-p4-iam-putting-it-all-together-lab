from sqlalchemy.orm import validates
from config import db

class Recipe(db.Model):

    __tablename__ = "recipes"

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String, nullable=False)

    instructions = db.Column(db.String, nullable=False)

    minutes_to_complete = db.Column(db.Integer)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    @validates("title")
    def validate_title(self, key, title):

        if not title:
            raise ValueError("Title required")

        return title

    @validates("instructions")
    def validate_instructions(self, key, instructions):

        if not instructions:
            raise ValueError("Instructions required")

        if len(instructions) < 50:
            raise ValueError("Instructions must be at least 50 characters")

        return instructions