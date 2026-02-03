from services.llm.client import get_llm_client

def run_llm(
    prompt: str,
    model: str = "gpt-4o-mini",
    temperature: float = 0,
    max_tokens: int | None = None
) -> str:
    client = get_llm_client()

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
        max_tokens=max_tokens
    )

    return response.choices[0].message.content.strip()