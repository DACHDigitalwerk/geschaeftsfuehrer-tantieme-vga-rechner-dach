# -*- coding: utf-8 -*-
import pytest
from tantieme_dach.models import (
    Country,
    Industry,
    VGARiskLevel,
    CompanyProfile,
    GFProfile,
)
from tantieme_dach.calculator import (
    calculate_bbe_benchmark_range,
    calculate_tantieme_amount,
    assess_bfh_50_rule,
    assess_bfh_75_rule,
    assess_formal_vga_criteria,
    assess_gf_compensation,
)
from tantieme_dach.validator import ValidationError, validate_company_profile, validate_gf_profile


def test_calculate_bbe_benchmark_range():
    # Small company
    low, med, high = calculate_bbe_benchmark_range(400_000, 3, Industry.SERVICES)
    assert low > 0
    assert med > low
    assert high > med
    assert high <= 200_000

    # Midsize IT company
    low_it, med_it, high_it = calculate_bbe_benchmark_range(3_000_000, 25, Industry.IT_TECH)
    assert med_it > 200_000
    assert high_it > med_it

    # Large enterprise
    low_lg, med_lg, high_lg = calculate_bbe_benchmark_range(30_000_000, 150, Industry.MANUFACTURING)
    assert med_lg > 400_000


def test_calculate_tantieme_amount_standard():
    # Profit 200k, 15% rate, 0 equity hurdle
    tantieme = calculate_tantieme_amount(
        profit_before_tantieme=200_000.0,
        rate_percent=15.0,
        equity=0.0,
    )
    assert tantieme == 30_000.0


def test_calculate_tantieme_amount_with_equity_hurdle():
    # Profit 200k, equity 500k, 8% hurdle = 40k. Basis = 160k. 10% rate = 16k.
    tantieme = calculate_tantieme_amount(
        profit_before_tantieme=200_000.0,
        rate_percent=10.0,
        equity=500_000.0,
        target_min_roe=0.08,
    )
    assert tantieme == 16_000.0


def test_calculate_tantieme_amount_fixed():
    tantieme = calculate_tantieme_amount(
        profit_before_tantieme=100_000.0,
        rate_percent=10.0,
        fixed_amount=25_000.0,
    )
    assert tantieme == 25_000.0


def test_calculate_tantieme_zero_or_negative_profit():
    assert calculate_tantieme_amount(0.0, 15.0) == 0.0
    assert calculate_tantieme_amount(-50_000.0, 15.0) == 0.0


def test_bfh_50_rule_compliance():
    # Profit 300k, Tantieme 100k -> 33.3% <= 50%
    exceeds, max_allowed, excess = assess_bfh_50_rule(100_000.0, 300_000.0)
    assert not exceeds
    assert max_allowed == 150_000.0
    assert excess == 0.0


def test_bfh_50_rule_violation():
    # Profit 200k, Tantieme 130k -> 65% > 50%
    exceeds, max_allowed, excess = assess_bfh_50_rule(130_000.0, 200_000.0)
    assert exceeds
    assert max_allowed == 100_000.0
    assert excess == 30_000.0


def test_bfh_75_rule_controlling_shareholder():
    # Base 150k, Tantieme 30k, Perks 10k -> Total 190k. Fixed = 160k (84.2%), Var = 30k (15.8%).
    exceeds, fix_pct, var_pct, max_var, excess = assess_bfh_75_rule(
        base_salary=150_000.0,
        tantieme=30_000.0,
        perks=10_000.0,
        pension=0.0,
        bonuses=0.0,
        is_controlling=True,
    )
    assert not exceeds
    assert fix_pct > 75.0
    assert excess == 0.0

    # Base 100k, Tantieme 100k -> Total 200k. Fixed = 50%, Var = 50% (> 25-30% limit)
    exceeds2, fix_pct2, var_pct2, max_var2, excess2 = assess_bfh_75_rule(
        base_salary=100_000.0,
        tantieme=100_000.0,
        perks=0.0,
        pension=0.0,
        bonuses=0.0,
        is_controlling=True,
    )
    assert exceeds2
    assert var_pct2 == 50.0
    assert excess2 == 50_000.0


