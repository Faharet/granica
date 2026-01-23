from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, ListView, TemplateView, DeleteView
from django.views import View
from django.utils import timezone
from datetime import timedelta

from .models import FormResponse, BorderOfficerAssessment
from .forms import FormResponseForm, BorderOfficerAssessmentForm


def is_admin(user):
	"""Return True only if user is superuser or staff.
	
	This is used for actions that require admin privileges like deleting data.
	"""
	if not user or not user.is_authenticated:
		return False
	return user.is_superuser


def is_manager(user):
	"""Return True if the user is in the 'manager' group or is a superuser.

	Only superusers and users in the 'manager' group have full access to all manager functions.
	"""
	if not user or not user.is_authenticated:
		return False
	# Only superusers have automatic manager rights
	if user.is_superuser:
		return True
	# Otherwise check for manager group membership
	return user.groups.filter(name='manager').exists()


@method_decorator(login_required, name='dispatch')
class SubmitFormView(View):
	template_name = 'platform_manager/form_submit.html'
	
	def get(self, request):
		step = int(request.GET.get('step', 1))
		form_data = request.session.get('form_data', {})
		
		form = FormResponseForm(initial=form_data)
		assessment_form = BorderOfficerAssessmentForm(initial=form_data)
		
		context = {
			'form': form,
			'assessment_form': assessment_form,
			'current_step': step,
			'total_steps': 22,
		}
		return render(request, self.template_name, context)
	
	def post(self, request):
		import os
		import base64
		from django.core.files.storage import default_storage
		from django.core.files import File
		from django.core.files.uploadedfile import SimpleUploadedFile
		
		current_step = int(request.POST.get('current_step', 1))
		action = request.POST.get('action', 'next')
		
		# Сохраняем данные текущего шага в сессию
		form_data = request.session.get('form_data', {})
		file_data = request.session.get('file_data', {})
		
		# Handle multiple choice fields (checkboxes)
		checkbox_fields = [
			'radical_internet_content', 'radical_internet_sheikhs',
			'radical_religious_signs', 'document_issues_types',
			'religious_deviations_types', 'suspicious_mobile_types',
			'suspicious_behavior_types', 'psychological_types',
			'relatives_mto_types', 'criminal_element_types',
			'violence_traces_types'
		]
		
		for key in checkbox_fields:
			values = request.POST.getlist(key)
			if values:
				form_data[key] = values
		
		# Handle boolean fields explicitly (checkboxes send 'on' when checked)
		# Map steps to their boolean fields to avoid overwriting values from other steps
		step_bool_fields = {
			2: ['name_changed'],
			4: ['military_service'],
			5: ['criminal_record'],
			6: ['detained_abroad'],
			7: ['relatives_in_countries'],
			8: ['religious'],
			9: ['relatives_wanted'],
			10: ['visited_countries'],
			11: ['deported']
		}
		
		# Only update boolean fields that belong to the current step
		if current_step in step_bool_fields:
			for field in step_bool_fields[current_step]:
				form_data[field] = request.POST.get(field) == 'on'
		
		# Handle other fields
		for key, value in request.POST.items():
			if key not in ['csrfmiddlewaretoken', 'current_step', 'action'] and key not in checkbox_fields:
				# Skip boolean fields - they're handled above
				if key not in ['name_changed', 'military_service', 'criminal_record', 'detained_abroad',
					'relatives_in_countries', 'relatives_wanted', 'religious', 'visited_countries', 'deported']:
					form_data[key] = value
		
		# Handle uploaded files - encode as base64 for session storage
		for key, file in request.FILES.items():
			file_content = file.read()
			file_data[key] = {
				'content': base64.b64encode(file_content).decode('utf-8'),
				'name': file.name,
				'content_type': file.content_type
			}
		
		request.session['form_data'] = form_data
		request.session['file_data'] = file_data
		
		if action == 'previous':
			next_step = max(1, current_step - 1)
			return redirect(f"{request.path}?step={next_step}")
		elif action == 'next':
			next_step = min(22, current_step + 1)
			return redirect(f"{request.path}?step={next_step}")
		elif action == 'submit':
			# Финальная отправка
			# Decode files from base64
			saved_file_data = request.session.get('file_data', {})
			files_dict = {}
			
			for key, file_info in saved_file_data.items():
				if isinstance(file_info, dict) and 'content' in file_info:
					file_content = base64.b64decode(file_info['content'])
					files_dict[key] = SimpleUploadedFile(
						name=file_info['name'],
						content=file_content,
						content_type=file_info['content_type']
					)
			
			# Convert boolean values to 'on' for Django form processing
			form_data_for_submit = form_data.copy()
			bool_fields = [
				'name_changed', 'military_service', 'criminal_record', 'detained_abroad',
				'relatives_in_countries', 'relatives_wanted', 'religious', 'visited_countries', 'deported'
			]
			
			# Clear dependent fields when checkbox is unchecked
			dependent_fields = {
				'name_changed': ['name_change_reason'],
				'military_service': ['military_details'],
				'criminal_record': ['criminal_period_where', 'criminal_offenses'],
				'detained_abroad': ['detained_when_why', 'detained_where'],
				'relatives_in_countries': ['relatives_full_name', 'relatives_when_left', 'relatives_occupation', 'relatives_details'],
				'relatives_wanted': ['relatives_wanted_reason'],
				'religious': ['denomination', 'denomination_other'],
				'visited_countries': ['visited_when_purpose', 'visited_duration', 'visited_countries_details'],
				'deported': ['deportation_details']
			}
			
			for field in bool_fields:
				if form_data_for_submit.get(field) is True:
					form_data_for_submit[field] = 'on'
				elif field in form_data_for_submit:
					# If checkbox is False, clear dependent fields
					if form_data_for_submit.get(field) is False and field in dependent_fields:
						for dep_field in dependent_fields[field]:
							form_data_for_submit[dep_field] = ''
					del form_data_for_submit[field]
			
			form = FormResponseForm(form_data_for_submit, files_dict)
			assessment_form = BorderOfficerAssessmentForm(form_data_for_submit, files_dict)
			
			if form.is_valid():
				instance = form.save(commit=False)
				if request.user.is_authenticated:
					instance.created_by = request.user
				instance.save()
				
				# Always create officer assessment
				if assessment_form.is_valid():
					assessment = assessment_form.save(commit=False)
					assessment.form_response = instance
					assessment.assessed_by = request.user
					assessment.calculate_score()
					assessment.save()
				else:
					# Create empty assessment if form is invalid (no data filled)
					assessment = BorderOfficerAssessment.objects.create(
						form_response=instance,
						assessed_by=request.user
					)
					assessment.calculate_score()
					assessment.save()
				
				# Update response with assessment score
				instance.total_score = assessment.total_score
				instance.threat_level = assessment.threat_level
				instance.save()
				
				request.session.pop('form_data', None)
				request.session.pop('file_data', None)
				return redirect('platform_manager:form_submitted')
			else:
				# Если форма невалидна, вернуться на первый шаг с ошибками
				return redirect(f"{request.path}?step=1")
		
		return redirect(f"{request.path}?step={current_step}")


