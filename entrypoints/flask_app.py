from datetime import datetime
from flask import Flask, request, jsonify

from domain import model
from adapters import orm
from service import services, unit_of_work
from flask_cors import CORS


orm.start_mappers()
app = Flask(__name__)
CORS(app, headers="Content-Type", expose_headers="Content-Type")

@app.route("/add_cat", methods=["POST"])
def add_cat():
    try:
        birthdate = request.json["birthdate"]
        if birthdate is not None:
            birthdate = datetime.strptime(birthdate, "%Y-%m-%d").date()
        result = services.add_cat(
            request.json["name"],
            birthdate,
            model.Nature(request.json["nature"]),
            unit_of_work.SqlAlchemyUnitOfWork(),
            bool(request.json.get("new_house", False)),
            request.json.get("destination_id", None)
        )
        return {"id": result[0], "house_id": result[1], "count": result[2]}, 201
    except (services.NotEnoughRoom) as e:
        return {"message": str(e)}, 400

@app.route("/transfer", methods=["POST"])
def transfer_endpoint():
    destiny_id = request.json["destiny_id"]
    cat_id = request.json["cat_id"]
    try:
        result = services.transfer(
            destiny_id,
            cat_id,
            unit_of_work.SqlAlchemyUnitOfWork()
        )
    except (services.NotEnoughRoom) as e:
        return {"message": str(e)}, 400

    return {"house_id": destiny_id, "cat_id": result}, 201

@app.route("/houses", methods=["GET"])
def houses_endpoint():
    result = services.list_houses(
        unit_of_work.SqlAlchemyUnitOfWork()
    )
    if not result:
        return "not found", 404
    return jsonify(result), 200

@app.route("/cats", methods=["GET"])
def cats_by_house_endpoint():
    try:
        house_id = request.args.get('house_id')
        result = services.get_cats_by_house(
            house_id,
            unit_of_work.SqlAlchemyUnitOfWork()
        )
        
        return jsonify(result), 200
    except (Exception) as e:
        return {"message": str(e)}, 400




    