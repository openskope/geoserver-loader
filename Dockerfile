FROM python:2
MAINTAINER Jeff Terstriep <jefft@illnois.edu>

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY scripts .

ENTRYPOINT [ "python", "./load_paleocar.py" ]
CMD [ "-h" ]

