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


def is_manager(user):
	"""Return True only if the user is in the 'manager' group.

	Note: superusers and staff are intentionally NOT granted implicit manager
	rights here so group-based permissions are enforced consistently.
	"""
	if not user or not user.is_authenticated:
		return False
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
			'total_steps': 23,
		}
		return render(request, self.template_name, context)
	
	def post(self, request):
		current_step = int(request.POST.get('current_step', 1))
		action = request.POST.get('action', 'next')
		
		# Сохраняем данные текущего шага в сессию
		form_data = request.session.get('form_data', {})
		for key, value in request.POST.items():
			if key not in ['csrfmiddlewaretoken', 'current_step', 'action']:
				form_data[key] = value
		request.session['form_data'] = form_data
		
		if action == 'previous':
			next_step = max(1, current_step - 1)
			return redirect(f"{request.path}?step={next_step}")
		elif action == 'next':
			next_step = min(23, current_step + 1)
			return redirect(f"{request.path}?step={next_step}")
		elif action == 'submit':
			# Финальная отправка
			form = FormResponseForm(form_data)
			assessment_form = BorderOfficerAssessmentForm(form_data)
			
			if form.is_valid():
				instance = form.save(commit=False)
				if request.user.is_authenticated:
					instance.created_by = request.user
				instance.save()
				
				# Create officer assessment if there's assessment data
				if assessment_form.is_valid():
					assessment = assessment_form.save(commit=False)
					assessment.form_response = instance
					assessment.assessed_by = request.user
					assessment.calculate_score()
					assessment.save()
					
					# Update response with assessment score
					instance.total_score = assessment.total_score
					instance.threat_level = assessment.threat_level
					instance.save()
				
				request.session.pop('form_data', None)
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
		
		return queryset.order_by('-created_at')
	
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['is_manager'] = is_manager(self.request.user)
		
		# Add filter values to context for form persistence
		context['date_from'] = self.request.GET.get('date_from', '')
		context['date_to'] = self.request.GET.get('date_to', '')
		context['created_by'] = self.request.GET.get('created_by', '')
		context['threat_level'] = self.request.GET.get('threat_level', '')
		
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
		response = FormResponse.objects.filter(pk=pk).first()
		
		# Check access: managers can see all, others can only see their own
		if response:
			if not is_manager(request.user) and response.created_by != request.user:
				# Redirect to responses list if trying to access someone else's form
				return redirect('platform_manager:form_responses')
		
		return super().get(request, *args, **kwargs)

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		pk = kwargs.get('pk')
		response = FormResponse.objects.filter(pk=pk).first()
		
		context['response'] = response
		context['is_manager'] = is_manager(self.request.user)
		
		# Check if delete button should be shown
		# Managers always see delete button, submitters only within 30 minutes
		if response:
			if is_manager(self.request.user):
				context['can_delete'] = True
			else:
				# Submitters can delete only within 30 minutes
				time_since_creation = timezone.now() - response.created_at
				context['can_delete'] = time_since_creation < timedelta(minutes=30)
		else:
			context['can_delete'] = False
		
		return context


@method_decorator(user_passes_test(is_manager), name='dispatch')
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
def logout_view(request):
	"""Custom logout view that works for all authenticated users."""
	from django.contrib.auth import logout
	logout(request)
	return redirect('admin:login')
