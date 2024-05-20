# Use a lightweight Python image
FROM python:3.9-alpine

# Install dependencies
RUN apk add --no-cache gcc musl-dev

# Upgrade pip
RUN pip install --upgrade pip

# Set the working directory inside the container
WORKDIR /url-shortener-using-flask

# Copy the current directory contents into the container
COPY . .

# Install Python dependencies
RUN pip install -r requirements.txt

# Expose port 5000
EXPOSE 5000

# Run the Flask application
CMD ["python", "app.py"]
