import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
import json

from models import setup_db, Question, Category, db

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    '''
    @~TODO: Set up CORS. Allow '*' for origins.
    Delete the sample route after completing the TODOs
    '''
    cors = CORS(app)
    '''
    @~TODO: Use the after_request decorator to set Access-Control-Allow
    '''
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add
        (
            'Access-Control-Allow-Methods',
            'GET, POST, PATCH, DELETE, OPTION'
        )
        return response
    '''
    @~TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    '''
    @app.route('/categories', methods=['GET'])
    def get_categories():
        try:
            all_categories = Category.query.all()
            formatted_categories = {}
            for category in all_categories:
                formatted_categories[category.id] = category.type
            return jsonify({
              "success": True,
              "categories": formatted_categories
            })
        except Exception:
            abort(500)
    '''
    @~TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    '''
    @app.route('/questions', methods=['GET'])
    def get_paginated_questions():
        try:
            page = int(request.args.get('page'))
            questionsQuery = Question.query.all()
            questions = [question.format() for question in questionsQuery]
            start = (page - 1) * QUESTIONS_PER_PAGE
            end = page * QUESTIONS_PER_PAGE
            categories = {}
            query = Category.query.all()
            for category in query:
                categories[category.id] = category.type
            return jsonify({
              "success": True,
              "questions": questions[start:end],
              "total_questions": len(questions),
              "categories": categories,
              "current_category": None
            })
        except Exception:
            abort(404)

    '''
    @~TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    '''
    @app.route('/questions/<int:id>', methods=['DELETE'])
    def delete_question(id):
        try:
            question = Question.query.get(id)
            question.delete()
            return jsonify({
              "success": True,
              "deleted_question": question.format()
            })
        except Exception:
            db.session.rollback()
            abort(422)
    '''
    @~TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    '''
    @app.route('/questions', methods=['POST'])
    def add_question():
        try:
            data_str = request.data
            data_dict = json.loads(data_str)
            question = data_dict['question']
            answer = data_dict['answer']
            category = data_dict['category']
            difficulty = data_dict['difficulty']
            new_question = Question(
                question=question,
                answer=answer,
                category=category,
                difficulty=difficulty)
            new_question.insert()
            return jsonify({
              "success": True,
              "new_question": new_question.format()
            })
        except:
            db.session.rollback()
            abort(422)
    '''
    @~TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    '''
    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        try:
            search_term_str = request.data
            search_term_dict = json.loads(search_term_str)
            questions = Question.query.filter(Question.question.ilike('%' + search_term_dict['searchTerm'] + '%')).all()
            formatted_questions = [q.format() for q in questions]
            return jsonify({
              "success": True,
              "questions": formatted_questions,
              "total_questions": len(formatted_questions),
              "current_category": None
            })
        except Exception:
            abort(404)
    '''
    @~TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    '''
    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def get_questions_by_categories(category_id):
        try:
            questions = Question.query.filter_by(category=category_id).all()
            formatted_questions = [question.format() for question in questions]
            return jsonify({
              "success": True,
              "questions": formatted_questions,
              "total_questions": len(formatted_questions),
              "current_category": category_id
            })
        except Exception:
            abort(404)

    '''
    @~TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    '''
    @app.route('/quizzes', methods=['POST'])
    def get_quizzes():
        try:
            data_str = request.data
            data_dict = json.loads(data_str)
            previous_questions = data_dict['previous_questions']
            quiz_category = data_dict['quiz_category']
            print(previous_questions, quiz_category)
            #all categories
            if quiz_category['id'] == 0:
                questions = Question.query.filter(~Question.id.in_(previous_questions)).all()
            #specific category
            else:
                questions = Question.query.filter_by(category=quiz_category['id']).filter(~Question.id.in_(previous_questions)).all()

            random_question = random.choice(questions)
            formatted_random_question = random_question.format()
            return jsonify({
              "success": True,
              "question": formatted_random_question
            })
        except Exception:
            abort(404)

    '''
    @~TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    '''
    @app.errorhandler(404)
    def page_not_found(e):
        return jsonify({
          "success": False,
          "error": 404,
          "message": "page not found"
        }), 404

    @app.errorhandler(422)
    def unprocessable_entity(e):
        return jsonify({
          "success": False,
          "error": 422,
          "message": "unprocessable entity"
        }), 422

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({
          "success": False,
          "error": 500,
          "message": "server_error"
        }), 500

    return app

    