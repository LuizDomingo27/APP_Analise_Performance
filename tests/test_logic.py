import unittest
from datetime import datetime
from src.utils import fmt, fmtD, fmtPct, fmtDate, prazo_badge
from src.logic import parse_date, calcular_prazo_dias

class TestUtilsAndLogic(unittest.TestCase):
    def test_fmt(self):
        self.assertEqual(fmt(1234.56), "1.235")
        self.assertEqual(fmt("100"), "100")
        self.assertEqual(fmt("abc"), "abc")

    def test_fmtD(self):
        self.assertEqual(fmtD(12.34), "12,3")
        self.assertEqual(fmtD("abc"), "-")

    def test_fmtPct(self):
        self.assertEqual(fmtPct(45.67), "45.7%")
        self.assertEqual(fmtPct("abc"), "-")

    def test_fmtDate(self):
        self.assertEqual(fmtDate("2026-06-13"), "13/06/2026")
        self.assertEqual(fmtDate("13/06/2026"), "13/06/2026")
        self.assertEqual(fmtDate("2025-06-01 00:00:00"), "01/06/2025")
        self.assertEqual(fmtDate(None), "-")

    def test_parse_date(self):
        self.assertIsInstance(parse_date("13/06/2026"), datetime)
        self.assertIsNone(parse_date("data-invalida"))

    def test_calcular_prazo_dias(self):
        self.assertEqual(calcular_prazo_dias("10/06/2026", "15/06/2026"), 5)
        # fallback case
        self.assertEqual(calcular_prazo_dias("invalido", "15/06/2026", fallback=10), 10)

if __name__ == "__main__":
    unittest.main()
