import os
import re
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def rule_based_detection(text):
    findings = []

    patterns = {
        "Email": r"\b[\w\.-]+@[\w\.-]+\.\w+\b",
        "Phone Number": r"(\+90|0)?\s?5\d{2}\s?\d{3}\s?\d{2}\s?\d{2}|\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b",
        "Turkish ID-like Number": r"\b\d{11}\b",
        "Credit Card-like Number": r"\b(?:\d[ -]*?){13,16}\b",

        "Name": r"(my name is\s+[A-ZÇĞİÖŞÜ][a-zA-ZçğıöşüÇĞİÖŞÜ]+|i'?m\s+[A-ZÇĞİÖŞÜ][a-zA-ZçğıöşüÇĞİÖŞÜ]+|i am\s+[A-ZÇĞİÖŞÜ][a-zA-ZçğıöşüÇĞİÖŞÜ]+|ben\s+[A-ZÇĞİÖŞÜ][a-zA-ZçğıöşüÇĞİÖŞÜ]+|benim adım\s+[A-ZÇĞİÖŞÜ][a-zA-ZçğıöşüÇĞİÖŞÜ]+)",
        "Age": r"\b\d{1,2}\s?(years old|year old|yaşındayım|yaşında|yaş)\b",

        "Salary / Income": r"(\d[\d,.]*\s?(bin|tl|₺|lira|usd|dollar|\$|€|euro)|salary|income|monthly salary|earnings|maaş|gelir|kazanç)",
        "Health Information": r"(disease|allergy|allergic|rhinitis|depression|anxiety|medicine|medication|treatment|doctor|diagnosis|health issue|health issues|health condition|medical|illness|hastalık|alerji|alerjik|rinit|depresyon|anksiyete|ilaç|tedavi|doktor|tanı)",
        "Address / Location": r"(address|street|avenue|district|city|neighborhood|apartment|istanbul|ankara|izmir|new york|london|kadiköy|kadikoy|kadıköy|adres|mahalle|sokak|cadde|apartman|maltepe|tuzla)"
    }

    for label, pattern in patterns.items():
        if re.search(pattern, text, re.IGNORECASE):
            findings.append(label)

    return findings


def calculate_risk(findings):
    if not findings:
        return "Low"

    risk_weights = {
        "Turkish ID-like Number": 5,
        "Credit Card-like Number": 5,
        "Health Information": 4,
        "Salary / Income": 3,
        "Name": 2,
        "Address / Location": 2,
        "Phone Number": 2,
        "Email": 2,
        "Age": 1,
    }

    score = sum(risk_weights.get(item, 1) for item in findings)

    if score >= 6:
        return "High"
    elif score >= 3:
        return "Medium"
    else:
        return "Low"


def analyze_with_llm(text, findings, risk_level):
    prompt = f"""
You are a privacy-aware AI agent.

Analyze the user's text for sensitive personal information.
Return the answer in English.

STRICT RULES:
- Only mention categories that appear in the "Rule-based detected categories" list below. Do not add categories that are not in that list.
- The risk level is already final: {risk_level}. Do not change it or suggest a different one.
- In the anonymized version, you MUST replace every name with [Name], every age with [Age], every location with [Location], every income/salary mention with [Income], and every health-related mention with [Health Information]. The anonymized text must contain NONE of the original sensitive values.

User text:
{text}

Rule-based detected categories:
{findings}

Please provide:
1. Detected sensitive information types (must match the rule-based list exactly)
2. Risk level: {risk_level}
3. A short explanation of the privacy risk
4. A safer anonymized version of the text (following the strict rules above)
5. Safe sharing recommendation for the user

Be clear, structured, and concise.
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful AI privacy assistant."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2
    )

    return response.choices[0].message.content


def run_privacy_agent(text):
    findings = rule_based_detection(text)
    risk_level = calculate_risk(findings)
    result = analyze_with_llm(text, findings, risk_level)

    return findings, risk_level, result