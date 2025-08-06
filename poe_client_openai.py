import os
import openai

async def get_bot_response(messages: list[dict], bot_name: str) -> str:
    """
    Gets a response from a Poe bot using the openai library compatibility.
    """
    # Configure the client to use Poe's API inside the function
    client = openai.AsyncOpenAI(
        api_key=os.environ.get("POE_API_KEY"),
        base_url=os.environ.get("POE_BASE_URL", "https://api.poe.com/v1")
    )

    response_chunks = []
    stream = await client.chat.completions.create(
        model=bot_name,
        messages=messages,
        stream=True
    )
    async for chunk in stream:
        if chunk.choices:
            content = chunk.choices[0].delta.content
            if content:
                response_chunks.append(content)
    
    return "".join(response_chunks)
