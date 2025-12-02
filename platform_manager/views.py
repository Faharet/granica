from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, ListView, TemplateView, DeleteView
from django.views import View

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


@method_decorator(user_passes_test(is_manager), name='dispatch')
class ResponsesListView(ListView):
	model = FormResponse
	template_name = 'platform_manager/form_responses_list.html'
	context_object_name = 'responses'
	paginate_by = 50


@method_decorator(user_passes_test(is_manager), name='dispatch')
class FormResponseDetailView(TemplateView):
	template_name = 'platform_manager/form_response_detail.html'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		pk = kwargs.get('pk')
		context['response'] = FormResponse.objects.filter(pk=pk).first()
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
