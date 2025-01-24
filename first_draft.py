from openai import OpenAI
from pydantic import BaseModel
import os
import time
from tqdm import tqdm
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

@dataclass
class Config:
    """Configuration settings for the thesis generator."""
    API_KEY: str
    BASE_URL: str
    MODEL: str
    LOW_RATE_LIMITS: bool
    PROJECT_FILES_DIR: str
    TRANSLATION_LANG: Optional[str]

    @classmethod
    def from_env(cls) -> 'Config':
        """Create Config instance from environment variables."""
        load_dotenv()
        
        low_rate_limits = os.environ.get("LOW_RATE_LIMITS", "").lower()
        return cls(
            API_KEY=os.environ.get("API_KEY", ""),
            BASE_URL=os.environ.get("BASE_URL", ""),
            MODEL=os.environ.get("MODEL", ""),
            LOW_RATE_LIMITS=low_rate_limits in ("true", "1", "yes"),
            PROJECT_FILES_DIR=os.environ.get("PROJECT_FILES_DIR", ""),
            TRANSLATION_LANG=os.environ.get("TRANSLATION_LANG")
        )

    def validate(self) -> None:
        """Validates the configuration settings."""
        if not self.API_KEY:
            raise ValueError("API_KEY is required")
        if not self.BASE_URL:
            raise ValueError("BASE_URL is required")
        if not self.MODEL:
            raise ValueError("MODEL is required")
        if not os.path.isdir(self.PROJECT_FILES_DIR):
            raise ValueError(f"PROJECT_FILES_DIR '{self.PROJECT_FILES_DIR}' does not exist")
        if self.TRANSLATION_LANG and self.TRANSLATION_LANG not in ("RU", "UZ"):
            raise ValueError("TRANSLATION_LANG must be either 'RU' or 'UZ'")

config = Config.from_env()
config.validate()

TOTAL_STEPS = 14
if config.TRANSLATION_LANG:
    TOTAL_STEPS += 13

pbar = tqdm(total=TOTAL_STEPS, desc="Starting thesis generation", 
            bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]')

def update_progress(desc):
    """Update progress bar with description and increment"""
    pbar.set_description(desc)
    pbar.update(1)


# ---------------------------------
class Part1(BaseModel):
    part_1_title: str
    general_analysis_1_1: str
    principles_1_2: str
    problem_statement_1_3: str

class Part2(BaseModel):
    part_2_title: str
    design_creation_2_1: str
    sequence_development_2_2: str
    instructions_2_3: str

class ThesisPlan(BaseModel):
    part1: Part1
    part2: Part2
# ---------------------------------

def read_files(filepaths):
    """Reads the content of multiple files."""
    file_contents = {}
    
    for filepath in filepaths:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                file_contents[filepath] = f.read()
        except Exception as e:
            print(f"Error reading file {filepath}: {str(e)}")
    return file_contents

CLIENT = OpenAI(
    api_key=config.API_KEY,
    base_url=config.BASE_URL
)

def get_chat_completion(system_message, user_message, max_retries=3, base_delay=5):
    """Generates a chat completion with retry logic for handling temporary API failures.
    
    Args:
        system_message: The system message for the chat
        user_message: The user message for the chat
        max_retries: Maximum number of retry attempts (default: 3)
        base_delay: Base delay between retries in seconds (default: 5)
    
    Returns:
        The chat completion content
        
    Raises:
        Exception: If all retry attempts fail
    """
    if config.LOW_RATE_LIMITS:
        time.sleep(10)

    for attempt in range(max_retries):
        try:
            response = CLIENT.chat.completions.create(
                model=config.MODEL,
                n=1,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ]
            )
            return response.choices[0].message.content
            
        except Exception as e:
            if attempt == max_retries - 1:  # Last attempt
                raise Exception(f"Failed after {max_retries} attempts. Last error: {str(e)}")
            
            # Calculate exponential backoff delay
            delay = base_delay * (2 ** attempt)  # 5, 10, 20 seconds
            print(f"Attempt {attempt + 1} failed. Retrying in {delay} seconds... Error: {str(e)}")
            time.sleep(delay)

update_progress("Reading source code files")
folder_path = config.PROJECT_FILES_DIR
filepaths = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
file_contents = read_files(filepaths)

source_code_content = ""
for filepath, content in file_contents.items():
    source_code_content += f"--- {filepath} ---\n{content}\n"

