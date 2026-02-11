# Contributing to AI Memory Assistant

First off, thank you for considering contributing to AI Memory Assistant! 🎉

## How Can I Contribute?

### 🐛 Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates. When you create a bug report, include as many details as possible:

**Bug Report Template:**
- **Description**: Clear description of the bug
- **Steps to Reproduce**: Detailed steps to reproduce the issue
- **Expected Behavior**: What you expected to happen
- **Actual Behavior**: What actually happened
- **Environment**: 
  - OS (Windows/macOS/Linux)
  - Python version
  - PostgreSQL version
  - Relevant package versions
- **Error Messages**: Full error messages and stack traces
- **Screenshots**: If applicable

### 💡 Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

- **Clear title** describing the enhancement
- **Detailed description** of the proposed functionality
- **Use cases** explaining when/why this would be useful
- **Possible implementation** if you have ideas

### 🔧 Pull Requests

1. **Fork the repo** and create your branch from `main`
2. **Make your changes**:
   - Write clear, commented code
   - Follow the existing code style (PEP 8)
   - Add docstrings to functions
   - Update documentation if needed
3. **Test your changes**:
   - Ensure all existing tests pass
   - Add tests for new features
   - Test manually with the app
4. **Commit your changes**:
   - Use clear, descriptive commit messages
   - Reference issues if applicable (e.g., "Fixes #123")
5. **Push to your fork** and submit a pull request

## Development Setup

### 1. Clone Your Fork

```bash
git clone https://github.com/YOUR_USERNAME/AI-memory-assistance.git
cd AI-memory-assistance
```

### 2. Set Up Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
# Edit .env with your credentials
```

### 3. Initialize Database

```bash
python setup_database.py
```

### 4. Run Tests

```bash
python test_config.py
```

### 5. Start Development Server

```bash
streamlit run app.py
```

## Code Style Guidelines

### Python

- Follow [PEP 8](https://pep8.org/) style guide
- Use meaningful variable and function names
- Maximum line length: 88 characters (Black formatter)
- Use type hints where appropriate

**Example:**

```python
def get_session_history(session_id: str, connection_string: str) -> SQLChatMessageHistory:
    """
    Create or retrieve PostgreSQL chat message history for a session.
    
    Args:
        session_id: Unique identifier for the chat session
        connection_string: PostgreSQL connection string
        
    Returns:
        SQLChatMessageHistory instance for the session
    """
    return SQLChatMessageHistory(
        session_id=session_id,
        connection=connection_string,
        table_name="message_store",
    )
```

### Documentation

- Add docstrings to all functions and classes
- Use Google-style docstrings
- Update README.md for significant changes
- Include inline comments for complex logic

### Git Commit Messages

- Use present tense ("Add feature" not "Added feature")
- Use imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit first line to 72 characters
- Reference issues and pull requests after first line

**Good commit messages:**
```
Add session export functionality

- Add export_session() function to app.py
- Create CSV export format
- Add download button to sidebar
Fixes #45
```

## Project Structure

```
AI-memory-assistance/
├── app.py                    # Main Streamlit application
├── setup_database.py         # Database initialization
├── test_config.py           # Configuration tests
├── schema.sql               # Database schema
├── requirements.txt         # Dependencies
├── .env.example            # Environment template
├── .gitignore              # Git ignore rules
├── README.md               # Project documentation
├── LICENSE                 # MIT License
└── CONTRIBUTING.md         # This file
```

## Areas for Contribution

Looking for ways to contribute? Here are some ideas:

### 🌟 Feature Ideas

- [ ] Export conversation history (PDF, TXT, JSON)
- [ ] Multi-user support with authentication
- [ ] Voice input/output integration
- [ ] Image upload and analysis
- [ ] Web search integration
- [ ] Conversation tagging and search
- [ ] Analytics dashboard
- [ ] Custom LLM model selection UI
- [ ] Conversation templates
- [ ] Automatic conversation summarization

### 🐛 Known Issues

Check the [Issues](https://github.com/dev-k99/AI-memory-assistance/issues) page for current bugs and feature requests.

### 📚 Documentation

- Improve installation instructions
- Add more usage examples
- Create video tutorials
- Translate documentation
- Add API documentation

## Testing

### Manual Testing Checklist

Before submitting a PR, verify:

- [ ] App starts without errors
- [ ] Database connection works
- [ ] Messages persist after refresh
- [ ] Clear memory function works
- [ ] New session creates fresh context
- [ ] No console errors
- [ ] UI is responsive
- [ ] Memory viewer displays correctly

### Automated Tests

We welcome contributions to our test suite:

- Add unit tests for new functions
- Add integration tests for features
- Improve test coverage
- Add performance benchmarks

## Questions?

- Open an issue for questions
- Discuss ideas in GitHub Discussions
- Check existing issues and PRs first

## Code of Conduct

### Our Standards

- Be respectful and inclusive
- Accept constructive criticism gracefully
- Focus on what's best for the community
- Show empathy towards others

### Unacceptable Behavior

- Harassment or discriminatory language
- Trolling or insulting comments
- Publishing others' private information
- Other unprofessional conduct

## Recognition

Contributors will be recognized in:
- GitHub contributors page
- README.md acknowledgments section
- Release notes (for significant contributions)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to AI Memory Assistant!** 🙏

Every contribution, no matter how small, makes a difference! 