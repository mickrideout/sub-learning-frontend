# Sub Learning Frontend

This project is a web application for learning with subtitles.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

You need to have Python 3 and pip installed on your system.

### Installation

1.  Clone the repo
    ```sh
    git clone https://github.com/your_username_/sub-learning-frontend.git
    ```
2.  Install Python packages
    ```sh
    pip install -r requirements.txt
    ```

### Configuration

1.  Create a `.env` file in the root directory of the project.
2.  Copy the contents of `.env.example` to the new `.env` file.
3.  Update the values in the `.env` file with your own configuration.

### Database

To create the database, run the following command:

```sh
PYTHONPATH=. python scripts/init_db.py
```

To create the database with sample data, run:

```sh
PYTHONPATH=. python scripts/init_db.py --with-samples
```

When you change the database model, you need to create a migration script:

```sh
flask db migrate -m "Your migration message"
```

Then, apply the migration to the database:

```sh
flask db upgrade
```

## Usage

To run the application, execute the following command:

```sh
python run.py
```

The application will be available at `http://localhost:5000`.

## Testing

To run the tests, execute the following command:

```sh
pytest
```

## Built With

*   [Flask](https://flask.palletsprojects.com/) - The web framework used
*   [SQLAlchemy](https://www.sqlalchemy.org/) - The SQL toolkit and Object Relational Mapper
*   [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/) - Flask extension for SQLAlchemy
*   [Flask-Migrate](https://flask-migrate.readthedocs.io/) - SQLAlchemy database migrations for Flask applications
*   [Flask-Login](https://flask-login.readthedocs.io/) - Flask user session management
*   [Authlib](https://authlib.org/) - The ultimate Python library in building OAuth and OpenID Connect clients and providers.
*   [WTForms](https://wtforms.readthedocs.io/) - A flexible forms validation and rendering library for Python web development.
*   [pytest](https://docs.pytest.org/) - A framework that makes it easy to write small tests, yet scales to support complex functional testing.