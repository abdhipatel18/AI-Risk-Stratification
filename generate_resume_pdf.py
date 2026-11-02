"""
Generates the updated, ATS-compliant, single-page resume in PDF and DOCX formats.
Includes exact clickable hyperlinks for all certificates and contact info from the uploaded PDF.
"""

import os
import shutil
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import pypdf

pdf_path = r"c:\Users\Abdhi Patel\OneDrive\Desktop\abdhi\ABDHI_Patel_Resume.pdf"
downloads_pdf_path = r"C:\Users\Abdhi Patel\Downloads\ABDHI_Patel_Resume.pdf"
docx_path = r"c:\Users\Abdhi Patel\OneDrive\Desktop\abdhi\ABDHI_Patel_Resume.docx"
downloads_docx_path = r"C:\Users\Abdhi Patel\Downloads\ABDHI_Patel_Resume.docx"

# Exact Certificate URLs extracted from the user's uploaded PDF:
INTEL_CERT_URL = "https://drive.google.com/file/d/1_RAP9YGkyizoipB0psFVCeFo0Nr2BdZp/view?usp=drivesdk"
ANTHROPIC_FLUENCY_CERT_URL = "https://drive.google.com/file/d/16JTpQl1lkHdlfUnJnGzL23H_7AqAYH7Y/view?usp=drivesdk"
CLAUDE_101_CERT_URL = "https://drive.google.com/file/d/1g4p8EUZyU3xFl-913ddSw0Y8xdH6QgIA/view?usp=drivesdk"
INTERNSHIP_CERT_URL = "https://drive.google.com/file/d/14uKC1svAcYrI5JJCYSHdty21s9rlxWOp/view?usp=drivesdk"
LINKEDIN_URL = "http://www.linkedin.com/in/abdhi-p-patel-712488292"
GITHUB_URL = "https://github.com/abdhipatel18"
EMAIL_URL = "mailto:abdhipatel18@gmail.com"

# =========================================================================
# 1. GENERATE PDF RESUME (REPORTLAB)
# =========================================================================
doc = SimpleDocTemplate(
    pdf_path,
    pagesize=letter,
    leftMargin=28,
    rightMargin=28,
    topMargin=20,
    bottomMargin=20
)

styles = getSampleStyleSheet()

title_style = ParagraphStyle(
    "TitleStyle",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=16,
    leading=18,
    alignment=1,
    textColor=colors.HexColor("#0f172a")
)

subtitle_style = ParagraphStyle(
    "SubtitleStyle",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=9.5,
    leading=12,
    alignment=1,
    textColor=colors.HexColor("#1e40af")
)

contact_style = ParagraphStyle(
    "ContactStyle",
    parent=styles["Normal"],
    fontName="Helvetica",
    fontSize=8.2,
    leading=10.5,
    alignment=1,
    textColor=colors.HexColor("#334155")
)

heading_style = ParagraphStyle(
    "HeadingStyle",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=9.5,
    leading=11.5,
    textColor=colors.HexColor("#0f172a"),
    spaceAfter=1
)

body_style = ParagraphStyle(
    "BodyStyle",
    parent=styles["Normal"],
    fontName="Helvetica",
    fontSize=8.2,
    leading=10.5,
    textColor=colors.HexColor("#1e293b")
)

bullet_style = ParagraphStyle(
    "BulletStyle",
    parent=styles["Normal"],
    fontName="Helvetica",
    fontSize=8.0,
    leading=9.8,
    leftIndent=8,
    firstLineIndent=-5,
    textColor=colors.HexColor("#1e293b")
)

item_title_style = ParagraphStyle(
    "ItemTitleStyle",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=8.6,
    leading=10.5,
    textColor=colors.HexColor("#0f172a")
)

tech_stack_style = ParagraphStyle(
    "TechStackStyle",
    parent=styles["Normal"],
    fontName="Helvetica-Oblique",
    fontSize=7.8,
    leading=9.5,
    textColor=colors.HexColor("#475569")
)

