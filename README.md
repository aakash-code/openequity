# OpenEquity Research Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Node Version](https://img.shields.io/badge/node-18+-green.svg)](https://nodejs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-blue)](https://www.typescriptlang.org/)

**Democratizing professional-grade equity research tools for everyone.**

OpenEquity is the world's first comprehensive open-source equity research platform that bridges the $20,000+ annual cost barrier of professional financial terminals. We combine equity research tools, financial modeling capabilities, CFA curriculum integration, and collaborative features in a single, free platform.

---

## 🎯 Vision

Create a world where anyone—students, individual investors, emerging market professionals—has access to institutional-quality financial analysis tools without the prohibitive costs of Bloomberg Terminal, FactSet, or similar platforms.

## ✨ Key Features

### Core Capabilities
- 📊 **Professional Equity Research Tools** - Comprehensive financial analysis suite
- 📈 **Integrated Spreadsheet** - Native Excel-compatible spreadsheet with financial formulas
- 💹 **Real-time Market Data** - Live quotes and historical data from multiple sources
- 🤖 **AI-Powered Analysis** - NLP-driven earnings call analysis and sentiment scoring
- 🎓 **CFA Integration** - Native curriculum alignment and practice tools
- 👥 **Collaborative Research** - Real-time co-editing and team workspaces
- 🏪 **Model Marketplace** - Share and fork financial models

### Competitive Advantages
| Feature | Bloomberg Terminal | **OpenEquity** |
|---------|-------------------|----------------|
| Annual Cost | $24,000+ | **Free (Open Source)** |
| Spreadsheet Integration | Separate Plugin | **Native** |
| CFA Curriculum | None | **Integrated** |
| AI Analysis | Limited | **Advanced NLP/ML** |
| Collaboration | Limited | **Full Suite** |
| Customization | Restricted | **Unlimited** |

---

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose (recommended)
- OR: Node.js 18+, Python 3.11+, PostgreSQL 15+

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/openequity.git
cd openequity

# Start all services
make dev-setup

# Or manually:
docker-compose up -d
```

**Access the application:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/api/docs

### Option 2: Local Development

#### Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Run database migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload
```

#### Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env.local
# Edit .env.local with your settings

# Start development server
npm run dev
```

---

## 📁 Project Structure

```
openequity/
├── frontend/              # Next.js frontend application
│   ├── src/
│   │   ├── app/          # Next.js app router
│   │   ├── components/   # React components
│   │   ├── lib/          # Utilities and configs
│   │   ├── hooks/        # Custom React hooks
│   │   └── types/        # TypeScript types
│   └── package.json
│
├── backend/              # FastAPI backend application
│   ├── app/
│   │   ├── api/         # API routes
│   │   ├── core/        # Core configuration
│   │   ├── db/          # Database connection
│   │   ├── models/      # SQLAlchemy models
│   │   ├── schemas/     # Pydantic schemas
│   │   ├── services/    # Business logic
│   │   └── ml/          # ML models
│   └── requirements.txt
│
├── database/             # Database schemas and migrations
│   ├── schemas/         # SQL schema files
│   ├── migrations/      # Alembic migrations
│   └── seeds/           # Sample data
│
├── infrastructure/       # Infrastructure as code
│   ├── docker/          # Docker configurations
│   ├── kubernetes/      # K8s manifests
│   └── nginx/           # Nginx configs
│
├── docs/                # Documentation
│   ├── PDR.md          # Product Design Requirements
│   ├── ROADMAP.md      # Development roadmap
│   └── api/            # API documentation
│
├── .github/             # GitHub Actions workflows
├── docker-compose.yml   # Docker Compose configuration
└── Makefile            # Development commands
```

---

## 🛠️ Technology Stack

### Frontend
- **Framework:** Next.js 14+ (React 18+)
- **Language:** TypeScript 5.0+
- **Styling:** Tailwind CSS 3.0+
- **State Management:** Redux Toolkit
- **Data Fetching:** TanStack Query
- **Charts:** Recharts + D3.js
- **Spreadsheet:** Luckysheet/OnlyOffice
- **Testing:** Jest + React Testing Library

### Backend
- **Framework:** FastAPI 0.110+
- **Language:** Python 3.11+
- **Database:** PostgreSQL 15+ with TimescaleDB
- **ORM:** SQLAlchemy 2.0+
- **Cache:** Redis 7.0+
- **Search:** Elasticsearch 8.0+
- **Queue:** Celery + RabbitMQ
- **ML:** PyTorch/TensorFlow
- **Testing:** pytest

### Infrastructure
- **Containerization:** Docker
- **Orchestration:** Kubernetes
- **CI/CD:** GitHub Actions
- **Monitoring:** Prometheus + Grafana
- **Logging:** ELK Stack

---

## 🧪 Testing

### Backend Tests
```bash
# Run all tests
cd backend
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_api.py -v
```

### Frontend Tests
```bash
# Run all tests
cd frontend
npm test

