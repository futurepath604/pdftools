FROM python:3.10-slim

# PDF to Image কনভার্টারের জন্য প্রয়োজনীয় সিস্টেম টুল ইনস্টল করা
RUN apt-get update && apt-get install -y \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY . /code

# FastAPI রান করার কমান্ড
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
