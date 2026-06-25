# analyzerapp/forms.py

from django import forms
from .models import Candidate
import re

class ResumeUploadForm(forms.ModelForm):
    class Meta:
        model = Candidate
        fields = ['resume_file']


from django import forms
from .models import Candidate

class CandidateForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}), label='Password')
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}), label='Confirm Password')
    class Meta:
        model = Candidate
        fields = ['name', 'email', 'phone', 'address', 'state']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 2}),
            
        
        }
    def clean_name(self):
        name = (self.cleaned_data.get('name') or '').strip()
        if len(name) < 2:
            raise forms.ValidationError("Enter your full name.")
        if not re.match(r"^[A-Za-z][A-Za-z .'-]*$", name):
            raise forms.ValidationError("Name should contain only letters, spaces, dots, apostrophes, or hyphens.")
        return name

    def clean_email(self):
        email = (self.cleaned_data.get('email') or '').strip().lower()
        if email and Candidate.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        if email and not re.match(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$", email):
            raise forms.ValidationError("Enter a valid email address.")
        return email

    def clean_phone(self):
        phone = re.sub(r"\s+", "", self.cleaned_data.get('phone') or '')
        if not re.match(r"^(\+91)?[6-9]\d{9}$", phone):
            raise forms.ValidationError("Enter a valid Indian mobile number starting with 6, 7, 8, or 9.")
        return phone

    def clean_address(self):
        address = (self.cleaned_data.get('address') or '').strip()
        if len(address) < 10:
            raise forms.ValidationError("Address should be at least 10 characters.")
        return address

    def clean_state(self):
        state = (self.cleaned_data.get('state') or '').strip()
        if len(state) < 2:
            raise forms.ValidationError("Enter your state.")
        return state

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm = cleaned_data.get('confirm_password')
        if password and confirm and password != confirm:
            raise forms.ValidationError("Passwords do not match")
        if password and Candidate.objects.filter(password=password).exists():
            raise forms.ValidationError("This password is already used. Please choose a different password.")
        if password:
            if len(password) < 8:
                raise forms.ValidationError("Password must be at least 8 characters.")
            if not re.search(r"[A-Z]", password):
                raise forms.ValidationError("Password must include at least one uppercase letter.")
            if not re.search(r"[a-z]", password):
                raise forms.ValidationError("Password must include at least one lowercase letter.")
            if not re.search(r"\d", password):
                raise forms.ValidationError("Password must include at least one number.")
            if not re.search(r"[^A-Za-z0-9]", password):
                raise forms.ValidationError("Password must include at least one special character.")
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.password = self.cleaned_data['password']  # ✅ save password to model
        if commit:
            instance.save()
        return instance
        
class LoginForm(forms.Form):
    email = forms.EmailField(label='Email')
    password = forms.CharField(widget=forms.PasswordInput(attrs={'autocomplete': 'current-password'}), label='Password')
