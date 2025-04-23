from flask import Flask, render_template, request, send_file, send_from_directory, make_response, session
from ticket_generator import TicketCaisse
from datetime import datetime
import os
import json

app = Flask(__name__)
app.secret_key = 'votre_clé_secrète_ici'  # Nécessaire pour utiliser session

# Dossier pour stocker les tickets PDF
TICKETS_FOLDER = 'tickets'
if not os.path.exists(TICKETS_FOLDER):
    os.makedirs(TICKETS_FOLDER)

# Fichier pour stocker le dernier numéro de vente
COUNTER_FILE = 'counter.json'

def get_next_sale_number():
    try:
        if os.path.exists(COUNTER_FILE):
            with open(COUNTER_FILE, 'r') as f:
                data = json.load(f)
                counter = data.get('counter', 0)
        else:
            counter = 0
        
        # Incrémenter le compteur
        counter += 1
        
        # Sauvegarder le nouveau compteur
        with open(COUNTER_FILE, 'w') as f:
            json.dump({'counter': counter}, f)
        
        # Formater le numéro avec des zéros devant (ex: 001, 002, etc.)
        return f"{counter:03d}"
    except Exception:
        # En cas d'erreur, retourner un numéro basé sur la date/heure
        return datetime.now().strftime("%Y%m%d%H%M")

@app.route('/')
def index():
    # Obtenir le prochain numéro de vente
    next_number = get_next_sale_number()
    return render_template('index.html', numero_vente=next_number)

@app.route('/ticket/<numero_vente>')
def get_ticket(numero_vente):
    """Route pour accéder au fichier PDF"""
    try:
        filename = f"ticket_{numero_vente}.pdf"
        filepath = os.path.join(TICKETS_FOLDER, filename)
        
        # Vérifier si le fichier existe
        if not os.path.exists(filepath):
            return "Le ticket demandé n'existe pas.", 404
            
        return send_file(
            filepath,
            mimetype='application/pdf'
        )
    except Exception as e:
        return f"Erreur lors de l'accès au ticket: {str(e)}", 404

@app.route('/dernier_ticket')
def dernier_ticket():
    """Route pour obtenir le dernier ticket généré"""
    try:
        # Obtenir la liste des fichiers dans le dossier tickets
        files = os.listdir(TICKETS_FOLDER)
        pdf_files = [f for f in files if f.endswith('.pdf')]
        
        if not pdf_files:
            return "Aucun ticket n'a été généré.", 404
            
        # Trier les fichiers par date de modification (le plus récent en premier)
        latest_file = max(
            pdf_files,
            key=lambda x: os.path.getmtime(os.path.join(TICKETS_FOLDER, x))
        )
        
        return send_file(
            os.path.join(TICKETS_FOLDER, latest_file),
            mimetype='application/pdf'
        )
    except Exception as e:
        return f"Erreur lors de l'accès au dernier ticket: {str(e)}", 404

@app.route('/generer_ticket', methods=['POST'])
def generer_ticket():
    try:
        # Récupération des données du formulaire
        numero_vente = request.form['numero_vente']
        vendeur = request.form['vendeur']
        comptoir = request.form['comptoir']
        
        # Création du ticket
        ticket = TicketCaisse()
        
        # Date et heure actuelles
        maintenant = datetime.now()
        date = maintenant.strftime("%d/%m/%Y")
        heure = maintenant.strftime("%H:%M")
        
        # Ajout de l'en-tête
        ticket.add_header(
            numero_vente=numero_vente,
            date=date,
            heure=heure,
            comptoir=comptoir,
            vendeur=vendeur
        )
        
        # Ajout de l'en-tête des produits
        ticket.add_product_header()
        
        # Récupération des produits du formulaire
        produits = zip(
            request.form.getlist('nom_produit'),
            request.form.getlist('quantite'),
            request.form.getlist('prix_unitaire')
        )
        
        # Ajout des produits
        for nom, quantite, prix in produits:
            if nom and quantite and prix:  # Vérifier que les champs ne sont pas vides
                ticket.add_product(nom, int(quantite), float(prix))
        
        # Ajout du total (sans montant versé)
        ticket.add_total(ticket.total)  # On utilise le total comme montant versé
        
        # Sauvegarde du ticket dans le dossier tickets
        filename = f"ticket_{numero_vente}.pdf"
        filepath = os.path.join(TICKETS_FOLDER, filename)
        ticket.save(filepath)
        
        # Stocker le numéro du dernier ticket généré
        session['dernier_ticket'] = numero_vente
        
        # Créer la réponse pour le téléchargement
        response = make_response(send_file(
            filepath,
            as_attachment=True,
            download_name=filename
        ))
        
        return response
        
    except Exception as e:
        return f"Erreur lors de la génération du ticket: {str(e)}", 400

if __name__ == '__main__':
    app.run(debug=True) 
