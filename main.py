from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
# from sqlalchemy.sql.expression import func
import random

app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

apikey= "TopSecretAPIKey"

##Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    # def make_dict(self):
    #     dictionary = {}
    #     for values in self.__table__.columns:
    #         dictionary[values.name] = getattr(self, values.name)
    #     return dictionary

    # dictionary comprehension is Below
    def make_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/random", methods= ["GET","POST"])
def get_random_cafe():
    all_cafes = db.session.query(Cafe).all()
    random_cafe = random.choice(all_cafes)
    print(random_cafe)
    print(random_cafe.can_take_calls)
    # uzun yol
    # deneme = jsonify (can_take_calls=random_cafe.can_take_calls,
    #         coffee_price=random_cafe.coffee_price,
    #         has_sockets=random_cafe.has_sockets,
    #         has_wifi=random_cafe.has_wifi,
    #         id=random_cafe.id,
    #         img_url=random_cafe.img_url,
    #         location=random_cafe.location,
    #         map_url=random_cafe.map_url,
    #         name=random_cafe.name,
    #         seats=random_cafe.seats)
    # print(type(deneme))
    deneme = jsonify(cafe= random_cafe.make_dict())
    # sql alch random function
    # random_cafe = db.session.query(Cafe).order_by(func.random()).first()
    return deneme
@app.route("/all", methods= ['GET','POST'])
def get_all_cafes():
    all_cafes = db.session.query(Cafe).all()
    cafe_list = []
    for cafes in all_cafes:
        cafe_list.append(cafes.make_dict())
    information = jsonify(cafe=cafe_list)
    return information
    # single line version
    # return jsonify(cafes=[cafe.make_dict() for cafe in all_cafes])

@app.route("/search", methods= ['GET','POST'])
def search_cafe():
    location =request.args.get('loc')
    # cafe_selected = Cafe.query.filter_by(location=location).first()
    cafe_selected = Cafe.query.filter_by(location=location).all()
    cafes_selected = []
    for cafes in cafe_selected:
        cafes_selected.append(cafes.make_dict())
    if cafe_selected:
        return jsonify(cafe=cafes_selected)
    else:
        return jsonify(error={"Not Found": "Sorry, we don't have a cafe at that location."})
    # try and expect also okay

# @app.route("/search/<loc>", methods= ['GET','POST'])
# def search_cafe(loc):
#     # cafe_selected = Cafe.query.filter_by(location=loc).first()
#     if cafe_selected:
#         return jsonify(cafe=cafe_selected.make_dict())
#     else:
#         return jsonify(error={"Not Found": "Sorry, we don't have a cafe at that location."})
    # try and expect also okay
@app.route("/add", methods= ['GET','POST'])
def add_cafe():
    # name_cafe = request.args.get('name')
    # map_url = request.args.get('map_url')
    # print(name_cafe)
    # print(map_url)
    can_take_calls = bool(request.form.get('can_take_calls'))
    coffee_price=request.form.get('coffee_price')
    has_sockets=bool(request.form.get('has_sockets'))
    has_wifi=bool(request.form.get('has_wifi'))
    img_url=request.form.get('img_url')
    location=request.form.get('location')
    map_url=request.form.get('map_url')
    name=request.form.get('name')
    seats=request.form.get('seats')
    has_toilet=bool(request.form.get('has_toilet'))
    cafe_check = Cafe.query.filter_by(name=name).first()
    if cafe_check:
        return jsonify(response={"fail": "Cafe is already in the database."})
    else:
        add_new_cafe = Cafe(can_take_calls=can_take_calls, coffee_price= coffee_price, has_sockets=has_sockets, has_wifi=has_wifi, img_url=img_url, location=location, map_url=map_url, name=name, seats=seats, has_toilet=has_toilet)
        print(add_new_cafe)
        db.session.add(add_new_cafe)
        db.session.commit()
        return jsonify(response={"success": "Successfully added the new cafe."})

@app.route('/patch/<int:cafe_id>', methods= ['GET','PATCH'])
def update_coffee_price(cafe_id):
    update_coffee_p = Cafe.query.get(cafe_id)
    if update_coffee_p:
        update_coffee_p.coffee_price = request.form.get('coffee_price')
        db.session.commit()
        return jsonify(response={"success": "Successfully updated coffee price."})
    else:
        return jsonify(response={"fail": "No cafe with this id."})

@app.route('/report-closed/<int:cafe_id>',methods= ['GET','DELETE'])
def delete_coffee_shop(cafe_id):
    api_check = request.args.get("api-key")
    if api_check == apikey:
        delete_coffee = Cafe.query.get(cafe_id)
        if delete_coffee:
            db.session.delete(delete_coffee)
            db.session.commit()
            return jsonify(response={"success": "Successfully delete the cafe"})
        else:
            return jsonify(response= {"error": {"Not Found": "Sorry a cafe with that id was not found in the database."}})
    else:
        return jsonify(response={"error": "Sorry, that's not allowed. Make sure you have the correct api_key."})

## HTTP GET - Read Record

## HTTP POST - Create Record

## HTTP PUT/PATCH - Update Record

## HTTP DELETE - Delete Record


if __name__ == '__main__':
    app.run(debug=True)
