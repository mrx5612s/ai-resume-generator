# utils.py
from reportlab.pdfgen import canvas
import io

def text_to_pdf(text, title="Document"):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer)
    c.setTitle(title)

    lines = text.split('\n')
    y = 800  # Start from top of the page
    for line in lines:
        if y <= 50:
            c.showPage()
            y = 800
        c.drawString(50, y, line)
        y -= 15

    c.save()
    buffer.seek(0)
    return buffer
