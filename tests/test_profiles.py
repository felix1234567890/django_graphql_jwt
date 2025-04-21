import os
import tempfile
from django.test import TestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from .utils import GraphQLTestClient, create_test_user
from profiles.models import Profile

# Create a temporary media directory for testing file uploads
TEMP_MEDIA_ROOT = tempfile.mkdtemp()

@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class ProfileTests(TestCase):
    def setUp(self):
        self.client = GraphQLTestClient()
        self.user = create_test_user()
        
        # Login the user
        self.client.login('testuser', 'password123')
        
        # Create a test image file
        self.image_content = b'GIF87a\x01\x00\x01\x00\x80\x01\x00\x00\x00\x00ccc,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;'
        self.image_file = SimpleUploadedFile(
            name='test_image.gif',
            content=self.image_content,
            content_type='image/gif'
        )
    
    def tearDown(self):
        # Clean up the temporary media directory
        for root, dirs, files in os.walk(TEMP_MEDIA_ROOT):
            for file in files:
                os.remove(os.path.join(root, file))
    
    def test_query_profiles(self):
        """Test querying all profiles"""
        # First create a profile
        profile = Profile.objects.create(
            name="Test Profile",
            image=self.image_file,
            user=self.user
        )
        
        query = '''
        query {
            profiles {
                id
                name
                user {
                    username
                }
            }
        }
        '''
        
        response = self.client.query(query)
        
        self.assertNotIn('errors', response)
        self.assertEqual(len(response['data']['profiles']), 1)
        self.assertEqual(response['data']['profiles'][0]['name'], 'Test Profile')
        self.assertEqual(response['data']['profiles'][0]['user']['username'], 'testuser')
    
    def test_query_profile_by_id(self):
        """Test querying a single profile by ID"""
        # First create a profile
        profile = Profile.objects.create(
            name="Test Profile",
            image=self.image_file,
            user=self.user
        )
        
        query = f'''
        query {{
            profile(id: {profile.id}) {{
                id
                name
                user {{
                    username
                }}
            }}
        }}
        '''
        
        response = self.client.query(query)
        
        self.assertNotIn('errors', response)
        self.assertEqual(response['data']['profile']['name'], 'Test Profile')
        self.assertEqual(response['data']['profile']['user']['username'], 'testuser')
    
    def test_my_profile(self):
        """Test querying the authenticated user's profile"""
        # First create a profile
        profile = Profile.objects.create(
            name="Test Profile",
            image=self.image_file,
            user=self.user
        )
        
        query = '''
        query {
            myProfile {
                id
                name
                user {
                    username
                }
            }
        }
        '''
        
        response = self.client.query(query)
        
        self.assertNotIn('errors', response)
        self.assertEqual(response['data']['myProfile']['name'], 'Test Profile')
        self.assertEqual(response['data']['myProfile']['user']['username'], 'testuser')
    
    def test_delete_profile(self):
        """Test deleting a profile"""
        # First create a profile
        profile = Profile.objects.create(
            name="Test Profile",
            image=self.image_file,
            user=self.user
        )
        
        mutation = f'''
        mutation {{
            deleteProfile(id: {profile.id}) {{
                success
            }}
        }}
        '''
        
        response = self.client.query(mutation)
        
        self.assertNotIn('errors', response)
        self.assertTrue(response['data']['deleteProfile']['success'])
        
        # Verify profile was deleted from the database
        self.assertFalse(Profile.objects.filter(id=profile.id).exists())
