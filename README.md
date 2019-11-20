# "What's New" Rock Climbing Metrics
A data pipeline and metric dashboard that scrapes Mountain Project's "What's New" feed and shows some graphs about the data.

##### Motivation and Goals

My motivation for this side project is to learn about technology I'm interested in

Goals:

1. Consume a data stream using AWS services
2. Learn more about developing with Docker and deploying Docker applications on AWS
3. Create some vizualization the data
4. Minimize AWS monthly cost by designing a serverless architecture.


##### System Design

I want to consume this data stream (https://www.mountainproject.com/whats-new). However, there is no API specifically for this stream, so I will scrape the data.

A dockerized web scraper written in python and deployed as an ECS fargate task (kicked off periodically by a cloudwatch alarm) will collect the data and write it to DynamoDB. The nature of the web scraper will mean it will pick up duplicates every run, so we need some kind of cache to identify duplicates. The cheapest cache functionality for this scenario will be a DynamoDB table with a time-to-live column. Our primary key for the DynamoDB table will be a MD5 hash of the other columns in the row. This hash ensures an equal distribution of the keys to the underlying DynamoDB bucekts??

Next, a python lambda function will pick up new records in DynamboDB and put them to S3 for storage.

An s3 static site will host a simple webapp that utilizes chart.js to display graphs of my chosen metrics.

Some aggregation function will pull data from S3, transform it to data usable by chart.js, and place it on the s3 static site bucket. Repeat this daily so the graphs will be somewhat dynamic.
