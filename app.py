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
from typing import List
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


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

# SQLAlchemy setup for MySQL database
Base = declarative_base()
encoded_password = 'root'  # URL-encoded password
engine = create_engine(f'mysql+mysqlconnector://root:{encoded_password}@localhost/resume_db')
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Define Resume model for SQLAlchemy
class Resume(Base):
    __tablename__ = 'resume_data'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
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
    name: str
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
# Replace "%" with "." in the JSON response processing function
def clean_llm_response(raw_response: str) -> dict:
    try:
        # Locate JSON portion in the response
        json_match = re.search(r"\{.*\}", raw_response, re.DOTALL)
        if json_match:
            json_text = json_match.group()
            json_text = json_text.replace('%', '')  # Remove '%' for JSON parsing
            return json.loads(json_text)
        else:
            raise ValueError("No valid JSON found in the LLM response.")
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse JSON: {e}. Extracted response: {json_text if 'json_text' in locals() else raw_response}")

# Ensure column and key names are consistent
def insert_into_db(data: dict):
    try:
        conn = db_pool.get_connection()
        cursor = conn.cursor()

        query = """
        INSERT INTO resume_data (name, college_name, tenth_percent, twelfth_percent, cgpa, skills)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        values = (
            data.get("name"),
            data.get("college name"),
            data.get("10th percentage"),
            data.get("12th or diploma percentage"),
            data.get("CGPA"),
            json.dumps(data.get("skills", []))  # Convert skills to JSON string
        )
        cursor.execute(query, values)
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


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
            "Extract name, college name, 10th percentage, 12th percentage, CGPA, and skills from this resume text. "
            "Provide the output strictly in JSON format as follows: "
            "{\"name\": \"name\",\"college name\": \"name of the college\", \"10th percentage\": \"percentage\", \"12th or diploma percentage\": \"percentage\", \"CGPA\": \"value\", \"skills\": [\"skill1\", \"skill2\", \"skill3\"]}. "
            "For skills, include both explicitly mentioned skills and inferred skills based on projects and internships in the resume. "
            "In the resume either 12th percentage is present or diploma percentage will be present , extract one of the percentage present. Don't confuse diploma percentage with 10th percentage"
            "for 12th percentage in resume , 12th may also be written as HSC so extract the percentage of hsc if 12th not written "
            "for 10th percentage in resume , 10th may also be written as SSC so extract the percentage of ssc if 10th not written "
            "Ensure valid JSON output and do not include duplicates or additional information. If the specified detail is not present, write it as null or an empty list."
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
    
from fastapi import HTTPException, Depends
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy.orm import Session
from typing import List
from sqlalchemy import text
import json

@app.post("/rank-students")
async def rank_students(
    min10th: float,
    min12th: float,
    minCGPA: float,
    db: Session = Depends(get_db)
):
    try:
        # Fetch resumes that match the provided filters for 10th, 12th percentage, and CGPA
        query_str = f"""
            SELECT id, name, skills, resume_path
            FROM resume_data 
            WHERE tenth_percent >= :min10th 
              AND twelfth_percent >= :min12th 
              AND cgpa >= :minCGPA
        """

        # Execute the query to fetch the matching resumes
        query = text(query_str)
        results = db.execute(
            query, 
            {"min10th": min10th, "min12th": min12th, "minCGPA": minCGPA}
        ).fetchall()

        if not results:
            return {"message": "No resumes found matching the criteria"}

        # Extract skills and resume path for each resume and create a list
        resumes = [
            {
                "id": row.id,
                "name": row.name,
                "skills": json.loads(row.skills),  # Skills are stored as JSON
                "resume_path": row.resume_path
            }
            for row in results
        ]

        # Now, extract HR skills based on the job description (example job description, can be dynamic)
        job_description = "We are looking for a software engineer with skills in Python, Java, and Machine Learning."
        job_description_skills = extract_skills_from_job_description(job_description)

        # Create a list to store cosine similarity scores
        cosine_scores = []

        # Prepare the TfidfVectorizer to convert text to vector representation
        tfidf_vectorizer = TfidfVectorizer(stop_words="english")

        # Process the skills and job description for similarity calculation
        job_description_str = " ".join(job_description_skills)

        for resume in resumes:
            # Convert the student's skills into a string (comma-separated)
            resume_skills_str = " ".join(resume["skills"])

            # Combine job description and resume skills for similarity calculation
            text_to_compare = [job_description_str, resume_skills_str]
            tfidf_matrix = tfidf_vectorizer.fit_transform(text_to_compare)
            
            # Calculate cosine similarity
            similarity_score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            cosine_scores.append((resume["name"], similarity_score, resume["resume_path"]))

        # Sort students based on cosine similarity score in descending order
        cosine_scores.sort(key=lambda x: x[1], reverse=True)

        # Return the ranked students based on cosine similarity
        ranked_students = [
            {"name": student[0], "similarity_score": student[1], "resume_path": student[2]} 
            for student in cosine_scores
        ]

        return {"ranked_students": ranked_students}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

    

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
