import json
import unittest

from flaskr import create_app
from models import setup_db, Question, Category,db


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.database_name = "trivia_test"
        self.database_user = "postgres"
        self.database_password = "password"
        self.database_host = "localhost:5432"
        self.database_path = f"postgresql://{self.database_user}:{self.database_password}@{self.database_host}/{self.database_name}"

        self.app = create_app({
            "SQLALCHEMY_DATABASE_URI": self.database_path,
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
            "TESTING": True
        })
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()

            # Neue Frage und Kategorie hinzufügen für meine Katze Schubi :)
            new_category = Category(type="cat")
            db.session.add(new_category)
            db.session.commit()

            new_question = Question(
                question="What is my cat's name?",
                answer="Schubiger",
                category=1,
                difficulty=2
            )
            db.session.add(new_question)
            db.session.commit()

    def tearDown(self):
        with self.app.app_context():
            db.session.query(Question).delete()
            db.session.query(Category).delete()
            db.session.commit()
            db.session.remove()
            db.drop_all()

# ------------------------------------------------------------------------------
#  TEST FOR ALL QUESTION SPECIFIC QUERIES
#  Write at least one test for each test for successful operation and for expected errors.
# ----------------------------------------------------------------------------
    
    def test_search_question(self):
        res = self.client.post('/questions/search', json={"searchTerm": "cat"})
        data = json.loads(res.data) 

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
    
    def test_get_questions_by_page(self):
        res = self.client.get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_404_request_beyond_valid_pages(self):
        res = self.client.get('/questions?page=2000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "Resource not found")


    def test_delete_question(self):
        res = self.client.delete('/questions/1')
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        
    
    def test_404_question_not_exist(self):
        res = self.client.delete('/questions/1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found')

    def test_add_question(self):
        new_question = {
            "question": "What is my cat's name?",
            "answer": "Schubiger",
            "category": 1,
            "difficulty": 2
        }
        res = self.client.post('/questions', json=new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['created'])

    def test_422_if_question_creation_fails(self):
        res = self.client.post('/questions', json={})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable entity')
        
    def test_422_question_search_with_no_results(self):
        res = self.client.post('/questions/search', json={"search": "SFSFGS"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable entity: searchTerm is required')

# ------------------------------------------------------------------------------
#  TEST FOR ALL CATEGORY SPECIFIC QUERIES
#  Write at least one test for each test for successful operation and for expected errors.
# ------------------------------------------------------------------------------    
    
    def test_get_categories(self):
        res = self.client.get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])

    def test_get_question_by_category(self):
        new_question = {
            "question": "What is my cat's name?",
            "answer": "Schubiger",
            "category": 1,
            "difficulty": 2
        }
        res = self.client.post('/questions', json=new_question)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['created'])

        res = self.client.get('/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])

    def test_404_category_not_exist(self):
        res = self.client.get('/categories/1000/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found')



if __name__ == "__main__":
    unittest.main()
