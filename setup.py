from setuptools import setup, find_packages

setup(
    name="npcgen",
    version="0.1",
    author="JW",
    license="MIT",
    packages=find_packages(exclude=['tests*']),
    install_requires=[],
    include_package_data=True,
    package_data={'npcgen': ['npcgen/data/*.csv'],
                  '': ['*.csv']},
    url='https://github.com/FriendGaru/npcgen',
)