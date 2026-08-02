# ATS Resume Scanner - Backend Prototype (with Auth + History)

## Setup
```bash
pip install -r requirements.txt
python3 -m spacy download en_core_web_sm
```

## Database
Defaults to SQLite (zero setup) — a file `ats_scanner.db` is created automatically.

To use MySQL instead:
```bash
export DATABASE_URL="mysql+pymysql://username:password@localhost:3306/ats_scanner"
```
(Create the `ats_scanner` database in MySQL first — tables are created automatically on startup.)

## Secret key
For real use, set a proper secret key instead of the dev default:
```bash
export SECRET_KEY="a-long-random-string"
```

## Run
```bash
uvicorn app:app --reload --port 8000
```
Open http://127.0.0.1:8000/docs for interactive API docs.

## Flow
1. `POST /auth/signup` — {"email", "password"} -> returns JWT
2. `POST /auth/login` — {"email", "password"} -> returns JWT
3. `POST /scan` — (Authorization: Bearer <token>) multipart form: resume (PDF), job_description (text)
4. `GET /history` — (Authorization: Bearer <token>) -> list of past scans

## Next steps
- Semantic matching upgrade with sentence-transformers (catches paraphrased skills)
- Frontend (React or plain HTML/JS) to consume this API
- Resume improvement suggestions beyond missing-keyword lists
