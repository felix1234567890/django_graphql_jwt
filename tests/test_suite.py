import unittest
from django.test import TestCase
from django.test.runner import DiscoverRunner

# Import all test modules
from .test_auth import AuthenticationTests
from .test_books import BookTests
from .test_reviews import ReviewTests
from .test_profiles import ProfileTests

def suite():
    """
    Create a test suite that includes all tests
    """
    test_suite = unittest.TestSuite()
    
    # Add all test cases
    test_suite.addTest(unittest.makeSuite(AuthenticationTests))
    test_suite.addTest(unittest.makeSuite(BookTests))
    test_suite.addTest(unittest.makeSuite(ReviewTests))
    test_suite.addTest(unittest.makeSuite(ProfileTests))
    
    return test_suite

if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
