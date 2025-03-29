#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module d'interprétation des métriques pour MT5 Trading Analyzer
"""

import logging
import pandas as pd
import numpy as np

class MetricsInterpreter:
    """Classe pour l'interprétation et les conseils sur les métriques de trading"""
    
    def __init__(self):
        """Initialisation de l'interpréteur de métriques"""
        self.logger = logging.getLogger(__name__)
        
        # Définir les seuils pour différentes métriques
        self.sharpe_thresholds = {
            "médiocre": 0.5,
            "acceptable": 1.0,
            "bon": 2.0,
            "excellent": 3.0
        }
        
        self.sortino_thresholds = {
            "médiocre": 0.5,
            "acceptable": 1.0,
            "bon": 2.0,
            "excellent": 3.0
        }
        
        self.calmar_thresholds = {
            "médiocre": 0.5,
            "acceptable": 1.0,
            "bon": 3.0,
            "excellent": 5.0
        }
        
        # Seuils de D-Leverage par style de trading
        self.d_leverage_thresholds = {
            "scalping": {
                "sous-optimal": 10.0,
                "optimal_max": 16.25
            },
            "intraday": {
                "sous-optimal": 8.0,
                "optimal_max": 13.0
            },
            "swing": {
                "sous-optimal": 5.0,
                "optimal_max": 9.75
            }
        }
    
    def interpret_sharpe_ratio(self, sharpe, history=None):
        """
        Interprète le ratio de Sharpe et fournit des recommandations
        
        Args:
            sharpe (float): Valeur du ratio de Sharpe
            history (list, optional): Historique des valeurs du ratio pour analyse de tendance
            
        Returns:
            dict: Interprétation et recommandations
        """
        try:
            # Interprétation de base
            if sharpe < self.sharpe_thresholds["médiocre"]:
                rating = "Médiocre"
                interpretation = "Le rendement ne compense pas suffisamment le risque pris."
                level_color = "red"
            elif sharpe < self.sharpe_thresholds["acceptable"]:
                rating = "Acceptable"
                interpretation = "Performance sous-optimale. Le risque est partiellement compensé."
                level_color = "orange"
            elif sharpe < self.sharpe_thresholds["bon"]:
                rating = "Bon"
                interpretation = "Votre stratégie génère un rendement qui compense adéquatement le risque."
                level_color = "lightgreen"
            elif sharpe < self.sharpe_thresholds["excellent"]:
                rating = "Très bon"
                interpretation = "Votre stratégie surperforme la plupart des professionnels."
                level_color = "green"
            else:
                rating = "Exceptionnel"
                interpretation = "Performance remarquable, mais surveillez sa soutenabilité à long terme."
                level_color = "darkgreen"
            
            # Analyse de tendance si l'historique est fourni
            trend_analysis = None
            if history and len(history) > 2:
                # Convertir en array numpy pour faciliter les calculs
                history_array = np.array(history)
                
                # Calculer la tendance récente (derniers 20% des données ou minimum 3 points)
                recent_n = max(3, int(len(history) * 0.2))
                recent_trend = history_array[-recent_n:]
                
                # Calculer la pente de la tendance récente
                slope = np.polyfit(range(len(recent_trend)), recent_trend, 1)[0]
                
                # Analyser la stabilité (écart-type normalisé)
                stability = np.std(history_array) / np.mean(history_array) if np.mean(history_array) != 0 else np.inf
                
                if slope > 0.05:  # Tendance positive significative
                    trend_analysis = "Votre ratio de Sharpe s'améliore de façon significative récemment, ce qui indique une optimisation réussie de votre stratégie."
                elif slope < -0.05:  # Tendance négative significative
                    trend_analysis = "Votre ratio de Sharpe se dégrade récemment. Vérifiez si les conditions de marché ont changé ou si votre exécution est moins disciplinée."
                
                if stability > 0.5:  # Haute volatilité du ratio
                    trend_analysis = (trend_analysis or "") + " La forte variabilité de votre ratio de Sharpe suggère une inconsistance dans votre approche ou une forte dépendance aux conditions de marché."
            
            # Recommandations spécifiques
            if sharpe < 1.0:
                recommendations = [
                    "Réduisez votre exposition aux instruments qui contribuent négativement au ratio.",
                    "Réévaluez votre stratégie d'entrée/sortie pour améliorer le rapport rendement/risque.",
                    "Considérez l'utilisation de stops plus serrés pour limiter les pertes importantes."
                ]
            elif sharpe < 2.0:
                recommendations = [
                    "Votre stratégie fonctionne bien, mais vous pouvez l'optimiser davantage.",
                    "Analysez quelles positions contribuent le plus positivement au ratio et augmentez leur allocation.",
                    "Maintenez votre discipline de trading tout en explorant des améliorations marginales."
                ]
            else:
                recommendations = [
                    "Maintenez votre approche actuelle qui fonctionne très bien.",
                    "Documentez soigneusement votre processus pour assurer sa reproductibilité.",
                    "Vérifiez que ce ratio élevé est statistiquement significatif et pas simplement dû à un petit échantillon ou à des conditions de marché particulièrement favorables."
                ]
            
            # Assembler la réponse
            response = {
                "metric": "Ratio de Sharpe",
                "value": sharpe,
                "rating": rating,
                "interpretation": interpretation,
                "trend_analysis": trend_analysis,
                "recommendations": recommendations,
                "color": level_color
            }
            
            return response
            
        except Exception as e:
            self.logger.exception("Erreur lors de l'interprétation du ratio de Sharpe")
            return {"error": str(e)}
    
    def interpret_sortino_ratio(self, sortino, sharpe=None, history=None):
        """
        Interprète le ratio de Sortino et fournit des recommandations
        
        Args:
            sortino (float): Valeur du ratio de Sortino
            sharpe (float, optional): Valeur du ratio de Sharpe pour comparaison
            history (list, optional): Historique des valeurs du ratio pour analyse de tendance
            
        Returns:
            dict: Interprétation et recommandations
        """
        try:
            # Interprétation de base
            if sortino < self.sortino_thresholds["médiocre"]:
                rating = "Médiocre"
                interpretation = "Gestion insuffisante du risque baissier. Votre stratégie est vulnérable aux mouvements défavorables."
                level_color = "red"
            elif sortino < self.sortino_thresholds["acceptable"]:
                rating = "Acceptable"
                interpretation = "Protection modérée contre le risque baissier. Des améliorations sont possibles."
                level_color = "orange"
            elif sortino < self.sortino_thresholds["bon"]:
                rating = "Bon"
                interpretation = "Bonne protection contre le risque baissier. Votre stratégie limite efficacement les pertes."
                level_color = "lightgreen"
            elif sortino < self.sortino_thresholds["excellent"]:
                rating = "Très bon"
                interpretation = "Excellente gestion du risque baissier. Votre stratégie génère des rendements tout en minimisant les pertes significatives."
                level_color = "green"
            else:
                rating = "Exceptionnel"
                interpretation = "Protection exceptionnelle contre le risque baissier."
                level_color = "darkgreen"
            
            # Analyse comparative avec Sharpe si disponible
            comparative_analysis = None
            if sharpe is not None:
                ratio_difference = sortino - sharpe
                if ratio_difference > 1.0:
                    comparative_analysis = "Votre ratio de Sortino est significativement supérieur à votre ratio de Sharpe, ce qui indique que votre stratégie gère particulièrement bien le risque baissier. Vous êtes efficace à éviter les mouvements défavorables tout en capturant les mouvements favorables."
                elif ratio_difference > 0.2:
                    comparative_analysis = "Votre ratio de Sortino est supérieur à votre ratio de Sharpe, ce qui indique que votre stratégie gère mieux le risque baissier que la volatilité globale. Cela suggère une approche asymétrique efficace."
                elif ratio_difference > -0.2:
                    comparative_analysis = "Votre ratio de Sortino est presque identique à votre ratio de Sharpe, ce qui indique que votre volatilité est relativement symétrique entre mouvements haussiers et baissiers."
                else:
                    comparative_analysis = "Votre ratio de Sortino est inférieur à votre ratio de Sharpe, ce qui est inhabituel et suggère que votre volatilité baissière est plus problématique que votre volatilité haussière. Examinez vos mécanismes de gestion des pertes."
            
            # Recommandations spécifiques
            if sortino < 1.0:
                recommendations = [
                    "Améliorez vos mécanismes de gestion des pertes, comme les stop-loss ou les trailing stops.",
                    "Considérez l'utilisation de techniques de couverture durant les périodes de haute volatilité.",
                    "Revoyez votre stratégie d'entrée pour éviter les positions à haut risque baissier."
                ]
            elif sortino < 2.0:
                recommendations = [
                    "Votre gestion du risque baissier est efficace, mais peut être affinée.",
                    "Analysez les transactions qui ont généré les plus grandes pertes pour identifier des patterns à éviter.",
                    "Envisagez d'implémenter une stratégie adaptative qui réduit l'exposition pendant les périodes de forte volatilité baissière."
                ]
            else:
                recommendations = [
                    "Maintenez votre excellente approche de gestion du risque baissier.",
                    "Vérifiez que vous ne sacrifiez pas trop d'opportunités haussières au nom de la protection contre le risque.",
                    "Documentez votre processus de gestion du risque baissier pour assurer sa cohérence future."
                ]
            
            # Assembler la réponse
            response = {
                "metric": "Ratio de Sortino",
                "value": sortino,
                "rating": rating,
                "interpretation": interpretation,
                "comparative_analysis": comparative_analysis,
                "recommendations": recommendations,
                "color": level_color
            }
            
            return response
            
        except Exception as e:
            self.logger.exception("Erreur lors de l'interprétation du ratio de Sortino")
            return {"error": str(e)}
    
    def interpret_calmar_ratio(self, calmar, max_drawdown=None, max_drawdown_date=None, history=None):
        """
        Interprète le ratio de Calmar et fournit des recommandations
        
        Args:
            calmar (float): Valeur du ratio de Calmar
            max_drawdown (float, optional): Valeur du drawdown maximum en pourcentage
            max_drawdown_date (datetime, optional): Date du drawdown maximum
            history (list, optional): Historique des valeurs du ratio pour analyse de tendance
            
        Returns:
            dict: Interprétation et recommandations
        """
        try:
            # Interprétation de base
            if calmar < self.calmar_thresholds["médiocre"]:
                rating = "Médiocre"
                interpretation = "Récupération lente des drawdowns. Le rendement ne compense pas suffisamment les baisses maximales."
                level_color = "red"
            elif calmar < self.calmar_thresholds["acceptable"]:
                rating = "Acceptable"
                interpretation = "Équilibre acceptable entre rendement et drawdown maximum."
                level_color = "orange"
            elif calmar < self.calmar_thresholds["bon"]:
                rating = "Bon"
                interpretation = "Bon équilibre entre rendement et drawdown. Votre stratégie récupère efficacement des baisses."
                level_color = "lightgreen"
            elif calmar < self.calmar_thresholds["excellent"]:
                rating = "Très bon"
                interpretation = "Excellente performance par rapport au risque de drawdown. Votre stratégie génère de forts rendements tout en limitant les baisses significatives."
                level_color = "green"
            else:
                rating = "Exceptionnel"
                interpretation = "Performance exceptionnelle avec une résistance remarquable aux drawdowns."
                level_color = "darkgreen"
            
            # Analyse contextuelle
            contextual_analysis = None
            
            # Si nous avons l'information sur le drawdown maximum et sa date
            if max_drawdown is not None and max_drawdown_date is not None:
                now = pd.Timestamp.now()
                days_since_max_dd = (now - max_drawdown_date).days
                
                if days_since_max_dd < 30:  # Drawdown récent (moins d'un mois)
                    contextual_analysis = f"Votre drawdown maximum de {abs(max_drawdown):.2f}% est récent (il y a {days_since_max_dd} jours). Cela suggère que vous êtes encore en phase de récupération."
                elif days_since_max_dd < 90:  # 1-3 mois
                    contextual_analysis = f"Votre drawdown maximum s'est produit il y a {days_since_max_dd} jours. Vous avez commencé à vous en remettre, mais restez vigilant."
                else:  # Plus de 3 mois
                    contextual_analysis = f"Votre drawdown maximum de {abs(max_drawdown):.2f}% s'est produit il y a {days_since_max_dd} jours. Vous avez bien récupéré depuis cette période difficile."
            
            # Analyser la taille de l'échantillon si l'historique est fourni
            if history and len(history) < 30:  # Petit échantillon (moins de 30 points)
                sample_warning = "Note: Un ratio de Calmar basé sur un petit échantillon devrait être interprété avec prudence. Le vrai test viendra lors de conditions de marché difficiles."
                contextual_analysis = (contextual_analysis + " " + sample_warning) if contextual_analysis else sample_warning
            
            # Recommandations spécifiques
            if calmar < 1.0:
                recommendations = [
                    "Améliorez vos mécanismes de limitation des drawdowns, comme les stop-loss à l'échelle du portefeuille.",
                    "Diversifiez davantage pour réduire la profondeur des drawdowns.",
                    "Envisagez de réduire temporairement l'exposition pendant les périodes de tendance baissière claire."
                ]
            elif calmar < 3.0:
                recommendations = [
                    "Votre gestion des drawdowns est efficace, mais peut être optimisée.",
                    "Analysez les conditions qui ont précédé votre drawdown maximum pour identifier des signaux d'alerte précoces.",
                    "Envisagez d'implémenter une allocation dynamique qui s'ajuste en fonction des conditions de marché."
                ]
            else:
                recommendations = [
                    "Votre stratégie gère exceptionnellement bien les drawdowns.",
                    "Documentez votre processus actuel de gestion des drawdowns pour maintenir cette performance.",
                    "Considérez des tests de stress pour confirmer la robustesse de votre approche face à des scénarios extrêmes."
                ]
            
            # Assembler la réponse
            response = {
                "metric": "Ratio de Calmar",
                "value": calmar,
                "rating": rating,
                "interpretation": interpretation,
                "contextual_analysis": contextual_analysis,
                "recommendations": recommendations,
                "color": level_color
            }
            
            if max_drawdown is not None:
                response["max_drawdown"] = max_drawdown
            
            return response
            
        except Exception as e:
            self.logger.exception("Erreur lors de l'interprétation du ratio de Calmar")
            return {"error": str(e)}
    
    def interpret_d_leverage(self, d_leverage, avg_position_duration=None, historical_values=None):
        """
        Interprète le D-Leverage et fournit des recommandations
        
        Args:
            d_leverage (float): Valeur actuelle du D-Leverage
            avg_position_duration (float, optional): Durée moyenne des positions en minutes
            historical_values (list, optional): Historique des valeurs du D-Leverage
            
        Returns:
            dict: Interprétation et recommandations
        """
        try:
            # Déterminer le style de trading basé sur la durée moyenne des positions
            if avg_position_duration is not None:
                if avg_position_duration < 30:
                    style = "scalping"
                    style_name = "Scalping"
                elif avg_position_duration < 60:
                    style = "intraday"
                    style_name = "Intraday"
                else:
                    style = "swing"
                    style_name = "Swing/Position"
            else:
                # Par défaut, utiliser le style le plus conservateur
                style = "swing"
                style_name = "Indéterminé (par défaut: Swing/Position)"
            
            # Obtenir les seuils pour ce style
            sous_optimal = self.d_leverage_thresholds[style]["sous-optimal"]
            optimal_max = self.d_leverage_thresholds[style]["optimal_max"]
            
            # Déterminer le rating et l'interprétation
            if d_leverage < sous_optimal:
                rating = "Sous-optimal"
                interpretation = f"Sous-utilisation du capital pour le style {style_name}. Vous pourriez augmenter prudemment votre exposition."
                level_color = "blue"
            elif d_leverage <= optimal_max:
                rating = "Optimal"
                interpretation = f"Zone optimale pour le style {style_name}. Bon équilibre entre risque et utilisation du capital."
                level_color = "green"
            else:
                excess_pct = ((d_leverage / optimal_max) - 1) * 100
                rating = "Excessif"
                interpretation = f"Risque excessif pour le style {style_name}. Votre D-Leverage dépasse de {excess_pct:.1f}% le maximum recommandé."
                level_color = "red"
            
            # Analyse de tendance si l'historique est fourni
            trend_analysis = None
            if historical_values and len(historical_values) > 2:
                # Convertir en array numpy pour faciliter les calculs
                history_array = np.array(historical_values)
                
                # Calculer la tendance récente (derniers 20% des données ou minimum 3 points)
                recent_n = max(3, int(len(history_array) * 0.2))
                recent_trend = history_array[-recent_n:]
                
                # Calculer la pente de la tendance récente
                slope = np.polyfit(range(len(recent_trend)), recent_trend, 1)[0]
                
                # Analyser la stabilité (écart-type normalisé)
                stability = np.std(history_array) / np.mean(history_array) if np.mean(history_array) != 0 else np.inf
                
                # Valeurs minimales et maximales récentes
                min_recent = np.min(recent_trend)
                max_recent = np.max(recent_trend)
                
                if slope > 0.1:  # Tendance à la hausse significative
                    trend_analysis = f"Votre D-Leverage augmente progressivement (de {min_recent:.2f} à {max_recent:.2f} récemment). Cette tendance indique une prise de risque croissante qui devrait être surveillée attentivement."
                elif slope < -0.1:  # Tendance à la baisse significative
                    trend_analysis = f"Votre D-Leverage diminue progressivement (de {max_recent:.2f} à {min_recent:.2f} récemment). Cette réduction du risque pourrait être bénéfique si vous étiez précédemment en zone excessive."
                
                if stability > 0.3:  # Haute volatilité du D-Leverage
                    fluctuation_text = f"Votre D-Leverage fluctue considérablement (entre {min(history_array):.2f} et {max(history_array):.2f}), ce qui suggère une inconsistance dans votre gestion du risque et du sizing des positions."
                    trend_analysis = (trend_analysis + " " + fluctuation_text) if trend_analysis else fluctuation_text
            
            # Recommandations spécifiques
            if rating == "Sous-optimal":
                if style == "scalping":
                    target = (sous_optimal + optimal_max) / 2  # Milieu de la plage optimale
                    increase_pct = ((target / d_leverage) - 1) * 100
                    recommendations = [
                        f"Augmentez progressivement votre exposition de {increase_pct:.1f}% pour atteindre un D-Leverage plus efficace d'environ {target:.2f}.",
                        "Identifiez les opportunités de scalping à faible risque pour augmenter votre exposition.",
                        "Considérez l'augmentation du nombre de positions plutôt que leur taille pour une meilleure diversification."
                    ]
                elif style == "intraday":
                    target = (sous_optimal + optimal_max) / 2
                    increase_pct = ((target / d_leverage) - 1) * 100
                    recommendations = [
                        f"Augmentez votre exposition d'environ {increase_pct:.1f}% pour optimiser l'utilisation de votre capital.",
                        "Recherchez des configurations intraday avec un bon rapport risque/rendement pour augmenter le nombre de positions.",
                        "Envisagez d'élargir votre univers d'instruments pour diversifier l'augmentation d'exposition."
                    ]
                else:  # swing
                    target = (sous_optimal + optimal_max) / 2
                    increase_pct = ((target / d_leverage) - 1) * 100
                    recommendations = [
                        f"Augmentez progressivement votre exposition de {increase_pct:.1f}% pour optimiser le rendement de votre capital.",
                        "Recherchez des opportunités de swing trading avec des configurations techniques solides.",
                        "Diversifiez votre portefeuille en ajoutant des positions non corrélées pour réduire le risque global."
                    ]
            elif rating == "Optimal":
                recommendations = [
                    f"Maintenez votre D-Leverage actuel qui est optimal pour le style {style_name}.",
                    "Surveillez régulièrement ce ratio lors des fluctuations significatives du marché.",
                    "Assurez-vous que votre gestion des stops et du risque est en accord avec ce niveau d'exposition."
                ]
            else:  # Excessif
                reduction_needed = 1 - (optimal_max / d_leverage)
                reduction_pct = reduction_needed * 100
                recommendations = [
                    f"Réduisez votre exposition globale d'environ {reduction_pct:.1f}% pour revenir à un niveau de risque approprié.",
                    "Identifiez et réduisez en priorité les positions présentant le moins bon rapport rendement/risque.",
                    "Implémentez un plan de réduction progressive pour éviter de liquider des positions dans des conditions défavorables."
                ]
            
            # Assembler la réponse
            response = {
                "metric": "D-Leverage",
                "value": d_leverage,
                "style": style_name,
                "optimal_range": f"{sous_optimal:.2f} - {optimal_max:.2f}",
                "rating": rating,
                "interpretation": interpretation,
                "trend_analysis": trend_analysis,
                "recommendations": recommendations,
                "color": level_color
            }
            
            return response
            
        except Exception as e:
            self.logger.exception("Erreur lors de l'interprétation du D-Leverage")
            return {"error": str(e)}