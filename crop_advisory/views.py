from django.shortcuts import render

import json
from django.core.serializers.json import DjangoJSONEncoder

#Market price tracking 
from django.http import JsonResponse
from .models import crop_price


#for ml model ( pest/disease detection )
import os # for path
from ultralytics import YOLO
from django.core.files.storage import default_storage # for storing the image
from django.core.files.base import ContentFile # for reading the image
from django.conf import settings

#chatbot 

from .nlp_engine import get_bot_response, preprocess_bot_response 
from .translator import  detect_language , translate_to_english , translate_to_user_language

# Create your views here.

def home(req):
    return render(req,'dashboard.html')

def chatbot(request):
    return render(request, "chatbot_app.html")

def chat_api(request):
    if request.method == "POST":

        user_message = request.POST.get("message", "")
        print(" User Query : ",user_message)

        lang=detect_language(user_message)
        print(" Detected Language : ",lang)

        message_in_english = translate_to_english(user_message, lang)
        print(" Translated Text : ",message_in_english)

        raw_response = get_bot_response(message_in_english)
        
        structured_response=preprocess_bot_response(raw_response)

        translated_response = translate_to_user_language(structured_response, lang)
        print("User Language text : ",translated_response)

        
        return JsonResponse({"reply": translated_response})
    return JsonResponse({"error": "POST request required."}, status=400)



def pest(request):

    REMEDIES = {
        # 🍎 Apple
        "Apple__Apple_scab": "Remove and destroy infected leaves, apply fungicides (e.g., mancozeb, captan), and plant resistant varieties.",
        "Apple_Black_rot": "Prune and burn infected branches, apply fungicides (copper-based), and avoid fruit injuries.",
        "Apple_Cedar_apple_rust": "Remove nearby cedar trees if possible, apply fungicides during early season, and plant resistant varieties.",
        "Apple_healthy": "No action needed. Maintain regular pruning and balanced fertilization.",

        # 🫐 Blueberry
        "Blueberry_healthy": "No action needed. Maintain mulching and irrigation for healthy growth.",

        # 🍒 Cherry
        "Cherry(including_sour)Powdery_mildew": "Apply sulfur or potassium bicarbonate sprays, prune dense canopy for airflow, and avoid overhead watering.",
        "Cherry(including_sour)healthy": "No action needed. Maintain pruning and pest monitoring.",

        # 🌽 Corn
        "Corn(maize)Cercospora_leaf_spot Gray_leaf_spot": "Rotate crops, use resistant hybrids, apply fungicides (strobilurins, triazoles).",
        "Corn(maize)Common_rust": "Plant resistant hybrids, apply fungicides during early infection, and avoid late planting.",
        "Corn_(maize)Northern_Leaf_Blight": "Use resistant varieties, rotate crops, and apply fungicides if severe.",
        "Corn(maize)healthy": "No action needed. Maintain soil fertility and crop rotation.",

        # 🍇 Grape
        "Grape_Black_rot": "Remove infected leaves/fruit, apply fungicides (myclobutanil, mancozeb), and maintain airflow in vineyards.",
        "Grape_Esca(Black_Measles)": "Prune infected wood, avoid excessive stress (drought, wounds), and remove dead vines.",
        "Grape__Leaf_blight(Isariopsis_Leaf_Spot)": "Prune infected leaves, use protective fungicides, and maintain vineyard hygiene.",
        "Grape__healthy": "No action needed. Maintain balanced irrigation and canopy management.",

        # 🍊 Orange
        "Orange_Haunglongbing(Citrus_greening)": "No cure available. Remove infected trees, control psyllid vector, and plant certified disease-free seedlings.",

        # 🍑 Peach
        "Peach__Bacterial_spot": "Use resistant varieties, apply copper fungicides, and avoid overhead irrigation.",
        "Peach_healthy": "No action needed. Maintain regular monitoring and pruning.",

        # 🫑 Pepper
        "Pepper,_bell_Bacterial_spot": "Use disease-free seeds, apply copper-based sprays, and avoid handling wet plants.",
        "Pepper,_bell_healthy": "No action needed. Maintain crop rotation and soil fertility.",

        # 🥔 Potato
        "Potato_Early_blight": "Apply fungicides (chlorothalonil, mancozeb), rotate crops, and remove infected debris.",
        "Potato_Late_blight": "Apply systemic fungicides (metalaxyl, cymoxanil), destroy infected plants, and avoid overhead watering.",
        "Potato_healthy": "No action needed. Ensure good hilling and irrigation management.",

        # 🍓 Raspberry
        "Raspberry_healthy": "No action needed. Maintain pruning and mulching.",

        # 🌱 Soybean
        "Soybean_healthy": "No action needed. Maintain weed control and rotation.",

        # 🎃 Squash
        "Squash_Powdery_mildew": "Apply sulfur fungicides, use resistant varieties, and ensure good air circulation.",

        # 🍓 Strawberry
        "Strawberry___Leaf_scorch": "Remove infected leaves, use resistant varieties, and apply fungicides if severe.",
        "Strawberry___healthy": "No action needed. Maintain drip irrigation and mulching.",

        # 🍅 Tomato
        "Tomato___Bacterial_spot": "Use disease-free seeds, apply copper sprays, and rotate crops.",
        "Tomato___Early_blight": "Apply fungicides (chlorothalonil, mancozeb), mulch soil, and rotate crops.",
        "Tomato___Late_blight": "Destroy infected plants, apply systemic fungicides, and avoid water splash.",
        "Tomato___Leaf_Mold": "Improve ventilation, avoid excess humidity, and apply fungicides (chlorothalonil).",
        "Tomato___Septoria_leaf_spot": "Remove infected leaves, apply fungicides, and mulch to reduce soil splash.",
        "Tomato_Spider_mites Two-spotted_spider_mite": "Use miticides, spray neem oil, and encourage natural predators.",
        "Tomato_Target_Spot": "Apply fungicides, remove lower infected leaves, and avoid overcrowding.",
        "Tomato_Tomato_Yellow_Leaf_Curl_Virus": "No cure. Remove infected plants, control whiteflies, and use resistant varieties.",
        "Tomato_Tomato_mosaic_virus": "No cure. Remove infected plants, disinfect tools, and use resistant varieties.",
        "Tomato___healthy": "No action needed. Maintain balanced nutrition and pest control."
    }


    if request.method == "POST" and request.FILES.get("image"):

        MODEL_PATH = os.path.join(settings.BASE_DIR, "best.pt")
        model = YOLO(MODEL_PATH)

        # 1. Save uploaded file
        uploaded_file = request.FILES["image"]
        temp_path = default_storage.save(
            "uploads/" + uploaded_file.name,
            ContentFile(uploaded_file.read())
        )
        input_path = os.path.join(settings.MEDIA_ROOT, temp_path)

        # 2. Run YOLOv8 inference
        results = model.predict(
            source=input_path,
            save=True,  # save annotated image(s)
            project=os.path.join(settings.MEDIA_ROOT, "results"),
            name="exp",   # folder name under project
            exist_ok=True # reuse "exp" instead of exp2, exp3...
        )

        cls_id = int(results[0].boxes.cls[0])  # take the first prediction
        class_name = model.names[cls_id]
        remedy = REMEDIES.get(class_name, "No remedy available.")
        remedy_list = [r.strip() for r in remedy.split(",")]
        print(class_name)
        print(remedy)
        print(remedy_list)


        # 3. YOLOv8 saves image in: media/results/exp/<filename>
        output_filename = os.path.basename(input_path)
        output_url = settings.MEDIA_URL + f"results/exp/{output_filename}"

        return render(request, "pest_detection.html", {"output_url": output_url,"remedy":remedy_list,'disease':class_name})    
    return render(request,'pest_detection.html')


