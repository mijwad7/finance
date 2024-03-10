# Finance Web Application

This repository contains the implementation of a finance web application built using Flask, HTML, and SQLite. The application allows users to register for an account, log in, buy and sell stocks, view their transaction history, and check their current portfolio.

## Project Structure

- **app.py**: This file contains the main Flask application. It includes routes for registering, logging in, buying and selling stocks, viewing portfolio and transaction history, as well as helper functions for user authentication and stock lookup.

- **helpers.py**: This file contains helper functions used by the Flask application. It includes functions for rendering apologies, checking if a user is logged in, and formatting stock prices.

- **requirements.txt**: This file lists all the Python packages required to run the application. You can install these packages using `pip install -r requirements.txt`.

- **static/**: This directory contains static assets such as CSS stylesheets.

- **templates/**: This directory contains HTML templates for rendering different pages of the application, including login, registration, buying and selling stocks, viewing portfolio, and transaction history.

- **finance.db**: This SQLite database file stores user information, stock transactions, and portfolio details.

## Usage

To run the application locally:

1. Clone this repository to your local machine.
2. Install the required Python packages using `pip install -r requirements.txt`.
3. Run the Flask application by executing `python app.py` in your terminal.
4. Access the application in your web browser by navigating to `http://localhost:5000`.

## Features

- **Registration**: Users can register for an account by providing a username and password. Passwords are hashed before storing them in the database for security.

- **Login**: Registered users can log in to their accounts using their username and password.

- **Buy Stocks**: Users can search for stocks by their symbol and buy shares of the desired stock. The application checks the user's available balance before completing the purchase.

- **Sell Stocks**: Users can sell shares of stocks they own. The application verifies that the user owns enough shares before completing the sale.

- **View Portfolio**: Users can view their current portfolio, including the stocks they own, the number of shares for each stock, the current price of each stock, and the total value of each holding.

- **Transaction History**: Users can view their transaction history, which includes all buy and sell transactions they have made.

## Dependencies

- Python 3
- Flask
- CS50 SQL Module
- SQLite
