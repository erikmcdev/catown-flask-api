import os
from datetime import datetime

from flask import Flask, jsonify, request
from flask_cors import CORS

from adapters import orm
from domain import model
from service import services, unit_of_work

orm.start_mappers()
app = Flask(__name__)
domain = os.environ.get("CORS_DOMAIN")
CORS(app, origins=domain, headers="Content-Type", expose_headers="Content-Type")


@app.before_request
def before_request():
    print(request.headers)
    if request.headers.get("Api-Key") != os.environ.get("API_KEY"):
        return jsonify({"error": "Unauthorized"}), 401


@app.route("/add_cat", methods=["POST"])
def add_cat():
    try:
        birthdate = request.json["birthdate"]
        if birthdate is not None:
            birthdate = datetime.strptime(birthdate, "%Y-%m-%d").date()
        result = services.add_cat(
            request.json["name"],
            birthdate,
            model.Nature[request.json["nature"]],
            request.json["house_id"],
            unit_of_work.SqlAlchemyUnitOfWork(),
        )
        response = {"id": result["id"], "count": result["count"]}
        if result["new_home_id"]:
            response["new_home_id"] = result["new_home_id"]
        print(response)
        return response, 201
    except (services.NotEnoughRoom, services.NoSuchHouse) as e:
        return {"message": str(e)}, 400


@app.route("/transfer", methods=["POST"])
def transfer_endpoint():
    destiny_id = request.json["destiny_id"]
    cat_id = request.json["cat_id"]
    try:
        result = services.transfer(
            destiny_id, cat_id, unit_of_work.SqlAlchemyUnitOfWork()
        )
    except services.NotEnoughRoom as e:
        return {"message": str(e)}, 400

    return {"house_id": destiny_id, "cat_id": result}, 201


@app.route("/create_house", methods=["POST"])
def create_house():
    try:
        result = services.create_house(unit_of_work.SqlAlchemyUnitOfWork())
    except services.NoNeedForCreatingHouse as e:
        return {"message": str(e)}, 400
    return {"house_id": result}, 201


@app.route("/houses", methods=["GET"])
def houses_endpoint():
    result = services.list_houses(unit_of_work.SqlAlchemyUnitOfWork())
    return jsonify(result), 200


@app.route("/cats", methods=["GET"])
def cats_by_house_endpoint():
    try:
        house_id = request.args.get("house_id")
        result = services.get_cats_by_house(
            house_id, unit_of_work.SqlAlchemyUnitOfWork()
        )

        return jsonify(result), 200
    except Exception as e:
        return {"message": str(e)}, 400
