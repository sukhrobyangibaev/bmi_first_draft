# Thesis Generator 📚

*Read this in other languages: [Русский](docs/translations/README.ru.md), [O'zbek](docs/translations/README.uz.md)*

An automated tool that analyzes source code files and generates a structured thesis document using Large Language Models through API integration.

## Prerequisites ✅

- Python 3.8 or higher
- Access to an OpenAI-compatible API (Google, Anthropic, or OpenAI)
- **Project source code files for analysis**

## Installation 🛠️

1. Clone the repository:
```bash
git clone https://github.com/sukhrobyangibaev/bmi_first_draft.git
cd bmi_first_draft
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. Create environment configuration:
```bash
# For Unix/Linux/MacOS
cp .env.example .env

# For Windows (Command Prompt)
copy .env.example .env

# For Windows (PowerShell)
Copy-Item .env.example .env
```

4. Configure your `.env` file with appropriate settings:
```env
API_KEY=your_api_key_here
BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
LOW_RATE_LIMITS=true
MODEL=gemini-exp-1206
PROJECT_FILES_DIR=project_files
TRANSLATE=true
TRANSLATION_LANG=RU
```

Important configuration notes:

- **API_KEY**: Get your free Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey)
- **BASE_URL**: Keep the default value when using Gemini API
- **LOW_RATE_LIMITS**: Leave as `true` when using free Gemini API key (adds necessary request delays)
- **MODEL**: Available models can be found in [Gemini API documentation](https://ai.google.dev/gemini-api/docs/models/gemini). Currently, `gemini-exp-1206` provides the best results. If you encounter errors with this model, use `gemini-2.0-flash-exp` as a reliable alternative
- **PROJECT_FILES_DIR**: Create a folder with this name to store your source code files
- **TRANSLATE**: Set to `true` if you want translation, `false` if you only need English
- **TRANSLATION_LANG**: Use `RU` for Russian translation or `UZ` for Uzbek translation

5. Create the project files directory:
```bash
# For Unix/Linux/MacOS
mkdir project_files

# For Windows (Command Prompt or PowerShell)
md project_files
```

## Usage 🚀

1. Place your project's main source code files in the `project_files` directory:
   - Include only your core project files
   - Do not include external libraries, virtual environments, or dependency files
   - Example: If you have a Python project, include your `.py` files but not `venv/` or `site-packages/`

2. Run the thesis generator:
```bash
python first_draft.py
```

3. The script will generate two main files in the `draft` directory:
   - `draft/EN/THESIS_PLAN_EN.txt`: Thesis structure and outline
   - `draft/EN/THESIS_MAIN_TEXT_EN.txt`: Complete thesis content

4. If translation is enabled, additional files will be generated in:
   - `draft/RU/` for Russian translation
   - `draft/UZ/` for Uzbek translation

> **Note:** The generated content is a first draft and should be carefully reviewed and edited. This is especially important for translated versions.


## Output Structure 📋

The generated thesis follows this structure:

1. Introduction
   - Relevance
   - Purpose
   - Object
   - Subject

2. Part I: Systematic Analysis
   - General Analysis (§1.1)
   - Principles (§1.2)
   - Problem Statement (§1.3)

3. Part II: Development
   - Design and Creation (§2.1)
   - Development Sequence (§2.2)
   - Usage Instructions (§2.3)

4. Conclusion

5. References

6. Appendix

## Contributing 🤝

Contributions are welcome! Please feel free to submit a Pull Request.

## Support ❓

For issues and feature requests, please create an issue in the repository.

## Acknowledgements 🙏

Special thanks to Google for providing free access to the Gemini API.