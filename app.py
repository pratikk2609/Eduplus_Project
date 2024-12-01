import mysql.connector
from fastapi import FastAPI, HTTPException, UploadFile, File
import uvicorn
import os
import fitz
import json
from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain.llms import Ollama
from dotenv import load_dotenv
from mysql.connector import pooling
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import re

app = FastAPI()

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load environment variables
load_dotenv()

db_host = os.getenv('DB_HOST', 'localhost')
db_user = os.getenv('DB_USER', 'root')
db_password = os.getenv('DB_PASSWORD', 'root')
db_name = os.getenv('DB_NAME', 'resume_db')

if not db_password:
    raise ValueError("Error: DB_PASSWORD is not set.")

# Database connection pool setup
db_config = {
    'host': db_host,
    'user': db_user,
    'password': db_password,
    'database': db_name,
    'pool_name': 'resume_db_pool',
    'pool_size': 5,
}
db_pool = pooling.MySQLConnectionPool(**db_config)

# LLM Initialization
llm = Ollama(
    model="llama3.2",
    base_url="http://localhost:11434",
    temperature=0.3
)

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
        raise HTTPException(status_code=400, detail=f"Failed to extract text from PDF: {e}")

# Function to clean and deduplicate the LLM output
def clean_llm_response(raw_response: str) -> dict:
    try:
        # Use regex to locate the JSON portion in the response
        json_match = re.search(r"\{.*\}", raw_response, re.DOTALL)
        if json_match:
            json_text = json_match.group()
            return json.loads(json_text)
        else:
            raise ValueError("No valid JSON found in the LLM response.")
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse JSON: {e}. Extracted response: {json_text if 'json_text' in locals() else raw_response}")

# Function to insert data into the resume_data table in MySQL
def insert_into_db(data: dict):
    try:
        conn = db_pool.get_connection()
        cursor = conn.cursor()

        query = """
        INSERT INTO resume_data (college_name, tenth_percent, twelfth_percent, cgpa, skills)
        VALUES (%s, %s, %s, %s, %s)
        """
        values = (
            data.get("college name"),
            data.get("10th marks"),
            data.get("12th marks"),
            data.get("CGPA"),
            json.dumps(data.get("skills", []))
        )
        cursor.execute(query, values)
        conn.commit()
        cursor.close()
        conn.close()
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")

# Function to insert skills into the hr_db table in MySQL
def insert_skills_into_hr_db(skills: list):
    try:
        conn = db_pool.get_connection()
        cursor = conn.cursor()

        query = """
        INSERT INTO hr_db (skill_name)
        VALUES (%s)
        """
        # Convert skills list to JSON format for insertion
        skills_json = json.dumps(skills)
        cursor.execute(query, (skills_json,))
        conn.commit()
        cursor.close()
        conn.close()
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")

@app.post("/generate-response")
async def generate_response(file: UploadFile = File(...)):
    try:
        temp_memory = ConversationBufferWindowMemory(k=5)
        conversation = ConversationChain(llm=llm, memory=temp_memory)

        extracted_text = extract_pdf_text(file)
        hardcoded_prompt = (
            "Extract college name, 10th marks, 12th marks, CGPA, and skills from this resume text. "
            "Provide the output strictly in JSON format as follows: "
            "{\"college name\": \"name of the college\", \"10th marks\": \"marks\", \"12th marks\": \"marks\", \"CGPA\": \"value\", \"skills\": [\"skill1\", \"skill2\", \"skill3\"]}. "
        )
        full_prompt = f"{extracted_text} {hardcoded_prompt}"
        response = conversation.run(full_prompt)

        cleaned_response = clean_llm_response(response)
        insert_into_db(cleaned_response)
        return {"response": cleaned_response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/hr-skills")
async def extract_hr_skills(job_description: str):
    try:
        temp_memory = ConversationBufferWindowMemory(k=5)
        conversation = ConversationChain(llm=llm, memory=temp_memory)

        skill_prompt = (
            f"Extract the required skills from the following job description: {job_description}. "
            "Provide the skills as a list of words or short phrases in JSON format."
        )
        response = conversation.run(skill_prompt)
        skills = clean_llm_response(response)

        # Insert skills into hr_db table
        insert_skills_into_hr_db(skills)

        return {"skills": skills}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host='127.0.0.1', port=8000, reload=True)
