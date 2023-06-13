FROM python:3.10

MAINTAINER Jared Gallina

RUN mkdir /google-scheduler
COPY requirements.txt /google-scheduler/
COPY /src /google-scheduler/src
RUN pip install --upgrade pip
RUN pip install -r /google-scheduler/requirements.txt

WORKDIR /google-scheduler
ENV PYTHONPATH "${PYTHONPATH}:/google-scheduler/"

CMD ["streamlit", "run", "src/app/main.py"]