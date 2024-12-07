# Use an official Python runtime as a parent image
FROM python:3.14.0a2

# Set the working directory in the container
WORKDIR /app

# Clone the GitHub repository
RUN apt-get update && apt-get install -y git
RUN git clone https://github.com/xXxNIKIxXx/SpotifyLinkConverter.git .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r ./requirements.txt

# Run python file when the container launches
CMD ["python", "./bot.py"]