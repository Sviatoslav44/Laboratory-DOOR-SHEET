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

## Notes
- The PDF overlay positioning assumes a ~540 x 780 pt page with the MAIN Hazards box in the lower-left half. Adjust the `main_box_*` values in `app.py` if your templates differ.
- Download names reflect the chosen hazard and risk (e.g., `door_sheet_biological_minimal_hazard.pdf`).
