import os
import httpx



# OS environment variables for the URL and the model to use 
OPENROUTER_URL = os.environ["OPENROUTER_URL"]
MODEL_NAME = os.environ["MODEL_NAME"]



async def generate_job_summary(raw_text: str) -> str:
    """
    Sends the raw clipboard job text block to NVIDIA's Nemotron 3 Ultra model
    via OpenRouter to generate an operational technical requirements breakdown.
    """
    # Defensive programming: Return clean fallback notice if input string is empty
    if not raw_text or not raw_text.strip():
        return "No job description text provided for AI analysis."

    # Safely look up your private API key from system environment variables
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        return "[AI Engine Alert]: OPENROUTER_API_KEY is missing from system variables."

    # Structure explicit OpenRouter routing tracking headers
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    # Strict system execution guidelines matching your exact required formatting layout
    system_prompt = (
        "You are an elite, highly precise technical recruiter AI agent. "
        "Analyze the provided job description and extract a structured operational profile. "
        "You must start your response EXACTLY with this text string phrase:\n"
        "Here is a summary of the job description, with the key requirements:\n\n"
        "Following that mandatory sentence, output 3 to 5 concise bullet points detailing "
        "the core responsibilities, specific technology stack, and critical candidate requirements. "
        "Do not include conversational filler, meta-announcements, or greetings."
    )

    # Package standard payload for the OpenRouter model
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": raw_text}
        ],
        "temperature": 0.2  # Lower temperature locks in adherence to the string prefix formatting
    }

    try:
        # Open an async network stream connection with a generous timeout ceiling
        async with httpx.AsyncClient() as client:
            response = await client.post(OPENROUTER_URL, headers=headers, json=payload, timeout=45.0)
            
            # case where response is perfectly valid
            if response.status_code == 200:
                data = response.json()

                # Check if OpenRouter passed an inner error wrapped inside a 200 OK block
                if "error" in data:
                    error_info = data["error"]
                    return (
                        f"[OpenRouter Inner Error]: Code {error_info.get('code')} - "
                        f"{error_info.get('message')}"
                    )
                
                # Verify that the expected choices array actually exists
                if "choices" not in data or not data["choices"]:
                    return f"[AI Layout Error]: Received an unexpected payload format from OpenRouter. Raw: {data}"
                
                # Safely extract standard OpenAI-compatible completions
                return data["choices"][0]["message"]["content"]
            
            elif response.status_code == 429:
                # Capture API usage ceilings cleanly without locking up the front-end dashboard
                return (
                    "[OpenRouter Rate Limit Activated]: The free AI engine is currently "
                    "busy or your local request limit was reached. Please wait 60 seconds before trying again."
                )
            
            else:
                return f"[AI Generation Error]: HTTP {response.status_code} - {response.text}"
                
    except httpx.TimeoutException:
        return "[AI Network Timeout]: The remote reasoning model took too long to compile its tokens. Please retry."
    except Exception as e:
        return f"[AI Integration Exception]: Failed to communicate with OpenRouter. Detail: {str(e)}"
