from flask import Blueprint, render_template

raporlar_bp = Blueprint('raporlar', __name__)

@raporlar_bp.route('/raporlar')
def raporlar():
    return render_template('raporlar.html')
