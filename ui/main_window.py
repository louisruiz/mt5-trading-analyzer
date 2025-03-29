#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Fenêtre principale de l'application MT5 Trading Analyzer
"""

import tkinter as tk
from tkinter import ttk, messagebox
import logging
import threading
import time

from core.data_manager import DataManager
from core.config_manager import ConfigManager

from ui.widgets.account_info_widget import AccountInfoWidget
from ui.widgets.positions_widget import PositionsWidget
from ui.widgets.equity_chart_widget import EquityChartWidget
from ui.widgets.performance_widget import PerformanceWidget
from ui.widgets.allocation_widget import AllocationWidget
from ui.widgets.benchmark_widget import BenchmarkWidget
from ui.widgets.alerts_widget import AlertsWidget
from ui.widgets.status_bar_widget import StatusBarWidget
from ui.widgets.d_leverage_chart_widget import DLeverageChartWidget
from ui.widgets.risk_score_widget import RiskScoreWidget

from ui.dialogs.settings_dialog import SettingsDialog
from ui.dialogs.d_leverage_dialog import DLeverageDialog
from ui.dialogs.var_dialog import VarDialog
from ui.dialogs.about_dialog import AboutDialog

class MainWindow:
    """Classe de la fenêtre principale de l'application"""
    
    def __init__(self, root):
        """
        Initialisation de la fenêtre principale
        
        Args:
            root (tk.Tk): Fenêtre racine Tkinter
        """
        self.logger = logging.getLogger(__name__)
        self.root = root
        self.root.title("MT5 Analyste de Trading Pro")
        self.root.geometry("1280x900")
        self.root.minsize(1024, 768)
        
        # Initialiser les gestionnaires
        self.data_manager = DataManager()
        self.config_manager = ConfigManager()
        
        # Flag pour le rafraîchissement automatique
        self.auto_refresh_enabled = self.config_manager.get("data_refresh", "auto_refresh", True)
        self.refresh_interval = self.config_manager.get("data_refresh", "refresh_interval", 60)
        
        # Création de l'interface
        self.create_menu()
        self.create_widgets()
        
        # Tentative de connexion automatique à MT5
        self.connect_to_mt5()
        
        # Démarrer la surveillance en arrière-plan si activée
        if self.auto_refresh_enabled:
            self.start_background_monitoring()
    
    def create_menu(self):
        """Création de la barre de menu"""
        menubar = tk.Menu(self.root)
        
        # Menu Fichier
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Connecter à MT5", command=self.connect_to_mt5)
        file_menu.add_command(label="Rafraîchir les données", command=self.refresh_data)
        file_menu.add_separator()
        file_menu.add_command(label="Paramètres", command=self.show_settings)
        file_menu.add_separator()
        file_menu.add_command(label="Quitter", command=self.quit_application)
        menubar.add_cascade(label="Fichier", menu=file_menu)
        
        # Menu Analyse
        analysis_menu = tk.Menu(menubar, tearoff=0)
        analysis_menu.add_command(label="Exporter le rapport", command=self.export_report)
        analysis_menu.add_command(label="Optimisation D-Leverage", command=self.show_d_leverage_optimizer)
        analysis_menu.add_command(label="Analyse de VaR", command=self.show_var_analysis)
        menubar.add_cascade(label="Analyse", menu=analysis_menu)
        
        # Menu Aide
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="À propos", command=self.show_about)
        menubar.add_cascade(label="Aide", menu=help_menu)
        
        # Attacher le menu à la fenêtre
        self.root.config(menu=menubar)
    
    def create_widgets(self):
        """Création des widgets de l'interface utilisateur"""
        # Frame principal avec PanedWindow pour redimensionnement
        self.main_paned = ttk.PanedWindow(self.root, orient=tk.VERTICAL)
        self.main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # ==== PARTIE SUPÉRIEURE ====
        self.top_frame = ttk.Frame(self.main_paned)
        self.main_paned.add(self.top_frame, weight=9)
        
        # Widget d'informations du compte
        self.account_info_widget = AccountInfoWidget(self.top_frame, self.data_manager)
        self.account_info_widget.pack(fill=tk.X, padx=5, pady=5)
        
        # Onglets principaux
        self.tab_control = ttk.Notebook(self.top_frame)
        self.tab_control.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Onglet 1: Vue d'ensemble
        self.overview_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.overview_tab, text="Vue d'ensemble")
        
        # Division en deux parties
        overview_left_frame = ttk.Frame(self.overview_tab)
        overview_left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        overview_right_frame = ttk.Frame(self.overview_tab)
        overview_right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Graphique de l'équité (gauche)
        self.equity_chart_widget = EquityChartWidget(overview_left_frame, self.data_manager)
        self.equity_chart_widget.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Statistiques de performance (droite haut)
        self.performance_widget = PerformanceWidget(overview_right_frame, self.data_manager)
        self.performance_widget.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Ajout du widget D-Leverage dans le frame de droite (droite bas)
        self.d_leverage_chart_widget = DLeverageChartWidget(overview_right_frame, self.data_manager)
        self.d_leverage_chart_widget.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Onglet 2: Positions
        self.positions_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.positions_tab, text="Positions ouvertes")
        
        # Widget des positions
        self.positions_widget = PositionsWidget(self.positions_tab, self.data_manager)
        self.positions_widget.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Onglet 3: Allocation
        self.allocation_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.allocation_tab, text="Allocation")
        
        # Widget d'allocation
        self.allocation_widget = AllocationWidget(self.allocation_tab, self.data_manager)
        self.allocation_widget.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Onglet 4: Benchmarking
        self.benchmark_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.benchmark_tab, text="Benchmarking")
        
        # Widget de benchmarking
        self.benchmark_widget = BenchmarkWidget(self.benchmark_tab, self.data_manager)
        self.benchmark_widget.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Onglet 5: Alertes et Optimisation
        self.alerts_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.alerts_tab, text="Alertes & Optimisation")
        
        # Widget des alertes
        self.alerts_widget = AlertsWidget(self.alerts_tab, self.data_manager, self.config_manager)
        self.alerts_widget.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Onglet 6: Tableau de bord risque
        risk_dashboard_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(risk_dashboard_tab, text="Tableau de bord risque")
        
        # Diviser l'onglet en deux parties
        risk_top_frame = ttk.Frame(risk_dashboard_tab)
        risk_top_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        risk_bottom_frame = ttk.Frame(risk_dashboard_tab)
        risk_bottom_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Créer le widget de score de risque global
        self.risk_score_widget = RiskScoreWidget(risk_top_frame, self.data_manager)
        self.risk_score_widget.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Créer le widget de visualisation D-Leverage
        d_leverage_widget_risk = DLeverageChartWidget(risk_bottom_frame, self.data_manager)
        d_leverage_widget_risk.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # ==== PARTIE INFÉRIEURE ====
        self.bottom_frame = ttk.Frame(self.main_paned)
        self.main_paned.add(self.bottom_frame, weight=1)
        
        # Barre de statut
        self.status_bar = StatusBarWidget(self.bottom_frame)
        self.status_bar.pack(fill=tk.X, padx=5, pady=5)
        
        # Frame de contrôle
        control_frame = ttk.Frame(self.bottom_frame)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Checkbox pour le rafraîchissement automatique
        self.auto_refresh_var = tk.BooleanVar(value=self.auto_refresh_enabled)
        auto_refresh_check = ttk.Checkbutton(
            control_frame, 
            text="Rafraîchissement automatique", 
            variable=self.auto_refresh_var,
            command=self.toggle_auto_refresh
        )
        auto_refresh_check.pack(side=tk.LEFT, padx=5)
        
        # Bouton de rafraîchissement manuel
        refresh_button = ttk.Button(control_frame, text="Rafraîchir les données", command=self.refresh_data)
        refresh_button.pack(side=tk.RIGHT, padx=5)
    
    def connect_to_mt5(self):
        """Connexion à MetaTrader 5"""
        self.status_bar.set_status("Connexion à MT5 en cours...")
        
        # Exécuter la connexion dans un thread pour éviter de bloquer l'interface
        def connect_thread():
            success, message = self.data_manager.connect_to_mt5()
            
            # Mettre à jour l'interface dans le thread principal
            self.root.after(0, lambda: self.handle_connection_result(success, message))
        
        threading.Thread(target=connect_thread, daemon=True).start()
    
    def handle_connection_result(self, success, message):
        """Gère le résultat de la connexion MT5"""
        if success:
            self.status_bar.set_status(message, "success")
            self.refresh_data()
        else:
            self.status_bar.set_status(message, "error")
            messagebox.showerror("Erreur de connexion", message)
    
    def refresh_data(self):
        """Rafraîchir toutes les données"""
        if not self.data_manager.connected:
            self.status_bar.set_status("Non connecté à MT5", "error")
            return
        
        self.status_bar.set_status("Rafraîchissement des données en cours...")
        
        # Exécuter le rafraîchissement dans un thread pour éviter de bloquer l'interface
        def refresh_thread():
            success = self.data_manager.refresh_all_data()
            
            # Mettre à jour l'interface dans le thread principal
            self.root.after(0, lambda: self.update_ui(success))
        
        threading.Thread(target=refresh_thread, daemon=True).start()
    
    def update_ui(self, success=True):
        """Met à jour l'interface utilisateur avec les nouvelles données"""
        if success:
            # Mettre à jour tous les widgets
            self.account_info_widget.update()
            self.equity_chart_widget.update()
            self.performance_widget.update()
            self.positions_widget.update()
            self.allocation_widget.update()
            self.benchmark_widget.update()
            self.alerts_widget.update()
            self.risk_score_widget.update()
            self.d_leverage_chart_widget.update()
            
            # Mettre à jour le statut
            self.status_bar.set_status(f"Données rafraîchies à {time.strftime('%H:%M:%S')}", "success")
        else:
            self.status_bar.set_status("Erreur lors du rafraîchissement des données", "error")
    
    def toggle_auto_refresh(self):
        """Active/désactive le rafraîchissement automatique"""
        self.auto_refresh_enabled = self.auto_refresh_var.get()
        
        # Mettre à jour la configuration
        self.config_manager.set("data_refresh", "auto_refresh", self.auto_refresh_enabled)
        
        if self.auto_refresh_enabled:
            self.start_background_monitoring()
            self.status_bar.set_status("Rafraîchissement automatique activé")
        else:
            self.status_bar.set_status("Rafraîchissement automatique désactivé")
    
    def start_background_monitoring(self):
        """Démarrer la surveillance en arrière-plan"""
        if not self.auto_refresh_enabled:
            return
            
        def monitoring_thread():
            while self.auto_refresh_enabled:
                if self.data_manager.connected:
                    # Rafraîchir les données
                    self.data_manager.refresh_all_data()
                    
                    # Mettre à jour l'interface dans le thread principal
                    self.root.after(0, self.update_ui)
                    
                    # Vérifier les alertes
                    # La vérification des alertes est faite dans le widget AlertsWidget
                
                # Attendre l'intervalle de rafraîchissement
                for _ in range(self.refresh_interval):
                    if not self.auto_refresh_enabled:
                        break
                    time.sleep(1)
        
        # Démarrer le thread
        thread = threading.Thread(target=monitoring_thread, daemon=True)
        thread.start()
    
    def show_settings(self):
        """Afficher la boîte de dialogue des paramètres"""
        dialog = SettingsDialog(self.root, self.config_manager)
        
        # Si les paramètres ont été modifiés, mettre à jour l'application
        if dialog.result:
            self.refresh_interval = self.config_manager.get("data_refresh", "refresh_interval", 60)
            self.alerts_widget.load_thresholds()
    
    def show_d_leverage_optimizer(self):
        """Afficher l'optimiseur de D-Leverage"""
        if not self.data_manager.connected:
            messagebox.showwarning("Non connecté", "Veuillez vous connecter à MT5 d'abord")
            return
            
        dialog = DLeverageDialog(self.root, self.data_manager)
    
    def show_var_analysis(self):
        """Afficher l'analyse de VaR"""
        if not self.data_manager.connected:
            messagebox.showwarning("Non connecté", "Veuillez vous connecter à MT5 d'abord")
            return
            
        dialog = VarDialog(self.root, self.data_manager)
    
    def export_report(self):
        """Exporter un rapport complet"""
        if not self.data_manager.connected:
            messagebox.showwarning("Non connecté", "Veuillez vous connecter à MT5 d'abord")
            return
            
        messagebox.showinfo("Export de rapport", "Cette fonctionnalité sera disponible dans une future mise à jour.")
    
    def show_about(self):
        """Afficher la boîte de dialogue À propos"""
        dialog = AboutDialog(self.root)
    
    def quit_application(self):
        """Quitter l'application proprement"""
        if self.data_manager.connected:
            self.data_manager.disconnect()
        
        self.root.quit()