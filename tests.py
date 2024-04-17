import unittest
from unittest.mock import patch
import os
import sqlite3

# Assuming api.py is in the same directory
from api import Api

class TestApi(unittest.TestCase):

    def setUp(self):
        # Create a mock user ID and set environment variable
        self.user_id = "12345"
        os.environ["TOKEN"] = "mock_token"
        self.api = Api(self.user_id)

    def tearDown(self):
        # Clean up database after each test
        try:
            os.remove("user.db")
        except FileNotFoundError:
            pass

    @patch('requests.get')
    def test_vk_user_info_success(self, mock_get):
        # Mock successful response from API
        mock_response = {
            "response": [{
                "id": self.user_id,
                "sex": 1,
                "bdate": "01.01.2000",
                "city": {"title": "Moscow"},
                "university_name": "University"
            }]
        }
        mock_get.return_value.json.return_value = mock_response

        # Call the function
        self.api.vk_user_info()

        # Check if data is inserted into database
        with sqlite3.connect("user.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE id=?", (self.user_id,))
            user_data = cursor.fetchone()
            self.assertEqual(user_data[0], int(self.user_id))
            self.assertEqual(user_data[1], 1)
            self.assertEqual(user_data[2], "01.01.2000")
            self.assertEqual(user_data[3], "Moscow")
            self.assertEqual(user_data[4], "University")

    @patch('requests.get')
    def test_vk_user_info_missing_data(self, mock_get):
        # Mock response with missing data
        mock_response = {
            "response": [{
                "id": self.user_id,
                "sex": 2
            }]
        }
        mock_get.return_value.json.return_value = mock_response

        # Call the function
        self.api.vk_user_info()

        # Check if missing data is handled correctly
        with sqlite3.connect("user.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE id=?", (self.user_id,))
            user_data = cursor.fetchone()
            self.assertEqual(user_data[0], int(self.user_id))
            self.assertEqual(user_data[1], 2)
            self.assertIsNone(user_data[2])
            self.assertIsNone(user_data[3])
            self.assertIsNone(user_data[4])

    # Add tests for other functions similarly (vk_wall_posts, vk_posts_exporter)

if __name__ == '__main__':
    unittest.main()