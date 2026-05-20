# Project Setup

## 1. Clone Repository

```bash
git clone https://github.com/AnubhavBangari3/WexaAIDashboard.git
cd WexaAIDashboard
```

---

## 2. Create Virtual Environment

### Windows

```bash
python -m venv env
env\Scripts\activate
```

### Mac/Linux

```bash
python3 -m venv env
source env/bin/activate
```

---

## 3. Install Backend Dependencies

```bash
pip install django djangorestframework djangorestframework-simplejwt
pip install psycopg2-binary python-dotenv django-cors-headers
pip install celery redis django-celery-beat
pip install pandas pydantic
pip install pytest pytest-django factory-boy
pip install gunicorn whitenoise
```

---

## 4. Save Requirements

```bash
pip freeze > requirements.txt
```

---

## 5. Create Frontend

```bash
npx create-next-app@latest frontend
```

### Selected Configuration

- TypeScript → Yes
- Tailwind CSS → Yes
- App Router → Yes
- src directory → Yes
- Import Alias → Yes

---

## 6. Install Frontend Dependencies

```bash
cd frontend

npm install axios
npm install @tanstack/react-query
npm install recharts
npm install react-hook-form
npm install jwt-decode
npm install react-hot-toast
npm install lucide-react
```