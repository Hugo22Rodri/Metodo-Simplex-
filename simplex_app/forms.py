from django import forms

class ProblemForm(forms.Form):
    PROBLEM_TYPES = (
        ('max', 'Maximizar'),
        ('min', 'Minimizar'),
    )
    
    problem_type = forms.ChoiceField(
        choices=PROBLEM_TYPES,
        label='Tipo de Problema',
        initial='max',
        widget=forms.RadioSelect
    )
    
    num_variables = forms.IntegerField(
        label='Número de Variables',
        min_value=1,
        max_value=10,
        initial=2,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    
    num_constraints = forms.IntegerField(
        label='Número de Restricciones',
        min_value=1,
        max_value=10,
        initial=2,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

class SolveForm(forms.Form):
    def __init__(self, *args, **kwargs):
        num_vars = kwargs.pop('num_vars')
        num_cons = kwargs.pop('num_cons')
        problem_type = kwargs.pop('problem_type')
        super(SolveForm, self).__init__(*args, **kwargs)
        
        # Función objetivo
        for i in range(num_vars):
            self.fields[f'obj_coeff_{i}'] = forms.FloatField(
                label=f'x{i+1}',
                initial=0,
                widget=forms.NumberInput(attrs={'class': 'form-control'})
            )
        
        # Restricciones
        for i in range(num_cons):
            for j in range(num_vars):
                self.fields[f'cons_{i}_coeff_{j}'] = forms.FloatField(
                    label='',
                    initial=0,
                    widget=forms.NumberInput(attrs={'class': 'form-control'})
                )
            self.fields[f'cons_{i}_rhs'] = forms.FloatField(
                label='',
                initial=0,
                widget=forms.NumberInput(attrs={'class': 'form-control'})
            )
        
        # Campo oculto para el tipo de problema
        self.fields['problem_type'] = forms.CharField(
            initial=problem_type,
            widget=forms.HiddenInput()
        )