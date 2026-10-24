# -*- coding: utf-8 -*-
"""
Core calculation engine for managing director compensation, BFH tantieme checks,
BBE benchmarking, and vGA (Verdeckte Gewinnausschüttung) exposure in DACH.
"""

from typing import List, Tuple
from .models import (
    CompanyProfile,
    GFProfile,
    AssessmentResult,
    Country,
    Industry,
    VGARiskLevel,
)
from .validator import validate_company_profile, validate_gf_profile


def calculate_bbe_benchmark_range(
    annual_revenue: float,
    employee_count: int,
    industry: Industry,
) -> Tuple[float, float, float]:
    """
    Calculates BBE benchmark compensation range (lower quartile, median, upper limit)
    based on empirical salary studies for managing directors in KMU / Mittelstand.
    """
    if annual_revenue <= 500_000:
        base_median = 95_000.0
    elif annual_revenue <= 1_000_000:
        base_median = 125_000.0
    elif annual_revenue <= 2_500_000:
        base_median = 165_000.0
    elif annual_revenue <= 5_000_000:
        base_median = 210_000.0
    elif annual_revenue <= 10_000_000:
        base_median = 265_000.0
    elif annual_revenue <= 25_000_000:
        base_median = 340_000.0
    else:
        # Scale for large mid-market entities
        additional = min(180_000.0, (annual_revenue - 25_000_000.0) * 0.002)
        base_median = 420_000.0 + additional

    # Employee count multiplier
    if employee_count < 5:
        emp_mult = 0.90
    elif employee_count <= 20:
        emp_mult = 1.00
    elif employee_count <= 50:
        emp_mult = 1.08
    elif employee_count <= 100:
        emp_mult = 1.15
    else:
        emp_mult = 1.25

    # Industry multiplier
    industry_weights = {
        Industry.IT_TECH: 1.12,
        Industry.SERVICES: 1.05,
        Industry.MANUFACTURING: 1.02,
        Industry.CONSTRUCTION: 0.98,
        Industry.COMMERCE: 0.95,
        Industry.OTHER: 1.00,
    }
    ind_mult = industry_weights.get(industry, 1.0)

    median = round(base_median * emp_mult * ind_mult, 2)
    lower = round(median * 0.78, 2)
    # Upper safe limit recognized in tax audits
    upper = round(median * 1.35, 2)

    return lower, median, upper


def calculate_tantieme_amount(
    profit_before_tantieme: float,
    rate_percent: float,
    fixed_amount: float = None,
    equity: float = 0.0,
    target_min_roe: float = 0.08,
) -> float:
    """
    Calculates profit-based tantieme with consideration of required equity return.
    """
    if fixed_amount is not None:
        return max(0.0, float(fixed_amount))

    if profit_before_tantieme <= 0.0:
        return 0.0

    # Required minimum equity return before tantieme allocation
    equity_hurdle = max(0.0, equity * target_min_roe)
    basis = max(0.0, profit_before_tantieme - equity_hurdle)
    return round(basis * (rate_percent / 100.0), 2)


def assess_bfh_50_rule(
    tantieme: float,
    profit_before_tantieme: float,
) -> Tuple[bool, float, float]:
    """
    BFH 50% Rule: Total tantiemes granted to managing directors may not exceed
    50% of the commercial profit before taxes and tantiemes.
    Returns: (exceeds_50, max_allowed, excess_amount)
    """
    if profit_before_tantieme <= 0.0:
        # Any tantieme paid during negative profits is an excess
        return tantieme > 0.0, 0.0, tantieme

    max_allowed = round(profit_before_tantieme * 0.50, 2)
    if tantieme > max_allowed:
        excess = round(tantieme - max_allowed, 2)
        return True, max_allowed, excess
    return False, max_allowed, 0.0


def assess_bfh_75_rule(
    base_salary: float,
    tantieme: float,
    perks: float,
    pension: float,
    bonuses: float,
    is_controlling: bool,
) -> Tuple[bool, float, float, float, float]:
    """
    BFH 75% Rule for controlling shareholder-directors:
    At least 75% of total compensation must consist of fixed salary components
    (or variable compensation may not exceed 25-30%).
    Returns: (exceeds_rule, fixed_share_pct, variable_share_pct, max_allowed_var, excess_var)
    """
    total = base_salary + tantieme + perks + pension + bonuses
    if total <= 0:
        return False, 100.0, 0.0, 0.0, 0.0

    fixed_components = base_salary + perks + pension
    variable_components = tantieme + bonuses

    fixed_pct = round((fixed_components / total) * 100.0, 2)
    var_pct = round((variable_components / total) * 100.0, 2)

    if not is_controlling:
        # Non-controlling managing directors have more contractual flexibility
        return False, fixed_pct, var_pct, variable_components, 0.0

    # Max permissible variable share is 25% (or ratio 75/25)
    max_var_allowed = round(total * 0.25, 2)
    if variable_components > max_var_allowed:
        excess_var = round(variable_components - max_var_allowed, 2)
        return True, fixed_pct, var_pct, max_var_allowed, excess_var

    return False, fixed_pct, var_pct, max_var_allowed, 0.0


