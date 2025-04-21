# End-to-End Tests for Django GraphQL JWT Project

This directory contains end-to-end tests for the Django GraphQL JWT project. These tests verify that the entire application works correctly from the user's perspective, testing the GraphQL API endpoints and their functionality.

## Test Structure

The tests are organized into the following files:

- `test_auth.py`: Tests for user authentication (user creation, token auth, etc.)
- `test_books.py`: Tests for book operations (create, read, update, delete)
- `test_reviews.py`: Tests for review operations
- `test_profiles.py`: Tests for profile operations
- `test_suite.py`: A comprehensive test suite that runs all tests
- `utils.py`: Utility functions for testing

## Running the Tests

To run all tests, use the following command from the project root:

```bash
./run_tests.py
```

To run specific test modules, specify them as arguments:

```bash
./run_tests.py tests.test_auth tests.test_books
```

## Test Coverage

The tests cover the following functionality:

### Authentication
- User creation
- Token authentication
- User information retrieval

### Books
- Creating books
- Retrieving books (all, by ID, by author)
- Updating books
- Deleting books
- Searching and pagination

### Reviews
- Creating reviews
- Retrieving reviews (all, by ID, by user, by book)
- Updating reviews
- Deleting reviews
- Validation (can't review own book)

### Profiles
- Creating profiles
- Retrieving profiles (all, by ID, own profile)
- Updating profiles
- Deleting profiles

## Adding New Tests

To add new tests:

1. Create a new test file in the `tests` directory
2. Import the necessary modules and the `GraphQLTestClient` from `utils.py`
3. Create a test class that inherits from `django.test.TestCase`
4. Add test methods that use the GraphQL client to test functionality
5. Add the new test class to `test_suite.py`
