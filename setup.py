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


def get_long_description(filename='README.md'):
    with open(filename) as file:
        readme = file.read()
    return readme


setup(
    name='cabinets',
    version='0.1.0',
    description="A consistent approach to file operations, anywhere.",
    long_description=get_long_description(),
    long_description_content_type='text/markdown',
    author="Lucas Lofaro, Sam Hollenbach",
    author_email="lucasmlofaro@gmail.com, samhollenbach@gmail.com",
    url='https://github.com/lucasmlofaro/cabinets',
    packages=find_packages(exclude=['test']),
    install_requires=requirements,
    tests_require=tests_requirements,
    extras_require={'test': tests_requirements},
)
