# TriviaBot Deployment Guide

## Prerequisites

- Discord Bot Token ([Discord Developer Portal](https://discord.com/developers/applications))
- OpenAI API Key ([OpenAI Platform](https://platform.openai.com/api-keys))
- Server with Python 3.8+ and Git

## Option 1: Railway (Recommended)

1. Fork this repository to your GitHub account
2. Go to [Railway.app](https://railway.app) and sign in with GitHub
3. Create New Project → Deploy from GitHub repo → Select your TriviaBot repo
4. Set environment variables in Railway dashboard:
   ```
   DISCORD_TOKEN=your_discord_bot_token
   OPENAI_API_KEY=your_openai_api_key
   PORT=8080
   ```
5. Deploy - Railway automatically deploys from main branch

## Option 2: VPS/Cloud Server

### 1. Server Setup (Ubuntu/Debian)

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and Git
sudo apt install python3 python3-pip python3-venv git -y

# Clone the repository
git clone https://github.com/your-username/TriviaBot.git
cd TriviaBot
```

### 2. Python Environment

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit with your API keys
nano .env
```

Add your tokens:
```env
DISCORD_TOKEN=your_discord_bot_token
OPENAI_API_KEY=your_openai_api_key
DATABASE_URL=sqlite:///trivia_bot.db
DEFAULT_PERSONA=sarcastic_host
DEBUG_MODE=false
PORT=8080
HOST=0.0.0.0
```

### 4. Run the Bot

```bash
# Test run
python main.py

# For production, use a process manager like PM2:
sudo npm install -g pm2
pm2 start "python main.py" --name trivia-bot
pm2 startup
pm2 save
```

### 5. Optional: Nginx Reverse Proxy

```bash
# Install Nginx
sudo apt install nginx -y

# Create config file
sudo nano /etc/nginx/sites-available/trivia-bot
```

Nginx config:
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/trivia-bot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## Option 3: Docker

### 1. Build Image

```bash
# Create Dockerfile
cat > Dockerfile << EOF
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
EOF

# Build image
docker build -t trivia-bot .
```

### 2. Run Container

```bash
# Create .env file with your tokens first

# Run container
docker run -d --name trivia-bot \
  --env-file .env \
  -p 8080:8080 \
  trivia-bot
```

### 3. Docker Compose (Optional)

```yaml
# docker-compose.yml
version: '3.8'

services:
  trivia-bot:
    build: .
    env_file: .env
    ports:
      - "8080:8080"
    restart: unless-stopped
    volumes:
      - ./data:/app/data
```

```bash
# Run with compose
docker-compose up -d
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DISCORD_TOKEN` | Yes | Discord bot token |
| `OPENAI_API_KEY` | Yes | OpenAI API key |
| `DATABASE_URL` | No | Database URL (defaults to SQLite) |
| `DEFAULT_PERSONA` | No | Default bot personality |
| `DEBUG_MODE` | No | Enable debug logging |
| `PORT` | No | Server port (default: 8080) |
| `HOST` | No | Server host (default: 0.0.0.0) |

## Discord Bot Setup

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create New Application → Create Bot
3. Copy Bot Token to `DISCORD_TOKEN`
4. Under Bot → Privileged Gateway Intents:
   - Enable "Server Members Intent"
   - Enable "Message Content Intent"
5. Under OAuth2 → URL Generator:
   - Scopes: `bot`, `applications.commands`
   - Bot Permissions: `Send Messages`, `Use Slash Commands`, `Embed Links`
6. Use generated URL to invite bot to your server

## OpenAI API Setup

1. Go to [OpenAI Platform](https://platform.openai.com/api-keys)
2. Create new API key
3. Copy to `OPENAI_API_KEY`
4. Ensure you have credits/billing set up

## Troubleshooting

### Bot won't start
- Check your `.env` file has correct tokens
- Verify Discord bot has required permissions
- Check Python version is 3.8+

### Commands not appearing
- Bot needs `applications.commands` scope
- Try `/sync` command if available
- Restart bot after permission changes

### Database errors
- Check file permissions for SQLite
- Verify `DATABASE_URL` format
- For PostgreSQL, install `psycopg2-binary`

### OpenAI errors
- Verify API key is correct
- Check account has credits
- Monitor rate limits

## Monitoring

```bash
# Check logs with PM2
pm2 logs trivia-bot

# Check logs with Docker
docker logs trivia-bot

# System monitoring
htop
df -h
free -m
```

## Updates

```bash
# Pull latest changes
git pull origin main

# Update dependencies
pip install -r requirements.txt --upgrade

# Restart service
pm2 restart trivia-bot
# or
docker-compose restart
```

## Security Notes

- Never commit `.env` files to Git
- Use strong, unique API keys
- Keep dependencies updated
- Use HTTPS in production
- Regularly backup your database
- Monitor bot permissions