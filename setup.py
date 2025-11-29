from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="accessiai",
    version="0.1.0",
    author="AccessiAI Team",
    description="AI-Powered Web Accessibility Enhancer",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "streamlit==1.28.1",
        "transformers==4.35.2",
        "torch==2.1.1",
        "beautifulsoup4==4.12.2",
        "webcolors==1.13",
        "pillow==10.1.0",
        "requests==2.31.0",
    ],
)
