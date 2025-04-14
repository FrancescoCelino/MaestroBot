FROM pytorch/pytorch:2.2.1-cuda12.1-cudnn8-runtime

WORKDIR /app

# Install common utilities
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Install your specific dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

# Default: open a bash shell
CMD ["bash"]