import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)


def run_agent(prompt):
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response.text

    except Exception as e:
        return f"API Error: {str(e)}"


def code_style_agent(code_summary):
    prompt = f"""
You are a Code Style Agent in an Agentic AI system called CodeTrace AI.

Your task is to analyze the coding style of this project.

Check:
1. Variable naming style
2. Comment style
3. Formatting consistency
4. Repeated patterns
5. Beginner-level vs advanced-level mismatch
6. Unnecessary abstraction
7. Whether code looks human-written, AI-assisted, or mostly AI-generated

Return the answer in this format:

Code Style Risk Level:
Observations:
Suspicious Patterns:
Positive Signs:
Final Code Style Conclusion:

Project Code:
{code_summary}
"""
    return run_agent(prompt)


def documentation_agent(readme_content, code_summary):
    prompt = f"""
You are a Documentation Consistency Agent in CodeTrace AI.

Compare the README/documentation with the actual project code.

Check:
1. Features mentioned in README but missing in code
2. Generic AI-like documentation
3. Overclaiming
4. Missing technical explanation
5. Whether documentation matches actual implementation

Return the answer in this format:

Documentation Risk Level:
Matched Features:
Mismatched Features:
Generic Documentation Signs:
Final Documentation Conclusion:

README:
{readme_content}

Project Code Summary:
{code_summary}
"""
    return run_agent(prompt)


def viva_question_agent(code_summary):
    prompt = f"""
You are a Viva Question Generator Agent.

Generate 10 viva questions based only on this project code.

Questions should test whether the developer truly understands the project.

Rules:
- Ask project-specific questions
- Ask about files, functions, logic, validation, database, API, and improvements if present
- Avoid generic theory questions
- Suitable for college project review

Project Code:
{code_summary}
"""
    return run_agent(prompt)


def risk_scoring_agent(rule_score, rule_evidence, style_output, docs_output, viva_output):
    prompt = f"""
You are the Risk Scoring Agent in CodeTrace AI.

You receive analysis from multiple agents and must produce the final authenticity report.

Important:
Do not claim 100% proof.
Only estimate AI usage risk based on evidence.

Rule-Based Score:
{rule_score}/100

Rule-Based Evidence:
{rule_evidence}

Code Style Agent Output:
{style_output}

Documentation Agent Output:
{docs_output}

Viva Question Agent Output:
{viva_output}

Now generate final report in this format:

AI Usage Risk Score:
Category:
Confidence Level:
Major Evidence:
Human-Written Signs:
Suspicious Signs:
Suggested Viva Questions:
Final Recommendation:
"""
    return run_agent(prompt)