from django import forms
from .models import Reservation
from datetime import date, timedelta


class ReservationForm(forms.ModelForm):
    """Form for creating reservations with date selection"""
    
    check_in_date = forms.DateField(
        label='Check-in Date',
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'min': str(date.today())
        }),
        required=True,
        help_text='Select check-in date'
    )
    
    check_out_date = forms.DateField(
        label='Check-out Date',
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'min': str(date.today() + timedelta(days=1))
        }),
        required=True,
        help_text='Select check-out date'
    )
    
    class Meta:
        model = Reservation
        fields = ['notes']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # If editing existing reservation, populate date fields
        if self.instance and self.instance.pk:
            if self.instance.check_in:
                self.fields['check_in_date'].initial = self.instance.check_in.date()
            if self.instance.check_out:
                self.fields['check_out_date'].initial = self.instance.check_out.date()
    
    def clean(self):
        cleaned_data = super().clean()
        check_in = cleaned_data.get('check_in_date')
        check_out = cleaned_data.get('check_out_date')
        
        if check_in and check_out:
            if check_in < date.today():
                raise forms.ValidationError('Check-in date cannot be in the past.')
            
            if check_out <= check_in:
                raise forms.ValidationError('Check-out date must be after check-in date.')
            
            # Ensure minimum 1 day stay
            if (check_out - check_in).days < 1:
                raise forms.ValidationError('Minimum stay is 1 day.')
        
        return cleaned_data

