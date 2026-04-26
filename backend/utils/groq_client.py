"""
Groq LLM client helper for robust JSON generation.
"""
import os
import json
import re
from dotenv import load_dotenv
from langchain_groq import ChatGroq

# Load environment variables from .env file
load_dotenv()

# Assumes GROQ_API_KEY is in environment variables or .env file
# Uses llama-3.3-70b-versatile for high reasoning capabilities
try:
    llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.2)
except Exception as e:
    print(f"Warning: Failed to initialise ChatGroq. Check GROQ_API_KEY. Error: {e}")
    llm = None

async def call_llm_json(system_prompt: str, user_prompt: str) -> dict:
    """
    Invokes the LLM and forces JSON parsing. 
    Strips markdown formatting if present.
    """
    if not llm:
        print("LLM not configured.")
        return {}
        
    messages = [
        ("system", system_prompt),
        ("human", user_prompt),
    ]
    
    try:
        response = await llm.ainvoke(messages)
        content = response.content.strip()
        
        # Strategy 1: Direct parse
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            pass
            
        # Strategy 2: Remove markdown block ticks
        clean_content = re.sub(r'```(?:json)?\n?(.*?)\n?```', r'\1', content, flags=re.DOTALL).strip()
        try:
            return json.loads(clean_content)
        except json.JSONDecodeError:
            pass
            
        # Strategy 3: Find first { to last }
        match = re.search(r'(\{.*\})', clean_content, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass
                
        print(f"Failed to parse JSON using all strategies. Raw Content: {content}")
        return {}
        
    except Exception as e:
        print(f"LLM API Error: {e}")
        return {}
