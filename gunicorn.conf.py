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

# Preload: load the app (and all ML models) in the master process
# before forking workers. This means models load once, not once per
# worker, and the workers start up fast after the master is ready.
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
