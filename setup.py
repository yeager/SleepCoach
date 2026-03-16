from setuptools import setup, find_packages
setup(
    name="sleepcoach",
    version="0.2.0",
    packages=find_packages(),
    entry_points={"console_scripts": ["sleepcoach=sleepcoach.__main__:main"]},
    install_requires=["PyGObject"],
)
