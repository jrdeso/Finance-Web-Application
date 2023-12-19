import re
import hashlib
import os
from flask import redirect, session
from functools import wraps


"""
This function was sourced from CS50 problem set 9
https://cs50.harvard.edu/x/2023/psets/9/finance/

It is used to ensure users are logged in before accessing web functions
"""
def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


"""
return amount given formatted as USD
This function was sourced from CS50 Problem set 9
https://cs50.harvard.edu/x/2023/psets/9/finance/

@param amount: amount of money
@return amount formmatedd in USD currency
"""
def usd(amount):
    return f"${amount:,.2f}"


"""
This function validates whether a given password is strong enough
Requirements:
- 1+ capital letter
- 1+ lowercase letter
- 1+ digit
- 1+ symbol (?, !, #, $, &, @)
- length between 8 and 16 characters (inclusive)

@param password : password to test
@return true:   if pwd strong enough
        false: pwd not strong enough
"""
def check_pwd_strength(password):
        # Reg expression to verify strength of pwd defined above:
        pattern = re.compile(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[?!,#$&@])\S{8,16}$')
        if not pattern.match(password):
            return False
        else:
            return True


"""
Hashes given password to:
1. store initial registered password for new account
2. verify login and compare with usernames hashed pwd

Uses the SHA-256 hash algorithm
Uses a 16 byte salt

@param password : plaintext password to hash
@param salt : Login: Stored salt from users table
              Register: salt = None by default -> Generate new salt for new account
@return hashed_password, salt
"""
def hash_pwd(password, salt=None):
    # New user, make new salt
    if salt is None:
        salt = os.urandom(16)

    # Concatenate salt and plaintext pwd passed along
    salted_plaintext = salt + password.encode('utf-8')

    hashed_password = hashlib.sha256(salted_plaintext).hexdigest()

    return hashed_password, salt
