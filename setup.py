from setuptools import setup, find_packages

setup(
    name="videomaker",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.104.1",
        "uvicorn>=0.24.0",
        "python-multipart>=0.0.6",
        "pydantic>=2.5.2",
        "aiofiles>=23.2.1",
        "python-dotenv>=1.0.0",
        "moviepy>=1.0.3",
        "pillow>=10.0.0",
        "numpy>=1.24.0",
        "opencv-python>=4.8.0",
        "pathlib>=1.0.1"
    ]
)
