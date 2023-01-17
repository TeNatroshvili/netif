from reportlab.pdfgen import canvas
import mongotest as mo

# Erstelle ein neues PDF-Dokument mit einer Breite von 200 und einer Höhe von 300
c = canvas.Canvas("pdftest/mein_pdf.pdf", pagesize=(700, 200))

# Zeichne einen Text auf das PDF-Dokument
i=1
for x in mo.switches.find():
  print(x)
  c.drawString(10, (190-(i*10)), str(x))
  i=i+1

# Zeichne ein Rechteck auf das PDF-Dokument

# Speichere das PDF-Dokument
c.save()