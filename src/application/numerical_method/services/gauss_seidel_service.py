import numpy as np
from src.application.numerical_method.interfaces.matrix_method import MatrixMethod
from src.application.shared.utils.plot_matrix_solution import plot_matrix_solution, plot_system_equations


class GaussSeidelService(MatrixMethod):
    def solve(
        self,
        A: list[list[float]],
        b: list[float],
        x0: list[float],
        tolerance: float,
        max_iterations: int,
        precision: int,
        **kwargs,
    ) -> dict:

        A = np.array(A)
        b = np.array(b)
        x0 = np.array(x0)

        n = len(b)
        x1 = np.zeros_like(x0)
        current_error = tolerance + 1
        current_iteration = 0
        table = {}

        # Forma matricial como en MATLAB
        D = np.diag(np.diag(A))
        L = -np.tril(A, -1)
        U = -np.triu(A, 1)

        T = np.linalg.inv(D - L) @ U
        C = np.linalg.inv(D - L) @ b
        spectral_radius = max(abs(np.linalg.eigvals(T)))

        while current_error > tolerance and current_iteration < max_iterations:
            x1 = T @ x0 + C
            current_error = np.linalg.norm(x1 - x0, ord=np.inf)

            # Aplicar precisión
            if precision == 1:
                x1_rounded = [round(value, len(str(tolerance).split(".")[1])) for value in x1]
                error_rounded = round(current_error, len(str(tolerance).split(".")[1]))
            elif precision == 0:
                significant_digits = len(str(tolerance).replace("0.", ""))
                x1_rounded = [float(f"{value:.{significant_digits}g}") for value in x1]
                error_rounded = float(f"{current_error:.{significant_digits}g}")

            table[current_iteration + 1] = {
                "iteration": current_iteration + 1,
                "X": x1_rounded,
                "Error": error_rounded,
            }

            x0 = x1
            current_iteration += 1

        result = {}
        if current_error <= tolerance:
            result = {
                "message_method": f"Aproximación de la solución con tolerancia = {tolerance} y el radio espectral es de = {spectral_radius}",
                "table": table,
                "is_successful": True,
                "have_solution": True,
                "solution": x1_rounded,
                "spectral_radius": spectral_radius,
            }
        elif current_iteration >= max_iterations:
            result = {
                "message_method": f"El método funcionó correctamente, pero no se encontró una solución en {max_iterations} iteraciones y el radio espectral es de = {spectral_radius}.",
                "table": table,
                "is_successful": True,
                "have_solution": False,
                "solution": x1_rounded,
                "spectral_radius": spectral_radius,
            }
        else:
            result = {
                "message_method": f"El método falló al intentar aproximar una solución",
                "table": table,
                "is_successful": True,
                "have_solution": False,
                "solution": [],
            }

        if len(A) == 2:
            plot_matrix_solution(table, x1_rounded, spectral_radius)
            plot_system_equations(A.tolist(), b.tolist(), x1_rounded)

        return result

    def validate_input(
        self,
        matrix_a_raw: str,
        vector_b_raw: str,
        initial_guess_raw: str,
        tolerance: float,
        max_iterations: int,
        matrix_size: int,
        **kwargs,
    ) -> str | list:

        if not isinstance(tolerance, (int, float)) or tolerance <= 0:
            return "La tolerancia debe ser un número positivo"

        if not isinstance(max_iterations, int) or max_iterations <= 0:
            return "El máximo número de iteraciones debe ser un entero positivo."

        try:
            A = [
                [float(num) for num in row.strip().split()]
                for row in matrix_a_raw.split(";")
                if row.strip()
            ]

            b = [float(num) for num in vector_b_raw.strip().split()]
            x0 = [float(num) for num in initial_guess_raw.strip().split()]
        except ValueError:
            return "Todas las entradas deben ser numéricas."

        if len(A) != matrix_size or any(len(row) != matrix_size for row in A):
            return f"La matriz A debe ser cuadrada y coincidir con el tamaño seleccionado ({matrix_size}x{matrix_size})."

        if len(A) > 7 or any(len(row) != len(A) for row in A):
            return "La matriz A debe ser cuadrada de hasta 7x7."
        
        if np.any(np.diag(A) == 0):
            return "El método Gauss-Seidel no puede continuar: la matriz A tiene ceros en su diagonal."

        if len(b) != len(A) or len(x0) != len(A):
            return "El vector b y x0 deben ser compatibles con el tamaño de la matriz A."

        return [A, b, x0]
