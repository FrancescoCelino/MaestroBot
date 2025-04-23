# MaestroBot
user357010412 id del maestro

circa 14000 messaggi del maestro su gozomaxxing

## Overview
MaestroBot is a Telegram chatbot powered by LLama 3.1 7B using PyTorch. Docker is used for containerization in order to ensure consistent deployment for anyone who wants to contribute.

## Prerequisites
- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)
- NVIDIA GPU with [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html) installed (for GPU acceleration)

You can verify GPU availability with:

```bash
docker run --gpus all nvidia/cuda:12.0.0-base-ubuntu20.04 nvidia-smi
```

## Project Structure
```
.
├── .dockerignore        # which files will be excluded when building a Docker image
├── docker-compose.yml   # configures which services will be used in the docker image (just Python for now)
├── Dockerfile           # set of instructions for building the Docker image
├── requirements.txt     # Python dependencies (for example, NumPy, Pandas or PyTorch)
└── ...                  # Model files and application code
```

## Getting Started

### Environment Setup
1. Create a `.env` file in the project root with required environment variables. You can find the required environment variables in a file named `.env.example` (see below for details):
   ```
   # Telegram Bot configuration
   TELEGRAM_BOT_TOKEN=your_bot_token_here
   
   # Model configuration
   MODEL_PATH=/app/models/fine_tuned_model
   
   # Other configurations
   DEVICE=cuda  # or cpu if not using GPU
   ```

### Using Docker Compose

#### Start the Development Environment
```bash
docker-compose up -d
```

#### Access the Container Shell
```bash
docker-compose exec maestrobot bash
```

#### Run the Telegram Bot
```bash
# Inside the container
python bot.py
```

#### Stop the Services
```bash
docker-compose down
```

### Using VS Code Remote Development
This project includes configuration for VS Code's Remote Development extension:

1. Install the [Remote Development extension pack](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.vscode-remote-extensionpack)
2. Open the project folder in VS Code
3. Click "Reopen in Container" when prompted or use the command palette to "Remote-Containers: Reopen Folder in Container"

## Docker Configuration Details

### Dockerfile
The Dockerfile is based on PyTorch's official CUDA-enabled image, providing an environment with GPU acceleration for model fine-tuning and inference.

### docker-compose.yml
The docker-compose configuration:
- Mounts the local directory to `/app` in the container
- Forwards port 8000 (for potential web interface)
- Enables GPU access with NVIDIA runtime
- Opens an interactive bash shell

### NVIDIA GPU Support
This project is configured to use NVIDIA GPUs through Docker for faster model training and inference. Make sure you have:
- Compatible NVIDIA drivers installed on your host
- NVIDIA Container Toolkit installed and configured (already installed on Windows by default)

## Gozo Messages Dataset curation
docker compose run --rm exporter
this command runs the "exporter" service specified in docker-compose.yml and then deletes the container (any file created will stay in the local host though)

docker compose up -d maestrobot 
docker compose exec maestrobot bash
the first command looks for the "maestrobot" service, builds an image if not already present, and (re)starts a container.
the second command launches a new bash process in an already started container

## LLM Fine-tuning Workflow
WIP

## Telegram Bot Integration
WIP

## If you need Environment Variables

1. Copy the content of `.env.example` to a file named `.env`
2. Fill in with your actual secret keys.
3. Use those variables with the dotenv library
4. Never commit the .env file on GitHub


## Troubleshooting

### GPU Access Issues
If you encounter GPU access problems:
```bash
# Verify NVIDIA drivers are working
nvidia-smi

# Check if Docker can access the GPU
docker run --rm --gpus all pytorch/pytorch:2.2.1-cuda12.1-cudnn8-runtime python -c "import torch; print(torch.cuda.is_available())"
```

### Container Build Failures
If the container fails to build:
```bash
# Clean and rebuild
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## Contributing
1. Make sure to update requirements.txt when adding new dependencies
2. Test your changes inside the Docker container before committing