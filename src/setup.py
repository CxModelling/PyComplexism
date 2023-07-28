import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


keywords = [
    "simulation",
    "probability theory",
    "Bayesian networks",
    "graph",
    "model fitting",
]


packages = [
    'pycx',
    'pycx.element',
    'pycx.dcore',
    'pycx.mcore',
    'pycx.misc'
]


setuptools.setup(
    name='pycx',
    version='0.1.0',
    author="Chu-Chang Ku",
    author_email='TimeWz667@gmail.com',
    description='Dynamic modelling toolkit',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/CxModelling/PyComplexism",
    project_urls={
        "Bug Tracker": "https://github.com/CxModelling/PyComplexism/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=packages,
    install_requires=['pandas', 'numpy', 'scipy', 'matplotlib',
                    'networkx', 'sims_pars'],
    python_requires=">=3.9",
)
