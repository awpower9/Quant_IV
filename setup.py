"""
setup.py — Installs the Python package and generates gRPC stubs.
"""
import os
import subprocess
from setuptools import setup, find_packages
from setuptools.command.build_py import build_py

class BuildPyCommand(build_py):
    """Custom build command to generate gRPC stubs before package installation."""
    def run(self):
        # Generate gRPC stubs
        print("Generating gRPC stubs from proto file...")
        proto_file = "quantiv.proto"
        out_dir = "quantiv"
        os.makedirs(out_dir, exist_ok=True)
        # Using python -m grpc_tools.protoc
        subprocess.check_call([
            "python", "-m", "grpc_tools.protoc",
            f"-I.",
            f"--python_out={out_dir}",
            f"--grpc_python_out={out_dir}",
            proto_file
        ])
        
        # Ensure __init__.py exists in the quantiv folder
        init_file = os.path.join(out_dir, "__init__.py")
        if not os.path.exists(init_file):
            with open(init_file, "w") as f:
                pass
                
        # Run standard build_py
        super().run()

setup(
    name="quantiv",
    version="1.0.0",
    author="Quantiv Team",
    description="Quantitative Options Pricing Platform - gRPC Client",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=["tests*", "dashboard*", "docs*"]),
    cmdclass={"build_py": BuildPyCommand},
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
        "grpcio>=1.50",
        "grpcio-tools>=1.50",
        "protobuf>=4.21",
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
