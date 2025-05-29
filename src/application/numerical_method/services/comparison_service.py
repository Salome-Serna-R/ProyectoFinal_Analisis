from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import inch
from datetime import datetime
import os


class ComparisonService:
    
    def create_comparison(self, bisection_result, fixed_point_result, newton_result, 
                         regula_falsi_result, secant_result,
                         bisection_validation, fixed_point_validation, newton_validation,
                         regula_falsi_validation, secant_validation):
        """Crea la comparación entre los cinco métodos"""
        comparison = {
            "methods": [],
            "analysis": {},
            "has_valid_results": False
        }
        
        # Procesar resultado de bisección
        if bisection_result and bisection_result.get("is_successful"):
            bisection_data = self._process_method_result("Bisección", bisection_result)
            comparison["methods"].append(bisection_data)
            comparison["has_valid_results"] = True
        elif bisection_validation != True:
            comparison["methods"].append({
                "method": "Bisección",
                "status": "Error de validación",
                "error": bisection_validation,
                "iterations": "N/A",
                "root": "N/A",
                "final_error": "N/A"
            })
        
        # Procesar resultado de punto fijo
        if fixed_point_result and fixed_point_result.get("is_successful"):
            fixed_point_data = self._process_method_result("Punto Fijo", fixed_point_result)
            comparison["methods"].append(fixed_point_data)
            comparison["has_valid_results"] = True
        elif fixed_point_validation != True:
            comparison["methods"].append({
                "method": "Punto Fijo",
                "status": "Error de validación",
                "error": fixed_point_validation,
                "iterations": "N/A",
                "root": "N/A",
                "final_error": "N/A"
            })
        
        # Procesar resultado de Newton-Raphson
        if newton_result and newton_result.get("is_successful"):
            newton_data = self._process_method_result("Newton-Raphson", newton_result)
            comparison["methods"].append(newton_data)
            comparison["has_valid_results"] = True
        elif newton_validation != True:
            comparison["methods"].append({
                "method": "Newton-Raphson",
                "status": "Error de validación",
                "error": newton_validation,
                "iterations": "N/A",
                "root": "N/A",
                "final_error": "N/A"
            })
        
        # Procesar resultado de Regla Falsa
        if regula_falsi_result and regula_falsi_result.get("is_successful"):
            regula_falsi_data = self._process_method_result("Regla Falsa", regula_falsi_result)
            comparison["methods"].append(regula_falsi_data)
            comparison["has_valid_results"] = True
        elif regula_falsi_validation != True:
            comparison["methods"].append({
                "method": "Regla Falsa",
                "status": "Error de validación",
                "error": regula_falsi_validation,
                "iterations": "N/A",
                "root": "N/A",
                "final_error": "N/A"
            })
        
        # Procesar resultado de Secante
        if secant_result and secant_result.get("is_successful"):
            secant_data = self._process_method_result("Secante", secant_result)
            comparison["methods"].append(secant_data)
            comparison["has_valid_results"] = True
        elif secant_validation != True:
            comparison["methods"].append({
                "method": "Secante",
                "status": "Error de validación",
                "error": secant_validation,
                "iterations": "N/A",
                "root": "N/A",
                "final_error": "N/A"
            })
        
        # Realizar análisis comparativo solo si hay resultados válidos
        if comparison["has_valid_results"]:
            comparison["analysis"] = self._analyze_results(comparison["methods"])
        
        return comparison
    
    def _process_method_result(self, method_name, result):
        """Procesa el resultado de un método específico"""
        iterations = len(result.get("table", {}))
        final_error = "N/A"
        
        if result.get("table") and iterations > 0:
            last_iteration = result["table"][iterations]
            if "error" in last_iteration and last_iteration["error"] != float('inf'):
                final_error = last_iteration["error"]
        
        return {
            "method": method_name,
            "status": "Exitoso" if result.get("have_solution") else "Sin convergencia",
            "iterations": iterations,
            "root": result.get("root", "N/A"),
            "final_error": final_error,
            "message": result.get("message_method", ""),
            "have_solution": result.get("have_solution", False)
        }
    
    def _analyze_results(self, methods):
        """Analiza los resultados y determina el mejor método"""
        analysis = {
            "most_efficient": None,
            "most_accurate": None,
            "fastest_convergence": None,
            "best_overall": None,
            "summary": ""
        }
        
        successful_methods = [m for m in methods if m.get("have_solution", False)]
        
        if not successful_methods:
            analysis["summary"] = "Ningún método encontró una solución válida."
            return analysis
        
        # Encontrar el más eficiente (menos iteraciones)
        if len(successful_methods) > 0:
            most_efficient = min(successful_methods, key=lambda x: x["iterations"])
            analysis["most_efficient"] = most_efficient["method"]
            analysis["fastest_convergence"] = most_efficient["method"]
        
        # Encontrar el más preciso (menor error final)
        methods_with_error = [m for m in successful_methods if isinstance(m["final_error"], (int, float))]
        if methods_with_error:
            most_accurate = min(methods_with_error, key=lambda x: abs(x["final_error"]))
            analysis["most_accurate"] = most_accurate["method"]
        
        # Determinar el mejor en general
        if len(successful_methods) == 1:
            analysis["best_overall"] = successful_methods[0]["method"]
            analysis["summary"] = f"Solo el método de {successful_methods[0]['method']} encontró una solución válida."
        else:
            # Sistema de scoring mejorado para cinco métodos
            scores = {}
            for method in successful_methods:
                scores[method["method"]] = 0
                
                # Puntos por eficiencia (método con menos iteraciones)
                if method["method"] == analysis["most_efficient"]:
                    scores[method["method"]] += 4
                else:
                    # Puntos proporcionales basados en iteraciones
                    min_iterations = min(m["iterations"] for m in successful_methods)
                    if method["iterations"] <= min_iterations * 1.5:  # Si está cerca del mínimo
                        scores[method["method"]] += 2
                    elif method["iterations"] <= min_iterations * 2.0:  # Si está moderadamente cerca
                        scores[method["method"]] += 1
                
                # Puntos por precisión
                if method["method"] == analysis["most_accurate"]:
                    scores[method["method"]] += 4
                
                # Bonus específicos por características de cada método
                if method["method"] == "Newton-Raphson" and method["have_solution"]:
                    scores[method["method"]] += 2  # Convergencia cuadrática
                
                if method["method"] == "Bisección" and method["have_solution"]:
                    scores[method["method"]] += 2  # Robustez garantizada
                
                if method["method"] == "Regla Falsa" and method["have_solution"]:
                    scores[method["method"]] += 1  # Mejor que bisección, robustez
                
                if method["method"] == "Secante" and method["have_solution"]:
                    scores[method["method"]] += 1  # No requiere derivada, convergencia rápida
                
                if method["method"] == "Punto Fijo" and method["have_solution"]:
                    scores[method["method"]] += 1  # Versatilidad en reformulación
            
            best_method = max(scores.keys(), key=lambda k: scores[k])
            analysis["best_overall"] = best_method
            
            # Generar resumen detallado
            successful_names = [m["method"] for m in successful_methods]
            total_methods = len([m for m in methods if m["method"] in ["Bisección", "Punto Fijo", "Newton-Raphson", "Regla Falsa", "Secante"]])
            
            if len(successful_methods) == total_methods:
                summary_start = "Los cinco métodos convergieron exitosamente. "
            elif len(successful_methods) == 4:
                summary_start = "Cuatro métodos convergieron exitosamente. "
            elif len(successful_methods) == 3:
                summary_start = "Tres métodos convergieron exitosamente. "
            elif len(successful_methods) == 2:
                summary_start = f"Dos métodos convergieron: {' y '.join(successful_names)}. "
            else:
                summary_start = f"Solo {successful_names[0]} convergió. "
            
            min_iter = min(m['iterations'] for m in successful_methods)
            efficiency_info = f"El método más eficiente fue {analysis['most_efficient']} con {min_iter} iteraciones"
            accuracy_info = f"el más preciso fue {analysis['most_accurate']}"
            
            if analysis['most_efficient'] == analysis['most_accurate']:
                analysis["summary"] = summary_start + f"{analysis['most_efficient']} fue tanto el más eficiente como el más preciso."
            else:
                analysis["summary"] = summary_start + efficiency_info + f" y {accuracy_info}. Se recomienda el método de {best_method} como mejor opción general."
        
        return analysis
    
    def generate_pdf_report(self, comparison_data, form_data):
        """Genera el informe PDF comparativo"""
        filename = f"informe_comparativo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join("static", "reports", filename)
        
        # Crear directorio si no existe
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        doc = SimpleDocTemplate(filepath, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Título
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=1  # Center
        )
        story.append(Paragraph("INFORME COMPARATIVO DE MÉTODOS NUMÉRICOS", title_style))
        story.append(Spacer(1, 12))
        
        # Información general
        story.append(Paragraph("DATOS DE ENTRADA", styles['Heading2']))
        
        data_info = [
            ["Parámetro", "Valor"],
            ["Función f(x)", form_data.get("function_f", "N/A")],
            ["Función g(x)", form_data.get("function_g", "N/A")],
            ["Intervalo [a,b]", f"[{form_data.get('interval_a')}, {form_data.get('interval_b')}]"],
            ["Punto inicial x₀", str(form_data.get("x0"))],
            ["Tolerancia", str(form_data.get("tolerance"))],
            ["Máx. iteraciones", str(form_data.get("max_iterations"))],
            ["Tipo de precisión", form_data.get("precision")]
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
        
        # Tabla comparativa de resultados
        story.append(Paragraph("RESULTADOS COMPARATIVOS", styles['Heading2']))
        
        comparison_data_table = [["Método", "Estado", "Iteraciones", "Raíz aproximada", "Error final"]]
        
        for method in comparison_data["methods"]:
            root_str = f"{method['root']:.6f}" if isinstance(method['root'], (int, float)) else str(method['root'])
            error_str = f"{method['final_error']:.2e}" if isinstance(method['final_error'], (int, float)) else str(method['final_error'])
            
            comparison_data_table.append([
                method["method"],
                method["status"],
                str(method["iterations"]),
                root_str,
                error_str
            ])
        
        results_table = Table(comparison_data_table)
        results_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(results_table)
        story.append(Spacer(1, 20))
        
        # Análisis
        if comparison_data.get("analysis") and comparison_data["has_valid_results"]:
            story.append(Paragraph("ANÁLISIS COMPARATIVO", styles['Heading2']))
            
            analysis = comparison_data["analysis"]
            
            if analysis.get("most_efficient"):
                story.append(Paragraph(f"<b>Método más eficiente:</b> {analysis['most_efficient']}", styles['Normal']))
            
            if analysis.get("most_accurate"):
                story.append(Paragraph(f"<b>Método más preciso:</b> {analysis['most_accurate']}", styles['Normal']))
            
            if analysis.get("best_overall"):
                story.append(Paragraph(f"<b>Mejor método general:</b> {analysis['best_overall']}", styles['Normal']))
            
            story.append(Spacer(1, 12))
            story.append(Paragraph("<b>Conclusión:</b>", styles['Normal']))
            story.append(Paragraph(analysis.get("summary", "No se pudo realizar el análisis."), styles['Normal']))
        
        # Descripción de métodos
        story.append(Spacer(1, 20))
        story.append(Paragraph("DESCRIPCIÓN DE MÉTODOS", styles['Heading2']))
        
        bisection_desc = """
        <b>Método de Bisección:</b> Técnica que encuentra raíces en un intervalo [a,b] donde f(a)×f(b)<0.
        Divide repetidamente el intervalo por la mitad hasta encontrar la raíz con la precisión deseada.
        Es robusto y siempre converge, pero puede ser lento.
        """
        
        fixed_point_desc = """
        <b>Método de Punto Fijo:</b> Reformula la ecuación f(x)=0 como x=g(x) y usa iteraciones sucesivas
        para aproximarse a la raíz. Su convergencia depende de la función g(x) elegida y puede ser muy
        rápido cuando converge, pero no siempre garantiza convergencia.
        """
        
        newton_desc = """
        <b>Método de Newton-Raphson:</b> Utiliza la derivada de la función para encontrar raíces mediante
        la fórmula x_{n+1} = x_n - f(x_n)/f'(x_n). Tiene convergencia cuadrática cuando funciona bien,
        pero requiere que f'(x) ≠ 0 y puede fallar si la derivada es pequeña o el punto inicial es inadecuado.
        """
        
        regula_falsi_desc = """
        <b>Método de Regla Falsa (Falsa Posición):</b> Similar a bisección pero usa interpolación lineal
        para aproximar la raíz. Calcula el punto donde la línea secante interseca el eje x mediante
        c=(a×f(b)-b×f(a))/(f(b)-f(a)). Converge más rápido que bisección pero puede ser más lento cerca de la raíz.
        """
        
        secant_desc = """
        <b>Método de la Secante:</b> Aproxima la derivada usando dos puntos, evitando el cálculo explícito
        de la derivada. Usa la fórmula x_{n+1} = x_n - f(x_n)×(x_n-x_{n-1})/(f(x_n)-f(x_{n-1})).
        Converge más rápido que bisección y no requiere derivadas, pero puede ser inestable.
        """
        
        story.append(Paragraph(bisection_desc, styles['Normal']))
        story.append(Spacer(1, 12))
        story.append(Paragraph(fixed_point_desc, styles['Normal']))
        story.append(Spacer(1, 12))
        story.append(Paragraph(newton_desc, styles['Normal']))
        story.append(Spacer(1, 12))
        story.append(Paragraph(regula_falsi_desc, styles['Normal']))
        story.append(Spacer(1, 12))
        story.append(Paragraph(secant_desc, styles['Normal']))
        
        # Generar PDF
        doc.build(story)
        
        return filename