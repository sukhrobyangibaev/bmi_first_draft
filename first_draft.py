from openai import OpenAI
from pydantic import BaseModel
import os
import time
from tqdm import tqdm
from dotenv import load_dotenv

pbar = tqdm(total=25, desc="Processing")

load_dotenv()

class Config:
    def __init__(self):
        self.API_KEY = os.environ.get("API_KEY")
        self.BASE_URL = os.environ.get("BASE_URL")
        self.MODEL = os.environ.get("MODEL")
        self.LOW_RATE_LIMITS = os.environ.get("LOW_RATE_LIMITS") == "true"
        self.PROJECT_FILES_DIR = os.environ.get("PROJECT_FILES_DIR")
        self.TRANSLATION_LANG = os.environ.get("TRANSLATION_LANG")

config = Config()
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

def get_chat_completion(system_message, user_message):
    """Generates a chat completion. Raises an exception if the API call fails."""
    if config.LOW_RATE_LIMITS:
        time.sleep(10)

    response = CLIENT.chat.completions.create(
        model=config.MODEL,
        n=1,
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]
    )
    return response.choices[0].message.content

pbar.update(1)
# --------------------------------------
pbar.set_description('Reading source code content')

folder_path = config.PROJECT_FILES_DIR
filepaths = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
file_contents = read_files(filepaths)

source_code_content = ""
for filepath, content in file_contents.items():
    source_code_content += f"--- {filepath} ---\n{content}\n"

pbar.update(1)
# ----------------------------------------------------------------------------
pbar.set_description('Generating software features description')

software_features_sys_msg = (
    "I am writing a dissertation chapter that requires a detailed explanation of a software application I created. " 
    "Please outline all the application's features, functionalities, user interaction flows, and overall capabilities "
    "based on source code. The description should be comprehensive and suitable for an academic context."
    )

SOFTWARE_FEATURES_TEXT = get_chat_completion(software_features_sys_msg, source_code_content)

pbar.update(1)
# ----------------------------------------------------------------------------
pbar.set_description('Generating thesis plan outline')

thesis_plan_sys_msg = """
I am an undergraduate student working on my bachelor's thesis. I have developed a preliminary plan for my project, which is outlined below. This plan's structure must remain intact; only modifications within the square brackets [] are permissible:

# INTRODUCTION  
Relevance of the graduation thesis: Briefly explain the importance and timeliness of your chosen topic within the broader field of study. Why is this research necessary or valuable?  
The purpose of this graduation thesis: Clearly state the main goal you aim to achieve with your research. What specific outcome do you hope to produce or demonstrate?  
The object of the graduation thesis: Define the broader entity or area that your research will focus on. This is the general domain you are investigating.  
The subject of the graduation thesis: Define the specific aspect, property, or relationship within the object that you will be directly studying. This is the specific focus of your investigation.  
  
# PART I: SYSTEMATIC ANALYSIS OF [OBJECT OF STUDY]  
  
1.1-§. General analysis of existing [relevant category/examples related to your object of study]: Analyze the current state of the field, existing methodologies, technologies, or theories relevant to your object of study.  
1.2-§. Principles of [relevant methodology/technology/theory related to your subject of study]: Describe the fundamental concepts, principles, or workings of the key methods, technologies, or theories you will be utilizing or investigating. 1.3-§. Problem statement: Clearly identify the gap in knowledge, challenge, or problem that your thesis aims to address. This should logically flow from the analysis in the previous sections.  
  
# PART II. DEVELOPMENT OF A [TYPE OF SOLUTION/ANALYSIS/MODEL] FOR [SPECIFIC APPLICATION/TASK WITHIN THE OBJECT OF STUDY]  
  
2.1-§. Design and creation of the [foundation/structure/methodology] of the [solution/analysis/model]: Describe the planning and foundational steps involved in creating your solution, analysis, or model. This could involve database design, theoretical framework, experimental setup, etc.  
2.2-§. Sequence of developing a [solution/analysis/model] for conducting [specific task/process]: Detail the steps and stages involved in the actual development, implementation, or execution of your solution, analysis, or model.  
2.3-§. Instructions for using/applying the [solution/analysis/model]: Provide guidance on how to utilize, interpret, or apply the results of your work. 

# CONCLUSION
  
# LIST OF USED LITERATURE
  
# APPENDIX

---
I will provide you with a detailed description of my project's features and functionality. Based on this information, please help me modify thesis plan by suggesting appropriate headings within the square brackets.
Do not include the square brackets in the response.
"""

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

pbar.update(1)
# ----------------------------------------------------------------------------
pbar.set_description('Generating section 2.3-§')

