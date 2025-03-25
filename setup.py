#!/usr/bin/env python3
"""
Setup script for Arc LLM
"""

from setuptools import setup, find_packages

setup(
    name="arc-llm",
    version="0.1.0",
    description="A project that integrates Claude API with SpatialLM to convert text descriptions into 2D and 3D spatial representations",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/your-username/arc-llm",
    packages=find_packages(),
    install_requires=[
        "torch>=2.0.0",
        "numpy>=1.20.0",
        "scipy>=1.7.0",
        "einops>=0.6.0",
        "rerun-sdk>=0.10.0",
        "requests>=2.25.0",
        "torchsparse>=1.4.0",
    ],
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
