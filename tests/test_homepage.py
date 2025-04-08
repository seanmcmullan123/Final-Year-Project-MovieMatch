import pytest
from flask import url_for

def test_homepage_loads(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Welcome to MovieMatch" in response.data  # Adjust based on your actual homepage title

def test_register_button_link(client):
    response = client.get("/")
    assert b'href="/register"' in response.data  # Ensures there's a link to /register

def test_login_button_link(client):
    response = client.get("/")
    assert b'href="/login"' in response.data  # Ensures there's a link to /login




# PYTHONPATH=. pytest tests/test_homepage.py



#ALL PASSED LETS GOOOO