story = []

# --- 1. HEADER ---
story.append(Paragraph("ABDHI P PATEL", title_style))
story.append(Spacer(1, 1))
story.append(Paragraph("AI/ML ENGINEER", subtitle_style))
story.append(Spacer(1, 2))
contact_html = (
    "+91 9019282910 &nbsp;&nbsp;•&nbsp;&nbsp; "
    f"<a href='{EMAIL_URL}'><font color='#1e40af'><u>abdhipatel18@gmail.com</u></font></a> &nbsp;&nbsp;•&nbsp;&nbsp; "
    f"<a href='{LINKEDIN_URL}'><font color='#1e40af'><u>LinkedIn</u></font></a> &nbsp;&nbsp;•&nbsp;&nbsp; "
    f"<a href='{GITHUB_URL}'><font color='#1e40af'><u>GitHub: abdhipatel18</u></font></a> &nbsp;&nbsp;•&nbsp;&nbsp; "
    "Chamarajanagar, India"
)
story.append(Paragraph(contact_html, contact_style))
story.append(Spacer(1, 2))
story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor("#0f172a"), spaceBefore=1, spaceAfter=3))

# --- 2. PROFILE ---
story.append(Paragraph("PROFILE", heading_style))
profile_text = (
    "Motivated <b>AI/ML Engineer</b> with a strong foundation in machine learning, data engineering, and predictive modeling. "
    "Experienced in developing and deploying end-to-end intelligent applications, clinical risk scoring engines, and conversational RAG assistants. "
    "Proficient in Python, FastAPI, Flask, Scikit-learn, SQL, and modern development workflows. Eager to contribute technical skills, learn emerging "
    "AI technologies, and build scalable, data-driven systems in collaborative environments."
)
story.append(Paragraph(profile_text, body_style))
story.append(Spacer(1, 2))
story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor("#0f172a"), spaceBefore=1, spaceAfter=3))

# --- 3. TECHNICAL SKILLS ---
story.append(Paragraph("TECHNICAL SKILLS", heading_style))
skills_data = [
    [
        Paragraph("<b>Languages:</b> Python, SQL, JavaScript, HTML5/CSS3", body_style),
        Paragraph("<b>Frameworks & Tools:</b> FastAPI, Flask, Streamlit, Git, Pytest, OpenPyXL", body_style)
    ],
    [
        Paragraph("<b>AI/ML & Data:</b> Scikit-learn, RAG, NLP, Feature Engineering, Pandas, NumPy", body_style),
        Paragraph("<b>Core Concepts & DBs:</b> Data Structures, DBMS, PostgreSQL, MySQL, OS, Networks", body_style)
    ]
]
skills_table = Table(skills_data, colWidths=[280, 276])
skills_table.setStyle(TableStyle([
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 0.5),
    ("TOPPADDING", (0, 0), (-1, -1), 0.5),
    ("LEFTPADDING", (0, 0), (-1, -1), 0),
    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
]))
story.append(skills_table)
story.append(Spacer(1, 2))
story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor("#0f172a"), spaceBefore=1, spaceAfter=3))

# --- 4. EDUCATION ---
story.append(Paragraph("EDUCATION", heading_style))
edu_data = [
    [
        Paragraph("<b>Bachelor of Engineering in Computer Science</b> &nbsp;&nbsp;|&nbsp;&nbsp; <b>CGPA: 6.60</b><br/>"
                  "<font color='#475569'>Sri Jayachamarajendra College of Engineering (SJCE), Mysuru</font>", body_style),
        Paragraph("<b>2023 – 2027</b>", ParagraphStyle("Right1", parent=body_style, alignment=2))
    ],
    [
        Paragraph("<b>Pre-University College (PCMB)</b> &nbsp;&nbsp;|&nbsp;&nbsp; <b>Percentage: 82%</b><br/>"
                  "<font color='#475569'>St Joseph PU College, Bengaluru</font>", body_style),
        Paragraph("<b>2021 – 2023</b>", ParagraphStyle("Right2", parent=body_style, alignment=2))
    ]
]
edu_table = Table(edu_data, colWidths=[436, 120])
edu_table.setStyle(TableStyle([
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("LEFTPADDING", (0, 0), (-1, -1), 0),
    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
    ("TOPPADDING", (0, 0), (-1, -1), 1),
]))
story.append(edu_table)
story.append(Spacer(1, 2))
story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor("#0f172a"), spaceBefore=1, spaceAfter=3))

