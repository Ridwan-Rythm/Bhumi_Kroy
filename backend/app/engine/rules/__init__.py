"""Importing this package registers every rule."""
from app.engine.rules import (  # noqa: F401
    rule_chain_01,
    rule_chain_02,
    rule_chain_03,
    rule_chain_04,
    rule_disp_01,
    rule_disp_02,
    rule_disp_03,
    rule_info,
    rule_int,
    rule_int_04,
    rule_lien_01,
    rule_own_01,
    rule_own_02,
    rule_own_03,
    rule_res_01,
    rule_res_02,
    rule_res_03,
    rule_sale_01,
)
from app.engine.rules.base import REGISTRY, RuleContext, finding, run_rules  # noqa: F401
