import os
import openai
import dotenv

dotenv.load_dotenv()

api_key = os.getenv("POE_API_KEY")
base_url = os.getenv("POE_BASE_URL", "https://api.poe.com/v1")

if not api_key:
    raise ValueError("Defina POE_API_KEY no .env")

client = openai.OpenAI(api_key=api_key, base_url=base_url)

# Modelo padrão
model_name = "GPT-4o-mini"

# Frase de entrada (pode ser em PT-BR ou EN)
input_phrase = input("Digite a frase para tradução automática:\n> ")

# Prompt que decide automaticamente o idioma
auto_detect_prompt = (
    "Você é um tradutor profissional especializado em MMORPGs. "
    "Receba uma frase que pode estar em inglês (EUA) ou português brasileiro. "
    "Detecte o idioma e traduza para o outro idioma (PT-BR → EN ou EN → PT-BR). "
    "Mantenha termos típicos de jogos (como Warrior, DPS, build, glyphs, etc.) em inglês se forem comuns. "
    "Responda somente com a frase traduzida, sem explicações ou comentários:\n\n\"{}\""
)

def translate_auto(phrase):
    prompt = auto_detect_prompt.format(phrase)
    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": "You are a professional translator."},
            {"role": "user",   "content": prompt},
        ],
    )
    return response.choices[0].message.content.strip()

# Tradução automática
translated = translate_auto(input_phrase)
print("\n🗨️ Tradução:")
print(translated)
