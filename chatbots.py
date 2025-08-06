import logging
import dotenv
import openai
import os

dotenv.load_dotenv()
logger = logging.getLogger("izza-study")

api_key = os.getenv("POE_API_KEY")
base_url = os.getenv("POE_BASE_URL", "https://api.poe.com/v1")

if not api_key:
    raise ValueError("Defina POE_API_KEY no .env")

client = openai.OpenAI(api_key=api_key, base_url=base_url)

# Modelo padrão
model_name = "GPT-4o-mini"

# Prompt do sistema que define o comportamento do tradutor
system_prompt = (
    "Você é um tradutor profissional especializado em terminologia de jogos, especialmente MMORPGs. "
    "Sua tarefa é detectar o idioma de uma frase de entrada (inglês dos EUA ou português do Brasil) e traduzi-la para o outro idioma. "
    "Traduza de PT-BR para EN-US e de EN-US para PT-BR. "
    "É crucial que você mantenha termos comuns de jogos em inglês (por exemplo: 'Warrior', 'DPS', 'build', 'glyphs', 'healer', 'tank', 'aggro', 'pull') "
    "mesmo ao traduzir para o português, pois são de uso corrente na comunidade. "
    "Sua resposta deve conter APENAS a frase traduzida, sem nenhuma explicação, comentário ou formatação adicional."
)


def translate_auto(phrase):
    """Detecta o idioma da frase e a traduz para PT-BR ou EN-US."""
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": phrase},
            ],
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Erro na API de tradução: {e}")
        raise
