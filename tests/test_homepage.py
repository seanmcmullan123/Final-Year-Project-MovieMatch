import pytest
from flask import url_for
# Test 1.1 (Homepage loads)
def test_homepage_loads(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Welcome to MovieMatch" in response.data 
# Test 1.2 (Register button works)
def test_register_button_link(client):
    response = client.get("/")
    assert b'href="/register"' in response.data
# Test 1.3 (Login button works)
def test_login_button_link(client):
    response = client.get("/")
    assert b'href="/login"' in response.data
# PYTHONPATH=. pytest tests/test_homepage.py

