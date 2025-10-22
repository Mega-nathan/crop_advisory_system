from django.shortcuts import render,redirect,get_object_or_404

import json
from django.core.serializers.json import DjangoJSONEncoder

#multilingual articles
import requests
from googletrans import Translator

#Market price tracking 
from django.http import JsonResponse
from .models import crop_price
from datetime import date, timedelta


#for ml model ( pest/disease detection )
import os # for path
from ultralytics import YOLO
from django.core.files.storage import default_storage # for storing the image
from django.core.files.base import ContentFile # for reading the image
from django.conf import settings

#chatbot 
#from .nlp_engine import get_bot_response, preprocess_bot_response 
from .nlp_engine import  preprocess_bot_response 
from .translator import  detect_language , translate_to_english , translate_to_user_language

#chatbot offline functionality
from transformers import pipeline
from django.http import JsonResponse
import json 
import numpy as np
from sentence_transformers import SentenceTransformer , util


#complaint
from .models import Complaint_Box

#artilces
translator = Translator()


#loading model 
generator = pipeline("text2text-generation", model="google/flan-t5-small")

# qa_model = pipeline("question-answering",
#                     model="distilbert-base-uncased-distilled-squad")
#qa_model = pipeline("question-answering", model="deepset/tinyroberta-squad2") smaller
#qa_model = pipeline("question-answering", model="sshleifer/tiny-distilroberta-base") even smaller


embedder = SentenceTransformer("all-MiniLM-L6-v2")


# Load knowledge base
with open("data.json") as f:
    knowledge = json.load(f)
corpus = [item["advice"] for item in knowledge]
corpus_embeddings = embedder.encode(corpus, convert_to_tensor=True)



def home(req):
    return render(req,'dashboard.html')

def chatbot(request):
    return render(request, "chatbot_app.html")

def sample_chat(message):

    print(" sample chat Entered ")

    question = message
    print(question)
    #question = request.GET.get("query", "")
    
    # Simple fixed context (later replaced by retrieved text)
    # context = """
    # Farmers can improve soil fertility using organic compost, crop rotation,
    # and green manure. To control pests in tomato crops, neem oil or biological
    # controls can be effective.
    # """
    query_emb = embedder.encode(question, convert_to_tensor=True)
    similarity = util.cos_sim(query_emb, corpus_embeddings)
    best_idx = np.argmax(similarity.cpu().numpy())
    best_context = corpus[best_idx]

    # if not question:
    #     return JsonResponse({"answer": "Please ask a question."})

    # answer = qa_model(question=question, context=best_context)

    input_text = f"Question: {question} Context: {best_context}"
    generated = generator(input_text, max_length=300)
    answer = generated[0]['generated_text']

    print("Answer : " , answer)
    # return JsonResponse({"answer": answer["answer"]})
    return answer

def chat_api(request):
    if request.method == "POST":

        user_message = request.POST.get("message", "")
        print(" User Query : ",user_message)

        lang=detect_language(user_message)
        print(" Detected Language : ",lang)

        message_in_english = translate_to_english(user_message, lang)
        print(" Translated Text : ",message_in_english)

        #raw_response = get_bot_response(message_in_english)
            
        print(raw_response)
        
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
    recommendation = None
    message = None

    if( commodity and state ):

        today = date.today()
        one_month_ago = today - timedelta(days=30)

        data = crop_price.objects.filter(commodity=commodity,state=state,city=district,date__gte=one_month_ago).order_by('-date').values(); #date__gte=seven_days_ago
        data_json = json.dumps(list(data), cls=DjangoJSONEncoder)

        if len(data) == 0:
            # No data at all
            message = "No market data available for this crop and location."
        elif len(data) < 10:
            # 🔸 Less than 10 days of data → fallback strategy
            prices = [float(d['modal_Price']) for d in data]
            latest_price = prices[0]
            max_price = max(prices)
            min_price = min(prices)

            if latest_price >= max_price:
                recommendation = "SELL (Peak Price)"
            elif latest_price <= min_price:
                recommendation = "HOLD (Price at Low)"
            else:
                recommendation = "HOLD (Uncertain Trend)"
        else:
            # ✅ Sufficient data → full 1-month trend analysis
            prices = [float(d['modal_Price']) for d in data]

            # Define split ratio dynamically based on available data
            split_index = len(prices) // 3   # roughly 1/3 recent, 2/3 earlier
            recent_avg = sum(prices[:split_index]) / split_index
            earlier_avg = sum(prices[split_index:]) / max(len(prices[split_index:]), 1)

            change = ((recent_avg - earlier_avg) / earlier_avg) * 100

            if change > 5:
                recommendation = "SELL"
            elif change < -5:
                recommendation = "HOLD"
            else:
                recommendation = "HOLD (Stable)"

        return render(req,'market_price.html',{"data":data, "data_json": data_json,"recommendation":recommendation,"message":message})

    return render(req,'market_price.html')

def weather(req):
    return render(req,'weather.html')

def articles(req):
    return render(req,'articles.html')

def complaint_box(request):
    if request.method == "POST":
        farmer_name = request.POST.get("farmer_name")
        mobile = request.POST.get("mobile")
        crop_type = request.POST.get("crop_type")
        description = request.POST.get("description")
        image = request.FILES.get("image")

        complaint = Complaint_Box.objects.create(
            farmer_name=farmer_name,
            mobile=mobile,
            crop_type=crop_type,
            description=description,
            image=image,
        )

        # run quick validation check
        return redirect("validate_complaint", complaint_id=complaint.id)

    return render(request, "complaint_box.html")

def validate_complaint(request, complaint_id):
    complaint = get_object_or_404(Complaint_Box, id=complaint_id)

    # Fake rule: If crop is rice + "flood" in description -> approve
    if complaint.crop_type.lower() == "rice" and "flood" in complaint.description.lower():
        complaint.status = "Approved"
    elif "damage" in complaint.description.lower():
        complaint.status = "Under Review"
    else:
        complaint.status = "Pending"

    complaint.save()
    return redirect("admin_dashboard")


# iii) Dashboard to display complaints
def dashboard(request):
    complaints = Complaint_Box.objects.all().order_by("-created_at")
    return render(request, "admin_dashboard.html", {"complaints": complaints})


original_articles = []
NEWS_API_KEY = "e37b0c5a0091475e8e4b8f0a4d1093d9"


def multilingual_article(request):
    """Fetch agriculture-related news articles and render on homepage"""
    global original_articles

    url = f"https://newsapi.org/v2/everything?q=agriculture OR farming OR farmers&language=en&apiKey={NEWS_API_KEY}"
    response = requests.get(url)
    data = response.json()

    if data.get("status") == "ok":
        original_articles = data.get("articles", [])[:6]
    else:
        original_articles = []

    return render(request, "multilingual_article.html", {"articles": original_articles})

def translate_news(request):
    """Translate all articles to selected language"""
    global original_articles
    print("Entered")

    if request.method == "POST":
        import json
        data = json.loads(request.body.decode("utf-8"))
        selected_lang = data.get("language", "en")
        print(selected_lang)

        translated_articles = []
        for article in original_articles:
            title = article.get("title", "")
            desc = article.get("description", "")

            translated_title = translator.translate(title, dest=selected_lang).text if title else ""
            translated_desc = translator.translate(desc, dest=selected_lang).text if desc else ""

            translated_articles.append({
                "title": translated_title,
                "description": translated_desc,
                "urlToImage": article.get("urlToImage"),
                "url": article.get("url"),
            })

        return JsonResponse(translated_articles, safe=False)

    return JsonResponse({"error": "Invalid request method"}, status=400)