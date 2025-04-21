from django.test import TestCase
from .utils import GraphQLTestClient, create_test_user
from books.models import Book

class BookTests(TestCase):
    def setUp(self):
        self.client = GraphQLTestClient()
        self.user = create_test_user()
        
        # Login the user
        self.client.login('testuser', 'password123')
        
        # Create a test book
        self.book = Book.objects.create(
            title="Test Book",
            description="A book for testing",
            year_published=2023,
            author=self.user
        )
    
    def test_query_books(self):
        """Test querying all books"""
        query = '''
        query {
            books {
                id
                title
                description
                yearPublished
                author {
                    username
                }
            }
        }
        '''
        
        response = self.client.query(query)
        
        self.assertNotIn('errors', response)
        self.assertEqual(len(response['data']['books']), 1)
        self.assertEqual(response['data']['books'][0]['title'], 'Test Book')
        self.assertEqual(response['data']['books'][0]['description'], 'A book for testing')
        self.assertEqual(response['data']['books'][0]['yearPublished'], 2023)
        self.assertEqual(response['data']['books'][0]['author']['username'], 'testuser')
    
    def test_query_book_by_id(self):
        """Test querying a single book by ID"""
        query = f'''
        query {{
            book(id: {self.book.id}) {{
                id
                title
                description
            }}
        }}
        '''
        
        response = self.client.query(query)
        
        self.assertNotIn('errors', response)
        self.assertEqual(response['data']['book']['title'], 'Test Book')
        self.assertEqual(response['data']['book']['description'], 'A book for testing')
    
    def test_create_book(self):
        """Test creating a new book"""
        mutation = '''
        mutation CreateBook($input: CreateBookInput!) {
            createBook(createBookInput: $input) {
                book {
                    id
                    title
                    description
                    yearPublished
                }
            }
        }
        '''
        
        variables = {
            'input': {
                'title': 'New Book',
                'description': 'A newly created book',
                'yearPublished': 2024
            }
        }
        
        response = self.client.query(mutation, variables)
        
        self.assertNotIn('errors', response)
        self.assertEqual(response['data']['createBook']['book']['title'], 'New Book')
        self.assertEqual(response['data']['createBook']['book']['description'], 'A newly created book')
        self.assertEqual(response['data']['createBook']['book']['yearPublished'], 2024)
        
        # Verify book was created in the database
        self.assertTrue(Book.objects.filter(title='New Book').exists())
    
    def test_update_book(self):
        """Test updating an existing book"""
        mutation = f'''
        mutation UpdateBook($input: UpdateBookInput!) {{
            updateBook(updateBookInput: $input) {{
                book {{
                    id
                    title
                    description
                }}
            }}
        }}
        '''
        
        variables = {
            'input': {
                'id': self.book.id,
                'title': 'Updated Book Title',
                'description': 'Updated book description'
            }
        }
        
        response = self.client.query(mutation, variables)
        
        self.assertNotIn('errors', response)
        self.assertEqual(response['data']['updateBook']['book']['title'], 'Updated Book Title')
        self.assertEqual(response['data']['updateBook']['book']['description'], 'Updated book description')
        
        # Verify book was updated in the database
        self.book.refresh_from_db()
        self.assertEqual(self.book.title, 'Updated Book Title')
        self.assertEqual(self.book.description, 'Updated book description')
    
    def test_delete_book(self):
        """Test deleting a book"""
        mutation = f'''
        mutation {{
            deleteBook(bookId: {self.book.id}) {{
                success
            }}
        }}
        '''
        
        response = self.client.query(mutation)
        
        self.assertNotIn('errors', response)
        self.assertTrue(response['data']['deleteBook']['success'])
        
        # Verify book was deleted from the database
        self.assertFalse(Book.objects.filter(id=self.book.id).exists())
    
    def test_my_books(self):
        """Test querying books authored by the authenticated user"""
        query = '''
        query {
            myBooks {
                id
                title
            }
        }
        '''
        
        response = self.client.query(query)
        
        self.assertNotIn('errors', response)
        self.assertEqual(len(response['data']['myBooks']), 1)
        self.assertEqual(response['data']['myBooks'][0]['title'], 'Test Book')
    
    def test_search_books(self):
        """Test searching for books"""
        # Create additional books for testing search
        Book.objects.create(
            title="Python Programming",
            description="Learn Python programming",
            year_published=2022,
            author=self.user
        )
        
        Book.objects.create(
            title="Django Web Development",
            description="Build web apps with Django",
            year_published=2023,
            author=self.user
        )
        
        query = '''
        query {
            books(search: "Python") {
                id
                title
            }
        }
        '''
        
        response = self.client.query(query)
        
        self.assertNotIn('errors', response)
        self.assertEqual(len(response['data']['books']), 1)
        self.assertEqual(response['data']['books'][0]['title'], 'Python Programming')
        
        # Test pagination
        query = '''
        query {
            books(first: 2) {
                id
                title
            }
        }
        '''
        
        response = self.client.query(query)
        
        self.assertNotIn('errors', response)
        self.assertEqual(len(response['data']['books']), 2)
