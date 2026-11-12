from decimal import Decimal

from app.irmsd_engine import IRMSDDecisionEngine


def test_effort_calculation_formula():
    e_adj = IRMSDDecisionEngine.calculate_adjusted_effort(
        e_init=Decimal("10.00"),
        r_max=20,
        alpha_cal=Decimal("0.30")
    )
    assert e_adj == Decimal("12.40")
