import os
import sys

# Add the root directory to the python path so Vercel can find `web_client.py`
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web_client import app
