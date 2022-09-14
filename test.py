import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from app import app

from models import *

class BookingTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = app
        self.client = self.app.test_client      
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_home_page(self):
        response = self.client().get('/')
        self.assertEqual(response.status_code, 200)

    def test_venues_page(self):
        response = self.client().get('/venues')
        self.assertEqual(response.status_code, 200)

    def test_search_venues(self):
        search_term = {"search_term": 'a'}
        response = self.client().post('/venues/search', json=search_term)
        self.assertEqual(response.status_code, 200)

    def test_show_venue(self):
        response = self.client().get('/venues/2')
        self.assertEqual(response.status_code, 200)

    # def test_create_venue(self):
    #     new_venue = {
    #         "name" : 'test1',
    #         "city" :  'test',
    #         "state" :  'CA',
    #         "address" : 'test',
    #         "phone" : '123-123-1234',
    #         "genres" : 'jazz',
    #         "facebook_link" : "https://www.facebook.com/test/",
    #         "seeking_talent" : 'false',           
    #         "website" : "https://www.facebook.com/test"
    #     }
    #     response = self.client().post('/venues/create', json=new_venue)
    #     self.assertEqual(response.status_code, 200)



if __name__ == "__main__":
    unittest.main()