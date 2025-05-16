from django.views.generic import TemplateView
from src.application.numerical_method.interfaces.interpolation_method import (
    InterpolationMethod,
)
from src.application.numerical_method.containers.numerical_method_container import (
    NumericalMethodContainer,
)
from dependency_injector.wiring import inject, Provide
from src.application.shared.utils.plot_function import plot_function
from django.http import HttpRequest, HttpResponse
from src.application.shared.utils.plot_function import plot_function


class SimpsonView(TemplateView):
    template_name = "simpson.html"

    @inject
    def __init__(
        self,
        method_service: InterpolationMethod = Provide[
            NumericalMethodContainer.simpson_service
        ],
        **kwargs
    ):
        super().__init__(**kwargs)
        self.method_service = method_service
        self.method_name = "Simpson's Rule"
        self.method_description = (
            "Simpson's Rule is a numerical method for approximating the definite integral of a function. "
            "It uses parabolic segments to estimate the area under the curve."
        )
        self.method_formula = (
            "∫[a, b] f(x) dx ≈ (b - a) / 6 * (f(a) + 4 * f((a + b) / 2) + f(b))"
        )
        self.method_example = (
            "For example, to approximate the integral of f(x) = x^2 from 0 to 2, "
            "we can use Simpson's Rule with n = 2 subintervals."
        )
        self.method_code = (
            "def simpson(f, a, b, n):\n"
            "    h = (b - a) / n\n"
            "    integral = f(a) + f(b)\n"
            "    for i in range(1, n, 2):\n"
            "        integral += 4 * f(a + i * h)\n"
            "    for i in range(2, n - 1, 2):\n"
            "        integral += 2 * f(a + i * h)\n"
            "    integral *= h / 3\n"
            "    return integral"
        )   
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["method_name"] = self.method_name
        context["method_description"] = self.method_description
        context["method_formula"] = self.method_formula
        context["method_example"] = self.method_example
        context["method_code"] = self.method_code
        return context
    def post(
            self,
            request: HttpRequest,
            *args,
            **kwargs
    ) -> HttpResponse:
        context = self.get_context_data(**kwargs)
        # Aquí puedes manejar la lógica para la solicitud POST
        return self.render_to_response(context)
    def post(
        self, request: HttpRequest, *args: object, **kwargs: object
    ) -> HttpResponse:
        context = self.get_context_data()
        template_data = {}

        function_input = request.POST.get("function", "")
        a_input = request.POST.get("a", "")
        b_input = request.POST.get("b", "")
        n_input = request.POST.get("n", "")

        response_validation = self.method_service.validate_input(
            function_input, a_input, b_input, n_input
        )

        if isinstance(response_validation, str):
            error_response = {
                "message_method": response_validation,
                "is_successful": False,
                "have_solution": False,
            }
            template_data = template_data | error_response
            context["template_data"] = template_data
            return self.render_to_response(context)

        function, a, b, n = response_validation

        method_response = self.method_service.solve(
            function=function,
            a=a,
            b=b,
            n=n,
        )

        if method_response["is_successful"]:
            plot_function(
                method_response["polynomial"],
                method_response["x_values"],
                method_response["y_values"],
                method_response["a"],
                method_response["b"],
                method_response["n"],
                method_name=self.method_name,
                function=function,
            )
        template_data = template_data | method_response
        context["template_data"] = template_data    
        return self.render_to_response(context)