import requests
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

# Replace with your actual DeepSeek API key
DEEPSEEK_API_KEY = "sk-377a19a07bb447e2aaf8c7a6baacf11e"

@require_http_methods(["GET", "POST"])
def generate_content(request):
    generated_text = ""
    user_prompt = ""
    if request.method == "POST":
        user_prompt = request.POST.get("prompt", "").strip()
        if user_prompt:
            try:
                headers = {
                    "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                    "Content-Type": "application/json"
                }
                data = {
                    "model": "deepseek-chat",
                    "messages": [{"role": "user", "content": user_prompt}],
                    "max_tokens": 150,
                    "temperature": 0.7
                }
                response = requests.post(
                    "https://api.deepseek.com/v1/chat/completions",
                    headers=headers,
                    json=data
                )
                response.raise_for_status()
                result = response.json()
                generated_text = result['choices'][0]['message']['content'].strip()
            except Exception as e:
                generated_text = f"An error occurred: {e}"
    return render(request, "content/content_generation.html", {
        "generated_text": generated_text,
        "user_prompt": user_prompt
    })
