from django.shortcuts import render, redirect
from .forms import ProblemForm, SolveForm
from .algorithms.simplex import SimplexSolver

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
    else:
        form = ProblemForm()
    return render(request, 'simplex_app/index.html', {'form': form})

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
            
            # Formatear resultados
            context = {
                'status': status,
                'objective_value': objective_value,
                'solution': solution,
                'steps': steps,
                'problem_type': problem_type,
                'num_vars': num_vars,
                'solver': solver,
            }
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