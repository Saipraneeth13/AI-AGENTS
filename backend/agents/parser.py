import fitz  # PyMuPDF
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv

load_dotenv()

# We will use llama3-8b-8192 or llama3-70b-8192 from Groq
# Make sure GROQ_API_KEY is in the environment
llm = ChatGroq(model_name="llama3-8b-8192", temperature=0)

def parse_pdf(file_path: str) -> str:
    """Extracts text from a PDF file."""
    text = ""
    try:
        doc = fitz.open(file_path)
        for page in doc:
            text += page.get_text()
    except Exception as e:
        print(f"Error parsing PDF: {e}")
    return text

def extract_resume_details(resume_text: str):
    """Uses LLM to extract skills, experience, and roles from the resume."""
    parser = JsonOutputParser()
    
    prompt = PromptTemplate(
        template="You are an expert HR recruiter. Analyze the following resume text and extract the key skills, years of experience, and primary roles. \n\n{format_instructions}\n\nResume Text:\n{resume_text}",
        input_variables=["resume_text"],
        partial_variables={"format_instructions": "Return a JSON object with keys: 'skills' (list of strings), 'years_of_experience' (integer), 'primary_roles' (list of strings)."}
    )
    
    chain = prompt | llm | parser
    
    try:
        result = chain.invoke({"resume_text": resume_text})
        return result
    except Exception as e:
        print(f"Error extracting details: {e}")
        return {"skills": [], "years_of_experience": 0, "primary_roles": []}

if __name__ == "__main__":
    # Test block
    print("Parser agent ready.")
