import os
import string
from unicodedata import category
from unittest import result
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import load_only
from flask_cors import CORS
import random
from models import setup_db, Question, Category, db

QUESTIONS_PER_PAGE = 10

#----------------------------------------------------------------
# Pagination Funktion
#----------------------------------------------------------------


def paginate_questions(request, selection): 
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions


#----------------------------------------------------------------
# Create App
#----------------------------------------------------------------

def create_app(test_config=None):
    
    # App Kreators
    app = Flask(__name__)
    setup_db(app)
    CORS(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})


#----------------------------------------------------------------
# APP AFTER REQUEST
#----------------------------------------------------------------
 


    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS')
        response.headers.add('Access-Control-Allow-Origin', '*')    
        return response
    


#----------------------------------------------------------------
# QUESTION REQUESTS
#----------------------------------------------------------------

#----------------------------------------------------------------
# GET /questions    
#----------------------------------------------------------------


    @app.route('/questions')
    def get_questions():
        questions = Question.query.all()
        current_questions = paginate_questions(request, questions)
        categories = Category.query.all()
        formatted_categories = {category.id: category.type for category in categories}

        if len(current_questions) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': len(questions),
            'categories': formatted_categories
        })  

#----------------------------------------------------------------   
# DELETE /questions/<question_id>
#----------------------------------------------------------------   

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        question = Question.query.get(question_id)

        if question is None:
            abort(404)

        question.delete()
        
        total_questions = Question.query.all()
        current_questions = paginate_questions(request, total_questions)


        return jsonify({
            'success': True,
            'deleted': question_id,
        })
    
#----------------------------------------------------------------
# POST /questions
#----------------------------------------------------------------

    @app.route('/questions', methods=['POST'])
    def create_question():
        body = request.get_json()

        new_question = body.get('question', None)
        new_answer = body.get('answer', None)
        new_category = body.get('category', None)
        new_difficulty = body.get('difficulty', None)

        if new_question is None or new_answer is None or new_category is None or new_difficulty is None:
            abort(422)

        question = Question(question=new_question, answer=new_answer, category=new_category, difficulty=new_difficulty)
        question.insert()

        total_questions = Question.query.all()
        current_questions = paginate_questions(request, total_questions)

        return jsonify({
            'success': True,
            'created': question.id,
            'total_questions': len(total_questions),
            'questions': current_questions
        })
    
#----------------------------------------------------------------
# POST /questions/search
#----------------------------------------------------------------

    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        try:
            print("Incoming Request:", request.data)  
            body = request.get_json()
            print("Parsed JSON:", body)  

            if not body:
                return jsonify({
                    'success': False,
                    'error': 400,
                    'message': 'Bad request: JSON body missing'
                }), 400

            # Extract search term
            search_term = body.get('searchTerm', "").strip()
            print("Extracted searchTerm:", search_term) 

            if not search_term or search_term == "":
                return jsonify({
                    'success': False,
                    'error': 422,
                    'message': 'Unprocessable entity: searchTerm is required'
                }), 422

            # Search for questions
            questions = Question.query.filter(Question.question.ilike(f"%{search_term}%")).all()
            print("Matched Questions:", questions)  

            # Paginate results
            current_questions = paginate_questions(request, questions)

            return jsonify({
                'success': True,
                'questions': current_questions,
                'total_questions': len(questions),
                'current_category': None  
            })

        except Exception as e:
            print(f"Error in search_questions: {e}") 
            return jsonify({
                'success': False,
                'error': 500,
                'message': 'Internal server error'
            }), 500


#----------------------------------------------------------------
# CATEGORIE REQUESTS
#----------------------------------------------------------------    

#----------------------------------------------------------------
# GET /categories
#----------------------------------------------------------------

    @app.route('/categories')
    def get_categories():
        categories = db.session.query(Category).order_by(Category.id).all()
        
        if len(categories) == 0:
            abort(404)
        
        return jsonify({
            'success': True,
            'categories': {category.id: category.type for category in categories}   
        })

#----------------------------------------------------------------
# GET /categories/<int:category_id>/questions
#----------------------------------------------------------------
    @app.route('/categories/<int:category_id>/questions')
    def get_questions_by_category(category_id):
        category = Category.query.get(category_id)
        if category is None:
            abort(404)

        questions = Question.query.filter(Question.category == category_id).all()
        current_questions = paginate_questions(request, questions)

        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': len(questions),
            'current_category': category_id
        })
        


#----------------------------------------------------------------
# POST /quizzes
#----------------------------------------------------------------

    @app.route('/quizzes', methods=['POST'])
    def play_quiz():
        body = request.get_json()
        previous_questions = body.get('previous_questions', [])
        quiz_category = body.get('quiz_category', None)

        if quiz_category is None:
            abort(422)

        if quiz_category['id'] == 0:
            questions = Question.query.all()
        else:
            questions = Question.query.filter(Question.category == quiz_category['id']).all()

        questions = [question.format() for question in questions]
        random_question = None

        for question in questions:
            if question['id'] not in previous_questions:
                random_question = question
                break

        return jsonify({
            'success': True,
            'question': random_question
        })
    
#----------------------------------------------------------------
# Error Handling   
#----------------------------------------------------------------   

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
            'message': 'Resource not found'
        }), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            'success': False,
            'error': 405,
            'message': 'Method not allowed'
        }), 405
    
    @app.errorhandler(422)
    def unprocessable_entity(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': 'Unprocessable entity'
        }), 422
    
    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            'success': False,
            'error': 500,
            'message': 'Internal server error'
        }), 500
    
    return app



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

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """

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

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """

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

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """

   
