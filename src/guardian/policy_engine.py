import yaml
import re
import os
from typing import Dict, Any, List

class GuardianBlockError(Exception):
    """Raised when an action is blocked by the Guardian Policy."""
    pass

class PolicyEngine:
    def __init__(self, rules_path: str = "src/guardian/guardian_rules.yaml"):
        self.rules = self._load_rules(rules_path)

    def _load_rules(self, path: str) -> List[Dict[str, Any]]:
        """Loads rules from a YAML file."""
        if not os.path.exists(path):
            # Fallback or empty if file doesn't exist, though it should.
            print(f"[GUARDIAN] Warning: Rules file not found at {path}. Defaulting to empty.")
            return []
        
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
            return data.get('rules', [])

    def check(self, tool_name: str, arguments: Dict[str, Any], user_profile: Dict[str, Any] = None) -> bool:
        """
        Checks the tool call against the loaded rules.
        Returns True if ALLOWED, raises GuardianBlockError if BLOCKED.
        """
        # Flatten arguments to a string for pattern matching
        # Also include tool_name to allow rules to target specific tools
        check_str = f"{tool_name} {str(arguments)}".upper()
        
        user_role = user_profile.get("role", "USER") if user_profile else "USER"

        for rule in self.rules:
            pattern = rule.get("pattern")
            if pattern and re.search(pattern, check_str):
                # Check exceptions
                exceptions = rule.get("exceptions", [])
                is_exempt = False
                for exc in exceptions:
                    if exc.get("user_role") == user_role:
                        is_exempt = True
                        break
                
                if not is_exempt:
                    if rule.get("action") == "BLOCK":
                        raise GuardianBlockError(f"Action prohibited by Policy Rule: {rule.get('name')}")
        
        return True
