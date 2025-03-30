# MT5 Trading Analyzer

MT5 Trading Analyzer est une application de bureau avancée conçue pour surveiller, analyser et optimiser vos activités de trading sur MetaTrader 5. Cette application offre une vision détaillée de votre portefeuille, des métriques de performance avancées, et des outils d'aide à la décision.

## Fonctionnalités principales

- **Dashboard synthétique**: Vue d'ensemble des métriques clés de performance et de risque
- **Analyse de performance**: Calcul des ratios Sharpe, Sortino, Calmar et autres métriques avancées
- **Visualisation des risques**: Drawdowns, distribution des rendements
- **Analyse des positions**: Suivi détaillé de vos positions ouvertes
- **Analyse d'allocation**: Répartition par instrument, direction et durée
- **Benchmarking**: Comparaison de performance avec les indices majeurs
- **Alertes intelligentes**: Surveillance continue des niveaux de risque et notifications
- **Optimisation de D-Leverage**: Optimisation de l'effet de levier dynamique selon votre style de trading
- **Analyse de VaR**: Calcul et suivi de la Value at Risk avec différentes méthodes

## Architecture

L'application est structurée de manière modulaire pour faciliter la maintenance et l'extension:

```
mt5_trading_analyzer/
│
├── main.py                  # Point d'entrée principal de l'application
│
├── core/                    # Modules de base
│   ├── mt5_connector.py     # Gestion de la connexion MT5
│   ├── data_manager.py      # Gestion des données
│   └── config_manager.py    # Gestion de la configuration
│
├── ui/                      # Interface utilisateur
│   ├── main_window.py       # Fenêtre principale
│   ├── widgets/             # Widgets d'interface
│   └── dialogs/             # Boîtes de dialogue
│
├── analysis/                # Modules d'analyse
│   ├── performance_metrics.py  # Métriques de performance
│   ├── risk_metrics.py         # Métriques de risque
│   ├── allocation_analysis.py  # Analyse de l'allocation
│   └── alerts_engine.py        # Moteur d'alertes
│
└── utils/                   # Utilitaires
    ├── constants.py         # Constantes
    └── helpers.py           # Fonctions utilitaires
```

## Prérequis

- Python 3.7 ou supérieur
- MetaTrader 5 installé et configuré
- Bibliothèques Python requises:
  - MetaTrader5
  - pandas
  - numpy
  - matplotlib
  - scipy
  - yfinance
  - tkinter

## Installation

1. Clonez ce dépôt:
   ```
   git clone https://github.com/your-username/mt5-trading-analyzer.git
   cd mt5-trading-analyzer
   ```

2. Installez les dépendances:
   ```
   pip install -r requirements.txt
   ```

3. Assurez-vous que MetaTrader 5 est installé et en cours d'exécution.

## Utilisation

Lancez l'application avec:
```
python main.py
```

L'application se connectera automatiquement à votre terminal MT5 s'il est en cours d'exécution.

### Connexion à MetaTrader 5

L'application se connecte automatiquement à votre terminal MT5 local. Assurez-vous que:
- MetaTrader 5 est installé et en cours d'exécution
- Vous êtes connecté à votre compte de trading
- La fonctionnalité AutoTrading est activée dans MT5

### Interface utilisateur

L'interface est organisée en plusieurs onglets:
- **Vue d'ensemble**: Graphique d'équité et statistiques de performance
- **Positions ouvertes**: Liste détaillée des positions actuelles avec filtres
- **Allocation**: Répartition par instrument, direction et durée
- **Benchmarking**: Comparaison de performance avec les indices majeurs
- **Alertes & Optimisation**: Alertes de risque et suggestions d'optimisation

## Métriques et analyses

### D-Leverage

Le D-Leverage est une métrique importante pour évaluer le risque de votre portefeuille:
- Mesure l'effet de levier dynamique (exposition / équité)
- Recommandations selon le style de trading:
  * Scalping (<30min): D-Leverage max de 16.25
  * Intraday (30-60min): D-Leverage max de 13
  * Swing (>60min): D-Leverage max de 9.75

### Value at Risk (VaR)

L'application propose trois méthodes de calcul de VaR:
- **Paramétrique**: Basée sur l'hypothèse de distribution normale
- **Historique**: Basée sur la distribution empirique des rendements passés
- **Monte Carlo**: Basée sur des simulations de scénarios

### Métriques de performance

- Rendement total/annualisé
- Volatilité
- Drawdown maximum
- Ratio de Sharpe
- Ratio de Sortino
- Ratio de Calmar
- Skewness et Kurtosis

## Configuration

Les paramètres de l'application peuvent être configurés via le menu Fichier > Paramètres:

- **Alertes**: Seuils d'alerte pour différentes métriques
- **Rafraîchissement**: Intervalle de rafraîchissement automatique des données
- **Interface**: Personnalisation de l'interface utilisateur
- **Notifications**: Configuration des notifications par email

## Prochaines fonctionnalités

- Rapports d'analyse exportables (PDF/Excel)
- Backtesting de stratégies
- Classification automatique des instruments par secteur
- Interface pour la gestion de portefeuilles multiples
- Intégration avec d'autres plateformes de trading

## Contribution

Les contributions sont les bienvenues! N'hésitez pas à ouvrir une issue ou à soumettre une pull request.

## Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.