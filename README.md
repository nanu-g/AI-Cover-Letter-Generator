# AI Cover Letter Generator

A Streamlit-based application that helps users create, customize, and export job-specific cover letters. It also analyzes skills mentioned in a job description and provides a skill-match summary.

## Features

- **Cover Letter Generation:** Generate a cover letter using candidate details and job information.
- **Writing Styles:** Choose Professional, Standard, or Creative writing styles.
- **Editable Output:** Review and edit the generated cover letter before exporting.
- **PDF Export:** Download the cover letter as a PDF.
- **Job Skill Analysis:** Identify matched and missing skills based on the job description.
- **Email Validation:** Validate email input and provide suggestions for possible domain typos.
- **Information Completeness:** Check whether important candidate details are provided.

## Technologies Used

- Python
- Streamlit
- ReportLab
- Regular expressions and rule-based text processing

## Project Structure

```text
AI-Cover-Letter-Generator/
├── app.py
├── requirements.txt
├── .gitignore
├── README.md
└── screenshots/
```

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/nanu-g/AI-Cover-Letter-Generator.git
cd AI-Cover-Letter-Generator
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the environment

For Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 5. Run the application

```bash
python -m streamlit run app.py
```

The application will open in your browser.

## How to Use

1. Enter your candidate information.
2. Add your technical skills and project details.
3. Paste the job description.
4. Select a preferred writing style.
5. Generate and edit the cover letter.
6. Review the job skill analysis and information completeness.
7. Download the final cover letter as a PDF.

## Implementation Note

The current version uses predefined templates, rule-based text processing, and skill matching. It does not currently rely on an external generative AI API.

## Future Enhancements

- Integrate a large language model for more context-aware cover letters.
- Expand the skill database and improve skill extraction.
- Add support for multiple resume formats.
- Improve personalization using resume and job-description analysis.

## Author

**GitHub:** [nanu-g](https://github.com/nanu-g)

## License

No license has been added yet.
