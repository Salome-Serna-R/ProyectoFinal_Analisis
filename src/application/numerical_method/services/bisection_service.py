import math
from src.application.shared.utils.plot_function import plot_function
from src.application.numerical_method.interfaces.interval_method import (
    IntervalMethod,
)

"""
El método de bisección es una técnica numérica para encontrar raíces de ecuaciones no lineales en un intervalo [a,b],
donde la función f(x) es continua y se cumple que f(a)×f(b)<0, lo que indica la existencia de al menos una raíz.
"""

class BisectionService(IntervalMethod):
    def solve(
        self,
        function_f: str,
        interval_a: float,
        interval_b: float,
        tolerance: float,
        max_iterations: int,
        precision: bool = False,
    ) -> dict:

        def evaluate_fx(x_val):
            try:
                return eval(function_f, {"x": x_val, "math": math})
            except Exception as e:
                raise ValueError(f"Error al evaluar f(x) en x = {x_val}: {str(e)}")

        interval = [interval_a, interval_b]
        table = {}
        current_iteration = 1
        current_error = math.inf

        try:
            fa = evaluate_fx(interval[0])
            fb = evaluate_fx(interval[1])
        except Exception as e:
            return {"error": str(e)}

        if fa == 0:
            return {
                "message_method": f"{interval[0]} es raíz de f(x) y es el extremo inferior del intervalo",
                "table": {},
                "is_successful": True,
                "have_solution": True,
                "root": interval[0],
            }

        elif fb == 0:
            return {
                "message_method": f"{interval[1]} es raíz de f(x) y es el extremo superior del intervalo",
                "table": {},
                "is_successful": True,
                "have_solution": True,
                "root": interval[1],
            }

        while current_iteration <= max_iterations:
            table[current_iteration] = {}
            Xn = (interval[0] + interval[1]) / 2

            try:
                f = evaluate_fx(Xn)
            except Exception as e:
                return {
                    "message_method": f"Error al evaluar la función en el punto medio: {str(e)}.",
                    "table": table,
                    "is_successful": False,
                    "have_solution": False,
                    "root": 0.0,
                }

            table[current_iteration]["iteration"] = current_iteration
            table[current_iteration]["approximate_value"] = Xn
            table[current_iteration]["f_evaluated"] = f

            if current_iteration == 1:
                table[current_iteration]["error"] = current_error
            else:
                prev_xn = table[current_iteration - 1]["approximate_value"]
                if precision:
                    current_error = abs(Xn - prev_xn)
                else:
                    current_error = abs((Xn - prev_xn) / Xn)
                table[current_iteration]["error"] = current_error

            if f == 0:
                return {
                    "message_method": f"{Xn} es raíz de f(x)",
                    "table": table,
                    "is_successful": True,
                    "have_solution": True,
                    "root": Xn,
                }
            elif current_error < tolerance:
                return {
                    "message_method": f"{Xn} es una aproximación de la raíz de f(x) con un error de {current_error}",
                    "table": table,
                    "is_successful": True,
                    "have_solution": True,
                    "root": Xn,
                }

            if fa * f < 0:
                interval = [interval[0], Xn]
                fb = f  # actualizar fb para el nuevo intervalo
            else:
                interval = [Xn, interval[1]]
                fa = f  # actualizar fa para el nuevo intervalo

            current_iteration += 1

        return {
            "message_method": f"El método funcionó correctamente pero no se encontró solución en {max_iterations} iteraciones",
            "table": table,
            "is_successful": True,
            "have_solution": False,
            "root": 0.0,
        }

    def validate_input(
        self,
        interval_a: float,
        interval_b: float,
        tolerance: float,
        max_iterations: int,
        function_f: str,
    ) -> str | bool:

        def evaluate_fx(x_val):
            return eval(function_f, {"x": x_val, "math": math})

        if not isinstance(tolerance, (int, float)) or tolerance <= 0:
            plot_function(function_f, False, [(interval_a, 0), (interval_b, 0)])
            return "La tolerancia debe ser un número positivo"

        if not isinstance(max_iterations, int) or max_iterations <= 0:
            plot_function(function_f, False, [(interval_a, 0), (interval_b, 0)])
            return "El máximo número de iteraciones debe ser un entero positivo."

        try:
            fa = evaluate_fx(interval_a)
            fb = evaluate_fx(interval_b)
        except ValueError:
            plot_function(function_f, False, [(interval_a, 0), (interval_b, 0)])
            return "Error: Valor fuera del dominio permitido para la función. Verifique que los valores de 'x' sean válidos."
        except SyntaxError:
            return "Error de sintaxis en la función ingresada."
        except NameError:
            return "Error de nombre en la función ingresada: use 'x' y funciones de 'math' correctamente."
        except ZeroDivisionError:
            plot_function(function_f, False, [(interval_a, 0), (interval_b, 0)])
            return "Error: División por cero en la función."
        except Exception as e:
            return f"Error desconocido: {str(e)}"

        if fa * fb > 0:
            plot_function(function_f, False, [(interval_a, 0), (interval_b, 0)])
            return "El intervalo es inadecuado, recuerde que f(a) * f(b) debe ser < 0 para garantizar una raíz."

        return True
