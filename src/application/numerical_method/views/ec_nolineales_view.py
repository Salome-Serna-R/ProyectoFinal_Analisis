from django.views.generic import TemplateView
from src.application.numerical_method.services.ec_nolineales_service import ECNoLinealesService
from src.application.numerical_method.interfaces.interval_method import (
    IntervalMethod,
)
from src.application.numerical_method.containers.numerical_method_container import (
    NumericalMethodContainer,
)
from dependency_injector.wiring import inject, Provide
from src.application.shared.utils.plot_function import plot_function
from django.http import HttpRequest, HttpResponse
from fpdf import FPDF

#Este es el controlador de la vista de ecuaciones no lineales donde pedimos TODOS los datos necesarios para ejecutar todos los metodos
# y graficar la funcion además de guardar los resultados en uun pdf para descargarlo como el informe comparativo de los metodos
class NonLinearView(TemplateView):
    template_name = "ec_nolineales.html"


    def descargar_pdf(request):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Informe generado dinámicamente", ln=True, align="C")
        
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="informe_comparativo.pdf"'
        pdf.output(response)
        return response

    def post(self, request, *args, **kwargs):
        # Obtener datos del formulario
        data = {
            "f": request.POST.get("funcion_f"),
            "g": request.POST.get("funcion_g"),
            "x0": float(request.POST.get("x0")),
            "interval_a": float(request.POST.get("interval_a")),
            "interval_b": float(request.POST.get("interval_b")),
            "precision": int(request.POST.get("precision")),
            "tol": float(request.POST.get("tolerance")),
            "max_iter": int(request.POST.get("max_iterations")),
        }

        service = ECNoLinealesService()

        # Validar datos
        error = service.validate_input(data)
        if error:
            return self.render_to_response({"error": error})

        # Ejecutar métodos y generar PDF
        resumen = service.generate_comparison_report(data)

        # Ruta de la gráfica (si usas graficación)
        graph_path = plot_function(data["f"], data["x0"], data["x1"])

        return self.render_to_response({
            "resultados": resumen,
            "graph_url": graph_path,
            "pdf_url": "media/pdf/informe_comparativo.pdf"
        })
