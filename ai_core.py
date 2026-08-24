import os
import google.generativeai as genai
from dotenv import load_dotenv

# 1. Laad de verborgen API sleutel uit het .env bestand
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    print("Fout: API sleutel niet gevonden. Check je .env bestand.")
    exit()

# 2. Geef de sleutel door aan de Google bibliotheek
genai.configure(api_key=API_KEY)

# 3. Kies het model (Gemini 1.5 Flash is heel snel en perfect voor dialogen)
model = genai.GenerativeModel('gemini-1.5-flash')

# 4. Stuur een testbericht naar de AI
print("Systeem opstarten... verbinding maken met AI...")
response = model.generate_content("Geef een korte, stoere begroeting alsof je een geavanceerd AI-systeem bent dat net is opgestart.")

# 5. Print het antwoord
print("\n[AI]:", response.text)