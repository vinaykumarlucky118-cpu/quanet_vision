import unittest
import sys
import os

# Add venv and root to path
app_dir = os.path.dirname(os.path.abspath(__file__))
venv_site = os.path.join(app_dir, '.venv', 'Lib', 'site-packages')
if venv_site not in sys.path:
    sys.path.insert(0, venv_site)
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)

if __name__ == '__main__':
    loader = unittest.TestLoader()
    suite = loader.discover('tests')
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
