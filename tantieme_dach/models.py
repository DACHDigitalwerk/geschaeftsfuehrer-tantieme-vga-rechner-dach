# -*- coding: utf-8 -*-
"""
Data models and enumerations for DACH GF Tantieme & vGA Calculator.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class Country(str, Enum):
    DE = "DE"
    AT = "AT"
    CH = "CH"


class Industry(str, Enum):
    IT_TECH = "it_tech"
    SERVICES = "services"
    COMMERCE = "commerce"
    MANUFACTURING = "manufacturing"
    CONSTRUCTION = "construction"
    OTHER = "other"


class VGARiskLevel(str, Enum):
    LOW_GREEN = "LOW_GREEN"
    MEDIUM_YELLOW = "MEDIUM_YELLOW"
    HIGH_RED = "HIGH_RED"


@dataclass
class CompanyProfile:
    annual_revenue: float
    employee_count: int
    pretax_profit_before_tantieme: float
    industry: Industry = Industry.SERVICES
    country: Country = Country.DE
    equity_capital: float = 0.0
    target_min_return_on_equity: float = 0.08  # 8% standard minimum return on equity


@dataclass
class GFProfile:
    name: str = "Geschäftsführer"
    base_salary: float = 120000.0  # Annual fixed gross salary
    tantieme_rate_percent: float = 10.0  # e.g., 10%
    agreed_tantieme_fixed: Optional[float] = None  # Optional fixed tantieme if not percentage
    share_percentage: float = 60.0  # Ownership % (>= 50% => controlling shareholder)
    perks_annual: float = 12000.0  # Company car, private phone, etc.
    pension_annual: float = 10000.0  # Company pension contributions / provisions
    other_bonuses: float = 0.0
    has_prior_written_agreement: bool = True
    has_clear_upper_cap: bool = True
    has_loss_carryforward_clause: bool = True
    has_shareholder_resolution: bool = True

    @property
    def is_controlling_shareholder(self) -> bool:
        return self.share_percentage >= 50.0


@dataclass
class AssessmentResult:
    company: CompanyProfile
    gf: GFProfile
    calculated_tantieme: float
    total_compensation: float
    max_permissible_tantieme_50_rule: float
    exceeds_50_rule: bool
    excess_50_rule: float
    fixed_salary_share_percent: float
    variable_salary_share_percent: float
    exceeds_75_rule: bool
    excess_variable: float
    bbe_benchmark_lower: float
    bbe_benchmark_median: float
    bbe_benchmark_upper: float
    exceeds_bbe_upper: bool
    excess_bbe: float
    formal_vga_reasons: List[str] = field(default_factory=list)
    material_vga_amount: float = 0.0
    formal_vga_amount: float = 0.0
    total_vga_amount: float = 0.0
    gmbh_tax_rate_approx: float = 0.308  # ~30.8% DE (15% KSt + 5.5% SolZ + 15% GewSt)
    gmbh_tax_repayment: float = 0.0
    gmbh_corrected_profit: float = 0.0
    shareholder_tax_treatment: str = ""
    risk_level: VGARiskLevel = VGARiskLevel.LOW_GREEN
    warnings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