@method_decorator(login_required, name='dispatch')
class ResponsesListView(ListView):
	model = FormResponse
	template_name = 'platform_manager/form_responses_list.html'
	context_object_name = 'responses'
	paginate_by = 50
	
	def get_queryset(self):
		# Managers see all responses, submitters see only their own
		if is_manager(self.request.user):
			queryset = FormResponse.objects.all()
		else:
			# Submitters and other authenticated users see only their own
			queryset = FormResponse.objects.filter(created_by=self.request.user)
		
		# Apply filters
		# Filter by search (full name) - case-insensitive search
		from django.db.models import Q
		search = self.request.GET.get('search')
		if search:
			search_term = search.strip()
			# For Cyrillic, icontains in SQLite is case-sensitive, so we search for multiple variants
			search_variants = [
				search_term,
				search_term.lower(),
				search_term.upper(),
				search_term.capitalize(),
				search_term.title()
			]
			
			q_objects = Q()
			for variant in search_variants:
				q_objects |= (
					Q(last_name__contains=variant) |
					Q(first_name__contains=variant) |
					Q(patronymic__contains=variant) |
					Q(full_name_and_birth__contains=variant)
				)
			
			queryset = queryset.filter(q_objects)
		
		# Filter by date range
		date_from = self.request.GET.get('date_from')
		date_to = self.request.GET.get('date_to')
		if date_from:
			queryset = queryset.filter(created_at__date__gte=date_from)
		if date_to:
			queryset = queryset.filter(created_at__date__lte=date_to)
		
		# Filter by creator (only for managers)
		if is_manager(self.request.user):
			created_by_id = self.request.GET.get('created_by')
			if created_by_id:
				queryset = queryset.filter(created_by_id=created_by_id)
		
		# Filter by threat level
		threat_level = self.request.GET.get('threat_level')
		if threat_level:
			queryset = queryset.filter(threat_level=threat_level)
		
		# Filter by country
		country = self.request.GET.get('country')
		if country:
			queryset = queryset.filter(birth_place=country)
		
		return queryset.order_by('-created_at')
	
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['is_manager'] = is_manager(self.request.user)
		
		# Add filter values to context for form persistence
		context['search'] = self.request.GET.get('search', '')
		context['date_from'] = self.request.GET.get('date_from', '')
		context['date_to'] = self.request.GET.get('date_to', '')
		context['created_by'] = self.request.GET.get('created_by', '')
		context['threat_level'] = self.request.GET.get('threat_level', '')
		context['country'] = self.request.GET.get('country', '')
		
		# Add country choices for filter dropdown
		from .forms import COUNTRY_CHOICES
		context['country_choices'] = COUNTRY_CHOICES
		
		# Get list of users for creator filter (only for managers)
		if is_manager(self.request.user):
			from django.contrib.auth import get_user_model
			from django.db.models import Count
			User = get_user_model()
			context['users'] = User.objects.filter(
				form_responses__isnull=False
			).distinct().order_by('first_name', 'last_name')
			
			# Get statistics for dashboard (same filters applied)
			queryset = self.get_queryset()
			
			# Threat level distribution
			threat_stats = {
				'low': queryset.filter(threat_level='Низкий').count(),
				'medium': queryset.filter(threat_level='Средний').count(),
				'high': queryset.filter(threat_level='Высокий').count(),
			}
			context['threat_stats'] = threat_stats
			
			# Total count
			context['total_responses'] = queryset.count()
			
			# Top submitters
			top_submitters = queryset.values(
				'created_by__first_name', 
				'created_by__last_name',
				'created_by__username'
			).annotate(count=Count('id')).order_by('-count')[:5]
			context['top_submitters'] = top_submitters
		
		return context


