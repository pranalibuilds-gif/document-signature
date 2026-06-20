import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, letter, landscape

def generate_pdf(filename, pages, size=A4, orientation='portrait'):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    if orientation == 'landscape':
        size = landscape(size)

    c = canvas.Canvas(filename, pagesize=size)
    width, height = size

    for i in range(1, pages + 1):
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, height - 50, f"Stress Test Page {i} of {pages}")
        c.setFont("Helvetica", 12)
        c.drawString(50, height - 80, f"Size: {size} | Orientation: {orientation}")

        # Draw some grid lines to help verify coordinates
        c.setStrokeColorRGB(0.8, 0.8, 0.8)
        for x in range(0, int(width), 100):
            c.line(x, 0, x, height)
        for y in range(0, int(height), 100):
            c.line(0, y, width, y)

        c.showPage()
    c.save()
    print(f"Generated: {filename} ({pages} pages)")

def generate_mixed_pdf(filename):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    c = canvas.Canvas(filename)

    # Page 1: Portrait A4
    c.setPageSize(A4)
    c.drawString(100, 700, "Page 1: Portrait A4")
    c.showPage()

    # Page 2: Landscape A4
    c.setPageSize(landscape(A4))
    c.drawString(100, 500, "Page 2: Landscape A4")
    c.showPage()

    # Page 3: Portrait Letter
    c.setPageSize(letter)
    c.drawString(100, 600, "Page 3: Portrait Letter")
    c.showPage()

    c.save()
    print(f"Generated Mixed: {filename}")

if __name__ == "__main__":
    base = "storage/stress_tests"
    generate_pdf(f"{base}/single_page.pdf", 1)
    generate_pdf(f"{base}/medium_20.pdf", 20)
    generate_pdf(f"{base}/large_50.pdf", 50)
    generate_pdf(f"{base}/landscape_a4.pdf", 5, orientation='landscape')
    generate_mixed_pdf(f"{base}/mixed_orientation.pdf")
