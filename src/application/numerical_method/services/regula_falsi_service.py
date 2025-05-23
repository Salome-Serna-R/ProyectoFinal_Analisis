import math
from src.application.shared.utils.plot_function import plot_function
from src.application.numerical_method.interfaces.interval_method import (
    IntervalMethod,
)

"""

El método de regla falsa es una técnica numérica para encontrar raíces de ecuaciones no lineales en un intervalo [a,b], donde la función f(x) es continua y se cumple que f(a)×f(b)<0, lo que indica la existencia de al menos una raíz. El proceso consiste en calcular el punto de intersección de la linea secante entre (a,f(a)) y (b,f(b)) con el eje x (c=(a*f(b)-b*f(a))/(f(b)-f(a))) y evaluar la función en este punto. Si f(c) es cero, c es la raíz. De lo contrario, se elige el subintervalo [a,c] o [c,b] donde la multiplicación de las funciones cambia de signo, y se repite el proceso hasta aproximar la raíz con la precisión deseada.

"""


class RegulaFalsiService(IntervalMethod):
    def solve(
        self,
        function_f: str,
        interval_a: float,
        interval_b: float,
        tolerance: float,
        max_iterations: int,
        precision: bool = False,
        **kwargs,
    ) -> dict:

        # Definición del intervalo inicial.
        interval = [interval_a, interval_b]

        # Definición de tabla que contiene todo el proceso
        table = {}

        # Inicializamos el contador de iteraciones
        current_iteration = 1

        # Inicializamos el error actual con infinito
        current_error = math.inf

        # Definimos la función f(x)
        try:
            f = lambda x: eval(function_f, {"x": x, "math": math})
        except Exception as e:
            return {
                "message_method": f"Error al definir la función: {str(e)}",
                "table": {},
                "is_successful": False,
                "have_solution": False,
                "root": 0.0,
            }

        # Evaluamos la función en los extremos del intervalo
        try:
            fa = f(interval[0])
            fb = f(interval[1])
        except Exception as e:
            return {
                "message_method": f"Error al evaluar f en los extremos del intervalo: {str(e)}",
                "table": {},
                "is_successful": False,
                "have_solution": False,
                "root": 0.0,
            }

        # Verificamos si alguno de los extremos es raíz
        if fa == 0:
            return {
                "message_method": f"{interval[0]} es raíz de f(x) y es el extremo inferior del intervalo.",
                "table": {},
                "is_successful": True,
                "have_solution": True,
                "root": interval[0],
            }

        if fb == 0:
            return {
                "message_method": f"{interval[1]} es raíz de f(x) y es el extremo superior del intervalo.",
                "table": {},
                "is_successful": True,
                "have_solution": True,
                "root": interval[1],
            }

        # Verificamos que el denominador no sea cero
        if fb - fa == 0:
            return {
                "message_method": "Error: división por cero en la fórmula de Regla Falsa (f(b) - f(a) = 0)",
                "table": {},
                "is_successful": False,
                "have_solution": False,
                "root": 0.0,
            }

        # Iteraciones del método
        while current_iteration <= max_iterations:
            table[current_iteration] = {}

            # Fórmula de la Regla Falsa
            Xn = (interval[0] * fb - interval[1] * fa) / (fb - fa)

            try:
                fxn = f(Xn)
            except Exception as e:
                return {
                    "message_method": f"Error al evaluar la función en Xn: {str(e)}.",
                    "table": table,
                    "is_successful": True,
                    "have_solution": False,
                    "root": 0.0,
                }

            # Guardar datos de la iteración
            table[current_iteration]["iteration"] = current_iteration
            table[current_iteration]["approximate_value"] = Xn
            table[current_iteration]["f_evaluated"] = fxn

            if current_iteration == 1:
                table[current_iteration]["error"] = current_error
            else:
                if precision:
                    current_error = abs(
                        table[current_iteration]["approximate_value"]
                        - table[current_iteration - 1]["approximate_value"]
                    )
                else:
                    current_error = abs(
                        (
                            table[current_iteration]["approximate_value"]
                            - table[current_iteration - 1]["approximate_value"]
                        )
                        / table[current_iteration]["approximate_value"]
                    )
                table[current_iteration]["error"] = current_error

            # Verificamos condiciones de parada
            if fxn == 0:
                return {
                    "message_method": f"{Xn} es raíz de f(x)",
                    "table": table,
                    "is_successful": True,
                    "have_solution": True,
                    "root": Xn,
                }
            elif current_error < tolerance:
                return {
                    "message_method": f"{Xn} es una aproximación de la raíz con error {current_error}",
                    "table": table,
                    "is_successful": True,
                    "have_solution": True,
                    "root": Xn,
                }

            # Actualización del intervalo
            if fa * fxn < 0:
                interval[1] = Xn
                fb = fxn
            else:
                interval[0] = Xn
                fa = fxn

            current_iteration += 1

        # Si se llega al máximo de iteraciones
        return {
            "message_method": f"El método funcionó pero no encontró raíz en {max_iterations} iteraciones",
            "table": table,
            "is_successful": True,
            "have_solution": False,
            "root": 0.0,
        }

