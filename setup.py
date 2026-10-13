from setuptools import setup

setup(
    name="StructPy",                           
    version="0.1.0",                           
    description="A Python-based tool for managing academic data projects.",  
    long_description=open("README.md").read(), 
    long_description_content_type="text/markdown",
    author="Edgar L Carrillo",                 
    author_email="edgarc.ec@gmail.com",        
    url="https://github.com/elcarrillo/StructPy",  
    license="MIT",                             
    package_dir={"": "src"},
    py_modules=["main", "core_features", "validate", "config_loader"],
    include_package_data=True,                 
    install_requires=[
        "pandas>=1.3.0",
        "pyyaml>=6.0",
        "pytest>=7.0.0",                       
        "setuptools>=65.0.0"
    ],
    entry_points={
        "console_scripts": [
            "structpy=main:main"  
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",  
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
    python_requires=">=3.8",                   
)
