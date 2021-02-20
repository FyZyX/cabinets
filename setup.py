from setuptools import setup, find_packages

requirements = (
    'boto3',
    'colorama',
    'pyYaml',
)

tests_requirements = (
    'moto==1.3.14',
    'pyfakefs',
    'pytest',
    'pytest-cov'
)

with open('README.md') as file:
    readme = file.read()

setup(
    name='cabinets',
    version='0.6.0',
    description="A consistent approach to file operations, anywhere.",
    long_description=readme,
    long_description_content_type='text/markdown',
    author="Lucas Lofaro, Sam Hollenbach",
    author_email="lucasmlofaro@gmail.com, samhollenbach@gmail.com",
    url='https://github.com/lucasmlofaro/cabinets',
    packages=find_packages(exclude=['test']),
    classifiers=(
        "Development Status :: 4 - Beta",
        "Framework :: Pytest",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ),
    license='GNU GPLv3+',
    python_requires='>=3.6',
    install_requires=requirements,
    tests_require=tests_requirements,
    extras_require={'test': tests_requirements},
)
