# Door Sheet PDF Generator

## Prerequisites

- Python 3.8+

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the app:
   ```bash
   python3 app.py
   ```
3. Open http://127.0.0.1:5000 in your browser

## Report on Version 1 of the “Door Sheet PDF Generator”

1. Purpose of Version 2

In this version the user can select several hazards, obligations and prohibitions at the same time, choose an overall risk level, and generate a door sheet where all selected pictograms are arranged cleanly inside the official template. The interface has been completely redesigned to be more structured.

2. What Version 2 can do now

- The web page now has three main selection areas: hazards, obligations and prohibitions, plus a separate panel to select the overall risk level (Minimal, Moderate or Significant).
- Each group (hazards, obligations, prohibitions) has a smart search bar. When the user starts typing, only the items whose name matches the text remain visible.
- The user can select up to four hazards. All chosen hazards are inserted into the MAIN Hazards area of the door sheet. The program automatically adjusts the layout so that all hazard pictograms and their labels fit inside the box in a clean and readable way, regardless of how many hazards are selected.
- The user can select up to six items in total from obligations and prohibitions combined. Their icons are added to the obligations/prohibitions area of the door sheet, again with automatic layout so that all icons fit without overlapping.
- Each hazard card can show additional information. When the user hovers over the card or clicks on the information button, a short description of this hazard is displayed.
- The risk panel on the right allows the user to choose one risk level for the room: Minimal Risk, Moderate Risk or Significant Risk. Each option is shown as a coloured card with a shape (square, triangle or circle) and has an information button that explains what this level means.
- The system now validates the selections. It prevents the user from choosing more than four hazards or more than six obligations/prohibitions combined.
- When the user presses the “Generate PDF” button, the application creates a door sheet that includes all selected hazards, obligations/prohibitions and the chosen risk level.

3. How it works

On the front‑end side, the smart search bars filter the lists directly in the browser, so the user only sees the items that match the text they type. Selected hazards, obligations, prohibitions and the risk level are stored as identifiers. When the user clicks “Generate PDF”, these identifiers are sent to the back‑end.
On the back‑end side, the program looks up each identifier in the internal catalogue, retrieves the correct pictograms and text labels, and calculates how many items must be placed in each area of the door sheet. It then arranges the icons in a simple grid so that they remain aligned inside the existing template and scales them if needed to avoid overlaps.

4. Planned improvements for the next version

The next version will focus on turning the generator into a complete “door sheet form”, where all relevant laboratory information can be entered directly on the website and then exported in one PDF.
In the next release we plan to add: a full interface redesign, a Research Group Count field (up to three groups), Room Number, Laboratory PI and Laboratory Safety Coordinator contacts, an Emergency Contact section (two contacts), and dropdown fields for Type of Activity and Hazard Class.