@method_decorator(login_required, name='dispatch')
class FormResponseDetailView(TemplateView):
	template_name = 'platform_manager/form_response_detail.html'

	def get(self, request, *args, **kwargs):
		pk = kwargs.get('pk')
		response = FormResponse.objects.select_related('officer_assessment').filter(pk=pk).first()
		
		# Check access: managers can see all, others can only see their own
		if response:
			if not is_manager(request.user) and response.created_by != request.user:
				# Redirect to responses list if trying to access someone else's form
				return redirect('platform_manager:form_responses')
		
		return super().get(request, *args, **kwargs)

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		pk = kwargs.get('pk')
		response = FormResponse.objects.select_related('officer_assessment').filter(pk=pk).first()
		
		context['response'] = response
		context['is_manager'] = is_manager(self.request.user)
		
		# Check if officer assessment exists
		if response:
			try:
				_ = response.officer_assessment
			except BorderOfficerAssessment.DoesNotExist:
				# Assessment doesn't exist, it's ok
				pass
		
		# Check if delete button should be shown (only admins can delete)
		if response:
			if is_admin(self.request.user):
				context['can_delete'] = True
			else:
				context['can_delete'] = False
		else:
			context['can_delete'] = False
		
		# Check if edit button should be shown
		# Managers can always edit, submitters only within 30 minutes
		if response:
			if is_manager(self.request.user):
				context['can_edit'] = True
			else:
				# Submitters can edit only within 30 minutes
				time_since_creation = timezone.now() - response.created_at
				context['can_edit'] = time_since_creation < timedelta(minutes=30)
		else:
			context['can_edit'] = False
		
		return context


