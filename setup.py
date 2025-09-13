try:
    from setuptools import setup
except:
    from distutils.core import setup

config = {
    'description': 'An extension of the Tiferet Framework for the Flask API.',
    'author': 'Andrew Shatz, Great Strength Systems',
    'url': r'https://github.com/greatstrength/tiferet-flask',
    'download_url': r'https://github.com/greatstrength/app',
    'author_email': 'andrew@greatstrength.me',
    'version': '1.0.0',
    'license': 'BSD 3',
    'install_requires': [
        'tiferet>=1.1.1',
        'flask>=3.1.2',
    ],
    'packages': [
        'tiferet_flask',
        'tiferet_flask.commands',
        'tiferet_flask.configs',
        'tiferet_flask.contexts',
        'tiferet_flask.contracts',
        'tiferet_flask.data',
        'tiferet_flask.handlers',
        'tiferet_flask.models',
        'tiferet_flask.proxies',
        'tiferet_flask.proxies.yaml',
    ],    
    'scripts': [],
    'name': 'tiferet_flask',
    'extras_require': {
        'test': ['pytest>=8.3.3', 'pytest_env>=1.1.5'],
    }
}

setup(**config)