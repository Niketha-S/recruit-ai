# Recruit AI

An AI-powered recruitment platform that automates candidate evaluation through **resume analysis** and **video interview analysis**. The system uses machine learning to score resumes against job descriptions, analyze facial expressions for confidence, perform speech-to-text transcription, and detect emotions from audio — giving recruiters data-driven insights into each applicant.

## Architecture

```
┌─────────────────────┐        REST API        ┌─────────────────────────┐
│   Android App       │ ◄────────────────────►  │   Django Backend        │
│   (Java/Kotlin)     │                         │   (DRF + Celery)        │
└────────┬────────────┘                         └────────┬────────────────┘
         │                                               │
         │   Upload resume/video                         │  Background tasks
         ▼                                               ▼
┌─────────────────────┐                         ┌─────────────────────────┐
│   Firebase           │                         │   RabbitMQ              │
│   - Auth             │                         │   (Message Broker)      │
│   - Realtime DB      │                         └─────────────────────────┘
│   - Storage          │
└──────────────────────┘
```

**Frontend:** Native Android app (Java/Kotlin) with Firebase Auth, CameraX for video recording, and Retrofit for API calls.

**Backend:** Django + Django REST Framework with Celery for async task processing. Uses TensorFlow/Keras models for facial emotion recognition and audio sentiment analysis, OpenCV for face detection, and scikit-learn for resume matching.

## Features

- **User & Company Registration** — Firebase-authenticated signup/login for both applicants and recruiters
- **Job Posting** — Companies can post jobs with descriptions (PDF)
- **Resume Analysis** — Cosine similarity matching between applicant resume and job description using CountVectorizer
- **Video Interview** — In-app video recording with question prompts via CameraX
- **Confidence Scoring** — Frame-by-frame facial analysis using a trained CNN model (Haar cascades + Keras)
- **Emotion Detection** — Audio analysis using MFCC features to classify emotions (neutral, happy, sad, angry, fearful, disgusted, surprised)
- **Speech-to-Text** — Google Speech Recognition API transcription of interview audio
- **Results Dashboard** — Recruiters view resume scores, confidence scores, emotion breakdown, and transcripts per applicant

---

## Prerequisites

### Backend
- Python 3.8 or 3.10
- RabbitMQ server
- Firebase project with Realtime Database, Storage, and Authentication enabled
- Firebase Service Account Key (`serviceAccountKey.json`)
- Pre-trained model files (`mymodelhistory1.h5`, `andioAnalysisModel.h5`)

### Frontend
- Android Studio (Arctic Fox or later)
- Android SDK 30
- A `google-services.json` file from your Firebase project

---

## How to Run

### Backend Setup

1. **Clone the repo**
   ```bash
   git clone https://github.com/Niketha-S/recruit-ai.git
   cd recruit-ai/recruitai-backend-master
   ```

2. **Create a virtual environment and install dependencies**
   ```bash
   python -m venv venv
   source venv/bin/activate        # Linux/Mac
   venv\Scripts\activate           # Windows
   pip install -r requirements.txt
   ```

3. **Add required files to `proj_files/`**

   These files are not included in the repo for security/size reasons. You need to add them manually:
   ```
   proj_files/
   ├── serviceAccountKey.json      # Firebase service account credentials
   ├── mymodelhistory1.h5          # Facial emotion recognition model
   └── andioAnalysisModel.h5       # Audio emotion analysis model
   ```
   - Get `serviceAccountKey.json` from Firebase Console → Project Settings → Service Accounts → Generate New Private Key
   - The `.h5` model files must be trained separately or obtained from the project owner

4. **Install and start RabbitMQ**
   ```bash
   # Ubuntu
   sudo apt install rabbitmq-server
   sudo systemctl start rabbitmq-server
   sudo systemctl enable rabbitmq-server

   # macOS (Homebrew)
   brew install rabbitmq
   brew services start rabbitmq

   # Windows — download from https://www.rabbitmq.com/download.html
   ```

