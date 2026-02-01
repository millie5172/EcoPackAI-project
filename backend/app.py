from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
import os

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecopackai.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Material(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    material_type = db.Column(db.String(50))
    co2_per_kg = db.Column(db.Float)
    cost_per_unit = db.Column(db.Float)
    biodegradability = db.Column(db.Integer)
    durability = db.Column(db.Integer)
    recyclability = db.Column(db.Integer)
    decompose_days = db.Column(db.Integer)
    certifications = db.Column(db.JSON)

@app.route('/')
def home():
    return jsonify({
        "message": "EcoPackAI Backend is Running!",
        "endpoints": [
            "/api/materials",
            "/api/recommend",
            "/api/init-db",
            "/api/analytics/dashboard"
        ],
        "status": "active"
    })

@app.route('/api/materials')
def get_materials():
    materials = Material.query.all()
    return jsonify([{
        'id': m.id, 'name': m.name, 'type': m.material_type,
        'co2_per_kg': m.co2_per_kg, 'cost_per_unit': m.cost_per_unit,
        'biodegradability': m.biodegradability, 'durability': m.durability,
        'recyclability': m.recyclability, 'decompose_days': m.decompose_days,
        'certifications': m.certifications or []
    } for m in materials])

@app.route('/api/recommend', methods=['POST'])
def recommend():
    data = request.json
    materials = Material.query.all()
    recommendations = []
    
    for mat in materials:
        pred_cost = round(mat.cost_per_unit * random.uniform(0.9, 1.1), 2)
        pred_co2 = round(mat.co2_per_kg * random.uniform(0.9, 1.1), 3)
        suitability = (mat.biodegradability + mat.durability) / 2
        
        recommendations.append({
            'material_id': mat.id, 'name': mat.name,
            'predicted_cost': pred_cost, 'predicted_co2': pred_co2,
            'suitability_score': round(suitability, 1),
            'biodegradability': mat.biodegradability,
            'durability': mat.durability,
            'decompose_days': mat.decompose_days,
            'recyclability': mat.recyclability,
            'certifications': m.certifications or []
        })
    
    recommendations.sort(key=lambda x: x['suitability_score'], reverse=True)
    for i, rec in enumerate(recommendations):
        rec['rank'] = i + 1
    
    return jsonify({
        'recommendations': recommendations,
        'top_recommendation': recommendations[0]
    })

@app.route('/api/init-db', methods=['GET','POST'])
def init_db():
    db.create_all()
    if Material.query.first() is None:
        materials = [
            Material(name="Sugarcane Bagasse", material_type="Plant Fiber", co2_per_kg=0.15,
                    cost_per_unit=0.42, biodegradability=98, durability=85, recyclability=100,
                    decompose_days=67, certifications=["EN 13432"]),
            Material(name="Mushroom Mycelium", material_type="Bio-based", co2_per_kg=0.08,
                    cost_per_unit=0.85, biodegradability=100, durability=90, recyclability=100,
                    decompose_days=37, certifications=["OK Compost"]),
            Material(name="PLA", material_type="Bioplastic", co2_per_kg=0.68,
                    cost_per_unit=0.65, biodegradability=85, durability=75, recyclability=60,
                    decompose_days=135, certifications=["EN 13432"])
        ]
        db.session.bulk_save_objects(materials)
        db.session.commit()
    return jsonify({'message': 'Database initialized'})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Auto-initialize database on startup
        if Material.query.first() is None:
            materials = [
                Material(name="Sugarcane Bagasse", material_type="Plant Fiber", co2_per_kg=0.15,
                        cost_per_unit=0.42, biodegradability=98, durability=85, recyclability=100,
                        decompose_days=67, certifications=["EN 13432"]),
                Material(name="Mushroom Mycelium", material_type="Bio-based", co2_per_kg=0.08,
                        cost_per_unit=0.85, biodegradability=100, durability=90, recyclability=100,
                        decompose_days=37, certifications=["OK Compost"]),
                Material(name="PLA", material_type="Bioplastic", co2_per_kg=0.68,
                        cost_per_unit=0.65, biodegradability=85, durability=75, recyclability=60,
                        decompose_days=135, certifications=["EN 13432"])
            ]
            db.session.bulk_save_objects(materials)
            db.session.commit()
            print("Database initialized with sample materials")
    
    # Production port configuration
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)