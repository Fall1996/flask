from fpdf import FPDF
from datetime import datetime

class TicketCaisse:
    def __init__(self):
        # Dimensions en millimètres (largeur=72mm, hauteur=200mm)
        #self.pdf = FPDF(orientation='P', unit='mm', format=(72, 200))
        self.pdf = FPDF(format='A5')
        self.pdf.add_page()
        # Ajout de support pour les caractères spéciaux
        self.pdf.add_font('Arial', '', 'C:\Windows\Fonts\Arial.ttf', uni=True)
        self.pdf.set_font('Arial', '', 8)
        # self.pdf.set_font('helvetica', '', 8)
        self.pdf.set_auto_page_break(auto=True, margin=10)
        self.current_y = 10
        self.produits = []
        self.total = 0

    def add_header(self, numero_vente, date, heure, comptoir, vendeur):
        # En-tête du ticket
        self.pdf.set_xy(5, self.current_y)
        self.pdf.cell(15, 4, 'REMIS', 0, 0, 'L')
        self.pdf.cell(15, 4, '$0.00', 0, 0, 'L')
        self.pdf.cell(15, 4, 'MONNAIE', 0, 0, 'L')
        self.pdf.cell(15, 4, '$0.00', 0, 1, 'L')
        
        self.current_y += 5
        self.pdf.set_xy(5, self.current_y)
        self.pdf.cell(0, 4, f'Numero vente: {numero_vente}', 0, 1, 'L')
        
        self.current_y += 5
        self.pdf.set_xy(5, self.current_y)
        self.pdf.cell(40, 4, f'Date: {date}', 0, 0, 'L')
        self.pdf.cell(30, 4, f'Heure: {heure}', 0, 1, 'L')
        
        self.current_y += 5
        self.pdf.set_xy(5, self.current_y)
        self.pdf.cell(0, 4, comptoir, 0, 1, 'L')
        
        self.current_y += 5
        self.pdf.set_xy(5, self.current_y)
        self.pdf.cell(35, 4, vendeur, 0, 0, 'L')
        self.pdf.cell(35, 4, vendeur, 0, 1, 'R')

    def add_product_header(self):
        self.current_y += 5
        self.pdf.set_xy(5, self.current_y)
        self.pdf.cell(40, 4, 'NomProduit', 1, 0, 'L')
        self.pdf.cell(10, 4, 'Qte', 1, 0, 'C')
        self.pdf.cell(10, 4, 'Prix', 1, 0, 'R')
        self.pdf.cell(15, 4, 'Total', 1, 1, 'R')

    def add_product(self, nom, quantite, prix_unitaire):
        self.current_y += 5
        prix_total = quantite * prix_unitaire
        self.total += prix_total
        self.produits.append({
            'nom': nom,
            'quantite': quantite,
            'prix_unitaire': prix_unitaire,
            'prix_total': prix_total
        })
        self.pdf.set_xy(5, self.current_y)
        self.pdf.cell(40, 4, nom, 0, 0, 'L')
        self.pdf.cell(10, 4, str(quantite), 0, 0, 'C')
        self.pdf.cell(10, 4, str(prix_unitaire), 0, 0, 'R')
        self.pdf.cell(15, 4, str(prix_total), 0, 1, 'R')

    def add_total(self, verse):
        self.current_y += 5
        self.pdf.set_xy(5, self.current_y)
        self.pdf.cell(60, 4, 'TOTAL', 0, 0, 'L')
        self.pdf.cell(15, 4, f'{self.total:.2f}', 0, 1, 'R')
        
        self.current_y += 5
        self.pdf.set_xy(5, self.current_y)
        self.pdf.cell(60, 4, 'VERSE', 0, 0, 'L')
        self.pdf.cell(15, 4, f'{verse:.2f}', 0, 1, 'R')
        
        self.current_y += 5
        self.pdf.set_xy(5, self.current_y)
        self.pdf.cell(60, 4, 'RELIQUAT', 0, 0, 'L')
        self.pdf.cell(15, 4, f'{verse - self.total:.2f}', 0, 1, 'R')

    def save(self, filename):
        try:
            self.pdf.output(filename)
            print("Le ticket a été généré avec succès!")
        except Exception as e:
            print(f"Erreur lors de la sauvegarde du fichier: {str(e)}")
            raise

def saisir_produit():
    nom = input("Nom du produit (ou 'fin' pour terminer): ")
    if nom.lower() == 'fin':
        return None
    
    while True:
        try:
            quantite = int(input("Quantité: "))
            if quantite > 0:
                break
            print("La quantité doit être positive.")
        except ValueError:
            print("Veuillez entrer un nombre entier valide.")
    
    while True:
        try:
            prix = float(input("Prix unitaire: "))
            if prix > 0:
                break
            print("Le prix doit être positif.")
        except ValueError:
            print("Veuillez entrer un nombre valide.")
    
    return nom, quantite, prix

def generer_ticket():
    # Création du ticket
    ticket = TicketCaisse()
    
    # Informations d'en-tête
    numero_vente = input("Numéro de vente: ")
    vendeur = input("Nom du vendeur: ")
    comptoir = input("Nom du comptoir: ")
    
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
    
    # Saisie des produits
    print("\nSaisie des produits (tapez 'fin' comme nom de produit pour terminer)")
    while True:
        produit = saisir_produit()
        if produit is None:
            break
        nom, quantite, prix = produit
        ticket.add_product(nom, quantite, prix)
    
    # Saisie du montant versé
    while True:
        try:
            verse = float(input("\nMontant versé: "))
            if verse >= ticket.total:
                break
            print(f"Le montant versé doit être supérieur ou égal au total ({ticket.total:.2f})")
        except ValueError:
            print("Veuillez entrer un nombre valide.")
    
    # Ajout du total et sauvegarde
    ticket.add_total(verse)
    ticket.save("ticket.pdf")

if __name__ == "__main__":
    try:
        print("=== GÉNÉRATION DE TICKET DE CAISSE ===")
        generer_ticket()
    except KeyboardInterrupt:
        print("\nOpération annulée.")
    except Exception as e:
        print(f"Une erreur est survenue: {str(e)}") 
