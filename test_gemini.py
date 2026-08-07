# test_gemini.py

import google.generativeai as genai

genai.configure(api_key="AIzaSyB7lyuK_CRhcPyfbo_6N94Za-6KFxHzVmg")

model = genai.GenerativeModel("gemini-2.5-flash-lite")

response = model.generate_content("Hello")

print(response.text)