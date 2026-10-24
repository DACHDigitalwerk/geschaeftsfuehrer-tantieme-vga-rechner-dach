# -*- coding: utf-8 -*-
"""
Quickstart Example: DACH Geschäftsführer-Tantieme & vGA-Rechner 2026
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tantieme_dach import (
    CompanyProfile,
    GFProfile,
    Country,
    Industry,
    assess_gf_compensation,
)


def main():
    print("=== DACH Geschäftsführer-Tantieme Quickstart ===")

    # 1. Profile erstellen
    company = CompanyProfile(
        annual_revenue=2_500_000.0,
        employee_count=18,
        pretax_profit_before_tantieme=350_000.0,
        industry=Industry.SERVICES,
        country=Country.DE,
        equity_capital=300_000.0,
    )

    gf = GFProfile(
        name="Geschäftsführer",
        base_salary=140_000.0,
        tantieme_rate_percent=15.0,  # 15% auf 350k Vorsteuergewinn = 52.500 €
        share_percentage=100.0,     # Beherrschender Gesellschafter
        perks_annual=9_600.0,       # Firmenwagen 1%-Regel
        pension_annual=8_000.0,     # bAV / Unterstützungskasse
        has_prior_written_agreement=True,
        has_clear_upper_cap=True,
        has_loss_carryforward_clause=True,
        has_shareholder_resolution=True,
    )

    # 2. Angemessenheitsprüfung durchführen
    result = assess_gf_compensation(company, gf)

    print(f"\nErgebnis für {company.country.value}-GmbH:")
    print(f"  • Gesamtausstattung : {result.total_compensation:,.2f} €")
    print(f"  • Davon Tantieme   : {result.calculated_tantieme:,.2f} € ({result.variable_salary_share_percent:.1f} %)")
    print(f"  • BFH 50%-Regel     : {'VERLETZT' if result.exceeds_50_rule else 'Eingehalten'}")
    print(f"  • BFH 75%-Regel     : {'VERLETZT' if result.exceeds_75_rule else 'Eingehalten'}")
    print(f"  • Karlsruher Median : {result.bbe_benchmark_median:,.2f} € (Obergrenze: {result.bbe_benchmark_upper:,.2f} €)")
    print(f"  • vGA-Status        : {result.risk_level.value}")
    print(f"  • vGA-Nachzahlung   : {result.gmbh_tax_repayment:,.2f} €")


if __name__ == "__main__":
    main()
