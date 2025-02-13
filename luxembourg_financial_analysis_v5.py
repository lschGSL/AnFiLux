import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io
import os

# Gestion de l'import de reportlab pour la génération du PDF
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    REPORTLAB_AVAILABLE = True
except ModuleNotFoundError:
    st.error("Module 'reportlab' non trouvé. La génération du PDF ne sera pas disponible. "
             "Veuillez ajouter 'reportlab' dans vos dépendances (ex. via requirements.txt) pour activer cette fonctionnalité.")
    REPORTLAB_AVAILABLE = False

# --- Fonctions utilitaires ---

def interpret_ratio(ratio_name, ratio_value):
    """
    Retourne une interprétation basique du ratio selon sa valeur.
    """
    if ratio_name == "Liquidité générale":
        if ratio_value < 1:
            return "Insuffisante"
        elif ratio_value < 2:
            return "Correcte"
        else:
            return "Excellente"
    elif ratio_name == "Autonomie financière":
        if ratio_value < 0.5:
            return "Faible"
        else:
            return "Satisfaisante"
    elif ratio_name == "Rentabilité nette":
        if ratio_value < 0.05:
            return "Faible"
        elif ratio_value < 0.15:
            return "Moyenne"
        else:
            return "Excellente"
    elif ratio_name == "Rentabilité des capitaux propres":
        if ratio_value < 0.1:
            return "Faible"
        elif ratio_value < 0.2:
            return "Moyenne"
        else:
            return "Excellente"
    elif ratio_name == "Endettement global":
        if ratio_value > 1:
            return "Trop endetté"
        else:
            return "Sain"
    return ""

def generate_pdf(analysis_text, ratios_dict):
    """
    Génère un PDF contenant le texte d'analyse et un tableau des ratios financiers.
    Si reportlab n'est pas disponible, retourne None.
    """
    if not REPORTLAB_AVAILABLE:
        return None

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Titre du rapport
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "Analyse Financière")

    # Zone d'analyse textuelle
    c.setFont("Helvetica", 12)
    text_object = c.beginText(50, height - 80)
    for line in analysis_text.split("\n"):
        text_object.textLine(line)
    c.drawText(text_object)

    # Tableau des ratios
    y_position = height - 200
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y_position, "Ratio")
    c.drawString(250, y_position, "Valeur")
    c.drawString(400, y_position, "Interprétation")
    y_position -= 20

    c.setFont("Helvetica", 12)
    for key, value in ratios_dict.items():
        interpr = interpret_ratio(key, value)
        c.drawString(50, y_position, key)
        c.drawString(250, y_position, f"{value:.2f}")
        c.drawString(400, y_position, interpr)
        y_position -= 20
        if y_position < 50:
            c.showPage()
            y_position = height - 50
    c.save()
    buffer.seek(0)
    return buffer

# --- Classe d'analyse financière ---

class FinancialAnalysis:
    def __init__(self, bilan, compte):
        """
        Exige des DataFrames contenant au moins les colonnes 'Nom' et 'Valeur'.
        On suppose que le bilan et le compte possèdent des lignes identifiées par :
          - Bilan : 'Total du Bilan', 'Actifs Courants', 'Passifs Courants',
                    'Capitaux Propres', 'Dettes Totales'
          - Compte : 'Chiffre d\'affaires', 'Résultat Net'
        """
        self.bilan = bilan.set_index('Nom')
        self.compte = compte.set_index('Nom')
        self.ratios = {}

    def calculate_ratios(self):
        try:
            # Ratio de liquidité : Actifs Courants / Passifs Courants
            self.ratios['Liquidité générale'] = self.bilan.loc['Actifs Courants', 'Valeur'] / self.bilan.loc['Passifs Courants', 'Valeur']
            # Ratio de solvabilité : Capitaux Propres / Total du Bilan
            self.ratios['Autonomie financière'] = self.bilan.loc['Capitaux Propres', 'Valeur'] / self.bilan.loc['Total du Bilan', 'Valeur']
            # Rentabilité nette : Résultat Net / Chiffre d'affaires
            self.ratios['Rentabilité nette'] = self.compte.loc['Résultat Net', 'Valeur'] / self.compte.loc["Chiffre d'affaires", 'Valeur']
            # Rentabilité des capitaux propres (ROE) : Résultat Net / Capitaux Propres
            self.ratios['Rentabilité des capitaux propres'] = self.compte.loc['Résultat Net', 'Valeur'] / self.bilan.loc['Capitaux Propres', 'Valeur']
            # Endettement global : Dettes Totales / Capitaux Propres
            self.ratios['Endettement global'] = self.bilan.loc['Dettes Totales', 'Valeur'] / self.bilan.loc['Capitaux Propres', 'Valeur']
        except KeyError as e:
            st.error(f"Clé manquante dans les données : {e}")
            return None
        except ZeroDivisionError:
            st.error("Erreur de division par zéro dans les calculs.")
            return None
        return self.ratios

    def analyze_ratios(self):
        analysis_text = ""
        for key, value in self.ratios.items():
            interpretation = interpret_ratio(key, value)
            analysis_text += f"{key} : {value:.2f} => {interpretation}\n"
        return analysis_text

