import os
from django.views.generic import TemplateView
from django.http import HttpRequest, HttpResponse
from dependency_injector.wiring import inject, Provide
from src.application.numerical_method.containers.numerical_method_container import NumericalMethodContainer
from src.application.numerical_method.interfaces.interpolation_method import InterpolationMethod
from src.application.numerical_method.services.comparison3_service import Comparison3Service
from django.utils.decorators import method_decorator
from dependency_injector.wiring import inject, Provide
from src.application.numerical_method.containers.numerical_method_container import NumericalMethodContainer

@method_decorator(inject, name="dispatch")
class ComparisonViewInterpol(TemplateView):
    template_name = "comparison3.html"

    vandermonde_service: InterpolationMethod = Provide[NumericalMethodContainer.vandermonde_service]
    newton_interpol_service: InterpolationMethod = Provide[NumericalMethodContainer.newton_interpol_service]
    lagrange_service: InterpolationMethod = Provide[NumericalMethodContainer.lagrange_service]
    spline_linear_service: InterpolationMethod = Provide[NumericalMethodContainer.spline_linear_service]
    spline_cubic_service: InterpolationMethod = Provide[NumericalMethodContainer.spline_cubic_service]
    comparison_service: Comparison3Service = Provide[NumericalMethodContainer.comparison3_service]

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        context = self.get_context_data()

        x_values_raw = request.POST.get("x_values")
        y_values_raw = request.POST.get("y_values")
        generate_pdf = request.POST.get("generate_pdf") == "on"

        validations = {}
        results = {}
        pdf_path = None  # Inicializar

        try:
            generate_pdf = request.POST.get("generate_pdf") == "on"
            pdf_path = None

            x = [float(val) for val in x_values_raw.strip().split()]
            y = [float(val) for val in y_values_raw.strip().split()]

            if len(x) != len(y):
                validations["longitud"] = {
                    "valid": False,
                    "message": "Los vectores X e Y deben tener la misma longitud."
                }
            else:
                validations["longitud"] = {"valid": True}

                results_dict = {
                    "Vandermonde": self.vandermonde_service.solve(x, y),
                    "Newton": self.newton_interpol_service.solve(x, y),
                    "Lagrange": self.lagrange_service.solve(x, y),
                    "Spline lineal": self.spline_linear_service.solve(x, y),
                    "Spline cúbico": self.spline_cubic_service.solve(x, y),
                }
                

                comparison_data = self.comparison_service.create_comparison(
                    results_dict,
                    validations,
                    x_values=x,
                    y_values=y
                )

                results["Interpolación"] = comparison_data

                # Generar PDF si se solicita y si hay resultados válidos
                if generate_pdf and comparison_data.get("has_valid_results", True):
                    form_data = {
                        "x_values": x_values_raw,
                        "y_values": y_values_raw
                    }
                    pdf_path = self.comparison_service.generate_pdf_report(comparison_data, form_data)
                    # pdf_path debe ser la ruta relativa a static, ejemplo: 'reports/comparison3.pdf'

        except ValueError:
            validations["formato"] = {
                "valid": False,
                "message": "Error de formato. Usa solo números separados por espacios."
            }

        context["template_data"] = {
            "comparison_data": results,
            "validations": validations,
            "form_data": {
                "x_values": x_values_raw,
                "y_values": y_values_raw
            },
            "pdf_path": pdf_path,
        }

        print("Context data:", context["template_data"])

        return self.render_to_response(context)

