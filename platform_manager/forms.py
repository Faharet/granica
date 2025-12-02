from django import forms
from .models import FormResponse, BorderOfficerAssessment


class FormResponseForm(forms.ModelForm):
    class Meta:
        model = FormResponse
        # include all questionnaire fields
        fields = [
            'full_name_and_birth',
            'name_changed',
            'name_change_reason',
            'phones_emails',
            'military_service',
            'military_details',
            'criminal_record',
            'criminal_period_where',
            'criminal_offenses',
            'detained_abroad',
            'detained_when_why',
            'detained_where',
            'relatives_in_countries',
            'relatives_details',
            'relatives_wanted',
            'relatives_wanted_reason',
            'religious',
            'denomination',
            'visited_countries',
            'visited_countries_details',
            'deported',
            'deportation_details',
            'not_allowed_reason',
            'last_time_in_homeland',
        ]

        widgets = {
            'full_name_and_birth': forms.Textarea(attrs={'class': 'textarea textarea-bordered w-full', 'rows': 3}),
            'name_change_reason': forms.Textarea(attrs={'class': 'textarea textarea-bordered w-full', 'rows': 2}),
            'phones_emails': forms.Textarea(attrs={'class': 'textarea textarea-bordered w-full', 'rows': 2}),
            'military_details': forms.Textarea(attrs={'class': 'textarea textarea-bordered w-full', 'rows': 2}),
            'criminal_period_where': forms.Textarea(attrs={'class': 'textarea textarea-bordered w-full', 'rows': 2}),
            'criminal_offenses': forms.Textarea(attrs={'class': 'textarea textarea-bordered w-full', 'rows': 2}),
            'detained_when_why': forms.Textarea(attrs={'class': 'textarea textarea-bordered w-full', 'rows': 2}),
            'detained_where': forms.Textarea(attrs={'class': 'textarea textarea-bordered w-full', 'rows': 2}),
            'relatives_details': forms.Textarea(attrs={'class': 'textarea textarea-bordered w-full', 'rows': 3}),
            'relatives_wanted_reason': forms.Textarea(attrs={'class': 'textarea textarea-bordered w-full', 'rows': 2}),
            'denomination': forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
            'visited_countries_details': forms.Textarea(attrs={'class': 'textarea textarea-bordered w-full', 'rows': 3}),
            'deportation_details': forms.Textarea(attrs={'class': 'textarea textarea-bordered w-full', 'rows': 2}),
            'not_allowed_reason': forms.Textarea(attrs={'class': 'textarea textarea-bordered w-full', 'rows': 2}),
            'last_time_in_homeland': forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add common class to boolean fields (checkboxes)
        bool_fields = [
            'name_changed', 'military_service', 'criminal_record', 'detained_abroad',
            'relatives_in_countries', 'relatives_wanted', 'religious', 'visited_countries', 'deported'
        ]
        for f in bool_fields:
            if f in self.fields:
                # Use DaisyUI + Tailwind classes for consistent size, color and alignment
                self.fields[f].widget = forms.CheckboxInput(attrs={
                    'class': 'checkbox checkbox-primary h-5 w-5 align-middle',
                    'style': 'vertical-align: middle;'
                })


class BorderOfficerAssessmentForm(forms.ModelForm):
    class Meta:
        model = BorderOfficerAssessment
        fields = [
            'radical_internet',
            'radical_internet_details',
            'radical_religious_ideology',
            'radical_religious_details',
            'document_issues',
            'document_issues_details',
            'religious_deviations',
            'religious_deviations_details',
            'suspicious_mobile_content',
            'suspicious_mobile_details',
            'suspicious_behavior',
            'suspicious_behavior_details',
            'psychological_issues',
            'psychological_details',
            'relatives_mto',
            'relatives_mto_details',
            'criminal_element',
            'criminal_element_details',
            'violence_traces',
            'violence_traces_details',
            'notes',
        ]
        
        widgets = {
            'radical_internet_details': forms.Textarea(attrs={'class': 'textarea textarea-bordered w-full', 'rows': 2}),
            'radical_religious_details': forms.Textarea(attrs={'class': 'textarea textarea-bordered w-full', 'rows': 2}),
            'document_issues_details': forms.Textarea(attrs={'class': 'textarea textarea-bordered w-full', 'rows': 2}),
            'religious_deviations_details': forms.Textarea(attrs={'class': 'textarea textarea-bordered w-full', 'rows': 2}),
            'suspicious_mobile_details': forms.Textarea(attrs={'class': 'textarea textarea-bordered w-full', 'rows': 2}),
            'suspicious_behavior_details': forms.Textarea(attrs={'class': 'textarea textarea-bordered w-full', 'rows': 2}),
            'psychological_details': forms.Textarea(attrs={'class': 'textarea textarea-bordered w-full', 'rows': 2}),
            'relatives_mto_details': forms.Textarea(attrs={'class': 'textarea textarea-bordered w-full', 'rows': 2}),
            'criminal_element_details': forms.Textarea(attrs={'class': 'textarea textarea-bordered w-full', 'rows': 2}),
            'violence_traces_details': forms.Textarea(attrs={'class': 'textarea textarea-bordered w-full', 'rows': 2}),
            'notes': forms.Textarea(attrs={'class': 'textarea textarea-bordered w-full', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        bool_fields = [
            'radical_internet', 'radical_religious_ideology', 'document_issues',
            'religious_deviations', 'suspicious_mobile_content', 'suspicious_behavior',
            'psychological_issues', 'relatives_mto', 'criminal_element', 'violence_traces'
        ]
        for f in bool_fields:
            if f in self.fields:
                self.fields[f].widget = forms.CheckboxInput(attrs={
                    'class': 'checkbox checkbox-primary h-5 w-5 align-middle',
                    'style': 'vertical-align: middle;'
                })
