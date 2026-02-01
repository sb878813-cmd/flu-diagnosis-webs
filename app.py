from flask import Flask, render_template, request, send_file
from reportlab.platypus import SimpleDocTemplate, Paragraph, Image, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
import uuid
from datetime import datetime

app = Flask(__name__)

def diagnose(data):
    probability = 0.25
    symptoms = data.getlist("symptoms")

    probability += 0.05 * len(symptoms)

    temp = float(data["temperature"])
    age = int(data["age"])
    sys_bp = int(data["sys_bp"])
    dia_bp = int(data["dia_bp"])

    if temp >= 100.4:
        probability += 0.15
        temp_status = "High Fever"
    elif temp >= 99:
        probability += 0.08
        temp_status = "Mild Fever"
    else:
        temp_status = "Normal"

    if sys_bp > 140 or dia_bp > 90:
        bp_status = "High BP"
    elif sys_bp < 90 or dia_bp < 60:
        bp_status = "Low BP"
    else:
        bp_status = "Normal BP"

    if age > 60:
        probability += 0.10

    probability = min(probability, 0.95)
    percent = int(probability * 100)

    if percent >= 70:
        risk = "HIGH RISK"
        meds = ["Paracetamol", "Antiviral (doctor prescribed)", "Fluids"]
    elif percent >= 40:
        risk = "MODERATE RISK"
        meds = ["Paracetamol", "Antihistamine", "Vitamin C"]
    else:
        risk = "LOW RISK"
        meds = ["Paracetamol (if needed)", "ORS", "Rest"]

    return percent, risk, temp_status, bp_status, meds


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        result = diagnose(request.form)
        return render_template("index.html", result=result)
    return render_template("index.html")


@app.route("/download", methods=["POST"])
def download():
    data = request.form
    percent, risk, temp_status, bp_status, meds = diagnose(data)

    filename = "Flu_Report.pdf"
    doc = SimpleDocTemplate(filename, pagesize=A4)
    styles = getSampleStyleSheet()
    content = []

    try:
        content.append(Image("hospital.png", width=80, height=80))
    except:
        pass

    content.append(Spacer(1, 10))
    content.append(Paragraph("<b>AI-Based Seasonal Flu Diagnostic Report</b>", styles["Title"]))
    content.append(Spacer(1, 10))

    content.append(Paragraph(f"<b>Report ID:</b> {uuid.uuid4().hex[:8]}", styles["Normal"]))
    content.append(Paragraph(f"<b>Date:</b> {datetime.now()}", styles["Normal"]))
    content.append(Spacer(1, 12))

    content.append(Paragraph(f"Patient Name: {data['name']}", styles["Normal"]))
    content.append(Paragraph(f"Age: {data['age']}", styles["Normal"]))
    content.append(Paragraph(f"Temperature Status: {temp_status}", styles["Normal"]))
    content.append(Paragraph(f"Blood Pressure Status: {bp_status}", styles["Normal"]))
    content.append(Paragraph(f"Risk Level: {risk}", styles["Normal"]))
    content.append(Spacer(1, 10))

    content.append(Paragraph("<b>Recommended Medication:</b>", styles["Heading2"]))
    for m in meds:
        content.append(Paragraph(f"- {m}", styles["Normal"]))

    content.append(Spacer(1, 20))
    content.append(Paragraph("<i>For academic demonstration purposes only.</i>", styles["Normal"]))

    doc.build(content)
    return send_file(filename, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)
