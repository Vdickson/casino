from .models import ContactMessage
from django import forms
from .models import RechargeRequest, PaymentMethod

class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control fish-input',
                'placeholder': 'Enter your name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control fish-input',
                'placeholder': 'Enter your email'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control fish-input',
                'placeholder': 'Type your message here...',
                'rows': 4
            }),
        }




class RechargeForm(forms.ModelForm):
    class Meta:
        model = RechargeRequest
        fields = ['payment_method', 'amount', 'transaction_id', 'screenshot', 'notes']
        widgets = {
            'payment_method': forms.RadioSelect,
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['payment_method'].queryset = PaymentMethod.objects.filter(is_active=True)