# --- 5. EXPERIENCE & PROJECTS ---
story.append(Paragraph("EXPERIENCE & PROJECTS", heading_style))

# Internship Entry
exp_data = [
    [
        Paragraph("<b>Machine Learning Intern</b> &nbsp;—&nbsp; <b>MyClinicPulse LLC</b> (Arizona, USA / Remote)", item_title_style),
        Paragraph("<b>August 2026</b>", ParagraphStyle("RightDate", parent=item_title_style, alignment=2))
    ]
]
exp_table = Table(exp_data, colWidths=[436, 120])
exp_table.setStyle(TableStyle([
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("LEFTPADDING", (0, 0), (-1, -1), 0),
    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ("TOPPADDING", (0, 0), (-1, -1), 0),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
]))
story.append(exp_table)
story.append(Paragraph("<i>Project: AI-Based Patient Risk Stratification & Scheduling Prioritization</i>", tech_stack_style))
story.append(Paragraph("Tech Stack: Python, Pandas, NumPy, Scikit-learn, FastAPI, PyYAML, OpenPyXL, Streamlit, Pytest", tech_stack_style))

intern_bullets = [
    "• Developed an AI-driven healthcare decision-support pipeline consolidating multi-source EHR data (demographics, medications, lab results, care gaps) for automated patient risk assessment.",
    "• Implemented a configurable rule-based risk engine using Python and YAML with weighted clinical care-gap parameters to classify patients into High, Medium, Lower, and Already Scheduled tiers.",
    "• Built a scheduling prioritization engine that analyzes clinical risk factors to recommend actionable 1-month, 2-month, or 3-month outreach windows and conflict-free appointment slots.",
    "• Integrated Machine Learning using Scikit-learn for patient risk classification and model evaluation, alongside feature engineering, record matching, and automated data validation.",
    "• Developed an interactive Streamlit dashboard and automated reporting system generating prioritized patient cohorts, care-gap summaries, data-quality reports, and multi-tab Excel/CSV outputs."
]
for b in intern_bullets:
    story.append(Paragraph(b, bullet_style))

story.append(Spacer(1, 2.5))

# Project 2: AI Personalized Learning System
story.append(Paragraph("<b>AI Personalized Learning System</b>", item_title_style))
story.append(Paragraph("Tech Stack: Python, Flask, Scikit-learn, NLP, Pandas, Machine Learning", tech_stack_style))
p2_bullets = [
    "• Developed an AI-Based Personalized Learning System using Machine Learning and Flask to analyze student performance and learning patterns.",
    "• Implemented recommendation systems and predictive models to provide personalized study materials, adaptive learning content, and real-time progress tracking.",
    "• Utilized Python, Scikit-learn, NLP, and data analytics techniques to improve student engagement and academic learning outcomes."
]
for b in p2_bullets:
    story.append(Paragraph(b, bullet_style))

story.append(Spacer(1, 2))
story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor("#0f172a"), spaceBefore=1, spaceAfter=3))

# --- 6. CERTIFICATES (WITH EXACT CLICKABLE HYPERLINKS) ---
story.append(Paragraph("CERTIFICATES", heading_style))
certs = [
    f"• AI for Future Workforce – Intel : <a href='{INTEL_CERT_URL}'><font color='#1e40af'><u>Certificate</u></font></a>",
    f"• AI Fluency: Framework and Foundations by Anthropic : <a href='{ANTHROPIC_FLUENCY_CERT_URL}'><font color='#1e40af'><u>Certificate</u></font></a>",
    f"• Claude 101 by Anthropic : <a href='{CLAUDE_101_CERT_URL}'><font color='#1e40af'><u>Certificate</u></font></a>",
    f"• Internship Completion Certificate — AI-Based Patient Risk Stratification and Scheduling Prioritization, MyClinicPulse LLC, Arizona, USA | August 2026 : <a href='{INTERNSHIP_CERT_URL}'><font color='#1e40af'><u>Certificate</u></font></a>"
]
for c in certs:
    story.append(Paragraph(c, bullet_style))

