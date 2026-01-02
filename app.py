from io import BytesIO
from pathlib import Path
from typing import Dict, List, Tuple

from flask import Flask, render_template, request, send_file
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent
TEMPLATE_PATH = BASE_DIR / "door_sheet_template.pdf"

HAZARDS = {
    "electrical": {
        "label": "Electrical Hazard",
        "caption": "Electrical Hazard",
        "icon_path": BASE_DIR / "static" / "hazards" / "electrical_hazard.png",
        "lines": ["Electrical Hazard"],
    },
    "biosafety_level_1": {
        "label": "Biosafety Level 1",
        "caption": "Biosafety Level 1",
        "icon_path": BASE_DIR / "static" / "hazards" / "biosafety_hazard.png",
        "lines": ["Biosafety Level 1"],
    },
    "biosafety_level_2": {
        "label": "Biosafety Level 2",
        "caption": "Biosafety Level 2",
        "icon_path": BASE_DIR / "static" / "hazards" / "biosafety_hazard.png",
        "lines": ["Biosafety Level 2"],
    },
    "toxic_cmr": {
        "label": "Toxic and/or CMR Compounds",
        "caption": "Toxic and/or CMR Compounds",
        "icon_path": BASE_DIR / "static" / "hazards" / "toxic_cmr_compounds.png",
        "lines": ["Toxic and/or CMR", "Compounds"],
    },
    "harmful_compounds": {
        "label": "Harmful Compounds",
        "caption": "Harmful Compounds",
        "icon_path": BASE_DIR / "static" / "hazards" / "Harmful_Compounds.png",
        "lines": ["Harmful Compounds"],
    },
    "asphyxiation_hazard": {
        "label": "Asphyxiation Hazard",
        "caption": "Asphyxiation Hazard",
        "icon_path": BASE_DIR / "static" / "hazards" / "Asphyxiation_Hazard.png",
    },
    "compressed_gas": {
        "label": "Compressed Gas",
        "caption": "Compressed Gas",
        "icon_path": BASE_DIR / "static" / "hazards" / "Compressed_Gas.png",
    },
    "corrosive_compounds": {
        "label": "Corrosive Compounds",
        "caption": "Corrosive Compounds",
        "icon_path": BASE_DIR / "static" / "hazards" / "Corrosive_Compounds.png",
    },
    "explosive_compounds": {
        "label": "Explosive Compounds",
        "caption": "Explosive Compounds",
        "icon_path": BASE_DIR / "static" / "hazards" / "Explosive_Compounds.png",
    },
    "flammable_compounds": {
        "label": "Flammable Compounds",
        "caption": "Flammable Compounds",
        "icon_path": BASE_DIR / "static" / "hazards" / "Flammable_Compounds.png",
    },
    "hot_surface": {
        "label": "Hot Surface",
        "caption": "Hot Surface",
        "icon_path": BASE_DIR / "static" / "hazards" / "Hot_Surface.png",
    },
    "ionising_radiation": {
        "label": "Ionising Radiation",
        "caption": "Ionising Radiation",
        "icon_path": BASE_DIR / "static" / "hazards" / "Ionising_Radiation.png",
    },
    "laser_radiation": {
        "label": "Laser Radiation",
        "caption": "Laser Radiation",
        "icon_path": BASE_DIR / "static" / "hazards" / "Laser_Radiation.png",
    },
    "low_temperature": {
        "label": "Low Temperature",
        "caption": "Low Temperature",
        "icon_path": BASE_DIR / "static" / "hazards" / "Low_Temperature.png",
    },
    "magnetic_fields": {
        "label": "Magnetic Fields",
        "caption": "Magnetic Fields",
        "icon_path": BASE_DIR / "static" / "hazards" / "Magnetic_Fields.png",
    },
    "nanomaterial_hazard": {
        "label": "Nanomaterial Hazard",
        "caption": "Nanomaterial Hazard",
        "icon_path": BASE_DIR / "static" / "hazards" / "Nanomaterial_Hazard.png",
    },
    "non_ionising_radiation": {
        "label": "Non Ionising Radiation",
        "caption": "Non Ionising Radiation",
        "icon_path": BASE_DIR / "static" / "hazards" / "Non-Ionising_Radiation.png",
    },
    "explosive_atmosphere": {
        "label": "Explosive Atmosphere",
        "caption": "Explosive Atmosphere",
        "icon_path": BASE_DIR / "static" / "hazards" / "Explosive_Atmosphere.png",
    },
    "oxidising_compounds": {
        "label": "Oxidising Compounds",
        "caption": "Oxidising Compounds",
        "icon_path": BASE_DIR / "static" / "hazards" / "Oxidising_Compounds.png",
    },
}

