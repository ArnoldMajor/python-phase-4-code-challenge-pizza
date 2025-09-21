#!/usr/bin/env python3
import os
from flask import Flask, request
from flask_restful import Api, Resource
from flask_migrate import Migrate

# Same imports you already use
from models import db, Restaurant, Pizza, RestaurantPizza

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

api = Api(app)

@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

class Restaurants(Resource):
    def get(self):
        restaurants = Restaurant.query.all()
        result = [
            {"id": restaurant.id, "name": restaurant.name, "address": restaurant.address}
            for restaurant in restaurants
        ]
        return result, 200


class RestaurantByID(Resource):
    def get(self, id):
        restaurant = Restaurant.query.filter_by(id=id).first()
        if not restaurant:
            return {"error": "Restaurant not found"}, 404

        data = restaurant.to_dict()
        return data, 200

    def delete(self, id):
        restaurant = Restaurant.query.filter_by(id=id).first()
        if not restaurant:
            return {"error": "Restaurant not found"}, 404

        db.session.delete(restaurant)
        db.session.commit()
        return "", 204 


class Pizzas(Resource):
    def get(self):
        pizzas = Pizza.query.all()
        result = [pizza.to_dict(only=("id", "name", "ingredients")) for pizza in pizzas]
        return result, 200


class RestaurantPizzas(Resource):
    def post(self):
        data = request.get_json() or {}
        price = data.get("price")
        pizza_id = data.get("pizza_id")
        restaurant_id = data.get("restaurant_id")

        if price is None or pizza_id is None or restaurant_id is None:
            return {"errors": ["price, pizza_id and restaurant_id are required"]}, 400

        pizza = Pizza.query.filter_by(id=pizza_id).first()
        if not pizza:
            return {"error": "Pizza not found"}, 404
        restaurant = Restaurant.query.filter_by(id=restaurant_id).first()
        if not restaurant:
            return {"error": "Restaurant not found"}, 404

        try:
            new_entry = RestaurantPizza(price=price, pizza_id=pizza.id, restaurant_id=restaurant.id)
            db.session.add(new_entry)
            db.session.commit()
        except Exception:
            return {"errors": ["validation errors"]}, 400
        return new_entry.to_dict(), 201


api.add_resource(Restaurants, "/restaurants")
api.add_resource(RestaurantByID, "/restaurants/<int:id>")
api.add_resource(Pizzas, "/pizzas")
api.add_resource(RestaurantPizzas, "/restaurant_pizzas")


if __name__ == "__main__":
    app.run(port=5555, debug=True)