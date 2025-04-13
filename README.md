# MaestroBot
user357010412 id del maestro

circa 14000 messaggi del maestro su gozomaxxing

## Development Setup (Docker)

### Requirements
- Docker
- Docker Compose
- (optional) VS Code with Remote Containers extension
- NVIDIA GPU drivers installed
- NVIDIA Container Toolkit installed

You can verify GPU availability with:

```bash
docker run --gpus all nvidia/cuda:12.0.0-base-ubuntu20.04 nvidia-smi
```
### Run the app

```bash
# Build and start the container
docker-compose up --build
```
### If you need Environment Variables

1. Copy the content of `.env.example` to a file named `.env`
2. Fill in with your actual secret keys.
3. Use those variables with the dotenv library
4. Never commit the .env file on GitHub