5. **Run database migrations**
   ```bash
   python manage.py migrate
   ```

6. **Start the Celery worker** (in a separate terminal)
   ```bash
   celery -A recruitai_backend worker -l info
   ```

7. **Start the Django development server**
   ```bash
   python manage.py runserver 0.0.0.0:8000
   ```

The backend will be available at `http://localhost:8000/`.

### Frontend Setup

1. **Open in Android Studio**
   ```
   File → Open → select the recruitai-frontend-master/ folder
   ```

2. **Add Firebase config**

   Place your `google-services.json` in:
   ```
   recruitai-frontend-master/app/google-services.json
   ```

3. **Update the backend URL**

   In `API.java` and any Retrofit base URL references, update the server address to point to your running backend (e.g., `http://<your-ip>:8000/`).

4. **Build and run** on an emulator or physical device (min SDK 23 / Android 6.0).

---

## API Endpoints

| Method | Endpoint | Params | Description |
|--------|----------|--------|-------------|
| GET | `/analyse/resume/` | `userid`, `companyid` | Triggers async resume analysis via Celery |
| GET | `/analyse/interview/` | `userid`, `companyid` | Triggers async video interview analysis via Celery |

Both endpoints return immediately with a status message. Results are written to Firebase Realtime Database asynchronously.

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Mobile App | Java, Kotlin, Android SDK 30, CameraX, Retrofit, MPAndroidChart |
| Backend | Python, Django 4.0, Django REST Framework, Celery |
| ML/AI | TensorFlow/Keras, OpenCV, scikit-learn, librosa, SpeechRecognition |
| Database | Firebase Realtime Database, SQLite (Django local) |
| Storage | Firebase Cloud Storage |
| Auth | Firebase Authentication |
| Message Broker | RabbitMQ (via AMQP) |

---

## Project Structure

```
recruit-ai/
├── recruitai-backend-master/
│   ├── manage.py
│   ├── requirements.txt
│   ├── recruitai_backend/          # Django project config
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── celery.py
│   │   └── wsgi.py
│   ├── resume_analysis/            # Resume scoring app
│   │   ├── views.py
│   │   ├── resume_analyser.py      # PDF → docx → cosine similarity
│   │   └── urls.py
│   ├── interview_analysis/         # Interview processing app
│   │   ├── views.py
│   │   ├── interview_analyser.py   # Video, audio, speech analysis
│   │   └── urls.py
│   └── proj_files/                 # Models & cascades (not in repo)
│       ├── haarcascade_frontalface_default.xml
│       ├── haarcascade_eye.xml
│       ├── mymodelhistory1.h5
│       ├── andioAnalysisModel.h5
│       └── serviceAccountKey.json
│
└── recruitai-frontend-master/
    ├── app/
    │   ├── build.gradle
    │   ├── src/main/
    │   │   ├── AndroidManifest.xml
    │   │   ├── java/com/example/recruitai/
    │   │   │   ├── MainActivity.java       # Splash screen
    │   │   │   ├── Signup.java             # Role selection
    │   │   │   ├── UserLogin.java          # Applicant auth
    │   │   │   ├── CompanyLogin.java       # Recruiter auth
    │   │   │   ├── User.java               # Applicant dashboard
    │   │   │   ├── Company.java            # Recruiter dashboard
    │   │   │   ├── PostJob.java            # Job posting
    │   │   │   ├── Interview.java          # Video interview
    │   │   │   ├── FinalAnalysis.java       # Results display
    │   │   │   ├── API.java                # Retrofit interface
    │   │   │   └── Model/                  # Data classes
    │   │   └── res/                        # Layouts, drawables, values
    │   └── google-services.json            # Firebase config (not in repo)
    ├── build.gradle
    ├── gradlew / gradlew.bat
    └── settings.gradle
```

---

## License

This project is for educational purposes.