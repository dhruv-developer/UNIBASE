# generate_pdf.py

from fpdf import FPDF
import os

# List of source files to include in the PDF.
files = [
    "unibase/registry.py",
    "unibase/utils/ai_agent.py",
    "unibase/cli.py"
]

class PDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, "UNIBASE Codebase", 0, 1, "C")
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", 0, 0, "C")

pdf = PDF()
pdf.set_auto_page_break(auto=True, margin=15)
pdf.add_page()

pdf.set_font("Courier", size=10)

for file in files:
    if os.path.exists(file):
        pdf.multi_cell(0, 5, f"FILE: {file}\n{'-'*80}\n")
        with open(file, "r") as f:
            code = f.read()
            pdf.multi_cell(0, 5, code)
        pdf.add_page()
    else:
        pdf.multi_cell(0, 5, f"FILE: {file} not found.\n")

output_file = "UNIBASE_Codebase.pdf"
pdf.output(output_file)
print(f"PDF generated: {output_file}")
