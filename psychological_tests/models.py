from django.db import models
import uuid
from clinics.models import Clinic
from patients.models import Patient
from appointments.models import Appointment

class PsychologicalTest(models.Model):
    """
    Definition of a Test (e.g., PHQ-9, GAD-7, MiniMental).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    instructions = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Dimension(models.Model):
    """
    Parts of a test (e.g., Depressive mood, Anxiety levels).
    """
    test = models.ForeignKey(PsychologicalTest, on_delete=models.CASCADE, related_name='dimensions')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    weight = models.FloatField(default=1.0)

    def __str__(self):
        return f"{self.test.name} - {self.name}"

class Question(models.Model):
    """
    Individual items/questions.
    """
    dimension = models.ForeignKey(Dimension, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.dimension.test.name}: {self.text[:50]}"

class ScaleOption(models.Model):
    """
    Options for a question (e.g., Not at all = 0, Several days = 1).
    """
    test = models.ForeignKey(PsychologicalTest, on_delete=models.CASCADE, related_name='scale_options')
    label = models.CharField(max_length=255)
    value = models.IntegerField()

    def __str__(self):
        return f"{self.test.name}: {self.label} ({self.value})"

class Baremo(models.Model):
    """
    Interpretation of total scores.
    """
    test = models.ForeignKey(PsychologicalTest, on_delete=models.CASCADE, related_name='baremos')
    dimension = models.ForeignKey(Dimension, on_delete=models.SET_NULL, null=True, blank=True, related_name='baremos')
    min_score = models.IntegerField()
    max_score = models.IntegerField()
    result_text = models.CharField(max_length=255) # e.g. "Ansiedad Moderada"
    clinical_interpretation = models.TextField(blank=True)

    def __str__(self):
        return f"{self.test.name} ({self.min_score}-{self.max_score}): {self.result_text}"

class TestApplication(models.Model):
    """
    An instance of a patient taking a test.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    test = models.ForeignKey(PsychologicalTest, on_delete=models.PROTECT)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='test_applications')
    appointment = models.ForeignKey(Appointment, on_delete=models.SET_NULL, null=True, blank=True)
    
    total_score = models.IntegerField(null=True, blank=True)
    result_label = models.CharField(max_length=255, blank=True)
    clinical_notes = models.TextField(blank=True)
    
    applied_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.test.name} - {self.patient} ({self.applied_at.date()})"

class Answer(models.Model):
    """
    Specific answer to a question in an application.
    """
    application = models.ForeignKey(TestApplication, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_option = models.ForeignKey(ScaleOption, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.application.id} - Q: {self.question.id}"
