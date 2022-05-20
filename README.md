<h1 align="center">
  <b>SciBench</b>
</h1>

<p align="center">
  <a href="https://pypi.org/project/scibench">
    <img alt="PyPI" src="https://img.shields.io/pypi/v/scibench">
  </a>
  <a href="https://pypi.org/project/scibench">
    <img alt="PyPI - Python Version" src="https://img.shields.io/pypi/pyversions/scibench" />
  </a>
  <a href="">
    <img alt="PyPI - Status" src="https://img.shields.io/pypi/status/scibench" />
  </a>
  <a href="">
    <img alt="PyPI - Implementation" src="https://img.shields.io/pypi/implementation/scibench">
  </a>
  <a href="">
    <img alt="PyPI - Wheel" src="https://img.shields.io/pypi/wheel/scibench">
  </a>
  <a href="https://github.com/marcofavorito/scibench/blob/master/LICENSE">
    <img alt="GitHub" src="https://img.shields.io/github/license/marcofavorito/scibench">
  </a>
</p>
<p align="center">
  <a href="">
    <img alt="test" src="https://github.com/marcofavorito/scibench/workflows/test/badge.svg">
  </a>
  <a href="">
    <img alt="lint" src="https://github.com/marcofavorito/scibench/workflows/lint/badge.svg">
  </a>
  <a href="">
    <img alt="docs" src="https://github.com/marcofavorito/scibench/workflows/docs/badge.svg">
  </a>
  <a href="https://codecov.io/gh/marcofavorito/scibench">
    <img alt="codecov" src="https://codecov.io/gh/marcofavorito/scibench/branch/master/graph/badge.svg?token=FG3ATGP5P5">
  </a>
</p>


Experimental general-purpose benchmarking framework for research.

## Install

To install from GitHub:
```
pip install git+https://github.com/marcofavorito/scibench.git
```

## Tests

To run tests: `tox`

To run only the code tests: `tox -e py3.7`

To run only the linters: 
- `tox -e flake8`
- `tox -e mypy`
- `tox -e black-check`
- `tox -e isort-check`

Please look at the `tox.ini` file for the full list of supported commands. 

## Docs

To build the docs: `mkdocs build`

To view documentation in a browser: `mkdocs serve`
and then go to [http://localhost:8000](http://localhost:8000)

## License

scibench is released under the GNU Lesser General Public License v3.0 or later (LGPLv3+).

Copyright 2022 Marco Favorito

## Authors

- [Marco Favorito](https://marcofavorito.me/)
