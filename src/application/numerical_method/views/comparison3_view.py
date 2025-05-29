import os
from django.views.generic import TemplateView
from django.http import HttpRequest, HttpResponse
from dependency_injector.wiring import inject, Provide
from src.application.numerical_method.containers.numerical_method_container import NumericalMethodContainer
from src.application.numerical_method.interfaces.interpolation_method import InterpolationMethod
from src.application.numerical_method.services.comparison3_service import Comparison3Service
from django.utils.decorators import method_decorator


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

        x_values_raw = request.POST.get("x_values", "")
        y_values_raw = request.POST.get("y_values", "")
        generate_pdf = request.POST.get("generate_pdf") == "on"

        validations = {}
        results = {}
        pdf_path = None

        try:
            x = [float(val) for val in x_values_raw.strip().split()]
            y = [float(val) for val in y_values_raw.strip().split()]

            if len(x) != len(y):
                validations["longitud"] = {
                    "valid": False,
                    "message": "Los vectores X e Y deben tener la misma longitud."
                }
            else:
                validations["longitud"] = {"valid": True}
                validations["formato"] = {"valid": True}  # AGREGADO

                results_dict = {
                    "Vandermonde": self.vandermonde_service.solve(x, y),
                    "Newton": self.newton_interpol_service.solve(x, y),
                    "Lagrange": self.lagrange_service.solve(x, y),
                    "Spline lineal": self.spline_linear_service.solve(x, y),
                    "Spline cúbico": self.spline_cubic_service.solve(x, y),
                }
                
                # Debug: imprimir todos los resultados
                for method_name, result in results_dict.items():
                    print(f"DEBUG - Resultado de {method_name}:")
                    print(f"  - is_successful: {result.get('is_successful') if result else None}")
                    print(f"  - polynomial: {result.get('polynomial') if result else None}")
                    print(f"  - error: {result.get('error') if result else None}")
                    print(f"  - message: {result.get('message_method') if result else None}")
                    print("---")

                comparison_data = self.comparison_service.create_comparison(
                    results_dict,
                    validations,
                    x_values=x,
                    y_values=y
                )

                results["Interpolación"] = comparison_data

                # CORREGIDO: Generar PDF si se solicita
                if generate_pdf:
                    form_data = {
                        "x_values": x_values_raw,
                        "y_values": y_values_raw
                    }
                    pdf_filename = self.comparison_service.generate_pdf_report(comparison_data, form_data)
                    if pdf_filename:
                        pdf_path = pdf_filename
                        print(f"PDF generado exitosamente: {pdf_filename}")
                    else:
                        print("Error al generar el PDF")

        except ValueError as e:
            print(f"Error de formato: {e}")
            validations["formato"] = {
                "valid": False,
                "message": "Error de formato. Usa solo números separados por espacios."
            }
            validations["longitud"] = {"valid": True}

        except Exception as e:
            print(f"Error inesperado: {e}")
            validations["formato"] = {
                "valid": False,
                "message": f"Error inesperado: {str(e)}"
            }

        context["template_data"] = {
            "comparison_data": results,
            "validations": validations,
            "form_data": {
                "x_values": x_values_raw,
                "y_values": y_values_raw,
                "generate_pdf": generate_pdf
            },
            "pdf_path": pdf_path,
        }

        print("Context data:", context["template_data"])
        if pdf_path:
            print(f"PDF path enviado al template: {pdf_path}")

        return self.render_to_response(context)