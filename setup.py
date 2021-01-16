from setuptools import setup, find_packages

requirements = (
    'boto3',
    'colorama',
    'pyYaml',
)

tests_requirements = (
    'flake8',
    'coverage',
    'moto==1.3.14',
    'pyfakefs',
    'pytest',
    'pytest-cov'
)

with open('README.md') as file:
    readme = file.read()


setup(
    name='cabinets',
    version='0.1.1',
    description="A consistent approach to file operations, anywhere.",
    long_description=readme,
    long_description_content_type='text/markdown',
    author="Lucas Lofaro, Sam Hollenbach",
    author_email="lucasmlofaro@gmail.com, samhollenbach@gmail.com",
    url='https://github.com/lucasmlofaro/cabinets',
    packages=find_packages(exclude=['test']),
    install_requires=requirements,
    tests_require=tests_requirements,
    extras_require={'test': tests_requirements},
)
