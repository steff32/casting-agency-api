
import unittest
from unittest.mock import patch
from app import create_app
from models import db, Movie, Actor, setup_db, db_drop_and_create_all

# Define permissions for each role
CASTING_ASSISTANT_PERMS = ["view:movies", "view:actors"]
CASTING_DIRECTOR_PERMS = [
    "view:movies", "view:actors", "add:actors", "update:actors", "delete:actors", "update:movies"
]
EXEC_PRODUCER_PERMS = [
    "view:movies", "view:actors", "add:actors", "update:actors", "delete:actors",
    "add:movies", "update:movies", "delete:movies"
]

class CastingAgencyTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()
        with self.app.app_context():
            setup_db(self.app)
            db_drop_and_create_all()
            # Add test data
            self.movie = Movie(title="Test Movie", release_date="2025-01-01")
            self.movie.insert()
            self.actor = Actor(name="Test Actor", age=30, gender="Male")
            self.actor.insert()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    # Helper to patch permissions for a test
    def patch_auth(self, permissions):
        patcher_verify = patch('auth.verify_decode_jwt', return_value={"permissions": permissions})
        patcher_token = patch('auth.get_token_auth_header', return_value="mock_token")
        return patcher_verify, patcher_token

    # Success tests
    def test_get_movies_success(self):
        patch_verify, patch_token = self.patch_auth(CASTING_ASSISTANT_PERMS)
        with patch_verify, patch_token:
            res = self.client.get('/movies')
            data = res.get_json()
            self.assertEqual(res.status_code, 200)
            self.assertTrue(data['success'])
            self.assertGreaterEqual(len(data['movies']), 1)

    def test_get_actors_success(self):
        patch_verify, patch_token = self.patch_auth(CASTING_ASSISTANT_PERMS)
        with patch_verify, patch_token:
            res = self.client.get('/actors')
            data = res.get_json()
            self.assertEqual(res.status_code, 200)
            self.assertTrue(data['success'])
            self.assertGreaterEqual(len(data['actors']), 1)

    def test_create_movie_success(self):
        patch_verify, patch_token = self.patch_auth(EXEC_PRODUCER_PERMS)
        with patch_verify, patch_token:
            new_movie = {'title': 'New Movie', 'release_date': '2025-01-01'}
            res = self.client.post('/movies', json=new_movie)
            data = res.get_json()
            self.assertEqual(res.status_code, 201)
            self.assertTrue(data['success'])
            self.assertIn('movie', data)

    def test_create_actor_success(self):
        patch_verify, patch_token = self.patch_auth(CASTING_DIRECTOR_PERMS)
        with patch_verify, patch_token:
            new_actor = {'name': 'New Actor', 'age': 35, 'gender': 'Female'}
            res = self.client.post('/actors', json=new_actor)
            data = res.get_json()
            self.assertEqual(res.status_code, 201)
            self.assertTrue(data['success'])
            self.assertIn('actor', data)

    def test_update_movie_success(self):
        patch_verify, patch_token = self.patch_auth(CASTING_DIRECTOR_PERMS)
        with patch_verify, patch_token:
            update_data = {'title': 'Updated Movie'}
            res = self.client.patch(f'/movies/{self.movie.id}', json=update_data)
            data = res.get_json()
            self.assertEqual(res.status_code, 200)
            self.assertTrue(data['success'])
            self.assertEqual(data['movie']['title'], 'Updated Movie')

    def test_update_actor_success(self):
        patch_verify, patch_token = self.patch_auth(CASTING_DIRECTOR_PERMS)
        with patch_verify, patch_token:
            update_data = {'name': 'Updated Actor'}
            res = self.client.patch(f'/actors/{self.actor.id}', json=update_data)
            data = res.get_json()
            self.assertEqual(res.status_code, 200)
            self.assertTrue(data['success'])
            self.assertEqual(data['actor']['name'], 'Updated Actor')

    def test_delete_movie_success(self):
        patch_verify, patch_token = self.patch_auth(EXEC_PRODUCER_PERMS)
        with patch_verify, patch_token:
            res = self.client.delete(f'/movies/{self.movie.id}')
            data = res.get_json()
            self.assertEqual(res.status_code, 200)
            self.assertTrue(data['success'])
            self.assertEqual(data['delete'], self.movie.id)

    def test_delete_actor_success(self):
        patch_verify, patch_token = self.patch_auth(CASTING_DIRECTOR_PERMS)
        with patch_verify, patch_token:
            res = self.client.delete(f'/actors/{self.actor.id}')
            data = res.get_json()
            self.assertEqual(res.status_code, 200)
            self.assertTrue(data['success'])
            self.assertEqual(data['delete'], self.actor.id)

    # Error tests
    def test_get_movies_empty(self):
        patch_verify, patch_token = self.patch_auth(CASTING_ASSISTANT_PERMS)
        with patch_verify, patch_token, self.app.app_context():
            Movie.query.delete()
            db.session.commit()
            res = self.client.get('/movies')
            data = res.get_json()
            self.assertEqual(res.status_code, 200)
            self.assertTrue(data['success'])
            self.assertEqual(len(data['movies']), 0)

    def test_create_movie_invalid_data(self):
        patch_verify, patch_token = self.patch_auth(EXEC_PRODUCER_PERMS)
        with patch_verify, patch_token:
            invalid_movie = {'title': 'Invalid Movie'}  # Missing release_date
            res = self.client.post('/movies', json=invalid_movie)
            data = res.get_json()
            self.assertEqual(res.status_code, 422)
            self.assertFalse(data['success'])

    def test_update_movie_not_found(self):
        patch_verify, patch_token = self.patch_auth(CASTING_DIRECTOR_PERMS)
        with patch_verify, patch_token:
            res = self.client.patch('/movies/9999', json={'title': 'No Movie'})
            data = res.get_json()
            self.assertEqual(res.status_code, 404)
            self.assertFalse(data['success'])

    def test_delete_actor_not_found(self):
        patch_verify, patch_token = self.patch_auth(CASTING_DIRECTOR_PERMS)
        with patch_verify, patch_token:
            res = self.client.delete('/actors/9999')
            data = res.get_json()
            self.assertEqual(res.status_code, 404)
            self.assertFalse(data['success'])

    # RBAC Tests - Casting Assistant
    def test_casting_assistant_can_view(self):
        patch_verify, patch_token = self.patch_auth(CASTING_ASSISTANT_PERMS)
        with patch_verify, patch_token:
            self.assertEqual(self.client.get('/movies').status_code, 200)
            self.assertEqual(self.client.get('/actors').status_code, 200)
    
    def test_casting_assistant_cannot_modify(self):
        patch_verify, patch_token = self.patch_auth(CASTING_ASSISTANT_PERMS)
        with patch_verify, patch_token:
            res = self.client.post('/actors', json={'name': 'New', 'age': 30, 'gender': 'Male'})
            self.assertEqual(res.status_code, 403)
            res = self.client.delete(f'/actors/{self.actor.id}')
            self.assertEqual(res.status_code, 403)

    # RBAC Tests - Casting Director
    def test_casting_director_can_manage_actors(self):
        patch_verify, patch_token = self.patch_auth(CASTING_DIRECTOR_PERMS)
        with patch_verify, patch_token:
            res = self.client.post('/actors', json={'name': 'New', 'age': 30, 'gender': 'Male'})
            self.assertEqual(res.status_code, 201)
            res = self.client.patch(f'/movies/{self.movie.id}', json={'title': 'Updated'})
            self.assertEqual(res.status_code, 200)
    
    def test_casting_director_cannot_manage_movies(self):
        patch_verify, patch_token = self.patch_auth(CASTING_DIRECTOR_PERMS)
        with patch_verify, patch_token:
            res = self.client.post('/movies', json={'title': 'New Movie', 'release_date': '2025-01-01'})
            self.assertEqual(res.status_code, 403)
            res = self.client.delete(f'/movies/{self.movie.id}')
            self.assertEqual(res.status_code, 403)

    # RBAC Tests - Executive Producer
    def test_executive_producer_can_manage_all(self):
        patch_verify, patch_token = self.patch_auth(EXEC_PRODUCER_PERMS)
        with patch_verify, patch_token:
            res = self.client.post('/movies', json={'title': 'New Movie', 'release_date': '2025-01-01'})
            self.assertEqual(res.status_code, 201)
            res = self.client.delete(f'/movies/{self.movie.id}')
            self.assertEqual(res.status_code, 200)
    
    def test_executive_producer_can_delete_actors(self):
        patch_verify, patch_token = self.patch_auth(EXEC_PRODUCER_PERMS)
        with patch_verify, patch_token:
            res = self.client.delete(f'/actors/{self.actor.id}')
            self.assertEqual(res.status_code, 200)

    # Additional RBAC tests
    def test_casting_director_can_delete_actors(self):
        patch_verify, patch_token = self.patch_auth(CASTING_DIRECTOR_PERMS)
        with patch_verify, patch_token:
            res = self.client.delete(f'/actors/{self.actor.id}')
            self.assertEqual(res.status_code, 200)
    
    def test_executive_producer_can_create_actors(self):
        patch_verify, patch_token = self.patch_auth(EXEC_PRODUCER_PERMS)
        with patch_verify, patch_token:
            res = self.client.post('/actors', json={'name': 'New', 'age': 30, 'gender': 'Male'})
            self.assertEqual(res.status_code, 201)

if __name__ == "__main__":
    unittest.main()