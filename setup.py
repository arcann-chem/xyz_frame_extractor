from setuptools import setup, find_packages

setup(
    name="xyz_frame_extractor",
    version="0.2.0",
    author="cdavro",
    author_email="cdavro.arcann.yi9jv@eridanitech.com",
    description="to_do",
    url="https://github.com/arcann/xyz_frame_extractor",
    license="GNU Affero General Public License v3",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.6",
    install_requires=["numpy"],
)
