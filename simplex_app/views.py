from django.shortcuts import render, redirect
from .forms import ProblemForm, SolveForm
from .algorithms.simplex import SimplexSolver
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
import datetime
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Para entornos sin display
import matplotlib.pyplot as plt
import os
from django.conf import settings

def portada(request):
    """
    Vista para la portada de la aplicación Simplex.
    Redirige a la página de inicio del problema.
    """
    return render(request, 'simplex_app/base.html')

def index(request):
    if request.method == 'POST':
        form = ProblemForm(request.POST)
        if form.is_valid():
            request.session['num_vars'] = form.cleaned_data['num_variables']
            request.session['num_cons'] = form.cleaned_data['num_constraints']
            request.session['problem_type'] = form.cleaned_data['problem_type']
            return redirect('simplex_app:solve')
        # Si el formulario no es válido, vuelve a mostrar el formulario con errores
        return render(request, 'simplex_app/index.html', {'form': form})
    else:
        form = ProblemForm()
        return render(request, 'simplex_app/index.html', {'form': form})

def plot_feasible_region(c, A, b, solution, problem_type):
    """
    Genera y guarda la gráfica de la región factible para problemas de 2 variables.
    """
    import numpy as np
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import os
    x = np.linspace(0, max(b)*1.2, 400)
    plt.figure(figsize=(7, 6))
    for i, (a, bi) in enumerate(zip(A, b)):
        if a[1] != 0:
            y = (bi - a[0]*x) / a[1]
            plt.plot(x, y, label=f'Restricción {i+1}')
            plt.fill_between(x, y, max(b)*1.2, alpha=0.1)
        else:
            plt.axvline(x=bi/a[0], label=f'Restricción {i+1}')
    plt.xlim(0, max(b)*1.2)
    plt.ylim(0, max(b)*1.2)
    plt.xlabel('x1')
    plt.ylabel('x2')
    plt.title('Zona factible')
    # Dibujar la solución óptima
    if solution is not None:
        plt.plot(solution[0], solution[1], 'ro', label='Óptimo')
    plt.legend()
    plt.grid(True)
    # Guardar imagen en la carpeta estática
    static_img_dir = os.path.join(settings.BASE_DIR, 'simplex_app', 'static', 'simplex_app', 'img')
    os.makedirs(static_img_dir, exist_ok=True)
    img_path = os.path.join(static_img_dir, 'zona_factible.png')
    plt.savefig(img_path)
    plt.close()

def solve(request):
    num_vars = request.session.get('num_vars', 2)
    num_cons = request.session.get('num_cons', 2)
    problem_type = request.session.get('problem_type', 'max')
    
    if request.method == 'POST':
        form = SolveForm(request.POST, num_vars=num_vars, num_cons=num_cons, problem_type=problem_type)
        if form.is_valid():
            # Extraer coeficientes de la función objetivo
            c = [form.cleaned_data[f'obj_coeff_{i}'] for i in range(num_vars)]
            
            # Extraer restricciones
            A = []
            b = []
            for i in range(num_cons):
                constraint = [form.cleaned_data[f'cons_{i}_coeff_{j}'] for j in range(num_vars)]
                rhs = form.cleaned_data[f'cons_{i}_rhs']
                A.append(constraint)
                b.append(rhs)
            
            # Resolver el problema
            solver = SimplexSolver(c, A, b, problem_type)
            status, objective_value, solution, steps = solver.solve()
            
            # Asegurar que solution sea una lista serializable
            if hasattr(solution, 'tolist'):
                solution_list = solution.tolist()
            else:
                solution_list = list(solution)
            request.session['solution'] = solution_list
            request.session['objective_value'] = float(objective_value)
            request.session['status'] = status
            
            # En la función solve, guardar los pasos en la sesión para exportar
            if hasattr(steps, 'tolist'):
                steps_list = steps.tolist()
            else:
                steps_list = steps
            request.session['steps'] = steps_list
            
            # Conversión profunda de steps para serialización
            def deep_convert(obj):
                if isinstance(obj, np.ndarray):
                    return obj.tolist()
                elif isinstance(obj, dict):
                    return {k: deep_convert(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [deep_convert(v) for v in obj]
                elif isinstance(obj, np.integer):
                    return int(obj)
                elif isinstance(obj, np.floating):
                    return float(obj)
                else:
                    return obj
            steps_serializable = deep_convert(steps)
            request.session['steps'] = steps_serializable
            
            # Formatear resultados
            rango_vars = range(len(steps[0]['tableau'][0]) - 1) if steps and 'tableau' in steps[0] else []
            nombres_vars = []
            for i in rango_vars:
                if i < num_vars:
                    nombres_vars.append(f"x{i+1}")
                else:
                    nombres_vars.append(f"s{i+1-num_vars}")
            context = {
                'status': status,
                'objective_value': objective_value,
                'solution': solution,
                'steps': steps,
                'problem_type': problem_type,
                'num_vars': num_vars,
                'solver': solver,
                'nombres_vars': nombres_vars,
                'rango_vars': rango_vars,
            }
            # Generar gráfica si hay dos variables
            if num_vars == 2:
                plot_feasible_region(c, A, b, solution, problem_type)
                zona_factible_url = 'simplex_app/img/zona_factible.png'
            else:
                zona_factible_url = None
            context['zona_factible_url'] = zona_factible_url
            
            return render(request, 'simplex_app/results.html', context)
    else:
        form = SolveForm(num_vars=num_vars, num_cons=num_cons, problem_type=problem_type)
    
    return render(request, 'simplex_app/solve.html', {
        'form': form,
        'num_vars': num_vars,
        'num_cons': num_cons,
        'problem_type': problem_type,
        'var_range': range(num_vars),
        'cons_range': range(num_cons),
    })

def results(request):
    # Esta vista se maneja en la vista solve()
    return redirect('simplex_app:index')

def exportar_pdf(request):
    # Obtener los datos de la última solución de la sesión
    num_vars = request.session.get('num_vars', 2)
    solution = request.session.get('solution')
    objective_value = request.session.get('objective_value')
    status = request.session.get('status')
    pasos = request.session.get('steps', [])
    iteraciones = len(pasos)
    rango_vars = range(len(pasos[0]['tableau'][0]) - 1) if pasos and 'tableau' in pasos[0] else []
    if not solution or not objective_value:
        return HttpResponse('No hay solución para exportar.', status=400)

    resultados = {f"x{i+1}": v for i, v in enumerate(solution)}
    fecha = datetime.datetime.now().strftime('%d/%m/%Y %H:%M')
    
    # Para mostrar nombres de variables (x1, x2, ..., s1, s2, ...)
    nombres_vars = []
    for i in rango_vars:
        if i < num_vars:
            nombres_vars.append(f"x{i+1}")
        else:
            nombres_vars.append(f"s{i+1-num_vars}")
    
    html_string = render_to_string('simplex_app/solucion_pdf.html', {
        'resultados': resultados,
        'valor_optimo': objective_value,
        'fecha': fecha,
        'status': status,
        'pasos': pasos,
        'iteraciones': iteraciones,
        'rango_vars': rango_vars,
        'nombres_vars': nombres_vars,
        'num_vars': num_vars,
    })
    pdf_file = HTML(string=html_string).write_pdf()
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="solucion_simplex.pdf"'
    return response