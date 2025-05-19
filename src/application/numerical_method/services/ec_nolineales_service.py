"""
Este servicio se encarga de realizar la comparación de métodos numéricos para resolver ecuaciones no lineales.
"""
from fpdf import FPDF


class ECNoLinealesService:
    def __init__(self):
        # Importa aquí para evitar el ciclo
        from src.application.numerical_method.containers.numerical_method_container import NumericalMethodContainer
        self.methods = [
            NumericalMethodContainer.bisection_service.bisection_service(),
            NumericalMethodContainer.regula_falsi_service.regula_falsi_service(),
            NumericalMethodContainer.fixed_point_service.fixed_point_service(),
            NumericalMethodContainer.newton_service.newtons_service(),
            NumericalMethodContainer.secant_service.secant_service(),
            NumericalMethodContainer.multiple_roots_1_service.multiple_roots_1_service(),
            NumericalMethodContainer.multiple_roots_2_service.multiple_roots_2_service(),
        ]

    # Validación de datos de entrada
    def validate_input(self, data):
        for method in self.methods:
            validation_result = method.validate_input(data)
            if validation_result is not None:
                return validation_result
        return None

    # Ejecutar todos los métodos y retornar los resultados completos
    def compare_methods(self, data):
        results = {}
        for method in self.methods:
            results[method.name] = method.solve(data)
        return results

    # Resumir resultados para tabla: Método, Iteraciones, Error, Raíz
    def summarize_results(self, raw_results):
        summary = []
        for method_name, result in raw_results.items():
            if result.get("have_solution", False):
                table = result.get("table", {})
                last_iter = max(table.keys(), default=0)
                last_error = table.get(last_iter, {}).get("error", 0)
                summary.append({
                    "Metodo": method_name,
                    "Iteraciones": last_iter,
                    "Error": round(last_error, 6),
                    "Raiz": round(result["root"], 6),
                })
        return summary

    # Generar informe comparativo completo y PDF
    def generate_comparison_report(self, data):
        raw_results = self.compare_methods(data)
        summary = self.summarize_results(raw_results)
        self.create_pdf_report(summary)
        return summary

    # Crear el PDF
    def create_pdf_report(self, results: list, filename="informe_comparativo.pdf"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        # Título
        pdf.set_font("Arial", "B", 14)
        pdf.cell(200, 10, txt="Informe Comparativo de Métodos Numéricos", ln=True, align="C")
        pdf.ln(10)

        # Encabezados
        headers = ["Método", "Iteraciones", "Error", "Raíz"]
        pdf.set_font("Arial", "B", 12)
        for header in headers:
            pdf.cell(45, 10, txt=header, border=1, align='C')
        pdf.ln()

        # Cuerpo de la tabla
        pdf.set_font("Arial", size=12)
        for row in results:
            pdf.cell(45, 10, txt=str(row["Metodo"]), border=1)
            pdf.cell(45, 10, txt=str(row["Iteraciones"]), border=1, align="C")
            pdf.cell(45, 10, txt=str(row["Error"]), border=1, align="C")
            pdf.cell(45, 10, txt=str(row["Raiz"]), border=1, align="C")
            pdf.ln()

        pdf.output(filename)
