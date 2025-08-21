import json
import pandas as pd

# Load JSON from file
with open("/Users/user/Documents/frontdoor_waf_policy.json", "r") as f:
    data = json.load(f)

# Extract rules
rules = data["resources"][0]["properties"]["customRules"]["rules"]

# Prepare rows for Excel
rows = []
for rule in rules:
    for condition in rule["matchConditions"]:
        rows.append({
            "Rule Name": rule.get("name"),
            "Priority": rule.get("priority"),
            "Rule Type": rule.get("ruleType"),
            "Action": rule.get("action"),
            "Rate Limit Duration (min)": rule.get("rateLimitDurationInMinutes"),
            "Rate Limit Threshold": rule.get("rateLimitThreshold"),
            "Match Variable": condition.get("matchVariable"),
            "Operator": condition.get("operator"),
            "Negate Condition": condition.get("negateCondition"),
            "Match Values": ", ".join(condition.get("matchValue", [])),
            "Group By": ", ".join(g.get("variableName", "") for g in rule.get("groupBy", []))
        })

# Save to Excel
df = pd.DataFrame(rows)
df.to_excel("/Users/user/Documents/Frontdoor_Custom_Rules.xlsx", index=False)
print("Excel file saved: Frontdoor_Custom_Rules.xlsx")
