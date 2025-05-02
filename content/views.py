# content/views.py

import os
import google.generativeai as genai
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.conf import settings # Import settings

# --- IMPORTANT: Security Best Practice ---
# Avoid hardcoding keys directly in code. Use environment variables or Django settings.
# Option 1: Environment Variable (Recommended)
# Set GOOGLE_API_KEY in your environment (e.g., .env file with python-dotenv)
# GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

# Option 2: Django Settings (Good Practice)
# Add GOOGLE_API_KEY = "YOUR_ACTUAL_API_KEY" to your settings.py
# (Even better: load it from an environment variable into settings.py)
try:
    # Prioritize settings.py if it's defined there
    GOOGLE_API_KEY = settings.GOOGLE_API_KEY
except AttributeError:
    # Fallback to environment variable if not in settings
    GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
    if not GOOGLE_API_KEY:
        # --- LAST RESORT / FOR QUICK TESTING ONLY ---
        # --- REPLACE THIS PLACEHOLDER WITH YOUR *ACTUAL* KEY ---
        GOOGLE_API_KEY = "YOUR_ACTUAL_API_KEY_GOES_HERE" # <--- REPLACE THIS!
        # ------------------------------------------------------
        if GOOGLE_API_KEY == "YOUR_ACTUAL_API_KEY_GOES_HERE":
             print("WARNING: Using placeholder API Key in views.py. Replace it or use settings/environment variables.")


# --- Configure the Google AI Client ---
IS_GEMINI_CONFIGURED = False
PLACEHOLDER_KEY = "YOUR_ACTUAL_API_KEY_GOES_HERE" # Keep the placeholder check consistent

if GOOGLE_API_KEY and GOOGLE_API_KEY != PLACEHOLDER_KEY:
    try:
        print(f"Configuring Gemini with API Key ending in ...{GOOGLE_API_KEY[-4:]}") # Log confirmation (hide most of key)
        genai.configure(api_key=GOOGLE_API_KEY)
        IS_GEMINI_CONFIGURED = True
        print("Gemini SDK configured successfully.")
    except Exception as e:
        print(f"Error configuring Google AI SDK: {e}")
        # In a real app, you might want to log this error more formally
else:
    print("Warning: GOOGLE_API_KEY not set or is the placeholder value. Gemini API will not be called.")
    if not GOOGLE_API_KEY:
        print("Reason: GOOGLE_API_KEY is empty or not found in settings/environment.")
    elif GOOGLE_API_KEY == PLACEHOLDER_KEY:
        print(f"Reason: GOOGLE_API_KEY is still the placeholder value ('{PLACEHOLDER_KEY}'). Please replace it.")

# --- ---

@require_http_methods(["GET", "POST"])
def generate_content(request):
    """
    Handles GET and POST requests for generating content using the Gemini API.
    """
    generated_text = ""
    user_prompt = ""
    error_message = "" # To store potential errors

    # Check if the API key is configured before processing any request
    if not IS_GEMINI_CONFIGURED:
        # This error is set if configuration failed above
        error_message = "API Key is not configured correctly or is missing. Please check server logs and setup (settings.py or environment variables)."
        # Still get prompt if user submitted the form anyway
        if request.method == "POST":
             user_prompt = request.POST.get("prompt", "").strip()

    # Process POST request only if configured and method is POST
    elif request.method == "POST":
        user_prompt = request.POST.get("prompt", "").strip()
        if user_prompt:
            try:
                print(f"Received prompt: '{user_prompt}'") # Log received prompt
                # --- Select the Gemini Model ---
                # Model options include 'gemini-1.5-pro-latest', 'gemini-pro', 'gemini-1.5-flash-latest', etc.
                # Check available models if needed:
                # for m in genai.list_models():
                #   if 'generateContent' in m.supported_generation_methods:
                #     print(m.name)
                model = genai.GenerativeModel('gemini-1.5-flash-latest') # Use a common, available model

                # --- Optional: Set Generation Configuration ---
                # generation_config = genai.types.GenerationConfig(
                #     max_output_tokens=500,
                #     temperature=0.7
                # )
                # --- ---

                # --- Generate Content ---
                print("Sending request to Gemini API...")
                # Simple call:
                response = model.generate_content(user_prompt)

                # Call with optional config:
                # response = model.generate_content(
                #     user_prompt,
                #     generation_config=generation_config
                # )
                # --- ---
                print("Received response from Gemini API.")

                # --- Process the Response ---
                # Safer check for response text
                try:
                    generated_text = response.text.strip()
                    print(f"Generated text (first 50 chars): {generated_text[:50]}...")
                except ValueError:
                     # This can happen if the response is blocked or empty
                     generated_text = ""
                     try:
                         # Attempt to get the blocking reason
                         reason = response.prompt_feedback.block_reason.name
                         error_message = f"Content generation blocked due to: {reason}. Please adjust your prompt."
                         print(f"Content generation blocked: {reason}")
                     except (AttributeError, ValueError):
                         error_message = "Content generation failed. The response was empty or potentially blocked for an unspecified reason."
                         print("Content generation failed: Empty or blocked response.")
                except Exception as resp_err:
                    # Catch other potential errors processing the response
                    error_message = f"Error processing Gemini response: {resp_err}"
                    generated_text = ""
                    print(f"Error processing response: {resp_err}")


            except Exception as e:
                error_message = f"An error occurred calling the Gemini API: {e}"
                print(f"Gemini API call error: {e}") # Log the full error server-side
                generated_text = "" # Clear text on error
        else:
            # Handle case where POST request has an empty prompt
             error_message = "Please enter a prompt to generate content."


    # --- Prepare Context for Rendering ---
    # Ensure user_prompt is included even on GET requests if it was previously submitted (or from POST)
    context = {
        "generated_text": generated_text,
        "user_prompt": user_prompt, # Pass the prompt back to the template
        "error_message": error_message, # Pass error messages to the template
    }
    # --- Render the HTML Template ---
    return render(request, "content/content_generation.html", context)