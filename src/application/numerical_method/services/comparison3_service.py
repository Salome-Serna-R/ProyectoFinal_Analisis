from datetime import datetime
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer


class Comparison3Service:

    def create_comparison(self, results_dict, validations, x_values=None, y_values=None):
        comparison = {
            "methods": [],
            "has_valid_results": False,
            "analysis": {}
        }
        if not validations.get("formato", {}).get("valid", True):
            comparison["methods"].append({
                "method": "Error de formato",
                "status": "Error",
                "polynomial": "N/A",
                "error": "N/A",
                "message": validations["formato"]["message"]
            })
            return comparison

        if not validations.get("longitud", {}).get("valid", True):
            comparison["methods"].append({
                "method": "Error de longitud",
                "status": "Error",
                "polynomial": "N/A",
                "error": "N/A",
                "message": validations["longitud"]["message"]
            })
            return comparison

        for name, result in results_dict.items():
            if result is None:
                self._append_method(name, None, comparison)
            else:
                self._append_method(name, result, comparison)

        if comparison["methods"]:
            analysis = self._analyze_results(comparison["methods"])
            comparison["analysis"] = analysis
            comparison["has_valid_results"] = analysis.get("most_accurate") is not None

        return comparison

    

    def _append_method(self, name, result, comparison):
        if result and result.get("is_successful"):
            comparison["methods"].append({
                "method": name,
                "status": "Exitoso",
                "polynomial": result.get("polynomial", "N/A"),
                "error": result.get("error", "N/A"),
                "message": result.get("message_method", "")
            })
            comparison["has_valid_results"] = True
        else:
            comparison["methods"].append({
                "method": name,
                "status": "Error",
                "polynomial": "N/A",
                "error": "N/A",
                "message": result.get("message_method", "Fallo en la ejecución") if result else "Resultado inválido"
            })

    def _analyze_results(self, methods):
        analysis = {
            "most_accurate": None,
            "summary": ""
        }

        valid_methods = [m for m in methods if isinstance(m["error"], (int, float))]

        if not valid_methods:
            analysis["summary"] = "Ningún método produjo resultados válidos."
            return analysis

        most_accurate = min(valid_methods, key=lambda x: abs(x["error"]))
        analysis["most_accurate"] = most_accurate["method"]
        analysis["summary"] = f"El método más preciso fue {most_accurate['method']} con un error de {most_accurate['error']:.2e}."

        return analysis

    def generate_pdf_report(self, comparison_data, form_data):
        filename = f"reporte_interpolacion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join("static", "reports", filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        doc = SimpleDocTemplate(filepath, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []

        title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=18, spaceAfter=30, alignment=1)
        story.append(Paragraph("INFORME COMPARATIVO DE MÉTODOS DE INTERPOLACIÓN", title_style))
        story.append(Spacer(1, 12))

        story.append(Paragraph("DATOS DE ENTRADA", styles['Heading2']))
        data_info = [
            ["Parámetro", "Valor"],
            ["Puntos x", str(form_data.get("x_values_raw", "N/A"))],
            ["Puntos y", str(form_data.get("y_values_raw", "N/A"))],
        ]
        data_table = Table(data_info)
        data_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(data_table)
        story.append(Spacer(1, 20))

        story.append(Paragraph("RESULTADOS COMPARATIVOS", styles['Heading2']))
        results = [["Método", "Estado", "Polinomio", "Error"]]
        for method in comparison_data["methods"]:
            err_str = f"{method['error']:.2e}" if isinstance(method["error"], (int, float)) else str(method["error"])
            results.append([
                method["method"],
                method["status"],
                method["polynomial"],
                err_str
            ])
        table = Table(results)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(table)
        story.append(Spacer(1, 20))

        if comparison_data.get("analysis") and comparison_data["has_valid_results"]:
            story.append(Paragraph("ANÁLISIS COMPARATIVO", styles['Heading2']))
            analysis = comparison_data["analysis"]
            if analysis.get("most_accurate"):
                story.append(Paragraph(f"<b>Método más preciso:</b> {analysis['most_accurate']}", styles['Normal']))
            story.append(Spacer(1, 12))
            story.append(Paragraph("<b>Conclusión:</b>", styles['Normal']))
            story.append(Paragraph(analysis.get("summary", "No se pudo realizar el análisis."), styles['Normal']))

        doc.build(story)
        return filename
