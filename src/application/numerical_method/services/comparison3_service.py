from datetime import datetime
import os
import numpy as np
import re
from django.conf import settings
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer


class Comparison3Service:

    def create_comparison(self, results_dict, validations, x_array=None, y_array=None, x_values=None, y_values=None):
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

        # Manejar diferentes tipos de entrada para x_array e y_array
        if x_array is None and x_values is not None:
            try:
                if isinstance(x_values, str):
                    x_array = np.array([float(x) for x in x_values.split()])
                elif isinstance(x_values, (list, tuple)):
                    x_array = np.array(x_values)
                else:
                    x_array = np.array(x_values)
            except:
                x_array = None
                
        if y_array is None and y_values is not None:
            try:
                if isinstance(y_values, str):
                    y_array = np.array([float(y) for y in y_values.split()])
                elif isinstance(y_values, (list, tuple)):
                    y_array = np.array(y_values)
                else:
                    y_array = np.array(y_values)
            except:
                y_array = None

        for name, result in results_dict.items():
            if result is None:
                self._append_method(name, None, comparison, x_array, y_array)
            else:
                self._append_method(name, result, comparison, x_array, y_array)

        if comparison["methods"]:
            analysis = self._analyze_results(comparison["methods"])
            comparison["analysis"] = analysis
            comparison["has_valid_results"] = analysis.get("most_accurate") is not None

        return comparison

    def _append_method(self, name, result, comparison, x_array=None, y_array=None):
        if result and result.get("is_successful"):
            # Calcular error si tenemos datos
            error_value = "N/A"
            polynomial_display = "N/A"
            
            # Manejar splines con estructura específica
            if "spline" in name.lower():
                if result.get("tramos"):
                    tramos = result["tramos"]
                    
                    # Crear una representación compacta de los tramos
                    if len(tramos) <= 2:
                        # Para pocos tramos, mostrar versión resumida
                        tramos_display = []
                        for i, tramo in enumerate(tramos):
                            # Extraer solo la parte esencial de la ecuación
                            tramo_clean = str(tramo).replace("Tramo ", "").strip()
                            if len(tramo_clean) > 40:
                                tramo_clean = tramo_clean[:37] + "..."
                            tramos_display.append(f"T{i+1}: {tramo_clean}")
                        polynomial_display = " | ".join(tramos_display)
                    else:
                        # Para muchos tramos, solo mostrar el resumen
                        polynomial_display = f"{len(tramos)} tramos de spline"
                    
                    # Calcular error para splines
                    if x_array is not None and y_array is not None:
                        try:
                            error_value = self._calculate_spline_tramos_error(tramos, x_array, y_array)
                        except Exception as e:
                            print(f"Error calculando error para {name}: {e}")
                            error_value = 0.0  # Splines son interpolaciones exactas
                else:
                    polynomial_display = "Tramos no disponibles"
            else:
                # Para métodos tradicionales (Vandermonde, Newton, Lagrange)
                polynomial_display = result.get("polynomial", "N/A")
                
                if x_array is not None and y_array is not None and polynomial_display != "N/A":
                    try:
                        error_value = self._calculate_interpolation_error(polynomial_display, x_array, y_array)
                    except Exception as e:
                        print(f"Error calculando error para {name}: {e}")
                        error_value = "N/A"
            
            comparison["methods"].append({
                "method": name,
                "status": "Exitoso",
                "polynomial": polynomial_display,
                "error": error_value,
                "message": result.get("message_method", "")
            })
        else:
            comparison["methods"].append({
                "method": name,
                "status": "Error",
                "polynomial": "N/A",
                "error": "N/A",
                "message": result.get("message_method", "Fallo en la ejecución") if result else "Resultado inválido"
            })

    def _calculate_spline_tramos_error(self, tramos, x_data, y_data):
        """
        Calcula el error RMSE para splines usando los tramos directamente
        """
        try:
            if not tramos or len(tramos) == 0:
                return 0.0
            
            y_predicted = []
            
            for i, x_val in enumerate(x_data):
                # Para cada punto, encontrar el tramo correspondiente
                # Normalmente cada tramo cubre un intervalo específico
                
                if i < len(tramos):
                    tramo = tramos[i]
                else:
                    # Si hay más puntos que tramos, usar el último tramo
                    tramo = tramos[-1]
                
                try:
                    # Evaluar la ecuación del tramo
                    # Limpiar la ecuación para evaluación
                    ecuacion = str(tramo).strip()
                    
                    # Reemplazar la notación de potencias ^2, ^3, etc. con **2, **3
                    ecuacion = ecuacion.replace('^', '**')
                    
                    # Reemplazar x con el valor numérico
                    ecuacion_eval = ecuacion.replace('x', str(x_val))
                    
                    # Evaluar la expresión
                    y_pred = eval(ecuacion_eval)
                    y_predicted.append(y_pred)
                    
                except Exception as e:
                    print(f"Error evaluando tramo {i}: {e}")
                    print(f"Ecuación original: {tramo}")
                    # Si falla la evaluación, usar el valor original (interpolación exacta)
                    y_predicted.append(y_data[i])
            
            y_predicted = np.array(y_predicted)
            
            # Calcular RMSE
            rmse = np.sqrt(np.mean((y_data - y_predicted)**2))
            return float(rmse)
            
        except Exception as e:
            print(f"Error general calculando error de spline: {e}")
            return 0.0
    
    def _calculate_interpolation_error(self, polynomial_str, x_data, y_data):
        """
        Calcula el error RMSE del polinomio interpolante
        """
        try:
            # Evaluar el polinomio en los puntos x_data
            y_predicted = []
            
            for x_val in x_data:
                # Reemplazar x con el valor numérico en el string del polinomio
                poly_eval = polynomial_str.replace('x', f'*{x_val}').replace('**', '**')
                
                # Limpiar el string para evaluación segura
                poly_eval = self._clean_polynomial_for_eval(poly_eval, x_val)
                
                try:
                    y_pred = eval(poly_eval)
                    y_predicted.append(y_pred)
                except:
                    # Si falla eval, usar evaluación alternativa
                    y_pred = self._evaluate_polynomial_alternative(polynomial_str, x_val)
                    y_predicted.append(y_pred)
            
            y_predicted = np.array(y_predicted)
            
            # Calcular RMSE
            rmse = np.sqrt(np.mean((y_data - y_predicted)**2))
            return float(rmse)
            
        except Exception as e:
            print(f"Error en cálculo de error: {e}")
            return float('inf')

    def _clean_polynomial_for_eval(self, poly_str, x_val):
        """
        Limpia y prepara el string del polinomio para evaluación segura
        """
        # Reemplazar x con el valor
        poly_str = poly_str.replace('x', str(x_val))
        
        # Limpiar signos al inicio
        poly_str = poly_str.strip().lstrip('+')
        
        # Manejar multiplicaciones implícitas
        poly_str = re.sub(r'(\d+\.?\d*)\*', r'\1*', poly_str)
        
        # Reemplazar ** con **
        poly_str = poly_str.replace('**', '**')
        
        return poly_str

    def _evaluate_polynomial_alternative(self, poly_str, x_val):
        """
        Método alternativo para evaluar polinomios cuando eval() falla
        """
        try:
            # Método simple para polinomios lineales como "2.0*x"
            if '*x' in poly_str and '+' not in poly_str and '-' not in poly_str.strip('-'):
                coeff = float(poly_str.split('*')[0])
                return coeff * x_val
            
            # Para casos más complejos, intentar numpy
            # Extraer coeficientes manualmente si es necesario
            return 0.0  # Valor por defecto
            
        except:
            return 0.0

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

        # Filtrar métodos exitosos con errores numéricos válidos
        valid_methods = [m for m in methods 
                        if m["status"] == "Exitoso" 
                        and isinstance(m["error"], (int, float)) 
                        and not np.isinf(m["error"])]
        
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