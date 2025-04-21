from django.test import TestCase
from django.contrib.auth import get_user_model
from .utils import GraphQLTestClient, create_test_user

User = get_user_model()

class AuthenticationTests(TestCase):
    def setUp(self):
        self.client = GraphQLTestClient()
        self.user = create_test_user()
    
    def test_user_creation(self):
        """Test creating a new user through GraphQL"""
        response = self.client.create_user(
            username="newuser",
            email="newuser@example.com",
            password="newpassword123"
        )
        
        self.assertNotIn('errors', response)
        self.assertEqual(response['data']['createUser']['user']['username'], 'newuser')
        self.assertEqual(response['data']['createUser']['user']['email'], 'newuser@example.com')
        
        # Verify user was created in the database
        self.assertTrue(User.objects.filter(username='newuser').exists())
    
    def test_token_auth(self):
        """Test user can get authentication token"""
        mutation = '''
        mutation {
            tokenAuth(username: "testuser", password: "password123") {
                token
            }
        }
        '''
        
        response = self.client.query(mutation)
        
        self.assertNotIn('errors', response)
        self.assertIn('token', response['data']['tokenAuth'])
        self.assertIsNotNone(response['data']['tokenAuth']['token'])
    
    def test_invalid_credentials(self):
        """Test token auth with invalid credentials"""
        mutation = '''
        mutation {
            tokenAuth(username: "testuser", password: "wrongpassword") {
                token
            }
        }
        '''
        
        response = self.client.query(mutation)
        
        self.assertIn('errors', response)
    
    def test_me_query(self):
        """Test authenticated user can query their own info"""
        # First login to get token
        self.client.login('testuser', 'password123')
        
        query = '''
        query {
            me {
                id
                username
                email
            }
        }
        '''
        
        response = self.client.query(query)
        
        self.assertNotIn('errors', response)
        self.assertEqual(response['data']['me']['username'], 'testuser')
        self.assertEqual(response['data']['me']['email'], 'test@example.com')
    
    def test_me_query_unauthenticated(self):
        """Test unauthenticated user cannot query me endpoint"""
        query = '''
        query {
            me {
                id
                username
                email
            }
        }
        '''
        
        response = self.client.query(query)
        
        # The me query should return null for unauthenticated users
        self.assertIsNone(response['data']['me'])
