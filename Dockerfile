FROM python:3.10-slim-bullseye

RUN apt-get update \
   && apt-get install -y --no-install-recommends \
      build-essential \
      pkg-config \
   && apt-get clean \
   && rm -rf /var/lib/apt/lists/* \
   && pip install --no-cache-dir --upgrade pip

WORKDIR /app
COPY ./requirements.txt /app

RUN pip install --no-cache-dir --requirement /app/requirements.txt
COPY . /app


EXPOSE 8501


CMD ["streamlit", "run", "interface.py"]
