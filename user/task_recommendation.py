import os
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain_openai import OpenAI

# Load environment variables from a .env file
load_dotenv('.env')

# Fetch the API key from the loaded environment variables
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    raise EnvironmentError("API key not found. Please set the OPENAI_API_KEY environment variable in the .env file.")

# Request template
request_template = """
Please review the following resumes:

{RESUMES}

Considering the task description below:

{TASK}

Identify the resume number and the name of the candidate that best matches the task requirements. If no suitable match is found, state that no suitable resume is available.

Response format:
1. Resume number: [number], Name: [name]
2. Additional comments or reasoning
"""

prompt = PromptTemplate(
    input_variables=["RESUMES", "TASK"],
    template=request_template,
)

llm = OpenAI(temperature=0.5, api_key=api_key)

def process_resumes_and_task(resumes, task):
    """
    Processes the given resumes and task to find the best match.

    Parameters:
    resumes (str): A string containing the resumes.
    task (str): A string containing the task description.

    Returns:
    str: The response from the OpenAI API.
    """
    return "YOU ARE DOING RIGHT"
    # try:
    #     formatted_prompt = prompt.format(RESUMES=resumes, TASK=task)
    #     response = llm.invoke(formatted_prompt)
    #     return response
    # except Exception as e:
    #     return f"An error occurred: {e}"



######################THE NEXT IS FOR TESING######################
# Example usage within the module
# resumes="""
# Resume 1: John Doe
# Title: Software Engineer
# Experience: 5 years
# Skills: 
# - Full-stack development
# - Python, JavaScript, SQL
# - Django, React, PostgreSQL
# Projects:
# - Developed and maintained a web application for a healthcare startup, improving patient data management.
# - Created an internal tool for automating report generation, reducing manual effort by 50%.
# Education:
# - BSc in Computer Science from University of California, Berkeley
# Certifications:
# - AWS Certified Solutions Architect
# - Certified Kubernetes Administrator (CKA)

# Resume 2: Jane Smith
# Title: Data Scientist
# Experience: 3 years
# Skills:
# - Data analysis, machine learning
# - Python, R, SQL
# - TensorFlow, scikit-learn, pandas
# Projects:
# - Developed a predictive model for customer churn, resulting in a 20% reduction in churn rate.
# - Conducted a data-driven market analysis that informed strategic decisions, increasing revenue by 15%.
# Education:
# - MSc in Data Science from Stanford University
# Certifications:
# - Google Professional Data Engineer
# - IBM Data Science Professional Certificate


# Resume 3: Emily Davis
# Title: Project Manager
# Experience: 7 years
# Skills:
# - Project management, team leadership
# - Jira, Trello, MS Project
# - Agile methodologies, Scrum
# Projects:
# - Managed a $1 million project to launch a new SaaS product, delivering on time and within budget.
# - Led a cross-functional team to develop a mobile application, resulting in 100,000 downloads within the first month.
# Education:
# - MBA in Business Management from Harvard Business School
# Certifications:
# - Project Management Professional (PMP)
# - Certified ScrumMaster (CSM)


# Resume 4: Michael Brown
# Title: Network Engineer
# Experience: 6 years
# Skills:
# - Network design, administration, security
# - Cisco, Juniper, network security protocols
# - Routers, switches, firewalls
# Projects:
# - Designed and implemented a secure network for a financial institution, ensuring compliance with industry standards.
# - Upgraded a company's network infrastructure, improving performance and reliability.
# Education:
# - BSc in Information Technology from MIT
# Certifications:
# - Cisco Certified Network Professional (CCNP)
# - Certified Information Systems Security Professional (CISSP)
# """


# task = """Develop a web application for an e-commerce platform. 
# - Requirements: Build the front-end and back-end using modern web technologies, set up a PostgreSQL database, and implement user authentication and payment processing."""
# result = process_resumes_and_task(resumes, task)
# print("The resume that can do this task is:")
# print(result)
