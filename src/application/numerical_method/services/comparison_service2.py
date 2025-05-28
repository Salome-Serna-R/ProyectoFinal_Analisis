from datetime import datetime
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer


class ComparisonService:

    def create_comparison(self, gauss_result, jacobi_result, sor_result, gauss_validation, jacobi_validation, sor_validation):
        comparison = {
            "methods": [],
            "analysis": {},
            "has_valid_results": False
        }

        self._append_method("Gauss-Seidel", gauss_result, gauss_validation, comparison)
        self._append_method("Jacobi", jacobi_result, jacobi_validation, comparison)
        self._append_method("SOR", sor_result, sor_validation, comparison)

        if comparison["has_valid_results"]:
            comparison["analysis"] = self._analyze_results(comparison["methods"])

        return comparison

    def _append_method(self, name, result, validation, comparison):
        if result and result.get("is_successful"):
            comparison["methods"].append(self._process_result(name, result))
            if result.get("have_solution"):
                comparison["has_valid_results"] = True
        elif validation != True:
            comparison["methods"].append({
                "method": name,
                "status": "Error de validación",
                "error": validation,
                "iterations": "N/A",
                "solution": "N/A",
                "final_error": "N/A"
            })

    def _process_result(self, method_name, result):
        iterations = len(result.get("table", {}))
        last = result["table"].get(iterations, {})
        final_error = last.get("Error", "N/A")

        return {
            "method": method_name,
            "status": "Exitoso" if result.get("have_solution") else "Sin convergencia",
            "iterations": iterations,
            "solution": result.get("solution", "N/A"),
            "final_error": final_error,
            "message": result.get("message_method", ""),
            "have_solution": result.get("have_solution", False)
        }

    def _analyze_results(self, methods):
        analysis = {
            "most_efficient": None,
            "most_accurate": None,
            "best_overall": None,
            "summary": ""
        }

        successful = [m for m in methods if m["have_solution"]]

        if not successful:
            analysis["summary"] = "Ningún método encontró una solución válida."
            return analysis

        analysis["most_efficient"] = min(successful, key=lambda x: x["iterations"])["method"]

        with_error = [m for m in successful if isinstance(m["final_error"], (int, float))]
        if with_error:
            analysis["most_accurate"] = min(with_error, key=lambda x: abs(x["final_error"]))["method"]

        if len(successful) == 1:
            analysis["best_overall"] = successful[0]["method"]
            analysis["summary"] = f"Solo {successful[0]['method']} encontró una solución válida."
        else:
            scores = {m["method"]: 0 for m in successful}
            scores[analysis["most_efficient"]] += 2
            if analysis.get("most_accurate"):
                scores[analysis["most_accurate"]] += 2
            best = max(scores, key=scores.get)
            analysis["best_overall"] = best
            if analysis["most_efficient"] == analysis["most_accurate"]:
                analysis["summary"] = f"{best} fue el más eficiente y preciso."
            else:
                analysis["summary"] = (
                    f"El más eficiente fue {analysis['most_efficient']} y el más preciso fue {analysis['most_accurate']}. "
                    f"Se recomienda usar {best}."
                )

        return analysis

    def generate_pdf_report(self, comparison_data, form_data):
        filename = f"reporte_comparativo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join("static", "reports", filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        doc = SimpleDocTemplate(filepath, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []

        title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=18, spaceAfter=30, alignment=1)
        story.append(Paragraph("INFORME COMPARATIVO DE MÉTODOS DE SISTEMAS LINEALES", title_style))
        story.append(Spacer(1, 12))

        story.append(Paragraph("DATOS DE ENTRADA", styles['Heading2']))
        data_info = [
            ["Parámetro", "Valor"],
            ["Matriz A", form_data.get("matrix_a_raw", "N/A")],
            ["Vector b", form_data.get("vector_b_raw", "N/A")],
            ["x0", form_data.get("initial_guess_raw", "N/A")],
            ["Tolerancia", str(form_data.get("tolerance"))],
            ["Máx. iteraciones", str(form_data.get("max_iterations"))],
            ["T. precisión", str(form_data.get("precision_type", "N/A"))],
            ["w (SOR)", str(form_data.get("relaxation_factor", "N/A"))]
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
        results = [["Método", "Estado", "Iteraciones", "Solución", "Error final"]]
        for method in comparison_data["methods"]:
            sol_str = ", ".join(f"{v:.4f}" for v in method["solution"]) if isinstance(method["solution"], list) else str(method["solution"])
            err_str = f"{method['final_error']:.2e}" if isinstance(method["final_error"], (int, float)) else str(method["final_error"])
            results.append([
                method["method"],
                method["status"],
                str(method["iterations"]),
                sol_str,
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
            for key in ["most_efficient", "most_accurate", "best_overall"]:
                if analysis.get(key):
                    story.append(Paragraph(f"<b>{key.replace('_', ' ').capitalize()}:</b> {analysis[key]}", styles['Normal']))
            story.append(Spacer(1, 12))
            story.append(Paragraph("<b>Conclusión:</b>", styles['Normal']))
            story.append(Paragraph(analysis.get("summary", "No se pudo realizar el análisis."), styles['Normal']))

        doc.build(story)
        return filename
