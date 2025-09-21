from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

metadata = MetaData(
    naming_convention={
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }
)

db = SQLAlchemy(metadata=metadata)


class Restaurant(db.Model, SerializerMixin):
    __tablename__ = "restaurants"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    address = db.Column(db.String)

    # add relationship
    restaurant_pizzas = db.relationship('RestaurantPizza', back_populates="restaurant", cascade="all, delete-orphan")
    pizzas = association_proxy('restaurant_pizzas', 'pizza',
                               creator=lambda pizza: RestaurantPizza(pizza=pizza))

    # add serialization rules
    serialize_only = (
        'id', 
        'name', 
        'address',
        'restaurant_pizzas.id',
        'restaurant_pizzas.price',
        'restaurant_pizzas.pizza_id',
        'restaurant_pizzas.restaurant_id',
        'restaurant_pizzas.pizza.id',
        'restaurant_pizzas.pizza.name',
        'restaurant_pizzas.pizza.ingredients'
        )

    def __repr__(self):
        return f"<Restaurant {self.name}>"


class Pizza(db.Model, SerializerMixin):
    __tablename__ = "pizzas"

    id = db.Column(db.Integer, primary_key=True)
    ingredients = db.Column(db.String)
    name = db.Column(db.String)

    # add relationship
    restaurant_pizzas = db.relationship("RestaurantPizza", back_populates="pizza", cascade="all, delete-orphan")
    restaurants = association_proxy("restaurant_pizzas", 'restaurant', 
                              creator=lambda restaurant: RestaurantPizza(restaurant=restaurant))

    # add serialization rules
    serialize_only = (
        'id', 
        'name', 
        'ingredients',
        )

    def __repr__(self):
        return f"<Pizza {self.name}, {self.ingredients}>"
    


class RestaurantPizza(db.Model, SerializerMixin):
    __tablename__ = "restaurant_pizzas"

    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer, nullable=False)

    pizza_id = db.Column(db.Integer, db.ForeignKey('pizzas.id'))
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'))

    # add relationships
    pizza = db.relationship('Pizza', back_populates='restaurant_pizzas')
    restaurant = db.relationship('Restaurant', back_populates="restaurant_pizzas")

    # add serialization rules
    serialize_only = (
        'id', 
        'price',
        'pizza_id',
        'restaurant_id',
        'pizza.id', 
        'pizza.name',
        'pizza.ingredients',
        'restaurant.id', 
        'restaurant.name',
        'restaurant.address',
        )
    serialize_rules = (
        '-restaurant.restaurant_pizzas',
    )

    # add validation
    @validates('price')
    def price_between_1_and_30(self, key, price):
        if not (1 <= price <= 30):
            raise ValueError("Price must have a value between 1 and 30")
        return price

    def __repr__(self):
        return f"<RestaurantPizza ${self.price}>"
