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

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app, resources={r"*": {"origins": "*"}})
    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """

    @app.after_request
    def after_request(response):
        response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
        response.headers.add("Access-Control-Allow-Headers", "GET, POST, PATCH,DELETE, OPTIONS")
        return response

    """
@TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """

    @app.route('/categories')
    def get_categories():
        categories = {}
        for category in Category.query.all():
            categories[category.id] = category.type

        return jsonify({
            'categories': categories
        })
        # categories = Category.query.all()
        #
        # formatted_categories = {category.format() for category in categories}
        #
        # if len(formatted_categories) == 0:
        #     abort(404)
        #
        # return jsonify({
        #     'categories': formatted_categories,
        # })

    # Endpoint to add a new category
    @app.route("/categories", methods=["POST"])
    def add_category():
        try:
            category_type = request.get_json()["type"]
            category = Category(type=category_type)
            category.insert()

            return jsonify({
                "added": category.id,
                "success": True
            })

        except:
            abort(400)

    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.
    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """

    @app.route('/questions')
    def get_questions():
        questions = Question.query.all()
        categories = Category.query.all()
        paginated_questions = paginate_questions(request, questions)

        if len(paginated_questions) == 0:
            abort(404)

        return jsonify({
            'questions': paginated_questions,
            'total_questions': len(questions),
            'categories': {category.id: category.type for category in categories},
            'current_category': None
        })

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.
    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        question = Question.query.filter(Question.id == question_id).one_or_none()

        if question is None:
            abort(404)

        try:
            question.delete()

            return jsonify({
                'success': True,
                'deleted': question.id,

            })

        except:
            abort(422)

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.
    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.
    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """

    @app.route('/questions', methods=["POST"])
    def add_question():
        try:
            data = request.get_json()

            searchTerm = data.get("searchTerm", None)

            if searchTerm is not None:
                questions = Question.query.filter(Question.question.ilike("%{}%".format(searchTerm))).all()
                formatted_questions = [question.format() for question in questions]

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

                question = Question(question=question, answer=answer, difficulty=difficulty, category=category)

                question.insert()

                return jsonify({
                    "added": question.id,
                    "success": True
                })

        except:
            abort(400)

    """
    @TODO:
    Create a GET endpoint to get questions based on category.
    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """

    @app.route('/categories/<int:category_id>/questions', methods=["GET"])
    def get_questions_by_category(category_id):
        questions = Question.query.filter_by(category=category_id).all()
        formatted_questions = [question.format() for question in questions]

        return jsonify({
            "questions": formatted_questions,
            "totalQwuestions": len(questions),
            "currentCategory": None
        })

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.
    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """

    @app.route("/quizzes", methods=["POST"])
    def get_questions_for_quiz():
        try:
            data = request.get_json()

            previous_questions = data["previous_questions"]
            quiz_category = data["quiz_category"]

        except:
            abort(400)

        if quiz_category:
            questions = Question.query.filter_by(category=quiz_category).filter(Question.id.notin_(
                previous_questions)).all()

        else:
            questions = Question.query.filter(~Question.category.in_(previous_questions)).all()

        question = random.choice(questions).format() if questions else None

        return jsonify({
            "question": question
        })

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """

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