"""
Test script to verify OpenAI API connection.
"""
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

def test_openai_connection():
    """Test the connection to OpenAI API."""
    # Get API key from environment variable
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("[ERROR] OPENAI_API_KEY not found in environment variables.")
        print("   Make sure you have a .env file with OPENAI_API_KEY set.")
        return False
    
    try:
        # Create OpenAI client
        client = OpenAI(api_key=api_key)
        
        # Test with a simple prompt
        print("Testing OpenAI API connection...")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "Say 'Hello, connection successful!' in one sentence."}
            ],
            max_tokens=50
        )
        
        print("[SUCCESS] Connection successful!")
        print(f"Response: {response.choices[0].message.content}")
        print(f"Model used: {response.model}")
        return True
        
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "unauthorized" in error_msg.lower():
            print("[ERROR] Authentication failed. Please check your API key.")
            print(f"       Error details: {error_msg[:200]}...")
            return False
        elif "429" in error_msg or "quota" in error_msg.lower() or "rate limit" in error_msg.lower():
            print("[INFO] API connection is working, but rate limit/quota has been reached.")
            print("       This means the API key is valid and the connection is successful.")
            print("       You may need to wait or upgrade your plan.")
            print(f"       Error details: {error_msg[:200]}...")
            return True  # Connection works, just quota issue
        else:
            print(f"[ERROR] Connection failed: {error_msg}")
            return False

if __name__ == "__main__":
    test_openai_connection()

