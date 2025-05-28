# comparison_view.py - Colocar en: src/application/numerical_method/views/comparison_view.py
from django.views.generic import TemplateView
from django.http import HttpRequest, HttpResponse
from src.application.numerical_method.interfaces.interval_method import IntervalMethod
from src.application.numerical_method.interfaces.iterative_method import IterativeMethod
from src.application.numerical_method.containers.numerical_method_container import NumericalMethodContainer
from dependency_injector.wiring import inject, Provide
from src.application.shared.utils.plot_function import plot_function
from src.application.numerical_method.services.comparison_service import ComparisonService
import json


class ComparisonView(TemplateView):
    template_name = "comparison.html"

    @inject
    def __init__(
        self,
        bisection_service: IntervalMethod = Provide[NumericalMethodContainer.bisection_service],
        fixed_point_service: IterativeMethod = Provide[NumericalMethodContainer.fixed_point_service],
        newton_service: IterativeMethod = Provide[NumericalMethodContainer.newton_service],
        regula_falsi_service: IntervalMethod = Provide[NumericalMethodContainer.regula_falsi_service],
        secant_service: IterativeMethod = Provide[NumericalMethodContainer.secant_service],
        **kwargs
    ):
        super().__init__(**kwargs)
        self.bisection_service = bisection_service
        self.fixed_point_service = fixed_point_service
        self.newton_service = newton_service
        self.regula_falsi_service = regula_falsi_service
        self.secant_service = secant_service
        self.comparison_service = ComparisonService()

    def post(self, request: HttpRequest, *args: object, **kwargs: object) -> HttpResponse:
        context = self.get_context_data()
        
        # Extraer datos del formulario
        interval_a = float(request.POST.get("interval_a"))
        interval_b = float(request.POST.get("interval_b"))
        x0 = float(request.POST.get("x0"))
        tolerance = float(request.POST.get("tolerance"))
        max_iterations = int(request.POST.get("max_iterations"))
        function_f = request.POST.get("function_f")
        function_g = request.POST.get("function_g")
        precision = int(request.POST.get("precision"))
        generate_pdf = request.POST.get("generate_pdf") == "on"

        # Ejecutar método de bisección
        bisection_validation = self.bisection_service.validate_input(
            interval_a=interval_a,
            interval_b=interval_b,
            tolerance=tolerance,
            max_iterations=max_iterations,
            function_f=function_f,
        )

        bisection_result = None
        if bisection_validation is True:
            bisection_result = self.bisection_service.solve(
                interval_a=interval_a,
                interval_b=interval_b,
                tolerance=tolerance,
                max_iterations=max_iterations,
                function_f=function_f,
                precision=precision,
            )

        # Ejecutar método de punto fijo
        fixed_point_validation = self.fixed_point_service.validate_input(
            x0=x0,
            tolerance=tolerance,
            max_iterations=max_iterations,
            function_f=function_f,
            function_g=function_g,
        )

        fixed_point_result = None
        if fixed_point_validation is True:
            fixed_point_result = self.fixed_point_service.solve(
                x0=x0,
                tolerance=tolerance,
                max_iterations=max_iterations,
                function_f=function_f,
                function_g=function_g,
                precision=precision,
            )

        # Ejecutar método de Newton-Raphson
        newton_validation = self.newton_service.validate_input(
            x0=x0,
            tolerance=tolerance,
            max_iterations=max_iterations,
            function_f=function_f,
        )

        newton_result = None
        if newton_validation is True:
            newton_result = self.newton_service.solve(
                function_f=function_f,
                x0=x0,
                tolerance=tolerance,
                max_iterations=max_iterations,
                precision=precision,
            )


        # Ejecutar método de Regla Falsa
        regula_falsi_validation = self.regula_falsi_service.validate_input(
            interval_a=interval_a,
            interval_b=interval_b,
            tolerance=tolerance,
            max_iterations=max_iterations,
            function_f=function_f,
        )

        regula_falsi_result = None
        if regula_falsi_validation is True:
            regula_falsi_result = self.regula_falsi_service.solve(
                interval_a=interval_a,
                interval_b=interval_b,
                tolerance=tolerance,
                max_iterations=max_iterations,
                function_f=function_f,
                precision=precision,
            )

        # Ejecutar método de Secante
        secant_validation = self.secant_service.validate_input(
            x0=x0,
            tolerance=tolerance,
            max_iterations=max_iterations,
            function_f=function_f,
        )

        secant_result = None
        if secant_validation is True:
            secant_result = self.secant_service.solve(
                function_f=function_f,
                x0=x0,
                tolerance=tolerance,
                max_iterations=max_iterations,
                precision=precision,
            )

        # Crear comparación con los cinco métodos
        comparison_data = self.comparison_service.create_comparison(
            bisection_result=bisection_result,
            fixed_point_result=fixed_point_result,
            newton_result=newton_result,
            regula_falsi_result=regula_falsi_result,
            secant_result=secant_result,
            bisection_validation=bisection_validation,
            fixed_point_validation=fixed_point_validation,
            newton_validation=newton_validation,
            regula_falsi_validation=regula_falsi_validation,
            secant_validation=secant_validation,
        )

        # Generar PDF si se solicita
        pdf_path = None
        if generate_pdf and (bisection_result or fixed_point_result or newton_result):
            form_data = {
                "interval_a": interval_a,
                "interval_b": interval_b,
                "x0": x0,
                "tolerance": tolerance,
                "max_iterations": max_iterations,
                "function_f": function_f,
                "function_g": function_g,
                "precision": "Decimales correctos" if precision else "Cifras significativas"
            }
            pdf_path = self.comparison_service.generate_pdf_report(
                comparison_data, form_data
            )

        # Generar gráfica si hay al menos un resultado exitoso
        if (bisection_result and bisection_result.get("have_solution")) or \
           (fixed_point_result and fixed_point_result.get("have_solution")) or \
           (newton_result and newton_result.get("have_solution")):
            
            roots = []
            if bisection_result and bisection_result.get("have_solution"):
                roots.append((bisection_result["root"], 0.0))
            if fixed_point_result and fixed_point_result.get("have_solution"):
                roots.append((fixed_point_result["root"], 0.0))
            if newton_result and newton_result.get("have_solution"):
                roots.append((newton_result["root"], 0.0))
            if regula_falsi_result and regula_falsi_result.get("have_solution"):
                roots.append((regula_falsi_result["root"], 0.0))
            if secant_result and secant_result.get("have_solution"):
                roots.append((secant_result["root"], 0.0))
            
            plot_function(function_f, True, roots)

        context["template_data"] = {
            "comparison_data": comparison_data,
            "pdf_path": pdf_path,
            "form_data": {
                "interval_a": interval_a,
                "interval_b": interval_b,
                "x0": x0,
                "tolerance": tolerance,
                "max_iterations": max_iterations,
                "function_f": function_f,
                "function_g": function_g,
                "precision": precision,
                "generate_pdf": generate_pdf
            }
        }

        return self.render_to_response(context)