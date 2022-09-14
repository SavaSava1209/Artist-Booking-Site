import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from app import create_app

from models import setup_db, Venue, Artist, Show

class BookingTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client 
        self.database_name = 'fyyur_test'
        self.database_path = f'postgresql://postgres:jin@localhost:5432/{self.database_name}'
        setup_db(self.app, self.database_path)

        # with self.app.app_context():
        #     self.db = SQLAlchemy()
        #     self.db.init_app(self.app)
        #     # create all tables
        #     self.db.create_all()
    
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

    def test_create_venue(self):
        new_venue = {
            "name" : 'test1',
            "city" :  'test',
            "state" :  'CA',
            "address" : 'test',
            "phone" : '123-123-1234',
            "genres" : 'Jazz',
            "facebook_link" : "https://www.facebook.com/TheMusicalHop",
            "seeking_talent" : 'false',           
            "website" : "https://www.facebook.com/test"
        }
        response = self.client().post('/venues/create', json=new_venue)
        self.assertEqual(response.status_code, 200)

    def test_delete_show(self):
        new_venue = Venue(name = 'test1', city='test1', state='CA', address='test', phone='123-123-1234', genres='Jazz', seeking_talent='False',facebook_link = "https://www.facebook.com/TheMusicalHop")
        new_venue.insert()
        new_venue_id = new_venue.id
        response = self.client().delete(f'/venues/{new_venue_id}/delete')
        self.assertEqual(response.status_code, 200)

if __name__ == "__main__":
    unittest.main()