import json
import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from reportlab.pdfgen import canvas
from matplotlib import pyplot as plt
from textwrap import wrap
from datetime import datetime
output_dir = "output_reports"

def generate_reports(input_file_path, output_dir):
    logo_path = "https://soc2-compliance-check-reports-bucket.s3.us-east-1.amazonaws.com/gms.png" 
    os.makedirs(output_dir, exist_ok=True)
    
    # Define fonts and styles
    TITLE_FONT = ("Helvetica-Bold", 24)
    SECTION_HEADING_FONT = ("Helvetica-Bold", 18)
    SUBHEADING_FONT = ("Helvetica-Bold", 12)
    BODY_TEXT_FONT = ("Helvetica", 12)
    HEADER_FOOTER_FONT = ("Helvetica-Bold", 10)
        
    def generate_pdf_report_for_compliance_type(data, compliance_type, output_pdf_path):
        
        def add_header_footer(pdf, page_num):
            # Header with logo and title
            pdf.setFont(HEADER_FOOTER_FONT[0], HEADER_FOOTER_FONT[1])
            pdf.setFillColor(colors.HexColor("#085292"))
            pdf.drawImage(logo_path, 20, 745, width=70, height=35, mask='auto')
            pdf.drawString(500, 770, "Compliance Report")
            pdf.line(50, 730, 550, 730) 

            # Footer with page number
            pdf.setFont("Helvetica", 9)  # Light and clean font
            pdf.setFillColor(colors.black)
            
            # Footer content
            pdf.drawString(40, 40, f"Generated on: {datetime.now().strftime('%Y-%m-%d')}")
            pdf.drawCentredString(300, 40, "cloud@gmobility.com | www.gmobility.com")
            pdf.drawRightString(570, 40, f"Page {page_num}")
            
            # Divider line above footer
            pdf.setLineWidth(0.5)
            pdf.setStrokeColor(colors.black)
            pdf.line(40, 55, 570, 55)


        def add_title_page(pdf, findings_summary):
            # Title Page Layout
            pdf.setFillColor(colors.HexColor("#085292"))
            pdf.rect(0, 730, 620, 70, fill=True)  # Accent banner

            pdf.setFillColor(colors.white)
            pdf.setFont(TITLE_FONT[0], TITLE_FONT[1])
            pdf.drawCentredString(300, 750, "AWS Compliance Report 2025")  # Centered title

            # Compliance Type Subheading
            pdf.setFillColor(colors.HexColor("#EE751D"))
            pdf.setFont(SUBHEADING_FONT[0], 16)
            pdf.drawCentredString(300, 710, f"{compliance_type} Compliance Report")  # Subheading

            # Date of Report
            pdf.setFont(SUBHEADING_FONT[0], SUBHEADING_FONT[1])
            pdf.setFillColor(colors.HexColor("#085292"))
            pdf.drawString(50, 690, "Date of Report:")
            pdf.setFont(BODY_TEXT_FONT[0], BODY_TEXT_FONT[1])
            pdf.setFillColor(colors.black)
            pdf.drawString(170, 690, f"{datetime.now().strftime('%Y-%m-%d')}")

            # Divider below Date
            pdf.setFillColor(colors.HexColor("#085292"))
            pdf.rect(40, 675, 520, 3, fill=True)

            # Summary Subheading
            pdf.setFont(SUBHEADING_FONT[0], 16)
            pdf.setFillColor(colors.HexColor("#085292"))
            pdf.drawString(50, 650, "Summary of Findings:")

            # Summary Table
            table_data = [
                ["Metric", "Value"],
                ["Total Checks", findings_summary["Total Findings"]],
                ["Passed", findings_summary["Passed"]],
                ["Failed", findings_summary["Failed"]],
                ["Compliance (%)", f"{findings_summary['Passed'] / findings_summary['Total Findings'] * 100:.2f}%"],
            ]

            table = Table(table_data, colWidths=[250, 200])
            table_style = TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EE751D")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 12),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
                ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
                ("TEXTCOLOR", (0, 1), (-1, -1), colors.black),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ])
            table.setStyle(table_style)
            table.wrapOn(pdf, 50, 490)
            table.drawOn(pdf, 50, 550)

            # Divider below table
            pdf.setFillColor(colors.HexColor("#085292"))
            pdf.rect(40, 540, 520, 3, fill=True)

            # Title for Donut Chart
            pdf.setFont(SUBHEADING_FONT[0], 16)
            pdf.setFillColor(colors.HexColor("#085292"))
            pdf.drawCentredString(140, 500, "Compliance Distribution:")

            # Enhanced Donut Chart
            donut_chart_path = "compliance_donut_chart.png"
            generate_donut_chart(findings_summary, donut_chart_path)
            pdf.drawImage(donut_chart_path, 130, 150, width=350, height=350)  # Adjusted donut chart size and placement
            os.remove(donut_chart_path)

            pdf.setFillColor(colors.HexColor("#085292"))
            pdf.rect(40, 55, 520, 3, fill=True)

        def generate_donut_chart(findings_summary, chart_path):
            labels = ["Passed", "Failed"]
            sizes = [findings_summary["Passed"], findings_summary["Failed"]]
            colors = ["#4CAF50", "#F44336"]  # Green and red for pass and fail
            explode = (0.1, 0)  # Slightly "explode" the passed section for emphasis

            plt.figure(figsize=(5, 5))  # Adjusted figure size for better layout
            plt.pie(
                sizes,
                labels=labels,
                autopct='%1.1f%%',
                startangle=140,
                colors=colors,
                explode=explode,
                textprops={'fontsize': 12, 'color': "black"},  # Enhanced readability
                wedgeprops={'edgecolor': 'black', 'linewidth': 1.5},  # Cleaner edges
            )
            plt.savefig(chart_path, bbox_inches="tight")
            plt.close()
            
        def add_resource_finding(pdf, y_position, resource_counter, finding):
            # Extract finding details
            resource_id = finding.get("resources", [{}])[0].get("name", "No Resource ID")
            region = finding.get("cloud", {}).get("region", "Unknown")
            title = finding.get("finding_info", {}).get("title", "No Title")
            status_code = finding.get("status_code", "Unknown").upper()
            recommendations = finding.get("remediation", {}).get("references", [])

            # Present findings in order: Resource, Region, Check, Status, Recommendation
            pdf.setFont("Helvetica-Bold", 12)
            pdf.setFillColor(colors.HexColor("#085292"))
            wrapped_id = wrap_text(f"{resource_counter}. Resource ID: {resource_id}")
            for line in wrapped_id:
                pdf.drawString(40, y_position, line)
                y_position -= 15

            pdf.setFont(BODY_TEXT_FONT[0], BODY_TEXT_FONT[1])
            pdf.setFillColor(colors.black)
            pdf.drawString(60, y_position, f"● Region: {region}")
            y_position -= 15

            wrapped_check = wrap_text(f"● Check: {title}")
            for line in wrapped_check:
                pdf.drawString(60, y_position, line)
                y_position -= 15

            # Color-coded status
            if status_code == "PASS":
                status_color = colors.HexColor("#4CAF50")  # Green for Pass
                status_icon = "✔️"
            elif status_code == "FAIL":
                status_color = colors.HexColor("#F44336")  # Red for Fail
                status_icon = "❌"
            else:
                status_color = colors.HexColor("#FFC107")  # Yellow for Manual
                status_icon = "🕒"

            pdf.setFillColor(status_color)
            pdf.drawString(60, y_position, f"● Status: {status_icon} {status_code}")
            y_position -= 15

            # Recommendations
            pdf.setFillColor(colors.black)
            for rec in recommendations:
                wrapped_recommendation = wrap_text(f"● Recommendation: {rec}")
                for line in wrapped_recommendation:
                    pdf.drawString(60, y_position, line)
                    y_position -= 15

            return y_position - 10

        
        def add_service_findings(pdf, service, findings, page_num):
            pdf.showPage()
            add_header_footer(pdf, page_num)
            pdf.setFont(SECTION_HEADING_FONT[0], SECTION_HEADING_FONT[1])
            pdf.setFillColor(colors.HexColor("#085292"))
            pdf.drawCentredString(300, 740, service.upper())
            pdf.line(50, 730, 550, 730)  # Divider

            y_position = 700
            resource_counter = 1
            for finding in findings:
                if y_position < 270:
                    pdf.showPage()
                    page_num += 1
                    add_header_footer(pdf, page_num)
                    y_position = 700
                y_position = add_resource_finding(pdf, y_position, resource_counter, finding)
                resource_counter += 1
            return page_num

        def wrap_text(text, width=70):
            return wrap(text, width=width)

        with open(input_file_path, "r") as json_file:
            data = json.load(json_file)

        findings_by_service = {}
        findings_summary = {"Total Findings": 0, "Passed": 0, "Failed": 0}
        for finding in data:
            service_name = finding.get("resources", [{}])[0].get("group", {}).get("name", "Unknown Service").capitalize()
            findings_by_service.setdefault(service_name, []).append(finding)
            findings_summary["Total Findings"] += 1
            if finding.get("status_code", "").upper() == "PASS":
                findings_summary["Passed"] += 1
            elif finding.get("status_code", "").upper() == "FAIL":
                findings_summary["Failed"] += 1

        pdf = canvas.Canvas(output_pdf_path, pagesize=letter)
        pdf.setTitle("Compliance Assessment Report")
        add_title_page(pdf, findings_summary)

        page_num = 1
        for service, findings in findings_by_service.items():
            page_num = add_service_findings(pdf, service, findings, page_num)

        for service, findings in findings_by_service.items():
            pdf.showPage()
            page_num += 1
            add_header_footer(pdf, page_num)
            pdf.setFont(SECTION_HEADING_FONT[0], SECTION_HEADING_FONT[1])
            pdf.setFillColor(colors.HexColor("#085292"))
            pdf.drawCentredString(300, 740, service.upper())
            pdf.setStrokeColor(colors.HexColor("#085292"))
            pdf.setLineWidth(1)
            pdf.line(50, 730, 550, 730)  # Divider below the service heading

            y_position = 700
            pdf.setFont(BODY_TEXT_FONT[0], BODY_TEXT_FONT[1])
            resource_counter = 1

            for finding in findings:
                if y_position < 270:  # Create a new page if space is insufficient
                    pdf.showPage()
                    page_num += 1
                    add_header_footer(pdf, page_num)
                    y_position = 700

                # Extract finding details
                resource_id = finding.get("resources", [{}])[0].get("name", "No Resource ID")
                region = finding.get("cloud", {}).get("region", "Unknown")
                title = finding.get("finding_info", {}).get("title", "No Title")
                status_code = finding.get("status_code", "Unknown").upper()
                recommendations = finding.get("remediation", {}).get("references", [])

                # Present findings in order: Resource, Region, Check, Status, Recommendation
                pdf.setFont("Helvetica-Bold", 12)
                pdf.setFillColor(colors.HexColor("#EE751D"))
                wrapped_id = wrap_text(f"{resource_counter}. Resource: {resource_id}")
                for line in wrapped_id:
                    pdf.drawString(40, y_position, line)
                    y_position -= 15

                pdf.setFont(BODY_TEXT_FONT[0], BODY_TEXT_FONT[1])
                pdf.setFillColor(colors.black)
                pdf.drawString(60, y_position, f"● Region: {region}")
                y_position -= 15

                pdf.drawString(60, y_position, f"● Check: {title}")
                y_position -= 15

                status_color = colors.red if status_code == "FAIL" else colors.HexColor("#085292")
                pdf.setFillColor(status_color)
                pdf.drawString(60, y_position, f"● Status: {status_code}")
                y_position -= 15

                pdf.setFillColor(colors.black)
                for rec in recommendations:
                    wrapped_recommendation = wrap_text(f"● Recommendation: {rec}")
                    for line in wrapped_recommendation:
                        pdf.drawString(60, y_position, line)
                        y_position -= 15

                resource_counter += 1
                y_position -= 10

        pdf.save()
        """Generate a PDF report for a specific compliance type."""
        filtered_findings = [
            finding for finding in data if compliance_type in finding.get("unmapped", {}).get("compliance", {})
        ]

        if not filtered_findings:
            return  # Skip if no findings for the compliance type

        findings_summary = {
            "Total Findings": len(filtered_findings),
            "Passed": sum(1 for finding in filtered_findings if finding.get("status_code", "").upper() == "PASS"),
            "Failed": sum(1 for finding in filtered_findings if finding.get("status_code", "").upper() == "FAIL"),
        }

        pdf = canvas.Canvas(output_pdf_path, pagesize=letter)
        pdf.setTitle(f"{compliance_type} Compliance Report")
        add_title_page(pdf, findings_summary)

        findings_by_service = {}
        for finding in filtered_findings:
            service_name = finding.get("resources", [{}])[0].get("group", {}).get("name", "Unknown Service").capitalize()
            findings_by_service.setdefault(service_name, []).append(finding)

        page_num = 1
        for service, findings in findings_by_service.items():
            pdf.showPage()
            add_header_footer(pdf, page_num)
            pdf.setFont("Helvetica-Bold", 18)
            pdf.setFillColor(colors.HexColor("#085292"))
            pdf.drawCentredString(300, 740, service.upper())
            pdf.line(50, 730, 550, 730)

            y_position = 700
            resource_counter = 1

            for finding in findings:
                if y_position < 270:  # Create a new page if space is insufficient
                    pdf.showPage()
                    page_num += 1
                    add_header_footer(pdf, page_num)
                    y_position = 700

                y_position = add_resource_finding(pdf, y_position, resource_counter, finding)
                resource_counter += 1

        pdf.save()

    """Generate separate PDF reports for each compliance type."""
    with open(input_file_path, "r") as json_file:
        data = json.load(json_file)

    all_compliance_types = set()
    for finding in data:
        compliance_data = finding.get("unmapped", {}).get("compliance", {})
        all_compliance_types.update(compliance_data.keys())

    for compliance_type in all_compliance_types:
        sanitized_name = compliance_type.replace('-', '_')  # Replace hyphens with underscores
        output_pdf_path = os.path.join(output_dir, f"{sanitized_name}_Compliance_Report.pdf")
        generate_pdf_report_for_compliance_type(data, compliance_type, output_pdf_path)

# Entry Point
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <input_json_file>")
        sys.exit(1)

    input_json_file = sys.argv[1]
    generate_reports(input_json_file,output_dir)