from flask import Flask, render_template, request, send_file, send_from_directory
from ticket_generator import TicketCaisse
from datetime import datetime
import os
import json
from pathlib import Path
app = Flask(__name__)


TICKETS_FOLDER = os.path.join(Path(__file__).parent.absolute(), 'tickets')
os.makedirs(TICKETS_FOLDER, exist_ok=True, mode=0o777)
# Dossier pour stocker les tickets PDF
#TICKETS_FOLDER = 'tickets'
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
#def get_ticket(numero_vente):
 #   """Route pour accéder au fichier PDF"""
  #  try:
   #     filename = f"ticket_{numero_vente}.pdf"
    #    return send_from_directory(TICKETS_FOLDER, filename)
    #except Exception as e:
     #   return f"Erreur lors de l'accès au ticket: {str(e)}", 404
def get_ticket(numero_vente):
    filename = f"ticket_{numero_vente}.pdf"
    filepath = os.path.join(TICKETS_FOLDER, filename)
    
    if not os.path.exists(filepath):
        app.logger.error(f"Fichier non trouvé : {filepath}")
        return f"Ticket {numero_vente} introuvable", 404
    
    return send_from_directory(TICKETS_FOLDER, filename)
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
        
        # Envoi du fichier PDF
        return send_file(
            filepath,
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        return f"Erreur lors de la génération du ticket: {str(e)}", 400

if __name__ == '__main__':
    app.run(debug=True) 
