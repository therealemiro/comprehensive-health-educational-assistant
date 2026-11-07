# Comprehensive Health Educational Assistant
# دستیار جامع آموزش سلامت

> **Academic Final-Year Bachelor's Project | پروژه پایانی کارشناسی**

A bilingual (Persian/English) educational health assistant built with a Retrieval-Augmented Generation (RAG) pipeline. The system retrieves relevant information from a medical knowledge base and uses a locally hosted language model through Ollama to generate contextual educational answers.

یک دستیار آموزشی سلامت دو‌زبانه (فارسی/انگلیسی) که با معماری تولید تقویت‌شده با بازیابی (RAG) توسعه داده شده است. سیستم ابتدا اطلاعات مرتبط را از پایگاه دانش پزشکی بازیابی می‌کند و سپس با استفاده از یک مدل زبانی محلی از طریق Ollama، پاسخ آموزشی متناسب با پرسش تولید می‌کند.

---

## Contents | فهرست مطالب

- [English](#english)
- [فارسی](#فارسی)

---

# English

## 1. Project Overview

The Comprehensive Health Educational Assistant is an academic project designed to provide general educational information about health, medications, and medical topics. It is not intended to diagnose medical conditions, prescribe treatments, or replace professional medical advice.

The application combines a React frontend, a FastAPI backend, a relational database, and a RAG-based question-answering pipeline.

## 2. Main Features

- User registration and login.
- Password hashing and JWT-based authentication.
- Rate limiting on login attempts.
- Chat creation, listing, renaming, and deletion.
- Persistent chat messages and reply-to-message support.
- Like/dislike feedback on assistant responses.
- Downloading a conversation as a text file.
- Persian and English question answering.
- Dense semantic retrieval using FAISS.
- Sparse keyword retrieval using BM25.
- Hybrid retrieval that combines dense and sparse search results.
- Cross-Encoder reranking of retrieved passages.
- Local response generation through Ollama (default model: `qwen3:8b`).
- Evaluation utilities for retrieval and answer-generation performance.
- Logging utilities for application interactions.

## 3. Technology Stack

| Layer | Technologies |
|---|---|
| Frontend | React 18, Vite, JavaScript, CSS |
| Backend | Python, FastAPI, Uvicorn |
| Data validation | Pydantic |
| Database / ORM | MySQL or SQLite, SQLAlchemy |
| Authentication | JWT, Passlib, bcrypt |
| Retrieval | Sentence Transformers, FAISS, BM25 |
| Reranking | Sentence Transformers Cross-Encoder |
| Language model runtime | Ollama |
| Data processing | Hugging Face Datasets, NumPy |
| Markdown rendering | Marked, DOMPurify |

## 4. Repository Structure

```text
Final_Project/
├── backend/
│   ├── app/
│   │   ├── auth/              # Registration, login, authentication dependencies
│   │   ├── chats/             # Chat and message endpoints
│   │   ├── rag/               # Retrieval, hybrid search, reranking, prompts, LLM client
│   │   ├── config.py          # Application configuration
│   │   ├── database.py        # SQLAlchemy database setup
│   │   ├── main.py            # FastAPI application entry point
│   │   ├── models.py          # Database models
│   │   └── schemas.py         # Pydantic schemas
│   ├── evaluate.py            # RAG evaluation runner
│   ├── requirements.txt
│   ├── run_backend.sh
│   └── run_eval.sh
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── api.js
│   │   ├── App.jsx
│   │   └── styles.css
│   ├── package.json
│   └── vite.config.js
├── scripts/
│   ├── download_medical_datasets.py
│   ├── process_external_datasets_filtered.py
│   ├── merge_datasets.py
│   ├── prepare_finetune_pairs.py
│   ├── finetune_embedding.py
│   ├── build_vector_index.py
│   └── build_bm25_index.py
├── .env.example
├── .gitignore
└── README.md
```

## 5. Requirements

- Python 3.10 or newer.
- Node.js and npm.
- Ollama installed and running locally.
- A compatible Ollama model (the default configuration uses `qwen3:8b`).
- MySQL if you choose MySQL instead of the SQLite development database.
- The generated datasets, indexes, and model files described in the Data and Model Setup section.

The archive supplied with this repository contains source code only. It does **not** include the generated medical datasets, FAISS/BM25 indexes, fine-tuned embedding model, or local Cross-Encoder model files. These assets must be prepared separately before the complete RAG chat flow can run.

## 6. Configuration and Environment Variables

Create the local environment file from the example stored at the repository root:

```bash
cp .env.example backend/.env
```

Edit `backend/.env` and configure the database URL and a new random secret key.

Example using SQLite for local development:

```env
DATABASE_URL=sqlite:///./health_assistant.db
SECRET_KEY=replace-this-with-a-long-random-secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=43200
```

Example using MySQL:

```env
DATABASE_URL=mysql+pymysql://USERNAME:PASSWORD@localhost:3306/health_assistant_db
SECRET_KEY=replace-this-with-a-long-random-secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=43200
```

Generate a secure secret key, for example:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Never commit `.env`, database passwords, production credentials, or real secret keys. The committed `.env.example` must contain placeholders only.

## 7. Backend Setup

From the repository root:

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

On Windows PowerShell, activate the environment with:

```powershell
.\venv\Scripts\Activate.ps1
```

Create `backend/.env` as described above.

Start the backend from the `backend` directory:

```bash
./run_backend.sh
```

The API is configured for local development at:

- API base: `http://localhost:8000`
- Health check: `http://localhost:8000/health`
- Interactive API documentation: `http://localhost:8000/docs`

The frontend currently targets `http://localhost:8000` in `frontend/src/api.js`, and the backend CORS configuration allows the Vite development origins on ports `5173`.

## 8. Frontend Setup

Open a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open the Vite development URL shown in the terminal (normally `http://localhost:5173`).

To create a production build:

```bash
npm run build
```

## 9. Ollama Setup

Install Ollama, start its service, and pull the configured model:

```bash
ollama pull qwen3:8b
ollama serve
```

If Ollama is already running as a background service, the separate `ollama serve` command may not be necessary.

The default Ollama endpoint is `http://127.0.0.1:11434`. The application communicates with Ollama's local HTTP API; no third-party LLM API key is configured in the supplied source code.

## 10. Data and Model Setup

The RAG application expects generated assets that are not included in this source archive. The paths below are important:

```text
data/
├── external/
├── processed/
│   ├── chunks.jsonl
│   ├── chunks_external.jsonl
│   ├── chunks_final.jsonl
│   ├── vector_index.faiss
│   ├── vector_metadata.json
│   ├── bm25_index.pkl
│   ├── finetune_train_pairs.jsonl
│   └── finetune_eval_pairs.jsonl
└── eval/
    └── eval_queries.jsonl

backend/
└── models_cache/
    ├── finetuned-embedding-health/
    └── mmarco-mMiniLMv2-L12-H384-v1/
```

The general data preparation sequence implemented by the scripts is:

1. Download the external datasets:

   ```bash
   cd scripts
   python download_medical_datasets.py
   ```

2. Process the downloaded datasets:

   ```bash
   python process_external_datasets_filtered.py
   ```

3. Prepare `data/processed/chunks.jsonl` containing the project's manually curated Persian content. This input is expected by `merge_datasets.py` and is not included in the supplied archive.

4. Merge the internal and external chunks:

   ```bash
   python merge_datasets.py
   ```

5. Prepare embedding fine-tuning pairs:

   ```bash
   python prepare_finetune_pairs.py
   ```

6. Fine-tune the embedding model:

   ```bash
   python finetune_embedding.py
   ```

7. Build the FAISS vector index:

   ```bash
   python build_vector_index.py
   ```

8. Build the BM25 index:

   ```bash
   python build_bm25_index.py
   ```

Install the additional packages needed by the data preparation scripts when they are not already available:

```bash
pip install datasets tqdm
```

The fine-tuning and indexing scripts also rely on the relevant packages in `backend/requirements.txt`, including Sentence Transformers, PyTorch (installed as a dependency where supported), NumPy, FAISS, and `rank_bm25`.

### Cross-Encoder model

The reranker loads model files from:

```text
backend/models_cache/mmarco-mMiniLMv2-L12-H384-v1/
```

The model files must be placed in that exact directory. The code uses `local_files_only=True`; it will not automatically download the reranker at runtime. Confirm the model source and its license before redistributing its files.

### Evaluation data

`backend/evaluate.py` expects:

```text
data/eval/eval_queries.jsonl
```

This evaluation input is not present in the supplied archive. Create or provide it before running:

```bash
cd backend
./run_eval.sh
```

## 11. API Overview

The backend exposes the following main route groups:

| Route | Purpose |
|---|---|
| `/auth/register` | Register a user |
| `/auth/login` | Authenticate and obtain a JWT |
| `/auth/logout` | Revoke the current token |
| `/chats/` | Create and list chats |
| `/chats/{chat_id}` | Rename or delete a chat |
| `/chats/{chat_id}/messages` | List messages and send a message |
| `/chats/{chat_id}/messages/{message_id}/feedback` | Submit or clear response feedback |
| `/health` | Health check |

See `/docs` while the backend is running for the interactive API schema.

## 12. Medical Disclaimer

This application is an academic health-education project. Its responses are generated by an AI model and may be incomplete, outdated, or incorrect. It must not be used for diagnosis, emergency decisions, medication selection, or dosage decisions. Always consult a qualified healthcare professional for personal medical concerns. The application is not a substitute for a doctor, pharmacist, or other licensed professional.

## 13. Current Scope and Limitations

- The supplied frontend and backend are configured for local development.
- The frontend API base URL is currently hard-coded to `http://localhost:8000`.
- The RAG pipeline requires locally prepared datasets, indexes, and model files.
- The reranker requires a local model directory.
- The evaluation runner requires a separate evaluation-query JSONL file.
- Database table creation currently uses SQLAlchemy `create_all`; database migrations are recommended for production.
- Production deployment requires additional work, including HTTPS, production-grade secrets, database migrations, deployment configuration, and a review of privacy and security requirements.

---

# فارسی

## ۱. معرفی پروژه

«دستیار جامع آموزش سلامت» یک پروژه دانشگاهی با هدف ارائه اطلاعات عمومی و آموزشی درباره سلامت، داروها و موضوعات پزشکی است. این سامانه برای تشخیص بیماری، تجویز درمان یا جایگزینی مشاوره تخصصی پزشک طراحی نشده است.

ساختار برنامه از یک رابط کاربری مبتنی بر React، بک‌اند مبتنی بر FastAPI، پایگاه داده رابطه‌ای و یک خط لوله پرسش‌وپاسخ مبتنی بر معماری RAG تشکیل شده است.

در معماری RAG، ابتدا بخش‌های مرتبط از پایگاه دانش بازیابی می‌شوند و سپس این اطلاعات به همراه پرسش کاربر در اختیار مدل زبانی قرار می‌گیرند تا پاسخ نهایی بر اساس زمینه بازیابی‌شده تولید شود.

## ۲. قابلیت‌های اصلی

- ثبت‌نام و ورود کاربران.
- ذخیره امن رمز عبور به‌صورت هش‌شده.
- احراز هویت مبتنی بر JWT.
- محدودسازی تعداد تلاش‌های ورود برای کاهش حملات Brute Force.
- ایجاد، مشاهده، تغییر نام و حذف گفتگوها.
- ذخیره تاریخچه پیام‌ها.
- امکان پاسخ دادن به یک پیام مشخص (Reply).
- ثبت بازخورد مثبت یا منفی برای پاسخ‌های دستیار.
- دانلود تاریخچه گفتگو به‌صورت فایل متنی.
- پاسخ‌گویی آموزشی به زبان فارسی و انگلیسی.
- بازیابی معنایی اطلاعات با استفاده از FAISS.
- بازیابی کلیدواژه‌ای با استفاده از BM25.
- ترکیب بازیابی معنایی و کلیدواژه‌ای در Hybrid Retrieval.
- مرتب‌سازی مجدد نتایج با مدل Cross-Encoder.
- تولید پاسخ با استفاده از مدل زبانی محلی از طریق Ollama.
- ابزارهای ارزیابی عملکرد سیستم RAG.
- ثبت اطلاعات مربوط به تعاملات و عملکرد سیستم.

## ۳. فناوری‌های استفاده‌شده

| بخش | فناوری‌ها |
|---|---|
| رابط کاربری | React 18، Vite، JavaScript، CSS |
| بک‌اند | Python، FastAPI، Uvicorn |
| اعتبارسنجی داده | Pydantic |
| پایگاه داده و ORM | MySQL یا SQLite، SQLAlchemy |
| احراز هویت | JWT، Passlib، bcrypt |
| بازیابی اطلاعات | Sentence Transformers، FAISS، BM25 |
| رتبه‌بندی مجدد | Cross-Encoder |
| مدل زبانی | Ollama |
| پردازش داده | Hugging Face Datasets، NumPy |
| نمایش Markdown | Marked، DOMPurify |

## ۴. ساختار پروژه

```text
Final_Project/
├── backend/
│   ├── app/
│   │   ├── auth/              # ثبت‌نام، ورود و احراز هویت
│   │   ├── chats/             # مدیریت گفتگوها و پیام‌ها
│   │   ├── rag/               # بازیابی، جستجوی ترکیبی، رتبه‌بندی و تولید پاسخ
│   │   ├── config.py          # تنظیمات برنامه
│   │   ├── database.py        # اتصال به پایگاه داده
│   │   ├── main.py            # نقطه شروع FastAPI
│   │   ├── models.py          # مدل‌های پایگاه داده
│   │   └── schemas.py         # مدل‌های اعتبارسنجی
│   ├── evaluate.py            # اجرای ارزیابی سیستم RAG
│   ├── requirements.txt
│   ├── run_backend.sh
│   └── run_eval.sh
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── api.js
│   │   ├── App.jsx
│   │   └── styles.css
│   ├── package.json
│   └── vite.config.js
├── scripts/
│   ├── download_medical_datasets.py
│   ├── process_external_datasets_filtered.py
│   ├── merge_datasets.py
│   ├── prepare_finetune_pairs.py
│   ├── finetune_embedding.py
│   ├── build_vector_index.py
│   └── build_bm25_index.py
├── .env.example
├── .gitignore
└── README.md
```

## ۵. پیش‌نیازهای اجرا

برای اجرای کامل پروژه به موارد زیر نیاز دارید:

- Python نسخه 3.10 یا بالاتر.
- Node.js و npm.
- نصب و اجرای Ollama.
- دریافت مدل زبانی سازگار با Ollama؛ مدل پیش‌فرض پروژه `qwen3:8b` است.
- MySQL در صورت استفاده از MySQL به‌جای SQLite.
- دیتاست‌ها، ایندکس‌ها و فایل‌های مدل موردنیاز خط لوله RAG.

**نکته مهم:** فایل ZIP ارائه‌شده شامل کدهای منبع پروژه است؛ اما دیتاست‌های پردازش‌شده، ایندکس‌های FAISS و BM25، مدل Fine-tuned و فایل‌های مدل Cross-Encoder در آن وجود ندارند. برای اجرای کامل قابلیت چت مبتنی بر RAG باید این منابع جداگانه آماده شوند.

## ۶. تنظیم متغیرهای محیطی

ابتدا از فایل نمونه، فایل محیطی محلی ایجاد کنید:

```bash
cp .env.example backend/.env
```

سپس فایل `backend/.env` را باز کرده و تنظیمات پایگاه داده و کلید امنیتی را تغییر دهید.

نمونه تنظیمات با SQLite:

```env
DATABASE_URL=sqlite:///./health_assistant.db
SECRET_KEY=replace-this-with-a-long-random-secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=43200
```

نمونه تنظیمات با MySQL:

```env
DATABASE_URL=mysql+pymysql://USERNAME:PASSWORD@localhost:3306/health_assistant_db
SECRET_KEY=replace-this-with-a-long-random-secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=43200
```

برای تولید کلید امنیتی تصادفی می‌توانید از دستور زیر استفاده کنید:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

فایل `.env`، رمز عبور پایگاه داده، کلیدهای امنیتی و اطلاعات محرمانه نباید در GitHub منتشر شوند. فقط فایل نمونه با مقادیر غیرواقعی باید در مخزن قرار بگیرد.

## ۷. راه‌اندازی بک‌اند

از مسیر اصلی پروژه:

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

در Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

پس از ایجاد و تنظیم فایل `backend/.env`، بک‌اند را اجرا کنید:

```bash
./run_backend.sh
```

آدرس‌های اصلی:

- آدرس API: `http://localhost:8000`
- بررسی سلامت سرور: `http://localhost:8000/health`
- مستندات تعاملی API: `http://localhost:8000/docs`

## ۸. راه‌اندازی فرانت‌اند

در یک ترمینال جداگانه:

```bash
cd frontend
npm install
npm run dev
```

آدرس نمایش‌داده‌شده در ترمینال را در مرورگر باز کنید. آدرس پیش‌فرض Vite معمولاً `http://localhost:5173` است.

برای ساخت نسخه Production:

```bash
npm run build
```

## ۹. راه‌اندازی Ollama

پس از نصب Ollama، مدل پیش‌فرض پروژه را دریافت کنید:

```bash
ollama pull qwen3:8b
```

در صورت اجرا نبودن سرویس Ollama:

```bash
ollama serve
```

آدرس پیش‌فرض ارتباط با Ollama برابر `http://127.0.0.1:11434` است. در کدهای ارائه‌شده، برای ارتباط با مدل زبانی از API محلی Ollama استفاده شده و کلید API سرویس خارجی مشخصی وجود ندارد.

## ۱۰. آماده‌سازی دیتاست‌ها و مدل‌ها

خط لوله پردازش داده پروژه به فایل‌هایی نیاز دارد که در ZIP موجود نیستند.

ساختار مورد انتظار:

```text
data/
├── external/
├── processed/
│   ├── chunks.jsonl
│   ├── chunks_external.jsonl
│   ├── chunks_final.jsonl
│   ├── vector_index.faiss
│   ├── vector_metadata.json
│   ├── bm25_index.pkl
│   ├── finetune_train_pairs.jsonl
│   └── finetune_eval_pairs.jsonl
└── eval/
    └── eval_queries.jsonl

backend/
└── models_cache/
    ├── finetuned-embedding-health/
    └── mmarco-mMiniLMv2-L12-H384-v1/
```

ترتیب کلی اجرای اسکریپت‌های آماده‌سازی داده:

۱. دریافت دیتاست‌های خارجی:

```bash
cd scripts
python download_medical_datasets.py
```

۲. پردازش دیتاست‌های دانلودشده:

```bash
python process_external_datasets_filtered.py
```

۳. آماده‌سازی فایل `data/processed/chunks.jsonl` شامل محتوای فارسی گردآوری‌شده و آماده‌شده توسط پروژه. این فایل در ZIP ارائه‌شده وجود ندارد، اما اسکریپت ادغام داده‌ها به آن نیاز دارد.

۴. ادغام داده‌های داخلی و خارجی:

```bash
python merge_datasets.py
```

۵. آماده‌سازی زوج‌های پرسش و متن مرتبط برای Fine-tuning:

```bash
python prepare_finetune_pairs.py
```

۶. Fine-tuning مدل Embedding:

```bash
python finetune_embedding.py
```

۷. ساخت ایندکس برداری FAISS:

```bash
python build_vector_index.py
```

۸. ساخت ایندکس BM25:

```bash
python build_bm25_index.py
```

در صورت نصب نبودن وابستگی‌های مربوط به پردازش دیتاست:

```bash
pip install datasets tqdm
```

اسکریپت‌های Fine-tuning و ساخت ایندکس نیز به کتابخانه‌های مرتبط مانند Sentence Transformers، PyTorch، NumPy، FAISS و `rank_bm25` نیاز دارند.

### مدل Cross-Encoder

مدل رتبه‌بندی مجدد باید در مسیر زیر قرار بگیرد:

```bash
backend/models_cache/mmarco-mMiniLMv2-L12-H384-v1/
```

کد پروژه مدل را با گزینه `local_files_only=True` بارگذاری می‌کند؛ بنابراین دانلود خودکار آن هنگام اجرای برنامه انجام نمی‌شود. پیش از انتشار فایل‌های مدل، منبع و مجوز استفاده از آن را بررسی کنید.

### داده‌های ارزیابی

اسکریپت ارزیابی به فایل زیر نیاز دارد:

```text
data/eval/eval_queries.jsonl
```

این فایل در ZIP موجود نیست. پس از آماده‌سازی آن، می‌توانید ارزیابی را اجرا کنید:

```bash
cd backend
./run_eval.sh
```

## ۱۱. مسیرهای اصلی API

| مسیر | کاربرد |
|---|---|
| `/auth/register` | ثبت‌نام کاربر |
| `/auth/login` | ورود و دریافت JWT |
| `/auth/logout` | لغو اعتبار توکن |
| `/chats/` | ایجاد و مشاهده گفتگوها |
| `/chats/{chat_id}` | تغییر نام یا حذف گفتگو |
| `/chats/{chat_id}/messages` | مشاهده و ارسال پیام |
| `/chats/{chat_id}/messages/{message_id}/feedback` | ثبت یا حذف بازخورد پاسخ |
| `/health` | بررسی وضعیت سرور |

مستندات کامل و تعاملی مسیرها پس از اجرای بک‌اند در آدرس `/docs` در دسترس است.

## ۱۲. هشدار پزشکی

این پروژه صرفاً یک سامانه دانشگاهی برای آموزش عمومی سلامت است. پاسخ‌های تولیدشده توسط مدل هوش مصنوعی ممکن است ناقص، قدیمی یا نادرست باشند. از این سامانه نباید برای تشخیص بیماری، تصمیم‌گیری در شرایط اورژانسی، انتخاب دارو یا تعیین دوز مصرفی استفاده شود. برای مسائل پزشکی شخصی باید با پزشک، داروساز یا متخصص دارای صلاحیت مشورت شود. این سامانه جایگزین خدمات تخصصی درمانی نیست.

## ۱۳. محدودیت‌های فعلی پروژه

- فرانت‌اند و بک‌اند برای اجرای محلی پیکربندی شده‌اند.
- آدرس API در فایل `frontend/src/api.js` به‌صورت ثابت روی `http://localhost:8000` تنظیم شده است.
- اجرای کامل RAG به دیتاست‌ها، ایندکس‌ها و فایل‌های مدل محلی نیاز دارد.
- مدل Cross-Encoder باید به‌صورت محلی در مسیر مشخص‌شده قرار بگیرد.
- اجرای اسکریپت ارزیابی به فایل جداگانه پرسش‌های ارزیابی نیاز دارد.
- ایجاد جداول پایگاه داده در حال حاضر با `SQLAlchemy create_all` انجام می‌شود؛ برای محیط Production استفاده از ابزار مهاجرت پایگاه داده مانند Alembic توصیه می‌شود.
- انتشار Production به تنظیمات تکمیلی مانند HTTPS، مدیریت امن کلیدها، مهاجرت پایگاه داده، پیکربندی استقرار و بازبینی الزامات امنیت و حریم خصوصی نیاز دارد.
