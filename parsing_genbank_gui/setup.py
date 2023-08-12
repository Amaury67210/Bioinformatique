from setuptools import setup

setup(
    name='bio_inofrmatique_projet',
    version='1.2.5',
    packages=['src', 'src.utils'],
    author='Groupe SDSC',
    install_requires=[
        "pyqt5",
        "bio",
        "pandas",
        "setuptools",
        "gdown"
    ],
)
