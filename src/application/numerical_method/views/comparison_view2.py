# comparison_view2.py - Corregido y mejorado

from django.views.generic import TemplateView
from django.http import HttpRequest, HttpResponse
from src.application.numerical_method.containers.numerical_method_container import NumericalMethodContainer
from dependency_injector.wiring import inject, Provide
from src.application.numerical_method.interfaces.matrix_method import MatrixMethod
from src.application.numerical_method.services.comparison_service2 import ComparisonService as ComparisonLinearService


class ComparisonLinearView(TemplateView):
    template_name = "comparison_linear.html"

    @inject
    def __init__(
        self,
        jacobi_service: MatrixMethod = Provide[NumericalMethodContainer.jacobi_service],
        gauss_seidel_service: MatrixMethod = Provide[NumericalMethodContainer.gauss_seidel_service],
        sor_service: MatrixMethod = Provide[NumericalMethodContainer.sor_service],
        **kwargs
    ):
        super().__init__(**kwargs)
        self.jacobi_service = jacobi_service
        self.gauss_seidel_service = gauss_seidel_service
        self.sor_service = sor_service
        self.comparison_service = ComparisonLinearService()

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        context = self.get_context_data()

        # Extraer datos del formulario
        matrix_a_raw = request.POST.get("matrix_a_raw")
        vector_b_raw = request.POST.get("vector_b_raw")
        initial_guess_raw = request.POST.get("initial_guess_raw")
        tolerance = float(request.POST.get("tolerance"))
        max_iterations = int(request.POST.get("max_iterations"))
        matrix_size = int(request.POST.get("matrix_size"))
        precision = int(request.POST.get("precision_type"))
        relaxation_factor = float(request.POST.get("relaxation_factor"))
        generate_pdf = request.POST.get("generate_pdf") == "on"

        # Validaciones y ejecuciones
        jacobi_result = None
        jacobi_validation = self.jacobi_service.validate_input(
            matrix_a_raw=matrix_a_raw,
            vector_b_raw=vector_b_raw,
            initial_guess_raw=initial_guess_raw,
            tolerance=tolerance,
            max_iterations=max_iterations,
            matrix_size=matrix_size,
        )
        if isinstance(jacobi_validation, list):
            A, b, x0 = jacobi_validation
            jacobi_result = self.jacobi_service.solve(
                A=A, b=b, x0=x0, tolerance=tolerance,
                max_iterations=max_iterations,
                precision_type="decimales_correctos" if precision else "cifras_significativas"
            )

        gauss_result = None
        gauss_validation = self.gauss_seidel_service.validate_input(
            matrix_a_raw=matrix_a_raw,
            vector_b_raw=vector_b_raw,
            initial_guess_raw=initial_guess_raw,
            tolerance=tolerance,
            max_iterations=max_iterations,
            matrix_size=matrix_size,
        )
        if isinstance(gauss_validation, list):
            A, b, x0 = gauss_validation
            gauss_result = self.gauss_seidel_service.solve(
                A=A, b=b, x0=x0, tolerance=tolerance,
                max_iterations=max_iterations,
                precision=precision
            )

        sor_result = None
        sor_validation = self.sor_service.validate_input(
            matrix_a_raw=matrix_a_raw,
            vector_b_raw=vector_b_raw,
            initial_guess_raw=initial_guess_raw,
            tolerance=tolerance,
            max_iterations=max_iterations,
            relaxation_factor=relaxation_factor,
            matrix_size=matrix_size,
        )
        if isinstance(sor_validation, list):
            A, b, x0 = sor_validation
            sor_result = self.sor_service.solve(
                A=A, b=b, x0=x0, tolerance=tolerance,
                max_iterations=max_iterations,
                relaxation_factor=relaxation_factor,
                precision_type=precision
            )

        # Crear comparación
        comparison_data = self.comparison_service.create_comparison(
            gauss_result=gauss_result,
            jacobi_result=jacobi_result,
            sor_result=sor_result,
            gauss_validation=gauss_validation,
            jacobi_validation=jacobi_validation,
            sor_validation=sor_validation,
        )

        # Generar PDF si se solicita
        pdf_path = None
        if generate_pdf and comparison_data["has_valid_results"]:
            form_data = {
                "matrix_a_raw": matrix_a_raw,
                "vector_b_raw": vector_b_raw,
                "initial_guess_raw": initial_guess_raw,
                "tolerance": tolerance,
                "max_iterations": max_iterations,
                "precision_type": "Decimales correctos" if precision else "Cifras significativas",
                "relaxation_factor": relaxation_factor
            }
            pdf_path = self.comparison_service.generate_pdf_report(comparison_data, form_data)

        context["template_data"] = {
            "comparison_data": comparison_data,
            "pdf_path": pdf_path,
            "form_data": {
                "matrix_a_raw": matrix_a_raw,
                "vector_b_raw": vector_b_raw,
                "initial_guess_raw": initial_guess_raw,
                "tolerance": tolerance,
                "max_iterations": max_iterations,
                "precision_type": precision,
                "relaxation_factor": relaxation_factor,
                "generate_pdf": generate_pdf
            }
        }

        # Debug en consola
        print("VALIDACIONES:")
        print("Gauss-Seidel:", gauss_validation)
        print("Jacobi:", jacobi_validation)
        print("SOR:", sor_validation)

        return self.render_to_response(context)
