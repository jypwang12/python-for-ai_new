import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from openai import OpenAI
import requests
from csv_average import CSVAverageCalculator

load_dotenv(Path(__file__).resolve().parent / ".env")
load_dotenv(Path(__file__).resolve().parents[2] / ".env")

REMOTE_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
REMOTE_MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
LOCAL_API_KEY = os.getenv("LOCAL_MODEL_API_KEY", "ollama")
LOCAL_BASE_URL = os.getenv("LOCAL_MODEL_URL", "http://localhost:11434/v1")
LOCAL_MODEL_NAME = os.getenv("LOCAL_MODEL_NAME", "mistral:latest")
SYSTEM_PROMPT = (
    "You are a playful assistant. Be concise, upbeat, and friendly. "
    "When the user asks for something fun, respond with a witty and lighthearted tone. "
    "If the user asks for code, provide short, working examples."
)
FUN_PROMPT = (
    "You are a playful, witty assistant. Keep replies short, upbeat, and fun. "
    "If the user asks about the weather or everyday life, respond with a cheerful one-liner."
)


def get_system_prompt(prompt: str) -> str:
    lower_prompt = prompt.lower()
    if any(
        word in lower_prompt
        for word in ["fun", "funny", "playful", "joke", "silly", "cheerful"]
    ):
        return FUN_PROMPT
    return SYSTEM_PROMPT


def get_remote_client():
    if not REMOTE_API_KEY:
        return None
    return genai.Client(api_key=REMOTE_API_KEY)


def get_local_client():
    return OpenAI(base_url=LOCAL_BASE_URL, api_key=LOCAL_API_KEY)


def chat_remote(prompt: str) -> str:
    client = get_remote_client()
    if client is None:
        raise RuntimeError("No remote Gemini key configured.")

    response = client.models.generate_content(
        model=REMOTE_MODEL_NAME,
        contents=f"{get_system_prompt(prompt)}\n\nUser: {prompt}",
    )
    return response.text.strip()


def chat_local(prompt: str) -> str:
    print(f"Using local model: {LOCAL_MODEL_NAME} at {LOCAL_BASE_URL}")
    client = get_local_client()

    def try_completion(model_name: str):
        completion = client.chat.completions.create(
            model=model_name,
            messages=[
                # {
                #    "role": "system",
                #    "content": SYSTEM_PROMPT,
                # },  # system prompt is injected into the user message for local models
                {
                    "role": "user",
                    "content": prompt,
                },  # user message is injected into the system prompt for local models
            ],
        )
        print(f"\n\nsystem prompt: {SYSTEM_PROMPT}\n\n")
        print(f"prompt: {prompt}\n\n")
        # print(f"Local model response: {completion.choices[0].message.content.strip()}")
        return completion.choices[0].message.content.strip()

    try:
        return try_completion(LOCAL_MODEL_NAME)
    except Exception as exc:
        # If the configured model is not available on the local endpoint, try to discover available models
        msg = str(exc).lower()
        if "not found" in msg or "model" in msg:
            available = get_local_models()
            if available:
                new_model = available[0]
                print(
                    f"Configured local model '{LOCAL_MODEL_NAME}' not found. Trying available model: {new_model}"
                )
                return try_completion(new_model)
        # re-raise original exception if we couldn't recover
        raise