HAZARD_INFO = {
    "biosafety_level_1": "Organisms of biosafety level 1 and above are present in the lab.",
    "biosafety_level_2": "Organisms of biosafety level 2 and above are present in the lab.",
    "toxic_cmr": "The quantity of toxic or CMR compounds in the lab > 5 g. Exception: Methanol.",
    "harmful_compounds": "The quantity of harmful compounds in the lab > 2 L.",
    "flammable_compounds": (
        "Total volume of containers with flammable compounds is:\n"
        "> 25 L in ventilated cabinet\n"
        "> 50 L in EI90 ventilated cabinet\n"
        "> 5 L in non-ventilated cabinets, or out in the lab"
    ),
    "oxidising_compounds": "The quantity of oxidising compounds in the lab > 1 kg.",
    "corrosive_compounds": "The quantity of corrosive compounds (esp. GHS Cat 1A) present in the lab > 1 L.",
    "electrical": (
        "Non-covered live parts:\n"
        "Voltage > 51 V (AC) or 121 (DC) - no capacitors\n"
        "Voltage > 1000 V (AC) or 1500 (DC) - with capacitors"
    ),
    "non_ionising_radiation": "Radio or microwave sources are only partially or not at all shielded.",
    "compressed_gas": "Cylinder > 10 L at 200 bars or any cylinder in a very small space.",
    "magnetic_fields": (
        "0.5 mT (5 Gauss) line outside the instrument.\n"
        "'No access for people with implanted cardiac device' compulsory"
    ),
    "hot_surface": "Temperature of surface > 80 °C, with exception of heating plates.",
    "low_temperature": "Room temperature < 5 °C.",
    "nanomaterial_hazard": "Nanomaterials in significant quantities in powder form (>1 g) are present in the laboratories.",
    "asphyxiation_hazard": "Cryogenic liquids volume > 20 L per 100 m³ of laboratory.",
    "explosive_compounds": "Explosive compounds are present in the laboratory.",
    "laser_radiation": "One or more lasers of class 3B and above are present in the lab.",
    "ionising_radiation": "Radioactive sources (sealed or unsealed) and/or X-ray sources are present in the lab.",
    "explosive_atmosphere": (
        "The lab is classified according to the ATEX directive (2014/34/EU).\n"
        "- Storage or use of flammable liquids without adequate ventilation\n"
        "- Places where dust particles < 0.5 mm are formed\n"
        "- Confined storage of flammable gases\n"
        "Radioactive sources (sealed or unsealed) and/or X-ray sources are present in the lab."
    ),
}

OBLIGATION_DIR = BASE_DIR / "static" / "obligation_signs"
PROHIBITION_DIR = BASE_DIR / "static" / "prohibition_signs"


def load_obligations() -> Dict[str, dict]:
    obligations: Dict[str, dict] = {}
    if not OBLIGATION_DIR.exists():
        return obligations
    for path in sorted(OBLIGATION_DIR.glob("*.png")):
        key = path.stem.lower().replace("-", "_")
        label = path.stem.replace("_", " ").replace("-", " ").replace("  ", " ").title()
        obligations[key] = {
            "label": label,
            "caption": label,
            "icon_path": path,
        }
    return obligations


OBLIGATIONS = load_obligations()
PROHIBITIONS = {}
PROHIBITION_INFO = {
    "no_access_to_unauthorised_personnel": "No access to unauthorised personnel.",
    "no_food_or_drink_allowed": "No food or drink allowed.",
    "no_access_for_people_with_active_implanted_cardiac_device": "No access for people with active implanted cardiac device.",
    "no_access_for_people_with_metallic_implants": "No access for people with metallic implants.",
    "do_not_extinguish_with_water": "Do not extinguish with water.",
    "no_open_flame": "No open flame.",
    "no_flammable_compounds.": "No flammable compounds.",
    "no_active_mobile_phones": "No active mobile phones.",
    "no_metallic_articles_or_watches": "No metallic articles or watches.",
}
if PROHIBITION_DIR.exists():
    for path in sorted(PROHIBITION_DIR.glob("*.png")):
        key = path.stem.lower().replace("-", "_")
        label = path.stem.replace("_", " ").replace("-", " ").replace("  ", " ").title()
        PROHIBITIONS[key] = {
            "label": label,
            "caption": label,
            "icon_path": path,
        }

