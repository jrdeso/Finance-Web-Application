"""
This app.py is the driver for the Financial Analysis website

Created as final project for HarvardX CS50.

Sources:
CS50 Problem Set 9: created stock portfolio: https://cs50.harvard.edu/x/2023/psets/9/finance/

Notes:
- Not using cs50's SQL library:
    - https://docs.sqlalchemy.org/en/20/index.html
- For helper.py I used the helpers.py file used for problem set 9 as a resource for some functions as they can be used for similar
  functionality
    - (login_required, usd, spinoff of apology)

"""

from datetime import datetime
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from sqlalchemy import create_engine, Column, Integer, Text, text, Date, Float, ForeignKey, CheckConstraint
from sqlalchemy.orm import scoped_session, sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from helper import login_required, usd, hash_pwd, check_pwd_strength


app = Flask(__name__)

# Configure Jinja for usd (default format for applications expenses/income )
# Custom filter
app.jinja_env.filters["usd"] = usd

# Disable cachine of responses (easier for active development)
# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

DATABASE_URL = "sqlite:///financials.db" # Using local financials db
engine = create_engine(DATABASE_URL)

Base = declarative_base()

# Class representing users table
class User(Base):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True)
    username = Column(Text, unique=True)
    password = Column(Text)
    salt = Column(Text)
    name = Column(Text)

# Class representing transactions table (holds users income and expense transactions)
class Transactions(Base):
    __tablename__ = 'transactions'
    transaction_id = Column(Integer, primary_key=True)
    date = Column(Date)
    memo = Column(Text)
    amount = Column(Float)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    transaction_type = Column(Text, CheckConstraint('transaction_type IN ("income", "expense")'))
    user = relationship(User)


# Create a scoped session to manage database connections
db = scoped_session(sessionmaker(bind=engine))


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


"""
Home page
TODO: this page needs to generate a finance report: currently just welcomes user
"""
@app.route("/")
@login_required
def home():
    # Get transaction data for the current user
    user_id = session["user_id"]

    # Get the sort_by and sort_order parameters from the query string (default to date and ascending order)
    sort_by = request.args.get("sort_by", "date")
    sort_order = request.args.get("sort_order", "asc")

    # Define the allowed sorting options
    allowed_sort_options = ["date", "memo", "amount"]

    # Validate the sort_by parameter
    if sort_by not in allowed_sort_options:
        flash("Invalid sorting option. Defaulting to date.", "warning")
        sort_by = "date"

    # Toggle the sort order
    new_sort_order = "desc" if sort_order == "asc" else "asc"

    # Construct the SQL query based on the sort_by and sort_order parameters
    query = text(f"SELECT * FROM transactions WHERE user_id = :user_id ORDER BY {sort_by} {sort_order}")

    transaction_data = db.execute(query, {"user_id": user_id}).fetchall()

    return render_template("home.html", name=get_current_accnt_name(), transactions=transaction_data, sort_by=sort_by, sort_order=sort_order, new_sort_order=new_sort_order)


"""
Allows users to update their records of expense transactions and view their past ones

"""
@app.route("/expense", methods=["GET", "POST"])
@login_required
def expenses():
    if request.method == "POST":
        # Verify all data has been entered, if so collect all new data
        date_str = request.form.get("date")
        memo = request.form.get("memo")
        amount = request.form.get("amount")

        if not (date_str and memo and amount):
            flash("400 : All fields must be filled out", 'error')
            return render_template("expense.html")

        # Upload data to transactions table as an 'expense' type
        # Convert date string to datetime
        date = datetime.strptime(date_str, "%Y-%m-%d")

        user_id = session["user_id"]
        new_expense_entry = Transactions(date=date, memo=memo, amount=-float(amount), user_id=user_id, transaction_type='expense')
        db.add(new_expense_entry)
        db.commit()

        flash("Expense entry added successfully!", "success")

    # Sorting logic for GET requests
    if request.method == "GET":
        sort_by = request.args.get("sort_by", "date")
        sort_order = request.args.get("sort_order", "asc")

        # Validate sort_by parameter
        if sort_by not in ["date", "memo", "amount"]:
            flash("Invalid sort parameter", 'error')
            return render_template("expense.html")

        user_id = session["user_id"]
        expense_data = db.execute(
            text(f"SELECT * FROM transactions WHERE user_id = :user_id AND transaction_type = 'expense' ORDER BY {sort_by} {sort_order}"),
            {"user_id": user_id}
        ).fetchall()

        return render_template("expense.html", expenses=expense_data, sort_by=sort_by, sort_order=sort_order)

    # Get expense data for the current user
    user_id = session["user_id"]
    expense_data = db.execute(
        text("SELECT * FROM transactions WHERE user_id = :user_id AND transaction_type = 'expense'"),
        {"user_id": user_id}
    ).fetchall()

    return render_template("expense.html", expenses=expense_data)