update_progress("Analyzing software features")
software_features_sys_msg = (
    "You are a technical documentation expert analyzing software applications. "
    "Analyze the provided source code and create a detailed technical description that covers:\n"
    "1. Core functionalities and features\n"
    "2. System architecture and key components\n"
    "3. Data flows and processing logic\n"
    "4. User interaction patterns\n"
    "5. Integration points and external dependencies\n\n"
    "Focus on technical accuracy and provide specific examples from the code where relevant. "
    "The description should be suitable for an academic thesis."
)

SOFTWARE_FEATURES_TEXT = get_chat_completion(software_features_sys_msg, source_code_content)

update_progress("Generating thesis plan structure")
thesis_plan_sys_msg = """You are an academic advisor helping structure a bachelor's thesis about software development.

The thesis must follow this structure, replacing the placeholders in <angle brackets> with specific content based on the software description provided:

# INTRODUCTION
[Standard introduction sections remain unchanged]

# PART I: SYSTEMATIC ANALYSIS OF <software domain/category>
1.1-§. Analysis of existing <specific type of software solutions>
1.2-§. Core principles of <key technologies/frameworks used>
1.3-§. Problem statement and requirements analysis

# PART II: DEVELOPMENT OF <specific software solution name/type>
2.1-§. System architecture and technical design
2.2-§. Implementation methodology and development process
2.3-§. Deployment and usage documentation

[Remaining sections unchanged]

Based on the software features description provided, suggest appropriate specific terms for the placeholders while maintaining academic rigor and technical precision. Format the response as a ThesisPlan object."""

time.sleep(10)

thesis_plan_response = CLIENT.beta.chat.completions.parse(
    model=config.MODEL,
    n=1,
    messages=[
        {"role": "system", "content": thesis_plan_sys_msg},
        {"role": "user", "content": SOFTWARE_FEATURES_TEXT}
    ],
    response_format=ThesisPlan
)

PART_1_TITLE = thesis_plan_response.choices[0].message.parsed.part1.part_1_title
GENERAL_ANALYSIS_1_1 = thesis_plan_response.choices[0].message.parsed.part1.general_analysis_1_1
PRINCIPLES_1_2 = thesis_plan_response.choices[0].message.parsed.part1.principles_1_2
PROBLEM_STATEMENT_1_3 = thesis_plan_response.choices[0].message.parsed.part1.problem_statement_1_3

PART_2_TITLE = thesis_plan_response.choices[0].message.parsed.part2.part_2_title
DESIGN_CREATION_2_1 = thesis_plan_response.choices[0].message.parsed.part2.design_creation_2_1
SEQUENCE_DEVELOPMENT_2_2 = thesis_plan_response.choices[0].message.parsed.part2.sequence_development_2_2
INSTRUCTIONS_2_3 = thesis_plan_response.choices[0].message.parsed.part2.instructions_2_3


THESIS_PLAN = """INTRODUCTION
Relevance of the graduation thesis
The purpose of this graduation thesis
The object of the graduation thesis
The subject of the graduation thesis

PART I: {}
1.1-§. {}
1.2-§. {}
1.3-§. {}

PART II: {}
2.1-§. {}
2.2-§. {}
2.3-§. {}

CONCLUSION  
  
LIST OF USED LITERATURE
  
APPENDIX
""".format(PART_1_TITLE, 
           GENERAL_ANALYSIS_1_1, 
           PRINCIPLES_1_2, 
           PROBLEM_STATEMENT_1_3, 
           PART_2_TITLE, 
           DESIGN_CREATION_2_1, 
           SEQUENCE_DEVELOPMENT_2_2, 
           INSTRUCTIONS_2_3)

update_progress("Generating section 2.3-§")

sys_msg_3 = """You are a technical documentation specialist writing deployment and usage documentation for an academic thesis.

Using the provided software features description, create comprehensive documentation that covers:
1. System requirements and prerequisites
2. Installation and configuration steps
3. Detailed usage instructions with examples
4. Common workflows and use cases
5. Troubleshooting guidelines
6. Best practices and recommendations

Write in a formal academic style, focusing on clarity and technical accuracy. Include specific details from the software implementation where relevant.
Minimum length: 1000 words."""

PART_2_3_TEXT = get_chat_completion(sys_msg_3, SOFTWARE_FEATURES_TEXT)

