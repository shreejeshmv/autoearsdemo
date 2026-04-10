from setuptools import setup, find_packages

setup(
    name="workspace",
    version="0.1.0",
    packages=find_packages(),
    install_requires=["flask>=3.0", "requests>=2.31"],
    extras_require={"test": ["pytest>=7.0"]},
)
