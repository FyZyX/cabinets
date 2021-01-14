from setuptools import setup, find_packages

tests_require = [
    'flake8',
    'coverage',
    'moto==1.3.14',
    'pyfakefs',
    'pytest',
    'pytest-cov'
]

setup(
    name='cabinets',
    version='0.1.0',
    description="Place to store many things.",
    author="Lucas Lofaro, Sam Hollenbach",
    author_email="lucasmlofaro@gmail.com, samhollenbach@gmail.com",
    packages=find_packages(exclude=['test', 'test_*', 'fixtures']),
    install_requires=[
        'boto3',
        'colorama',
        'pyYaml',
    ],
    tests_require=tests_require,
    extras_require={'test': tests_require},
)
