# Door Sheet PDF Generator

A minimal Flask app that overlays a hazard pictogram and caption onto a provided door sheet template PDF.

## Prerequisites
- Python 3.8+
- Hazard icons placed under `static/images/`:
  - `electrical_hazard.png`
  - `biosafety_hazard.png` (used for Biosafety Level 1 and 2)
  - `toxic_cmr_compounds.png`
  - `Harmful_Compounds.png`
- Risk-specific PDF templates placed under `static/risks/`:
  - `minimal_risk.pdf`
  - `moderate_risk.pdf`
  - `significant_risk.pdf`

## Setup
1. Create and activate a virtual environment (optional but recommended):
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\\Scripts\\activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the app:
   ```bash
   python app.py
   ```
4. Open http://127.0.0.1:5000 in your browser:
   - Click the hazard search box to select **Biological Hazard** or **Electrical Hazard**.
   - Choose a risk level (Minimal/Moderate/Significant) via the colored buttons.
   - Click **Generate PDF**.

Purpose of Version 5

Version 5 focuses on improving usability, standardization, and visual clarity.
Laboratory staff can now select Departments and Rooms from predefined lists instead of entering free text, reducing errors and ensuring consistency across generated door sheets. In addition, the interface has been visually redesigned, and a dark theme has been introduced to improve comfort and accessibility.

