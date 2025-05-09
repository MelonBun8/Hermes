import io
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import streamlit as st

def export_conversation_to_pdf(messages):
    """Export conversation to PDF"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, 
                           rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=72)
    
    styles = getSampleStyleSheet()
    
    # Create custom styles
    styles.add(ParagraphStyle(name='User',
                              parent=styles['Normal'],
                              fontName='Helvetica-Bold',
                              fontSize=12,
                              textColor=colors.blue,
                              spaceAfter=6))
    
    styles.add(ParagraphStyle(name='Assistant',
                              parent=styles['Normal'],
                              fontName='Helvetica',
                              fontSize=12,
                              spaceBefore=6,
                              spaceAfter=12))
    
    story = []
    
    # Add title
    title = Paragraph("Hermes Research Assistant - Conversation Export", styles['Title'])
    story.append(title)
    story.append(Spacer(1, 24))
    
    # Add conversation
    for message in messages:
        if message["role"] == "user":
            story.append(Paragraph(f"<b>You:</b> {message['content']}", styles['User']))
        else:
            story.append(Paragraph(f"<b>Hermes:</b> {message['content']}", styles['Assistant']))
        story.append(Spacer(1, 12))
    
    doc.build(story)
    
    # Get PDF data
    pdf_data = buffer.getvalue()
    buffer.close()
    
    return pdf_data