import numpy as np
import fractions

class SimplexSolver:
    def __init__(self, c, A, b, problem_type='max'):
        """
        Inicializa el solucionador simplex.
        
        :param c: Coeficientes de la función objetivo
        :param A: Matriz de restricciones
        :param b: Vector de lados derechos
        :param problem_type: 'max' para maximización, 'min' para minimización
        """
        self.problem_type = problem_type
        self.c = np.array(c, dtype=float)
        self.A = np.array(A, dtype=float)
        self.b = np.array(b, dtype=float)
        self.steps = []
        self.solution = None
        self.objective_value = None
        self.status = None
        self.basic_vars = None
        self.iterations = 0
        
    def solve(self):
        """Resuelve el problema de programación lineal."""
        # Convertir minimización a maximización
        if self.problem_type == 'min':
            self.c = -self.c
        
        # Agregar variables de holgura
        m, n = self.A.shape
        self.tableau = np.zeros((m + 1, n + m + 1))
        self.tableau[:-1, :n] = self.A
        self.tableau[:-1, n:n+m] = np.eye(m)
        self.tableau[:-1, -1] = self.b
        self.tableau[-1, :n] = -self.c
        
        # Variables básicas (variables de holgura)
        self.basic_vars = list(range(n, n + m))
        self.steps.append({
            'tableau': self.tableau.copy(),
            'basic_vars': self.basic_vars.copy(),
            'iteration': self.iterations,
            'message': 'Tabla inicial'
        })
        
        while True:
            self.iterations += 1
            # Verificar optimalidad
            if np.all(self.tableau[-1, :-1] >= 0):
                self.status = 'Óptimo'
                break
                
            # Seleccionar variable entrante (más negativa en la fila objetivo)
            entering = np.argmin(self.tableau[-1, :-1])
            
            # Verificar si el problema es no acotado
            if np.all(self.tableau[:-1, entering] <= 0):
                self.status = 'No acotado'
                break
                
            # Seleccionar variable saliente (mínimo ratio)
            ratios = []
            for i in range(m):
                if self.tableau[i, entering] > 0:
                    ratios.append(self.tableau[i, -1] / self.tableau[i, entering])
                else:
                    ratios.append(float('inf'))
            leaving = np.argmin(ratios)
            
            # Actualizar variable básica
            self.basic_vars[leaving] = entering
            
            # Pivoteo
            pivot = self.tableau[leaving, entering]
            self.tableau[leaving, :] /= pivot
            for i in range(m + 1):
                if i != leaving:
                    factor = self.tableau[i, entering]
                    self.tableau[i, :] -= factor * self.tableau[leaving, :]
            
            self.steps.append({
                'tableau': self.tableau.copy(),
                'basic_vars': self.basic_vars.copy(),
                'entering': entering,
                'leaving': self.basic_vars[leaving] if leaving < len(self.basic_vars) else None,
                'iteration': self.iterations,
                'message': f'Iteración {self.iterations}'
            })
        
        # Obtener solución
        self._extract_solution(n)
        return self.status, self.objective_value, self.solution, self.steps
    
    def _extract_solution(self, n):
        """Extrae la solución del tableau final."""
        m = len(self.basic_vars)
        solution = np.zeros(n + m)
        
        for i in range(m):
            row = i
            col = self.basic_vars[i]
            solution[col] = self.tableau[row, -1]
        
        # Valor objetivo
        self.objective_value = self.tableau[-1, -1]
        if self.problem_type == 'min':
            self.objective_value = -self.objective_value
        
        self.solution = solution[:n]
    
    def format_tableau(self, tableau, decimals=2):
        """Formatea el tableau para visualización."""
        formatted = []
        for row in tableau:
            formatted_row = []
            for val in row:
                frac = fractions.Fraction(val).limit_denominator()
                if frac.denominator == 1:
                    formatted_row.append(str(int(frac)))
                else:
                    formatted_row.append(f"{frac.numerator}/{frac.denominator}")
            formatted.append(formatted_row)
        return formatted