# Run in watch mode
npm run test:watch

# Run with coverage
npm run test:coverage
```

### End-to-End Tests
```bash
# Using Cypress
npm run e2e

# Using Playwright
npm run test:e2e
```

---

## 📚 Documentation

- [Product Design Requirements (PDR)](./docs/PDR.md)
- [Development Roadmap](./docs/ROADMAP.md)
- [API Documentation](http://localhost:8000/api/docs) (when running)
- [Contributing Guidelines](./CONTRIBUTING.md)
- [Code of Conduct](./CODE_OF_CONDUCT.md)

---

## 🗺️ Roadmap

### Phase 1: Foundation (Months 1-3) - Current
- [x] Basic data infrastructure
- [x] Core API endpoints
- [x] Spreadsheet integration
- [ ] User authentication
- [ ] Company profiles

### Phase 2: Core Features (Months 4-6)
- [ ] Financial analysis engine
- [ ] Valuation models
- [ ] Real-time data feeds
- [ ] Basic collaboration
- [ ] Mobile responsive design

### Phase 3: Advanced Features (Months 7-9)
- [ ] AI/ML capabilities
- [ ] CFA integration
- [ ] Model marketplace
- [ ] Advanced collaboration
- [ ] API documentation

### Phase 4: Scale & Polish (Months 10-12)
- [ ] Performance optimization
- [ ] Mobile apps
- [ ] Enterprise features
- [ ] Comprehensive testing
- [ ] Production deployment

See [ROADMAP.md](./docs/ROADMAP.md) for detailed timeline.

---

## 🤝 Contributing

We welcome contributions from developers, finance professionals, and anyone passionate about democratizing financial tools!

### How to Contribute

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Commit your changes** (`git commit -m 'Add amazing feature'`)
4. **Push to the branch** (`git push origin feature/amazing-feature`)
5. **Open a Pull Request**

Please read our [Contributing Guidelines](./CONTRIBUTING.md) for details on our code of conduct and development process.

### Areas We Need Help
- 🔧 Backend Development (Python/FastAPI)
- 🎨 Frontend Development (React/Next.js)
- 📊 Financial Modeling Expertise
- 🤖 Machine Learning / NLP
- 📝 Documentation
- 🧪 Testing & QA
- 🎓 CFA Curriculum Integration

---

## 📊 Target Users

### Primary: CFA Candidates
- 300,000+ globally
- Need affordable practice tools
- Require professional-grade analysis

### Secondary: Finance Students
- 2M+ globally
- Limited access to expensive tools
- Seeking hands-on experience

### Tertiary: Independent Investors
- Individual researchers
- Emerging market analysts
- Small investment firms

---

## 🎯 Success Metrics

**Year 1 Goals:**
- 50,000+ active users
- 100+ contributing developers
- 1,000+ financial models in marketplace
- 25+ university adoptions
- CFA Institute partnership

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### Why MIT?
We chose MIT for maximum flexibility and adoption, allowing:
- ✅ Free use, modification, and distribution
- ✅ Commercial use
- ✅ Private use
- ✅ Patent use (with proper attribution)

---

## 🙏 Acknowledgments

- CFA Institute for the inspiration
- Open-source community for the tools
- All contributors who make this possible

---

## 📞 Contact & Support

- **Documentation:** [docs/](./docs/)
- **Issues:** [GitHub Issues](https://github.com/yourusername/openequity/issues)
- **Discussions:** [GitHub Discussions](https://github.com/yourusername/openequity/discussions)
- **Email:** contact@openequity.org (coming soon)
- **Discord:** [Join our community](https://discord.gg/openequity) (coming soon)

---

## 🌟 Star History

If you find this project useful, please consider giving it a star! ⭐

[![Star History Chart](https://api.star-history.com/svg?repos=yourusername/openequity&type=Date)](https://star-history.com/#yourusername/openequity&Date)

---

## 💡 Why OpenEquity?

Financial markets should be accessible to everyone, not just those who can afford $20,000+ annual subscriptions. OpenEquity levels the playing field by providing:

- **Education:** Help students learn professional tools
- **Opportunity:** Enable emerging market analysts
- **Innovation:** Foster collaborative research
- **Transparency:** Open-source financial analysis

**Join us in democratizing finance! 🚀**

---

Made with ❤️ by the OpenEquity Community
