FROM python:3.11

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir \
    --trusted-host pypi.org \
    --trusted-host files.pythonhosted.org \
    -r requirements.txt

EXPOSE 8000

CMD ["sleep", "infinity"]
#CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
