"""
Test script to verify Gemini API connection.
"""
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from .env file
load_dotenv()

def test_gemini_connection():
    """Test the connection to Gemini API."""
    # Get API key from environment variable
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        print("[ERROR] GEMINI_API_KEY not found in environment variables.")
        print("   Make sure you have a .env file with GEMINI_API_KEY set.")
        return False
    
    try:
        # Configure the API
        genai.configure(api_key=api_key)
        
        # List available models first
        print("Fetching available models...")
        models = genai.list_models()
        available_models = [m.name for m in models if 'generateContent' in m.supported_generation_methods]
        print(f"Available models: {', '.join(available_models[:5])}...")
        
        # Try using a model that's likely to have quota available
        # Prefer flash models as they're typically more available
        preferred_models = ['gemini-2.5-flash', 'gemini-1.5-flash', 'gemini-1.5-pro']
        model_name = None
        
        for pref in preferred_models:
            matching = [m for m in available_models if pref in m]
            if matching:
                model_name = matching[0]  # Use full model path
                break
        
        # Fallback to first available model if preferred not found
        if not model_name and available_models:
            model_name = available_models[0]
        else:
            model_name = available_models[0] if available_models else 'models/gemini-2.5-flash'
        
        # Extract just the model name (without 'models/' prefix) for GenerativeModel
        model_short_name = model_name.split('/')[-1] if '/' in model_name else model_name
        
        # Create a model instance
        model = genai.GenerativeModel(model_short_name)
        
        # Test with a simple prompt
        print(f"Testing Gemini API connection with model: {model_short_name}...")
        response = model.generate_content("Say 'Hello, connection successful!' in one sentence.")
        
        print("[SUCCESS] Connection successful!")
        print(f"Response: {response.text}")
        return True
        
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "quota" in error_msg.lower() or "Quota exceeded" in error_msg:
            print("[INFO] API connection is working, but quota limit has been reached.")
            print("       This means the API key is valid and the connection is successful.")
            print("       You may need to wait or upgrade your plan.")
            print(f"       Error details: {error_msg[:200]}...")
            return True  # Connection works, just quota issue
        else:
            print(f"[ERROR] Connection failed: {error_msg}")
            return False

if __name__ == "__main__":
    test_gemini_connection()


