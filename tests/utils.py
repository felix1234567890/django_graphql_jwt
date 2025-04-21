import json
from django.test import Client
from django.contrib.auth import get_user_model

User = get_user_model()

class GraphQLTestClient:
    """
    A test client for GraphQL queries and mutations
    """
    def __init__(self, client=None):
        self.client = client or Client()
        self.token = None
    
    def query(self, query, variables=None, headers=None):
        """
        Execute a GraphQL query
        """
        data = {
            'query': query,
            'variables': variables or {}
        }
        
        request_headers = {'Content-Type': 'application/json'}
        if self.token:
            request_headers['Authorization'] = f'JWT {self.token}'
        
        if headers:
            request_headers.update(headers)
        
        response = self.client.post(
            '/graphql/',
            json.dumps(data),
            content_type='application/json',
            **{f'HTTP_{k.replace("-", "_").upper()}': v for k, v in request_headers.items()}
        )
        
        return json.loads(response.content.decode())
    
    def login(self, username, password):
        """
        Login a user and store the token
        """
        mutation = '''
        mutation TokenAuth($username: String!, $password: String!) {
            tokenAuth(username: $username, password: $password) {
                token
            }
        }
        '''
        
        variables = {
            'username': username,
            'password': password
        }
        
        response = self.query(mutation, variables)
        
        if 'errors' in response:
            raise Exception(f"Login failed: {response['errors']}")
        
        self.token = response['data']['tokenAuth']['token']
        return self.token
    
    def create_user(self, username, email, password):
        """
        Create a test user
        """
        mutation = '''
        mutation CreateUser($input: CreateUserInput!) {
            createUser(createUserInput: $input) {
                user {
                    id
                    username
                    email
                }
            }
        }
        '''
        
        variables = {
            'input': {
                'username': username,
                'email': email,
                'password': password
            }
        }
        
        return self.query(mutation, variables)

def create_test_user(username="testuser", email="test@example.com", password="password123"):
    """
    Create a test user directly in the database
    """
    return User.objects.create_user(
        username=username,
        email=email,
        password=password
    )