@method_decorator(login_required, name='dispatch')
class EditFormResponseView(View):
	"""
	View for editing form responses.
	Managers can always edit, submitters only within 30 minutes.
	"""
	template_name = 'platform_manager/form_submit.html'
	
	def dispatch(self, request, *args, **kwargs):
		# Get the response object
		self.response = get_object_or_404(FormResponse, pk=kwargs['pk'])
		
		# Check permissions
		if is_manager(request.user):
			# Managers can always edit
			pass
		elif self.response.created_by == request.user:
			# Submitters can edit only within 30 minutes
			time_since_creation = timezone.now() - self.response.created_at
			if time_since_creation >= timedelta(minutes=30):
				# Redirect to detail view if time expired
				return redirect('platform_manager:form_response_detail', pk=self.response.pk)
		else:
			# Not authorized to edit this response
			return redirect('platform_manager:form_responses')
		
		return super().dispatch(request, *args, **kwargs)
	
	def get(self, request, pk):
		step = int(request.GET.get('step', 1))
		
		# Initialize form data from existing response
		if 'form_data' not in request.session:
			form_data = {}
			# Get all field names from the model (not form meta)
			for field in self.response._meta.fields:
				field_name = field.name
				# Skip file fields, primary keys, and foreign keys
				if field_name in ['id', 'created_at', 'updated_at', 'created_by', 'full_name_photo', 'person_photo']:
					continue
				value = getattr(self.response, field_name, None)
				if value is not None:
					# Convert to string for JSON serialization
					if hasattr(value, '__str__'):
						form_data[field_name] = str(value) if not isinstance(value, (bool, int, float)) else value
			request.session['form_data'] = form_data
		else:
			form_data = request.session.get('form_data', {})
		
		form = FormResponseForm(instance=self.response)
		
		# Get or create assessment
		try:
			assessment = self.response.officer_assessment
			assessment_form = BorderOfficerAssessmentForm(instance=assessment)
		except BorderOfficerAssessment.DoesNotExist:
			assessment_form = BorderOfficerAssessmentForm()
		
		context = {
			'form': form,
			'assessment_form': assessment_form,
			'current_step': step,
			'total_steps': 22,
			'is_edit': True,
			'response_id': self.response.pk,
		}
		return render(request, self.template_name, context)
	
	def post(self, request, pk):
		import os
		import base64
		from django.core.files.uploadedfile import SimpleUploadedFile
		
		current_step = int(request.POST.get('current_step', 1))
		action = request.POST.get('action', 'next')
		
		# Save current step data to session
		form_data = request.session.get('form_data', {})
		file_data = request.session.get('file_data', {})
		
		# Handle checkbox fields
		checkbox_fields = [
			'radical_internet_content', 'radical_internet_sheikhs',
			'radical_religious_signs', 'document_issues_types',
			'religious_deviations_types', 'suspicious_mobile_types',
			'suspicious_behavior_types', 'psychological_types',
			'relatives_mto_types', 'criminal_element_types', 'violence_traces_types'
		]
		
		for field_name in checkbox_fields:
			if field_name in request.POST:
				form_data[field_name] = request.POST.getlist(field_name)
		
		# Handle boolean fields explicitly (checkboxes send 'on' when checked)
		# Map steps to their boolean fields to avoid overwriting values from other steps
		step_bool_fields = {
			2: ['name_changed'],
			4: ['military_service'],
			5: ['criminal_record'],
			6: ['detained_abroad'],
			7: ['relatives_in_countries'],
			8: ['religious'],
			9: ['relatives_wanted'],
			10: ['visited_countries'],
			11: ['deported']
		}
		
		# Only update boolean fields that belong to the current step
		if current_step in step_bool_fields:
			for field in step_bool_fields[current_step]:
				form_data[field] = request.POST.get(field) == 'on'
		
		# Save regular fields
		for key, value in request.POST.items():
			if key not in ['csrfmiddlewaretoken', 'current_step', 'action'] and key not in checkbox_fields:
				# Skip boolean fields and photo fields - they're handled separately
				if key not in ['name_changed', 'military_service', 'criminal_record', 'detained_abroad',
					'relatives_in_countries', 'relatives_wanted', 'religious', 'visited_countries', 'deported'] and not key.endswith('_photo'):
					form_data[key] = value
		
		# Handle file uploads
		for field_name in ['full_name_photo', 'person_photo', 'radical_internet_photo', 'suspicious_mobile_photo']:
			if field_name in request.FILES:
				uploaded_file = request.FILES[field_name]
				file_content = uploaded_file.read()
				file_base64 = base64.b64encode(file_content).decode('utf-8')
				file_data[field_name] = {
					'name': uploaded_file.name,
					'content': file_base64,
					'content_type': uploaded_file.content_type,
				}
		
		request.session['form_data'] = form_data
		request.session['file_data'] = file_data
		
		# Handle navigation
		if action == 'previous' and current_step > 1:
			return redirect(f"{request.path}?step={current_step - 1}")
		elif action == 'next' and current_step < 22:
			return redirect(f"{request.path}?step={current_step + 1}")
		elif action == 'submit':
			# Update the response using session data
			# Decode files from base64
			files_dict = {}
			for key, file_info in file_data.items():
				if isinstance(file_info, dict) and 'content' in file_info:
					file_content = base64.b64decode(file_info['content'])
					files_dict[key] = SimpleUploadedFile(
						name=file_info['name'],
						content=file_content,
						content_type=file_info['content_type']
					)
			
			# Convert boolean values to 'on' for Django form processing
			form_data_for_submit = form_data.copy()
			bool_fields = [
				'name_changed', 'military_service', 'criminal_record', 'detained_abroad',
				'relatives_in_countries', 'relatives_wanted', 'religious', 'visited_countries', 'deported'
			]
			
			# Clear dependent fields when checkbox is unchecked
			dependent_fields = {
				'name_changed': ['name_change_reason'],
				'military_service': ['military_details'],
				'criminal_record': ['criminal_period_where', 'criminal_offenses'],
				'detained_abroad': ['detained_when_why', 'detained_where'],
				'relatives_in_countries': ['relatives_full_name', 'relatives_when_left', 'relatives_occupation', 'relatives_details'],
				'relatives_wanted': ['relatives_wanted_reason'],
				'religious': ['denomination', 'denomination_other'],
				'visited_countries': ['visited_when_purpose', 'visited_duration', 'visited_countries_details'],
				'deported': ['deportation_details']
			}
			
			for field in bool_fields:
				if form_data_for_submit.get(field) is True:
					form_data_for_submit[field] = 'on'
				elif field in form_data_for_submit:
					# If checkbox is False, clear dependent fields
					if form_data_for_submit.get(field) is False and field in dependent_fields:
						for dep_field in dependent_fields[field]:
							form_data_for_submit[dep_field] = ''
					del form_data_for_submit[field]
			
			form = FormResponseForm(form_data_for_submit, files_dict, instance=self.response)
			assessment_form = BorderOfficerAssessmentForm(form_data_for_submit, files_dict)
			
			if form.is_valid():
				instance = form.save(commit=False)
				
				instance.calculate_score()
				instance.save()
				
				# Update or create assessment
				try:
					assessment = self.response.officer_assessment
					assessment_form = BorderOfficerAssessmentForm(request.POST, request.FILES, instance=assessment)
				except BorderOfficerAssessment.DoesNotExist:
					assessment_form = BorderOfficerAssessmentForm(request.POST, request.FILES)
				
				if assessment_form.is_valid():
					assessment = assessment_form.save(commit=False)
					assessment.form_response = instance
					if not assessment.assessed_by:
						assessment.assessed_by = request.user
					assessment.calculate_score()
					assessment.save()
				else:
					# Create or update empty assessment
					try:
						assessment = self.response.officer_assessment
						assessment.calculate_score()
						assessment.save()
					except BorderOfficerAssessment.DoesNotExist:
						assessment = BorderOfficerAssessment.objects.create(
							form_response=instance,
							assessed_by=request.user
						)
						assessment.calculate_score()
						assessment.save()
				
				# Update response with assessment score
				instance.total_score = assessment.total_score
				instance.threat_level = assessment.threat_level
				instance.save()
				
				request.session.pop('form_data', None)
				request.session.pop('file_data', None)
				return redirect('platform_manager:form_response_detail', pk=instance.pk)
			else:
				return redirect(f"{request.path}?step=1")
		
		return redirect(f"{request.path}?step={current_step}")


@method_decorator(user_passes_test(is_admin), name='dispatch')
class FormResponseDeleteView(DeleteView):
	model = FormResponse
	template_name = 'platform_manager/form_response_confirm_delete.html'
	success_url = reverse_lazy('platform_manager:form_responses')


class FormSubmittedView(TemplateView):
	template_name = 'platform_manager/form_submitted.html'


# A simple dashboard view for managers/submitters who are not staff.
# This view is intended to be used outside of the Django admin interface
# so users who are authenticated but not `is_staff` can still access
# the forms and menu.
@method_decorator(login_required, name='dispatch')
class DashboardView(TemplateView):
	template_name = 'platform_manager/manager_panel.html'