THESIS_MAIN_TEXT = """INTRODUCTION
Relevance of the graduation thesis
The purpose of this graduation thesis
The object of the graduation thesis
The subject of the graduation thesis

PART I: {}
1.1-§. {}
1.2-§. {}
1.3-§. {}

PART II: {}
2.1-§. {}
2.2-§. {}

2.3-§. {}

CONCLUSION  
  
LIST OF USED LITERATURE  
  
APPENDIX
""".format(
    PART_1_TITLE, 
    GENERAL_ANALYSIS_1_1, 
    PRINCIPLES_1_2, 
    PROBLEM_STATEMENT_1_3, 
    PART_2_TITLE, 
    DESIGN_CREATION_2_1, 
    SEQUENCE_DEVELOPMENT_2_2, 
    PART_2_3_TEXT)

update_progress("Generating section 2.2-§")

sys_msg_4 = """You are a software development methodologist documenting the implementation process for an academic thesis.

Analyze the provided source code and describe the development process, including:
1. Development methodology and approach
2. Key implementation decisions and their rationale
3. Critical code components and their interactions
4. Technical challenges and solutions
5. Testing and validation procedures

Include relevant code snippets to illustrate important concepts. Write in formal academic style."""

PART_2_2_TEXT = get_chat_completion(sys_msg_4, source_code_content)

THESIS_MAIN_TEXT = """INTRODUCTION
Relevance of the graduation thesis
The purpose of this graduation thesis
The object of the graduation thesis
The subject of the graduation thesis

PART I: {}
1.1-§. {}
1.2-§. {}
1.3-§. {}

PART II: {}
2.1-§. {}

2.2-§. {}

2.3-§. {}

CONCLUSION  
  
LIST OF USED LITERATURE  
  
APPENDIX
""".format(
    PART_1_TITLE, 
    GENERAL_ANALYSIS_1_1, 
    PRINCIPLES_1_2, 
    PROBLEM_STATEMENT_1_3, 
    PART_2_TITLE, 
    DESIGN_CREATION_2_1, 
    PART_2_2_TEXT.replace('2.2-§.', '', 1), 
    PART_2_3_TEXT.replace('2.3-§.', '', 1))

update_progress("Generating section 2.1-§")

sys_msg_5 = """You are a software architecture expert assisting with a bachelor's thesis. Your task is to write a detailed technical design section that follows academic standards.

Context:
- This is for section 2.1-§ focusing on system architecture and technical design
- The content should align with the following thesis structure:
---
{}
---

Requirements for PART II: {}
Section 2.1-§. {}

Please provide:
1. High-level system architecture overview
2. Detailed component design and interactions
3. Key design patterns and architectural decisions
4. Data structures and flow diagrams
5. Security considerations and implementation
6. Scalability and performance design choices

Guidelines:
- Include relevant UML diagrams or architectural schemas
- Reference specific code implementations to support design choices
- Maintain formal academic language and technical precision
- Cite industry best practices where applicable
- Include code snippets to illustrate key architectural components
- Length should be approximately 2000-2500 words

Format the response as a cohesive academic section without any introductory or concluding meta-commentary.""".format(THESIS_MAIN_TEXT, PART_2_TITLE, DESIGN_CREATION_2_1)

PART_2_1_TEXT = get_chat_completion(sys_msg_5, source_code_content)

THESIS_MAIN_TEXT = """INTRODUCTION
Relevance of the graduation thesis
The purpose of this graduation thesis
The object of the graduation thesis
The subject of the graduation thesis

PART I: {}
1.1-§. {}
1.2-§. {}
1.3-§. {}

PART II: {}
2.1-§. {}

2.2-§. {}

2.3-§. {}

CONCLUSION  
  
LIST OF USED LITERATURE  
  
APPENDIX
""".format(
    PART_1_TITLE, 
    GENERAL_ANALYSIS_1_1, 
    PRINCIPLES_1_2, 
    PROBLEM_STATEMENT_1_3, 
    PART_2_TITLE, 
    PART_2_1_TEXT.replace('2.1-§.', '', 1), 
    PART_2_2_TEXT.replace('2.2-§.', '', 1), 
    PART_2_3_TEXT.replace('2.3-§.', '', 1))

update_progress("Generating section 1.1-§")

