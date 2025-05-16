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

class TrapezoidalView(TemplateView):
    template_name = "numerical_method/trapezoidal.html"

    @inject
    def __init__(
        self,
        *args,
        #trapezoidal_service: Trapezoidal_Service = Provide[NumericalMethodContainer.trapezoidal_service],
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        #self.trapezoidal_service = trapezoidal_service

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["method_name"] = self.trapezoidal_service.method_name
        context["method_description"] = self.trapezoidal_service.method_description
        context["method_formula"] = self.trapezoidal_service.method_formula
        context["method_example"] = self.trapezoidal_service.method_example
        context["method_code"] = self.trapezoidal_service.method_code
        return context
#TERMINARRRRRRRRR 