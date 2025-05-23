from django.shortcuts import render


def auto_compare_view(request):
    if request.method == 'POST':
        function_str = request.POST['function_f']
        a = float(request.POST['interval_a'])
        b = float(request.POST['interval_b'])
        tol = float(request.POST['tolerance'])
        max_iter = int(request.POST['max_iterations'])
        precision = int(request.POST['precision'])

        results = []
        # Importar los métodos de solución
        from src.application.numerical_method.services.bisection_service import BisectionService as bisection_method
        from src.application.numerical_method.services.regula_falsi_service import RegulaFalsiService as false_position_method
        from src.application.numerical_method.services.fixed_point_service import FixedPointService as fixed_point_method
        from src.application.numerical_method.services.newton_raphson_service import NewtonService as newton_method
        from src.application.numerical_method.services.secant_service import SecantService as secant_method
        from src.application.numerical_method.services.multiple_roots_1_service import MultipleRoots1Service as multiple_roots_1_method
        from src.application.numerical_method.services.multiple_roots_2_service import MultipleRoots2Service as multiple_roots_2_method
        from src.application.numerical_method.services.regula_falsi_service import RegulaFalsiService as regula_falsi_method

        #Cambiar la funcion a un string
        function_str = str(function_str)
        # Método de bisección
        try:
            result = bisection_method.solve(function_str, a, b, tol, max_iter, precision)
            # Si la tabla tiene datos, obtiene el error de la última iteración.
            if result['table']:
                last_iteration = max(result['table'].keys())
                last_error = result['table'][last_iteration].get('error', None)
            else:
                last_error = None
            results.append({
                'method': 'Bisección',
                'root': result['root'],
                'iterations': len(result['table']),  # o lo que represente tus iteraciones
                'error': last_error,
            })

        except Exception as e:
            results.append({'method': 'Bisección', 'error_msg': str(e)})

        # Falsa posición
        try:
            result = false_position_method.solve(function_str, a, b, tol, max_iter, precision)
            last_error = None
            if result['table']:
                last_iteration = max(result['table'].keys())
                last_error = result['table'][last_iteration].get('error', None)
            results.append({
                'method': 'Falsa Posición',
                'root': result['root'],
                'iterations': len(result['table']),
                'error': last_error,
            })
        except Exception as e:
            results.append({'method': 'Falsa Posición', 'error_msg': str(e)})

        # Newton-Raphson
        try:
            result = newton_method.solve(function_str, a, tol, max_iter, precision)
            results.append({
                'method': 'Newton-Raphson',
                'root': result['root'],
                'iterations': len(result['table']),
                'error': last_error,
            })
        except Exception as e:
            results.append({'method': 'Newton-Raphson', 'error_msg': str(e)})

        # Secante 
        try:
            result = secant_method.solve(function_str, a, b, tol, max_iter, precision)
            results.append({
                'method': 'Secante',
                'root': result['root'],
                'iterations': len(result['table']),
                'error': last_error,
            })
        except Exception as e:
            results.append({'method': 'Secante', 'error_msg': str(e)})

        # Punto fijo
        """
        try:

            root, iterations, error = fixed_point_method(function_str, a, tol, max_iter)
            results.append({
                'method': 'Punto Fijo',
                'root': root,
                'iterations': iterations,
                'error': error,
            })
        except Exception as e:
            results.append({'method': 'Punto Fijo', 'error_msg': str(e)})

        # Raíces múltiples 1
        try:

            root, iterations, error = multiple_roots_1_method(function_str, a, tol, max_iter)
            results.append({
                'method': 'Raíces Múltiples 1',
                'root': root,
                'iterations': iterations,
                'error': error,
            })
        except Exception as e:
            results.append({'method': 'Raíces Múltiples 1', 'error_msg': str(e)})

        # Raíces múltiples 2
        try:

            root, iterations, error = multiple_roots_2_method(function_str, a, tol, max_iter)
            results.append({
                'method': 'Raíces Múltiples 2',
                'root': root,
                'iterations': iterations,
                'error': error,
            })
        except Exception as e:
            results.append({'method': 'Raíces Múltiples 2', 'error_msg': str(e)})
    """

        #Resultados imprimir
        for result in results:
            if 'error_msg' in result:
                print(f"{result['method']}: {result['error_msg']}")
            else:
                print(f"{result['method']}: Raíz = {result['root']}, Iteraciones = {result['iterations']}, Error = {result['error']}")

        return render(request, 'ec_nolineales.html', {'results': results})

    return render(request, 'ec_nolineales.html')
