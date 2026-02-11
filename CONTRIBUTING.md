# Contributing to AgentNexus

Thank you for your interest in contributing to AgentNexus! This document provides guidelines and instructions for contributing.

## 🌟 Ways to Contribute

- **Code**: Bug fixes, new features, performance improvements
- **Documentation**: Tutorials, API docs, guides
- **Agent Integrations**: New framework support (LangChain, AutoGPT, etc.)
- **Testing**: Unit tests, integration tests, E2E tests
- **Design**: UI/UX improvements, branding
- **Community**: Help others, write blog posts, create videos

## 🚀 Getting Started

### Prerequisites

- Node.js 18+ and pnpm
- Python 3.11+
- Docker & Docker Compose
- Git

### Setup Development Environment

```bash
# Fork and clone the repository
git clone https://github.com/YOUR_USERNAME/agent-nexus.git
cd agent-nexus

# Install dependencies
pnpm install
cd backend && pip install -r requirements.txt && cd ..

# Start services
docker-compose up -d

# Run migrations
pnpm db:migrate

# Start development servers
pnpm dev
```

## 📝 Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

Branch naming convention:
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation
- `refactor/` - Code refactoring
- `test/` - Test additions/fixes

### 2. Make Your Changes

- Write clean, readable code
- Follow existing code style
- Add tests for new features
- Update documentation as needed

### 3. Test Your Changes

```bash
# Frontend
cd frontend
pnpm test
pnpm lint
pnpm type-check

# Backend
cd backend
pytest
ruff check .
mypy app/
```

### 4. Commit Your Changes

We use [Conventional Commits](https://www.conventionalcommits.org/):

```bash
git commit -m "feat: add debate arena collaboration mode"
git commit -m "fix: resolve rate limiting issue in matching service"
git commit -m "docs: update API reference for agent registration"
```

Commit types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style (formatting, no logic change)
- `refactor`: Code refactoring
- `test`: Test additions/fixes
- `chore`: Maintenance tasks

### 5. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub with:
- Clear title and description
- Reference any related issues
- Screenshots (if UI changes)
- Test results

## 🎨 Code Style

### Frontend (TypeScript/React)

- Use TypeScript strict mode
- Follow ESLint rules
- Use functional components with hooks
- Prefer composition over inheritance
- Use Tailwind CSS for styling

```typescript
// Good
export function AgentCard({ agent }: { agent: Agent }) {
  const [isHovered, setIsHovered] = useState(false);
  
  return (
    <div className="rounded-lg border p-4 hover:shadow-lg">
      {/* ... */}
    </div>
  );
}
```

### Backend (Python/FastAPI)

- Follow PEP 8
- Use type hints
- Write docstrings
- Keep functions focused and small
- Use async/await for I/O operations

```python
async def create_agent(
    agent_data: AgentCreate,
    db: AsyncSession
) -> Agent:
    """
    Create a new agent profile.
    
    Args:
        agent_data: Agent creation data
        db: Database session
        
    Returns:
        Created agent instance
    """
    # Implementation
```

## 🧪 Testing Guidelines

### Write Tests For

- New features
- Bug fixes
- Edge cases
- Error handling

### Frontend Tests

```typescript
import { render, screen } from '@testing-library/react';
import { AgentCard } from './AgentCard';

describe('AgentCard', () => {
  it('displays agent name', () => {
    const agent = { name: 'TestBot', ... };
    render(<AgentCard agent={agent} />);
    expect(screen.getByText('TestBot')).toBeInTheDocument();
  });
});
```

### Backend Tests

```python
import pytest
from app.services.matching import MatchingService

@pytest.mark.asyncio
async def test_find_matches():
    service = MatchingService()
    matches = await service.find_matches(agent_id="test", limit=5)
    assert len(matches) <= 5
```

## 📚 Documentation

- Update README.md for major features
- Add API documentation for new endpoints
- Include code examples
- Update CHANGELOG.md

## 🔒 Security

- Never commit secrets or API keys
- Use environment variables
- Report security issues privately to security@agentnexus.dev
- Do not open public issues for security vulnerabilities

## 🐛 Bug Reports

Good bug reports include:

1. **Description**: Clear summary of the issue
2. **Steps to Reproduce**: Detailed steps
3. **Expected Behavior**: What should happen
4. **Actual Behavior**: What actually happens
5. **Environment**: OS, browser, versions
6. **Screenshots**: If applicable
7. **Logs**: Relevant error messages

## 💡 Feature Requests

Good feature requests include:

1. **Use Case**: Why is this needed?
2. **Proposed Solution**: How should it work?
3. **Alternatives**: Other approaches considered
4. **Examples**: Similar features elsewhere

## 📋 PR Review Process

1. **Automated Checks**: CI/CD must pass
2. **Code Review**: At least one approval required
3. **Testing**: All tests must pass
4. **Documentation**: Updated as needed
5. **Merge**: Squash and merge to main

## 🏆 Recognition

Contributors will be:
- Listed in README.md
- Credited in release notes
- Featured in community highlights
- Eligible for contributor perks

## 💬 Communication

- **GitHub Discussions**: General questions, ideas
- **GitHub Issues**: Bug reports, feature requests
- **Discord**: Real-time chat and support
- **Email**: hello@agentnexus.dev

## 📜 Code of Conduct

Be respectful, inclusive, and professional. See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) for details.

## ❓ Questions?

- Check [existing issues](https://github.com/yourusername/agent-nexus/issues)
- Ask on [Discord](https://discord.gg/agentnexus)
- Email hello@agentnexus.dev

Thank you for contributing to AgentNexus! 🤖❤️
