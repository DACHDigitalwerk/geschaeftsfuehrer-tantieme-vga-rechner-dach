# -*- coding: utf-8 -*-
"""
Command line interface for DACH Geschäftsführer-Tantieme & vGA-Rechner 2026.
"""

import sys
import os
import json
import argparse
from typing import Optional

if __package__ is None or __package__ == "":
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from tantieme_dach.models import (
        Country,
        Industry,
        VGARiskLevel,
        CompanyProfile,
        GFProfile,
    )
    from tantieme_dach.calculator import (
        assess_gf_compensation,
        calculate_bbe_benchmark_range,
    )
else:
    from .models import (
        Country,
        Industry,
        VGARiskLevel,
        CompanyProfile,
        GFProfile,
    )
    from .calculator import (
        assess_gf_compensation,
        calculate_bbe_benchmark_range,
    )


def fmt_eur(val: float) -> str:
    return f"{val:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")


def print_karlsruher_table(current_revenue: float):
    print("\n" + "=" * 78)
    print("  KARLSRUHER TABELLE & BBE BENCHMARKS (GESAMTAUSSTATTUNG KMU)")
    print("=" * 78)
    print(f"{'Umsatzklasse':<24} | {'Unterwert':<13} | {'Median':<13} | {'Obergrenze (vGA)':<16}")
    print("-" * 78)
    brackets = [
        ("< 1,25 Mio. €", 95000, 130000, 165000, 0, 1250000),
        ("1,25 – 2,50 Mio. €", 135000, 175000, 230000, 1250000, 2500000),
        ("2,50 – 5,00 Mio. €", 175000, 235000, 310000, 2500000, 5000000),
        ("5,00 – 10,00 Mio. €", 225000, 315000, 420000, 5000000, 10000000),
        ("> 10,00 Mio. €", 300000, 415000, 550000, 10000000, float("inf")),
    ]
    for label, low, med, high, r_min, r_max in brackets:
        marker = " ◄ [Ihre Klasse]" if r_min <= current_revenue < r_max else ""
        print(f"{label:<24} | {fmt_eur(low):<13} | {fmt_eur(med):<13} | {fmt_eur(high):<16}{marker}")
    print("=" * 78 + "\n")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="dach-tantieme",
        description="DACH GF-Tantieme, Vergütung & vGA-Rechner 2026 (Karlsruher Tabelle & § 8 Abs. 3 KStG)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    group_comp = parser.add_argument_group("Unternehmensdaten")
    group_comp.add_argument("-r", "--revenue", type=float, default=2500000.0, help="GmbH Jahresumsatz in EUR (Default: 2.500.000)")
    group_comp.add_argument("-p", "--profit", type=float, default=300000.0, help="Vorsteuergewinn vor Tantieme in EUR (Default: 300.000)")
    group_comp.add_argument("-e", "--equity", type=float, default=250000.0, help="GmbH Eigenkapital in EUR (Default: 250.000)")
    group_comp.add_argument("--employees", type=int, default=15, help="Anzahl Mitarbeiter FTE (Default: 15)")
    group_comp.add_argument("--country", type=str, choices=["DE", "AT", "CH"], default="DE", help="Rechtsraum (Default: DE)")
    group_comp.add_argument("--industry", type=str, choices=["it_tech", "services", "commerce", "manufacturing", "construction", "other"], default="services", help="Branche (Default: services)")
    group_comp.add_argument("--hebesatz", type=float, default=410.0, help="Gewerbesteuer-Hebesatz in Prozent (Default: 410.0)")

    group_gf = parser.add_argument_group("Geschäftsführer-Vergütung")
    group_gf.add_argument("-s", "--base-salary", type=float, default=140000.0, help="Festgehalt / Grundvergütung p.a. in EUR (Default: 140.000)")
    group_gf.add_argument("-t", "--tantieme-rate", type=float, default=15.0, help="Gewinntantieme in Prozent des Vorsteuergewinns (Default: 15.0)")
    group_gf.add_argument("--fixed-tantieme", type=float, default=None, help="Optional: Feste Tantieme in EUR statt Prozentsatz")
    group_gf.add_argument("--perks", type=float, default=9000.0, help="Firmenwagen 1%% / Sachbezüge p.a. in EUR (Default: 9.000)")
    group_gf.add_argument("--pension", type=float, default=6000.0, help="Pensionszusage / bAV-Aufwand p.a. in EUR (Default: 6.000)")
    group_gf.add_argument("--share", type=float, default=100.0, help="Beteiligungsquote des GF in Prozent (Default: 100.0)")

    group_form = parser.add_argument_group("Formelle Kriterien (BFH)")
    group_form.add_argument("--no-written-agreement", action="store_true", help="Keine schriftliche Vorabvereinbarung vorhanden")
    group_form.add_argument("--no-cap", action="store_true", help="Keine vertragliche Obergrenze (Cap) fixiert")
    group_form.add_argument("--no-loss-carryforward", action="store_true", help="Fehlende Verlustvortragsklausel")
    group_form.add_argument("--no-resolution", action="store_true", help="Kein Gesellschafterbeschluss vorhanden")

    group_out = parser.add_argument_group("Ausgabeoptionen")
    group_out.add_argument("--json", action="store_true", help="Ausgabe als JSON formatieren")
    group_out.add_argument("--show-karlsruher-table", action="store_true", help="Karlsruher Tabelle anzeigen")

    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    country_map = {"DE": Country.DE, "AT": Country.AT, "CH": Country.CH}
    ind_map = {
        "it_tech": Industry.IT_TECH,
        "services": Industry.SERVICES,
        "commerce": Industry.COMMERCE,
        "manufacturing": Industry.MANUFACTURING,
        "construction": Industry.CONSTRUCTION,
        "other": Industry.OTHER,
    }

    company = CompanyProfile(
        annual_revenue=args.revenue,
        employee_count=args.employees,
        pretax_profit_before_tantieme=args.profit,
        industry=ind_map[args.industry],
        country=country_map[args.country],
        equity_capital=args.equity,
    )

    gf = GFProfile(
        name="Geschäftsführer",
        base_salary=args.base_salary,
        tantieme_rate_percent=args.tantieme_rate,
        agreed_tantieme_fixed=args.fixed_tantieme,
        share_percentage=args.share,
        perks_annual=args.perks,
        pension_annual=args.pension,
        has_prior_written_agreement=not args.no_written_agreement,
        has_clear_upper_cap=not args.no_cap,
        has_loss_carryforward_clause=not args.no_loss_carryforward,
        has_shareholder_resolution=not args.no_resolution,
    )

    result = assess_gf_compensation(company, gf)

    if args.json:
        data = {
            "company": {
                "annual_revenue": company.annual_revenue,
                "employee_count": company.employee_count,
                "pretax_profit": company.pretax_profit_before_tantieme,
                "equity_capital": company.equity_capital,
                "country": company.country.value,
                "industry": company.industry.value,
            },
            "gf": {
                "base_salary": gf.base_salary,
                "tantieme_rate": gf.tantieme_rate_percent,
                "share_percentage": gf.share_percentage,
                "is_controlling": gf.is_controlling_shareholder,
            },
            "compensation": {
                "base_salary": gf.base_salary,
                "calculated_tantieme": result.calculated_tantieme,
                "perks": gf.perks_annual,
                "pension": gf.pension_annual,
                "total_compensation": result.total_compensation,
            },
            "bfh_checks": {
                "exceeds_50_rule": result.exceeds_50_rule,
                "excess_50_rule": result.excess_50_rule,
                "exceeds_75_rule": result.exceeds_75_rule,
                "excess_variable": result.excess_variable,
                "fixed_share_percent": result.fixed_salary_share_percent,
                "variable_share_percent": result.variable_salary_share_percent,
            },
            "benchmark_karlsruher_bbe": {
                "lower": result.bbe_benchmark_lower,
                "median": result.bbe_benchmark_median,
                "upper": result.bbe_benchmark_upper,
                "exceeds_upper": result.exceeds_bbe_upper,
                "excess_amount": result.excess_bbe,
            },
            "vga_assessment": {
                "risk_level": result.risk_level.value,
                "total_vga_amount": result.total_vga_amount,
                "formal_vga_amount": result.formal_vga_amount,
                "material_vga_amount": result.material_vga_amount,
                "gmbh_tax_repayment": result.gmbh_tax_repayment,
                "warnings": result.warnings,
                "recommendations": result.recommendations,
            },
            "legal_disclaimer": "Rein technisches Simulationswerkzeug gem. BGH I ZR 113/20 (Smartlaw). Keine Rechts- oder Steuerberatung (§ 2 RDG / § 5 StBerG).",
        }
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return 0

    if args.show_karlsruher_table:
        print_karlsruher_table(company.annual_revenue)

    print("\n" + "=" * 78)
    print("  DACH GESCHÄFTSFÜHRER-TANTIEME & VGA-PRÜFBERICHT 2026")
    print("  Karlsruher Tabelle • BFH 50%-/75%-Regeln • § 8 Abs. 3 KStG")
    print("=" * 78)

    print("\n1. GESAMTAUSSTATTUNG DES GESCHÄFTSFÜHRERS:")
    print(f"  • Festgehalt p.a.          : {fmt_eur(gf.base_salary):>15}  ({result.fixed_salary_share_percent:.1f} %)")
    print(f"  • Gewinntantieme ({gf.tantieme_rate_percent:.1f} %)   : {fmt_eur(result.calculated_tantieme):>15}  ({result.variable_salary_share_percent:.1f} %)")
    print(f"  • Sachbezug (Firmenwagen)  : {fmt_eur(gf.perks_annual):>15}")
    print(f"  • Pensionszusage / bAV     : {fmt_eur(gf.pension_annual):>15}")
    print("  " + "-" * 42)
    print(f"  = GESAMTAUSSTATTUNG        : {fmt_eur(result.total_compensation):>15}  (100,0 %)")

    print("\n2. KARLSRUHER TABELLE & BBE-BENCHMARK (VERGLEICHSGRUPPE):")
    print(f"  • Unterer Toleranzwert     : {fmt_eur(result.bbe_benchmark_lower):>15}")
    print(f"  • Median (Richtwert)       : {fmt_eur(result.bbe_benchmark_median):>15}")
    print(f"  • Obere Schmerzensgrenze   : {fmt_eur(result.bbe_benchmark_upper):>15}")
    if result.exceeds_bbe_upper:
        print(f"  ⚠️  ÜBERSCHREITUNG        : {fmt_eur(result.excess_bbe):>15}  (vGA-Risiko!)")
    else:
        print("  ✓ Liegt innerhalb der anerkannten Bandbreite.")

    print("\n3. BFH-DECKEUNGEN:")
    rule_50_str = "❌ VERLETZT" if result.exceeds_50_rule else "✓ Eingehalten"
    print(f"  • BFH 50%-Regel (Tantieme) : {rule_50_str} (Zulässig max.: {fmt_eur(result.max_permissible_tantieme_50_rule)})")
    rule_75_str = "❌ VERLETZT" if result.exceeds_75_rule else "✓ Eingehalten"
    print(f"  • BFH 75%-Regel (Festanteil): {rule_75_str} (Festanteil: {result.fixed_salary_share_percent:.1f} %)")

    print("\n4. STEUERLICHES VGA-FAZIT & NACHZAHLUNG:")
    status_icon = "🟢" if result.risk_level == VGARiskLevel.LOW_GREEN else ("🟡" if result.risk_level == VGARiskLevel.MEDIUM_YELLOW else "🔴")
    print(f"  • Risikostufe              : {status_icon} {result.risk_level.value}")
    print(f"  • Gefährdeter vGA-Betrag   : {fmt_eur(result.total_vga_amount):>15}")
    print(f"  • Steuernachzahlung GmbH   : {fmt_eur(result.gmbh_tax_repayment):>15}  (KSt + SolZ + GewSt)")

    if result.warnings:
        print("\nWARNHINWEISE:")
        for w in result.warnings:
            print(f"  ⚠️  {w}")

    if result.recommendations:
        print("\nHANDLUNGSEMPFEHLUNGEN:")
        for r in result.recommendations:
            print(f"  💡 {r}")

    print("\n" + "-" * 78)
    print("Rechtlicher Hinweis (BGH I ZR 113/20 – Smartlaw):")
    print("Rein mathematisch-statistisches Simulationswerkzeug. Keine Rechts- oder Steuerberatung.")
    print("=" * 78 + "\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
