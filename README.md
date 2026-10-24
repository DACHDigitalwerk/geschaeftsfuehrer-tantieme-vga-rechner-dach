# 💼 DACH Geschäftsführer-Tantieme-, Vergütung- & VGA-Rechner 2026

[![CI](https://github.com/DACHDigitalwerk/geschaeftsfuehrer-tantieme-vga-rechner-dach/actions/workflows/python-tests.yml/badge.svg)](https://github.com/DACHDigitalwerk/geschaeftsfuehrer-tantieme-vga-rechner-dach/actions)
[![Python Version](https://img.shields.io/badge/python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://pypi.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Web App](https://img.shields.io/badge/Live%20Web%20Tool-%2322%20Online-success)](https://dachdigitalwerk.github.io/geschaeftsfuehrer-tantieme-vga-rechner/)

> **Rechtssicherer Angemessenheitsprüfer & vGA-Simulator für Gesellschafter-Geschäftsführer (G-GF) im DACH-Raum nach Karlsruher Tabelle, BFH-Rechtsprechung (§ 8 Abs. 3 KStG), BBE-Gehaltsstudien und Fremdvergleichsgrundsatz.**

---

## 🌐 Interaktive Web-Applikation (100 % Client-Side)

Nutzen Sie den interaktiven Online-Rechner mit DIN-A4 Prüfbericht-Export unter:  
👉 **[https://dachdigitalwerk.github.io/geschaeftsfuehrer-tantieme-vga-rechner/](https://dachdigitalwerk.github.io/geschaeftsfuehrer-tantieme-vga-rechner/)**

---

## 📚 B2B-Fachratgeber & Judikatur-Datenbank

- 📊 **[Geschäftsführer-Gehalt Karlsruher Tabelle 2026](https://dachdigitalwerk.github.io/geschaeftsfuehrer-gehalt-angemessenheit-tabelle-2026.html)**: BFH-Richtwerte, BBE-Vergleichswerte nach Umsatz und Branche.
- 📐 **[Tantieme berechnen & BFH 50%-Deckelung](https://dachdigitalwerk.github.io/tantieme-berechnen-formel-50-prozent-deckelung.html)**: Formel vor Steuern, 75%-Gewinngrenze, Verlustklausel und Rückwirkungsverbot.
- 🛡️ **[vGA nach § 8 Abs. 3 KStG vermeiden](https://dachdigitalwerk.github.io/verdeckte-gewinnausschuettung-vga-geschaeftsfuehrer-vermeiden.html)**: Checkliste für Betriebsprüfungen, Gesellschafterdarlehen und Pensionszusagen.

---

## ⚖️ Gesetzliche & Judikative Grundlagen

1. **BFH 50%-Regel (Urteil vom 05.10.1994 – I R 50/94):**  
   Die variable Tantieme darf im Regelfall **höchstens 50 % der gesamten Bezüge** (Festgehalt + Tantieme + Sachbezüge) eines Gesellschafter-Geschäftsführers ausmachen.
2. **BFH 75%-Gewinngrenze (Urteil vom 15.03.2000 – I R 40/94):**  
   Tantiemen dürfen maximal **50 bis 75 % des maßgeblichen Vorsteuergewinns** der Kapitalgesellschaft abschöpfen. Mindestens 25 % müssen als angemessener Gesellschaftsgewinn zur Eigenkapitalbildung verbleiben.
3. **Karlsruher Tabelle & BBE-Gehaltsbandbreiten:**  
   Die ständige Rechtsprechung der Finanzgerichte (u. a. FG Baden-Württemberg / Karlsruhe) und des BFH zieht für den **äußeren Betriebsvergleich** anerkannte Strukturuntersuchungen heran:
   - `< 1,25 Mio. € Umsatz`: 95.000 € bis 165.000 € (Median ca. 130.000 €)
   - `1,25 – 2,50 Mio. € Umsatz`: 135.000 € bis 230.000 € (Median ca. 175.000 €)
   - `2,50 – 5,00 Mio. € Umsatz`: 175.000 € bis 310.000 € (Median ca. 235.000 €)
   - `5,00 – 10,00 Mio. € Umsatz`: 225.000 € bis 420.000 € (Median ca. 315.000 €)
   - `> 10,00 Mio. € Umsatz`: 300.000 € bis 550.000 €+ (Median ca. 415.000 €)
4. **Formelle vGA-Kriterien bei beherrschenden Gesellschaftern:**  
   Schriftformgebot, striktes Rückwirkungsverbot, vorheriger Gesellschafterbeschluss (§ 46 Nr. 5 GmbHG), betragsmäßige Obergrenze (Cap) und Verlustvortragsklausel.
5. **Steuernachzahlung bei vGA (§ 8 Abs. 3 Satz 2 KStG):**  
   Körperschaftsteuer (15 %) + Solidaritätszuschlag (0,825 %) + Gewerbesteuer (Hebesatz &times; 3,5 %) &asymp; **30 bis 32 % Steuernachzahlung** auf Gesellschaftsebene zzgl. Zinsen nach § 233a AO.

---

## 🚀 Installation & Schnellstart

```bash
# Aus dem Repository installieren
pip install .

# Oder direkt als CLI aufrufen
dach-tantieme --help
```

### Python-Beispiel

```python
from tantieme_dach import (
    CompanyProfile,
    GFProfile,
    Country,
    Industry,
    assess_gf_compensation,
)

company = CompanyProfile(
    annual_revenue=2_500_000.0,
    employee_count=18,
    pretax_profit_before_tantieme=350_000.0,
    industry=Industry.SERVICES,
    country=Country.DE,
    equity_capital=250_000.0,
)

gf = GFProfile(
    name="Geschäftsführer",
    base_salary=140_000.0,
    tantieme_rate_percent=15.0,
    share_percentage=100.0,
    perks_annual=9_000.0,
    pension_annual=6_000.0,
)

result = assess_gf_compensation(company, gf)

print(f"Gesamtausstattung: {result.total_compensation:,.2f} €")
print(f"BFH 50%-Regel: {'Verletzt' if result.exceeds_50_rule else 'Eingehalten'}")
print(f"vGA-Risiko: {result.risk_level.value}")
print(f"Steuernachzahlung GmbH: {result.gmbh_tax_repayment:,.2f} €")
```

---

## 💻 CLI-Befehlsreferenz

```bash
# Standard-Prüfbericht erstellen
dach-tantieme -r 2500000 -p 300000 -s 140000 -t 15

# Karlsruher Tabelle anzeigen
dach-tantieme -r 3500000 --show-karlsruher-table

# JSON-Export für CI/CD & Steuerberater-Pipelines
dach-tantieme -r 2500000 -p 300000 --json
```

---

## 🧪 Unit-Tests ausführen

```bash
pytest -v
```

---

## 🛡️ Rechtlicher Hinweis & Compliance

Gemäß dem Grundsatzurteil des **Bundesgerichtshofs (BGH vom 09.09.2021, Az. I ZR 113/20 – Smartlaw)** stellt diese Software ein rein mathematisch-statistisches Simulations-, Modellierungs- und Dokumentationswerkzeug dar. Sie ersetzt keine individuelle Beratung durch einen zugelassenen Rechtsanwalt oder Steuerberater nach § 2 RDG / § 5 StBerG.

---

## 📄 Lizenz

MIT License &copy; 2026 [DACH Digitalwerk](https://dachdigitalwerk.github.io).
