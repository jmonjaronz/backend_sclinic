from rest_framework import serializers
from .models import PsychologicalTest, Dimension, Question, ScaleOption, Baremo, TestApplication, Answer

class ScaleOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScaleOption
        fields = ['id', 'label', 'value']

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'text', 'order']

class DimensionSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Dimension
        fields = ['id', 'name', 'description', 'questions']

class PsychologicalTestSerializer(serializers.ModelSerializer):
    dimensions = DimensionSerializer(many=True, read_only=True)
    scale_options = ScaleOptionSerializer(many=True, read_only=True)
    
    class Meta:
        model = PsychologicalTest
        fields = ['id', 'name', 'description', 'instructions', 'price', 'dimensions', 'scale_options']

class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['id', 'question', 'selected_option']

class TestApplicationSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, write_only=True)
    
    class Meta:
        model = TestApplication
        fields = ['id', 'test', 'patient', 'appointment', 'total_score', 'result_label', 'clinical_notes', 'applied_at', 'completed_at', 'answers']
        read_only_fields = ['id', 'total_score', 'result_label', 'clinical_notes', 'applied_at', 'completed_at']

    def create(self, validated_data):
        answers_data = validated_data.pop('answers')
        application = TestApplication.objects.create(**validated_data)
        
        for answer_data in answers_data:
            Answer.objects.create(application=application, **answer_data)
        
        # Trigger calculation
        from .logic import calculate_test_results
        calculate_test_results(application.id)
        
        # Refresh from DB
        application.refresh_from_db()
        return application
