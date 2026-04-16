"""Export the .pptx to PDF via PowerPoint COM. Requires PowerPoint installed."""
from pathlib import Path
import win32com.client
import os

HERE = Path(__file__).parent
pptx = HERE / "ACIC2026_CausalSHAP_Poster.pptx"
pdf  = HERE / "ACIC2026_CausalSHAP_Poster.pdf"

if pdf.exists():
    pdf.unlink()

app = win32com.client.Dispatch("PowerPoint.Application")
# PowerPoint sometimes needs a visible window on Windows 11
try:
    deck = app.Presentations.Open(str(pptx.resolve()), WithWindow=False)
except Exception:
    deck = app.Presentations.Open(str(pptx.resolve()))

# 32 = ppSaveAsPDF
deck.SaveAs(str(pdf.resolve()), 32)
deck.Close()
app.Quit()

print(f"Wrote {pdf}")
