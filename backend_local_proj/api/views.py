import os
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
#from huggingface_hub import login
#from transformers import pipeline
#from diffusers import StableDiffusionPipeline
from PIL import Image
#import torch
import io

# ========================================================
# ROBOMUNCH ENTEGRE YAPAY ZEKA MOTORU
# ========================================================
class RoboMunchEngine:
    
    def __init__(self):
        from huggingface_hub import login
        self.pipelines = {}
        self.device = "cpu"  # CPU üzerinde çalıştırıyoruz
        
        # Hugging Face Login 
        my_token = os.getenv("HF_TOKEN")
        if my_token:
            login(token=my_token)

        print(f"--- RoboMunch Engine Initialized (CPU) ---")

    def _get_pipeline(self, task, model_name, **kwargs):
        from transformers import pipeline
        if task not in self.pipelines:
            print(f"--- Loading {task}: {model_name} ---")
            self.pipelines[task] = pipeline(
                task, 
                model=model_name, 
                device=self.device,
                token=True,
                **kwargs
            )
        return self.pipelines[task]

    def chat_reply(self, message):
        pipe = self._get_pipeline("text-generation", "HuggingFaceTB/SmolLM2-135M-Instruct")
        
        system_prompt = (
            "You are RoboMunch, you ACT AS A PHOTO-REALISTIC ART PROMPT GENERATOR."
            "Your job is to generate concise, descriptive, and high-quality image prompts for AI generation. "
            "Focus on visual elements: subject, environment, lighting, art style, and color palette. "
            "Your ONLY output should be a detailed prompt about digital images. Don't add abstract words."
        )
        
        prompt = f"<|im_start|>system\n{system_prompt}<|im_end|>\n<|im_start|>user\n{message}<|im_end|>\n<|im_start|>assistant\n"
        
        out = pipe(prompt, 
                   max_new_tokens=128, 
                   do_sample=True, 
                   temperature=0.7,
                   pad_token_id=50256)
        
        response = out[0]['generated_text'].split("<|im_start|>assistant\n")[-1].replace("<|im_end|>", "").strip()
        return response
    
    def generate_image(self, prompt):
        import torch
        from diffusers import StableDiffusionPipeline
        if not prompt: return None
        
        if "text-to-image" not in self.pipelines:
            print("--- Loading Stable Diffusion v1-5 (This may take a while on CPU) ---")
            self.pipelines["text-to-image"] = StableDiffusionPipeline.from_pretrained(
                "runwayml/stable-diffusion-v1-5",
                torch_dtype=torch.float32,
                use_safetensors=True
            ).to(self.device)

        pipe = self.pipelines["text-to-image"]
        print(f"--- Generating Image for: {prompt} ---")
        
        image = pipe(prompt, num_inference_steps=15).images[0]
        return image

#munch_engine = RoboMunchEngine()


# ========================================================
# DJANGO API KAPILARI (ENDPOINT'LER)
# ========================================================

@api_view(['POST'])
def chat_with_munch(request):
    munch_engine = RoboMunchEngine()
    user_message = request.data.get('message', '')
    if not user_message:
        return Response({'reply': 'Boş mesaj gönderilemez.'}, status=400)
    
    try:
        bot_reply = munch_engine.chat_reply(user_message)
        return Response({'reply': bot_reply})
            
    except Exception as e:
        return Response({'reply': f"Yapay zeka motoru hatası: {str(e)}"}, status=500)


@api_view(['POST'])
def paint_image(request):
    munch_engine = RoboMunchEngine()
    prompt = request.data.get('prompt', '')
    if not prompt:
        return Response({'error': 'Prompt boş olamaz.'}, status=400)
        
    try:
        pil_img = munch_engine.generate_image(prompt)
        
        if pil_img:
            buffer = io.BytesIO()
            pil_img.save(buffer, format="JPEG")
            return HttpResponse(buffer.getvalue(), content_type="image/jpeg")
        else:
            return Response({'error': 'Resim üretilemedi.'}, status=500)
            
    except Exception as e:
        return Response({'error': f"Görsel motoru hatası: {str(e)}"}, status=500)


# ========================================================
# ÖDEV 2. TASK İÇİN EKLENEN BULUT ENDPOINT'LERİ
# ========================================================

@api_view(['POST'])
@csrf_exempt
def get_resolution(request):
    """
    1) http://BULUT-URL/get/resolution
    Flutter uygulamasından gönderilen yapay zeka resminin çözünürlüğünü döner.
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
            return Response({'error': f"Resim okuma hatası: {str(e)}"}, status=400)
            
    return Response({'error': 'Lütfen "image" anahtarı ile bir görsel gönderin.'}, status=400)


@api_view(['POST'])
@csrf_exempt
def convert_grayscale(request):
    """
    2) http://BULUT-URL/convert/grayscale
    Flutter'dan gelen resmi siyah-beyaza çevirip binary PNG olarak geri fırlatır.
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
            
            # Resmi doğrudan binary data akışı (stream) olarak Flutter'a geri gönder
            return HttpResponse(buffer.getvalue(), content_type="image/png")
        except Exception as e:
            return Response({'error': f"Dönüştürme hatası: {str(e)}"}, status=400)
            
    return Response({'error': 'Lütfen "image" anahtarı ile bir görsel gönderin.'}, status=400)