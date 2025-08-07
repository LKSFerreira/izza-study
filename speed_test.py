import time
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()
from poe_client_openai import get_bot_response as get_response_openai
from poe_client_sdk import get_bot_response as get_response_sdk

# --- Configuração ---
BOT_NAME = "Izza-Study"  # Ou qualquer outro bot que você queira testar
TEST_MESSAGE = {"role": "user", "content": "Meu Slayer está com a build errada, meu dano caiu muito nos últimos dungeons. As skills do meu Gunner não estão glyphadas certo, pode me ajudar?"}

# --- Garante que a chave da API está configurada ---
if not os.environ.get("POE_API_KEY"):
    print("Erro: A variável de ambiente POE_API_KEY não foi definida.")
    exit()

async def main():
    print("--- Iniciando Teste de Performance de API ---")
    print(f"\nMensagem de teste: \"{TEST_MESSAGE['content']}\"")

    # --- Teste 1: Biblioteca OpenAI ---
    print("\n==================================================")
    print("  TESTE 1: Biblioteca 'openai'")
    print("==================================================")
    start_time_openai = time.perf_counter()
    try:
        response_openai = await get_response_openai(messages=[TEST_MESSAGE], bot_name=BOT_NAME)
        end_time_openai = time.perf_counter()
        print(f"  -> Tempo de resposta: {end_time_openai - start_time_openai:.4f} segundos.")
        print(f"  -> Resposta do Bot:")
        print("-" * 50)
        print(response_openai)
        print("-" * 50)
    except Exception as e:
        print(f"  -> Ocorreu um erro: {e}")

    # --- Teste 2: SDK FastAPI-Poe ---
    print("\n==================================================")
    print("  TESTE 2: SDK 'fastapi-poe'")
    print("==================================================")
    start_time_sdk = time.perf_counter()
    try:
        response_sdk = await get_response_sdk(messages=[TEST_MESSAGE], bot_name=BOT_NAME)
        end_time_sdk = time.perf_counter()
        print(f"  -> Tempo de resposta: {end_time_sdk - start_time_sdk:.4f} segundos.")
        print(f"  -> Resposta do Bot:")
        print("-" * 50)
        print(response_sdk)
        print("-" * 50)
    except Exception as e:
        print(f"  -> Ocorreu um erro: {e}")

    print("\n--- Teste Concluído ---")

if __name__ == "__main__":
    asyncio.run(main())
