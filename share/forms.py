from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from .models import UploadedFile

# File Upload Constants
ALLOWED_CONTENT_TYPES = [
    'application/pdf',
    'image/jpeg',
    'image/png',
    'text/plain',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'application/vnd.ms-powerpoint',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation',
]

MAX_UPLOAD_SIZE_MB = 10
MAX_UPLOAD_SIZE_BYTES = MAX_UPLOAD_SIZE_MB * 1024 * 1024


class UploadFileForm(forms.ModelForm):
    title = forms.CharField(
        max_length=255,
        label="File Title",
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter a descriptive title',
            'class': 'form-control'
        })
    )
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': 'Optional file description',
            'class': 'form-control'
        })
    )

    class Meta:
        model = UploadedFile
        fields = ['title', 'description', 'file']
        widgets = {
            'file': forms.ClearableFileInput(attrs={
                'class': 'form-control-file',
                'accept': ','.join(ALLOWED_CONTENT_TYPES)
            })
        }

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            if file.size > MAX_UPLOAD_SIZE_BYTES:
                raise ValidationError(
                    f'File size exceeds maximum limit of {MAX_UPLOAD_SIZE_MB} MB. '
                    f'Your file: {file.size/1024/1024:.2f} MB'
                )
            if file.content_type not in ALLOWED_CONTENT_TYPES:
                raise ValidationError(
                    f'Unsupported file type ({file.content_type}). '
                    'Allowed types: PDF, Word, Excel, PowerPoint, images, and text files.'
                )
            valid_extensions = ['.pdf', '.jpg', '.jpeg', '.png', '.txt',
                                '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx']
            if not any(file.name.lower().endswith(ext) for ext in valid_extensions):
                raise ValidationError('Invalid file extension.')
        return file


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(
        label="First Name",
        max_length=30,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter your first name',
            'class': 'form-control'
        }),
        required=True
    )
    last_name = forms.CharField(
        label="Last Name",
        max_length=30,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter your last name',
            'class': 'form-control'
        }),
        required=True
    )
    username = forms.CharField(
        label="Index Number",
        max_length=20,
        widget=forms.TextInput(attrs={
            'placeholder': 'e.g. UGR12345',
            'class': 'form-control'
        }),
        help_text="Your university index number (e.g. UGR12345)",
        validators=[
            RegexValidator(
                regex=r'^[A-Za-z0-9_-]+$',
                message="Index number can only contain letters, numbers, underscores, and hyphens."
            )
        ]
    )
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={
            'placeholder': 'your.email@example.com',
            'class': 'form-control'
        }),
        help_text="Enter a valid email address"
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2']
        help_texts = {
            'password1': "",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].help_text = self.Meta.help_texts['password1']
        self.fields['password2'].help_text = "Enter the same password as before for verification"

    def clean_email(self):
        email = self.cleaned_data['email'].lower()

        # ✅ If you don't want to force .edu emails, comment/remove this check
        # if not email.endswith(('.edu', '.ac.uk', '.edu.gh')):
        #     raise ValidationError("Please use your university email address.")

        if User.objects.filter(email=email).exists():
            raise ValidationError("This email is already registered.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['username'].lower()
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class IndexNumberLoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Index Number",
        max_length=150,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter your index number',
            'class': 'form-control',
            'autofocus': True
        })
    )
    password = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Enter your password',
            'class': 'form-control'
        })
    )

    error_messages = {
        'invalid_login': (
            "Please enter a correct index number and password. Note that both "
            "fields may be case-sensitive."
        ),
        'inactive': "This account is inactive.",
    }
