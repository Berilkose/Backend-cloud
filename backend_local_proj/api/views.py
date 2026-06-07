import io
from PIL import Image
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

@api_view(['POST'])
@csrf_exempt
def get_resolution(request):
    """
    1) http://BULUT-URL/get/resolution
    Gelen resmin çözünürlüğünü döndürür.
    """
    if request.FILES.get('image'):
        try:
            image_file = request.FILES['image']
            img = Image.open(image_file)
            width, height = img.size
            
            return Response({
                'status': 'success',
                'resolution': f"{width}x{height}",
                'width': width,
                'height': height
            }, status=200)
        except Exception as e:
            return Response({'error': f"Image reading error: {str(e)}"}, status=400)
            
    return Response({'error': 'Please send an image with the "image" key.'}, status=400)


@api_view(['POST'])
@csrf_exempt
def convert_grayscale(request):
    """
    2) http://BULUT-URL/convert/grayscale
    Gelen resmi siyah-beyaza çevirip geri fırlatır.
    """
    if request.FILES.get('image'):
        try:
            image_file = request.FILES['image']
            img = Image.open(image_file)
            
            # Resmi Grayscale formatına (L) dönüştür
            grayscale_img = img.convert('L')
            
            # Sunucu diskine yazmadan RAM üzerinde hafıza havuzuna kaydet
            buffer = io.BytesIO()
            grayscale_img.save(buffer, format="PNG")
            buffer.seek(0)
            
            return HttpResponse(buffer.getvalue(), content_type="image/png")
        except Exception as e:
            return Response({'error': f"Conversion error: {str(e)}"}, status=400)
            
    return Response({'error': 'Please send an image with the "image" key.'}, status=400)