sys_msg_part_1 = """You are an academic writing expert specializing in computer science and software engineering theses. You are assisting an undergraduate student with their graduation thesis.

Your responsibilities:
1. Maintain formal academic writing standards
2. Use appropriate technical terminology
3. Ensure logical flow and coherent structure
4. Balance technical depth with clarity
5. Follow academic citation practices

Writing guidelines:
- Use clear, precise language suitable for academic audiences
- Support technical claims with evidence or references
- Maintain consistent terminology throughout
- Focus on analytical and critical discussion
- Avoid colloquial language and informal expressions
- Structure content with clear paragraphs and transitions

Remember that this is an undergraduate thesis in software engineering, requiring both technical accuracy and academic rigor."""


user_msg_part_1_1 = """Context:
Current thesis draft:
{0}

Task:
Generate a 2000-word analysis section for:
PART I: {1}
Section 1.1-§. {2}

Requirements:
1. Begin directly with the section title "{2}"
2. Provide comprehensive analysis of existing solutions in the field
3. Include critical evaluation of current approaches
4. Compare and contrast different methodologies
5. Reference relevant academic literature and industry standards
6. Discuss technological trends and their implications

Structure guidelines:
- Organize content into clear subsections
- Use topic sentences to guide reader through analysis
- Include specific examples and case studies
- Build logical progression of ideas
- Maintain consistent technical depth throughout
- Connect analysis to thesis objectives

Format:
- Academic writing style
- Technical precision in terminology
- 2000 words (±5%)
- No meta-commentary or introductory remarks
- Direct integration with overall thesis structure

Begin with section title and proceed directly with content.""".format(THESIS_MAIN_TEXT, PART_1_TITLE, GENERAL_ANALYSIS_1_1)

PART_1_1_TEXT = get_chat_completion(sys_msg_part_1, user_msg_part_1_1)

THESIS_MAIN_TEXT = """INTRODUCTION
Relevance of the graduation thesis
The purpose of this graduation thesis
The object of the graduation thesis
The subject of the graduation thesis

PART I: {}

1.1-§. {}

1.2-§. {}

1.3-§. {}

PART II: {}

2.1-§. {}

2.2-§. {}

2.3-§. {}

CONCLUSION  
  
LIST OF USED LITERATURE  
  
APPENDIX
""".format(
    PART_1_TITLE, 
    PART_1_1_TEXT, 
    PRINCIPLES_1_2, 
    PROBLEM_STATEMENT_1_3, 
    PART_2_TITLE, 
    PART_2_1_TEXT, 
    PART_2_2_TEXT, 
    PART_2_3_TEXT)

update_progress("Generating section 1.2-§")

user_msg_part_1_2 = """Context:
Current thesis draft:
{0}

Task:
Generate section 1.2-§ for:
PART I: {1}
Title: {2}

Requirements:
1. Length: 1500 words (±5%)
2. Focus on core principles and theoretical foundations
3. Analyze key technologies and frameworks
4. Explain technical concepts with academic rigor
5. Include relevant examples and implementations
6. Connect principles to practical applications

Structure:
- Begin with section title "{2}"
- Organize content into clear subsections
- Use appropriate technical terminology
- Include citations to academic sources
- Progress from fundamental concepts to advanced applications
- Maintain consistent technical depth throughout

Format guidelines:
- Academic writing style
- Clear paragraph transitions
- Technical precision in terminology
- Direct integration with overall thesis structure
- No meta-commentary or introductory remarks
- Citations for technical standards and methodologies

Ensure content aligns with previous section 1.1 and sets up for section 1.3.""".format(THESIS_MAIN_TEXT, PART_1_TITLE, PRINCIPLES_1_2)

PART_1_2_TEXT = get_chat_completion(sys_msg_part_1, user_msg_part_1_2)

THESIS_MAIN_TEXT = """INTRODUCTION
Relevance of the graduation thesis
The purpose of this graduation thesis
The object of the graduation thesis
The subject of the graduation thesis

PART I: {}

1.1-§. {}

1.2-§. {}

1.3-§. {}

PART II: {}

2.1-§. {}

2.2-§. {}

2.3-§. {}

CONCLUSION  
  
LIST OF USED LITERATURE  
  
APPENDIX
""".format(
    PART_1_TITLE, 
    PART_1_1_TEXT, 
    PART_1_2_TEXT, 
    PROBLEM_STATEMENT_1_3, 
    PART_2_TITLE, 
    PART_2_1_TEXT, 
    PART_2_2_TEXT, 
    PART_2_3_TEXT)
update_progress("Generating section 1.3-§")

