from setuptools import setup

setup(
    name='shoppingtracker',
    version='0.1',
    description='Tracks pantry stock',
    author='Trevor Peacock',
    author_email='trevorp@peacocktec.com',
    packages=[
        'shoppingtracker',
        'shoppingtracker.db',
        'shoppingtracker.db.migrations',
    ],
    scripts=[
        'run.py',
    ],
    package_data={
        'shoppingtracker': ['icon.png', 'bell.wav', 'woosh.wav']
    },
)
