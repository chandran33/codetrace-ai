def get_category(score):
    if score <= 30:
        return "Mostly Human-Written"
    elif score <= 60:
        return "AI-Assisted"
    elif score <= 80:
        return "High AI Usage Suspected"
    else:
        return "Very High AI-Generated Risk"


def build_simple_report(project_name, total_files, rule_score, category):
    return f"""
Project Name: {project_name}

Total Files Analyzed: {total_files}

Initial Rule-Based Risk Score: {rule_score}/100

Initial Category: {category}

Note:
This system does not prove AI usage. It estimates AI usage risk using multiple evidence signals such as code style, comments, documentation consistency, and developer understanding.
"""