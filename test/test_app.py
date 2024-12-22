import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app_2 import app, signup, login, users, create_post, posts, add_comment, postsusers_collection, forum_posts_collection, comments_collection, users_collection, posts_collection, forum_posts, create_forum_post, add_forum_comment
import unittest
from flask import json
from unittest.mock import patch


class TestAuth(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        users_collection.delete_many({})  # Clear the database before each test

    def tearDown(self):
        users_collection.delete_many({})  # Clear the database after] each test

    def test_signup(self):
        response = self.app.post('/signup', data=dict(
            username='testuser',
            password='password'
        ))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Signup successful', response.data)
        self.assertIn('testuser', users)

    def test_login(self):
        signup('testuser2', 'password123')  # Pre-add a user
        response = self.app.post('/login', data=dict(
            username='testuser2',
            password='password123'
        ))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login successful', response.data)

    def test_login_failure(self):
        response = self.app.post('/login', data=dict(
            username='wronguser',
            password='wrongpassword'
        ))
        self.assertEqual(response.status_code, 401)
        self.assertIn(b'Invalid credentials', response.data)

class TestBlog(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        posts_collection.delete_many({})  # Clear the posts collection before each test

    def tearDown(self):
        posts_collection.delete_many({})  # Clear the posts collection after each test

    def test_create_post(self):
        response = self.app.post('/create_post', data=dict(
            title='My First Blog Post',
            content='This is the content of my first post.'
        ))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Post created successfully', response.data)
        self.assertEqual(posts[-1]['title'], 'My First Blog Post')

    def test_view_post(self):
        create_post('Sample Post', 'Sample content')  # Pre-create a post
        response = self.app.get('/post/1')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Sample Post', response.data)
        self.assertIn(b'Sample content', response.data)

    def test_add_comment(self):
        create_post('Another Post', 'Content here')
        response = self.app.post('/post/2/comment', data=dict(
            username='commenter',
            comment='Nice post!'
        ))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Comment added', response.data)
        self.assertEqual(posts[1]['comments'][-1]['comment'], 'Nice post!')

    def test_comment_failure(self):
        response = self.app.post('/post/999/comment', data=dict(
            username='user',
            comment='This should fail.'
        ))
        self.assertEqual(response.status_code, 404)
        self.assertIn(b'Post not found', response.data)

class TestForum(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        forum_posts_collection.delete_many({})  # Clear the forum posts collection before each test

    def tearDown(self):
        forum_posts_collection.delete_many({})  # Clear the forum posts collection after each test

    def test_create_forum_post(self):
        response = self.app.post('/create_forum_post', data=dict(
            title='My First Forum Post',
            content='This is the content of my first forum post.'
        ))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Post created successfully', response.data)
        self.assertEqual(forum_posts[-1]['title'], 'My First Forum Post')

    def test_view_forum_post(self):
        create_forum_post('Sample Forum Post', 'Sample content')  # Pre-create a forum post
        response = self.app.get('/forum_post/1')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Sample Forum Post', response.data)
        self.assertIn(b'Sample content', response.data)

    def test_add_forum_comment(self):
        create_forum_post('Another Forum Post', 'Content here')
        response = self.app.post('/forum_post/2/comment', data=dict(
            username='commenter',
            comment='Nice post!'
        ))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Comment added', response.data)
        self.assertEqual(forum_posts[1]['comments'][-1]['comment'], 'Nice post!')

    def test_comment_failure(self):
        response = self.app.post('/forum_post/999/comment', data=dict(
            username='user',
            comment='This should fail.'
        ))
        self.assertEqual(response.status_code, 404)
        self.assertIn(b'Post not found', response.data)

class TestUserSignupLogin(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        users_collection.delete_many({})

    def tearDown(self):
        users_collection.delete_many({})

    def test_signup_valid_user(self):
        response = self.app.post('/signup', data={
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'password123',
            'confirm-password': 'password123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertIn(b"Signup successful", response.data)

    def test_signup_existing_user(self):
        users_collection.insert_one({
            "username": "existinguser",
            "email": "existinguser@example.com",
            "password": "hashed_password"
        })
        response = self.app.post('/signup', data={
            'username': 'existinguser',
            'email': 'existinguser@example.com',
            'password': 'password123',
            'confirm-password': 'password123'
        })
        self.assertIn(b"Email is already registered", response.data)

    def test_signup_empty_fields(self):
        response = self.app.post('/signup', data={})
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"All fields are required", response.data)

    def test_signup_mismatched_passwords(self):
        response = self.app.post('/signup', data={
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'password123',
            'confirm-password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"Passwords do not match", response.data)

    def test_login_valid_user(self):
        users_collection.insert_one({
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "hashed_password"
        })
        response = self.app.post('/login', data={
            'email': 'testuser@example.com',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertIn(b"Login successful", response.data)

    def test_login_invalid_user(self):
        response = self.app.post('/login', data={
            'email': 'nonexistentuser@example.com',
            'password': 'wrongpassword'
        })
        self.assertIn(b"Invalid email or password", response.data)

class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        users_collection.delete_many({})
        posts_collection.delete_many({})

    def tearDown(self):
        users_collection.delete_many({})
        posts_collection.delete_many({})

    def test_insert_user(self):
        users_collection.insert_one({
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "hashed_password"
        })
        user = users_collection.find_one({"email": "testuser@example.com"})
        self.assertIsNotNone(user)
        self.assertEqual(user['username'], 'testuser')

    def test_insert_post(self):
        create_post('Test Post', 'This is a test post')
        post = posts_collection.find_one({"title": "Test Post"})
        self.assertIsNotNone(post)
        self.assertEqual(post['title'], 'Test Post')

    def test_delete_post(self):
        create_post('Post to Delete', 'This post will be deleted')
        post = posts_collection.find_one({"title": "Post to Delete"})
        post_id = post['_id']
        posts_collection.delete_one({'_id': post_id})
        post = posts_collection.find_one({"title": "Post to Delete"})
        self.assertIsNone(post)

if __name__ == "__main__":
    unittest.main()