doc.build(story)

reader = pypdf.PdfReader(pdf_path)
print(f"Generated PDF page count: {len(reader.pages)}")
shutil.copyfile(pdf_path, downloads_pdf_path)
print("Copied PDF to Downloads:", downloads_pdf_path)


# =========================================================================
# 2. GENERATE DOCX RESUME (PYTHON-DOCX) WITH HYPERLINKS
# =========================================================================
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

doc_w = docx.Document()
for section in doc_w.sections:
    section.top_margin = Inches(0.35)
    section.bottom_margin = Inches(0.35)
    section.left_margin = Inches(0.45)
    section.right_margin = Inches(0.45)

def add_docx_hr(p):
    pPr = p._p.get_or_add_pPr()
    pBdr = docx.oxml.OxmlElement('w:pBdr')
    bottom = docx.oxml.OxmlElement('w:bottom')
    bottom.set(docx.oxml.ns.qn('w:val'), 'single')
    bottom.set(docx.oxml.ns.qn('w:sz'), '6')
    bottom.set(docx.oxml.ns.qn('w:space'), '1')
    bottom.set(docx.oxml.ns.qn('w:color'), '0F172A')
    pBdr.append(bottom)
    pPr.append(pBdr)

def add_hyperlink(paragraph, url, text, color="1E40AF", underline=True):
    part = paragraph.part
    r_id = part.relate_to(url, docx.opc.constants.RELATIONSHIP_TYPE.HYPERLINK, is_external=True)
    hyperlink = docx.oxml.OxmlElement('w:hyperlink')
    hyperlink.set(docx.oxml.ns.qn('r:id'), r_id)
    new_run = docx.oxml.OxmlElement('w:r')
    rPr = docx.oxml.OxmlElement('w:rPr')
    if color:
        c = docx.oxml.OxmlElement('w:color')
        c.set(docx.oxml.ns.qn('w:val'), color)
        rPr.append(c)
    if underline:
        u = docx.oxml.OxmlElement('w:u')
        u.set(docx.oxml.ns.qn('w:val'), 'single')
        rPr.append(u)
    new_run.append(rPr)
    new_run.text = text
    hyperlink.append(new_run)
    paragraph._p.append(hyperlink)

# Header
p_h1 = doc_w.add_paragraph()
p_h1.alignment = WD_ALIGN_PARAGRAPH.CENTER
r_name = p_h1.add_run("ABDHI P PATEL")
r_name.bold = True
r_name.font.size = Pt(16)
r_name.font.name = "Arial"

p_sub = doc_w.add_paragraph()
p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
r_sub = p_sub.add_run("AI/ML ENGINEER")
r_sub.bold = True
r_sub.font.size = Pt(10)
r_sub.font.name = "Arial"
r_sub.font.color.rgb = RGBColor(30, 64, 175)

p_cnt = doc_w.add_paragraph()
p_cnt.alignment = WD_ALIGN_PARAGRAPH.CENTER
r_c1 = p_cnt.add_run("+91 9019282910   |   ")
r_c1.font.size = Pt(8.5)
add_hyperlink(p_cnt, EMAIL_URL, "abdhipatel18@gmail.com")
r_c2 = p_cnt.add_run("   |   ")
r_c2.font.size = Pt(8.5)
add_hyperlink(p_cnt, LINKEDIN_URL, "LinkedIn")
r_c3 = p_cnt.add_run("   |   ")
r_c3.font.size = Pt(8.5)
add_hyperlink(p_cnt, GITHUB_URL, "GitHub: abdhipatel18")
r_c4 = p_cnt.add_run("   |   Chamarajanagar, India")
r_c4.font.size = Pt(8.5)
add_docx_hr(p_cnt)

