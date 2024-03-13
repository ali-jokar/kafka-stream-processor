FROM python:3.10
USER root
RUN pip install kafka-python requests
COPY . /app
WORKDIR /app
CMD ["python", "my_project_AliJokar.py"]
