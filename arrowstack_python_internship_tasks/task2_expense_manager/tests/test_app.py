import pytest
from app import app, db, Expense, Budget

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            db.session.add(Budget(monthly_limit=500.00))
            db.session.commit()
        yield client

def test_index_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"Personal Expense & Budget Manager" in response.data

def test_add_expense(client):
    response = client.post('/add-expense', data={
        'title': 'Lunch',
        'amount': '15.50',
        'category': 'Food & Dining',
        'date': '2026-10-21'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Expense added successfully!" in response.data
    assert b"Lunch" in response.data

def test_update_budget(client):
    response = client.post('/update-budget', data={
        'monthly_limit': '2000.00'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Budget limit updated!" in response.data