sys_msg_3 = """You are helping me to write graduation thesis.
I am an undergraduate student writing my graduation thesis. I need to adhere to the following plan:
---
{}
---
Write the following section: 
PART II: {}
2.3-§. {}

I will provide you with the features of my software.
Respond in plain text only, without using any markdown formatting.
Do not include any introductory or concluding remarks.
Focus solely on generating the content for the specified section.
The response should be at least 1000 words long.
""".format(THESIS_PLAN, PART_2_TITLE, INSTRUCTIONS_2_3)

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

pbar.update(1)
# ----------------------------------------------------------------------------
pbar.set_description('Generating section 2.2-§')

sys_msg_4 = """You are helping me to write graduation thesis.
I am an undergraduate student writing my graduation thesis. I need to adhere to the following plan:
---
{}
---
Write the following section: 
PART II: {}
2.2-§. {}

I will provide you with the source code of my software.
Respond in plain text only, without using any markdown formatting.
Do not include any introductory or concluding remarks.
Focus solely on generating the content for the specified section.
you can include code snippets.
""".format(THESIS_MAIN_TEXT, PART_2_TITLE, SEQUENCE_DEVELOPMENT_2_2)

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

pbar.update(1)
# ----------------------------------------------------------------------------
pbar.set_description('Generating section 2.1-§')

sys_msg_5 = """You are helping me to write graduation thesis.
I am an undergraduate student writing my graduation thesis. I need to adhere to the following plan:
---
{}
---
Write the following section: 
PART II: {}
2.1-§. {}

I will provide you with the source code of my software.
Do not include any introductory or concluding remarks.
Focus solely on generating the content for the specified section.
you can include code snippets.
""".format(THESIS_MAIN_TEXT, PART_2_TITLE, DESIGN_CREATION_2_1)

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

pbar.update(1)
# ----------------------------------------------------------------------------
pbar.set_description('Generating section 1.1-§')

sys_msg_part_1 = """I am an undergraduate student writing my graduation thesis.
You are helping me to write this graduation thesis."""


user_msg_part_1_1 = """here is my draft:
{0}
---
write 2000 words for the following section: 
PART I: {1}
1.1-§. {2}

Do not include any introductory or concluding remarks like "Okay, here's the...".
Focus solely on generating the content for the specified section.
start with "{2}".
""".format(THESIS_MAIN_TEXT, PART_1_TITLE, GENERAL_ANALYSIS_1_1)

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

pbar.update(1)
# ----------------------------------------------------------------------------
pbar.set_description('Generating section 1.2-§')

user_msg_part_1_2 = """here is my draft:
{0}
---
write 1500 words for the following section: 
PART I: {1}
1.2-§. {2}

Do not include any introductory or concluding remarks like "Okay, here's the...".
Focus solely on generating the content for the specified section.
start with "{2}".
""".format(THESIS_MAIN_TEXT, PART_1_TITLE, PRINCIPLES_1_2)

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
pbar.update(1)
# ----------------------------------------------------------------------------
pbar.set_description('Generating section 1.3-§')

user_msg_part_1_3 = """here is my draft:
{0}
---
write 300 words for the following section: 
PART I: {1}
1.3-§. {2}

Do not include any introductory or concluding remarks like "Okay, here's the...".
Focus solely on generating the content for the specified section.
Start with title of section: 1.3-$...
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

pbar.update(1)
# ----------------------------------------------------------------------------
pbar.set_description('Generating introduction section')

sys_msg_intro = """I am an undergraduate student writing my graduation thesis.
You are helping me to write this graduation thesis."""


user_msg_part_intro = """here is my draft:
{0}
---
Write INTRODUCTION part of this graduation thesis.

Relevance of the graduation thesis
130-150 words 

The purpose of this graduation thesis  
170-190 words 

The object of the graduation thesis  
15-20 words  

The subject of the graduation thesis  
110-120 words  

Do not include any introductory or concluding remarks like "Okay, here's the...".
Focus solely on generating the content for the specified section.
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

pbar.update(1)
# ----------------------------------------------------------------------------
pbar.set_description('Generating conclusion section')

user_msg_part_conclusion = """here is my draft:
{0}
---
Write CONCLUSION for this graduation thesis.
250-300 words 

Do not include any introductory or concluding remarks like "Okay, here's the...".
Focus solely on generating the content for the specified section.
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

pbar.update(1)
# ----------------------------------------------------------------------------
pbar.set_description('Generating list of used literature')

user_msg_part_refs = """here is my draft:
{0}
---
write LIST OF USED LITERATURE for this graduation thesis in MLA format.
write real world 15-20 references.

Do not include any introductory or concluding remarks like "Okay, here's the...".
Focus solely on generating the content for the specified section.
""".format(THESIS_MAIN_TEXT)

PART_REFS = get_chat_completion(sys_msg_intro, user_msg_part_refs)

THESIS_MAIN_TEXT = """
INTRODUCTION

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