def add_docx_section(title):
    p = doc_w.add_paragraph()
    p.paragraph_format.space_before = Pt(3)
    p.paragraph_format.space_after = Pt(1)
    r = p.add_run(title)
    r.bold = True
    r.font.size = Pt(10.5)
    r.font.name = "Arial"
    r.font.color.rgb = RGBColor(15, 23, 42)
    add_docx_hr(p)

# Profile
add_docx_section("PROFILE")
p_prof = doc_w.add_paragraph()
p_prof.paragraph_format.space_before = Pt(1)
p_prof.paragraph_format.space_after = Pt(2)
r_pr = p_prof.add_run(
    "Motivated AI/ML Engineer with a strong foundation in machine learning, data engineering, and predictive modeling. "
    "Experienced in developing and deploying end-to-end intelligent applications, clinical risk scoring engines, and conversational RAG assistants. "
    "Proficient in Python, FastAPI, Flask, Scikit-learn, SQL, and modern development workflows. Eager to contribute technical skills, learn emerging "
    "AI technologies, and build scalable, data-driven systems in collaborative environments."
)
r_pr.font.size = Pt(8.5)
r_pr.font.name = "Arial"

# Technical Skills
add_docx_section("TECHNICAL SKILLS")
p_sk1 = doc_w.add_paragraph()
p_sk1.paragraph_format.space_before = Pt(1)
p_sk1.paragraph_format.space_after = Pt(1)
r_sk1_b = p_sk1.add_run("• Languages: ")
r_sk1_b.bold = True
r_sk1_b.font.size = Pt(8.5)
r_sk1 = p_sk1.add_run("Python, SQL, JavaScript, HTML5/CSS3   |   ")
r_sk1.font.size = Pt(8.5)
r_sk1_t = p_sk1.add_run("Frameworks & Tools: ")
r_sk1_t.bold = True
r_sk1_t.font.size = Pt(8.5)
r_sk1_t2 = p_sk1.add_run("FastAPI, Flask, Streamlit, Git, Pytest, OpenPyXL")
r_sk1_t2.font.size = Pt(8.5)

p_sk2 = doc_w.add_paragraph()
p_sk2.paragraph_format.space_before = Pt(1)
p_sk2.paragraph_format.space_after = Pt(2)
r_sk2_b = p_sk2.add_run("• AI/ML & Data: ")
r_sk2_b.bold = True
r_sk2_b.font.size = Pt(8.5)
r_sk2 = p_sk2.add_run("Scikit-learn, RAG, NLP, Feature Engineering, Pandas, NumPy   |   ")
r_sk2.font.size = Pt(8.5)
r_sk2_c = p_sk2.add_run("Core & DBs: ")
r_sk2_c.bold = True
r_sk2_c.font.size = Pt(8.5)
r_sk2_c2 = p_sk2.add_run("Data Structures, DBMS, PostgreSQL, MySQL, OS, Computer Networks")
r_sk2_c2.font.size = Pt(8.5)

# Education
add_docx_section("EDUCATION")
p_ed1 = doc_w.add_paragraph()
p_ed1.paragraph_format.space_before = Pt(1)
p_ed1.paragraph_format.space_after = Pt(1)
r = p_ed1.add_run("Bachelor of Engineering in Computer Science (SJCE, Mysuru) — CGPA: 6.60")
r.bold = True
r.font.size = Pt(8.5)
r_d = p_ed1.add_run("\t\t2023 – 2027")
r_d.bold = True
r_d.font.size = Pt(8.5)

