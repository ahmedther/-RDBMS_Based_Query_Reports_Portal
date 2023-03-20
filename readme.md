RDBMS Query Reports Portal

This is a web application that displays various reports used by different departments in a hospital, such as Pharmacy, Clinical Admin, Marketing, Discharge Billing, Radiology, etc. The reports are rights-based, meaning that users can only see reports that have been assigned to them by an admin.
Technologies Used

    Backend: Python, Django
    Frontend: JavaScript, CSS, HTML
    Databases: Oracle (for retrieving information from the Hospital Information System) and Postgres (for storing user data and website data)

Features

    User authentication and authorization using Django's built-in authentication system
    Admin panel for assigning access rights to different reports
    Querying data from the Hospital Information System using Oracle
    Displaying reports in a user-friendly manner using JavaScript, CSS, and HTML

Getting Started

To run this project on your local machine, you will need to have Python, Django, Oracle, and Postgres installed.

    Clone this repository to your local machine.
    Navigate to the root directory of the project in your terminal and run pip install -r requirements.txt to install the required dependencies.
    Set up the database by running the following commands in your terminal:

bash

python manage.py makemigrations
python manage.py migrate

    Start the development server by running python manage.py runserver in your terminal.
    Visit http://localhost:8000 in your web browser to view the website.

Contributing

This project is open to contributions. If you find a bug or have a suggestion for a new feature, please create a new issue or submit a pull request.
License
