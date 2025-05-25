from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="startpageapi",
    version="0.1.0",
    author="deepnor",
    author_email="nothellnor@gmail.com",
    description="The StartpageAPI is an unofficial Python library that facilitates access to search results from the Startpage.com engine.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/deepnor/startpageapi",
    project_urls={
        "Bug Tracker": "https://github.com/deepnor/startpageapi/issues",
        "Documentation": "https://github.com/deepnor/startpageapi",
        "Source Code": "https://github.com/deepnor/startpageapi",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Intended Audience :: Developers",
        "Development Status :: 4 - Beta",
    ],
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=[
        "beautifulsoup4",
        "lxml",
    ],
    keywords="search, startpage, api, web scraping, search engine",
)
