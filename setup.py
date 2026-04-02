"""
setup.py — Builds the C++ extension via CMake and installs the Python package.

Usage:
    pip install -e .        # editable install (development)
    pip install .           # standard install
"""

import os
import sys
import subprocess
from pathlib import Path

from setuptools import setup, Extension, find_packages
from setuptools.command.build_ext import build_ext


class CMakeExtension(Extension):
    """A setuptools Extension that delegates to CMake."""

    def __init__(self, name: str, sourcedir: str = "") -> None:
        super().__init__(name, sources=[])
        self.sourcedir = os.fspath(Path(sourcedir).resolve())


class CMakeBuild(build_ext):
    """Custom build_ext that invokes CMake."""

    def build_extension(self, ext: CMakeExtension) -> None:
        ext_fullpath = Path.cwd() / self.get_ext_fullpath(ext.name)
        extdir = ext_fullpath.parent.resolve()

        import pybind11
        pybind11_dir = pybind11.get_cmake_dir().replace("\\", "/")
        cmake_args = [
            f"-DCMAKE_LIBRARY_OUTPUT_DIRECTORY={extdir}{os.sep}",
            f"-DPYTHON_EXECUTABLE={sys.executable}",
            f"-Dpybind11_DIR={pybind11_dir}",
            "-DBUILD_TESTS=OFF",
            "-DBUILD_BINDINGS=ON",
        ]

        cfg = "Debug" if self.debug else "Release"
        build_args = ["--config", cfg]
        if "CMAKE_TOOLCHAIN_FILE" in os.environ:
            cmake_args.append(f"-DCMAKE_TOOLCHAIN_FILE={os.environ['CMAKE_TOOLCHAIN_FILE']}")
        elif sys.platform == "win32" and os.path.exists("C:/vcpkg/scripts/buildsystems/vcpkg.cmake"):
            cmake_args.append("-DCMAKE_TOOLCHAIN_FILE=C:/vcpkg/scripts/buildsystems/vcpkg.cmake")
        cmake_args += [
            f"-DCMAKE_BUILD_TYPE={cfg}",
            f"-DCMAKE_LIBRARY_OUTPUT_DIRECTORY_{cfg.upper()}={extdir}{os.sep}"
        ]

        build_temp = Path(self.build_temp) / ext.name
        build_temp.mkdir(parents=True, exist_ok=True)

        subprocess.run(
            ["cmake", ext.sourcedir, *cmake_args],
            cwd=build_temp,
            check=True,
        )
        subprocess.run(
            ["cmake", "--build", ".", *build_args],
            cwd=build_temp,
            check=True,
        )


setup(
    name="quantiv",
    version="1.0.0",
    author="Quantiv Team",
    description="Quantitative Options Pricing Platform",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=["tests*", "dashboard*", "docs*"]),
    ext_modules=[CMakeExtension("quantiv._quantiv_engine")],
    cmdclass={"build_ext": CMakeBuild},
    python_requires=">=3.10",
    install_requires=[
        "numpy>=1.24",
        "scipy>=1.10",
        "pandas>=2.0",
        "plotly>=5.15",
        "dash>=2.14",
        "dash-bootstrap-components>=1.5",
        "yfinance>=0.2.36",
        "python-dotenv>=1.0.0",
        "gunicorn>=21.2.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "black>=23.0",
            "mypy>=1.0",
            "ruff>=0.1",
        ],
    },
    zip_safe=False,
)
