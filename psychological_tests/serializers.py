from rest_framework import serializers
from django.utils import timezone
from .models import (
    TestBattery, PsychologicalTest, Dimension, Question, ScaleOption, 
    Baremo, TestApplication, Answer, DimensionResult
)
from .logic import calculate_test_results

class ScaleOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScaleOption
        fields = ['id', 'label', 'value', 'order']

class QuestionSerializer(serializers.ModelSerializer):
    options = ScaleOptionSerializer(many=True, read_only=True)
    class Meta:
        model = Question
        fields = ['id', 'dimension', 'text', 'order', 'is_reverse_scored', 'options']

class DimensionSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    class Meta:
        model = Dimension
        fields = ['id', 'name', 'description', 'questions']

class BaremoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Baremo
        fields = '__all__'

class PsychologicalTestSerializer(serializers.ModelSerializer):
    dimensions = DimensionSerializer(many=True, read_only=True)
    baremos = BaremoSerializer(many=True, read_only=True)
    
    class Meta:
        model = PsychologicalTest
        fields = ['id', 'name', 'description', 'instructions', 'dimensions', 'baremos']


class TestBatterySerializer(serializers.ModelSerializer):
    tests = PsychologicalTestSerializer(many=True, read_only=True)
    class Meta:
        model = TestBattery
        fields = ['id', 'clinic', 'name', 'description', 'tests', 'created_at']

class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['id', 'question', 'selected_option']

class DimensionResultSerializer(serializers.ModelSerializer):
    dimension_name = serializers.CharField(source='dimension.name', read_only=True)
    class Meta:
        model = DimensionResult
        fields = ['id', 'dimension', 'dimension_name', 'score', 'result_label']

class TestApplicationSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, write_only=True)
    dimension_results = DimensionResultSerializer(many=True, read_only=True)
    patient_name = serializers.CharField(source='patient.user.get_full_name', read_only=True)
    test_name = serializers.CharField(source='test.name', read_only=True)

    class Meta:
        model = TestApplication
        fields = [
            'id', 'test', 'test_name', 'patient', 'patient_name', 'appointment',
            'modality', 'valid_until', 'applied_at', 'completed_at',
            'total_score', 'result_label', 'clinical_notes', 'answers', 'dimension_results'
        ]
        read_only_fields = ['id', 'total_score', 'result_label', 'applied_at', 'completed_at', 'dimension_results']

    def create(self, validated_data):
        answers_data = validated_data.pop('answers', [])
        application = TestApplication.objects.create(**validated_data)
        
        # Save answers
        for answer_data in answers_data:
            Answer.objects.create(application=application, **answer_data)
        
        # Trigger scoring logic from logic.py
        calculate_test_results(application.id)
        
        # Refresh from DB
        application.refresh_from_db()
        return application
