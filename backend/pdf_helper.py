import os
import json
import logging
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

logger = logging.getLogger(__name__)

# Custom canvas to support Page X of Y numbering
class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            super().showPage()
        super().save()

    def draw_page_number(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.HexColor("#64748b")) # slate-500
        
        # Draw header
        self.drawString(54, 750, "AI-Powered Video Summarization System")
        self.setStrokeColor(colors.HexColor("#cbd5e1")) # slate-300
        self.setLineWidth(0.5)
        self.line(54, 742, 558, 742)
        
        # Draw footer
        self.line(54, 45, 558, 45)
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 30, page_text)
        self.drawString(54, 30, "Generated automatically by AI Video Summarizer")
        self.restoreState()

def _ensure_string(val, default_val) -> str:
    if val is None:
        return default_val
    if isinstance(val, str):
        return val
    if isinstance(val, list):
        return '\n'.join([str(v) for v in val])
    if isinstance(val, dict):
        return json.dumps(val, indent=2)
    return str(val)

def generate_pdf_report(
    video_title: str,
    summary_data: dict,
    quiz_data_str: str,
    output_path: str
):
    """Generates a comprehensive PDF containing summaries, notes, and quizzes."""
    logger.info(f"Generating PDF report for '{video_title}' -> {output_path}")
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # 0.75 in margins
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=72,
        bottomMargin=72
    )
    
    styles = getSampleStyleSheet()
    
    # Define custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=colors.HexColor("#0f172a"), # slate-900
        spaceAfter=15
    )
    
    h1_style = ParagraphStyle(
        'DocH1',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        textColor=colors.HexColor("#1e3a8a"), # deep blue
        spaceBefore=18,
        spaceAfter=10,
        keepWithNext=True
    )
    
    h2_style = ParagraphStyle(
        'DocH2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#0f766e"), # teal-700
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=10.5,
        leading=15,
        textColor=colors.HexColor("#334155"), # slate-700
        spaceAfter=8
    )
    
    keyword_style = ParagraphStyle(
        'DocKeywords',
        parent=styles['Italic'],
        fontName='Helvetica-Oblique',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#475569"),
        spaceAfter=15
    )
    
    story = []
    
    # Title Section
    story.append(Spacer(1, 10))
    story.append(Paragraph(f"Analysis Report: {video_title}", title_style))
    
    # Keywords
    keywords = summary_data.get("keywords", "N/A")
    story.append(Paragraph(f"<b>Keywords / Concepts:</b> {keywords}", keyword_style))
    story.append(Spacer(1, 10))
    
    # SECTION 1: Summaries
    story.append(Paragraph("1. Executive Summary", h1_style))
    story.append(Paragraph("<b>Short Summary:</b>", h2_style))
    story.append(Paragraph(summary_data.get("short_summary", "No short summary generated."), body_style))
    
    story.append(Paragraph("<b>Detailed Analysis:</b>", h2_style))
    detailed_text = _ensure_string(summary_data.get("detailed_summary"), "No detailed summary generated.")
    for para in detailed_text.split('\n\n'):
        if para.strip():
            story.append(Paragraph(para.strip(), body_style))
            
    story.append(Paragraph("<b>Topic-wise Breakdown:</b>", h2_style))
    topic_text = _ensure_string(summary_data.get("topic_summary"), "No topic breakdown generated.")
    for line in topic_text.split('\n'):
        if line.strip():
            # Format bullets
            text = line.strip().lstrip('-*').strip()
            story.append(Paragraph(f"• {text}", body_style))
            
    story.append(PageBreak())
    
    # SECTION 2: Study Notes
    story.append(Paragraph("2. Comprehensive Study Notes", h1_style))
    
    story.append(Paragraph("<b>Key Takeaways & Formulas:</b>", h2_style))
    takeaways = _ensure_string(summary_data.get("notes_important"), "")
    for line in takeaways.split('\n'):
        if line.strip():
            text = line.strip().lstrip('-*').strip()
            story.append(Paragraph(f"• {text}", body_style))
            
    story.append(Paragraph("<b>Revision Cheatsheet:</b>", h2_style))
    revision = _ensure_string(summary_data.get("notes_revision"), "")
    for line in revision.split('\n'):
        if line.strip():
            text = line.strip().lstrip('-*').strip()
            story.append(Paragraph(f"• {text}", body_style))
            
    story.append(Paragraph("<b>Detailed Study Guide:</b>", h2_style))
    study_guide = _ensure_string(summary_data.get("notes_study"), "")
    for para in study_guide.split('\n\n'):
        if para.strip():
            story.append(Paragraph(para.strip(), body_style))
            
    story.append(PageBreak())
    
    # SECTION 3: Quizzes and Assessment
    story.append(Paragraph("3. Assessment Quiz", h1_style))
    
    try:
        quiz_data = json.loads(quiz_data_str) if isinstance(quiz_data_str, str) else quiz_data_str
    except Exception:
        quiz_data = {}
        
    mcqs = quiz_data.get("mcqs", [])
    if mcqs:
        story.append(Paragraph("Multiple Choice Questions (MCQs)", h2_style))
        for idx, mcq in enumerate(mcqs, 1):
            q_text = f"<b>Q{idx}. {mcq.get('question')}</b>"
            story.append(Paragraph(q_text, body_style))
            for opt in mcq.get("options", []):
                story.append(Paragraph(f"&nbsp;&nbsp;&nbsp;&nbsp;{opt}", body_style))
            story.append(Paragraph(f"<i>Correct Answer: {mcq.get('answer')}</i>", body_style))
            story.append(Spacer(1, 5))
            
    shorts = quiz_data.get("short_questions", [])
    if shorts:
        story.append(Spacer(1, 10))
        story.append(Paragraph("Short Answer Questions", h2_style))
        for idx, sq in enumerate(shorts, 1):
            story.append(Paragraph(f"<b>Q{idx}. {sq}</b>", body_style))
            story.append(Spacer(1, 10)) # Leave blank space for answer
            
    longs = quiz_data.get("long_questions", [])
    if longs:
        story.append(Spacer(1, 10))
        story.append(Paragraph("Essay / Case Study Questions", h2_style))
        for idx, lq in enumerate(longs, 1):
            story.append(Paragraph(f"<b>Q{idx}. {lq}</b>", body_style))
            story.append(Spacer(1, 20)) # Leave blank space
            
    # Build Document
    doc.build(story, canvasmaker=NumberedCanvas)
    logger.info("PDF generation complete.")
