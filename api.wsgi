import sys
import logging
logging.basicConfig(stream=sys.stderr)

# Add your project directory to the Python path
sys.path.insert(0, 'D:/Courses/AI Sprints/Capstone Project 2')

# Import your Flask app
from task7 import app as application