p_ed2 = doc_w.add_paragraph()
p_ed2.paragraph_format.space_before = Pt(1)
p_ed2.paragraph_format.space_after = Pt(2)
r2 = p_ed2.add_run("Pre-University College (PCMB) (St Joseph PU College, Bengaluru) — Percentage: 82%")
r2.bold = True
r2.font.size = Pt(8.5)
r2_d = p_ed2.add_run("\t\t2021 – 2023")
r2_d.bold = True
r2_d.font.size = Pt(8.5)

# Experience & Projects
add_docx_section("EXPERIENCE & PROJECTS")
p_exp = doc_w.add_paragraph()
p_exp.paragraph_format.space_before = Pt(1)
p_exp.paragraph_format.space_after = Pt(1)
r_exp1 = p_exp.add_run("Machine Learning Intern — MyClinicPulse LLC (Arizona, USA / Remote)")
r_exp1.bold = True
r_exp1.font.size = Pt(9)
r_exp_d = p_exp.add_run("\tAugust 2026")
r_exp_d.bold = True
r_exp_d.font.size = Pt(9)

p_exp_sub = doc_w.add_paragraph()
p_exp_sub.paragraph_format.space_before = Pt(0)
p_exp_sub.paragraph_format.space_after = Pt(1)
r_sub_t = p_exp_sub.add_run("Project: AI-Based Patient Risk Stratification & Scheduling Prioritization | Tech Stack: Python, Pandas, Scikit-learn, FastAPI, Streamlit, OpenPyXL, Pytest")
r_sub_t.italic = True
r_sub_t.font.size = Pt(8)

for b in intern_bullets:
    bp = doc_w.add_paragraph(style='List Bullet')
    bp.paragraph_format.space_before = Pt(0)
    bp.paragraph_format.space_after = Pt(1)
    br = bp.add_run(b.replace("• ", ""))
    br.font.size = Pt(8)
    br.font.name = "Arial"

p_p2 = doc_w.add_paragraph()
p_p2.paragraph_format.space_before = Pt(2)
p_p2.paragraph_format.space_after = Pt(1)
r_p2_t = p_p2.add_run("AI Personalized Learning System")
r_p2_t.bold = True
r_p2_t.font.size = Pt(9)

p_p2_sub = doc_w.add_paragraph()
p_p2_sub.paragraph_format.space_before = Pt(0)
p_p2_sub.paragraph_format.space_after = Pt(1)
r_p2_st = p_p2_sub.add_run("Tech Stack: Python, Flask, Scikit-learn, NLP, Pandas, Machine Learning")
r_p2_st.italic = True
r_p2_st.font.size = Pt(8)

for b in p2_bullets:
    bp = doc_w.add_paragraph(style='List Bullet')
    bp.paragraph_format.space_before = Pt(0)
    bp.paragraph_format.space_after = Pt(1)
    br = bp.add_run(b.replace("• ", ""))
    br.font.size = Pt(8)
    br.font.name = "Arial"

# Certificates with docx hyperlinks
add_docx_section("CERTIFICATES")

certs_docx = [
    ("• AI for Future Workforce – Intel : ", INTEL_CERT_URL, "Certificate"),
    ("• AI Fluency: Framework and Foundations by Anthropic : ", ANTHROPIC_FLUENCY_CERT_URL, "Certificate"),
    ("• Claude 101 by Anthropic : ", CLAUDE_101_CERT_URL, "Certificate"),
    ("• Internship Completion Certificate — AI-Based Patient Risk Stratification and Scheduling Prioritization, MyClinicPulse LLC, Arizona, USA | August 2026 : ", INTERNSHIP_CERT_URL, "Certificate")
]

for prefix, url, link_text in certs_docx:
    cp = doc_w.add_paragraph()
    cp.paragraph_format.space_before = Pt(0)
    cp.paragraph_format.space_after = Pt(1)
    cr = cp.add_run(prefix)
    cr.font.size = Pt(8)
    cr.font.name = "Arial"
    add_hyperlink(cp, url, link_text)

doc_w.save(docx_path)
shutil.copyfile(docx_path, downloads_docx_path)
print("Saved DOCX with clickable hyperlinks to:", docx_path, "and", downloads_docx_path)
