from datetime import datetime
import os
from django.conf import settings
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
            "least_accurate": None,
            "summary": "",
            "ranking": [],
            "total_successful": 0,
            "total_failed": 0,
            "success_rate": 0
        }

        # Filtrar métodos exitosos con errores numéricos
        valid_methods = [m for m in methods if m["status"] == "Exitoso" and isinstance(m["error"], (int, float))]
        
        # Contar métodos exitosos y fallidos
        successful_methods = [m for m in methods if m["status"] == "Exitoso"]
        failed_methods = [m for m in methods if m["status"] == "Error"]
        
        analysis["total_successful"] = len(successful_methods)
        analysis["total_failed"] = len(failed_methods)
        analysis["success_rate"] = (len(successful_methods) / len(methods)) * 100 if methods else 0

        if not valid_methods:
            analysis["summary"] = "Ningún método produjo resultados válidos para comparar."
            return analysis

        # Ordenar por error (menor error = mejor)
        sorted_methods = sorted(valid_methods, key=lambda x: abs(x["error"]))
        
        # Identificar el mejor y peor método
        most_accurate = sorted_methods[0]
        least_accurate = sorted_methods[-1] if len(sorted_methods) > 1 else None
        
        analysis["most_accurate"] = most_accurate["method"]
        analysis["least_accurate"] = least_accurate["method"] if least_accurate else None
        
        # Crear ranking completo
        analysis["ranking"] = [
            {
                "position": i + 1,
                "method": method["method"],
                "error": method["error"],
                "polynomial": method["polynomial"]
            }
            for i, method in enumerate(sorted_methods)
        ]
        
        # Generar resumen detallado
        if len(valid_methods) == 1:
            analysis["summary"] = f"Solo {most_accurate['method']} produjo resultados válidos con un error de {most_accurate['error']:.2e}."
        else:
            error_diff = abs(least_accurate["error"]) - abs(most_accurate["error"])
            analysis["summary"] = f"El método más preciso fue {most_accurate['method']} con un error de {most_accurate['error']:.2e}. "
            analysis["summary"] += f"El menos preciso fue {least_accurate['method']} con un error de {least_accurate['error']:.2e}. "
            analysis["summary"] += f"Diferencia: {error_diff:.2e}."

        return analysis

    def generate_pdf_report(self, comparison_data, form_data):
        filename = f"reporte_interpolacion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        # CORREGIDO: Usar la ruta correcta de Django
        static_reports_dir = os.path.join(settings.STATICFILES_DIRS[0], "reports")
        os.makedirs(static_reports_dir, exist_ok=True)
        
        filepath = os.path.join(static_reports_dir, filename)

        doc = SimpleDocTemplate(filepath, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []

        title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=18, spaceAfter=30, alignment=1)
        story.append(Paragraph("INFORME COMPARATIVO DE MÉTODOS DE INTERPOLACIÓN", title_style))
        story.append(Spacer(1, 12))

        story.append(Paragraph("DATOS DE ENTRADA", styles['Heading2']))
        data_info = [
            ["Parámetro", "Valor"],
            ["Puntos x", str(form_data.get("x_values", "N/A"))],
            ["Puntos y", str(form_data.get("y_values", "N/A"))],
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
            
            # Resumen general
            story.append(Paragraph(f"<b>Métodos exitosos:</b> {analysis['total_successful']}/{analysis['total_successful'] + analysis['total_failed']}", styles['Normal']))
            story.append(Paragraph(f"<b>Tasa de éxito:</b> {analysis['success_rate']:.1f}%", styles['Normal']))
            story.append(Spacer(1, 12))
            
            if analysis.get("most_accurate"):
                story.append(Paragraph(f"<b>Método más preciso:</b> {analysis['most_accurate']}", styles['Normal']))
                if analysis.get("least_accurate"):
                    story.append(Paragraph(f"<b>Método menos preciso:</b> {analysis['least_accurate']}", styles['Normal']))
                story.append(Spacer(1, 12))
            
            # Ranking de métodos
            if analysis.get("ranking"):
                story.append(Paragraph("<b>Ranking de Precisión:</b>", styles['Normal']))
                ranking_data = [["Posición", "Método", "Error"]]
                for rank in analysis["ranking"]:
                    ranking_data.append([
                        str(rank["position"]),
                        rank["method"],
                        f"{rank['error']:.2e}"
                    ])
                
                ranking_table = Table(ranking_data)
                ranking_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(ranking_table)
                story.append(Spacer(1, 12))
            
            story.append(Paragraph("<b>Conclusión:</b>", styles['Normal']))
            story.append(Paragraph(analysis.get("summary", "No se pudo realizar el análisis."), styles['Normal']))

        try:
            doc.build(story)
            # CORREGIDO: Retornar solo el nombre del archivo
            return filename
        except Exception as e:
            print(f"Error generando PDF: {e}")
            return None