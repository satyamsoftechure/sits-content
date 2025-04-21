# forms.py
from django import forms
from .models import BlogPost  # Import your model

class BlogGeneratorForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = ['title', 'keywords']  # Adjust fields as needed
        widgets = {
            'title': forms.Textarea(attrs={'placeholder': 'Enter a topic or title to generate Content   '}),
            'keywords': forms.TextInput(attrs={'placeholder': 'keywords like: features, specification, etc'}),
        }

    def __str__(self):
        return self.instance.title  # Use instance to get the title of the model instance
