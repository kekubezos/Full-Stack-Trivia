import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
import random
import json

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_questions(request, data):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    formatted_questions = [item.format() for item in data]
    return formatted_questions[start: end]


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    # Setting up CORS
    CORS(app, resources={r"*": {"origins": "*"}})

    @app.after_request
    def after_request(response):
        response.headers.add("Access-Control-Allow-Headers",
                             "Content-Type, Authorization")
        response.headers.add("Access-Control-Allow-Headers",
                             "GET, POST, PATCH,DELETE, OPTIONS")
        return response

    @app.route('/categories')
    def get_categories():
        try:
            categories = {}
            for category in Category.query.all():
                categories[category.id] = category.type

            return jsonify({
                'categories': categories
            })

        except Exception:
            abort(422)

    # Endpoint to add a new category
    @app.route("/categories", methods=["POST"])
    def add_category():
        category_type = request.get_json()["type"]
        category = Category(type=category_type)

        try:
            category.insert()

            return jsonify({
                "added": category.id,
                "success": True
            })

        except Exception:
            abort(400)

    @app.route('/questions')
    def get_questions():
        questions = Question.query.all()
        categories = Category.query.all()
        paginated_questions = paginate_questions(request, questions)

        try:
            if len(paginated_questions) == 0:
                abort(404)

            return jsonify({
                'questions': paginated_questions,
                'total_questions': len(questions),
                'categories': {category.id: category.type
                               for category in categories},
                'current_category': None
            })

        except Exception:
            abort(400)

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        question = Question.query.filter(Question.id == question_id) \
            .one_or_none()

        if question is None:
            abort(404)

        try:
            question.delete()

            return jsonify({
                'success': True,
                'deleted': question.id,

            })

        except Exception:
            abort(422)

    @app.route('/questions', methods=["POST"])
    def add_question():
        try:
            data = request.get_json()

            searchTerm = data.get("searchTerm", None)

            if searchTerm is not None:
                questions = Question.query \
                    .filter(Question.question.ilike("%{}%".
                                                    format(searchTerm))).all()
                formatted_questions = [question.format()
                                       for question in questions]

                return jsonify({
                    "questions": formatted_questions,
                    "totalQuestions": len(questions),
                    "currentCategory": None
                })

            else:
                question = data["question"]
                answer = data["answer"]
                difficulty = int(data["difficulty"])
                category = int(data["category"])

                question = Question(question=question,
                                    answer=answer,
                                    difficulty=difficulty,
                                    category=category)

                question.insert()

                return jsonify({
                    "added": question.id,
                    "success": True
                })

        except Exception:
            abort(400)

    @app.route('/categories/<int:category_id>/questions', methods=["GET"])
    def get_questions_by_category(category_id):
        questions = Question.query.filter_by(category=category_id).all()
        formatted_questions = [question.format() for question in questions]

        try:
            return jsonify({
                "questions": formatted_questions,
                "totalQwuestions": len(questions),
                "currentCategory": None
            })

        except Exception:
            abort(400)

    @app.route("/quizzes", methods=["POST"])
    def get_questions_for_quiz():
        try:
            data = request.get_json()

            previous_questions = data["previous_questions"]
            quiz_category = data["quiz_category"]

        except Exception:
            abort(400)

        if quiz_category:
            questions = Question.query.filter_by(
                category=quiz_category).\
                filter(Question.id.notin_(previous_questions)).all()

        else:
            questions = Question.query. \
                filter(~Question.category.in_(previous_questions)).all()

        question = random.choice(questions).format() if questions else None

        return jsonify({
            "question": question
        })

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': 400,
            'message': 'Bad request'
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'Resource Not found'
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': 'Request could not be processed'
        }), 422

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            'success': False,
            'error': 500,
            'message': 'Internal server error.'
        }), 500

    return app
