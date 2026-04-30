# MedMemory AI

## Project Structure

```
/backend
  main.py
  requirements.txt
/frontend
  package.json
  /public/index.html
  /src/App.js
  /src/index.js
```

## Backend Setup

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

## Frontend Setup

```bash
cd frontend
npm install
npm start
```

Frontend runs at `http://localhost:3000` and calls backend `http://localhost:8000/analyze`.