def test_bfh_75_rule_non_controlling():
    # Non-controlling has contractual liberty
    exceeds, fix_pct, var_pct, _, excess = assess_bfh_75_rule(
        base_salary=50_000.0,
        tantieme=150_000.0,
        perks=0.0,
        pension=0.0,
        bonuses=0.0,
        is_controlling=False,
    )
    assert not exceeds
    assert excess == 0.0


def test_formal_vga_criteria():
    gf_compliant = GFProfile(
        share_percentage=80.0,
        has_prior_written_agreement=True,
        has_clear_upper_cap=True,
        has_loss_carryforward_clause=True,
        has_shareholder_resolution=True,
    )
    assert len(assess_formal_vga_criteria(gf_compliant)) == 0

    gf_defective = GFProfile(
        share_percentage=80.0,
        has_prior_written_agreement=False,
        has_clear_upper_cap=False,
        has_loss_carryforward_clause=False,
        has_shareholder_resolution=False,
    )
    reasons = assess_formal_vga_criteria(gf_defective)
    assert len(reasons) == 4


def test_full_assessment_de_healthy():
    company = CompanyProfile(
        annual_revenue=2_500_000.0,
        employee_count=15,
        pretax_profit_before_tantieme=300_000.0,
        industry=Industry.SERVICES,
        country=Country.DE,
        equity_capital=200_000.0,
    )
    gf = GFProfile(
        name="Dr. Weber",
        base_salary=130_000.0,
        tantieme_rate_percent=12.0,
        share_percentage=100.0,
        perks_annual=8_000.0,
        pension_annual=6_000.0,
    )
    result = assess_gf_compensation(company, gf)

    assert result.calculated_tantieme > 0
    assert not result.exceeds_50_rule
    assert not result.exceeds_75_rule
    assert result.total_vga_amount == 0.0
    assert result.risk_level == VGARiskLevel.LOW_GREEN
    assert result.gmbh_tax_repayment == 0.0


def test_full_assessment_de_excessive_vga():
    company = CompanyProfile(
        annual_revenue=1_000_000.0,
        employee_count=4,
        pretax_profit_before_tantieme=400_000.0,
        country=Country.DE,
    )
    gf = GFProfile(
        base_salary=300_000.0,
        tantieme_rate_percent=60.0,  # 60% of 400k = 240k tantieme -> Total 540k on 1M revenue!
        share_percentage=100.0,
    )
    result = assess_gf_compensation(company, gf)

    assert result.exceeds_50_rule
    assert result.exceeds_bbe_upper
    assert result.total_vga_amount > 100_000.0
    assert result.risk_level == VGARiskLevel.HIGH_RED
    assert result.gmbh_tax_repayment > 30_000.0


def test_assessment_austria_and_switzerland():
    co_at = CompanyProfile(
        annual_revenue=2_000_000.0,
        employee_count=10,
        pretax_profit_before_tantieme=200_000.0,
        country=Country.AT,
    )
    gf_at = GFProfile(base_salary=120_000.0, tantieme_rate_percent=10.0, share_percentage=100.0)
    res_at = assess_gf_compensation(co_at, gf_at)
    assert res_at.gmbh_tax_rate_approx == 0.23
    assert "§ 8 Abs. 2 KStG" in res_at.shareholder_tax_treatment

    co_ch = CompanyProfile(
        annual_revenue=2_000_000.0,
        employee_count=10,
        pretax_profit_before_tantieme=200_000.0,
        country=Country.CH,
    )
    res_ch = assess_gf_compensation(co_ch, gf_at)
    assert res_ch.gmbh_tax_rate_approx == 0.145
    assert "Verrechnungssteuer" in res_ch.shareholder_tax_treatment


def test_validation_errors():
    with pytest.raises(ValidationError):
        validate_company_profile(CompanyProfile(annual_revenue=-100.0, employee_count=5, pretax_profit_before_tantieme=50_000.0))

    with pytest.raises(ValidationError):
        validate_gf_profile(GFProfile(base_salary=-1000.0))

    with pytest.raises(ValidationError):
        validate_gf_profile(GFProfile(tantieme_rate_percent=150.0))

    with pytest.raises(ValidationError):
        validate_gf_profile(GFProfile(share_percentage=-5.0))