# --- Interface utilisateur Streamlit ---

st.title("Analyse Financière des Comptes Annuels")

# Demande de fournir un fichier PDF ou Excel
uploaded_file = st.file_uploader(
    "Veuillez fournir un fichier PDF ou Excel contenant le bilan et le compte de profits et pertes (1 ou 2 exercices)",
    type=["xlsx", "xls", "pdf"]
)

if uploaded_file is not None:
    file_extension = os.path.splitext(uploaded_file.name)[1].lower()
    try:
        if file_extension in [".xlsx", ".xls"]:
            # On suppose que le fichier Excel comporte deux feuilles nommées "Bilan" et "Compte"
            bilan = pd.read_excel(uploaded_file, sheet_name="Bilan")
            compte = pd.read_excel(uploaded_file, sheet_name="Compte")
        elif file_extension == ".pdf":
            # Extraction des tableaux depuis le PDF à l'aide de tabula-py
            try:
                import tabula
                tables = tabula.read_pdf(uploaded_file, pages="all", multiple_tables=True)
                if len(tables) < 2:
                    st.error("Le PDF ne contient pas suffisamment de tableaux pour extraire le bilan et le compte.")
                    st.stop()
                bilan = tables[0]
                compte = tables[1]
            except Exception as e:
                st.error(f"Erreur lors de la lecture du PDF : {e}")
                st.stop()
        else:
            st.error("Format de fichier non supporté.")
            st.stop()

        # Vérification des colonnes attendues
        required_cols = ['Nom', 'Valeur']
        if not all(col in bilan.columns for col in required_cols):
            st.error("La feuille 'Bilan' doit contenir les colonnes 'Nom' et 'Valeur'.")
            st.stop()
        if not all(col in compte.columns for col in required_cols):
            st.error("La feuille 'Compte' doit contenir les colonnes 'Nom' et 'Valeur'.")
            st.stop()

        # Calcul des ratios
        analyzer = FinancialAnalysis(bilan, compte)
        ratios = analyzer.calculate_ratios()
        if ratios is None:
            st.stop()

        st.subheader("Ratios Financiers Calculés")
        st.write(ratios)

        # Analyse et interprétation
        analysis_text = analyzer.analyze_ratios()
        st.subheader("Analyse et Interprétations")
        st.text(analysis_text)

        # Visualisation graphique des ratios
        st.subheader("Visualisation des Ratios")
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.bar(list(ratios.keys()), list(ratios.values()), color="skyblue")
        ax.set_ylabel("Valeurs")
        ax.set_title("Ratios Financiers")
        plt.xticks(rotation=45)
        st.pyplot(fig)

        # Génération du rapport PDF si reportlab est disponible
        if REPORTLAB_AVAILABLE:
            pdf_buffer = generate_pdf(analysis_text, ratios)
            if pdf_buffer:
                st.download_button(
                    label="Télécharger l'analyse en PDF",
                    data=pdf_buffer,
                    file_name="analyse_financiere.pdf",
                    mime="application/pdf"
                )
        else:
            st.info("La génération du PDF est désactivée car le module 'reportlab' n'est pas installé.")

    except Exception as e:
        st.error(f"Une erreur s'est produite : {e}")
