from flask import Blueprint, request, render_template, jsonify, send_file
from app.utils.fetch_reviews import fetch_reviews
from openai import OpenAI
import tempfile
import os
from dotenv import load_dotenv

load_dotenv()

oneriler_bp = Blueprint("oneriler", __name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

summary_cache = {}  # analiz sonuçlarını saklamak için

def generate_summary_chunked(comments: list, chunk_size: int = 100):
    chunks = [comments[i:i + chunk_size] for i in range(0, len(comments), chunk_size)]
    all_summaries = []

    for chunk in chunks:
        prompt = (
            "Aşağıda kullanıcıların bir mobil uygulamayla ilgili yorumları yer almaktadır.\n"
            "Lütfen yorumlara göre iki ayrı başlık altında analiz yap:\n\n"
            "1. Negatif Geri Bildirimler ve Öneriler:\n"
            "- Kullanıcıların yaşadığı sorunlar, teknik eksiklikler ve geliştirme önerileri.\n\n"
            "2. Pozitif Geri Bildirimler:\n"
            "- Kullanıcıların memnun kaldığı, övdüğü ve takdir ettiği özellikler.\n\n"
            "⚠️ Her zaman önce negatif, ardından pozitif başlık yer almalı.\n"
            "⚠️ Pozitif geri bildirimler az bile olsa yazılmalıdır.\n"
            "⚠️ Giriş, açıklama, yorumlama ya da sistem tavsiyesi gibi ek metinler yazma.\n\n"
            "Biçim şu şekilde olmalı:\n"
            "Negatif Geri Bildirimler ve Öneriler:\n- ...\n- ...\n\nPozitif Geri Bildirimler:\n- ...\n- ...\n\n"
            "Yorumlar:\n"
            + "\n".join(f"- {c}" for c in chunk)
        )

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        all_summaries.append(response.choices[0].message.content)

    return "\n\n---\n\n".join(all_summaries)


@oneriler_bp.route("/oneriler")
def oneriler():
    return render_template("oneriler.html")


@oneriler_bp.route("/generate_summary")
def generate_summary_api():
    months = request.args.get("months", "1")
    app = request.args.get("app", "biletinial")
    cache_key = f"{app}_{months}"

    if cache_key in summary_cache:
        return summary_cache[cache_key]

    yorumlar = fetch_reviews(months, app)
    metinler = [y["comment"] for y in yorumlar if len(y["comment"]) > 20]
    summary = generate_summary_chunked(metinler)
    summary_cache[cache_key] = summary
    return summary


@oneriler_bp.route("/download_txt")
def download_txt():
    months = request.args.get("months", "1")
    app = request.args.get("app", "biletinial")
    cache_key = f"{app}_{months}"

    if cache_key in summary_cache:
        summary = summary_cache[cache_key]
    else:
        yorumlar = fetch_reviews(months, app)
        metinler = [y["comment"] for y in yorumlar if len(y["comment"]) > 20]
        summary = generate_summary_chunked(metinler)
        summary_cache[cache_key] = summary

    with tempfile.NamedTemporaryFile(delete=False, mode='w', encoding='utf-8', suffix='.txt') as tmp:
        tmp.write(summary)
        temp_path = tmp.name

    return send_file(temp_path, as_attachment=True, download_name=f"{app}_analiz_ozeti.txt", mimetype="text/plain")
