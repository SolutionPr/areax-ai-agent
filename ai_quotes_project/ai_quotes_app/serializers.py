from rest_framework import serializers
from.models import Quotes_DB,UploadedPDF
class QuoteSerializer(serializers.Serializer):
    class Meta:
        model=Quotes_DB
        fields="__all__"

class UploadedPDFSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedPDF
        fields = ['pdf_file']