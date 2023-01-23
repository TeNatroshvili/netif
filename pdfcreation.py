from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from mongodb import switches

c = canvas.Canvas("reports/mein_pdf.pdf", pagesize=A4)

# Zeichne einen Text auf das PDF-Dokument
i=1
for x in switches.find():
  print(x)
  c.drawString(10, (190-(i*10)), str(x))
  i=i+1

# Zeichne ein Rechteck auf das PDF-Dokument

# Speichere das PDF-Dokument
c.save()