RISK_TEMPLATES = {
    "minimal": {
        "label": "Minimal Risk",
        "template_path": BASE_DIR / "static" / "risks" / "minimal_risk.pdf",
    },
    "moderate": {
        "label": "Moderate Risk",
        "template_path": BASE_DIR / "static" / "risks" / "moderate_risk.pdf",
    },
    "significant": {
        "label": "Significant Risk",
        "template_path": BASE_DIR / "static" / "risks" / "significant_risk.pdf",
    },
}
RISK_INFO = {
    "minimal": "- Minimal risk present.\n- Limited access to personnel.\n- Office, auditorium, kitchen.",
    "moderate": (
        "- Moderate risk present, such as limited amounts of hazardous chemicals, lasers up to class 2B, or biosafety level 1 laboratories.\n"
        "- Restricted access. Only personnel who followed the general safety training can obtain access."
    ),
    "significant": (
        "- Restricted access; emergency intervention only.\n"
        "- Access not authorized; cleaning on request under supervision of lab personnel."
    ),
}


def generate_hazard_pdf(
    hazard_keys: List[str],
    obligation_keys: List[str],
    prohibition_keys: List[str],
    risk_key: str,
    department: str,
    research_groups: List[str],
    room_number: str,
    pi_name: str,
    pi_phone: str,
    safety_name: str,
    safety_phone: str,
    emergency_name_1: str,
    emergency_phone_1: str,
    emergency_name_2: str,
    emergency_phone_2: str,
    activity_type: str,
    activity_hazard: str,
) -> Tuple[BytesIO, str]:
    """Overlay selected hazard icons, obligation/prohibition signs, research groups, department, and captions onto the chosen risk template."""
    unique_hazards = []
    for key in hazard_keys:
        hazard = HAZARDS.get(key)
        if hazard:
            unique_hazards.append((key, hazard))

    unique_obligations = []
    for key in obligation_keys:
        obligation = OBLIGATIONS.get(key)
        if obligation:
            unique_obligations.append((key, obligation))
    unique_prohibitions = []
    for key in prohibition_keys:
        prohibition = PROHIBITIONS.get(key)
        if prohibition:
            unique_prohibitions.append((key, prohibition))

    risk = RISK_TEMPLATES.get(risk_key)
    if risk is None:
        raise ValueError(f"Unsupported risk type: {risk_key}")

    template_path = risk["template_path"]
    if not template_path.exists():
        raise FileNotFoundError(f"Template PDF not found at: {template_path}")

    reader = PdfReader(str(template_path))
    if not reader.pages:
        raise ValueError("Template PDF has no pages")

    template_page = reader.pages[0]
    page_width = float(template_page.mediabox.width)
    page_height = float(template_page.mediabox.height)

    # Tune these values if the MAIN Hazards box changes position/size in the template.
    main_box_x = 40
    main_box_y = 80
    main_box_width = page_width * 0.45
    main_box_height = page_height * 0.45
    hazard_center_x = (
        main_box_x + (main_box_width / 2) - 15
    )  # fixed center for the hazard box
    obligation_box_width = main_box_width
    obligation_box_height = main_box_height
    obligation_box_x = min(
        page_width - obligation_box_width - 20, main_box_x + main_box_width + 20
    )
    obligation_box_y = main_box_y
    # Research group header row estimates (adjust if the header layout moves)
    logo_block_width = 140.0
    label_block_width = 110.0  # cell with "Research group(s):"
    room_block_width = 110.0
    research_margin = 10.0
    research_row_top = page_height - 130.0
    research_row_height = 38.0
    research_row_width = (
        page_width
        - logo_block_width
        - label_block_width
        - room_block_width
        - (research_margin * 2)
    )
    research_row_start_x = logo_block_width + label_block_width + research_margin

    # Create the overlay with the icons and captions.
    overlay_stream = BytesIO()
    overlay_canvas = canvas.Canvas(overlay_stream, pagesize=(page_width, page_height))

    # Department line (centered in the header area). If empty, draw nothing.
    if department:
        # Aim for Calibri Bold 14; fall back to Helvetica-Bold if unavailable.
        preferred_font = "Calibri-Bold"
        fallback_font = "Helvetica-Bold"
        try:
            overlay_canvas.setFont(preferred_font, 12)
            font_name = preferred_font
        except Exception:  # noqa: BLE001
            overlay_canvas.setFont(fallback_font, 12)
            font_name = fallback_font
        overlay_canvas.setFillColorRGB(0, 0, 0)
        # Align text to the center of the header band (using the prior rectangle bounds).
        rect_w = 395
        rect_h = 28
        rect_x = (page_width - rect_w) / 2 + 57  # right-shift reference
        rect_y = page_height - 88
        header_center_x = rect_x + rect_w / 2
        text_y = rect_y + (rect_h / 2) - 1  # lift text baseline by 2 pts
        # Text centered inside (rectangle removed).
        overlay_canvas.setFont(font_name, 12)
        overlay_canvas.setFillColorRGB(0, 0, 0)
        overlay_canvas.drawCentredString(header_center_x, text_y, department)

    count = len(unique_hazards)
    caption_gap = 12
    caption_height = 14
    spacing = 0  # vertical spacing between entries

    def scaled_size(
        path: Path, max_w: float, max_h: float
    ) -> Tuple[float, float, ImageReader]:
        reader_img = ImageReader(str(path))
        img_w, img_h = reader_img.getSize()
        target_w = max_w
        scale = target_w / float(img_w)
        target_h = img_h * scale
        if target_h > max_h:
            scale = max_h / float(img_h)
            target_w = img_w * scale
            target_h = max_h
        return target_w, target_h, reader_img

    def draw_caption_lines(x: float, base_y: float, hazard: dict) -> float:
        """Draw one or multiple caption lines centered at x, starting at base_y."""
        lines = hazard.get("lines") or [hazard["caption"]]
        line_height = 10.4  # 20% smaller
        start_y = max(base_y, main_box_y + 10 + (len(lines) - 1) * line_height)
        overlay_canvas.setFont("Helvetica-Bold", 10.4)
        for idx_line, line in enumerate(lines):
            overlay_canvas.drawCentredString(x, start_y - idx_line * line_height, line)
        # Return the y of the last drawn line
        return start_y - (len(lines) - 1) * line_height

    if count == 0:
        # No hazards selected; skip drawing hazards.
        pass
    elif count == 4:
        # Grid 2x2 layout.
        cell_w = main_box_width / 2
        cell_h = main_box_height / 2
        max_w = min(cell_w - 40.0, 180.0)
        max_h = cell_h - 50.0

        icon_sizes = []
        for hazard_key, hazard in unique_hazards:
            w, h, reader_icon = scaled_size(
                hazard["icon_path"],
                max_w=max_w,
                max_h=max_h,
            )
            icon_sizes.append((hazard, reader_icon, w, h))

        col_centers = [
            hazard_center_x - (cell_w / 2),
            hazard_center_x + (cell_w / 2),
        ]
        row_tops = [
            main_box_y + main_box_height - 50.0,
            main_box_y + cell_h - 0.0,  # raise bottom row by 20 pts
        ]

        positions = [
            (0, 0),  # top-left
            (0, 1),  # top-right
            (1, 0),  # bottom-left
            (1, 1),  # bottom-right
        ]

        for (row_idx, col_idx), (hazard, reader_icon, w, h) in zip(
            positions, icon_sizes
        ):
            # Scale up for 4-item layout.
            w *= 1.3
            h *= 1.3
            icon_x = col_centers[col_idx] - (w / 2)
            icon_y = row_tops[row_idx] - h + 10  # raise icons and captions by 10 pts
            overlay_canvas.drawImage(
                reader_icon,
                icon_x,
                icon_y,
                width=w,
                height=h,
                preserveAspectRatio=True,
                mask="auto",
            )
            # Give captions more breathing room under each icon.
            text_y = max(icon_y - (caption_gap), main_box_y)
            draw_caption_lines(col_centers[col_idx], text_y, hazard)

    elif count == 3:
        # Special layout: one large icon on top, two smaller side-by-side (like the reference image).
        top_hazard = unique_hazards[0][1]
        bottom_hazards = [h[1] for h in unique_hazards[1:3]]

        top_icon_w, top_icon_h, top_reader = scaled_size(
            top_hazard["icon_path"],
            max_w=min(220.0, main_box_width - 40.0),
            max_h=main_box_height * 0.45,
        )

        bottom_left_w, bottom_left_h, bottom_left_reader = scaled_size(
            bottom_hazards[0]["icon_path"],
            max_w=min(150.0, (main_box_width / 2) - 30.0),
            max_h=main_box_height * 0.22,
        )
        bottom_right_w, bottom_right_h, bottom_right_reader = scaled_size(
            bottom_hazards[1]["icon_path"],
            max_w=min(150.0, (main_box_width / 2) - 30.0),
            max_h=main_box_height * 0.22,
        )

        # Optional gentle shrink for the pair.
        bottom_left_w *= 0.9
        bottom_left_h *= 0.9
        bottom_right_w *= 0.9
        bottom_right_h *= 0.9

        # Top icon centered near upper area.
        top_center_x = hazard_center_x
        top_icon_y = main_box_y + main_box_height - 40 - top_icon_h + 30
        overlay_canvas.drawImage(
            top_reader,
            top_center_x - (top_icon_w / 2),
            top_icon_y,
            width=top_icon_w,
            height=top_icon_h,
            preserveAspectRatio=True,
            mask="auto",
        )
        draw_caption_lines(
            hazard_center_x,
            max(top_icon_y - caption_gap, main_box_y + 14),
            top_hazard,
        )

        # Bottom row positions.
        row_y = main_box_y + 60 + max(bottom_left_h, bottom_right_h) + 30
        # Slightly widen horizontal spacing between the two bottom icons.
        x_offset = main_box_width * 0.22 + 7
        left_x = hazard_center_x - x_offset - (bottom_left_w / 2)
        right_x = hazard_center_x + x_offset - (bottom_right_w / 2)

        overlay_canvas.drawImage(
            bottom_left_reader,
            left_x,
            row_y - bottom_left_h,
            width=bottom_left_w,
            height=bottom_left_h,
            preserveAspectRatio=True,
            mask="auto",
        )
        draw_caption_lines(
            left_x + (bottom_left_w / 2),
            max(row_y - bottom_left_h - caption_gap, main_box_y + 10),
            bottom_hazards[0],
        )

        overlay_canvas.drawImage(
            bottom_right_reader,
            right_x,
            row_y - bottom_right_h,
            width=bottom_right_w,
            height=bottom_right_h,
            preserveAspectRatio=True,
            mask="auto",
        )
        draw_caption_lines(
            right_x + (bottom_right_w / 2),
            max(row_y - bottom_right_h - caption_gap, main_box_y + 10),
            bottom_hazards[1],
        )
    else:
        # Centered vertical stack for other counts.
        icon_entries = []
        effective_spacing = (
            -10 if count == 2 else spacing
        )  # tighten gap for two hazards
        slot_height = (main_box_height - 40 - (count - 1) * effective_spacing) / count
        slot_height = max(60, slot_height)

        for hazard_key, hazard in unique_hazards:
            icon_path = hazard["icon_path"]
            if not icon_path.exists():
                raise FileNotFoundError(f"Hazard icon not found at: {icon_path}")

            target_icon_width, target_icon_height, icon_reader = scaled_size(
                icon_path,
                max_w=min(160.0, main_box_width - 36.0),
                max_h=max(50.0, slot_height - caption_gap - caption_height),
            )

            if count == 2:
                target_icon_width *= 0.9
                target_icon_height *= 0.9

            icon_entries.append(
                {
                    "hazard": hazard,
                    "reader": icon_reader,
                    "width": target_icon_width,
                    "height": target_icon_height,
                }
            )

        total_height = (
            sum(
                entry["height"] + caption_gap + caption_height for entry in icon_entries
            )
            + (count - 1) * effective_spacing
        )
        group_bottom = main_box_y + (main_box_height - total_height) / 2
        current_y = group_bottom + total_height
        has_multiline = any(
            len(e["hazard"].get("lines") or [e["hazard"]["caption"]]) > 1
            for e in icon_entries
        )

        for idx, entry in enumerate(icon_entries):
            icon_w = entry["width"]
            icon_h = entry["height"]
            hazard = entry["hazard"]
            icon_reader = entry["reader"]

            icon_x = hazard_center_x - (icon_w / 2)
            icon_y = current_y - icon_h

            if count == 1:
                icon_y = min(icon_y + 30, main_box_y + main_box_height - icon_h - 4)
            elif count == 2:
                if idx == 0:
                    icon_y = min(icon_y + 40, main_box_y + main_box_height - icon_h - 4)
                else:
                    icon_y = max(main_box_y + 4, icon_y - 30)
                    if has_multiline:
                        icon_y = min(
                            icon_y + 10, main_box_y + main_box_height - icon_h - 4
                        )

            overlay_canvas.drawImage(
                icon_reader,
                icon_x,
                icon_y,
                width=icon_w,
                height=icon_h,
                preserveAspectRatio=True,
                mask="auto",
            )

            text_y = max(icon_y - caption_gap, main_box_y + 10)
            last_line_y = draw_caption_lines(hazard_center_x, text_y, hazard)

            current_y = last_line_y - effective_spacing

    # Draw obligation and prohibition signs (icons only) in a 2-column grid to the right box.
    combined_signs = unique_obligations + unique_prohibitions
    if combined_signs:
        combined_signs = combined_signs[:6]  # enforce max 6 total
        cols = 2
        margin_x = 12
        margin_y = 12
        cell_w = (obligation_box_width - margin_x * (cols + 1)) / cols
        target_size = min(80.0, cell_w)  # fixed size ~80pt
        rows = max(1, (len(combined_signs) + cols - 1) // cols)
        start_y = obligation_box_y + obligation_box_height - margin_y - target_size
        idx = 0
        for row in range(rows):
            y = start_y - row * (target_size + margin_y)
            for col in range(cols):
                if idx >= len(combined_signs):
                    break
                _, sign = combined_signs[idx]
                icon_path = sign["icon_path"]
                if not icon_path.exists():
                    idx += 1
                    continue
                icon_reader = ImageReader(str(icon_path))
                img_w, img_h = icon_reader.getSize()
                scale = target_size / max(img_w, img_h)
                draw_w = img_w * scale
                draw_h = img_h * scale
                x = (
                    obligation_box_x
                    + margin_x
                    + col * (cell_w + margin_x)
                    + (cell_w - draw_w) / 2
                )
                overlay_canvas.drawImage(
                    icon_reader,
                    x,
                    y,
                    width=draw_w,
                    height=draw_h,
                    preserveAspectRatio=True,
                    mask="auto",
                )
                idx += 1

    # Draw research group names centered in their slots (no rectangles).
    if research_groups is not None:
        groups = [g for g in research_groups if g]
        if groups:
            slot_w = research_row_width / 3
            rect_h = 36.0
            center_y = research_row_top - (research_row_height / 2) + 47.0
            line_spacing = 1.1
            font_name = "Helvetica"

            def wrap_text(text: str, font_size: float, max_width: float) -> List[str]:
                words = text.split()
                if not words:
                    return []
                lines: List[str] = []
                current = words[0]
                for word in words[1:]:
                    trial = current + " " + word
                    if (
                        overlay_canvas.stringWidth(trial, font_name, font_size)
                        <= max_width
                    ):
                        current = trial
                    else:
                        lines.append(current)
                        current = word
                lines.append(current)
                return lines

            count_groups = max(1, min(3, len(groups)))
            if count_groups == 1:
                widths = [research_row_width]
            elif count_groups == 2:
                widths = [
                    slot_w * 1.5,
                    slot_w * 1.5,
                ]  # split at center of second original cell
            else:
                widths = [slot_w, slot_w, slot_w]

            centers = []
            cursor_x = research_row_start_x
            for w in widths:
                centers.append(cursor_x + (w / 2))
                cursor_x += w

            # Slots fill only (no borders).
            rect_h = 34.0  # slightly shorter height
            overlay_canvas.setStrokeColorRGB(0, 0, 0)
            if count_groups == 1:
                rect_left = centers[0] - ((widths[0] + 20) / 2) - 16
                rect_width = widths[0] + 20
                # Neutral fill, no border
                overlay_canvas.setFillColorRGB(1, 1, 1)
                overlay_canvas.rect(
                    rect_left,
                    center_y - (rect_h / 2),
                    rect_width + 0.1,
                    rect_h + 1.1,
                    stroke=0,
                    fill=1,
                )
                rect_positions = [(rect_left, rect_width)]
            elif count_groups == 2:
                rect_positions = []
                for i in range(2):
                    adj_center = centers[i]
                    if i == 0:
                        adj_center -= 31
                    if i == 1:
                        adj_center -= 2
                    rect_width = widths[i] + 20
                    rect_left = adj_center - (rect_width / 2)
                    if i == 0:
                        rect_width += 4  # extend right
                    if i == 1:
                        rect_left -= 4  # extend left
                        rect_width += 5
                    rect_positions.append((rect_left, rect_width))
                    overlay_canvas.setFillColorRGB(1, 1, 1)
                    overlay_canvas.rect(
                        rect_left,
                        center_y - (rect_h / 2) + 0.1,
                        rect_width + 0.1,
                        rect_h + 1.1,
                        stroke=0,
                        fill=1,
                    )
            else:
                rect_positions = []
                for i in range(3):
                    left = centers[i] - (widths[i] / 2)
                    if i == 0:
                        left -= 42
                    if i == 1:
                        left -= 25
                    if i == 2:
                        left -= 8
                    rect_positions.append((left, widths[i] + 17))

            # Small vertical separator at the right edge of the first slot (only when 2 groups).
            if count_groups == 2 and rect_positions:
                first_left, first_width = rect_positions[0]
                right_x = first_left + first_width + 0.6
                overlay_canvas.setStrokeColorRGB(0, 0, 0)
                line_half = 18  # shorten by 3px total (37px length)
                overlay_canvas.line(
                    right_x,
                    center_y - line_half + 1,
                    right_x,
                    center_y + line_half + 1,
                )

            for i in range(count_groups):
                text = groups[i].strip()
                if not text:
                    continue
                rect_left, rect_width = (
                    rect_positions[i]
                    if i < len(rect_positions)
                    else (centers[i] - (widths[i] / 2), widths[i])
                )
                max_width = rect_width - 8
                font_size = 11.0
                overlay_canvas.setFillColorRGB(0, 0, 0)
                overlay_canvas.setFont(font_name, font_size)
                wrapped = wrap_text(text, font_size, max_width)
                max_lines_height = rect_h - 6
                while (
                    wrapped
                    and len(wrapped) * font_size * line_spacing > max_lines_height
                    and font_size > 7.0
                ):
                    font_size -= 0.5
                    overlay_canvas.setFont(font_name, font_size)
                    wrapped = wrap_text(text, font_size, max_width)
                if not wrapped:
                    continue
                overlay_canvas.setFont(font_name, font_size)
                total_height = len(wrapped) * font_size * line_spacing
                start_y = center_y + (total_height / 2) - (font_size * 0.8)
                center_x = rect_left + (rect_width / 2)
                for idx_line, line in enumerate(wrapped):
                    line_y = start_y - idx_line * font_size * line_spacing
                    overlay_canvas.drawCentredString(center_x, line_y, line)

    # Draw room number centered in a target box (no border)
    if room_number:
        overlay_canvas.setFont("Helvetica-Bold", 11)
        text_x = page_width - 42  # shift left
        # Move the room number text up by 30 pts
        text_y = research_row_top - (research_row_height / 2) + 36
        rect_w, rect_h = 30, 20
        rect_x = text_x - rect_w - 38  # expand left by 20
        rect_y = text_y - (rect_h / 2)
        rect_w += 65  # expand right by 20
        center_x = rect_x + rect_w / 2
        center_y = rect_y + rect_h / 2
        overlay_canvas.drawCentredString(center_x, center_y, room_number)
        # Contacts table entries
    contact_font = "Helvetica"
    contact_size = 11
    overlay_canvas.setFont(contact_font, contact_size)
    name_x = 180
    phone_x = page_width - 65  # shift phones 10 pts to the right
    # Laboratory contacts positioning (raised by 30 pts)
    row1_y = research_row_top - 35
    row_gap = 32
    # Move the second row down by an extra 70 pts (lifted up by 2 pts)
    row2_y = row1_y - row_gap + 10
    if pi_name:
        overlay_canvas.drawString(name_x, row1_y, pi_name)
    if pi_phone:
        overlay_canvas.drawRightString(phone_x, row1_y, pi_phone)
    if safety_name:
        overlay_canvas.drawString(name_x, row2_y, safety_name)
    if safety_phone:
        overlay_canvas.drawRightString(phone_x, row2_y, safety_phone)

    # Emergency contacts block: same layout, shifted down by 70 pts
    em_row1_y = row1_y - 95
    em_row2_y = row2_y - 95
    if emergency_name_1:
        overlay_canvas.drawString(name_x, em_row1_y, emergency_name_1)
    if emergency_phone_1:
        overlay_canvas.drawRightString(phone_x, em_row1_y, emergency_phone_1)
    if emergency_name_2:
        overlay_canvas.drawString(name_x, em_row2_y, emergency_name_2)
    if emergency_phone_2:
        overlay_canvas.drawRightString(phone_x, em_row2_y, emergency_phone_2)

    # Type of activity / Hazard class row (below emergency contacts)
    # Type of activity / Hazard class row (below emergency contacts)
    act_row_y = em_row2_y - 30  # raised by 10 pts
    start_x = 40
    total_w = page_width - 80
    gap = 10
    mid_x = start_x + (total_w * 0.5)

    # Draw two boxes without borders; text centered inside
    overlay_canvas.setFont("Helvetica", 11)
    rect_w = 150
    rect_h = 20
    offset_x = 140
    rect_y = act_row_y - 4.5
    rect_w_draw = rect_w - 20  # reduce width by 10 on the right
    left_box_x = start_x + offset_x - 40
    right_box_x = mid_x + offset_x - 12
    # No stroke to avoid borders
    overlay_canvas.rect(left_box_x, rect_y, rect_w_draw, rect_h, stroke=0, fill=0)
    overlay_canvas.rect(right_box_x, rect_y, rect_w_draw, rect_h, stroke=0, fill=0)
    if activity_type:
        overlay_canvas.drawCentredString(
            left_box_x + rect_w_draw / 2, rect_y + rect_h / 2 - 4, activity_type
        )
    if activity_hazard:
        overlay_canvas.drawCentredString(
            right_box_x + rect_w_draw / 2, rect_y + rect_h / 2 - 4, activity_hazard
        )

    # Finalize the single overlay page even if nothing was drawn.
    overlay_canvas.showPage()
    overlay_canvas.save()
    overlay_stream.seek(0)

    overlay_pdf = PdfReader(overlay_stream)
    overlay_page = overlay_pdf.pages[0]

    template_page.merge_page(overlay_page)

    writer = PdfWriter()
    writer.add_page(template_page)

    output_stream = BytesIO()
    writer.write(output_stream)
    output_stream.seek(0)
    first_hazard = unique_hazards[0][0] if unique_hazards else ""
    sanitized = (
        [rg.strip().replace(" ", "_") for rg in research_groups if rg.strip()]
        if research_groups
        else []
    )
    group_part = "_".join(sanitized) if sanitized else ""
    # Prefer research group names; if none, use selected risk; fallback to hazard or default.
    base_name = group_part or risk_key or first_hazard or "door_sheet"
    download_name = f"{base_name}.pdf"
    return output_stream, download_name


@app.route("/")
def index():
    hazard_options = []
    for key, value in sorted(HAZARDS.items(), key=lambda kv: kv[1]["label"].lower()):
        icon_name = value["icon_path"].name
        hazard_options.append(
            {
                "key": key,
                "label": value["label"],
                "icon": f"/static/hazards/{icon_name}",
                "info": HAZARD_INFO.get(key, value["caption"]),
            }
        )
    obligation_options = []
    for key, value in sorted(
        OBLIGATIONS.items(), key=lambda kv: kv[1]["label"].lower()
    ):
        icon_name = value["icon_path"].name
        obligation_options.append(
            {
                "key": key,
                "label": value["label"],
                "icon": f"/static/obligation_signs/{icon_name}",
                "info": value["caption"],
            }
        )
    prohibition_options = []
    for key, value in sorted(
        PROHIBITIONS.items(), key=lambda kv: kv[1]["label"].lower()
    ):
        icon_name = value["icon_path"].name
        prohibition_options.append(
            {
                "key": key,
                "label": value["label"],
                "icon": f"/static/prohibition_signs/{icon_name}",
                "info": PROHIBITION_INFO.get(key, value["caption"]),
            }
        )
    risk_options = [
        {
            "key": key,
            "label": value["label"],
            "title": "Minimal\nRisk" if key == "minimal" else value["label"],
            "info": RISK_INFO.get(key, value["label"]),
        }
        for key, value in RISK_TEMPLATES.items()
    ]
    return render_template(
        "index.html",
        hazards=hazard_options,
        obligations=obligation_options,
        prohibitions=prohibition_options,
        risks=risk_options,
    )


@app.route("/generate", methods=["POST"])
def generate():
    order_str = request.form.get("hazards_order", "")
    if order_str:
        hazard_keys = [h for h in order_str.split(",") if h]
    else:
        hazard_keys = [h.lower() for h in request.form.getlist("hazards") if h]
    obligations_order = request.form.get("obligations_order", "")
    obligation_keys = (
        [o for o in obligations_order.split(",") if o] if obligations_order else []
    )
    prohibitions_order = request.form.get("prohibitions_order", "")
    prohibition_keys = (
        [p for p in prohibitions_order.split(",") if p] if prohibitions_order else []
    )
    # Research groups: count comes from the dropdown, but we only keep non-empty names.
    department = (request.form.get("department") or "").strip()
    research_count = int((request.form.get("research_count") or "0").strip() or 0)
    research_names = [
        name.strip() for name in request.form.getlist("research_names") if name.strip()
    ]
    if research_count > 0:
        research_names = research_names[:research_count]
    room_number = (request.form.get("room_number") or "").strip()
    pi_name = (request.form.get("pi_name") or "").strip()
    pi_phone = (request.form.get("pi_phone") or "").strip()
    safety_name = (request.form.get("safety_name") or "").strip()
    safety_phone = (request.form.get("safety_phone") or "").strip()
    emergency_name_1 = (request.form.get("emergency_name_1") or "").strip()
    emergency_phone_1 = (request.form.get("emergency_phone_1") or "").strip()
    emergency_name_2 = (request.form.get("emergency_name_2") or "").strip()
    emergency_phone_2 = (request.form.get("emergency_phone_2") or "").strip()
    activity_type = (request.form.get("activity_type") or "").strip()
    activity_hazard = (request.form.get("activity_hazard") or "").strip()
    risk_key = (request.form.get("risk") or "").strip().lower()
    if not risk_key:
        # Fallback to the first configured risk if none was chosen.
        risk_key = next(iter(RISK_TEMPLATES))
    try:
        pdf_buffer, download_name = generate_hazard_pdf(
            hazard_keys,
            obligation_keys,
            prohibition_keys,
            risk_key,
            department,
            research_names,
            room_number,
            pi_name,
            pi_phone,
            safety_name,
            safety_phone,
            emergency_name_1,
            emergency_phone_1,
            emergency_name_2,
            emergency_phone_2,
            activity_type,
            activity_hazard,
        )
    except Exception as exc:  # pylint: disable=broad-except
        app.logger.exception("Failed to generate PDF")
        return f"Error generating PDF: {exc}", 500

    return send_file(
        pdf_buffer,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=download_name,
    )


if __name__ == "__main__":
    app.run(debug=True)
