# -*- coding: utf-8 -*-
import json
from io import StringIO
import sys
from tantieme_dach.cli import main


def test_cli_standard_execution(capsys):
    exit_code = main(["--revenue", "2000000", "--profit", "250000", "--base-salary", "120000", "--tantieme-rate", "10"])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "DACH GESCHÄFTSFÜHRER-TANTIEME & VGA-PRÜFBERICHT 2026" in captured.out
    assert "GESAMTAUSSTATTUNG" in captured.out


def test_cli_json_output(capsys):
    exit_code = main(["--revenue", "3000000", "--profit", "300000", "--json"])
    assert exit_code == 0
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert "compensation" in data
    assert "bfh_checks" in data
    assert "vga_assessment" in data
    assert data["company"]["annual_revenue"] == 3000000.0


def test_cli_karlsruher_table(capsys):
    exit_code = main(["--revenue", "4000000", "--show-karlsruher-table"])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "KARLSRUHER TABELLE & BBE BENCHMARKS" in captured.out
    assert "◄ [Ihre Klasse]" in captured.out
