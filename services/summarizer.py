import logging
from services.gemini_client import GeminiClient

logger = logging.getLogger(__name__)

class Summarizer:
    """Service to handle text summarization logic."""
    
    def __init__(self):
        """Initialize the summarizer with a Gemini client."""
        self.gemini_client = GeminiClient()
    
    def summarize_text(self, text: str) -> str:
        """Summarize the given text using Gemini AI.
        
        Args:
            text: The text content to summarize
            
        Returns:
            A summary of the text
        """
        try:
            # Use the Gemini client to generate a summary
            summary = self.gemini_client.generate_summary(text)
            return summary
        except Exception as e:
            logger.error(f"Error in summarize_text: {str(e)}")
            raise
    
    def extract_key_points(self, text: str, max_points: int = 5) -> list:
        """Extract key points from the text.
        
        Args:
            text: The text to extract key points from
            max_points: Maximum number of key points to extract
            
        Returns:
            A list of key points
        """
        try:
            # Construct a prompt to extract key points
            prompt = f"""Extract the {max_points} most important key points from the following text:

{text}

Format your response as a list, with each key point clearly and briefly stated.
"""
            
            # Use the Gemini client to process the prompt
            response = self.gemini_client._make_api_call(prompt)
            key_points_text = response.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')
            
            # Process the response into a list
            key_points = [point.strip() for point in key_points_text.split('\n') if point.strip()]
            
            # Remove any list markers like "1.", "-", "*" etc.
            import re
            key_points = [re.sub(r'^\s*[\d\-\*]+\.?\s*', '', point) for point in key_points]
            
            return key_points[:max_points]
            
        except Exception as e:
            logger.error(f"Error in extract_key_points: {str(e)}")
            raise
    
    def categorize_content(self, text: str) -> dict:
        """Categorize the content into different topics or sections.
        
        Args:
            text: The text to categorize
            
        Returns:
            A dictionary with categories and their relevant content
        """
        try:
            # Construct a prompt to categorize content
            prompt = f"""Analyze the following study material and categorize it into 3-5 main topics or sections:

{text}

For each category/topic, provide:
1. A clear title for the category
2. A brief summary of what this category covers
3. The key points within this category

Format your response as a JSON object with this structure:
{{
  "categories": [
    {{
      "title": "Category Title",
      "summary": "Brief summary of this category",
      "key_points": ["Point 1", "Point 2", "Point 3"]
    }}
  ]
}}
"""
            
            # Use the Gemini client to process the prompt
            response = self.gemini_client._make_api_call(prompt)
            response_text = response.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')
            
            # Extract JSON from the response text
            import json
            # Sometimes the API includes markdown code blocks, so we need to handle that
            if "```json" in response_text:
                json_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                json_text = response_text.split("```")[1].strip()
            else:
                json_text = response_text
            
            categories = json.loads(json_text)
            
            return categories
            
        except Exception as e:
            logger.error(f"Error in categorize_content: {str(e)}")
            raise
