from reportlab.pdfgen import canvas

def generate():
    c = canvas.Canvas("test_upload.pdf")
    c.drawString(100, 750, "DocuSign Mini Release Candidate Test Document")
    c.drawString(100, 730, "This is a valid PDF generated for flow verification.")
    c.save()
    print("Valid PDF 'test_upload.pdf' generated.")

if __name__ == "__main__":
    generate()
