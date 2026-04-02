"""
quantiv — Quantitative Options Pricing Platform

This is the top-level package. Import pricing and analytics from here.

Usage:
    from quantiv.pricing import Pricer
    pricer = Pricer()
    result = pricer.price(model="bsm", spot=100, strike=100, vol=0.2,
                          rate=0.05, expiry=1.0, option_type="call")
"""

__version__ = "1.0.0"

import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# On Windows Python 3.8+, DLLs in the PATH are no longer automatically loaded.
# We must explicitly add the vcpkg /bin directory so _quantiv_engine can find pqxx.dll and libpq.dll.
if os.name == "nt" and sys.version_info >= (3, 8):
    vcpkg_bin = r"C:\vcpkg\installed\x64-windows\bin"
    if os.path.exists(vcpkg_bin):
        os.add_dll_directory(vcpkg_bin)
