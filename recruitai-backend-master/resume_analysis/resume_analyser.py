import os

import docx2txt
import pyrebase
from celery import shared_task
from celery.utils.log import get_task_logger
from django.conf import settings
from pdf2docx import parse
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

job_desc_path = str(settings.BASE_DIR) + "/proj_files/JobDesc.pdf"
resume_path = str(settings.BASE_DIR) + "/proj_files/resume.pdf"
job_desc_docx_path = str(settings.BASE_DIR) + "/proj_files/JobDesc.docx"
resume_docx_path = str(settings.BASE_DIR) + "/proj_files/resume.docx"


def clean_directory_resume():
    if os.path.isfile(job_desc_path):
        os.remove(job_desc_path)
    if os.path.isfile(resume_path):
        os.remove(resume_path)
    if os.path.isfile(job_desc_docx_path):
        os.remove(job_desc_docx_path)
    if os.path.isfile(resume_docx_path):
        os.remove(resume_docx_path)


def ResumeAnalyzer(applicant_resume_pdf, job_description_pdf):
    applicant_resume_docx = resume_docx_path

    job_description_docx = job_desc_docx_path

    parse(applicant_resume_pdf, applicant_resume_docx, start=0, end=None)
    parse(job_description_pdf, job_description_docx, start=0, end=None)

    result1 = docx2txt.process(applicant_resume_docx)
    result2 = docx2txt.process(job_description_docx)

    text = [result1, result2]

    cv = CountVectorizer()
    count_matrix = cv.fit_transform(text)
    match_percentage = cosine_similarity(count_matrix)[0][1] * 100
    match_percentage = round(match_percentage, 2)
    return match_percentage


logger = get_task_logger(__name__)


@shared_task(name="analyse_resume")
def process_resume(userid, companyid):
    clean_directory_resume()

    firebaseConfig = {
        "apiKey": "AIzaSyBZReE0HUqcTKagQCPU5HwDrKrBJsW787A",
        "authDomain": "recruit-ai-cb3c1.firebaseapp.com",
        "projectId": "recruit-ai-cb3c1",
        "databaseURL": "https://recruit-ai-cb3c1-default-rtdb.firebaseio.com",
        "storageBucket": "recruit-ai-cb3c1.appspot.com",
        "messagingSenderId": "1012646425167",
        "appId": "1:1012646425167:web:e9c3d8c58927d64078303a",
        "measurementId": "G-G87J196BTV",
        "serviceAccount": str(settings.BASE_DIR) + "/proj_files/serviceAccountKey.json",
    }

    firebase = pyrebase.initialize_app(firebaseConfig)
    db = firebase.database()
    storage = firebase.storage()

    jobdesc = "company/" + companyid + '/job_desc.pdf'
    resume = "users/" + userid + '/user_resume.pdf'

    storage.child(resume).download(resume_path)
    
    storage.child(jobdesc).download( job_desc_path)

    resume_score = ResumeAnalyzer(resume_path, job_desc_path)

    db.child("Jobs").child(companyid).child("Juser").child(userid).child("resume_score").set(resume_score)
    db.child("Jobs").child(companyid).child("Juser").child(userid).child("status").set("Resume Processed")

    clean_directory_resume()
    logger.info("Resume Processed")

    return resume_score