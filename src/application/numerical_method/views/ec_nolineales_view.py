from django.views.generic import TemplateView
from src.application.numerical_method.interfaces.interval_method import (
    IntervalMethod,
)
from src.application.numerical_method.containers.numerical_method_container import (
    NumericalMethodContainer,
)
from dependency_injector.wiring import inject, Provide
from src.application.shared.utils.plot_function import plot_function
from django.http import HttpRequest, HttpResponse

#Este es el controlador de la vista de ecuaciones no lineales donde pedimos TODOS los datos necesarios para ejecutar todos los metodos
# y graficar la funcion además de guardar los resultados en uun pdf para descargarlo como el informe comparativo de los metodos
class NonLinearView(TemplateView):
    template_name = "ec_nolineales.html"

