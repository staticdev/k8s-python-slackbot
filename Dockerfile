FROM python:3.7.6-slim-stretch

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
ADD src/* requirements.txt /app/

# install requirements
RUN pip install --upgrade pip \
  && pip install -r requirements.txt

# Run app.py when the container launches
CMD ["python", "echobot.py"]
