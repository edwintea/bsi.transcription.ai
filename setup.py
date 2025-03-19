import sys
sys.setrecursionlimit(1500)  # Increase the recursion limit
from distutils.core import setup
import py2exe


setup(
    windows=['transcript_main.py'],
    options={
        'py2exe': {
            'bundle_files': 1,
            'compressed': True,
            'excludes': ['unwanted_module1', 'unwanted_module2'],  # Exclude any unnecessary modules
        }
    },
    zipfile=None,
    py_modules=['transcript_main', 'transcript'],  # Specify your modules
)