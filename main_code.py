import os
from pdf2image import convert_from_path
import pytesseract
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from rich.console import Console

console = Console()
os.environ["GOOGLE_API_KEY"] = "AIzaSyCCAgtfQEF0MEn7PtiHnOAyVpUSfEi65Tw"

# =======================
# Step 1: User Input
# =======================
console.print("[bold cyan]--- Cover Letter Generator ---[/bold cyan]\n")

resume_path = input("Enter path to your Resume PDF: ").strip()
jd_path = input("Enter path to the Job Description PDF: ").strip()
topic = input("Enter the Job Title (e.g. Mechanical Design Engineer): ").strip()

# =======================
# Step 2: OCR Function
# =======================
def ocr_pdf(path):
    """Extract text from a PDF file using OCR."""
    console.print(f"[yellow]Extracting text from {os.path.basename(path)}...[/yellow]")
    images = convert_from_path(path)
    text = ""
    for i, image in enumerate(images):
        page_text = pytesseract.image_to_string(image)
        text += page_text + "\n"
    return text

# =======================
# Step 3: Extract Text
# =======================
resume_text = ocr_pdf(resume_path)
job_text = ocr_pdf(jd_path)

def clean_text(text):
    return text.replace('\n', ' ').strip()

resume_text = clean_text(resume_text)
job_text = clean_text(job_text)

console.print("[green]Text extraction completed successfully![/green]\n")

# =======================
# Step 4: Setup Gemini LLM
# =======================
if not os.getenv("GOOGLE_API_KEY"):
    console.print("[red]ERROR:[/red] GOOGLE_API_KEY not set. Please export it before running.")
    exit(1)

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", temperature=0.7)

prompt = ChatPromptTemplate.from_template(
    """
    Based on the resume and job description below, write a tailored cover letter for the role of {topic}.
    Keep it under 50 lines, professional, and aligned with the job requirements.

    === RESUME ===
    {resume}

    === JOB DESCRIPTION ===
    {job_desc}
    """
)

output_parser = StrOutputParser()
chain = prompt | llm | output_parser

# =======================
# Step 5: Generate Cover Letter
# =======================
console.print("[cyan]Generating your custom cover letter... please wait[/cyan]")
response = chain.invoke({
    "topic": topic,
    "resume": resume_text,
    "job_desc": job_text
})

# =======================
# Step 6: Output Result
# =======================
output_file = "generated_cover_letter.md"
with open(output_file, "w", encoding="utf-8") as f:
    f.write(response)

console.print(f"\n[bold green]✅ Cover letter generated successfully![/bold green]")
console.print(f"Saved to: [underline]{output_file}[/underline]\n")
console.print("[bold white]Preview:[/bold white]\n")
console.print(response)
