# Contributing to OpenEquity Research Platform

Thank you for your interest in contributing to OpenEquity! We're building the world's first comprehensive open-source equity research platform, and we need your help to make it a reality.

## 🎯 Mission

Our mission is to democratize professional-grade financial analysis tools by providing a free, open-source alternative to expensive financial terminals like Bloomberg.

## 📋 Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [How Can I Contribute?](#how-can-i-contribute)
3. [Development Setup](#development-setup)
4. [Coding Standards](#coding-standards)
5. [Git Workflow](#git-workflow)
6. [Pull Request Process](#pull-request-process)
7. [Issue Guidelines](#issue-guidelines)
8. [Community](#community)

---

## 📜 Code of Conduct

This project adheres to a Code of Conduct that all contributors are expected to follow. Please read [CODE_OF_CONDUCT.md](./CODE_OF_CONDUCT.md) before contributing.

**TL;DR:** Be respectful, inclusive, and professional.

---

## 🤝 How Can I Contribute?

### 🐛 Reporting Bugs

Found a bug? Help us fix it!

**Before submitting:**
- Check if the bug has already been reported in [Issues](https://github.com/yourusername/openequity/issues)
- Ensure you're using the latest version

**When reporting:**
- Use the bug report template
- Include detailed steps to reproduce
- Provide system information (OS, browser, versions)
- Include screenshots if applicable
- Add relevant logs or error messages

### 💡 Suggesting Enhancements

Have an idea for improvement?

**Before suggesting:**
- Check [existing feature requests](https://github.com/yourusername/openequity/issues?q=is%3Aissue+is%3Aopen+label%3Aenhancement)
- Review our [Product Design Requirements](./docs/PDR.md)
- Consider if it aligns with our mission

**When suggesting:**
- Use the feature request template
- Explain the problem you're solving
- Describe your proposed solution
- Provide examples or mockups if possible

### 🔧 Code Contributions

We welcome code contributions in these areas:

#### Backend (Python/FastAPI)
- API endpoints development
- Database models and schemas
- Data pipeline integration
- Financial calculations
- Authentication & authorization
- Performance optimization

#### Frontend (React/Next.js)
- UI components
- Data visualization
- Spreadsheet integration
- Real-time collaboration
- Mobile responsiveness
- Accessibility improvements

#### Data & ML
- Financial data scraping/parsing
- ML model development
- NLP for earnings calls
- Sentiment analysis
- Anomaly detection

#### DevOps & Infrastructure
- Docker optimization
- Kubernetes configurations
- CI/CD improvements
- Monitoring & logging
- Performance testing

#### Documentation
- API documentation
- User guides
- Code comments
- Tutorial videos
- README improvements

---

## 🛠️ Development Setup

### Prerequisites

- **Docker & Docker Compose** (recommended)
- **OR** Local setup:
  - Node.js 18+
  - Python 3.11+
  - PostgreSQL 15+
  - Redis 7.0+

### Quick Start with Docker

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/openequity.git
cd openequity

# Start development environment
make dev-setup

# Or manually:
docker-compose up -d
```

### Local Development Setup

#### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup pre-commit hooks
pip install pre-commit
pre-commit install

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload
```

#### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env.local
# Edit .env.local

# Start development server
npm run dev
```

### Verify Setup

- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/api/docs

---

## 📐 Coding Standards

### Python (Backend)

**Style Guide:** PEP 8

```python
# Use type hints
def calculate_wacc(debt: float, equity: float, cost_of_debt: float) -> float:
    """Calculate Weighted Average Cost of Capital."""
    total = debt + equity
    return (debt / total) * cost_of_debt + (equity / total) * cost_of_equity

# Use docstrings
class Company:
    """
    Represents a publicly traded company.

    Attributes:
        ticker: Stock ticker symbol
        name: Company name
    """
    pass
```

**Tools:**
- **Formatter:** Black (line length: 100)
- **Linter:** Flake8
- **Type Checker:** mypy

```bash
# Format code
black app/ tests/

# Lint
flake8 app/ tests/

# Type check
mypy app/
```

### TypeScript (Frontend)

**Style Guide:** Airbnb TypeScript

```typescript
// Use functional components with TypeScript
interface CompanyProps {
  ticker: string;
  name: string;
}

export const CompanyCard: React.FC<CompanyProps> = ({ ticker, name }) => {
  return (
    <div className="company-card">
      <h2>{name}</h2>
      <span>{ticker}</span>
    </div>
  );
};

// Use async/await
const fetchCompany = async (ticker: string): Promise<Company> => {
  const response = await fetch(`/api/companies/${ticker}`);
  return response.json();
};
```

**Tools:**
- **Formatter:** Prettier
- **Linter:** ESLint

```bash
# Format
npm run format

# Lint
npm run lint

# Type check
npm run type-check
```

### General Principles

1. **Write Self-Documenting Code**
   - Use descriptive variable names
   - Keep functions small and focused
   - Add comments only when necessary

2. **Test Your Code**
   - Write unit tests for new features
   - Maintain 80%+ code coverage
   - Test edge cases

3. **Follow DRY (Don't Repeat Yourself)**
   - Extract reusable logic
   - Create utility functions
   - Use composition

4. **Security First**
   - Never commit secrets
   - Validate all inputs
   - Use parameterized queries
   - Follow OWASP guidelines

---

## 🌿 Git Workflow

### Branch Naming

Use descriptive branch names:

```
feature/add-dcf-model
fix/authentication-bug
docs/update-readme
refactor/optimize-queries
test/add-api-tests
```

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add DCF valuation model
fix: resolve login authentication issue
docs: update API documentation
style: format code with black
refactor: optimize database queries
test: add unit tests for financial calculations
chore: update dependencies
```

**Examples:**

```bash
# Good
git commit -m "feat: implement company search with autocomplete"
git commit -m "fix: correct WACC calculation formula"
git commit -m "docs: add contribution guidelines"

# Bad
git commit -m "updates"
git commit -m "fixed stuff"
git commit -m "WIP"
```

### Workflow

1. **Fork the repository**

2. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make changes**
   - Write code
   - Add tests
   - Update documentation

4. **Commit changes**
   ```bash
   git add .
   git commit -m "feat: add your feature"
   ```

5. **Keep your fork updated**
   ```bash
   git remote add upstream https://github.com/original/openequity.git
   git fetch upstream
   git rebase upstream/main
   ```

6. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create Pull Request**

---

## 🔀 Pull Request Process

### Before Submitting

- [ ] Code follows style guidelines
- [ ] All tests pass locally
- [ ] New tests added for new features
- [ ] Documentation updated
- [ ] No merge conflicts with main
- [ ] Commits are clean and descriptive

### PR Template

When creating a PR, include:

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
How did you test this?

## Screenshots (if applicable)

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added to complex code
- [ ] Documentation updated
- [ ] No new warnings generated
- [ ] Tests added and passing
- [ ] Dependent changes merged
```

### Review Process

1. **Automated Checks**
   - CI/CD pipeline runs
   - Code quality checks
   - Test suite execution

2. **Peer Review**
   - At least one maintainer review required
   - Address review comments
   - Request re-review after changes

3. **Merge**
   - Maintainer merges when approved
   - Squash and merge for clean history

---

## 📝 Issue Guidelines

### Creating Issues

**Use Templates:**
- Bug Report
- Feature Request
- Documentation
- Question

**Good Issue Titles:**
- ✅ "API returns 500 error when fetching financial statements"
- ✅ "Add support for international stock exchanges"
- ❌ "Broken"
- ❌ "Feature request"

**Include:**
- Clear description
- Steps to reproduce (for bugs)
- Expected vs actual behavior
- System information
- Screenshots/logs

### Labels

We use labels to organize issues:

- `bug` - Something isn't working
- `enhancement` - New feature request
- `documentation` - Documentation improvements
- `good first issue` - Good for newcomers
- `help wanted` - Extra attention needed
- `priority: high` - High priority
- `backend` - Backend related
- `frontend` - Frontend related
- `database` - Database related

---

## 👥 Community

### Communication Channels

- **GitHub Discussions:** General discussions, Q&A
- **GitHub Issues:** Bug reports, feature requests
- **Discord:** Real-time chat (coming soon)
- **Email:** contact@openequity.org (coming soon)

### Getting Help

- Check [documentation](./docs/)
- Search [existing issues](https://github.com/yourusername/openequity/issues)
- Ask in [Discussions](https://github.com/yourusername/openequity/discussions)
- Join our Discord community

### Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Featured in monthly highlights
- Invited to core team (for consistent contributors)

---

## 🎓 Learning Resources

### Financial Concepts
- [CFA Institute](https://www.cfainstitute.org/)
- [Financial Modeling Course](https://www.wallstreetoasis.com/financial-modeling)
- [Valuation Guide](https://www.investopedia.com/valuation-4689730)

### Technical Resources
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [PostgreSQL Tutorial](https://www.postgresql.org/docs/)
- [React Best Practices](https://react.dev/learn)

---

## 📊 Development Priorities

### Phase 1 (Current - Months 1-3)
Focus areas:
- Core API development
- Database schema refinement
- Basic UI components
- Authentication system

### Phase 2 (Months 4-6)
Focus areas:
- Financial calculations
- Valuation models
- Data pipeline
- Collaboration features

See [ROADMAP.md](./docs/ROADMAP.md) for full timeline.

---

## ⚖️ License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

## 🙏 Thank You!

Every contribution, no matter how small, helps make professional financial tools accessible to everyone. Thank you for being part of this mission!

**Questions?** Feel free to ask in [Discussions](https://github.com/yourusername/openequity/discussions) or open an issue.

---

**Happy Contributing! 🚀**