# ----------------------------------------------------------------------------

pbar.set_description('Saving EN files')

# Create directories if they don't exist
os.makedirs("draft/EN", exist_ok=True)

with open("draft/EN/THESIS_PLAN_EN.txt", "w", encoding="utf-8") as f:
    f.write(THESIS_PLAN)

with open("draft/EN/THESIS_MAIN_TEXT_EN.txt", "w", encoding="utf-8") as f:
    f.write(THESIS_MAIN_TEXT)

pbar.update(1)

# ----------------------------------------------------------------------------

translation_lang = config.TRANSLATION_LANG
target_language = "Uzbek" if translation_lang == "UZ" else "Russian" if translation_lang == "RU" else "Unknown"

sys_msg_translate_uz = """You are a professional translator specializing in academic texts. 
I will provide you with a section of my graduation thesis written in English. 
Your task is to translate it into {}, maintaining a formal and academic tone throughout. 
Please provide the translation as plain text only, 
without any markdown formatting or additional commentary.""".format(target_language)

pbar.set_description('Translating introduction to ' + target_language)
PART_INTRO_uz = get_chat_completion(sys_msg_translate_uz, PART_INTRO)
pbar.update(1)

pbar.set_description('Translating PART I title to ' + target_language)
PART_1_TITLE_uz = get_chat_completion(sys_msg_translate_uz, PART_1_TITLE)
pbar.update(1)

pbar.set_description('Translating section 1.1-§ to ' + target_language)
PART_1_1_TEXT_uz = get_chat_completion(sys_msg_translate_uz, PART_1_1_TEXT)
pbar.update(1)

pbar.set_description('Translating section 1.2-§ to ' + target_language)
PART_1_2_TEXT_uz = get_chat_completion(sys_msg_translate_uz, PART_1_2_TEXT)
pbar.update(1)

pbar.set_description('Translating section 1.3-§ to ' + target_language)
PART_1_3_TEXT_uz = get_chat_completion(sys_msg_translate_uz, PART_1_3_TEXT)
pbar.update(1)

pbar.set_description('Translating PART II title to ' + target_language)
PART_2_TITLE_uz = get_chat_completion(sys_msg_translate_uz, PART_2_TITLE)
pbar.update(1)

pbar.set_description('Translating section 2.1-§ to ' + target_language)
PART_2_1_TEXT_uz = get_chat_completion(sys_msg_translate_uz, PART_2_1_TEXT)
pbar.update(1)

pbar.set_description('Translating section 2.2-§ to ' + target_language)
PART_2_2_TEXT_uz = get_chat_completion(sys_msg_translate_uz, PART_2_2_TEXT)
pbar.update(1)

pbar.set_description('Translating section 2.3-§ to ' + target_language)
PART_2_3_TEXT_uz = get_chat_completion(sys_msg_translate_uz, PART_2_3_TEXT)
pbar.update(1)

pbar.set_description('Translating conclusion to ' + target_language)
PART_CONCLUSION_uz = get_chat_completion(sys_msg_translate_uz, PART_CONCLUSION)
pbar.update(1)

pbar.set_description('Translating thesis plan to ' + target_language)
THESIS_PLAN_uz = get_chat_completion(sys_msg_translate_uz, THESIS_PLAN)
pbar.update(1)

THESIS_MAIN_TEXT_UZ = """
{}

I QISM: {}

1.1-§. {}

1.2-§. {}

1.3-§. {}

II QISM: {}

2.1-§. {}

2.2-§. {}

2.3-§. {}

{}
  
{} 
  
ILOVA
""".format(
    PART_INTRO_uz,
    PART_1_TITLE_uz, 
    PART_1_1_TEXT_uz, 
    PART_1_2_TEXT_uz, 
    PART_1_3_TEXT_uz, 
    PART_2_TITLE_uz, 
    PART_2_1_TEXT_uz, 
    PART_2_2_TEXT_uz, 
    PART_2_3_TEXT_uz,
    PART_CONCLUSION_uz,
    PART_REFS)

# ----------------------------------------------------------------------------

pbar.set_description('Saving translated files')

os.makedirs(f"draft/{translation_lang}", exist_ok=True)

with open(f"draft/{translation_lang}/THESIS_PLAN_{translation_lang}.txt", "w", encoding="utf-8") as f:
    f.write(THESIS_PLAN_uz)

with open(f"draft/{translation_lang}/THESIS_MAIN_TEXT_{translation_lang}.txt", "w", encoding="utf-8") as f:
    f.write(THESIS_MAIN_TEXT_UZ)

pbar.update(1)
pbar.close()