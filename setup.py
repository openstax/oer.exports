from setuptools import setup, find_packages

install_requires = (
     'lxml',
     'argparse',
     'pillow',
     'numpy',
     'wand'
)

setup(
    name = "oer.exports",
    version = "0.1",
    packages = find_packages(),
    install_requires=install_requires,
    url="https://github.com/Connexions/oer.exports",
    entry_points={
        'console_scripts': [
            'collectiondbk2pdf = collectiondbk2pdf:main',
            'content2epub = content2epub:main'
        ],
    },
   test_suite = "tests"
)

