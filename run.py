import os
from app import create_app, db

config_key = os.environ.get("FLASK_CONFIG", "default")

app = create_app(config_key)

if __name__ == "__main__":
    port_num = os.environ.get("PORT", 8080)
    app.run(debug=True, port=port_num)