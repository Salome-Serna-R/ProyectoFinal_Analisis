"""
Este servicio se encarga de realizar la comparación de métodos numéricos para resolver ecuaciones no lineales.
"""
from fpdf import FPDF


class ECNoLinealesService:
    def __init__(self):
        # Importa aquí para evitar el ciclo
        from src.application.numerical_method.containers.numerical_method_container import NumericalMethodContainer
        self.methods = [
            NumericalMethodContainer.bisection_service(),
            NumericalMethodContainer.regula_falsi_service(),
            NumericalMethodContainer.fixed_point_service(),
            NumericalMethodContainer.newton_service(),
            NumericalMethodContainer.secant_service(),
            NumericalMethodContainer.multiple_roots_1_service(),
            NumericalMethodContainer.multiple_roots_2_service(),
        ]


    # Validar datos de entrada
    def validate_input(self, data):
        self.data = data
        # Validar que todos los campos estén presentes
        required_fields = ["function_f", "function_g", "x0", "interval_a", "interval_b", "precision", "tolerance", "max_iterations"]
        for field in required_fields:
            if field not in data:
                return f"Falta el campo: {field}"

        # Validar tipos de datos
        try:
            data["x0"] = float(data["x0"])
            data["interval_a"] = float(data["interval_a"])
            data["interval_b"] = float(data["interval_b"])
            data["precision"] = int(data["precision"])
            data["tolerance"] = float(data["tolerance"])
            data["max_iterations"] = int(data["max_iterations"])
        except ValueError as e:
            return f"Error de tipo de dato: {e}"

        return None

    # Ejecutar todos los métodos y retornar los resultados completos
    def compare_methods(self, data):
        method_params = {
        "BisectionService": ["interval_a", "interval_b", "tolerance", "max_iterations", "function_f", "precision"],
        "NewtonRaphsonService": ["x0", "tolerance", "max_iterations", "function_f", "df", "precision"],
        "SecantService": ["x0", "x1", "tolerance", "max_iterations", "function_f", "precision"],
        "FixedPointService": ["x0", "tolerance", "max_iterations", "function_f", "g", "precision"],
        "MultipleRoots1Service": ["x0", "tolerance", "max_iterations", "function_f", "precision"],
        "MultipleRoots2Service": ["x0", "tolerance", "max_iterations", "function_f", "precision"],
        }
        results = {}
        for method in self.methods:
            class_name = method.__class__.__name__
            params = {k: data.get(k, None) for k in method_params[class_name]}

            results[class_name] = method.solve(**params)
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
        #self.create_pdf_report(summary)
        return summary
