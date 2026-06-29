# Contributing to Sentimovie

Thank you for your interest in contributing to **Sentimovie**! We welcome and appreciate contributions of all kinds: bug fixes, feature requests, documentation improvements, UI redesigns, and optimization suggestions.

By participating in this project, you agree to abide by our standards of professional and respectful conduct.

---

## How Can I Contribute?

### 1. Report Bugs or Request Features
Before writing code, check the [Issues](https://github.com) page to see if your bug or feature request has already been reported. If not, open a new issue containing:
- A clear, descriptive title.
- Steps to reproduce the issue (for bugs).
- Expected vs. actual behavior.
- Context about your operating system, Python version, and dependency versions.

### 2. Submit Pull Requests (PRs)

Follow these steps to submit your contributions:

1. **Fork the Repository**  
   Click the "Fork" button at the top right of the GitHub page to create your own copy of the repository.

2. **Clone Your Fork**  
   Clone the repository locally:
   ```bash
   git clone https://github.com/YOUR-USERNAME/movie-recommendation.git
   cd movie-recommendation
   ```

3. **Create a Feature Branch**  
   Create a branch naming it descriptively:
   ```bash
   git checkout -b feature/amazing-new-feature
   # or
   git checkout -b bugfix/fix-memory-leak
   ```

4. **Set Up Your Environment**  
   Create a virtual environment and install all dependencies:
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate

   pip install -r requirements.txt
   ```

5. **Make Your Changes**  
   Write clean, well-documented, and strictly typed code. Follow the existing architecture and structure.

6. **Validate Your Changes**  
   Run linting, formatting, and unit tests to ensure nothing is broken.
   - **Linting & Formatting**: We use `ruff` to enforce styling guidelines.
     ```bash
     ruff check .         # Check for lint errors
     ruff format --check .  # Check formatting
     ```
     To auto-fix format errors, run:
     ```bash
     ruff format .
     ```
   - **Run Tests**:
     ```bash
     pytest tests/
     ```

7. **Commit and Push**  
   Write clear, concise commit messages following standard guidelines:
   ```bash
   git commit -am "feat: add emotion-to-genre mapping configuration"
   git push origin feature/amazing-new-feature
   ```

8. **Submit a Pull Request**  
   Go to the original Sentimovie repository on GitHub and click "Compare & pull request". Provide a detailed description of your changes, reference any related issues, and wait for feedback!

---

## Coding Guidelines
- **Type Annotations**: Always include type hints for function arguments and return types.
- **Docstrings**: Document classes, methods, and functions using Google-style docstrings.
- **Fallbacks First**: When integrating external services, ensure there is always a clean offline or rule-based fallback to preserve high-availability.
