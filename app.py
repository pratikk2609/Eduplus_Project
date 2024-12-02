from fastapi import FastAPI, HTTPException, UploadFile, File, Query
from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain.llms import Ollama
from dotenv import load_dotenv
from mysql.connector import pooling
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine, Column, Integer, Float, String, JSON as SQLJSON, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from typing import List
import os
import json
import re
import fitz
import uvicorn
from fastapi import Depends
from sqlalchemy import text


# FastAPI app setup
app = FastAPI()

# CORS configuration
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
db_password = os.getenv('DB_PASSWORD', 'Gauri@2004')
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

# SQLAlchemy setup for MySQL database
Base = declarative_base()
encoded_password = 'Gauri%402004'  # URL-encoded password
engine = create_engine(f'mysql+mysqlconnector://root:{encoded_password}@localhost/resume_db')
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Define Resume model for SQLAlchemy
class Resume(Base):
    __tablename__ = 'resume_data'
    id = Column(Integer, primary_key=True, index=True)
    college_name = Column(String(255))
    marks_10th = Column(Float)
    marks_12th = Column(Float)
    cgpa = Column(Float)
    skills = Column(SQLJSON)  # Storing skills as a JSON list

# Create the table in the database
Base.metadata.create_all(bind=engine)

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic model for response validation
class ResumeSchema(BaseModel):
    id: int
    college_name: str
    marks_10th: float
    marks_12th: float
    cgpa: float
    skills: List[str]

    class Config:
        orm_mode = True


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

# Pydantic model to validate incoming request data for job descriptions
class JobDescriptionRequest(BaseModel):
    job_title: str  # Add job_title field
    job_description: str

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
async def extract_hr_skills(request: JobDescriptionRequest):
    try:
        job_title = request.job_title  # Now you can access the job title
        job_description = request.job_description  # Extract job description from the request
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

        # Optionally, you can also insert the job_title into a database if needed
        # For example, insert_job_title(job_title)

        return {"skills": skills}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/fetch-resumes")
def fetch_resumes(
    min10th: float,
    min12th: float,
    minCGPA: float,
    skills: str = "",
    db: Session = Depends(get_db)
):
    try:
        # Convert skills into a list and strip spaces
        skills_list = [skill.strip() for skill in skills.split(",") if skill.strip()]

        # Start the query with basic conditions for 10th, 12th, and CGPA
        query_str = f"""
            SELECT id, college_name, tenth_percent AS marks_10th, 
                   twelfth_percent AS marks_12th, cgpa, skills 
            FROM resume_data 
            WHERE tenth_percent >= :min10th 
              AND twelfth_percent >= :min12th 
              AND cgpa >= :minCGPA 
        """

        # Add skills filtering conditions if provided
        if skills_list:
            skills_conditions = " AND ".join(
                [f"skills LIKE '%{skill}%'" for skill in skills_list]
            )
            query_str += f" AND ({skills_conditions})"

        # Prepare the query and execute it
        query = text(query_str)
        results = db.execute(
            query, 
            {"min10th": min10th, "min12th": min12th, "minCGPA": minCGPA}
        ).fetchall()

        # If no results, return a message
        if not results:
            return {"message": "No resumes found matching the criteria"}

        # Map results to a dictionary or schema
        resumes = [
            {
                "id": row.id,
                "college_name": row.college_name,
                "marks_10th": row.marks_10th,
                "marks_12th": row.marks_12th,
                "cgpa": row.cgpa,
                "skills": json.loads(row.skills),
            }
            for row in results
        ]

        return resumes

    except Exception as e:
        # Handle any errors and return a 500 response
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)