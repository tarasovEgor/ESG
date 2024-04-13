FROM python:3.10

RUN pip install -U nltk
RUN python -c "import nltk; nltk.download('punkt'); nltk.data.load('tokenizers/punkt/russian.pickle')"
WORKDIR "/app"
COPY requirements/requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .
# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--ssl-keyfile", "privkey.pem", "--ssl-certfile", "fullchain.pem"]
