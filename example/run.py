from distance.distance import distance
from dotenv import load_dotenv
from flask import Flask

app = Flask(__name__)

load_dotenv()

# Регистрируем Blueprint
app.register_blueprint(distance, url_prefix="/distance")

if __name__ == "__main__":
    app.run(debug=True)