def market_view(request):
    
    commodities = ["Absinthe", "Ajwan", "Alasande Gram", "Almond(Badam)", "Alsandikai", "Amaranthus", "Ambada Seed", "Ambady/Mesta", "Amla(Nelli Kai)", "Amphophalus", "Amranthas Red", "Antawala", "Anthurium", "Apple", "Apricot(Jardalu/Khumani)", "Arecanut(Betelnut/Supari)", "Arhar (Tur/Red Gram)(Whole)", "Arhar Dal(Tur Dal)", "Asalia", "Asgand", "Ashgourd", "Ashwagandha", "Asparagus", "Astera", "Avare Dal", "Bajra(Pearl Millet/Cumbu)", "Banana", "Banana - Green", "Barley (Jau)", "basil", "Beans", "Beetroot", "Behada", "Bengal Gram Dal (Chana Dal)", "Bengal Gram(Gram)(Whole)", "Ber(Zizyphus/Borehannu)", "Betal Leaves", "Bhindi(Ladies Finger)", "Bhui Amlaya", "Black Gram (Urd Beans)(Whole)", "Black Gram Dal (Urd Dal)", "Black pepper", "BOP", "Brahmi"]
    states = ["Madhya Pradesh", "Gujarat", "Uttar Pradesh", "Rajasthan", "Himachal Pradesh", "Maharashtra", "Andhra Pradesh", "Haryana", "Telangana", "Karnataka", "Odisha", "Kerala", "Punjab", "Tamil Nadu", "Tripura", "NCT of Delhi", "Jammu and Kashmir", "Uttrakhand", "Chandigarh", "Goa", "West Bengal", "Meghalaya", "Nagaland", "Chattisgarh", "Manipur", "Assam"]

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        data_type = request.GET.get("type")
        state_name = request.GET.get("state")

        if data_type == "commodities":
            return JsonResponse({"commodities": commodities})

        elif data_type == "states":
            return JsonResponse({"states": states})
        
        elif data_type == "districts" and state_name:
            districts = list(crop_price.objects.filter(state=state_name).values_list("city", flat=True).distinct())
            return JsonResponse({"districts": districts})
        
        

    # Default render with template
    return render(request, "market_price.html")


def marketPrice(req):

    commodity = req.GET.get("commodity", "")
    state = req.GET.get("state", "")
    district=req.GET.get("district","")

    data = []
    data_json = "[]"

    if( commodity and state ):

        data = crop_price.objects.filter(commodity=commodity,state=state,city=district).order_by('-date').values(); #date__gte=seven_days_ago
        data_json = json.dumps(list(data), cls=DjangoJSONEncoder)
        return render(req,'market_price.html',{"data":data, "data_json": data_json})

    return render(req,'market_price.html')

def weather(req):
    return render(req,'weather.html')

def articles(req):
    return render(req,'articles.html')