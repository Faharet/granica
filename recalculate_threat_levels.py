"""
Скрипт для пересчета уровней угрозы для всех существующих записей
после изменения пороговых значений (0-49 Low, 50-120 Medium, 121+ High)
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'granica_admin.settings')
django.setup()

from platform_manager.models import FormResponse, BorderOfficerAssessment

def recalculate_all_threat_levels():
    """Recalculate threat levels for all existing records"""
    
    # Recalculate FormResponse threat levels
    form_responses = FormResponse.objects.all()
    print(f"Пересчет {form_responses.count()} записей FormResponse...")
    
    updated_responses = 0
    for response in form_responses:
        old_level = response.threat_level
        response.calculate_score()
        response.save()
        if old_level != response.threat_level:
            print(f"  ID {response.id}: {old_level} -> {response.threat_level} (баллы: {response.total_score})")
            updated_responses += 1
    
    print(f"✓ Обновлено {updated_responses} записей FormResponse\n")
    
    # Recalculate BorderOfficerAssessment threat levels
    assessments = BorderOfficerAssessment.objects.all()
    print(f"Пересчет {assessments.count()} записей BorderOfficerAssessment...")
    
    updated_assessments = 0
    for assessment in assessments:
        old_level = assessment.threat_level
        assessment.calculate_score()
        assessment.save()
        if old_level != assessment.threat_level:
            print(f"  ID {assessment.id}: {old_level} -> {assessment.threat_level} (баллы: {assessment.total_score})")
            updated_assessments += 1
    
    print(f"✓ Обновлено {updated_assessments} записей BorderOfficerAssessment\n")
    
    print("=" * 60)
    print("Пересчет завершен!")
    print(f"Всего обновлено: {updated_responses + updated_assessments} записей")
    print("=" * 60)

if __name__ == "__main__":
    recalculate_all_threat_levels()
