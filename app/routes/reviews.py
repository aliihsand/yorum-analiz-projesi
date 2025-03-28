from flask import Blueprint, request, jsonify, render_template, send_file, current_app
from app.utils.fetch_reviews import fetch_reviews
import pandas as pd
from io import BytesIO
import traceback

reviews_bp = Blueprint("reviews", __name__)

@reviews_bp.route("/")
def index():
    return render_template("index.html")

@reviews_bp.route("/get_reviews")
def get_reviews():
    try:
        months = request.args.get("months", "1")
        app = request.args.get("app", "biletinial")
        data = fetch_reviews(months, app)
        return jsonify(data)
    except Exception as e:
        current_app.logger.error(f"Error in get_reviews: {str(e)}\n{traceback.format_exc()}")
        return jsonify({"error": "Yorumlar alınırken bir hata oluştu. Lütfen tekrar deneyin."}), 500

@reviews_bp.route("/download_reviews")
def download_reviews():
    months = request.args.get("months", "1")
    app = request.args.get("app", "biletinial")
    data = fetch_reviews(months, app)

    df = pd.DataFrame(data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name="Yorumlar")
    output.seek(0)

    filename = f"{app}_yorumlar_{months}_ay.xlsx" if months != "all" else f"{app}_tum_yorumlar.xlsx"

    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=filename
    )