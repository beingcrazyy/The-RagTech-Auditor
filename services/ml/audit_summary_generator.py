from openai import OpenAI

client = OpenAI()

def generate_audit_summary(
    status: str,
    hard_failures: list[str],
    soft_failures: list[str]
    ) -> str:
    prompt = f"""
    You are generating a short audit summary for a financial document.

    Document status: {status}

    Hard issues:
    {hard_failures}

    Soft issues:
    {soft_failures}

    Rules:
    - Write 1–2 concise sentences
    - Do NOT inven facts
    - Do NOT mention numbers
    - Only explain the status based on issues listed
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return response.choices[0].message.content.strip()
