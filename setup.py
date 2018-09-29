from setuptools import setup

setup(
    name="npcgen",
    version="0.1",
    author="JW",
    license="Whatever",
    packages=["npcgen"],
    install_requires=[],
    package_data={'npcgen': ['data/*.csv']}
)