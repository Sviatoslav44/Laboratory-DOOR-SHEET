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

## Report on Version 3 of the “Door Sheet PDF Generator”

1. Purpose of Version 3
   Laboratory staff can now enter room information (groups, room number, contacts, activity type and hazard class) directly in the web interface, select the relevant hazards, obligations, prohibitions and risk level, and generate a single PDF that is ready to be printed and placed on the laboratory door.

2. What Version 3 can do now

- The interface has been fully redesigned. The page is now structured as a clear form, with a block for laboratory information at the top and the selection blocks for hazards, obligations, prohibitions and risk below. The layout is more intuitive and user-friendly.
- A new field “Research Group Count” allows the user to specify how many research groups share the room (from 1 to 3).
- The user can enter the Room Number, which is transferred directly into the corresponding area of the PDF.
- Laboratory contacts are now part of the form. The generator includes fields for the Laboratory PI (name and phone number) and for the Laboratory Safety Coordinator (name and phone number).
- An “Emergency Contact” section lets the user define two independent emergency contacts (Emergency Contact 1 and Emergency Contact 2) with their phone numbers.
- Two dropdowns allow the user to specify the Type of Activity performed in the room and the Hazard Class.
- When the user clicks “Generate PDF”, the system now produces a complete door sheet that includes room information (group count, room number, contacts, activity type, hazard class) together with all selected hazards, obligations/prohibitions and the chosen risk level, with all pictograms and text elements placed in their appropriate positions.

3. How it works

On the front-end side, the interface combines classic form fields (text inputs, numeric fields and dropdowns) with the existing selection grids for hazards, obligations, prohibitions and risk. All values are stored in the browser until the user confirms the form by pressing “Generate PDF”. The smart search bars still filter the lists of hazards, obligations and prohibitions in real time, and selection limits are enforced in the browser to avoid overloading the layout.
When the form is submitted, the back-end receives a single structured payload that contains: room information, contact details, activity and hazard class, the list of selected hazards and obligations/prohibitions, and the selected risk level. The back-end looks up the corresponding pictograms and text labels in its catalogue and fills a predefined door sheet template.
