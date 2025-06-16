# 🛠️ conan-toolchains

This repository contains Conan recipes for toolchains and command line
utilities, for example the Emscripten SDK or other compilers. These recipes are
maintained independently of [Conan Center Index](https://github.com/conan-io/conan-center-index)
with flexible maintenance scopes.

---

## 🌟 Why a separate repo?

- **Different cadence**: Toolchains evolve separately from libraries (e.g., new compiler versions, SDK upgrades, experimental features).
- **Greater flexibility**: Easier to test, modify, or share alternative toolchain recipes without touching Conan Center.
- **Isolation from libraries**: Keeps toolchains out of library dependencies, avoiding unintended conflicts.

---

## 🚀 Getting started


### Setup `conan-toolchains` as a [local recipe index](https://docs.conan.io/2/devops/devops_local_recipes_index.html#devops-local-recipes-index) repository

Before adding `conan-toolchains` ensure [conan](https://github.com/conan-io/conan) is installed and available in your path.
Check conan [downloads](https://conan.io/downloads) page.

```sh
git clone https://github.com/conan-io/conan-toolchains.git
conan remote add conan-toolchains ./conan-toolchains
```

This repository is still under active development, and no Conan remote with pre-built binaries is available yet.


## Contributing


If you wish to contribute to **conan-toolchains**, follow these steps to clone the repository
and install the required development dependencies.

```
git clone git@github.com:conan-io/conan-toolchains.git
cd conan-toolchains
pip install pre-commit
```

We use [pre-commit](https://pre-commit.com/) to enforce code style and formatting. To
activate the pre-commit hooks:

```
pre-commit install
```

This will ensure that every time you commit changes, the code will be formatted and linted
according to the project's standards.
