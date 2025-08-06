import os
import fastapi_poe as fp

async def get_bot_response(messages: list[dict], bot_name: str) -> str:
    """
    Gets a response from a Poe bot using the official fastapi_poe SDK.
    """
    api_key = os.environ.get("POE_API_KEY")
    protocol_messages = [fp.ProtocolMessage(role=msg["role"], content=msg["content"]) for msg in messages]
    
    response_chunks = []
    async for partial in fp.get_bot_response(
        messages=protocol_messages,
        bot_name=bot_name,
        api_key=api_key
    ):
        response_chunks.append(partial.text)
        
    return "".join(response_chunks)
