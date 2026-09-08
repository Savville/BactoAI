"""
Gunicorn configuration for BactoAI on Render.
"""

import os

# Bind
bind = f"0.0.0.0:{os.environ.get('PORT', '10000')}"

# Workers
# Render free/starter tier: ~512MB RAM. The ML models are large,
# so 1 worker avoids OOM kills. Scale up if you upgrade the plan.
workers = 1

# Preload: load the app *shell* (routes, config, DB) in the master process
# before forking workers. Models are loaded in post_fork (below) so that
# gunicorn binds to the port BEFORE the slow model loading starts.
# This prevents Render from flagging "No open ports detected".
preload_app = True

# Timeouts
# Model loading can take 60-120 s on a cold Render instance.
# 300 s gives plenty of headroom without being dangerous.
timeout = 300
graceful_timeout = 30
keepalive = 5

# Logging
accesslog = "-"   # stdout (visible in Render logs)
errorlog = "-"    # stderr
loglevel = "info"


# =====================================================================
# Hooks
# =====================================================================

def post_fork(server, worker):
    """
    Called in each worker process after forking from the master.
    At this point gunicorn has already bound to $PORT, so Render can
    detect the port. We load the heavy ML models here rather than in
    create_app(), which means cold-start model loading happens AFTER
    the port is open — eliminating the "No open ports detected" error.
    """
    server.log.info(f"[post_fork] Worker {worker.pid}: loading prediction assets...")
    try:
        # Import here to avoid touching the model code in the master process
        from bactoai.models.prediction import load_prediction_assets

        # gunicorn stores the loaded WSGI callable on server.app after preload_app.
        # Unwrap any middleware layers to get the underlying Flask app object.
        app = server.app.callable
        while hasattr(app, "app"):
            app = app.app

        load_prediction_assets(app)
        server.log.info(f"[post_fork] Worker {worker.pid}: prediction assets loaded OK.")
    except Exception as exc:
        server.log.error(
            f"[post_fork] Worker {worker.pid}: failed to load prediction assets: {exc}",
            exc_info=True,
        )
        # Don't crash the worker — the predict route handles STARTUP_ERROR gracefully
