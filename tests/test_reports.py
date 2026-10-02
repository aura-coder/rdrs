"""Tests for report generation."""
import json
import os
from pathlib import Path
from app.reports.generator import generate_json_report, generate_csv_report


def test_generate_json_report():
    path = generate_json_report()
    assert path == 'report.json'
    assert Path('report.json').exists()
    with open('report.json') as f:
        data = json.load(f)
    assert isinstance(data, list)


def test_generate_csv_report():
    path = generate_csv_report()
    assert path == 'report.csv'
    assert Path('report.csv').exists()
    with open('report.csv') as f:
        header = f.readline().strip()
    assert 'score' in header
    assert 'level' in header
