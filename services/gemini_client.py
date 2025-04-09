from config import GEMINI_API_KEY
import json
import logging
import requests
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class GeminiClient:
    """Client for interacting with Google's Gemini API."""
    
    def __init__(self):
        """Initialize the Gemini client with API key from environment."""
        self.api_key = GEMINI_API_KEY
        if not self.api_key:
            logger.warning("GEMINI_API_KEY environment variable not set. API calls will fail.")
        
        self.api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
    
    def _make_api_call(self, prompt: str) -> Dict[str, Any]:
        """Make a request to the Gemini API.
        
        Args:
            prompt: The text prompt to send to the API
            
        Returns:
            The JSON response from the API
            
        Raises:
            Exception: If the API call fails
        """
        if not self.api_key:
            raise ValueError("Gemini API key not configured. Please set the GEMINI_API_KEY environment variable.")
        
        # Construct the API request payload
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ]
        }
        
        # Make the API call
        response = requests.post(
            f"{self.api_url}?key={self.api_key}",
            headers={"Content-Type": "application/json"},
            json=payload
        )
        
        # Check for successful response
        if response.status_code != 200:
            logger.error(f"Gemini API error: {response.status_code} - {response.text}")
            raise Exception(f"API request failed with status code {response.status_code}: {response.text}")
        
        return response.json()
    
    def generate_summary(self, content: str) -> str:
        """Generate a summary of the provided content.
        
        Args:
            content: The text content to summarize
            
        Returns:
            A concise summary of the content
        """
        prompt = f"""Please provide a concise but comprehensive summary of the following study material:

{content}

The summary should:
1. Highlight the main ideas and concepts
2. Include key facts and important details
3. Be organized in a clear, logical structure
4. Be suitable for a student reviewing this material
"""
        
        try:
            response = self._make_api_call(prompt)
            # Extract the generated text from the response
            summary = response.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')
            
            if not summary:
                raise ValueError("Received empty summary from API")
                
            return summary
            
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            raise
    
    def generate_quiz(self, content: str, question_count: int = 5, difficulty: str = "medium") -> Dict[str, Any]:
        """Generate a quiz based on the content.
        
        Args:
            content: The text content to generate questions from
            question_count: The number of questions to generate
            difficulty: The difficulty level (easy, medium, hard)
            
        Returns:
            A dictionary containing quiz questions, options, and answers
        """
        prompt = f"""Create a {difficulty} difficulty quiz with {question_count} multiple-choice questions based on the following study material:

{content}

Format your response as valid JSON with the following structure:
{{
  "questions": [
    {{
      "question": "Question text here?",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "correct_answer": "Option A",
      "explanation": "Why this answer is correct"
    }}
  ]
}}

Make sure each question tests understanding, not just memorization. Include an explanation for each correct answer.
"""
        
        try:
            response = self._make_api_call(prompt)
            # Extract the generated text from the response
            response_text = response.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')
            
            if not response_text:
                raise ValueError("Received empty response from API")
            
            # Extract JSON from the response text
            # Sometimes the API includes markdown code blocks, so we need to handle that
            if "```json" in response_text:
                json_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                json_text = response_text.split("```")[1].strip()
            else:
                json_text = response_text
            
            quiz_data = json.loads(json_text)
            
            # Validate the structure
            if "questions" not in quiz_data or not isinstance(quiz_data["questions"], list):
                raise ValueError("Invalid quiz data structure received from API")
                
            return quiz_data
            
        except Exception as e:
            logger.error(f"Error generating quiz: {str(e)}")
            raise
    
    def generate_explanation(self, topic: str, context: Optional[str] = None) -> str:
        """Generate a detailed explanation of a topic.
        
        Args:
            topic: The topic or concept to explain
            context: Optional additional context or material
            
        Returns:
            A detailed explanation of the topic
        """
        if context:
            prompt = f"""Please provide a detailed explanation of the following topic/concept:

Topic: {topic}

Use the following context or study material to inform your explanation:
{context}

Your explanation should:
1. Break down complex ideas into simpler components
2. Use examples to illustrate key points
3. Explain any relevant terminology
4. Connect this topic to broader concepts where relevant
5. Include a summary of the main points at the end
"""
        else:
            prompt = f"""Please provide a detailed explanation of the following topic/concept:

Topic: {topic}

Your explanation should:
1. Break down complex ideas into simpler components
2. Use examples to illustrate key points
3. Explain any relevant terminology
4. Connect this topic to broader concepts where relevant
5. Include a summary of the main points at the end
"""
        
        try:
            response = self._make_api_call(prompt)
            # Extract the generated text from the response
            explanation = response.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')
            
            if not explanation:
                raise ValueError("Received empty explanation from API")
                
            return explanation
            
        except Exception as e:
            logger.error(f"Error generating explanation: {str(e)}")
            raise
