"""
These classes describe one way of entering into the web site.
"""

from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Student, Document, StudentReadingData
from .analysis import RereadingAnalysis
from .serializers import (
    DocumentSerializer,
    ReadingSerializer,
    StudentReadingDataSerializer,
    StudentSerializer,
)


class Reading:
    """ Class to aggregate all of the models we need to serialize for the reading view """
    def __init__(self, document, reading_data):
        self.document = document
        self.reading_data = reading_data


@api_view(['POST'])
def reading_view(request, pk):
    """ Primary API endpoint for the reading view -- called with the student's name
        from the view (to be written) where we collect that
    """
    student_name = request.data.get('name')
    student = Student(name=student_name)
    student.save()
    doc = Document.objects.get(pk=pk)
    reading_data = StudentReadingData.objects.create(document=doc,
                                                     student=student)
    reading_data.save()
    reading = Reading(doc, reading_data)
    serializer = ReadingSerializer(reading)
    return Response(serializer.data)


class ListStudent(generics.ListCreateAPIView):
    """View a list of students or create a new one"""
    queryset = Student.objects.all()
    serializer_class = StudentSerializer


class DetailStudent(generics.RetrieveUpdateDestroyAPIView):
    """Get a single student's data or update/delete it"""
    queryset = Student.objects.all()
    serializer_class = StudentSerializer


class DetailReadingData(generics.RetrieveUpdateDestroyAPIView):
    """Get a single group of reading data or update/delete it"""
    queryset = StudentReadingData.objects.all()
    serializer_class = StudentReadingDataSerializer


class ListReadingData(generics.ListCreateAPIView):
    """View all instances of reading data"""
    queryset = StudentReadingData.objects.all()
    serializer_class = StudentReadingDataSerializer


@api_view(['GET'])
def analysis(request):
    """
    Init a RereadingAnalysis, and serialize it to send to the frontend.
    """
    analysis_obj = RereadingAnalysis()
    serializer = AnalysisSerializer(instance=analysis_obj)
    return Response(serializer.data)
