# Use Python 3.10-slim instead of 3.12-slim
FROM python:3.10-slim

# Step 2: Install necessary tools and libraries
RUN apt-get update && apt-get install -y \
    python3-distutils \
    python3-setuptools \
    python3-pip \
    build-essential \
    && apt-get clean

# Step 3: Upgrade pip, setuptools, and wheel
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Step 4: Set the working directory
WORKDIR /app

# Step 5: Copy requirements file
COPY requirements.txt .

# Step 6: Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Step 7: Copy the rest of your application code
COPY . .

# Set the PORT environment variable
ENV PORT=8080

# Expose the same port
EXPOSE 8080

# Step 7: Set environment variables (optional)
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Step 8: Start the Flask application when the container runs
CMD ["python", "run.py"]