@method_decorator(user_passes_test(is_manager), name='dispatch')
class OfficerAssessmentView(View):
	template_name = 'platform_manager/officer_assessment.html'
	
	def get(self, request, pk):
		response = get_object_or_404(FormResponse, pk=pk)
		
		# Try to get existing assessment or create new
		try:
			assessment = response.officer_assessment
			form = BorderOfficerAssessmentForm(instance=assessment)
		except BorderOfficerAssessment.DoesNotExist:
			form = BorderOfficerAssessmentForm()
		
		context = {
			'form': form,
			'response': response,
		}
		return render(request, self.template_name, context)
	
	def post(self, request, pk):
		response = get_object_or_404(FormResponse, pk=pk)
		
		# Try to get existing assessment or create new
		try:
			assessment = response.officer_assessment
			form = BorderOfficerAssessmentForm(request.POST, instance=assessment)
		except BorderOfficerAssessment.DoesNotExist:
			form = BorderOfficerAssessmentForm(request.POST)
		
		if form.is_valid():
			assessment = form.save(commit=False)
			assessment.form_response = response
			assessment.assessed_by = request.user
			assessment.calculate_score()
			assessment.save()
			
			# Update the form response with officer's score
			response.total_score = assessment.total_score
			response.threat_level = assessment.threat_level
			response.save()
			
			return redirect('platform_manager:form_response_detail', pk=pk)
		
		context = {
			'form': form,
			'response': response,
		}
		return render(request, self.template_name, context)