user_msg_part_1_3 = """here is my draft:
{0}
---
Generate content for section 1.3-§ (Problem Statement and Requirements Analysis):

Requirements:
1. Length: 300 words
2. Structure:
   - Clear problem definition
   - Specific technical requirements
   - Functional requirements
   - Non-functional requirements
   - Constraints and limitations
   - Success criteria

Guidelines:
- Use formal academic language
- Reference findings from sections 1.1 and 1.2
- Include measurable criteria where possible
- Connect requirements to project objectives
- Justify each requirement with technical rationale

Format:
- Start with section title: "1.3-§. {2}"
- Organize into clear subsections
- Use precise technical terminology
- Maintain academic writing style

Note: Generate only the section content without any meta-commentary or introductory remarks.
""".format(THESIS_MAIN_TEXT, PART_1_TITLE, PROBLEM_STATEMENT_1_3)

PART_1_3_TEXT = get_chat_completion(sys_msg_part_1, user_msg_part_1_3)

THESIS_MAIN_TEXT = """INTRODUCTION
Relevance of the graduation thesis
The purpose of this graduation thesis
The object of the graduation thesis
The subject of the graduation thesis

PART I: {}

1.1-§. {}

1.2-§. {}

1.3-§. {}

PART II: {}

2.1-§. {}

2.2-§. {}

2.3-§. {}

CONCLUSION  
  
LIST OF USED LITERATURE  
  
APPENDIX
""".format(
    PART_1_TITLE, 
    PART_1_1_TEXT, 
    PART_1_2_TEXT, 
    PART_1_3_TEXT, 
    PART_2_TITLE, 
    PART_2_1_TEXT, 
    PART_2_2_TEXT, 
    PART_2_3_TEXT)

update_progress("Generating introduction section")

sys_msg_intro = """You are an academic writing expert specializing in computer science and software engineering theses. You are assisting an undergraduate student with their graduation thesis.

Your responsibilities:
1. Maintain formal academic writing standards
2. Use appropriate technical terminology
3. Ensure logical flow and coherent structure
4. Balance technical depth with clarity
5. Follow academic citation practices

Writing guidelines:
- Use clear, precise language suitable for academic audiences
- Support technical claims with evidence or references
- Maintain consistent terminology throughout
- Focus on analytical and critical discussion
- Avoid colloquial language and informal expressions
- Structure content with clear paragraphs and transitions

Remember that this is an undergraduate thesis in software engineering, requiring both technical accuracy and academic rigor."""


user_msg_part_intro = """here is my draft:
{0}
---
Generate the INTRODUCTION section with the following components:

1. Relevance of the graduation thesis (130-150 words)
   - Current state of the field
   - Industry significance
   - Technical challenges addressed
   - Innovation potential

2. The purpose of this graduation thesis (170-190 words)
   - Primary objectives
   - Research questions
   - Expected contributions
   - Scope of investigation

3. The object of the graduation thesis (15-20 words)
   - Clear identification of the research focus
   - Specific system or technology being studied

4. The subject of the graduation thesis (110-120 words)
   - Specific aspects being investigated
   - Technical parameters
   - Methodological approach
   - Research boundaries

Requirements:
- Maintain consistent technical terminology
- Connect each section logically
- Reference current industry trends
- Align with thesis scope and objectives
- Use formal academic language
- Include relevant citations where appropriate

Format:
- Present each section with its heading
- Adhere strictly to word limits
- Use clear paragraph structure
- Avoid meta-commentary or explanatory notes
""".format(THESIS_MAIN_TEXT)

PART_INTRO = get_chat_completion(sys_msg_intro, user_msg_part_intro)

THESIS_MAIN_TEXT = """
{}

PART I: {}

1.1-§. {}

1.2-§. {}

1.3-§. {}

PART II: {}

2.1-§. {}

2.2-§. {}

2.3-§. {}

CONCLUSION  
  
LIST OF USED LITERATURE  
  
APPENDIX
""".format(
    PART_INTRO,
    PART_1_TITLE, 
    PART_1_1_TEXT, 
    PART_1_2_TEXT, 
    PART_1_3_TEXT, 
    PART_2_TITLE, 
    PART_2_1_TEXT, 
    PART_2_2_TEXT, 
    PART_2_3_TEXT)

update_progress("Generating conclusion section")

