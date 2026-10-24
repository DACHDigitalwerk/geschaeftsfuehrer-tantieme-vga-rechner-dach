# -*- coding: utf-8 -*-
"""
Input validation functions for company profile and managing director compensation.
"""

from .models import CompanyProfile, GFProfile


class ValidationError(ValueError):
    """Raised when compensation parameters or company profile values are invalid."""
    pass


def validate_company_profile(company: CompanyProfile) -> None:
    if company.annual_revenue < 0:
        raise ValidationError(f"Jahresumsatz darf nicht negativ sein (angegeben: {company.annual_revenue}).")
    if company.employee_count < 0:
        raise ValidationError(f"Mitarbeiteranzahl darf nicht negativ sein (angegeben: {company.employee_count}).")
    if company.target_min_return_on_equity < 0 or company.target_min_return_on_equity > 1.0:
        raise ValidationError("Mindesteigenkapitalverzinsung muss zwischen 0.0 (0%) und 1.0 (100%) liegen.")
    if company.equity_capital < 0:
        raise ValidationError("Eigenkapital darf fuer die Angemessenheitsberechnung nicht negativ angesetzt werden.")


def validate_gf_profile(gf: GFProfile) -> None:
    if gf.base_salary < 0:
        raise ValidationError(f"Jahresfestgehalt darf nicht negativ sein (angegeben: {gf.base_salary}).")
    if gf.tantieme_rate_percent < 0 or gf.tantieme_rate_percent > 100:
        raise ValidationError(f"Tantiemesatz muss zwischen 0 und 100 Prozent liegen (angegeben: {gf.tantieme_rate_percent}).")
    if gf.share_percentage < 0 or gf.share_percentage > 100:
        raise ValidationError(f"Beteiligungsquote muss zwischen 0 und 100 Prozent liegen (angegeben: {gf.share_percentage}).")
    if gf.perks_annual < 0:
        raise ValidationError("Sachbezuege / Firmenwagenaufwand darf nicht negativ sein.")
    if gf.pension_annual < 0:
        raise ValidationError("Pensionsaufwand darf nicht negativ sein.")
    if gf.other_bonuses < 0:
        raise ValidationError("Sonstige Bonuszahlungen duerfen nicht negativ sein.")
    if gf.agreed_tantieme_fixed is not None and gf.agreed_tantieme_fixed < 0:
        raise ValidationError("Fest vereinbarte Tantieme darf nicht negativ sein.")