def assess_formal_vga_criteria(gf: GFProfile) -> List[str]:
    """
    Checks formal requirements under BFH doctrine (§ 8 Abs. 3 KStG):
    Klarheitsgebot, Rückwirkungsverbot, Obergrenze, Gesellschafterbeschluss.
    """
    reasons: List[str] = []

    if gf.is_controlling_shareholder:
        if not gf.has_prior_written_agreement:
            reasons.append("Formfehler: Keine vorherige schriftliche Vereinbarung (Verstoß gegen Klarheitsgebot & Rückwirkungsverbot).")
        if not gf.has_clear_upper_cap:
            reasons.append("Formfehler: Keine betragsmäßige Obergrenze / Deckelung der variablen Tantieme im Anstellungsvertrag.")
        if not gf.has_loss_carryforward_clause:
            reasons.append("Formfehler: Fehlende Verlustvortragsklausel (Tantieme wird trotz früherer Fehlbeträge ausgeschüttet).")
        if not gf.has_shareholder_resolution:
            reasons.append("Formfehler: Fehlender Gesellschafterbeschluss über Vergütung nach § 46 Nr. 5 GmbHG.")
    else:
        # Non-controlling still needs clear basis
        if not gf.has_prior_written_agreement:
            reasons.append("Formfehler: Mündliche Vereinbarung erhöht das Risiko steuerlicher Verwerfung.")

    return reasons


