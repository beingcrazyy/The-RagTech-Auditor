from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

_client = OpenAI()

def get_llm_client():
    return _client