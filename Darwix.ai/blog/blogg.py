import os
import google.generativeai as genai
from typing import List
from dotenv import load_dotenv
from transformers import pipeline

# Load environment variables
load_dotenv()

# Get API keys from environment
api_key = os.getenv('GEMINI_API_KEY')
hf_token = os.getenv('HF_TOKEN')

# Initialize HuggingFace token for auth
if hf_token:
    from huggingface_hub import login
    login(hf_token)

# Debug: Print API key (first few characters)
if api_key:
    print(f"API key loaded (first 10 chars): {api_key[:10]}...")
else:
    print("No API key found in environment variables")

def suggest_blog_titles(content: str, num_titles: int = 3) -> List[str]:
    """
    Generate blog title suggestions using Google's Gemini AI based on blog content.
    
    Args:
        content: A string containing the blog post content
        num_titles: Number of title suggestions to generate (default: 3)
        
    Returns:
        A list of suggested blog titles
    """
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables. Please check your .env file.")
    genai.configure(api_key=api_key)
    
    # Initialize the model (using Gemini 1.5 Flash)
    model = genai.GenerativeModel('gemini-1.5-pro')
    
    # Create prompt asking for the specified number of blog title suggestions
    prompt = f"""
    Based on the following blog content, suggest {num_titles} catchy, SEO-friendly title options.
    Provide exactly {num_titles} titles, numbered 1-{num_titles}.
    
    BLOG CONTENT:
    {content}
    """
    
    # Generate response
    response = model.generate_content(prompt)
    
    # Process response to extract titles
    response_text = response.text
    
    # Parse the response to extract the titles
    titles = []
    for line in response_text.strip().split('\n'):
        # Look for numbered lines (1., 2., 3., etc.)
        if line.strip() and any(line.strip().startswith(f"{i}.") for i in range(1, num_titles + 1)):
            # Remove the number and extra characters
            title = line.strip().split(".", 1)[1].strip().strip('"').strip("'")
            titles.append(title)
    
    return titles[:num_titles]  # Ensure we return exactly the requested number of titles
