# Use an official Python runtime as a parent image
FROM python:3.14.0a3-alpine3.21

# Set the working directory in the container
WORKDIR /app

COPY . .

# Install any needed packages specified in requirements.txt
RUN apk add --no-cache g++ && pip install --no-cache-dir -r ./requirements.txt

# Run python file when the container launches
CMD ["python", "./bot.py"]