"""
Allows users to update their records of income transactions and view their past ones

"""
@app.route("/income", methods=["GET", "POST"])
@login_required
def income():
    if request.method == "POST":
        # Verify all data has been entered, if so collect all new data
        date_str = request.form.get("date")
        memo = request.form.get("memo")
        amount = request.form.get("amount")

        if not (date_str and memo and amount):
            flash("400 : All fields must be filled out", 'error')
            return render_template("income.html")

        # Upload data to transactions table as an 'income' type
        # Convert date string to datetime
        date = datetime.strptime(date_str, "%Y-%m-%d")

        user_id = session["user_id"]
        new_income_entry = Transactions(date=date, memo=memo, amount=float(amount), user_id=user_id, transaction_type='income')
        db.add(new_income_entry)
        db.commit()

        flash("Income entry added successfully!", "success")

    # Sorting logic for GET requests
    if request.method == "GET":
        sort_by = request.args.get("sort_by", "date")
        sort_order = request.args.get("sort_order", "asc")

        # Validate sort_by parameter
        if sort_by not in ["date", "memo", "amount"]:
            flash("Invalid sort parameter", 'error')
            return render_template("income.html")

        user_id = session["user_id"]
        income_data = db.execute(
            text(f"SELECT * FROM transactions WHERE user_id = :user_id AND transaction_type = 'income' ORDER BY {sort_by} {sort_order}"),
            {"user_id": user_id}
        ).fetchall()

        return render_template("income.html", incomes=income_data, sort_by=sort_by, sort_order=sort_order)

    # Get income data for the current user
    user_id = session["user_id"]
    income_data = db.execute(
        text("SELECT * FROM transactions WHERE user_id = :user_id AND transaction_type = 'income'"),
        {"user_id": user_id}
    ).fetchall()

    return render_template("income.html", incomes=income_data)


"""
Settings page allows user various functionality to change account info
- change name of user
- change username
- change password
- delete account
"""
@app.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    if request.method == "POST":
        # Get the action from the form data
        action = request.form.get("action")

        if action == "change_name":
            # Handle user changing name
            new_name = request.form.get("newName")
            if not new_name:
                flash("400 : Must provide new name for account", 'error')
            else:
                # Update user's name in the database
                user = db.query(User).filter_by(user_id=session["user_id"]).first()
                user.name = new_name
                db.commit()
                flash("Name updated successfully!", "success")

        elif action == "change_password":
            # Handle password change request
            current_password = request.form.get("currentPassword")
            new_password = request.form.get("newPassword")
            confirm_new_password = request.form.get("confirmNewPassword")

            if not (current_password and new_password and confirm_new_password):
                flash("400 : All fields must be filled out", 'error')
            else:
                user = db.query(User).filter_by(user_id=session["user_id"]).first()

                if not (user and hash_pwd(current_password, user.salt)[0] == user.password):
                    flash("400 : You did not enter your current password correctly", 'error')
                elif not check_pwd_strength(new_password):
                    flash("400 : New password is not strong enough", 'error')
                elif new_password != confirm_new_password:
                    flash("400 : Passwords do not match, please try again", 'error')
                else:
                    # Update user's password in the database
                    hashed_pwd, salt = hash_pwd(new_password)
                    user.password = hashed_pwd
                    user.salt = salt
                    db.commit()
                    # Clear session and notify user to log in again
                    session.clear()
                    flash("Password updated successfully! Please log in again.", "success")
                    return render_template("login.html")


        elif action == "delete_account":
            # Handle account deletion
            user_id = session["user_id"]
            # Delete the user's account from the database
            db.query(User).filter_by(user_id=user_id).delete()
            db.commit()
            # Clear session and notify user of account deletion
            session.clear()
            flash("Your account has been deleted. We're sad to see you go!", "success")
            return render_template("login.html")

    # Render the settings page with the current account name
    return render_template("settings.html", name=get_current_accnt_name())


"""
Logs current user out of webpage, sourced from CS50 week 9 pset
https://cs50.harvard.edu/x/2023/psets/9/finance/
"""
@app.route("/logout")
def logout():
    """Log user out"""
    # Forget any user_id
    session.clear()
    # Redirect user to login form
    return redirect("/")

"""
Register allows users to make a new account
They need to register with a name, username (unique from those existing) and pwd
The system then creates a salt and stores their data in the users table within the financials database
"""
@app.route("/register", methods=["GET", "POST"])
def register():
    session.clear()

    if request.method == "POST":
        # Form validation
        required_fields = ["name", "username", "password", "confirmation"]
        for field in required_fields:
            if not request.form.get(field):
                flash(f"400 : Must provide {field} for account", 'error')
                return render_template("register.html")

        # Store form data
        name = request.form.get("name")
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Check if username exists
        if db.query(User).filter_by(username=username).first():
            flash("400 : Username already exists, Choose a different username", 'error')
            return render_template("register.html")

        # Check password strength
        if not check_pwd_strength(password):
            flash("400 : Password is not strong enough", 'error')
            return render_template("register.html")

        # Check password confirmation
        if password != confirmation:
            flash("400 : Passwords do not match, please try again", 'error')
            return render_template("register.html")

        # If here -> new user has met registration requirements and we can make their account
        # hash password
        hashed_pwd, salt = hash_pwd(password)

        # Store account information in users table (name, username, password (hashed), salt)
        # Make a new user and commit to db
        new_user = User(username=username, password=hashed_pwd, name=name, salt=salt)
        db.add(new_user)
        db.commit()

        # Redirect user to home page afterwards (upon valid registration)
        return redirect("/")

    else:
        return render_template("register.html")


"""
Function for a user logging into their account

"""
@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()

    if request.method == "POST":
        # Form validation
        required_fields = ["username", "password"]
        for field in required_fields:
            if not request.form.get(field):
                flash(f"403 : Must provide {field}", 'error')
                return render_template("login.html")

        # Store form data
        username = request.form.get("username")
        password = request.form.get("password")

        # Get user information from the database based on the given username
        user = db.query(User).filter_by(username=username).first()

        # Validate username and password
        if user and hash_pwd(password, user.salt)[0] == user.password:
            # Successful login, store user_id in session and redirect to home page
            session["user_id"] = user.user_id
            return redirect("/")

        else:
            flash("403 : Invalid username or password", 'error')
            return render_template("login.html")

    else:
        return render_template("login.html")


"""
Function returns the name of user currently signed in:
@return name of user
"""
def get_current_accnt_name():
    # Get current's user's name
    user = db.query(User).filter_by(user_id=session["user_id"]).first()
    name = user.name

    return name