user_msg_part_conclusion = """here is my draft:
{0}
---
Generate the CONCLUSION section for this graduation thesis.

Requirements:
1. Length: 250-300 words
2. Structure:
   - Summary of key findings and achievements
   - Evaluation of objectives met
   - Technical contributions and innovations
   - Practical implications and applications
   - Limitations and challenges encountered
   - Future research directions and recommendations

Content guidelines:
- Connect conclusions to objectives stated in introduction
- Reference specific outcomes from Parts I and II
- Highlight technical significance of results
- Provide evidence-based conclusions
- Balance theoretical and practical implications
- Maintain academic tone and terminology

Format:
- Single cohesive section without subheadings
- Clear paragraph transitions
- Logical progression of ideas
- No new information or citations
- No meta-commentary or introductory remarks

Note: Focus on synthesizing the thesis content rather than introducing new concepts.
""".format(THESIS_MAIN_TEXT)

PART_CONCLUSION = get_chat_completion(sys_msg_intro, user_msg_part_conclusion)

THESIS_MAIN_TEXT = """
{}

PART I: {}

1.1-§. {}

1.2-§. {}

1.3-§. {}

PART II: {}

2.1-§. {}

2.2-§. {}

2.3-§. {}

{}
  
LIST OF USED LITERATURE  
  
APPENDIX
""".format(
    PART_INTRO,
    PART_1_TITLE, 
    PART_1_1_TEXT, 
    PART_1_2_TEXT, 
    PART_1_3_TEXT, 
    PART_2_TITLE, 
    PART_2_1_TEXT, 
    PART_2_2_TEXT, 
    PART_2_3_TEXT,
    PART_CONCLUSION)

update_progress("Generating list of used literature")

user_msg_part_refs = """here is my draft:
{0}
---
Generate the LIST OF USED LITERATURE section following these requirements:

Format Requirements:
1. Use MLA 9th edition citation format
2. Number of references: 15-20 entries
3. Alphabetically ordered by author's last name

Source Types to Include:
- Academic journal articles (minimum 6)
- Technical books and textbooks (3-4)
- Conference proceedings (2-3)
- Industry standards and documentation (2-3)
- Recent technical reports or whitepapers (2-3)
- Relevant software documentation or specifications (1-2)

Selection Criteria:
- Published within the last 5-7 years (except for fundamental works)
- Directly relevant to thesis topics and technologies
- Include sources referenced in all major sections
- Mix of theoretical foundations and practical applications
- Prefer peer-reviewed sources
- Include at least 2-3 high-impact publications

Format each entry according to MLA style:
Author(s). "Title." Journal/Source, vol. X, no. Y, Year, pp. XX-XX.

Note: Generate only real, verifiable academic and technical sources that exist in the real world.
""".format(THESIS_MAIN_TEXT)

PART_REFS = get_chat_completion(sys_msg_intro, user_msg_part_refs)

THESIS_MAIN_TEXT = """
-------------------------------- INTRODUCTION --------------------------------

{}

-------------------------------- PART I, 1.1-§ -------------------------------

PART I: {}

1.1-§. {}

-------------------------------- 1.2-§ -------------------------------

1.2-§. {}

-------------------------------- 1.3-§ -------------------------------

1.3-§. {}

-------------------------------- PART II, 2.1-§ -----------------------

PART II: {}

2.1-§. {}

-------------------------------- 2.2-§ -------------------------------

2.2-§. {}

-------------------------------- 2.3-§ -------------------------------

2.3-§. {}

-------------------------------- CONCLUSION -------------------------------

{}

-------------------------------- REFERENCES -------------------------------
  
{} 
  
APPENDIX
""".format(
    PART_INTRO,
    PART_1_TITLE, 
    PART_1_1_TEXT, 
    PART_1_2_TEXT, 
    PART_1_3_TEXT, 
    PART_2_TITLE, 
    PART_2_1_TEXT, 
    PART_2_2_TEXT, 
    PART_2_3_TEXT,
    PART_CONCLUSION,
    PART_REFS)

update_progress("Saving generated files")

# Create directories if they don't exist
os.makedirs("draft/EN", exist_ok=True)

with open("draft/EN/THESIS_PLAN_EN.txt", "w", encoding="utf-8") as f:
    f.write(THESIS_PLAN)

with open("draft/EN/THESIS_MAIN_TEXT_EN.txt", "w", encoding="utf-8") as f:
    f.write(THESIS_MAIN_TEXT)

update_progress("Generation complete!")

