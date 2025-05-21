from django.views.generic import TemplateView
from src.application.numerical_method.services.ec_nolineales_service import ECNoLinealesService
from src.application.shared.utils.plot_function import plot_function
from django.http import HttpResponse
from fpdf import FPDF
import os

class NonLinearView(TemplateView):
    template_name = "ec_nolineales.html"

    def descargar_pdf(self, resumen):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Informe comparativo de métodos:", ln=1, align='L')

        for metodo, resultado in resumen.items():
            pdf.ln(10)
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, txt=metodo, ln=1)

            pdf.set_font("Arial", size=10)
            for key, value in resultado.items():
                pdf.cell(0, 10, txt=f"{key}: {value}", ln=1)

        path = os.path.join('static', 'pdf', 'numerical_method', 'informe_comparativo.pdf')
        os.makedirs(os.path.dirname(path), exist_ok=True)
        pdf.output(path)

    def post(self, request, *args, **kwargs):
        # Obtener datos del formulario
        data = {
            "function_f": request.POST.get("funcion_f"),
            "function_g": request.POST.get("funcion_g"),
            "x0": float(request.POST.get("x0")),
            "interval_a": float(request.POST.get("interval_a")),
            "interval_b": float(request.POST.get("interval_b")),
            "precision": int(request.POST.get("precision")),
            "tolerance": float(request.POST.get("tolerance")),
            "max_iterations": int(request.POST.get("max_iterations")),
        }

        service = ECNoLinealesService()

        # Validar datos
        error = service.validate_input(data)
        if error:
            return self.render_to_response({"error": error})

        # Ejecutar métodos y generar resumen
        resumen = service.compare_methods(data)

        # Generar PDF
        self.descargar_pdf(resumen)

        # (Opcional) Ruta de la gráfica si usas graficación
        # graph_path = plot_function(data["function_f"], data["interval_a"], data["interval_b"])
        graph_path = None  # puedes quitar esto si no necesitas la gráfica aún

        # Renderizar respuesta
        return self.render_to_response({
            "resumen": resumen,
            "graph_path": graph_path,
            "data": data,
        })
