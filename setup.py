from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="roblox-dig-script",
    version="1.0.0",
    author="Simeon Milanov",
    author_email="simeonmlnv@outlook.com",
    description="Advanced auto-clicker with computer vision for Roblox digging minigames",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kokixzz/RobloxDigScript",
    project_urls={
        "Bug Tracker": "https://github.com/kokixzz/RobloxDigScript/issues",
        "Documentation": "https://github.com/kokixzz/RobloxDigScript#readme",
        "Source Code": "https://github.com/kokixzz/RobloxDigScript",
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Games/Entertainment",
        "Topic :: Scientific/Engineering :: Image Recognition",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: Microsoft :: Windows",
        "Environment :: Win32 (MS Windows)",
    ],
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "flake8>=3.8.0",
            "black>=21.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "roblox-dig-script=movement_clicker:main",
        ],
    },
    keywords=[
        "roblox", "auto-clicker", "computer-vision", "opencv", "gaming", 
        "automation", "minigame", "digging", "script", "bot"
    ],
    include_package_data=True,
    zip_safe=False,
) 