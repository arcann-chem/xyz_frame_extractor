from setuptools import setup, find_packages

setup(
    name="xyz_frame_extractor",
    version="1.0.1",
    author="Rolf David",
    author_email="cdavro.arcann.yi9jv@eridanitech.com",
    description="",
    url="https://github.com/arcann/xyz_frame_extractor",
    license="GNU Affero General Public License v3",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=["numpy>=1.17.3"],
)