from django import forms

class UploadFileForm(forms.Form):
    title = forms.CharField(max_length=50, required=False)
    csvFile  = forms.FileField()

    def __init__(self,*args, **kwargs):
        super(forms.Form, self).__init__(*args, **kwargs)
        for field in self.fields.itervalues():
            field.widget.attrs['class'] = 'fullwidth'

