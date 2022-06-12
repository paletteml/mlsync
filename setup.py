from setuptools import setup, find_packages

with open('README.md') as f:
    long_description = f.read()

setup(
    name='mlsync',
    version='0.1.3',
    description='Sync your machine learning data to your favorite productivity tools',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/paletteml/mlsync',
    author='Andre Terron and Kartik Hegde',
    author_email='support@paletteml.com',
    license='Apache 2.0',
    packages=find_packages(include=['mlsync', 'mlsync.*']),
    install_requires=[
        'inquirer>=2.9.2',
        'notion_client>=1.0.0',
        'python-dotenv>=0.20.0',
        'PyYAML>=6.0',
        'requests>=2.22.0',
    ],
    entry_points = {
        'console_scripts': ['mlsync=mlsync.command_line:main'],
    }
)