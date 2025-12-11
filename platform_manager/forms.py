from django import forms
from django.utils.translation import gettext_lazy as _
from .models import FormResponse, BorderOfficerAssessment
from .choices import *


class FormResponseForm(forms.ModelForm):
    class Meta:
        model = FormResponse
        # include all questionnaire fields
        fields = [
            'last_name',
            'first_name',
            'patronymic',
            'birth_date',
            'birth_place',
            'full_name_photo',
            'person_photo',
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
            'relatives_full_name',
            'relatives_when_left',
            'relatives_occupation',
            'relatives_details',
            'relatives_wanted',
            'relatives_wanted_reason',
            'religious',
            'denomination',
            'denomination_other',
            'visited_countries',
            'visited_when_purpose',
            'visited_duration',
            'visited_countries_details',
            'deported',
            'deportation_details',
            'not_allowed_reason',
            'last_time_in_homeland',
        ]

        widgets = {
            'last_name': forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
            'first_name': forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
            'patronymic': forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
            'birth_date': forms.TextInput(attrs={'class': 'input input-bordered w-full', 'placeholder': 'Например: 01.01.1990'}),
            'birth_place': forms.TextInput(attrs={'class': 'input input-bordered w-full', 'placeholder': 'Например: г. Алматы, Казахстан'}),
            'full_name_photo': forms.FileInput(attrs={'class': 'file-input file-input-bordered w-full'}),
            'person_photo': forms.FileInput(attrs={'class': 'file-input file-input-bordered w-full'}),
            'name_change_reason': forms.Textarea(attrs={'class': 'textarea textarea-bordered w-full', 'rows': 2}),
            'phones_emails': forms.Textarea(attrs={'class': 'textarea textarea-bordered w-full', 'rows': 2}),
            'military_details': forms.Textarea(attrs={'class': 'textarea textarea-bordered w-full', 'rows': 2}),
            'criminal_period_where': forms.Textarea(attrs={'class': 'textarea textarea-bordered w-full', 'rows': 2}),
            'criminal_offenses': forms.Textarea(attrs={'class': 'textarea textarea-bordered w-full', 'rows': 2}),
            'detained_when_why': forms.Textarea(attrs={'class': 'textarea textarea-bordered w-full', 'rows': 2}),
            'detained_where': forms.Textarea(attrs={'class': 'textarea textarea-bordered w-full', 'rows': 2}),
            'relatives_full_name': forms.Textarea(attrs={'class': 'textarea textarea-bordered w-full', 'rows': 2}),
            'relatives_when_left': forms.Textarea(attrs={'class': 'textarea textarea-bordered w-full', 'rows': 2}),
            'relatives_occupation': forms.Textarea(attrs={'class': 'textarea textarea-bordered w-full', 'rows': 2}),
            'relatives_details': forms.Textarea(attrs={'class': 'textarea textarea-bordered w-full', 'rows': 3}),
            'relatives_wanted_reason': forms.Textarea(attrs={'class': 'textarea textarea-bordered w-full', 'rows': 2}),
            'denomination': forms.Select(attrs={'class': 'select select-bordered w-full'}),
            'denomination_other': forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
            'visited_when_purpose': forms.Textarea(attrs={'class': 'textarea textarea-bordered w-full', 'rows': 2}),
            'visited_duration': forms.Textarea(attrs={'class': 'textarea textarea-bordered w-full', 'rows': 2}),
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
    # Дополнительные поля для множественного выбора
    radical_internet_content = forms.MultipleChoiceField(
        choices=RADICAL_CONTENT_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'checkbox checkbox-sm'}),
        required=False,
        label=_("Тип радикального контента")
    )
    radical_internet_sheikhs = forms.MultipleChoiceField(
        choices=RADICAL_SHEIKH_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'checkbox checkbox-sm'}),
        required=False,
        label=_("Какие шейхи")
    )
    
    radical_religious_signs = forms.MultipleChoiceField(
        choices=RADICAL_RELIGIOUS_SIGNS,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'checkbox checkbox-sm'}),
        required=False,
        label=_("Внешние признаки")
    )
    
    document_issues_types = forms.MultipleChoiceField(
        choices=DOCUMENT_ISSUES_TYPES,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'checkbox checkbox-sm'}),
        required=False,
        label=_("Типы проблем в документах")
    )
    
    religious_deviations_types = forms.MultipleChoiceField(
        choices=RELIGIOUS_DEVIATIONS_TYPES,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'checkbox checkbox-sm'}),
        required=False,
        label=_("Типы религиозных отклонений")
    )
    
    suspicious_mobile_types = forms.MultipleChoiceField(
        choices=SUSPICIOUS_MOBILE_TYPES,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'checkbox checkbox-sm'}),
        required=False,
        label=_("Типы сомнительного контента")
    )
    
    suspicious_behavior_types = forms.MultipleChoiceField(
        choices=SUSPICIOUS_BEHAVIOR_TYPES,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'checkbox checkbox-sm'}),
        required=False,
        label=_("Типы подозрительного поведения")
    )
    
    psychological_types = forms.MultipleChoiceField(
        choices=PSYCHOLOGICAL_TYPES,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'checkbox checkbox-sm'}),
        required=False,
        label=_("Типы психологических отклонений")
    )
    
    relatives_mto_types = forms.MultipleChoiceField(
        choices=RELATIVES_MTO_TYPES,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'checkbox checkbox-sm'}),
        required=False,
        label=_("Типы связей с МТО")
    )
    
    criminal_element_types = forms.MultipleChoiceField(
        choices=CRIMINAL_ELEMENT_TYPES,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'checkbox checkbox-sm'}),
        required=False,
        label=_("Типы криминала")
    )
    
    violence_traces_types = forms.MultipleChoiceField(
        choices=VIOLENCE_TRACES_TYPES,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'checkbox checkbox-sm'}),
        required=False,
        label=_("Типы следов насилия")
    )
    
    class Meta:
        model = BorderOfficerAssessment
        fields = [
            'radical_internet',
            'radical_internet_content',
            'radical_internet_sheikhs',
            'radical_internet_details',
            'radical_internet_photo',
            'radical_religious_ideology',
            'radical_religious_signs',
            'radical_religious_details',
            'document_issues',
            'document_issues_types',
            'document_issues_details',
            'religious_deviations',
            'religious_deviations_types',
            'religious_deviations_details',
            'suspicious_mobile_content',
            'suspicious_mobile_types',
            'suspicious_mobile_details',
            'suspicious_mobile_photo',
            'suspicious_behavior',
            'suspicious_behavior_types',
            'suspicious_behavior_details',
            'psychological_issues',
            'psychological_types',
            'psychological_details',
            'relatives_mto',
            'relatives_mto_types',
            'relatives_mto_details',
            'criminal_element',
            'criminal_element_types',
            'criminal_element_details',
            'violence_traces',
            'violence_traces_types',
            'violence_traces_details',
            'notes',
        ]
        
        widgets = {
            'radical_internet_details': forms.Textarea(attrs={'class': 'textarea textarea-bordered w-full', 'rows': 2}),
            'radical_internet_photo': forms.FileInput(attrs={'class': 'file-input file-input-bordered w-full'}),
            'radical_religious_details': forms.Textarea(attrs={'class': 'textarea textarea-bordered w-full', 'rows': 2}),
            'document_issues_details': forms.Textarea(attrs={'class': 'textarea textarea-bordered w-full', 'rows': 2}),
            'religious_deviations_details': forms.Textarea(attrs={'class': 'textarea textarea-bordered w-full', 'rows': 2}),
            'suspicious_mobile_details': forms.Textarea(attrs={'class': 'textarea textarea-bordered w-full', 'rows': 2}),
            'suspicious_mobile_photo': forms.FileInput(attrs={'class': 'file-input file-input-bordered w-full'}),
            'suspicious_behavior_details': forms.Textarea(attrs={'class': 'textarea textarea-bordered w-full', 'rows': 2}),
            'psychological_details': forms.Textarea(attrs={'class': 'textarea textarea-bordered w-full', 'rows': 2}),
            'relatives_mto_details': forms.Textarea(attrs={'class': 'textarea textarea-bordered w-full', 'rows': 2}),
            'criminal_element_details': forms.Textarea(attrs={'class': 'textarea textarea-bordered w-full', 'rows': 2}),
            'violence_traces_details': forms.Textarea(attrs={'class': 'textarea textarea-bordered w-full', 'rows': 2}),
            'notes': forms.Textarea(attrs={'class': 'textarea textarea-bordered w-full', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Инициализируем значения из JSONField
        if self.instance.pk:
            self.fields['radical_internet_content'].initial = self.instance.radical_internet_content or []
            self.fields['radical_internet_sheikhs'].initial = self.instance.radical_internet_sheikhs or []
            self.fields['radical_religious_signs'].initial = self.instance.radical_religious_signs or []
            self.fields['document_issues_types'].initial = self.instance.document_issues_types or []
            self.fields['religious_deviations_types'].initial = self.instance.religious_deviations_types or []
            self.fields['suspicious_mobile_types'].initial = self.instance.suspicious_mobile_types or []
            self.fields['suspicious_behavior_types'].initial = self.instance.suspicious_behavior_types or []
            self.fields['psychological_types'].initial = self.instance.psychological_types or []
            self.fields['relatives_mto_types'].initial = self.instance.relatives_mto_types or []
            self.fields['criminal_element_types'].initial = self.instance.criminal_element_types or []
            self.fields['violence_traces_types'].initial = self.instance.violence_traces_types or []
        
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
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Сохраняем данные множественного выбора в JSONField
        instance.radical_internet_content = self.cleaned_data.get('radical_internet_content', [])
        instance.radical_internet_sheikhs = self.cleaned_data.get('radical_internet_sheikhs', [])
        instance.radical_religious_signs = self.cleaned_data.get('radical_religious_signs', [])
        instance.document_issues_types = self.cleaned_data.get('document_issues_types', [])
        instance.religious_deviations_types = self.cleaned_data.get('religious_deviations_types', [])
        instance.suspicious_mobile_types = self.cleaned_data.get('suspicious_mobile_types', [])
        instance.suspicious_behavior_types = self.cleaned_data.get('suspicious_behavior_types', [])
        instance.psychological_types = self.cleaned_data.get('psychological_types', [])
        instance.relatives_mto_types = self.cleaned_data.get('relatives_mto_types', [])
        instance.criminal_element_types = self.cleaned_data.get('criminal_element_types', [])
        instance.violence_traces_types = self.cleaned_data.get('violence_traces_types', [])
        
        if commit:
            instance.save()
        return instance
