import os
import math

import pytest

from ai_agent.csv_average import CSVAverageCalculator


DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "test_data")
STUDENT_CSV = os.path.normpath(os.path.join(DATA_DIR, "Students.csv"))


def approx(a, b, tol=1e-6):
    return abs(a - b) <= tol


def test_column_averages():
    calc = CSVAverageCalculator(STUDENT_CSV)
    col_avgs = calc.column_averages()
    # Current numeric columns in Students.csv: Age, GPA, GraduationYear
    assert math.isclose(col_avgs["Age"], 20.0)
    assert math.isclose(col_avgs["GPA"], 3.7380000000000004)
    assert math.isclose(col_avgs["GraduationYear"], 2027.9333333333334)


def test_row_averages():
    calc = CSVAverageCalculator(STUDENT_CSV)
    rows = calc.row_averages()
    # Row means are calculated across numeric columns: Age, GPA, GraduationYear
    assert math.isclose(rows.iloc[0], (20 + 3.85 + 2028) / 3)
    assert math.isclose(rows.iloc[1], (19 + 3.72 + 2029) / 3)
    assert math.isclose(rows.iloc[2], (21 + 3.45 + 2027) / 3)


def test_file_not_found():
    calc = CSVAverageCalculator("nonexistent.csv")
    with pytest.raises(FileNotFoundError):
        calc.read()


def test_no_numeric_columns(tmp_path):
    p = tmp_path / "no_numbers.csv"
    p.write_text("Name,City\nA,NY\nB,LA\n")
    calc = CSVAverageCalculator(str(p))
    with pytest.raises(ValueError):
        calc.column_averages()
