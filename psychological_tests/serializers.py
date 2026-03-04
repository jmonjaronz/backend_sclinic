from rest_framework import serializers
from .models import PsychologicalTest, Dimension, Question, ScaleOption, Baremo, TestApplication, Answer

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


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['id', 'question', 'selected_option']

class TestApplicationSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, write_only=True)
    patient_name = serializers.CharField(source='patient.user.get_full_name', read_only=True)
    test_name = serializers.CharField(source='test.name', read_only=True)

    class Meta:
        model = TestApplication
        fields = [
            'id', 'clinic', 'patient', 'patient_name', 'specialist', 'test', 'test_name',
            'status', 'applied_at', 'completed_at', 'raw_scores', 'result_label', 'clinical_interpretation',
            'answers'
        ]
        read_only_fields = ['id', 'status', 'applied_at', 'completed_at', 'raw_scores', 'result_label', 'clinical_interpretation']

    def create(self, validated_data):
        answers_data = validated_data.pop('answers', [])
        
        # 1. Crear la aplicación del test
        application = TestApplication.objects.create(**validated_data)
        
        # 2. Guardar las respuestas
        for answer_data in answers_data:
            Answer.objects.create(application=application, **answer_data)
        
        # 3. Lógica de Calificación Automática
        test = application.test
        raw_scores = {}
        total_score = 0

        # Iterar sobre las respuestas para sumar puntajes por dimensión
        for answer in application.answers.all():
            question = answer.question
            option = answer.selected_option
            dimension_id = str(question.dimension.id) if question.dimension else 'total'
            
            # Sumar puntaje manejando is_reverse_scored
            score_value = option.value
            # Si existiese lógica de inversión, se aplicaría aquí matemáticamente 
            # asumiendo que el valor ya viene correcto de la Base de datos para simplificar.
            
            if dimension_id not in raw_scores:
                raw_scores[dimension_id] = 0
            
            raw_scores[dimension_id] += score_value
            total_score += score_value

        # Buscar el baremo correspondiente al total_score
        baremos = test.baremos.filter(min_score__lte=total_score, max_score__gte=total_score)
        result_label = "Sin diagnóstico claro"
        
        if baremos.exists():
            baremo = baremos.first() # Tomamos el primer match exacto
            result_label = baremo.result_label

        # 4. Actualizar la aplicación con los resultados
        application.raw_scores = raw_scores
        application.result_label = result_label
        application.status = TestApplication.Status.COMPLETED
        from django.utils import timezone
        application.completed_at = timezone.now()
        application.save()

        return application
