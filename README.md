# PyCx

[![PyPI](https://img.shields.io/pypi/v/pycx.svg)][pypi status]
[![Status](https://img.shields.io/pypi/status/pycx.svg)][pypi status]
[![Python Version](https://img.shields.io/pypi/pyversions/pycx)][pypi status]
[![License](https://img.shields.io/pypi/l/pycx)][license]

[![Read the documentation at https://pycx.readthedocs.io/](https://img.shields.io/readthedocs/pycx/latest.svg?label=Read%20the%20Docs)][read the docs]
[![Tests](https://github.com/timewz667/pycx/workflows/Tests/badge.svg)][tests]
[![Codecov](https://codecov.io/gh/timewz667/pycx/branch/main/graph/badge.svg)][codecov]

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)][pre-commit]
[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)][black]

[pypi status]: https://pypi.org/project/pycx/
[read the docs]: https://pycx.readthedocs.io/
[tests]: https://github.com/timewz667/pycx/actions?workflow=Tests
[codecov]: https://app.codecov.io/gh/timewz667/pycx
[pre-commit]: https://github.com/pre-commit/pre-commit
[black]: https://github.com/psf/black

## Features
An agent-based modelling toolkit for various dynamic modelling and simulation. The package is essentially designed for epidemiologists and health economists. 

Ordinary Differential Equation models and State-Space Agent-Based models are two major and mature model types supported. PyComplexism also strongly supports the combination of models (hybrid modelling, metapopulation, and multi-scale modelling). 


### Backbone of PyComplexism
We use
- Bayesian Networks for parameter modelling.
- Contiuous-Time Bayesian Networks and Markov Chain for dynamics of agents' states. 
- Monte Carlo and Bayesian inference for post-modelling inference. 



## Requirements

- TODO

## Installation

You can install _PyCx_ via [pip] from [PyPI]:

```console
$ pip install pycx
```

## Usage

Please see the [Command-line Reference] for details.

## Contributing

Contributions are very welcome.
To learn more, see the [Contributor Guide].

## License

Distributed under the terms of the [MIT license][license],
_PyCx_ is free and open source software.

## Issues

If you encounter any problems,
please [file an issue] along with a detailed description.

## Credits

This project was generated from [@cjolowicz]'s [Hypermodern Python Cookiecutter] template.

[@cjolowicz]: https://github.com/cjolowicz
[pypi]: https://pypi.org/
[hypermodern python cookiecutter]: https://github.com/cjolowicz/cookiecutter-hypermodern-python
[file an issue]: https://github.com/timewz667/pycx/issues
[pip]: https://pip.pypa.io/

<!-- github-only -->

[license]: https://github.com/timewz667/pycx/blob/main/LICENSE
[contributor guide]: https://github.com/timewz667/pycx/blob/main/CONTRIBUTING.md
[command-line reference]: https://pycx.readthedocs.io/en/latest/usage.html
