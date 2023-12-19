# Financial Analysis Web App
#### Video Demo:  <https://youtu.be/-vcIoytb3DE>


## Overview

The Financial Analysis Web App is a web application developed as the final project for HarvardX CS50. It provides users with a platform to manage their financial transactions, and track expenses and income. Built on the Flask web framework with SQLAlchemy for database interaction, the app offers a user-friendly interface and robust functionality.

## Core Functionality

### User Authentication and Registration

Users can create accounts by registering with a unique username, providing a name, and setting a secure password. The application employs session-based authentication to manage user logins securely.

### Transaction Management

The app allows users to log both expense and income transactions. Transactions are recorded with details such as date, memo, amount, and transaction type. Users can view and manage their transaction history conveniently through the web interface.

### Dynamic Sorting

Transactions can be dynamically sorted based on different parameters such as date, memo, and amount. This feature enhances user experience and provides flexibility in reviewing financial data.

### Settings

The settings page allows users to customize their account information. Users can change their name, update their username, and modify their password. Additionally, there is an option to delete the user's account.

### Robust Password Security

The application incorporates robust password security measures. Passwords are hashed and stored securely, and there are checks for password strength during registration and password change.

## Design Decisions

### Database Structure

The app utilizes an SQLite database named "financials.db." Two main tables, `users` and `transactions`, store user information and financial transactions, respectively. SQLAlchemy's declarative approach simplifies database interactions.

### Flask Framework

Flask was chosen as the web framework due to its simplicity, flexibility, and ease of integration with SQLAlchemy. The lightweight nature of Flask makes it well-suited for this project.

### Dynamic Templating

HTML templates are employed to dynamically render content based on user interactions. This design choice enhances the user interface and provides a seamless experience.

### Session Management

Flask-Session is used for session management, ensuring that user authentication and authorization are handled securely. This contributes to the overall robustness of the application.

## Getting Started

To run the Financial Analysis Web App locally, follow these steps:

1. Clone the repository.
2. Install the required dependencies using `pip install -r requirements.txt`.
4. Run the application with `flask run` while in the project directory.

Visit `http://localhost:5000` in your web browser to access the application.

## Contributors

This project was developed as part of HarvardX CS50 by Jordan Deso.


