import re
from typing import Optional

# Define high-priority patterns that indicate critical issues or severe dissatisfaction
HIGH_PRIORITY_PATTERNS = [
    r"refund not received",
    r"payment failed",
    r"charged twice",
    r"double.{0,10}charge",
    r"unauthorized.{0,15}charge",
    r"money.{0,10}deducted",
    r"account.{0,10}blocked",
    r"account.{0,10}hacked",
    r"account.{0,10}locked",
    r"unauthorized.{0,10}access",
    r"someone.{0,15}accessed",
    r"\d+\s*days?.{0,10}(down|outage|no service|not working)",
    r"(down|outage|no service).{0,20}\d+\s*days?",
    r"work from home",
    r"business.{0,15}(affected|impacted|critical|stopped)",
    r"never subscribed",
    r"never signed up",
    r"didn.t sign up",
]

# Precompile regex patterns for efficiency
_COMPILED = [re.compile(p, re.IGNORECASE) for p in HIGH_PRIORITY_PATTERNS]

# This function checks if any of the high-priority patterns are present in the text.
def apply_priority_rules(text: str, ml_priority: str) -> tuple[str, Optional[str]]:
    for pattern, compiled in zip(HIGH_PRIORITY_PATTERNS, _COMPILED):
        if compiled.search(text):
            return "High", pattern
    return ml_priority, None

# This function generates an explanation for why the priority was overridden, if applicable.
def explain_override(rule_pattern: Optional[str]) -> str:
    if rule_pattern is None:
        return "Priority set by ML model."
    return f"Priority overridden to High — rule matched: '{rule_pattern}'"