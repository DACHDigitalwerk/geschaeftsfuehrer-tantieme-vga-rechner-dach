# -*- coding: utf-8 -*-
import sys
import os

# Add package root to sys.path
package_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if package_root not in sys.path:
    sys.path.insert(0, package_root)
