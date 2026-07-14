{
    "name": "campaign_intelligence/calculate_worth_it_score",
    "description": "Calculate a Worth-It score for a campaign.",
    "variables": ["rules_str", "text"],
    "tags": ["extraction", "scoring"]
}
---
Analyze the campaign and calculate a 'Worth-It' score out of 100 for each category. Consider the requirements, restrictions, and payout. Higher ROI is better. 

RULES EXTRACTED:
{{rules_str}}

RAW TEXT:
{{text}}
