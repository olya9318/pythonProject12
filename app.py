# app.py

from flask import Flask, request, jsonify
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy

from schemas import movies_schema, movie_schema
import models

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['JSON_AS_ASCII'] = False
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

api = Api(app)
movie_ns = api.namespace('movies')


@movie_ns.route("/")
class MoviesView(Resource):
    def get(self):
        movie_with_genre_and_director = db.session.query(models.Movie.id, models.Movie.title, models.Movie.description,
                                                         models.Movie.rating, models.Movie.trailer,
                                                         models.Genre.name.label('genre'),
                                                         models.Director.name.label('director')).join(
            models.Genre).join(models.Director).all()

        director_id = request.args.get('director_id')
        genre_id = request.args.get('genre_id')
        if director_id:
            movie_with_genre_and_director = movie_with_genre_and_director.filter(
                models.Movie.director_id == director_id)
        if genre_id:
            movie_with_genre_and_director = movie_with_genre_and_director.filter(
                models.Movie.genre_id == genre_id)
        all_movies = movie_with_genre_and_director
        return jsonify(movies_schema.dump(all_movies))

    def post(self):
        req_json = request.json
        new_movie = models.Movie(**req_json)
        with db.session.begin():
            db.session.add(new_movie)
        return f"Новый объект с id {new_movie.id} создан!"


@movie_ns.route("/<int:movie_id>")
class MovieView(Resource):
    def get(self, movie_id: int):
        movie = db.session.query(models.Movie.id, models.Movie.title, models.Movie.description,
                                 models.Movie.rating, models.Movie.trailer, models.Genre.name.label('genre'),
                                 models.Director.name.label('director')).join(models.Genre).join(
            models.Director).filter(
            models.Movie.id == movie_id).first()
        if movie:
            return jsonify(movie_schema.dump(movie))
        return "Нет такого фильма", 404

    def delete(self, movie_id):
        movie = db.session.query(models.Movie).get(movie_id)
        if not movie:
            return "Нет такого фильма", 404
        db.session.delete(movie)
        db.session.commit()
        return f"Объект с id {movie_id} удален", 204


if __name__ == '__main__':
    app.run(debug=True)
