import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-123')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///expense_tracker.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)

class Budget(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    monthly_limit = db.Column(db.Float, nullable=False, default=1000.00)

@app.before_request
def create_tables():
    db.create_all()
    if not Budget.query.first():
        default_limit = float(os.getenv('DEFAULT_MONTHLY_BUDGET', '1000.00'))
        db.session.add(Budget(monthly_limit=default_limit))
        db.session.commit()

@app.route('/', methods=['GET'])
def index():
    expenses = Expense.query.order_by(Expense.date.desc()).all()
    budget = Budget.query.first()
    
    total_spent = sum(e.amount for e in expenses)
    remaining_budget = budget.monthly_limit - total_spent
    spent_percentage = min(100, (total_spent / budget.monthly_limit * 100)) if budget.monthly_limit > 0 else 0

    category_totals = {}
    for e in expenses:
        category_totals[e.category] = category_totals.get(e.category, 0) + e.amount

    return render_template(
        'index.html',
        expenses=expenses,
        monthly_limit=budget.monthly_limit,
        total_spent=total_spent,
        remaining_budget=remaining_budget,
        spent_percentage=round(spent_percentage, 1),
        category_totals=category_totals
    )

@app.route('/add-expense', methods=['POST'])
def add_expense():
    title = request.form.get('title')
    amount = request.form.get('amount')
    category = request.form.get('category')
    date_str = request.form.get('date')

    if not title or not amount or not category:
        flash('All fields are required!', 'error')
        return redirect(url_for('index'))

    try:
        expense_date = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else datetime.utcnow().date()
        new_expense = Expense(
            title=title.strip(),
            amount=float(amount),
            category=category.strip(),
            date=expense_date
        )
        db.session.add(new_expense)
        db.session.commit()
        flash('Expense added successfully!', 'success')
    except ValueError:
        flash('Invalid amount or date format!', 'error')

    return redirect(url_for('index'))

@app.route('/update-budget', methods=['POST'])
def update_budget():
    new_limit = request.form.get('monthly_limit')
    if new_limit:
        try:
            budget = Budget.query.first()
            budget.monthly_limit = float(new_limit)
            db.session.commit()
            flash('Budget limit updated!', 'success')
        except ValueError:
            flash('Invalid budget amount!', 'error')
    return redirect(url_for('index'))

@app.route('/delete-expense/<int:expense_id>', methods=['POST'])
def delete_expense(expense_id):
    expense = Expense.query.get_or_404(expense_id)
    db.session.delete(expense)
    db.session.commit()
    flash('Expense deleted!', 'info')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
