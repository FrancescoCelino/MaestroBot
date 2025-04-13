# Use official TensorFlow image with GPU support
FROM tensorflow/tensorflow:latest-gpu

WORKDIR /app

COPY requirements.txt .

# Install your specific dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

# Default: open a bash shell
CMD ["bash"]