# Close progress bar if no translation is needed
if not config.TRANSLATION_LANG:
    pbar.close()
    exit()

# Translation code continues below...
translation_lang = config.TRANSLATION_LANG
target_language = "Uzbek (latin)" if translation_lang == "UZ" else "Russian" if translation_lang == "RU" else "Unknown"

# Define section headers based on translation language
section_header = "QISM" if translation_lang == "UZ" else "ЧАСТЬ" if translation_lang == "RU" else "PART"

sys_msg_translate = """You are a professional translator specializing in academic texts. 
I will provide you with a section of my graduation thesis written in English. 
Your task is to translate it into {}, maintaining a formal and academic tone throughout. 
Please provide the translation as plain text only, 
without any markdown formatting or additional commentary.""".format(target_language)

update_progress(f"Translating introduction to {target_language}")
PART_INTRO_translated = get_chat_completion(sys_msg_translate, PART_INTRO)

update_progress(f"Translating Part I (Title & Section 1.1)")
PART_1_TITLE_translated = get_chat_completion(sys_msg_translate, PART_1_TITLE)

update_progress(f"Translating section 1.1-§ to {target_language}")
PART_1_1_TEXT_translated = get_chat_completion(sys_msg_translate, PART_1_1_TEXT)

update_progress(f"Translating section 1.2-§ to {target_language}")
PART_1_2_TEXT_translated = get_chat_completion(sys_msg_translate, PART_1_2_TEXT)

update_progress(f"Translating section 1.3-§ to {target_language}")
PART_1_3_TEXT_translated = get_chat_completion(sys_msg_translate, PART_1_3_TEXT)

update_progress(f"Translating PART II title to {target_language}")
PART_2_TITLE_translated = get_chat_completion(sys_msg_translate, PART_2_TITLE)

update_progress(f"Translating section 2.1-§ to {target_language}")
PART_2_1_TEXT_translated = get_chat_completion(sys_msg_translate, PART_2_1_TEXT)

update_progress(f"Translating section 2.2-§ to {target_language}")
PART_2_2_TEXT_translated = get_chat_completion(sys_msg_translate, PART_2_2_TEXT)

update_progress(f"Translating section 2.3-§ to {target_language}")
PART_2_3_TEXT_translated = get_chat_completion(sys_msg_translate, PART_2_3_TEXT)

update_progress(f"Translating conclusion to {target_language}")
PART_CONCLUSION_translated = get_chat_completion(sys_msg_translate, PART_CONCLUSION)

update_progress(f"Translating thesis plan to {target_language}")
THESIS_PLAN_translated = get_chat_completion(sys_msg_translate, THESIS_PLAN)

THESIS_MAIN_TEXT_TRANSLATED = """
{}

----------------------------------------------------------------

{} I: {}

1.1-§. {}

----------------------------------------------------------------

1.2-§. {}

----------------------------------------------------------------

1.3-§. {}

----------------------------------------------------------------

{} II: {}

2.1-§. {}

----------------------------------------------------------------

2.2-§. {}

----------------------------------------------------------------

2.3-§. {}

----------------------------------------------------------------

{}

----------------------------------------------------------------

{} 

----------------------------------------------------------------

{}
""".format(
    PART_INTRO_translated,
    section_header, PART_1_TITLE_translated, 
    PART_1_1_TEXT_translated, 
    PART_1_2_TEXT_translated, 
    PART_1_3_TEXT_translated, 
    section_header, PART_2_TITLE_translated, 
    PART_2_1_TEXT_translated, 
    PART_2_2_TEXT_translated, 
    PART_2_3_TEXT_translated,
    PART_CONCLUSION_translated,
    PART_REFS,
    "ILOVA" if translation_lang == "UZ" else "ПРИЛОЖЕНИЕ" if translation_lang == "RU" else "APPENDIX"
)

# ----------------------------------------------------------------------------

update_progress("Saving translated files")

os.makedirs(f"draft/{translation_lang}", exist_ok=True)

with open(f"draft/{translation_lang}/THESIS_PLAN_{translation_lang}.txt", "w", encoding="utf-8") as f:
    f.write(THESIS_PLAN_translated)

with open(f"draft/{translation_lang}/THESIS_MAIN_TEXT_{translation_lang}.txt", "w", encoding="utf-8") as f:
    f.write(THESIS_MAIN_TEXT_TRANSLATED)

update_progress("Generation complete!")
pbar.close()