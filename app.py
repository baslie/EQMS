from eqms import create_app
import os


if __name__ == '__main__':
    database_url = os.getenv('DATABASE_URL')
    app = create_app(database_url)
    app.run(debug=True)
