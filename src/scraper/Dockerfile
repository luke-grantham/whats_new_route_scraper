FROM python:3.7.4-alpine3.10
RUN pip install beautifulsoup4 boto3 
WORKDIR /usr/bin/local
ENV AWS_DEFAULT_REGION us-east-2
COPY scrape.py /usr/bin/local
CMD python scrape.py
