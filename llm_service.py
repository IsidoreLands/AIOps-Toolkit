# llm_service.py
# Version 1.0
# A simple, reusable module to interact with the Gemini API.

import os
import google.generativeai as genai
from dotenv import load_dotenv

def call_gemini(prompt_text):
    """
    Sends a prompt to the Gemini API and returns the response.

    Args:
        prompt_text (str): The text prompt to send to the model.

    Returns:
        str: The generated text from the model, or an error message.
    """
    try:
        # Load environment variables from the .env file in the current directory
        load_dotenv()

        # Get the API key from the environment variable
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            return "Error: GEMINI_API_KEY not found. Please check your .env file."

        # Configure the generative AI client with the API key
        genai.configure(api_key=api_key)

        # Create an instance of the Gemini 1.5 Flash model
        model = genai.GenerativeModel('gemini-1.5-flash')

        # Send the prompt and get the response
        response = model.generate_content(prompt_text)

        # Return the text part of the response
        return response.text

    except Exception as e:
        # Return a formatted error string if anything goes wrong
        return f"An error occurred: {e}"

# This block allows us to test the module directly
if __name__ == '__main__':
    print("--- Running llm_service.py test ---")
    
    # Define a simple test prompt
    test_prompt = "In one sentence, what is the OODA Loop?"
    print(f"Sending prompt: \"{test_prompt}\"")
    
    # Call the main function
    model_response = call_gemini(test_prompt)
    
    # Print the result
    print("\n--- Model Response ---")
    print(model_response)
    print("----------------------")
