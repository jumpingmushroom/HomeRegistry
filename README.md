# 🏠 HomeRegistry

A self-hosted home inventory management system that uses AI to analyze photos of household items and automatically extract metadata.

![HomeRegistry](https://img.shields.io/badge/version-1.0.0-green)
![License](https://img.shields.io/badge/license-MIT-blue)

## ✨ Features

- **📸 AI-Powered Photo Analysis**: Upload photos and let AI extract item details automatically
- **🤖 Multi-AI Provider Support**: Choose between Anthropic Claude, OpenAI GPT-4, Google Gemini, or local Ollama
- **📱 Mobile-First PWA**: Works seamlessly on phones with camera integration
- **🏘️ Hierarchical Organization**: Organize items by location (Home → Floor → Room → Storage)
- **📦 Category Management**: Flexible category system with hierarchical structure
- **📄 Document Management**: Attach warranties, manuals, and receipts
- **⏰ Warranty Tracking**: Get notified of expiring warranties
- **💰 Inventory Valuation**: Track purchase price and current value
- **🔍 Full-Text Search**: Find items quickly across all fields
- **📊 Dashboard Analytics**: Visualize your inventory at a glance
- **🐳 Docker Deployment**: Single-command deployment with Docker Compose
- **🔒 Privacy-First**: Self-hosted, no external dependencies (except AI APIs if chosen)

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose installed
- (Optional) API key for Claude, OpenAI, or Gemini, OR a running Ollama instance

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/homeregistry.git
cd homeregistry
```

2. Create environment file:
```bash
cp .env.example .env
```

3. (Optional) Edit `.env` to add your AI provider API key:
```bash
# For Claude
AI_PROVIDER=claude
CLAUDE_API_KEY=sk-ant-your-api-key

# OR for OpenAI
AI_PROVIDER=openai
OPENAI_API_KEY=sk-your-api-key

# OR for Google Gemini
AI_PROVIDER=gemini
GEMINI_API_KEY=your-gemini-api-key

# OR for local Ollama (no API key needed)
AI_PROVIDER=ollama
OLLAMA_ENDPOINT=http://ollama:11434
```

4. Start the application:
```bash
docker-compose up -d
```

5. Access HomeRegistry at `http://localhost:8080`

6. Complete the first-run setup wizard to configure your AI provider

### Using Local Ollama (No API Key Required)

1. Uncomment the Ollama service in `docker-compose.yml`

2. Start the application:
```bash
docker-compose up -d
```

3. Pull the llava model:
```bash
docker exec -it homeregistry-ollama ollama pull llava
```

4. In the setup wizard or settings, select "Ollama (Local)" as your AI provider

## 📱 Usage

### Adding Items

1. Navigate to the **Add** tab
2. Take photos or upload images of your item
3. Click **Analyze with AI** to extract information
4. Review and edit the AI-generated details
5. Select category and location
6. Save the item

### Organizing Your Inventory

**Locations**: Create a hierarchical structure:
- Home → Ground Floor → Kitchen → Drawer 3
- Home → Basement → Workshop → Tool Cabinet

**Categories**: Organize items by type:
- Electronics → Computers → Laptops
- Kitchen → Appliances → Small Appliances

### Tracking Warranties

1. When adding/editing an item, set the warranty expiration date
2. View expiring warranties on the Dashboard
3. Attach warranty documents to items for easy reference

### Searching Items

Use the search bar on the Items page to find items by:
- Name
- Description
- Manufacturer
- Model number
- Serial number

## 🏗️ Architecture

### Technology Stack

- **Backend**: Python FastAPI
- **Database**: SQLite with WAL mode for concurrent access
- **Frontend**: Vue.js 3 with Vite
- **AI Integration**: Multi-provider (Claude, OpenAI, Ollama)
- **Deployment**: Docker Compose
- **PWA**: Service Worker for offline capability

### Project Structure

```
homeregistry/
├── backend/
│   ├── app/
│   │   ├── api/          # API endpoints
│   │   ├── models/       # SQLAlchemy models
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── services/     # Business logic
│   │   │   └── ai/       # AI provider implementations
│   │   └── main.py       # FastAPI application
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── views/        # Vue components for pages
│   │   ├── components/   # Reusable components
│   │   ├── services/     # API client
│   │   └── router/       # Vue Router config
│   └── Dockerfile
└── docker-compose.yml
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `AI_PROVIDER` | AI provider to use (claude/openai/ollama) | claude |
| `CLAUDE_API_KEY` | Anthropic Claude API key | - |
| `OPENAI_API_KEY` | OpenAI API key | - |
| `OLLAMA_ENDPOINT` | Ollama endpoint URL | http://ollama:11434 |
| `DEFAULT_CURRENCY` | Default currency for prices | NOK |
| `MAX_IMAGE_SIZE_MB` | Maximum image upload size | 10 |
| `MAX_DOCUMENT_SIZE_MB` | Maximum document upload size | 50 |

### In-App Settings

After deployment, configure these in the Settings page:
- AI Provider selection
- API keys
- Default currency

## 📊 API Documentation

Once running, access the interactive API documentation at:
- Swagger UI: `http://localhost:8080/api/docs`
- ReDoc: `http://localhost:8080/api/redoc`

## 🔒 Security Considerations

- **Single-User Application**: No authentication system (designed for self-hosting)
- **API Keys**: Store sensitive keys in environment variables, not in code
- **Network Access**: Recommended to run behind a reverse proxy with authentication if exposing to internet
- **Backups**: Regularly backup the `/data` volume

## 🛠️ Development

### Running Locally for Development

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

### Database Migrations

The application automatically creates tables on first run. For schema changes, use Alembic:

```bash
cd backend
alembic revision --autogenerate -m "Description of changes"
alembic upgrade head
```

## 📦 Data Management

### Backup

Backup the Docker volume containing all data:

```bash
docker run --rm -v homeregistry_homeregistry-data:/data -v $(pwd):/backup \
  alpine tar czf /backup/homeregistry-backup-$(date +%Y%m%d).tar.gz /data
```

### Restore

```bash
docker run --rm -v homeregistry_homeregistry-data:/data -v $(pwd):/backup \
  alpine sh -c "cd / && tar xzf /backup/homeregistry-backup-YYYYMMDD.tar.gz"
```

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with FastAPI, Vue.js, and modern web technologies
- AI analysis powered by Anthropic Claude, OpenAI GPT-4, or Ollama
- Icons and UI inspired by Material Design

## 🐛 Troubleshooting

### AI Analysis Not Working

1. Check your API key is correct in Settings
2. Test the connection using "Test Connection" button
3. Check Docker logs: `docker logs homeregistry-backend`

### Images Not Loading

1. Ensure the images volume is mounted correctly
2. Check file permissions in the `/data/images` directory

### Database Locked Errors

- SQLite is configured with WAL mode for better concurrent access
- If issues persist, check no other processes are accessing the database

### Ollama Model Not Found

```bash
# Pull the llava model
docker exec -it homeregistry-ollama ollama pull llava

# Verify it's installed
docker exec -it homeregistry-ollama ollama list
```

## 📞 Support

For issues and questions:
- Open an issue on GitHub
- Check existing issues for solutions

## 🗺️ Roadmap

Future enhancements planned:
- [ ] CSV import/export
- [ ] Barcode scanning
- [ ] QR code label generation
- [ ] Multi-user support with authentication
- [ ] Maintenance schedules and reminders
- [ ] Loan tracking (who borrowed what)
- [ ] Insurance report generation
- [ ] Cloud backup integration

---

Made with ❤️ for organized homes
