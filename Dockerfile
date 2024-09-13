# Use the official Python image
FROM python:3.9

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Define environment variables
ENV MONGO_URL=<your_mongo_url>
ENV BOT_TOKEN=<your_bot_token>

# Run bot.py when the container launches
CMD ["python", "bot.py"]
