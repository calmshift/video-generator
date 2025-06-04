#!/usr/bin/env python3
"""
Setup script for AI Video Creator.
"""

from setuptools import setup, find_packages
import os

# Read requirements from requirements.txt
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

# Read long description from README.md
with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="ai-video-creator",
    version="1.0.0",
    description="Create engaging videos with AI narration and dynamic subtitles",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="AI Video Creator Team",
    author_email="info@example.com",
    url="https://github.com/yourusername/ai-video-creator",
    packages=find_packages(),
    py_modules=["ai_video_creator"],
    install_requires=requirements,
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "ai-video-creator=ai_video_creator:main",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Multimedia :: Video",
        "Topic :: Multimedia :: Sound/Audio",
    ],
    keywords="video, ai, narration, subtitles, content creation",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/ai-video-creator/issues",
        "Source": "https://github.com/yourusername/ai-video-creator",
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.sh"],
    },
)