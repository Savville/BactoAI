"""
BactoAI Entry Point
====================
Run the BactoAI application.

Usage:
    python run.py              # Run in development mode
    python run.py --production # Run in production mode
    flask --app run.py run     # Run via Flask CLI
"""

import warnings
warnings.filterwarnings("ignore", category=UserWarning)


import os
import sys
from bactoai.app import create_app
from bactoai.config import config_map

# Determine environment
env = os.environ.get("FLASK_ENV", "development")
config_class = config_map.get(env, config_map["development"])

app = create_app(config_class=config_class)

# Load prediction assets here for local development.
# On Render/gunicorn, this is done in the post_fork hook instead,
# so the port is bound before the slow model loading begins.
if not app.config.get("SKIP_MODEL_LOADING"):
    from bactoai.models.prediction import load_prediction_assets
    with app.app_context():
        load_prediction_assets(app)


if __name__ == "__main__":
    debug = env == "development"
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=debug)

