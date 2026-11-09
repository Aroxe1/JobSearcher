#!/usr/bin/env python3
"""Write job offers to an .xlsx file. Standard library only (no pip install needed).

Usage:
    python export_offers.py offers.json output.xlsx [--sheet "Offres"]

offers.json is a list of objects, one per offer. The keys of the first object
(written in the user's language) become the column headers, in that order.
Values starting with http:// or https:// become clickable links.
"""
import argparse
import json
import re
import sys
import zipfile
from xml.sax.saxutils import escape

MAIN = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PKG = "http://schemas.openxmlformats.org/package/2006/relationships"


def clean(value):
    """Text safe for XML (control characters are invalid in .xlsx)."""
    text = "" if value is None else str(value)
    return re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", text)


def col_letter(index):
    letters, n = "", index + 1
    while n:
        n, rem = divmod(n - 1, 26)
        letters = chr(65 + rem) + letters
    return letters


def cell(ref, value, style=0):
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return f'<c r="{ref}"><v>{value}</v></c>'
    text = clean(value)
    # Excel's HYPERLINK() caps strings at 255 chars; longer URLs stay plain text.
    if text.startswith(("http://", "https://")) and len(text) <= 255:
        formula = escape(text.replace('"', '""'))
        return f'<c r="{ref}" t="str" s="2"><f>HYPERLINK("{formula}","{formula}")</f><v>{escape(text)}</v></c>'
    s = f' s="{style}"' if style else ""
    return f'<c r="{ref}" t="inlineStr"{s}><is><t xml:space="preserve">{escape(text)}</t></is></c>'


def sheet_name(name):
    name = re.sub(r"[\[\]:*?/\\]", " ", name).strip()[:31]
    return name or "Sheet1"


def build(rows, name):
    headers = list(rows[0].keys()) if rows else ["(empty)"]
    for row in rows[1:]:  # keep columns that only appear in later rows
        headers += [k for k in row if k not in headers]

    widths = [len(h) for h in headers]
    lines = ['<row r="1">' + "".join(cell(f"{col_letter(i)}1", h, 1) for i, h in enumerate(headers)) + "</row>"]
    for r, row in enumerate(rows, start=2):
        cells = []
        for i, h in enumerate(headers):
            value = row.get(h, "")
            widths[i] = max(widths[i], len(clean(value)))
            cells.append(cell(f"{col_letter(i)}{r}", value))
        lines.append(f'<row r="{r}">' + "".join(cells) + "</row>")

    last = f"{col_letter(len(headers) - 1)}{max(len(rows), 1) + 1}"
    cols = "".join(
        f'<col min="{i + 1}" max="{i + 1}" width="{min(w + 2, 60)}" customWidth="1"/>' for i, w in enumerate(widths)
    )
    sheet = (
        f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><worksheet xmlns="{MAIN}">'
        '<sheetViews><sheetView workbookViewId="0"><pane ySplit="1" topLeftCell="A2" activePane="bottomLeft" state="frozen"/>'
        "</sheetView></sheetViews>"
        f"<cols>{cols}</cols><sheetData>{''.join(lines)}</sheetData>"
        f'<autoFilter ref="A1:{last}"/></worksheet>'
    )
    quoted = "'" + escape(name).replace("'", "''") + "'"
    abs_last = "$" + re.sub(r"(\d+)", r"$\1", last)
    workbook = (
        f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><workbook xmlns="{MAIN}" xmlns:r="{REL}">'
        f'<sheets><sheet name="{escape(name)}" sheetId="1" r:id="rId1"/></sheets>'
        f'<definedNames><definedName name="_xlnm._FilterDatabase" localSheetId="0" hidden="1">{quoted}!$A$1:{abs_last}</definedName></definedNames>'
        "</workbook>"
    )
    styles = (
        f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><styleSheet xmlns="{MAIN}">'
        '<fonts count="3"><font><sz val="11"/><name val="Calibri"/></font>'
        '<font><b/><sz val="11"/><name val="Calibri"/></font>'
        '<font><u/><sz val="11"/><color rgb="FF0563C1"/><name val="Calibri"/></font></fonts>'
        '<fills count="2"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill></fills>'
        '<borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders>'
        '<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>'
        '<cellXfs count="3"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>'
        '<xf numFmtId="0" fontId="1" fillId="0" borderId="0" xfId="0" applyFont="1"/>'
        '<xf numFmtId="0" fontId="2" fillId="0" borderId="0" xfId="0" applyFont="1"/></cellXfs>'
        '<cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles></styleSheet>'
    )
    return {
        "[Content_Types].xml": (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
            '<Default Extension="xml" ContentType="application/xml"/>'
            '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
            '<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
            '<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>'
            "</Types>"
        ),
        "_rels/.rels": (
            f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="{PKG}">'
            f'<Relationship Id="rId1" Type="{REL}/officeDocument" Target="xl/workbook.xml"/></Relationships>'
        ),
        "xl/_rels/workbook.xml.rels": (
            f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="{PKG}">'
            f'<Relationship Id="rId1" Type="{REL}/worksheet" Target="worksheets/sheet1.xml"/>'
            f'<Relationship Id="rId2" Type="{REL}/styles" Target="styles.xml"/></Relationships>'
        ),
        "xl/workbook.xml": workbook,
        "xl/worksheets/sheet1.xml": sheet,
        "xl/styles.xml": styles,
    }


def main():
    parser = argparse.ArgumentParser(description="Write job offers (JSON list of objects) to .xlsx")
    parser.add_argument("offers_json")
    parser.add_argument("output_xlsx")
    parser.add_argument("--sheet", default="Offers", help="worksheet name, in the user's language")
    args = parser.parse_args()
    with open(args.offers_json, encoding="utf-8") as f:
        rows = json.load(f)
    if not isinstance(rows, list) or not all(isinstance(r, dict) for r in rows):
        sys.exit("offers.json must be a list of objects")
    with zipfile.ZipFile(args.output_xlsx, "w", zipfile.ZIP_DEFLATED) as z:
        for path, xml in build(rows, sheet_name(args.sheet)).items():
            z.writestr(path, xml)
    print(f"Wrote {len(rows)} offers to {args.output_xlsx}")


if __name__ == "__main__":
    main()
