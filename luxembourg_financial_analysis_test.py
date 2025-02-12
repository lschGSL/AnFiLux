import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Simulation d'une extraction de données depuis un fichier Excel
mock_balance_sheet = pd.DataFrame({
    'Nom': ['Total du Bilan', 'Actifs Courants', 'Passifs Courants', 'Capitaux Propres', 'Dettes Totales'],
    'Valeur': [1000000, 300000, 200000, 500000, 400000]
})

mock_income_statement = pd.DataFrame({
    'Nom': ['Chiffre d'affaires', 'Résultat Net', 'Charges Totales'],
    'Valeur': [600000, 50000, 550000]
})

# Simulation de la classe principale
class LuxembourgFinancialAnalysisTest:
    def __init__(self, balance_sheet, income_statement):
        self.balance_sheet = balance_sheet.set_index('Nom')
        self.income_statement = income_statement.set_index('Nom')
        self.analysis_results = {}
    
    def calculate_ratios(self):
        try:
            self.analysis_results['Liquidité générale'] = self.balance_sheet.loc['Actifs Courants', 'Valeur'] / self.balance_sheet.loc['Passifs Courants', 'Valeur']
            self.analysis_results['Autonomie financière'] = self.balance_sheet.loc['Capitaux Propres', 'Valeur'] / self.balance_sheet.loc['Total du Bilan', 'Valeur']
            self.analysis_results['Rentabilité nette'] = self.income_statement.loc['Résultat Net', 'Valeur'] / self.income_statement.loc['Chiffre d'affaires', 'Valeur']
            self.analysis_results['Rentabilité des capitaux propres'] = self.income_statement.loc['Résultat Net', 'Valeur'] / self.balance_sheet.loc['Capitaux Propres', 'Valeur']
            self.analysis_results['Endettement global'] = self.balance_sheet.loc['Dettes Totales', 'Valeur'] / self.balance_sheet.loc['Capitaux Propres', 'Valeur']
        except KeyError as e:
            return f"Donnée manquante : {e}"
        except ZeroDivisionError:
            return "Division par zéro détectée dans les calculs."
        return self.analysis_results

    def visualize_ratios(self):
        """Affiche un graphique des ratios financiers"""
        if not self.analysis_results:
            return "Aucun ratio calculé."
        
        plt.figure(figsize=(8, 5))
        plt.bar(self.analysis_results.keys(), self.analysis_results.values())
        plt.ylabel("Valeurs des ratios")
        plt.xticks(rotation=45)
        plt.title("Visualisation des Ratios Financiers")
        plt.show()

# Exécution du test
if __name__ == "__main__":
    analyzer_test = LuxembourgFinancialAnalysisTest(mock_balance_sheet, mock_income_statement)
    ratios_test = analyzer_test.calculate_ratios()

    # Affichage des résultats
    print(ratios_test)
    analyzer_test.visualize_ratios()
