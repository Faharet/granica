from django.urls import path
from . import views

app_name = 'platform_manager'

urlpatterns = [
	path('submit/', views.SubmitFormView.as_view(), name='form_submit'),
	path('submitted/', views.FormSubmittedView.as_view(), name='form_submitted'),
	path('responses/', views.ResponsesListView.as_view(), name='form_responses'),
	path('responses/<uuid:pk>/', views.FormResponseDetailView.as_view(), name='form_response_detail'),
	path('responses/<uuid:pk>/delete/', views.FormResponseDeleteView.as_view(), name='form_response_delete'),
	path('responses/<uuid:pk>/assess/', views.OfficerAssessmentView.as_view(), name='officer_assessment'),
]