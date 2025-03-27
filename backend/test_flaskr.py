import os
import json
import unittest
from flaskr import create_app
from models import setup_db, Question, Category, db
from dotenv import load_dotenv

load_dotenv()

class TriviaTestCase(unittest.TestCase):
    """Diese Klasse testet alle Endpunkte der Trivia-App."""

    def setUp(self):
        """Testvariablen definieren und App initialisieren."""
        self.database_name = os.getenv("DB_NAME")
        self.database_user = os.getenv("DB_USER")
        self.database_password = os.getenv("DB_PASSWORD")
        self.database_host = os.getenv("DB_HOST") + ":" + os.getenv("DB_PORT")
        self.database_path = f"postgresql://{self.database_user}:{self.database_password}@{self.database_host}/{self.database_name}"

        self.app = create_app({
            "SQLALCHEMY_DATABASE_URI": self.database_path,
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
            "TESTING": True
        })
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()
            # Eine Kategorie und Frage für Tests einfügen
            new_category = Category(type="cat")
            db.session.add(new_category)
            db.session.commit()

            new_question = Question(
                question="What is my cat's name?",
                answer="Schubiger",
                category=new_category.id,
                difficulty=2
            )
            db.session.add(new_question)
            db.session.commit()

    def tearDown(self):
        """Wird nach jedem Test ausgeführt."""
        with self.app.app_context():
            db.session.query(Question).delete()
            db.session.query(Category).delete()
            db.session.commit()
            db.session.remove()
            db.drop_all()

    # GET /questions
    def test_get_questions_success(self):
        res = self.client.get('/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['categories'])

    def test_get_questions_failure_invalid_page(self):
        res = self.client.get('/questions?page=2000')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], "Resource not found")

    # DELETE /questions/<question_id>
    def test_delete_question_success(self):
        # Neue Frage zum Löschen hinzufügen
        with self.app.app_context():
            question = Question(
                question="Test delete question?",
                answer="Yes",
                category=1,
                difficulty=1
            )
            db.session.add(question)
            db.session.commit()
            question_id = question.id

        res = self.client.delete(f'/questions/{question_id}')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['deleted'], question_id)

    def test_delete_question_failure_not_exist(self):
        res = self.client.delete('/questions/1000')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], "Resource not found")

    # POST /questions (Erstellung einer Frage)
    def test_add_question_success(self):
        new_question = {
            "question": "What is my cat's name?",
            "answer": "Schubiger",
            "category": 1,
            "difficulty": 2
        }
        res = self.client.post('/questions', json=new_question)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(data['created'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['questions'])

    def test_add_question_failure_missing_fields(self):
        # 'answer' fehlt
        new_question = {
            "question": "Incomplete question?",
            "category": 1,
            "difficulty": 2
        }
        res = self.client.post('/questions', json=new_question)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], "Unprocessable entity")

    # POST /questions/search
    def test_search_question_success(self):
        res = self.client.post('/questions/search', json={"searchTerm": "cat"})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(len(data['questions']) > 0)
        self.assertIsNone(data['current_category'])

    def test_search_question_failure_missing_searchTerm(self):
        res = self.client.post('/questions/search', json={"search": "notexist"})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], "Unprocessable entity: searchTerm is required")

    def test_search_question_failure_no_json(self):
        res = self.client.post('/questions/search')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 500)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], "Internal server error")

    # GET /categories
    def test_get_categories_success(self):
        res = self.client.get('/categories')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(data['categories'])

    def test_get_categories_failure_empty(self):
        # Alle Fragen und Kategorien löschen, um leere Ergebnisse zu simulieren
        with self.app.app_context():
            Question.query.delete()
            Category.query.delete()
            db.session.commit()
        res = self.client.get('/categories')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], "Resource not found")

    # GET /categories/<int:category_id>/questions
    def test_get_questions_by_category_success(self):
        res = self.client.get('/categories/1/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(data['questions'])
        self.assertEqual(data['current_category'], 1)

    def test_get_questions_by_category_failure_invalid_category(self):
        res = self.client.get('/categories/1000/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], "Resource not found")

    # POST /quizzes
    def test_get_quiz_success(self):
        res = self.client.post('/quizzes', json={
            "previous_questions": [],
            "quiz_category": {"id": 1, "type": "cat"}
        })
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertIsNotNone(data['question'])

    def test_get_quiz_failure_missing_data(self):
        res = self.client.post('/quizzes', json={})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], "Unprocessable entity")

    def test_get_quiz_success_no_questions_remaining(self):
        # Alle Fragen der Kategorie 1 als bereits verwendet markieren
        with self.app.app_context():
            questions = Question.query.filter(Question.category == 1).all()
            previous_questions = [question.id for question in questions]
        res = self.client.post('/quizzes', json={
            "previous_questions": previous_questions,
            "quiz_category": {"id": 1, "type": "cat"}
        })
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertIsNone(data['question'])

if __name__ == "__main__":
    unittest.main()