def get_local_models():
    """Query the local model endpoint for available models and return a list of model ids/names.

    Returns an empty list on any error or if none found.
    """
    try:
        url = LOCAL_BASE_URL.rstrip("/") + "/models"
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        data = resp.json()

        # response may be {'models': [...] } or a list
        # response may be {'models': [...] }, {'data':[...]} (OpenAI style), or a plain list
        if isinstance(data, dict):
            if "models" in data and isinstance(data["models"], list):
                models = data["models"]
            elif "data" in data and isinstance(data["data"], list):
                models = data["data"]
            else:
                # unexpected dict shape; nothing to iterate
                models = []
        elif isinstance(data, list):
            models = data
        else:
            models = []

        def extract_model_id(obj):
            # return a string model identifier if found, otherwise None
            if isinstance(obj, str):
                return obj
            if isinstance(obj, dict):
                # common keys that might hold the model name
                for key in ("id", "name", "model", "modelId", "model_name"):
                    val = obj.get(key)
                    if isinstance(val, str) and val:
                        return val
                    if isinstance(val, dict):
                        nested = extract_model_id(val)
                        if nested:
                            return nested
                # if dict contains a single string value, return it
                for v in obj.values():
                    if isinstance(v, str) and v:
                        return v
                    if isinstance(v, dict):
                        nested = extract_model_id(v)
                        if nested:
                            return nested
            if isinstance(obj, list):
                for item in obj:
                    found = extract_model_id(item)
                    if found:
                        return found
            return None

        out = []
        for m in models or []:
            mid = extract_model_id(m)
            if mid and isinstance(mid, str):
                out.append(mid)
        # debug print of discovered models
        if out:
            print(f"Discovered local models: {out}")
        return out
    except Exception:
        try:
            # best-effort debugging output
            print("Failed to query local models endpoint")
        except Exception:
            pass
        return []


def chat_with_fallback(prompt: str) -> str:
    if REMOTE_API_KEY:
        try:
            return chat_remote(prompt)
        except Exception as exc:
            print(
                f"Remote Gemini failed ({type(exc).__name__}: {exc}). Falling back to local model."
            )

    try:
        return chat_local(prompt)
    except Exception as exc:
        raise RuntimeError(
            "Both remote Gemini and local fallback failed. "
            "Make sure your local model endpoint is running at HTTP://localhost:11434/v1 "
            "or set a valid Gemini API key. "
            f"Local error: {type(exc).__name__}: {exc}"
        ) from exc


def summarize_csv_with_model(csv_path: str) -> str:
    """Compute CSV averages and ask the model to produce a short friendly summary.

    The function computes numeric column averages and overall mean, then
    injects those statistics into the prompt which is sent to the model via
    the same remote/local fallback mechanism.
    """
    print(f"Summarizing CSV file: {csv_path}")
    if not os.path.exists(csv_path):
        raise FileNotFoundError(csv_path)

    calc = CSVAverageCalculator(csv_path)
    try:
        col_avgs = calc.column_averages()
    except Exception as exc:
        raise RuntimeError(f"Failed to compute CSV averages: {exc}") from exc

    stats_lines = [f"{k}: {v:.3f}" for k, v in col_avgs.items()]
    stats_text = "; ".join(stats_lines)

    model_prompt = (
        f"The user provided a CSV file at '{csv_path}'.\n"
        f"Computed numeric column averages: {stats_text}.\n"
        "Write one short, friendly sentence summarizing these results for the user."
    )
    print(f"\n\nModel prompt: {model_prompt}")
    return chat_with_fallback(model_prompt)


def handle_user_input(user_input: str) -> str:

    candidate = os.getcwd() + "/" + user_input.strip()
    if candidate.endswith(".csv") and os.path.exists(candidate):
        print(f"Detected CSV file input: {candidate}. Summarizing with model.")
        return summarize_csv_with_model(candidate)
    return chat_with_fallback("Hmmm, I can't seem to find a CSV file: " + user_input)


def main() -> None:
    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
        print(f"Handling command-line input: {prompt}")
        print(handle_user_input(prompt))
        return

    print("Gemini agent ready. Type 'exit' to quit.")
    while True:
        try:
            user_input = input("You: ").strip()
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break

        if not user_input:
            continue
        if user_input.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break

        try:
            print(f"\n\nHandling user input before calling: {user_input}")
            print(handle_user_input(user_input))
        except RuntimeError as exc:
            print(f"Error: {exc}")
            break


if __name__ == "__main__":
    main()
