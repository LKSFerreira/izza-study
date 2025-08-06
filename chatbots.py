import logging
import os
from poe_client_sdk import get_bot_response as get_response_sdk
from poe_client_openai import get_bot_response as get_response_openai

logger = logging.getLogger("izza-study")

# Modelo padrão
MODEL_NAME = "Izza-Study"

# Prompt do sistema que define o comportamento do tradutor
SYSTEM_PROMPT = (
    "Você é um tradutor profissional especializado em terminologia de jogos, especialmente MMORPGs. "
    "Sua tarefa é detectar o idioma de uma frase de entrada (inglês dos EUA ou português do Brasil) e traduzi-la para o outro idioma. "
    "Traduza de PT-BR para EN-US e de EN-US para PT-BR. "
    "É crucial que você mantenha termos comuns de jogos em inglês (por exemplo: 'Warrior', 'DPS', 'build', 'glyphs', 'healer', 'tank', 'aggro', 'pull') "
    "mesmo ao traduzir para o português, pois são de uso corrente na comunidade. "
    "Sua resposta deve conter APENAS a frase traduzida, sem nenhuma explicação, comentário ou formatação adicional."
)

async def traduzir(frase: str) -> str:
    """
    Fachada para o serviço de tradução.

    Tenta traduzir usando o método primário (SDK) e, em caso de falha,
    utiliza o método secundário (OpenAI) como fallback.
    """
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user",   "content": frase},
    ]

    try:
        logger.info("Tentando tradução via SDK (método primário).")
        response = await get_response_sdk(messages=messages, bot_name=MODEL_NAME)
        if not response:
            raise ValueError("Resposta do SDK veio vazia.")
        logger.info("Tradução via SDK bem-sucedida.")
        return response
    except Exception as e_sdk:
        logger.warning(f"Falha no método primário (SDK): {e_sdk}")
        logger.info("Acionando método de fallback (OpenAI).")
        
        try:
            response = await get_response_openai(messages=messages, bot_name=MODEL_NAME)
            if not response:
                raise ValueError("Resposta do OpenAI (fallback) veio vazia.")
            logger.info("Tradução via fallback (OpenAI) bem-sucedida.")
            return response
        except Exception as e_openai:
            logger.error(f"Falha no método de fallback (OpenAI): {e_openai}")
            # Se ambos falharem, levanta a exceção original do SDK para análise.
            raise e_sdk from e_openai
