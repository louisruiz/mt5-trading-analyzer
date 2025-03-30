# MT5 Trading Analyzer Pro

MT5 Trading Analyzer Pro est une application de bureau avancée conçue pour surveiller, analyser et optimiser vos activités de trading sur MetaTrader 5. Elle offre une vision complète de votre portefeuille à travers des métriques de performance sophistiquées, des outils d'analyse de risque et des fonctionnalités d'aide à la décision.

## Table des matières

- [Aperçu](#aperçu)
- [Fonctionnalités principales](#fonctionnalités-principales)
- [Architecture du projet](#architecture-du-projet)
- [Prérequis](#prérequis)
- [Installation](#installation)
- [Utilisation](#utilisation)
- [Interface utilisateur](#interface-utilisateur)
- [Fonctionnalités détaillées](#fonctionnalités-détaillées)
  - [Suivi de l'équité et des performances](#suivi-de-léquité-et-des-performances)
  - [Analyse des positions](#analyse-des-positions)
  - [Analyse d'allocation de portefeuille](#analyse-dallocation-de-portefeuille)
  - [Benchmarking](#benchmarking)
  - [D-Leverage Optimizer](#d-leverage-optimizer)
  - [Tableau de bord de risque](#tableau-de-bord-de-risque)
  - [Système d'alertes](#système-dalertes)
  - [Analyse VaR](#analyse-var)
- [Concepts clés](#concepts-clés)
  - [D-Leverage](#d-leverage)
  - [Value at Risk (VaR)](#value-at-risk-var)
  - [Métriques de performance](#métriques-de-performance)
- [Configuration](#configuration)
- [Développement](#développement)
  - [Structure détaillée du code](#structure-détaillée-du-code)
  - [Ajout de fonctionnalités](#ajout-de-fonctionnalités)
- [Roadmap](#roadmap)
- [Contribution](#contribution)
- [Licence](#licence)

## Aperçu

MT5 Trading Analyzer Pro a été conçu pour combler le fossé entre les plateformes de trading et l'analyse quantitative avancée. L'application se connecte à votre compte MetaTrader 5, extrait vos données de trading, et applique des algorithmes d'analyse sophistiqués pour vous fournir des insights en temps réel sur votre performance, votre risque et vos stratégies.

## Fonctionnalités principales

- **Dashboard complet**: Vue d'ensemble interactive avec toutes les métriques clés
- **Analyse de performance avancée**: Calcul des ratios Sharpe, Sortino, Calmar et métriques de performance
- **Visualisation des drawdowns**: Analyse détaillée des périodes de pertes et récupérations
- **Gestion des positions**: Suivi détaillé et filtrage des positions ouvertes
- **Analyse d'allocation**: Répartition du capital par instrument, direction et durée
- **Benchmarking**: Comparaison automatique avec les indices majeurs du marché
- **D-Leverage Optimizer**: Optimisation du ratio exposition/capital selon votre style de trading
- **Analyse de VaR multi-méthodes**: Calcul et suivi de la Value at Risk par approches paramétriques, historiques et Monte Carlo
- **Score de risque global**: Évaluation composite du risque du portefeuille
- **Système d'alertes intelligent**: Surveillance continue des seuils de risque avec suggestions d'optimisation

## Architecture du projet

L'application est structurée de manière modulaire pour faciliter la maintenance et l'extension:

```
mt5_trading_analyzer/
│
├── main.py                  # Point d'entrée principal
│
├── core/                    # Modules de base
│   ├── __init__.py          # Initialisation du package core
│   ├── mt5_connector.py     # Connexion et requêtes MetaTrader 5
│   ├── data_manager.py      # Gestion centralisée des données
│   └── config_manager.py    # Gestion de la configuration
│
├── analysis/                # Modules d'analyse
│   ├── __init__.py          # Initialisation du package analysis
│   ├── performance_metrics.py # Métriques de performance et retour
│   ├── risk_metrics.py      # Calcul des métriques de risque
│   ├── drawdown_analyzer.py # Analyse avancée des drawdowns
│   ├── metrics_interpreter.py # Interprétation des métriques
│   ├── allocation_analysis.py # Analyse de l'allocation du capital
│   ├── alerts_engine.py     # Moteur de détection d'alertes
│   └── risk_score_calculator.py # Calcul du score de risque global
│
├── ui/                      # Interface utilisateur
│   ├── __init__.py          # Initialisation du package ui
│   ├── main_window.py       # Fenêtre principale de l'application
│   ├── widgets/             # Widgets d'interface
│   │   ├── __init__.py      # Initialisation du package widgets
│   │   ├── account_info_widget.py      # Informations du compte
│   │   ├── positions_widget.py         # Liste des positions
│   │   ├── equity_chart_widget.py      # Graphique d'équité
│   │   ├── performance_widget.py       # Métriques de performance
│   │   ├── allocation_widget.py        # Analyse d'allocation
│   │   ├── benchmark_widget.py         # Benchmarking
│   │   ├── d_leverage_chart_widget.py  # Visualisation D-Leverage
│   │   ├── alerts_widget.py            # Alertes et optimisations
│   │   ├── risk_score_widget.py        # Score de risque global
│   │   ├── status_bar_widget.py        # Barre de statut
│   │   └── tooltip_widget.py           # Tooltips avancés
│   │
│   └── dialogs/             # Boîtes de dialogue
│       ├── __init__.py      # Initialisation du package dialogs
│       ├── settings_dialog.py          # Paramètres
│       ├── d_leverage_dialog.py        # Optimisation D-Leverage
│       ├── var_dialog.py               # Analyse VaR
│       └── about_dialog.py             # À propos
│
└── utils/                   # Utilitaires
    ├── __init__.py          # Initialisation du package utils
    ├── constants.py         # Constantes et configurations
    └── helpers.py           # Fonctions utilitaires
```

## Prérequis

- Python 3.7 ou supérieur
- MetaTrader 5 installé et configuré
- Bibliothèques Python requises:
  - MetaTrader5 (5.0.34 ou supérieur)
  - pandas (1.3.0 ou supérieur)
  - numpy (1.20.0 ou supérieur)
  - matplotlib (3.4.0 ou supérieur)
  - scipy (1.7.0 ou supérieur)
  - yfinance (pour les données de benchmarking)
  - tkinter (inclus dans la plupart des installations Python)
  - pytz (pour la gestion des fuseaux horaires)

## Installation

1. Clonez ce dépôt:
   ```
   git clone https://github.com/votre-username/mt5-trading-analyzer.git
   cd mt5-trading-analyzer
   ```

2. Créez un environnement virtuel (optionnel mais recommandé):
   ```
   python -m venv venv
   source venv/bin/activate  # Sur Windows: venv\Scripts\activate
   ```

3. Installez les dépendances:
   ```
   pip install -r requirements.txt
   ```

4. Assurez-vous que MetaTrader 5 est installé, configuré et en cours d'exécution.

## Utilisation

Lancez l'application avec:
```
python main.py
```

L'application tentera de se connecter automatiquement à votre terminal MT5 s'il est en cours d'exécution. Les données sont rafraîchies automatiquement selon l'intervalle configuré dans les paramètres.

### Connexion à MetaTrader 5

L'application se connecte au terminal MT5 local. Assurez-vous que:
- MetaTrader 5 est installé et en cours d'exécution
- Vous êtes connecté à votre compte de trading
- La fonctionnalité AutoTrading est activée dans MT5 (bouton en haut de l'interface MT5)

Si la connexion échoue, l'application affichera un message d'erreur. Vous pouvez tenter de vous reconnecter via le menu Fichier > Connecter à MT5.

## Interface utilisateur

L'interface est organisée en plusieurs sections et onglets:

1. **Barre de menu**:
   - Fichier: Connexion, rafraîchissement des données, paramètres
   - Analyse: Exportation de rapports, outils d'optimisation
   - Aide: Information sur l'application

2. **Informations du compte**: Affiche les données essentielles du compte (balance, équité, marge)

3. **Onglets principaux**:
   - **Vue d'ensemble**: Graphique d'équité et indicateurs de performance
   - **Positions ouvertes**: Liste détaillée des positions actuelles
   - **Allocation**: Analyse de la répartition du capital
   - **Benchmarking**: Comparaison avec les indices de marché
   - **Alertes & Optimisation**: Alertes de risque et suggestions
   - **Tableau de bord risque**: Score de risque global et composantes

4. **Barre d'état**: Statut de la connexion et horodatage de la dernière mise à jour

## Fonctionnalités détaillées

### Suivi de l'équité et des performances

Le module de suivi d'équité permet de visualiser l'évolution de votre capital au fil du temps:

- **Graphique d'équité interactif**: Visualisation de la courbe d'équité avec périodes configurables
- **Drawdown overlay**: Visualisation des périodes de drawdown sur la courbe d'équité
- **Analyse de tendance**: Ligne de tendance pour évaluer la direction générale
- **Détection des points de changement**: Identification des changements significatifs dans la performance
- **Métriques de robustesse**: Calcul du Pain Index et de l'Ulcer Index
- **Statistiques de performance**: Rendement, volatilité, drawdown maximum, ratios de performance

#### Métriques calculées:
- Rendement total et annualisé
- Volatilité annualisée
- Drawdown maximum
- Ratio de Sharpe
- Ratio de Sortino
- Ratio de Calmar
- Win Ratio (% de trades gagnants)
- Gains et pertes moyens

### Analyse des positions

Le module de positions offre une vue détaillée de vos positions ouvertes:

- **Liste filtrée**: Filtrages par symbole et direction (BUY/SELL)
- **Suivi des profits**: Visualisation claire des profits/pertes par position
- **Durée des positions**: Affichage du temps écoulé depuis l'ouverture
- **Informations détaillées**: Prix d'ouverture, prix actuel, volume, swap, etc.

### Analyse d'allocation de portefeuille

Ce module analyse la répartition de votre capital selon différentes dimensions:

- **Allocation par symbole**: Répartition du capital entre les instruments
- **Allocation par direction**: Distribution entre positions longues et courtes
- **Allocation par durée**: Répartition selon la durée de détention
- **Visualisations graphiques**: Diagrammes à barres et camemberts pour chaque type d'allocation
- **Exposition au marché**: Analyse de l'exposition directionnelle du portefeuille

### Benchmarking

Cette fonctionnalité compare votre performance à celle des principaux indices du marché:

- **Comparaison normalisée**: Performances relatives sur différentes périodes
- **Métriques comparatives**: Rendement, volatilité, drawdown, Sharpe ratio, etc.
- **Calculs Alpha/Beta**: Évaluation de votre performance ajustée au risque
- **Corrélation**: Analyse de la corrélation entre votre portefeuille et les indices

### D-Leverage Optimizer

Cet outil analyse et optimise votre ratio d'exposition/capital (D-Leverage):

- **Calcul du D-Leverage optimal**: En fonction de votre style de trading
- **Analyse du style de trading**: Détection automatique basée sur la durée des positions
- **Recommandations de sizing**: Suggestions de redimensionnement des positions
- **Suivi historique**: Graphique d'évolution du D-Leverage dans le temps
- **Zones optimales**: Visualisation des zones optimales de D-Leverage par style

### Tableau de bord de risque

Cette section offre une vue globale du risque de votre portefeuille:

- **Score de risque global**: Notation de 0 à 100 avec évaluation qualitative
- **Composantes de risque**: Décomposition du score par facteur de risque
- **Visualisation par jauge**: Représentation graphique du niveau de risque
- **Analyse des tendances**: Suivi de l'évolution du risque au fil du temps
- **Recommandations**: Suggestions pour l'optimisation du niveau de risque

### Système d'alertes

Le système d'alertes surveille en permanence votre portefeuille:

- **Alertes en temps réel**: Détection des situations à risque
- **Seuils configurables**: Personnalisation des niveaux d'alerte
- **Suggestions d'optimisation**: Recommandations concrètes pour résoudre les problèmes
- **Historique des alertes**: Suivi des alertes passées
- **Catégorisation**: Alertes par type et niveau de sévérité

### Analyse VaR

Module d'analyse de la Value at Risk multi-méthodes:

- **Méthodes de calcul**: Paramétrique, Historique et Monte Carlo
- **Horizons temporels**: VaR quotidienne, hebdomadaire et mensuelle
- **Niveaux de confiance**: Calculs à 95% et 99%
- **Expected Shortfall**: Calcul de l'ES/CVaR pour chaque configuration
- **Suivi historique**: Évolution de la VaR dans le temps
- **Ratio VaR**: Analyse de la stabilité de la VaR (max/min)

## Concepts clés

### D-Leverage

Le D-Leverage (Dynamic Leverage) est un concept central pour l'évaluation du risque:

- **Définition**: Ratio entre l'exposition totale et l'équité du compte
- **Calcul**: `(Somme des volumes * Taille du contrat) / Équité`
- **Interprétation**: Mesure l'effet de levier dynamique et le risque global
- **Valeurs optimales par style de trading**:
  * Scalping (<30min): D-Leverage max de 16.25
  * Intraday (30-60min): D-Leverage max de 13
  * Swing (>60min): D-Leverage max de 9.75

### Value at Risk (VaR)

La VaR est une mesure statistique de risque:

- **Définition**: Perte potentielle maximale sur une période donnée à un niveau de confiance spécifié
- **Méthodes de calcul**:
  * **Paramétrique**: Basée sur la distribution normale des rendements
  * **Historique**: Basée sur les rendements historiques réels
  * **Monte Carlo**: Simulation de milliers de scénarios possibles
- **Utilisation**: Évaluation du risque de queue et dimensionnement du portefeuille
- **Expected Shortfall (ES/CVaR)**: Mesure complémentaire qui indique la perte moyenne au-delà de la VaR

### Métriques de performance

L'application calcule plusieurs métriques clés:

- **Ratio de Sharpe**: Mesure le rendement excédentaire par unité de risque
- **Ratio de Sortino**: Similaire au Sharpe mais ne pénalise que le risque baissier
- **Ratio de Calmar**: Mesure le rendement annualisé par rapport au drawdown maximum
- **Pain Index**: Mesure la profondeur et la durée des drawdowns
- **Ulcer Index**: Alternative au drawdown standard qui pénalise les drawdowns longs
- **Rendement/risque**: Diverses mesures du rapport entre rendement et risque

## Configuration

Les paramètres peuvent être configurés via le menu Fichier > Paramètres:

### Seuils d'alerte

Configurez les seuils qui déclenchent des alertes:
- Pourcentage de marge utilisée
- Perte journalière maximale
- Drawdown maximum acceptable
- D-Leverage maximum
- VaR mensuelle maximale
- Seuil de corrélation
- Concentration sectorielle maximale

### Rafraîchissement des données

Paramètres de mise à jour des données:
- Activation/désactivation du rafraîchissement automatique
- Intervalle de rafraîchissement (30s, 1m, 5m, etc.)
- Nombre de jours d'historique à charger

### Interface utilisateur

Personnalisation de l'interface:
- Thème (default, dark)
- Style de graphique
- Langue
- Option d'affichage de l'écran de bienvenue

### Notifications

Configuration des notifications par email:
- Activation/désactivation des notifications
- Paramètres du serveur SMTP
- Destinataire des alertes

## Développement

### Structure détaillée du code

#### Package core

- **mt5_connector.py**: Interface avec l'API MT5
  * Établit la connexion à MetaTrader 5
  * Extrait les positions, historiques et infos de compte
  * Convertit les données MT5 en structures pandas

- **data_manager.py**: Centralise la gestion des données
  * Maintient en cache les données actuelles
  * Coordonne les requêtes de rafraîchissement
  * Calcule les métriques dérivées (D-Leverage, VaR, etc.)

- **config_manager.py**: Gère les configurations
  * Charge/sauvegarde les paramètres utilisateur
  * Gère les valeurs par défaut
  * Fournit une interface pour accéder aux configurations

#### Package analysis

- **performance_metrics.py**: Calcul des métriques de performance
  * Rendement, volatilité, drawdown
  * Ratios de performance (Sharpe, Sortino, Calmar)
  * Analyse de distribution des rendements

- **risk_metrics.py**: Calcul des métriques de risque
  * Value at Risk (VaR)
  * Expected Shortfall
  * Concentration du risque
  * Corrélation des positions

- **drawdown_analyzer.py**: Analyse approfondie des drawdowns
  * Identification des périodes de drawdown
  * Calcul des indices de drawdown (Pain Index, Ulcer Index)
  * Analyse des points de changement de tendance

- **allocation_analysis.py**: Analyse d'allocation
  * Répartition par instrument, direction, durée
  * Calcul des expositions et concentrations
  * Recommandations d'allocation

- **metrics_interpreter.py**: Interprétation des métriques
  * Analyse qualitative des ratios de performance
  * Recommandations basées sur les métriques
  * Analyse de tendance des indicateurs

- **alerts_engine.py**: Moteur d'alertes
  * Surveillance des métriques par rapport aux seuils
  * Génération d'alertes et de suggestions
  * Historique des alertes

- **risk_score_calculator.py**: Calcul du score de risque global
  * Normalisation des composantes de risque
  * Pondération et agrégation des facteurs
  * Évaluation qualitative du niveau de risque

#### Package ui

- **main_window.py**: Fenêtre principale
  * Organisation de l'interface utilisateur
  * Gestion des événements principaux
  * Coordination des widgets et dialogues

- **widgets/**: Composants d'interface
  * Widgets spécialisés pour chaque fonctionnalité
  * Visualisations interactives
  * Mises à jour en temps réel

- **dialogs/**: Boîtes de dialogue
  * Paramétrages avancés
  * Interfaces d'analyse spécialisées
  * Information et aide

#### Package utils

- **constants.py**: Constantes et configurations
  * Configurations par défaut
  * Mappings et correspondances
  * Seuils et limites

- **helpers.py**: Fonctions utilitaires
  * Formatage des nombres et dates
  * Calculs statistiques réutilisables
  * Fonctions d'aide diverses

### Ajout de fonctionnalités

Pour ajouter une nouvelle fonctionnalité:

1. **Analyse du besoin**: Déterminez si la fonctionnalité nécessite:
   - Un nouveau calcul d'analyse (module dans `analysis/`)
   - Une nouvelle visualisation (widget dans `ui/widgets/`)
   - Une interface dédiée (dialogue dans `ui/dialogs/`)

2. **Implémentation backend**:
   - Ajoutez les fonctions d'analyse dans le module approprié
   - Intégrez avec le `DataManager` si nécessaire
   - Testez les calculs indépendamment

3. **Implémentation frontend**:
   - Créez le widget ou le dialogue nécessaire
   - Connectez-le aux données via le `DataManager`
   - Gérez les mises à jour et événements utilisateur

4. **Intégration**:
   - Ajoutez le widget à la fenêtre principale
   - Mettez à jour les menus si nécessaire
   - Assurez la coordination avec les autres composants

5. **Documentation**:
   - Documentez la nouvelle fonctionnalité dans le code
   - Mettez à jour ce README.md
   - Ajoutez des tooltips explicatifs dans l'interface

## Roadmap

Voici les fonctionnalités prévues pour les prochaines versions:

### Version 1.1
- Export de rapports d'analyse au format PDF et Excel
- Analyse d'attribution de performance
- Backtesting simplifié de stratégies

### Version 1.2
- Classification automatique des instruments par secteur/classe d'actifs
- Analyse de corrélation avancée entre instruments
- Dashboard personnalisable

### Version 1.3
- Intégration multi-compte et multi-stratégie
- Analyse de scénarios (stress tests)
- Suivi des objectifs de trading et KPIs

### Version 2.0
- Intégration avec d'autres plateformes de trading
- Recommandations basées sur l'intelligence artificielle
- Interface mobile

## Contribution

Les contributions sont les bienvenues! Pour contribuer:

1. Forkez le dépôt
2. Créez une branche pour votre fonctionnalité (`git checkout -b feature/amazing-feature`)
3. Committez vos changements (`git commit -m 'Add some amazing feature'`)
4. Poussez vers la branche (`git push origin feature/amazing-feature`)
5. Ouvrez une Pull Request

Veuillez suivre les conventions de codage et ajouter des tests appropriés.

## Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.

---

© 2025 MT5 Trading Analyzer. Tous droits réservés.