def assess_gf_compensation(
    company: CompanyProfile,
    gf: GFProfile,
) -> AssessmentResult:
    """
    Master audit evaluation: performs complete quantitative & qualitative
    assessment of managing director remuneration against BFH limits, BBE benchmarks,
    and calculates tax impact of a potential vGA.
    """
    validate_company_profile(company)
    validate_gf_profile(gf)

    # 1. Calculate actual tantieme
    tantieme = calculate_tantieme_amount(
        profit_before_tantieme=company.pretax_profit_before_tantieme,
        rate_percent=gf.tantieme_rate_percent,
        fixed_amount=gf.agreed_tantieme_fixed,
        equity=company.equity_capital,
        target_min_roe=company.target_min_return_on_equity,
    )

    total_comp = round(gf.base_salary + tantieme + gf.perks_annual + gf.pension_annual + gf.other_bonuses, 2)

    # 2. BFH 50% Rule check
    exceeds_50, max_50, excess_50 = assess_bfh_50_rule(tantieme, company.pretax_profit_before_tantieme)

    # 3. BFH 75% Rule check
    exceeds_75, fixed_pct, var_pct, max_var, excess_var = assess_bfh_75_rule(
        base_salary=gf.base_salary,
        tantieme=tantieme,
        perks=gf.perks_annual,
        pension=gf.pension_annual,
        bonuses=gf.other_bonuses,
        is_controlling=gf.is_controlling_shareholder,
    )

    # 4. BBE benchmark check
    lower_bbe, median_bbe, upper_bbe = calculate_bbe_benchmark_range(
        annual_revenue=company.annual_revenue,
        employee_count=company.employee_count,
        industry=company.industry,
    )

    exceeds_bbe = total_comp > upper_bbe
    excess_bbe = round(max(0.0, total_comp - upper_bbe), 2)

    # 5. Formal criteria
    formal_reasons = assess_formal_vga_criteria(gf)

    # 6. Quantify vGA amounts
    material_vga = max(excess_bbe, excess_50, excess_var)
    formal_vga = 0.0

    # Formal defect for controlling shareholder often invalidates the entire tantieme
    if formal_reasons and gf.is_controlling_shareholder:
        formal_vga = tantieme

    total_vga = round(max(material_vga, formal_vga), 2)

    # 7. Tax rate and repayment calculation by country
    if company.country == Country.DE:
        tax_rate = 0.30825  # 15% KSt + 5.5% SolZ (0.825%) + ca. 15% GewSt
        shareholder_rule = "DE: Umqualifikation in vGA gem. § 20 Abs. 1 Nr. 1 Satz 2 EStG (Abgeltungsteuer 25% + SolZ oder Teileinkünfteverfahren 60% steuerpflichtig)."
    elif company.country == Country.AT:
        tax_rate = 0.23  # 23% KöSt ab 2024/2026
        shareholder_rule = "AT: Umqualifikation in verdeckte Ausschüttung gem. § 8 Abs. 2 KStG 1988 (27,5% KESt nach § 27 Abs. 2 EStG)."
    else:  # Country.CH
        tax_rate = 0.145  # Ca. 14.5% kombinierte Gewinnsteuer Bund/Kanton
        shareholder_rule = "CH: Geldwerte Leistung / vGA unterliegt der Verrechnungssteuer von 35% (§ 4 VStG) und Einkommenssteuer auf Ebene des Gesellschafters."

    tax_repayment = round(total_vga * tax_rate, 2)
    corrected_profit = round(company.pretax_profit_before_tantieme + total_vga, 2)

    # 8. Determine Risk Level & Warnings
    warnings: List[str] = []
    recommendations: List[str] = []

    if total_vga > 0:
        if formal_reasons:
            warnings.extend(formal_reasons)
        if exceeds_50:
            warnings.append(f"BFH 50%-Regel verletzt: Tantieme ({tantieme:,.2f} €) übersteigt 50% des Handelsgewinns ({max_50:,.2f} €) um {excess_50:,.2f} €.")
        if exceeds_75:
            warnings.append(f"BFH 75%-Regel verletzt: Variable Bezüge ({var_pct:.1f}%) überschreiten den zulässigen Höchstanteil von 25-30% um {excess_var:,.2f} €.")
        if exceeds_bbe:
            warnings.append(f"Gesamtausstattung ({total_comp:,.2f} €) übersteigt die BBE-Obergrenze ({upper_bbe:,.2f} €) um {excess_bbe:,.2f} € (Fremdvergleichs-Risiko).")

        if total_vga > 40_000 or (total_comp > upper_bbe * 1.25) or (len(formal_reasons) >= 2):
            risk_level = VGARiskLevel.HIGH_RED
            recommendations.append("Sofortige Anpassung der Geschäftsführer-Vergütung durch Gesellschafterbeschluss vor dem nächsten Bilanzstichtag vornehmen.")
            recommendations.append("Steuerliche Rückstellung für vGA-Nachzahlung der Körperschaft- und Gewerbesteuer bilden.")
        else:
            risk_level = VGARiskLevel.MEDIUM_YELLOW
            recommendations.append("Tantiemevereinbarung deckeln und BFH-Grenzen (50%-Gewinndeckelung & 75%-Festgehaltsanteil) nachjustieren.")
    else:
        risk_level = VGARiskLevel.LOW_GREEN
        recommendations.append("Die Geschäftsführer-Vergütung liegt vollumfänglich im steuerlich anerkannten Rahmen des Fremdvergleichs.")
        recommendations.append("Dokumentieren Sie die Angemessenheitsberechnung jährlich in den Akten der Gesellschaft für Betriebsprüfungen.")

    return AssessmentResult(
        company=company,
        gf=gf,
        calculated_tantieme=tantieme,
        total_compensation=total_comp,
        max_permissible_tantieme_50_rule=max_50,
        exceeds_50_rule=exceeds_50,
        excess_50_rule=excess_50,
        fixed_salary_share_percent=fixed_pct,
        variable_salary_share_percent=var_pct,
        exceeds_75_rule=exceeds_75,
        excess_variable=excess_var,
        bbe_benchmark_lower=lower_bbe,
        bbe_benchmark_median=median_bbe,
        bbe_benchmark_upper=upper_bbe,
        exceeds_bbe_upper=exceeds_bbe,
        excess_bbe=excess_bbe,
        formal_vga_reasons=formal_reasons,
        material_vga_amount=material_vga,
        formal_vga_amount=formal_vga,
        total_vga_amount=total_vga,
        gmbh_tax_rate_approx=tax_rate,
        gmbh_tax_repayment=tax_repayment,
        gmbh_corrected_profit=corrected_profit,
        shareholder_tax_treatment=shareholder_rule,
        risk_level=risk_level,
        warnings=warnings,
        recommendations=recommendations,
    )
