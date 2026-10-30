# Contributing to RouterLink

Thank you for your interest in contributing to **RouterLink**! We welcome contributions to our backend, WebUI, Android client, documentation, and MikroTik automation scripts.

## Code of Conduct
We are committed to providing a welcoming, inclusive, and harassment-free environment for all contributors.

## How Can I Contribute?
1. **Reporting Bugs**: Check existing issues first. Submit reproducible bug reports with log snippets, RouterOS version, and client details.
2. **Suggesting Enhancements**: Open an issue describing the proposed feature, user value, and technical feasibility.
3. **Submitting Pull Requests**:
   - Fork the repository.
   - Create a feature branch (`git checkout -b feature/amazing-feature`).
   - Write clean, well-tested, documented code.
   - Run tests (`pytest`, `npm test`, `./gradlew test`).
   - Follow semantic commit messages (`feat: ...`, `fix: ...`, `docs: ...`).
   - Open a Pull Request against `main`.

## Engineering Standards
- **Backend**: Python 3.11+, typed with Type Hints, black/flake8 formatted, unit tests in `tests/backend/`.
- **Frontend**: TypeScript, React functional components with hooks, Tailwind CSS for styling.
- **Android**: Modern Kotlin, Jetpack Compose, Material 3, clean architecture, MVVM.
- **MikroTik**: Scripts must be idempotent, strictly non-destructive, and commented. Never overwrite existing customer bridges, firewall rules, or DNS.
- **Security**: Never commit credentials, private keys, certificates, or unencrypted sensitive test data.