@login_required
def export_response_pdf(request, pk):
	"""Export form response to PDF. Managers can export any, others only their own."""
	from django.http import HttpResponse
	from reportlab.lib.pagesizes import A4
	from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
	from reportlab.lib.units import cm
	from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageTemplate, BaseDocTemplate, Frame
	from reportlab.lib import colors
	from reportlab.lib.enums import TA_LEFT, TA_CENTER
	from reportlab.pdfbase import pdfmetrics
	from reportlab.pdfbase.ttfonts import TTFont
	import os
	from django.conf import settings
	from django.utils.translation import gettext as _
	from django.utils import translation
	
	# Get current language from request
	current_language = translation.get_language()
	
	# Watermark text
	watermark_text = 'АБАЙ'
	
	# Register fonts for Cyrillic support
	fonts_dir = os.path.join(settings.BASE_DIR, 'fonts')
	try:
		pdfmetrics.registerFont(TTFont('DejaVuSans', os.path.join(fonts_dir, 'DejaVuSans.ttf')))
		pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', os.path.join(fonts_dir, 'DejaVuSans-Bold.ttf')))
		normal_font = 'DejaVuSans'
		bold_font = 'DejaVuSans-Bold'
	except:
		# Fallback to Helvetica if DejaVu fonts not available
		normal_font = 'Helvetica'
		bold_font = 'Helvetica-Bold'
	
	response_obj = get_object_or_404(FormResponse, pk=pk)
	
	# Check access: managers can export any, others can only export their own
	if not is_manager(request.user) and response_obj.created_by != request.user:
		from django.http import HttpResponseForbidden
		return HttpResponseForbidden("You don't have permission to export this response.")
	
	# Create HTTP response with PDF headers
	response = HttpResponse(content_type='application/pdf')
	response['Content-Disposition'] = f'attachment; filename="response_{pk}.pdf"'
	
	# Custom page template with watermark
	def add_watermark(canvas, doc):
		canvas.saveState()
		# Draw watermark text in center
		canvas.setFont(bold_font, 180)
		canvas.setFillColor(colors.HexColor('#1e40af'))
		canvas.setFillAlpha(0.08)
		# Rotate and position watermark
		canvas.translate(A4[0]/2, A4[1]/2)
		canvas.rotate(-12)
		# Draw text centered
		text_width = canvas.stringWidth(watermark_text, bold_font, 180)
		canvas.drawString(-text_width/2, -90, watermark_text)
		canvas.restoreState()
	
	# Create PDF document with custom page template
	doc = BaseDocTemplate(response, pagesize=A4, topMargin=1.5*cm, bottomMargin=1.5*cm, leftMargin=2*cm, rightMargin=2*cm)
	frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id='normal')
	template = PageTemplate(id='watermark', frames=frame, onPage=add_watermark)
	doc.addPageTemplates([template])
	
	story = []
	
	# Styles
	styles = getSampleStyleSheet()
	title_style = ParagraphStyle(
		'CustomTitle',
		parent=styles['Heading1'],
		fontSize=18,
		textColor=colors.HexColor('#1f2937'),
		spaceAfter=20,
		alignment=TA_CENTER,
		fontName=bold_font
	)
	
	heading_style = ParagraphStyle(
		'CustomHeading',
		parent=styles['Heading2'],
		fontSize=12,
		textColor=colors.HexColor('#1f2937'),
		spaceAfter=10,
		spaceBefore=15,
		fontName=bold_font
	)
	
	normal_style = ParagraphStyle(
		'CustomNormal',
		parent=styles['Normal'],
		fontSize=9,
		textColor=colors.HexColor('#1f2937'),
		fontName=normal_font
	)
	
	# Title
	story.append(Paragraph(_("Form Response"), title_style))
	story.append(Spacer(1, 0.5*cm))
	
	# Helper function for yes/no with details
	def add_field(data, question, yes_no_field, details_field=None, details_label=None):
		yes_no = _('Yes') if yes_no_field else _('No')
		data.append([Paragraph(question, normal_style), Paragraph(yes_no, normal_style)])
		if details_field and details_field.strip():
			if details_label:
				data.append([Paragraph(details_label, normal_style), Paragraph(details_field.replace('\n', '<br/>'), normal_style)])
	
	# Section 1: Biographical Data
	story.append(Paragraph(_("Biographical Data"), heading_style))
	bio_data = []
	
	# Question 1
	full_name_parts = []
	if response_obj.last_name:
		full_name_parts.append(response_obj.last_name)
	if response_obj.first_name:
		full_name_parts.append(response_obj.first_name)
	if response_obj.patronymic:
		full_name_parts.append(response_obj.patronymic)
	full_name = ' '.join(full_name_parts) if full_name_parts else ''
	
	birth_info_parts = []
	if response_obj.birth_date:
		# Handle both date objects and string representations
		if isinstance(response_obj.birth_date, str):
			birth_info_parts.append(f'{_("Birth date")}: {response_obj.birth_date}')
		else:
			birth_info_parts.append(f'{_("Birth date")}: {response_obj.birth_date.strftime("%d.%m.%Y")}')
	if response_obj.birth_place:
		birth_info_parts.append(f'{_("Birth place")}: {response_obj.birth_place}')
	birth_info = '<br/>'.join(birth_info_parts) if birth_info_parts else ''
	
	q1_answer = '<br/>'.join(filter(None, [full_name, birth_info])) if full_name or birth_info else '—'
	
	bio_data.append([
		Paragraph(_('1. Full name, date and place of birth'), normal_style),
		Paragraph(q1_answer, normal_style)
	])
	
	# Question 2
	add_field(bio_data, _('2. Changed surname/name/patronymic'), response_obj.name_changed, 
		response_obj.name_change_reason, _('Reason for change'))
	
	# Question 3
	bio_data.append([
		Paragraph(_('3. Phones and email'), normal_style),
		Paragraph(response_obj.phones_emails.replace('\n', '<br/>') if response_obj.phones_emails else '—', normal_style)
	])
	
	# Question 4
	add_field(bio_data, _('4. Military service'), response_obj.military_service,
		response_obj.military_details, _('Service details'))
	
	bio_table = Table(bio_data, colWidths=[7*cm, 10*cm])
	bio_table.setStyle(TableStyle([
		('BACKGROUND', (0, 0), (-1, -1), colors.white),
		('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#4b5563')),
		('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#1f2937')),
		('ALIGN', (0, 0), (-1, -1), 'LEFT'),
		('VALIGN', (0, 0), (-1, -1), 'TOP'),
		('FONTSIZE', (0, 0), (-1, -1), 9),
		('BOTTOMPADDING', (0, 0), (-1, -1), 8),
		('TOPPADDING', (0, 0), (-1, -1), 8),
		('LEFTPADDING', (0, 0), (-1, -1), 10),
		('RIGHTPADDING', (0, 0), (-1, -1), 10),
		('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb'))
	]))
	story.append(bio_table)
	story.append(Spacer(1, 0.5*cm))
	
	# Section 2: Criminal and Legal Information
	story.append(Paragraph(_("Сriminal and Legal Information"), heading_style))
	criminal_data = []
	
	# Question 5
	add_field(criminal_data, _('5. Criminal record'), response_obj.criminal_record,
		(response_obj.criminal_period_where or '') + '\n' + (response_obj.criminal_offenses or '') if response_obj.criminal_period_where or response_obj.criminal_offenses else None,
		_('Period and place of imprisonment / For which crimes'))
	
	# Question 6
	add_field(criminal_data, _('6. Detentions abroad'), response_obj.detained_abroad,
		(response_obj.detained_when_why or '') + ('\n' + response_obj.detained_where if response_obj.detained_where else ''),
		_('When and why / Where detained'))
	
	criminal_table = Table(criminal_data, colWidths=[7*cm, 10*cm])
	criminal_table.setStyle(TableStyle([
		('BACKGROUND', (0, 0), (-1, -1), colors.white),
		('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#4b5563')),
		('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#1f2937')),
		('ALIGN', (0, 0), (-1, -1), 'LEFT'),
		('VALIGN', (0, 0), (-1, -1), 'TOP'),
		('FONTSIZE', (0, 0), (-1, -1), 9),
		('BOTTOMPADDING', (0, 0), (-1, -1), 8),
		('TOPPADDING', (0, 0), (-1, -1), 8),
		('LEFTPADDING', (0, 0), (-1, -1), 10),
		('RIGHTPADDING', (0, 0), (-1, -1), 10),
		('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb'))
	]))
	story.append(criminal_table)
	story.append(Spacer(1, 0.5*cm))
	
	# Section 3: Relatives and Religion
	story.append(Paragraph(_("Relatives and Religion"), heading_style))
	relatives_data = []
	
	# Question 7
	add_field(relatives_data, _('7. Relatives in specified countries'), response_obj.relatives_in_countries,
		response_obj.relatives_details, _('Relatives details'))
	
	# Question 8
	add_field(relatives_data, _('8. Religious'), response_obj.religious,
		response_obj.denomination, _('Denomination/views'))
	
	# Question 9 (previously was question 8 about relatives_wanted)
	if response_obj.relatives_wanted:
		relatives_data.append([
			Paragraph(_('9. Are relatives wanted'), normal_style),
			Paragraph(_('Yes'), normal_style)
		])
		if response_obj.relatives_wanted_reason and response_obj.relatives_wanted_reason.strip():
			relatives_data.append([
				Paragraph(_('Reason for search'), normal_style),
				Paragraph(response_obj.relatives_wanted_reason.replace('\n', '<br/>'), normal_style)
			])
	
	relatives_table = Table(relatives_data, colWidths=[7*cm, 10*cm])
	relatives_table.setStyle(TableStyle([
		('BACKGROUND', (0, 0), (-1, -1), colors.white),
		('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#4b5563')),
		('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#1f2937')),
		('ALIGN', (0, 0), (-1, -1), 'LEFT'),
		('VALIGN', (0, 0), (-1, -1), 'TOP'),
		('FONTSIZE', (0, 0), (-1, -1), 9),
		('BOTTOMPADDING', (0, 0), (-1, -1), 8),
		('TOPPADDING', (0, 0), (-1, -1), 8),
		('LEFTPADDING', (0, 0), (-1, -1), 10),
		('RIGHTPADDING', (0, 0), (-1, -1), 10),
		('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb'))
	]))
	story.append(relatives_table)
	story.append(Spacer(1, 0.5*cm))
	
	# Section 4: Travel and Deportations
	story.append(Paragraph(_("Travel and Deportations"), heading_style))
	travel_data = []
	
	# Question 10
	add_field(travel_data, _('10. Visited specified countries'), response_obj.visited_countries,
		response_obj.visited_countries_details, _('Visit details'))
	
	# Question 11
	add_field(travel_data, _('11. Deportation/expulsion'), response_obj.deported,
		response_obj.deportation_details, _('Deportation details'))
	
	# Question 12
	if response_obj.not_allowed_reason:
		travel_data.append([
			Paragraph(_('12. Reason for not allowing entry'), normal_style),
			Paragraph(response_obj.not_allowed_reason.replace('\n', '<br/>'), normal_style)
		])
	
	# Question 13
	if response_obj.last_time_in_homeland:
		travel_data.append([
			Paragraph(_('13. Last time in homeland'), normal_style),
			Paragraph(str(response_obj.last_time_in_homeland), normal_style)
		])
	
	travel_table = Table(travel_data, colWidths=[7*cm, 10*cm])
	travel_table.setStyle(TableStyle([
		('BACKGROUND', (0, 0), (-1, -1), colors.white),
		('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#4b5563')),
		('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#1f2937')),
		('ALIGN', (0, 0), (-1, -1), 'LEFT'),
		('VALIGN', (0, 0), (-1, -1), 'TOP'),
		('FONTSIZE', (0, 0), (-1, -1), 9),
		('BOTTOMPADDING', (0, 0), (-1, -1), 8),
		('TOPPADDING', (0, 0), (-1, -1), 8),
		('LEFTPADDING', (0, 0), (-1, -1), 10),
		('RIGHTPADDING', (0, 0), (-1, -1), 10),
		('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb'))
	]))
	story.append(travel_table)
	story.append(Spacer(1, 0.8*cm))
	
	# Section 5: Officer Assessment (Questions 14-23)
	if hasattr(response_obj, 'officer_assessment') and response_obj.officer_assessment:
		story.append(Paragraph(_("Border Officer Assessment"), heading_style))
		assessment = response_obj.officer_assessment
		assessment_data = []
		
		# Helper function to add checkbox selections
		def add_checkbox_field(data, question, yes_no_field, labels_method, details_field=None):
			yes_no = _('Yes') if yes_no_field else _('No')
			data.append([Paragraph(question, normal_style), Paragraph(yes_no, normal_style)])
			if yes_no_field and labels_method:
				labels = labels_method()
				if labels:
					items_html = '<br/>'.join([f'• {label}' for label in labels])
					data.append([Paragraph(_('Identified issues:'), normal_style), Paragraph(items_html, normal_style)])
			if details_field and details_field.strip():
				data.append([Paragraph(_('Additional details:'), normal_style), Paragraph(details_field.replace('\n', '<br/>'), normal_style)])
		
		# Question 14 & 15 - Radical Internet
		add_checkbox_field(assessment_data, _('14. Radical content on internet'), 
			assessment.radical_internet, assessment.get_radical_internet_content_labels,
			assessment.radical_internet_details)
		
		if assessment.radical_internet_sheikhs:
			labels = assessment.get_radical_internet_sheikhs_labels()
			if labels:
				items_html = '<br/>'.join([f'• {label}' for label in labels])
				assessment_data.append([Paragraph(_('15. Radical sheikhs:'), normal_style), Paragraph(items_html, normal_style)])
		
		# Question 16 - Radical Religious Ideology
		add_checkbox_field(assessment_data, _('16. Radical religious ideology'),
			assessment.radical_religious_ideology, assessment.get_radical_religious_signs_labels,
			assessment.radical_religious_details)
		
		# Question 17 - Document Issues
		add_checkbox_field(assessment_data, _('17. Document issues'),
			assessment.document_issues, assessment.get_document_issues_types_labels,
			assessment.document_issues_details)
		
		# Question 18 - Religious Deviations
		add_checkbox_field(assessment_data, _('18. Deviation from religious norms'),
			assessment.religious_deviations, assessment.get_religious_deviations_types_labels,
			assessment.religious_deviations_details)
		
		# Question 19 - Suspicious Mobile Content
		add_checkbox_field(assessment_data, _('19. Suspicious mobile content'),
			assessment.suspicious_mobile_content, assessment.get_suspicious_mobile_types_labels,
			assessment.suspicious_mobile_details)
		
		# Question 20 - Suspicious Behavior
		add_checkbox_field(assessment_data, _('20. Suspicious behavior'),
			assessment.suspicious_behavior, assessment.get_suspicious_behavior_types_labels,
			assessment.suspicious_behavior_details)
		
		# Question 21 - Psychological Issues
		add_checkbox_field(assessment_data, _('21. Psychological deviations'),
			assessment.psychological_issues, assessment.get_psychological_types_labels,
			assessment.psychological_details)
		
		# Question 22 - Relatives MTO
		add_checkbox_field(assessment_data, _('22. Relatives in MTO'),
			assessment.relatives_mto, assessment.get_relatives_mto_types_labels,
			assessment.relatives_mto_details)
		
		# Question 23 - Criminal Element
		add_checkbox_field(assessment_data, _('23. Criminal element'),
			assessment.criminal_element, assessment.get_criminal_element_types_labels,
			assessment.criminal_element_details)
		
		# Question 23b - Violence Traces
		if assessment.violence_traces:
			add_checkbox_field(assessment_data, _('23. Traces of violence'),
				assessment.violence_traces, assessment.get_violence_traces_types_labels,
				assessment.violence_traces_details)
		
		assessment_table = Table(assessment_data, colWidths=[7*cm, 10*cm])
		assessment_table.setStyle(TableStyle([
			('BACKGROUND', (0, 0), (-1, -1), colors.white),
			('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#4b5563')),
			('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#1f2937')),
			('ALIGN', (0, 0), (-1, -1), 'LEFT'),
			('VALIGN', (0, 0), (-1, -1), 'TOP'),
			('FONTSIZE', (0, 0), (-1, -1), 9),
			('BOTTOMPADDING', (0, 0), (-1, -1), 8),
			('TOPPADDING', (0, 0), (-1, -1), 8),
			('LEFTPADDING', (0, 0), (-1, -1), 10),
			('RIGHTPADDING', (0, 0), (-1, -1), 10),
			('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb'))
		]))
		story.append(assessment_table)
		story.append(Spacer(1, 0.5*cm))
	
	# Section 6: Attached Photos (at the end)
	from reportlab.platypus import Image as RLImage
	photos = []
	
	# Check for full_name_photo (Question 1)
	if response_obj.full_name_photo:
		photos.append((_('Document photo (Question 1)'), response_obj.full_name_photo))
	
	# Check for person_photo (Question 1)
	if response_obj.person_photo:
		photos.append((_('Person photo (Question 1)'), response_obj.person_photo))
	
	# Check for radical_internet_photo (Question 14-15)
	if hasattr(response_obj, 'officer_assessment') and response_obj.officer_assessment.radical_internet_photo:
		photos.append((_('Radical internet content photo (Question 14-15)'), response_obj.officer_assessment.radical_internet_photo))
	
	# Check for suspicious_mobile_photo (Question 19)
	if hasattr(response_obj, 'officer_assessment') and response_obj.officer_assessment.suspicious_mobile_photo:
		photos.append((_('Suspicious mobile content photo (Question 19)'), response_obj.officer_assessment.suspicious_mobile_photo))
	
	if photos:
		story.append(Paragraph(_("Attached Photos"), heading_style))
		
		for photo_title, photo_field in photos:
			story.append(Paragraph(photo_title, normal_style))
			story.append(Spacer(1, 0.2*cm))
			
			try:
				# Get absolute path to the image
				photo_path = photo_field.path
				
				# Create image with max width to fit page
				img = RLImage(photo_path, width=15*cm, height=15*cm, kind='proportional')
				story.append(img)
				story.append(Spacer(1, 0.5*cm))
			except Exception as e:
				# If image can't be loaded, just show a note
				story.append(Paragraph(f"[{_('Photo unavailable')}: {str(e)}]", normal_style))
				story.append(Spacer(1, 0.3*cm))
	
	# Footer with metadata
	footer_data = [
		[_('Created:'), response_obj.created_at.strftime('%d.%m.%Y %H:%M')],
		[_('Total score:'), f"{response_obj.total_score} {_('points')}"],
		[_('Threat level:'), response_obj.threat_level],
	]
	if response_obj.created_by:
		footer_data.insert(0, [_('Created by:'), f"{response_obj.created_by.first_name} {response_obj.created_by.last_name}"])
	
	footer_table = Table(footer_data, colWidths=[4*cm, 13*cm])
	footer_table.setStyle(TableStyle([
		('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f3f4f6')),
		('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1f2937')),
		('ALIGN', (0, 0), (-1, -1), 'LEFT'),
		('FONTNAME', (0, 0), (0, -1), bold_font),
		('FONTNAME', (1, 0), (-1, -1), normal_font),
		('FONTSIZE', (0, 0), (-1, -1), 9),
		('BOTTOMPADDING', (0, 0), (-1, -1), 6),
		('TOPPADDING', (0, 0), (-1, -1), 6),
		('LEFTPADDING', (0, 0), (-1, -1), 10),
		('RIGHTPADDING', (0, 0), (-1, -1), 10),
		('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb'))
	]))
	story.append(footer_table)
	
	# Build PDF
	doc.build(story)
	
	return response


@login_required
def logout_view(request):
	"""Custom logout view that works for all authenticated users."""
	from django.contrib.auth import logout
	logout(request)
	return redirect('admin:login')
