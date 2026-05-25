import re


def count_comment_lines(content):
    lines = content.splitlines()
    comment_count = 0

    for line in lines:
        stripped = line.strip()

        if (
            stripped.startswith("#")
            or stripped.startswith("//")
            or stripped.startswith("/*")
            or stripped.startswith("*")
        ):
            comment_count += 1

    return comment_count, len(lines)


def detect_generic_comments(content):
    patterns = [
        "function to",
        "this function",
        "initialize",
        "validate input",
        "handle user",
        "main function",
        "get data",
        "set data",
        "update data",
        "delete data"
    ]

    lower = content.lower()
    count = 0

    for pattern in patterns:
        count += lower.count(pattern)

    return count


def detect_generic_variables(content):
    tokens = re.findall(r"\b[a-zA-Z_][a-zA-Z0-9_]*\b", content)

    generic_names = [
        "data", "result", "temp", "value",
        "item", "obj", "response", "input", "output"
    ]

    count = 0

    for token in tokens:
        if token.lower() in generic_names:
            count += 1

    return count


def rule_based_analysis(files_data):
    total_score = 0
    evidence = []

    for file in files_data:
        content = file["content"]

        comment_count, total_lines = count_comment_lines(content)
        generic_comment_count = detect_generic_comments(content)
        generic_variable_count = detect_generic_variables(content)

        file_score = 0

        if total_lines > 0:
            comment_percentage = (comment_count / total_lines) * 100
        else:
            comment_percentage = 0

        if comment_percentage > 25:
            file_score += 15
            evidence.append(f"{file['name']}: High comment percentage detected.")

        if generic_comment_count > 3:
            file_score += 20
            evidence.append(f"{file['name']}: Repeated generic comments detected.")

        if generic_variable_count > 15:
            file_score += 15
            evidence.append(f"{file['name']}: Many generic variable names detected.")

        if total_lines > 300:
            file_score += 10
            evidence.append(f"{file['name']}: Very large file detected.")

        total_score += file_score

    if len(files_data) == 0:
        return 0, ["No supported files found."]

    max_score = len(files_data) * 60
    final_score = round((total_score / max_score) * 100)

    return min(final_score, 100), evidence