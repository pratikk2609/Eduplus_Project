from fastapi import FastAPI, HTTPException, UploadFile, File
import uvicorn
import os
import fitz  # PyMuPDF for PDF text extraction
import json
from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain_groq import ChatGroq
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

groq_api_key = os.getenv('GROQ_API_KEY', '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')

if not groq_api_key:
    raise ValueError("Error: GROQ_API_KEY is not set.")

FIXED_MODEL_NAME = 'llama-3.2-1b-preview'

# FastAPI app instance
app = FastAPI()

# Function to extract text from a PDF
def extract_pdf_text(pdf_file: UploadFile) -> str:
    try:
        pdf_document = fitz.open(stream=pdf_file.file.read(), filetype="pdf")
        text = ""
        for page in pdf_document:
            text += page.get_text()
        pdf_document.close()
        one_line_text = " ".join(text.split())
        return one_line_text
    except Exception as e:
        raise ValueError(f"Failed to extract text from PDF: {e}")

# Function to clean and deduplicate the LLM output
def clean_llm_response(raw_response: str) -> dict:
    if not raw_response:
        raise ValueError("LLM response is empty.")
    try:
        parsed_response = json.loads(raw_response)
        cleaned_response = {}
        for key, value in parsed_response.items():
            if key not in cleaned_response:
                cleaned_response[key] = value
        return cleaned_response
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to process LLM response: {e}. Raw response: {raw_response}")

# Define the FastAPI endpoint
@app.post("/generate-response")
async def generate_response(file: UploadFile = File(...)):
    try:
        # Create a temporary memory for the current request
        temp_memory = ConversationBufferWindowMemory(k=5)

        # Initialize a new conversation chain with temporary memory
        conversation = ConversationChain(
            llm=ChatGroq(api_key=groq_api_key, model_name=FIXED_MODEL_NAME),
            memory=temp_memory
        )

        # Extract text from the uploaded PDF
        extracted_text = extract_pdf_text(file)
        
        # Refined prompt for JSON output
        hardcoded_prompt = (
            " Extract college name, 10th marks, 12th marks, CGPA from this text of resume. "
            "Provide the output strictly in JSON format as follows: "
            "{\"college name\": \"name of the college\", \"10th marks\": \"marks\", \"12th marks\": \"marks\", \"CGPA\": \"value\"}. "
            "Ensure valid JSON output and do not include duplicates or additional information."
        )
        full_prompt = f"{extracted_text}{hardcoded_prompt}"

        # Get the response from the conversation chain
        response = conversation(full_prompt)
        raw_response = response['response']
        
        # Debugging: Log the raw response
        print(f"Raw LLM response: {raw_response}")

        # Process the response to remove duplicates and validate JSON
        cleaned_response = clean_llm_response(raw_response)
        
        # Return the cleaned response
        return {"response": cleaned_response}

    except ValueError as e:
        # Handle specific value errors gracefully
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Catch-all for unexpected exceptions
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host='127.0.0.1', port=8000, reload=True)
