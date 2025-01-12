from flask import Flask
from selenium_endpoint import selenium_bp
from interact_endpoint import interact_bp
from file_system import file_system_bp
app = Flask(__name__)

app.register_blueprint(selenium_bp, url_prefix='/selenium')
app.register_blueprint(interact_bp, url_prefix='/tk')
app.register_blueprint(file_system_bp, url_prefix='/fs')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
