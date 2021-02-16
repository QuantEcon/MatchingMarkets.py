from setuptools import setup, find_packages

setup(
    name="matchingmarkeets",
    version="0.1.0",
    license='BSD-3',
    description='Matching Market Simulations',
    author='Matt Ranger',
    url='https://github.com/QuantEcon/MatchingMarkets.py',
    packages=find_packages(),
    keywords=['graph', 'network', 'matching'],
    package_data={
        # If any package contains *.txt or *.rst files, include them:
        '': ['*.md', '*.txt', '*.rst']
    },
    install_requires=[
        'matplotlib',
        'networkx',
        'numpy',
        'pandas',
        'scipy',
    ],
)