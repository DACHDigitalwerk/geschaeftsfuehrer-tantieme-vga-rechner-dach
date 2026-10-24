# -*- coding: utf-8 -*-
"""
DACH Tantieme-, Geschäftsführer-Vergütung- & VGA-Rechner 2026
==============================================================

Open-Source Python Core Engine für die Angemessenheitsprüfung von 
Gesellschafter-Geschäftsführer-Bezügen, BFH 50%- und 75%-Deckelungen, 
Karlsruher Tabelle & BBE-Branchenbenchmarks sowie vGA-Steuernachzahlungs-
simulation nach § 8 Abs. 3 KStG (DE), § 8 Abs. 2 KStG (AT) und Art. 58 DBG (CH).

Entwickelt von DACH Digitalwerk (https://dachdigitalwerk.github.io).
"""

__version__ = "1.0.0"
__author__ = "DACH Digitalwerk"
__license__ = "MIT"

from .models import (
    Country,
    Industry,
    VGARiskLevel,
    CompanyProfile,
    GFProfile,
    AssessmentResult,
)
from .calculator import (
    calculate_bbe_benchmark_range,
    calculate_tantieme_amount,
    assess_bfh_50_rule,
    assess_bfh_75_rule,
    assess_formal_vga_criteria,
    assess_gf_compensation,
)
from .validator import (
    ValidationError,
    validate_company_profile,
    validate_gf_profile,
)

__all__ = [
    "Country",
    "Industry",
    "VGARiskLevel",
    "CompanyProfile",
    "GFProfile",
    "AssessmentResult",
    "calculate_bbe_benchmark_range",
    "calculate_tantieme_amount",
    "assess_bfh_50_rule",
    "assess_bfh_75_rule",
    "assess_formal_vga_criteria",
    "assess_gf_compensation",
    "ValidationError",
    "validate_company_profile",
    "validate_gf_profile",
]
