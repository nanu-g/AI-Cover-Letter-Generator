import re
from io import BytesIO
from datetime import date
from difflib import get_close_matches
from xml.sax.saxutils import escape

import streamlit as st

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer





# ============================================================
# 1. PAGE CONFIGURATION
# ============================================================


# Page configuration
st.set_page_config(
    page_title="AI Cover Letter Generator",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Professional light theme styling
st.markdown("""
<style>
    .stApp {
        background-color: #F7F9FC;
        color: #1F2937;
    }

    .block-container {
        max-width: 1150px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    h1, h2, h3 {
        color: #17365D;
    }

    .main-title {
        color: #17365D;
        font-size: 2.4rem;
        font-weight: 750;
        text-align: center;
        margin-bottom: 0.4rem;
    }

    .subtitle {
        color: #64748B;
        text-align: center;
        font-size: 1.05rem;
        margin-bottom: 2rem;
    }

    
    /* Main action and download buttons */
    div.stButton > button,
    div.stDownloadButton > button {
        background-color: #17365D;
        color: #FFFFFF;
        border: 1px solid #17365D;
        border-radius: 8px;
        min-height: 46px;
        padding: 0.65rem 1.2rem;
        font-size: 1rem;
        font-weight: 600;
        transition: background-color 0.2s ease;
    }

    div.stButton > button:hover,
    div.stDownloadButton > button:hover {
        background-color: #24558A;
        color: #FFFFFF;
        border-color: #24558A;
    }

    div.stButton > button:focus,
    div.stDownloadButton > button:focus {
        box-shadow: 0 0 0 3px rgba(36, 85, 138, 0.25);
    }


    div[data-testid="stTextInput"] input,
    div[data-testid="stTextArea"] textarea {
        border-radius: 7px;
    }

    div[data-testid="stForm"] {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 1.2rem;
    }

    div[data-testid="stMetric"] {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        padding: 1rem;
        border-radius: 10px;
    }

    hr {
        border-color: #E2E8F0;
    }
    /* Section headings */
    .section-heading {
        color: #17365D;
        font-size: 1.25rem;
        font-weight: 700;
        padding-bottom: 0.6rem;
        margin-top: 1.2rem;
        margin-bottom: 0.8rem;
        border-bottom: 2px solid #DCE6F1;
    }

    /* Supporting text */
    .section-description {
        color: #64748B;
        font-size: 0.92rem;
        margin-top: -0.35rem;
        margin-bottom: 1rem;
    }

    /* Input labels */
    div[data-testid="stTextInput"] label,
    div[data-testid="stTextArea"] label,
    div[data-testid="stSelectbox"] label {
        color: #334155;
        font-weight: 600;
    }

</style>
""", unsafe_allow_html=True)


# ============================================================
# 2. SKILL DATABASE
# ============================================================

SKILL_DATABASE = [
    "python",
    "sql",
    "machine learning",
    "deep learning",
    "data analysis",
    "data visualization",
    "pandas",
    "numpy",
    "excel",
    "power bi",
    "tableau",
    "tensorflow",
    "pytorch",
    "natural language processing",
    "nlp",
    "artificial intelligence",
    "statistics",
    "scikit-learn",
    "communication",
    "problem solving",
    "git",
    "github",
    "java",
    "c++",
    "html",
    "css",
    "javascript",
    "react",
    "data science",
]

SKILL_DISPLAY_NAMES = {
    "python": "Python",
    "sql": "SQL",
    "machine learning": "Machine Learning",
    "deep learning": "Deep Learning",
    "data analysis": "Data Analysis",
    "data visualization": "Data Visualization",
    "pandas": "Pandas",
    "numpy": "NumPy",
    "excel": "Excel",
    "power bi": "Power BI",
    "tableau": "Tableau",
    "tensorflow": "TensorFlow",
    "pytorch": "PyTorch",
    "natural language processing": "Natural Language Processing",
    "nlp": "NLP",
    "artificial intelligence": "Artificial Intelligence",
    "statistics": "Statistics",
    "scikit-learn": "Scikit-learn",
    "communication": "Communication",
    "problem solving": "Problem-Solving",
    "git": "Git",
    "github": "GitHub",
    "java": "Java",
    "c++": "C++",
    "html": "HTML",
    "css": "CSS",
    "javascript": "JavaScript",
    "react": "React",
    "data science": "Data Science",
}


# ============================================================
# 3. TEXT NORMALIZATION
# ============================================================

def normalize_text(text):
    """Normalize text for comparison."""

    text = text.lower()
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def correct_skill_capitalization(skills):
    """Correct capitalization of recognized technical skills."""

    corrected_skills = []

    for skill in re.split(r"[,;\n]", skills):

        skill = skill.strip()

        if not skill:
            continue

        normalized = skill.lower()

        corrected = SKILL_DISPLAY_NAMES.get(
            normalized,
            skill,
        )

        corrected_skills.append(corrected)

    return ", ".join(corrected_skills)


def format_job_title(title):
    """Format a job title using title case."""

    title = re.sub(r"\s+", " ", title.strip())

    if not title:
        return ""

    # Preserve common abbreviations.
    abbreviations = {
        "ai": "AI",
        "ml": "ML",
        "hr": "HR",
        "ui": "UI",
        "ux": "UX",
        "it": "IT",
        "sql": "SQL",
    }

    words = title.lower().split()

    corrected_words = []

    for word in words:

        if word in abbreviations:
            corrected_words.append(abbreviations[word])

        else:
            corrected_words.append(word.capitalize())

    return " ".join(corrected_words)


def format_company_name(company):
    """
    Apply conservative capitalization corrections.

    Recognizes common company names while preserving the
    user's original spelling for unknown company names.
    """

    company = re.sub(r"\s+", " ", company.strip())

    known_companies = {
        "microsoft": "Microsoft",
        "google": "Google",
        "amazon": "Amazon",
        "openai": "OpenAI",
        "apple": "Apple",
        "meta": "Meta",
        "nvidia": "NVIDIA",
        "intel": "Intel",
        "amd": "AMD",
        "ibm": "IBM",
        "accenture": "Accenture",
        "infosys": "Infosys",
        "wipro": "Wipro",
        "tcs": "TCS",
        "deloitte": "Deloitte",
        "salesforce": "Salesforce",
    }

    normalized = company.lower()

    if normalized in known_companies:
        return known_companies[normalized]

    # Preserve unusual branding and acronyms rather than
    # blindly changing every word in a company name.
    return company



def format_education(education):
    """
    Normalize common degree abbreviations and specializations
    without inventing qualifications or claiming completion.
    """

    education = re.sub(r"\s+", " ", education.strip())

    # Normalize degree abbreviations.
    replacements = [
        (r"\bB\s*\.?\s*E\s*\.?\b", "B.E."),
        (r"\bB\s*\.?\s*Tech\s*\.?\b", "B.Tech."),
        (r"\bM\s*\.?\s*Tech\s*\.?\b", "M.Tech."),
        (r"\bM\s*\.?\s*E\s*\.?\b", "M.E."),
        (r"\bB\s*\.?\s*Sc\s*\.?\b", "B.Sc."),
        (r"\bM\s*\.?\s*Sc\s*\.?\b", "M.Sc."),
        (r"\bMBA\b", "MBA"),
    ]

    for pattern, replacement in replacements:
        education = re.sub(
            pattern,
            replacement,
            education,
            flags=re.IGNORECASE,
        )

    # Remove duplicate periods after degree abbreviations.
    education = re.sub(
        r"\b(B\.E|B\.Tech|M\.E|M\.Tech|B\.Sc|M\.Sc)\.+",
        r"\1.",
        education,
        flags=re.IGNORECASE,
    )

    # Normalize common specializations.
    education = re.sub(
        r"\bAI\s*&\s*DS\b",
        "Artificial Intelligence and Data Science (AI & DS)",
        education,
        flags=re.IGNORECASE,
    )

    education = re.sub(
        r"\bCSE\b",
        "Computer Science and Engineering (CSE)",
        education,
        flags=re.IGNORECASE,
    )

    # Ensure a space after degree abbreviations.
    education = re.sub(
        r"\b(B\.E\.|B\.Tech\.|M\.E\.|M\.Tech\.|B\.Sc\.|M\.Sc\.)\s*",
        r"\1 ",
        education,
        flags=re.IGNORECASE,
    )

    # Clean duplicate spaces and surrounding whitespace.
    education = re.sub(r"\s+", " ", education).strip()

    return education



# ============================================================
# 4. EMAIL VALIDATION
# ============================================================

def validate_email(email):
    """
    Check the basic email structure and identify possible
    common domain typos.
    """

    email = email.strip()

    if not email:
        return True, None

    pattern = (
        r"^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+"
        r"@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+$"
    )

    if not re.fullmatch(pattern, email):

        return (
            False,
            "Please enter an email address in a valid format, "
            "such as name@example.com.",
        )

    domain = email.rsplit("@", 1)[1].lower()

    common_domains = [
        "gmail.com",
        "outlook.com",
        "hotmail.com",
        "yahoo.com",
        "icloud.com",
        "proton.me",
    ]

    if domain not in common_domains:

        possible_match = get_close_matches(
            domain,
            common_domains,
            n=1,
            cutoff=0.80,
        )

        if possible_match:

            suggestion = possible_match[0]

            return (
                True,
                f"Your email format is valid, but the domain "
                f"'{domain}' may be a typo. Did you mean "
                f"'{suggestion}'? Please verify before continuing.",
            )

    return True, None


# ============================================================
# 5. SKILL EXTRACTION AND MATCHING
# ============================================================

def extract_skills(text):
    """Identify recognized skills in a text."""

    normalized_text = normalize_text(text)

    found_skills = []

    for skill in SKILL_DATABASE:

        pattern = (
            r"(?<!\w)"
            + re.escape(skill)
            + r"(?!\w)"
        )

        if re.search(pattern, normalized_text):

            found_skills.append(skill)

    return found_skills


def match_skills(candidate_skills, job_description):
    """Compare candidate skills with job requirements."""

    candidate_found = extract_skills(candidate_skills)

    required_skills = extract_skills(job_description)

    matched = [
        skill
        for skill in required_skills
        if skill in candidate_found
    ]

    missing = [
        skill
        for skill in required_skills
        if skill not in candidate_found
    ]

    return required_skills, matched, missing


# ============================================================
# 6. PROJECT FORMATTING
# ============================================================

def format_projects(projects):
    """
    Convert numbered or line-separated project descriptions
    into readable project names.
    """

    if not projects.strip():
        return []

    lines = projects.replace("\r", "\n").split("\n")

    cleaned_projects = []

    for line in lines:

        line = line.strip()

        if not line:
            continue

        # Remove leading numbers such as 1. or 2)
        line = re.sub(
            r"^\s*(?:\d+[\.\)]|[-*•])\s*",
            "",
            line,
        )

        if line:
            cleaned_projects.append(line)

    # If the user entered everything in a single line,
    # support common numbered project formats.
    if len(cleaned_projects) == 1:

        single_line = cleaned_projects[0]

        parts = re.split(
            r"\s+\d+[\.\)]\s*",
            single_line,
        )

        if len(parts) > 1:

            cleaned_projects = [
                part.strip()
                for part in parts
                if part.strip()
            ]

    return cleaned_projects


# ============================================================
# 7. COVER LETTER GENERATION
# ============================================================

def generate_cover_letter(
    name,
    email,
    education,
    job_title,
    company,
    experience,
    skills,
    projects,
    job_description,
    style,
):
    """Generate a cover letter in the selected writing style."""

    name = re.sub(r"\s+", " ", name.strip())

    email = email.strip()

    education = format_education(education)

    job_title = format_job_title(job_title)

    company = format_company_name(company)

    corrected_skills = correct_skill_capitalization(skills)

    required, matched, missing = match_skills(
        skills,
        job_description,
    )

    project_list = format_projects(projects)

    
    if corrected_skills:
     skill_sentence = (
        f"My technical skills include {corrected_skills}. "
        f"I am keen to apply these skills to practical "
        f"challenges and contribute to the team's work."
    )
    else:
     skill_sentence = (
        "I am committed to strengthening my technical "
        "knowledge and applying it to practical challenges."
    )

    if matched:

        matched_display = [
            SKILL_DISPLAY_NAMES.get(skill, skill)
            for skill in matched
        ]

        matched_text = ", ".join(matched_display)

        alignment_sentence = (
              f"My skills in {matched_text} are relevant to "
              f"several of the requirements for this position."
        )

    else:

        alignment_sentence = (
            "I am eager to develop the additional technical "
            "skills required for this role."
        )

    
    if education:
      education_sentence = (
        f"My educational background in {education} "
        f"has helped me develop my technical knowledge, "
        f"analytical thinking, and problem-solving abilities."
    )
    else:
      education_sentence = (
        "My academic and independent learning experiences "
        "have encouraged me to strengthen my technical "
        "knowledge and problem-solving abilities."
    )


    #project formatting and sentence construction

    # Display each project as a separate bullet point.

    if project_list:
      project_sentence = (
        "My academic projects include:\n\n"
        + "\n".join(
            f"- {project}" for project in project_list
        )
        + "\n\nThese projects have helped me apply my "
        "knowledge to practical problems and strengthen "
        "my technical and analytical skills."
    )
    else:
     project_sentence = (
        "I am motivated to apply my technical and analytical "
        "skills to practical challenges and contribute to "
        "the team's objectives."
    )

    # Experience wording must not claim experience the user
    # has not provided.
    
# Generate experience wording based on the candidate's background.

    if experience == "Student / Fresher":

      experience_sentence = (
         "As a student and aspiring professional, I value "
         "continuous learning, collaboration, and opportunities "
         "to gain practical experience."
    )

    elif experience == "Internship Experience":

       experience_sentence = (
         "Through my internship experience, I have gained "
         "exposure to professional workflows, teamwork, "
         "and the practical application of technical knowledge."
    )

    else:

     experience_sentence = (
        "I am prepared to draw on my professional experience "
        "to solve relevant problems, collaborate with colleagues, "
        "and contribute to the team's objectives."
    )


    # --------------------------------------------------------
    # DISTINCT WRITING STYLES
    # --------------------------------------------------------

    
# DISTINCT WRITING STYLES

    if style == "Professional":

      opening = (
        f"I am writing to apply for the position of "
        f"{job_title} at {company}. My background and "
        f"technical skills have prepared me to approach "
        f"the responsibilities of this role thoughtfully."
    )

      motivation = (
        f"I would welcome the opportunity to contribute "
        f"to {company}, apply my relevant skills, and "
        f"continue developing professionally."
    )

      closing = (
        "Thank you for considering my application. "
        "I would welcome an opportunity to discuss "
        "my suitability for this position."
    )

    elif style == "Standard":

      opening = (
        f"I am excited to apply for the {job_title} "
        f"position at {company}. I look forward to "
        f"using my skills, learning new technologies, "
        f"and contributing to meaningful work."
    )

      motivation = (
        f"I believe this opportunity at {company} would "
        f"allow me to learn from the team, apply my "
        f"knowledge, and grow professionally."
    )

      closing = (
        "Thank you for reviewing my application. "
        "I look forward to the possibility of discussing "
        "this opportunity with you."
    )

    elif style == "Creative":

      opening = (
        f"I enjoy exploring challenges, learning through "
        f"hands-on work, and turning ideas into practical "
        f"solutions. That is what draws me to the "
        f"{job_title} opportunity at {company}."
    )

      motivation = (
        f"I would be excited to bring curiosity, "
        f"dedication, and a willingness to learn to "
        f"{company}, while contributing to the team's work."
    )

      closing = (
        "Thank you for considering my application. "
        "I would love the opportunity to discuss how "
        "my interests and skills could contribute to your team."
    )

    else:

      opening = (
        f"I am interested in applying for the {job_title} "
        f"position at {company} and using my relevant "
        f"skills to contribute to the team."
    )

      motivation = (
        f"I would value the opportunity to contribute "
        f"to {company} while continuing to develop my abilities."
    )

      closing = (
        "Thank you for your time and consideration. "
        "I look forward to hearing from you."
    )


    # --------------------------------------------------------
    # ASSEMBLE THE LETTER
    # --------------------------------------------------------

    letter_parts = [
        name,
    ]

    if email:
        letter_parts.append(email)

    letter_parts.extend([
        "",
        date.today().strftime("%d %B %Y"),
        "",
        "Hiring Manager",
        company,
        "",
        f"Subject: Application for {job_title}",
        "",
        "Dear Hiring Manager,",
        "",
        opening,
        "",
        education_sentence,
        "",
        skill_sentence,
        "",
        alignment_sentence,
        "",
        project_sentence,
        "",
        experience_sentence,
        "",
        motivation,
        "",
        closing,
        "",
        "Sincerely,",
        name,
    ])

    letter = "\n".join(letter_parts)

    # --------------------------------------------------------
    # INFORMATION COMPLETENESS SCORE
    # --------------------------------------------------------

    
# INFORMATION COMPLETENESS SCORE

    quality_checks = {
       "Candidate name included": bool(name.strip()),
       "Job title included": bool(job_title.strip()),
       "Company name included": bool(company.strip()),
       "Education information included": bool(education.strip()),
       "Technical skills included": bool(skills.strip()),
       "Project details included": bool(projects.strip()),
       "Job description provided": bool(job_description.strip()),
       "Contact email included": bool(email.strip()),
}

    total_checks = len(quality_checks)
    completed_checks = sum(quality_checks.values())

    quality_score = (
      completed_checks / total_checks * 100
      if total_checks > 0
      else 0
)


    return (
        letter,
        required,
        matched,
        missing,
        quality_score,
        quality_checks,
    )


# ============================================================
# 8. PDF GENERATION
# ============================================================

def create_pdf(letter):
    """Create a formatted, downloadable PDF."""

    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=0.85 * inch,
        leftMargin=0.85 * inch,
        topMargin=0.65 * inch,
        bottomMargin=0.65 * inch,
        title="Cover Letter",
        author="Cover Letter Generator",
    )

    styles = getSampleStyleSheet()

    
    body_style = ParagraphStyle(
    "LetterBody",
    parent=styles["BodyText"],
    fontName="Helvetica",
    fontSize=10,
    leading=13,
    alignment=TA_LEFT,
    spaceAfter=6,
    wordWrap="LTR",
)


    name_style = ParagraphStyle(
        "ApplicantName",
        parent=styles["BodyText"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=17,
        spaceAfter=4,
    )

    subject_style = ParagraphStyle(
        "SubjectLine",
        parent=styles["BodyText"],
        fontName="Helvetica-Bold",
        fontSize=10.5,
        leading=15,
        spaceAfter=8,
    )

    story = []

    lines = letter.split("\n")

    for index, line in enumerate(lines):

        if not line.strip():

            story.append(Spacer(1, 3))

            continue

        safe_line = escape(line)

        if index == 0:

            story.append(
                Paragraph(safe_line, name_style)
            )

        elif line.startswith("Subject:"):

            story.append(
                Paragraph(safe_line, subject_style)
            )

        else:

            story.append(
                Paragraph(safe_line, body_style)
            )

    document.build(story)

    pdf_bytes = buffer.getvalue()

    buffer.close()

    return pdf_bytes


# ============================================================
# 9. SESSION STATE INITIALIZATION
# ============================================================

if "generated_letter" not in st.session_state:
    st.session_state["generated_letter"] = ""

if "last_generated_style" not in st.session_state:
    st.session_state["last_generated_style"] = None

if "generated_results" not in st.session_state:
    st.session_state["generated_results"] = None

if "editable_letter" not in st.session_state:
    st.session_state["editable_letter"] = ""


# ============================================================
# 10. APPLICATION INTERFACE
# ============================================================


st.markdown(
    '<div class="main-title">AI Cover Letter Generator</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Create tailored cover letters for your next opportunity.'
    '</div>',
    unsafe_allow_html=True
)

st.write(
    "Generate personalized cover letters, analyze job requirements, "
    "and download your letter as a PDF."
)

st.info(
    "This application uses rule-based text processing and writing "
    "templates. It does not require an external AI API."
)

st.divider()


# ============================================================
# 11. CANDIDATE INFORMATION
# ============================================================

st.markdown(
    '<div class="section-heading">1. Candidate Information</div>',
    unsafe_allow_html=True
)
st.markdown(
    '<div class="section-description">'
    'Enter your personal details and the role you are applying for.'
    '</div>',
    unsafe_allow_html=True
)

col1, col2 = st.columns(2)

with col1:

    name = st.text_input(
        "Full Name",
        key="candidate_name",
        placeholder="Enter your full name",
    )

    email = st.text_input(
    "Email Address",
    key="candidate_email",
    placeholder="name@example.com",
)

    email_valid, email_message = validate_email(email)

    if not email_valid:
         st.error(email_message)
    elif email_message:
         st.warning(email_message)
    education = st.text_input(
        "Education",
        key="candidate_education",
        placeholder="B.E. in CSE/M.Tech in AI & DS/Your Degree",
    )

with col2:

    job_title = st.text_input(
        "Job Title",
        key="candidate_job_title",
        placeholder="Data Analyst/Software Engineer/Your Desired Role",
    )

    company = st.text_input(
        "Company Name",
        key="candidate_company",
        placeholder="Microsoft/Google/Your Company Name",
    )

    experience = st.selectbox(
        "Experience Level",
        [
            "Student / Fresher",
            "Internship Experience",
            "Experienced",
        ],
        key="candidate_experience",
    )



# ============================================================
# 12. SKILLS AND PROJECTS
# ============================================================

st.markdown(
    '<div class="section-heading">2. Skills and Projects</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-description">'
    'Highlight the skills you have and the projects you have completed.'
    '</div>',
    unsafe_allow_html=True
)

col1, col2 = st.columns(2)

with col1:
    skills = st.text_area(
        "Technical Skills",
        key="candidate_skills",
        placeholder="Python, SQL, Pandas, Machine Learning",
        height=150,
        help="Separate your skills with commas."
    )

with col2:
    projects = st.text_area(
        "Academic Projects",
        key="candidate_projects",
        placeholder=(
            "Smart Learning Recommendation System\n"
            "Solar Power Generation Prediction\n"
            "AI Cover Letter Generator"
        ),
        height=150,
        help="Enter each project on a separate line."
    )



# ============================================================
# 13. JOB DESCRIPTION
# ============================================================

st.markdown(
    '<div class="section-heading">3. Job Description</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-description">'
    'Paste the job requirements to identify skills that match your profile.'
    '</div>',
    unsafe_allow_html=True
)

job_description = st.text_area(
    "Paste the Job Description",
    key="job_description",
    height=200,
    placeholder=(
        "Paste the job responsibilities, required skills, "
        "qualifications, and other requirements here."
    ),
    help="Include the job requirements for a more useful skill analysis."
)


# ============================================================
# 14. WRITING STYLE
# ============================================================


st.markdown(
    '<div class="section-heading">4. Writing Preferences</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-description">'
    'Choose the tone that best suits your job application.'
    '</div>',
    unsafe_allow_html=True
)


style = st.selectbox(
    "Choose a Writing Style",
    [
        "Professional",
        "Standard",
        "Creative",
    ],
    key="writing_style",
)

st.caption(
    "Change the writing style after generating a letter to "
    "automatically generate a new version using the same details."
)


# ============================================================
# 15. VALIDATE EMAIL AND GENERATE LETTER
# ============================================================

email_valid, email_message = validate_email(email)

if not email_valid:

    st.error(email_message)

elif email_message:

    st.warning(email_message)


generate_clicked = st.button(
    "Generate Cover Letter",
    type="primary",
    key="generate_button",
)


style_changed = (
    st.session_state["last_generated_style"] is not None
    and st.session_state["last_generated_style"] != style
    and bool(st.session_state["generated_letter"])
)

should_generate = generate_clicked or style_changed


if should_generate:

    if not all([
        name.strip(),
        job_title.strip(),
        company.strip(),
        skills.strip(),
        job_description.strip(),
    ]):

        st.warning(
            "Please enter your name, job title, company, "
            "technical skills, and job description."
        )

    elif not email_valid:

        st.error(
            "Please correct your email address before generating "
            "the cover letter."
        )

    else:

        (
            letter,
            required,
            matched,
            missing,
            quality_score,
            quality_checks,
        ) = generate_cover_letter(
            name=name,
            email=email,
            education=education,
            job_title=job_title,
            company=company,
            experience=experience,
            skills=skills,
            projects=projects,
            job_description=job_description,
            style=style,
        )

        # Save generated content and results.
        st.session_state["generated_letter"] = letter

        st.session_state["editable_letter"] = letter

        st.session_state["last_generated_style"] = style

        st.session_state["generated_results"] = {
            "required": required,
            "matched": matched,
            "missing": missing,
            "quality_score": quality_score,
            "quality_checks": quality_checks,
        }


# ============================================================
# 16. DISPLAY GENERATED LETTER
# ============================================================

if st.session_state["generated_letter"]:

    st.divider()

    st.markdown(
    '<div class="section-heading">5. Generated Cover Letter</div>',
    unsafe_allow_html=True
)

    st.markdown(
    '<div class="section-description">'
    'Review your generated letter, make any edits, and download it as a PDF.'
    '</div>',
    unsafe_allow_html=True
)

    st.caption(
        f"Current writing style: "
        f"{st.session_state['last_generated_style']}"
    )

    st.success(
        f"Your {st.session_state['last_generated_style']} "
        "cover letter is ready."
    )

    edited_letter = st.text_area(
    "Review and edit your cover letter",
    key="editable_letter",
    height=500,
    help="You can edit the generated text before downloading your PDF."
)

    # Update the stored letter after editing.
    st.session_state["generated_letter"] = edited_letter

    st.download_button(
        label="📄 Download Cover Letter as PDF",
        data=create_pdf(edited_letter),
        file_name="cover_letter.pdf",
        mime="application/pdf",
        key="download_cover_letter",
    )


# ============================================================
# 17. SKILL MATCHING RESULTS
# ============================================================

if (
    st.session_state["generated_letter"]
    and st.session_state["generated_results"] is not None
):

    results = st.session_state["generated_results"]

    required = results["required"]
    matched = results["matched"]
    missing = results["missing"]

    st.divider()

    st.markdown(
    '<div class="section-heading">6. Job Skill Analysis</div>',
    unsafe_allow_html=True
)

    st.markdown(
    '<div class="section-description">'
    'Compare your listed skills with the requirements in the job description.'
    '</div>',
    unsafe_allow_html=True
)

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Required Skills Found",
        len(required),
    )

    col2.metric(
        "Matching Skills",
        len(matched),
    )

    col3.metric(
        "Missing Skills",
        len(missing),
    )

    if required:

        match_percentage = (
            len(matched) / len(required)
        ) * 100

        st.subheader("Skill Match Percentage")

        st.progress(int(match_percentage))

        st.write(
            f"**{match_percentage:.1f}% match**"
        )

    else:

        st.info(
            "No recognized technical skills were found in the "
            "job description."
        )

    st.subheader("Matching Skills")

    if matched:

        st.success(
            ", ".join(
                SKILL_DISPLAY_NAMES.get(skill, skill)
                for skill in matched
            )
        )

    else:

        st.write("No matching skills identified.")

    st.subheader("Skills to Consider Developing")

    if missing:

        st.warning(
            ", ".join(
                SKILL_DISPLAY_NAMES.get(skill, skill)
                for skill in missing
            )
        )

    else:

        st.success(
            "All recognized skills in the job description "
            "match your listed skills."
        )

    st.caption(
        "The skill match percentage measures overlap between "
        "recognized skills. It does not predict hiring success."
    )


# ============================================================
# 18. INFORMATION COMPLETENESS
# ============================================================

if (
    st.session_state["generated_letter"]
    and st.session_state["generated_results"] is not None
):

    results = st.session_state["generated_results"]

    quality_score = results["quality_score"]

    quality_checks = results["quality_checks"]

    st.divider()

    
    st.markdown(
    '<div class="section-heading">7. Information Completeness</div>',
    unsafe_allow_html=True
)

    st.markdown(
    '<div class="section-description">'
    'Check whether you provided the key information needed for your cover letter.'
    '</div>',
    unsafe_allow_html=True
)


    st.metric(
        "Information Completeness",
        f"{quality_score:.0f}%",
    )

    st.progress(int(quality_score))

    for check, passed in quality_checks.items():

        if passed:

            st.write(f"✅ {check}")

        else:

            st.write(f"⚠️ {check}")

    st.caption(
        "This score measures the completeness of the supplied "
        "information. It does not assess writing quality or "
        "the likelihood of getting hired."
    )