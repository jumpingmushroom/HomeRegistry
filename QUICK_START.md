# Quick Start Guide

Get HomeRegistry running in 5 minutes!

## Step 1: Install Prerequisites

- **Docker**: [Install Docker](https://docs.docker.com/get-docker/)
- **Docker Compose**: Usually included with Docker Desktop

Verify installation:
```bash
docker --version
docker-compose --version
```

## Step 2: Download HomeRegistry

```bash
git clone https://github.com/yourusername/homeregistry.git
cd homeregistry
```

## Step 3: Choose Your AI Provider

You have 3 options:

### Option A: Anthropic Claude (Recommended)
1. Get an API key from [console.anthropic.com](https://console.anthropic.com)
2. Edit `.env`:
   ```bash
   AI_PROVIDER=claude
   CLAUDE_API_KEY=sk-ant-your-key-here
   ```

### Option B: OpenAI GPT-4
1. Get an API key from [platform.openai.com](https://platform.openai.com)
2. Edit `.env`:
   ```bash
   AI_PROVIDER=openai
   OPENAI_API_KEY=sk-your-key-here
   ```

### Option C: Ollama (Free, Local, No API Key!)
1. Uncomment the Ollama service in `docker-compose.yml`
2. No `.env` changes needed

## Step 4: Start HomeRegistry

```bash
# Build and start
docker-compose up -d

# If using Ollama, also run:
docker exec -it homeregistry-ollama ollama pull llava
```

## Step 5: Access the App

Open your browser to: **http://localhost:8080**

Complete the setup wizard:
1. Select your AI provider
2. Enter API key (if using Claude/OpenAI)
3. Test connection
4. Complete setup

## Step 6: Add Your First Item

1. Click the **Add** tab (camera icon)
2. Take a photo or upload an image
3. Click **Analyze with AI**
4. Review the extracted information
5. Save!

## Next Steps

- **Organize**: Create locations and categories in Settings
- **Search**: Use the search bar to find items
- **Track**: Add warranty dates to important items
- **Mobile**: Add HomeRegistry to your phone's home screen (PWA)

## Troubleshooting

**Can't access the app?**
```bash
# Check if containers are running
docker ps

# Check logs
docker-compose logs
```

**AI analysis not working?**
- Verify your API key in Settings → Test Connection
- Check logs: `docker logs homeregistry-backend`

**Need help?** Open an issue on GitHub!

---

Happy organizing! 🏠📦
