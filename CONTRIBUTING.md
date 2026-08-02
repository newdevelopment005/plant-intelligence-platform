# Contributing to Plant Intelligence Platform

Thank you for considering contributing to PIP!

## Development Setup

1. Fork and clone the repository
2. Copy `.env.example` to `.env`
3. Follow the setup instructions in README.md

## Code Standards

### Python (API & AI Service)
- Use type hints everywhere
- Follow PEP 8 (enforced by Ruff)
- Write docstrings for public functions
- Maximum line length: 100 characters
- Use async/await for database operations

### TypeScript (Frontend)
- Use TypeScript strict mode
- Follow ESLint rules
- Use Server Components by default
- Only use "use client" when necessary

## Commit Messages

Use conventional commits:
- `feat: add new feature`
- `fix: resolve bug`
- `docs: update documentation`
- `test: add tests`
- `refactor: improve code structure`

## Pull Request Process

1. Create a feature branch from `main`
2. Make your changes
3. Run `make lint` and `make test`
4. Submit a PR with a clear description
5. Wait for CI to pass
6. Request review

## Testing Requirements

- All new features must include tests
- Bug fixes must include regression tests
- Maintain or improve code coverage
- Run the full test suite before submitting

## Questions?

Open a discussion on GitHub or contact the team.
