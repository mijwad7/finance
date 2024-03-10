import os
import re

from sqlite3 import IntegrityError
from flask import Flask, flash, redirect, render_template, request, session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    user_id = session["user_id"]
    rows = db.execute(
        "SELECT symbol, SUM(shares) AS total_shares, SUM(cost) AS total_cost FROM stocks WHERE id = ? GROUP BY symbol", user_id)
    stocks = []
    total_value = 0
    for row in rows:
        symbol = row["symbol"]
        quote = lookup(symbol)
        name = quote['name']
        price = quote['price']
        shares = row["total_shares"]
        total = price * shares
        total_value += total
        stocks.append({"name": name, "price": price, "symbol": symbol, "total": total, "shares": shares})
    balance = db.execute("SELECT cash FROM users WHERE id = ?", user_id)[0]["cash"]
    cash = balance
    grand_total = cash + total_value

    return render_template("index.html", stocks=stocks, cash=cash, grand_total=grand_total)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":
        if not request.form.get("symbol"):
            return apology("must provide symbol", 400)
        shares = request.form.get("shares")
        if not shares.isdigit():
            return apology("invalid shares", 400)

        symbol = request.form.get("symbol")
        quote = lookup(symbol)
        if not lookup(symbol):
            return apology("invalid symbol", 400)

        price = quote['price']
        user_id = session["user_id"]
        cash = db.execute("SELECT cash FROM users WHERE id = ?", user_id)[0]["cash"]
        shares = int(shares)
        cost = price * shares
        if cost > cash:
            return apology("can't afford", 400)
        db.execute("INSERT INTO stocks (id, symbol, shares, cost) VALUES (?, ?, ?, ?)", user_id, symbol, shares, cost)
        db.execute("UPDATE users SET cash = cash - ? WHERE id = ?", cost, user_id)
        return redirect("/")
    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    user_id = session["user_id"]
    rows = db.execute(
        "SELECT symbol, SUM(shares) AS total_shares, SUM(cost) AS total_cost FROM stocks WHERE id = ? GROUP BY symbol", user_id)
    stocks = []
    total_value = 0
    for row in rows:
        symbol = row["symbol"]
        quote = lookup(symbol)
        name = quote['name']
        price = quote['price']
        shares = row["total_shares"]
        total = price * shares
        total_value += total
        stocks.append({"name": name, "price": price, "symbol": symbol, "total": total, "shares": shares})
    transacted = db.execute("SELECT transaction_date FROM transactions WHERE id = ?", user_id)[0]["transaction_date"]
    return render_template("history.html", stocks=stocks, transacted=transacted)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "POST":
        if not request.form.get("symbol"):
            return apology("must provide symbol", 400)
        symbol = request.form.get("symbol")
        quote = lookup(symbol)
        if not lookup(symbol):
            return apology("invalid symbol", 400)
        name = quote['name']
        price = quote['price']
        return render_template("quoted.html", name=name, price=price, symbol=symbol)

    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        if not request.form.get("username"):
            return apology("must provide username", 400)

        elif not request.form.get("password"):
            return apology("must provide password", 400)

        """personal touch: password strength check"""
        pattern = r"^(?=.*[0-9])(?=.*[!@#$%^&*])(?=.{8,})"
        if not re.search(pattern, request.form.get("password")):
            return apology("Password must be 8 characters long and contain at least one number and symbol", 400)

        elif not request.form.get("confirmation"):
            return apology("must provide password again", 400)

        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords don't match", 400)

        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        if len(rows) != 0:
            return apology("username already exists", 400)

        hash = generate_password_hash(request.form.get("password"))
        try:
            db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", request.form.get("username"), hash)
        except IntegrityError:
            return apology("username already exists", 400)

        return redirect("/")

    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == "POST":
        if not request.form.get("symbol"):
            return apology("must provide symbol", 400)
        sell_shares = request.form.get("shares")
        if not sell_shares.isdigit():
            return apology("invalid shares", 400)
        user_id = session["user_id"]
        rows = db.execute("SELECT symbol, SUM(shares) AS total_shares FROM stocks WHERE id = ? GROUP BY symbol", user_id)
        if rows[0]["total_shares"] < int(sell_shares):
            return apology("too many shares", 400)

        symbol = request.form.get("symbol")
        quote = lookup(symbol)
        if not lookup(symbol):
            return apology("invalid symbol", 400)

        price = quote['price']
        sell_shares = int(sell_shares)
        cost = price * sell_shares

        db.execute("UPDATE users SET cash = cash + ? WHERE id = ?", cost, user_id)
        db.execute("INSERT INTO transactions (id, symbol, shares, price, transaction_type) VALUES (?, ?, ?, ?, 'sell')",
                   user_id, symbol, -sell_shares, price)
        db.execute("UPDATE stocks SET shares = shares - ? WHERE symbol = ? AND id = ?", sell_shares, symbol, user_id)
        return redirect("/")

    else:
        user_id = session["user_id"]
        symbols = []
        rows = db.execute("SELECT symbol FROM stocks WHERE id = ? GROUP BY symbol", user_id)
        for row in rows:
            symbol = row["symbol"]
            symbols.append({"symbol": symbol})
        return render_template("sell.html", symbols=symbols)