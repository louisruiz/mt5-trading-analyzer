#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Boîte de dialogue des paramètres pour MT5 Trading Analyzer
"""

import tkinter as tk
from tkinter import ttk
import logging
from utils.constants import REFRESH_INTERVALS

class SettingsDialog:
    """Boîte de dialogue des paramètres de l'application"""
    
    def __init__(self, parent, config_manager):
        """
        Initialisation de la boîte de dialogue des paramètres
        
        Args:
            parent: Widget parent Tkinter
            config_manager (ConfigManager): Instance du gestionnaire de configuration
        """
        self.logger = logging.getLogger(__name__)
        self.config_manager = config_manager
        self.result = False
        
        # Création de la fenêtre de dialogue
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Paramètres")
        self.dialog.geometry("500x400")
        self.dialog.transient(parent)  # Dialogue modal
        self.dialog.grab_set()
        
        # Centrer la fenêtre
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        self.create_widgets()
        
        # Attendre la fermeture de la fenêtre
        self.dialog.wait_window()
    
    def create_widgets(self):
        """Création des widgets pour la boîte de dialogue"""
        # Notebook pour les onglets de paramètres
        notebook = ttk.Notebook(self.dialog)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Onglet 1: Seuils d'alerte
        alert_tab = ttk.Frame(notebook)
        notebook.add(alert_tab, text="Alertes")
        self.create_alert_tab(alert_tab)
        
        # Onglet 2: Rafraîchissement des données
        refresh_tab = ttk.Frame(notebook)
        notebook.add(refresh_tab, text="Rafraîchissement")
        self.create_refresh_tab(refresh_tab)
        
        # Onglet 3: Interface utilisateur
        ui_tab = ttk.Frame(notebook)
        notebook.add(ui_tab, text="Interface")
        self.create_ui_tab(ui_tab)
        
        # Onglet 4: Notification par email
        email_tab = ttk.Frame(notebook)
        notebook.add(email_tab, text="Notifications")
        self.create_email_tab(email_tab)
        
        # Frame pour les boutons
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Bouton Enregistrer
        save_button = ttk.Button(button_frame, text="Enregistrer", command=self.save_settings)
        save_button.pack(side=tk.RIGHT, padx=5)
        
        # Bouton Annuler
        cancel_button = ttk.Button(button_frame, text="Annuler", command=self.dialog.destroy)
        cancel_button.pack(side=tk.RIGHT, padx=5)
    
    def create_alert_tab(self, parent):
        """
        Création de l'onglet des seuils d'alerte
        
        Args:
            parent: Widget parent pour cet onglet
        """
        # Frame pour les seuils d'alerte
        alert_frame = ttk.LabelFrame(parent, text="Seuils d'alerte", padding=10)
        alert_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Charger les seuils actuels
        thresholds = self.config_manager.get_alert_thresholds()
        
        # Variables pour stocker les valeurs
        self.alert_vars = {}
        
        # Marge utilisée
        ttk.Label(alert_frame, text="Marge utilisée (%)").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.alert_vars['margin_pct'] = tk.DoubleVar(value=thresholds['margin_pct'])
        margin_pct_entry = ttk.Entry(alert_frame, textvariable=self.alert_vars['margin_pct'], width=10)
        margin_pct_entry.grid(row=0, column=1, padx=5)
        
        # Perte journalière
        ttk.Label(alert_frame, text="Perte journalière (%)").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.alert_vars['daily_loss'] = tk.DoubleVar(value=abs(thresholds['daily_loss']))
        daily_loss_entry = ttk.Entry(alert_frame, textvariable=self.alert_vars['daily_loss'], width=10)
        daily_loss_entry.grid(row=1, column=1, padx=5)
        
        # Drawdown
        ttk.Label(alert_frame, text="Drawdown (%)").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.alert_vars['drawdown'] = tk.DoubleVar(value=abs(thresholds['drawdown']))
        drawdown_entry = ttk.Entry(alert_frame, textvariable=self.alert_vars['drawdown'], width=10)
        drawdown_entry.grid(row=2, column=1, padx=5)
        
        # D-Leverage
        ttk.Label(alert_frame, text="D-Leverage").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.alert_vars['d_leverage'] = tk.DoubleVar(value=thresholds['d_leverage'])
        d_leverage_entry = ttk.Entry(alert_frame, textvariable=self.alert_vars['d_leverage'], width=10)
        d_leverage_entry.grid(row=3, column=1, padx=5)
        
        # VaR mensuelle
        ttk.Label(alert_frame, text="VaR mensuelle (%)").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.alert_vars['var_monthly'] = tk.DoubleVar(value=thresholds.get('var_monthly', 12))
        var_monthly_entry = ttk.Entry(alert_frame, textvariable=self.alert_vars['var_monthly'], width=10)
        var_monthly_entry.grid(row=4, column=1, padx=5)
        
        # Corrélation
        ttk.Label(alert_frame, text="Seuil de corrélation").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.alert_vars['correlation'] = tk.DoubleVar(value=thresholds.get('correlation', 0.8))
        correlation_entry = ttk.Entry(alert_frame, textvariable=self.alert_vars['correlation'], width=10)
        correlation_entry.grid(row=5, column=1, padx=5)
        
        # Concentration sectorielle
        ttk.Label(alert_frame, text="Concentration sectorielle (%)").grid(row=6, column=0, sticky=tk.W, pady=5)
        self.alert_vars['sector_concentration'] = tk.DoubleVar(value=thresholds.get('sector_concentration', 30))
        sector_concentration_entry = ttk.Entry(alert_frame, textvariable=self.alert_vars['sector_concentration'], width=10)
        sector_concentration_entry.grid(row=6, column=1, padx=5)
        
        # Ajouter des explications pour chaque seuil
        ttk.Label(alert_frame, text="Alerte si la marge utilisée dépasse ce pourcentage").grid(row=0, column=2, sticky=tk.W, padx=10)
        ttk.Label(alert_frame, text="Alerte si la perte quotidienne dépasse ce pourcentage").grid(row=1, column=2, sticky=tk.W, padx=10)
        ttk.Label(alert_frame, text="Alerte si le drawdown dépasse ce pourcentage").grid(row=2, column=2, sticky=tk.W, padx=10)
        ttk.Label(alert_frame, text="Alerte si le D-Leverage dépasse cette valeur").grid(row=3, column=2, sticky=tk.W, padx=10)
        ttk.Label(alert_frame, text="Alerte si la VaR mensuelle dépasse ce pourcentage").grid(row=4, column=2, sticky=tk.W, padx=10)
        ttk.Label(alert_frame, text="Alerte si la corrélation entre instruments dépasse cette valeur").grid(row=5, column=2, sticky=tk.W, padx=10)
        ttk.Label(alert_frame, text="Alerte si l'exposition à un secteur dépasse ce pourcentage").grid(row=6, column=2, sticky=tk.W, padx=10)
    
    def create_refresh_tab(self, parent):
        """
        Création de l'onglet de rafraîchissement des données
        
        Args:
            parent: Widget parent pour cet onglet
        """
        # Frame pour les paramètres de rafraîchissement
        refresh_frame = ttk.LabelFrame(parent, text="Paramètres de rafraîchissement", padding=10)
        refresh_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Charger les paramètres actuels
        refresh_settings = self.config_manager.get_data_refresh_settings()
        
        # Rafraîchissement automatique
        self.auto_refresh_var = tk.BooleanVar(value=refresh_settings['auto_refresh'])
        auto_refresh_check = ttk.Checkbutton(refresh_frame, text="Rafraîchissement automatique",
                                            variable=self.auto_refresh_var)
        auto_refresh_check.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=10)
        
        # Intervalle de rafraîchissement
        ttk.Label(refresh_frame, text="Intervalle de rafraîchissement:").grid(row=1, column=0, sticky=tk.W, pady=5)
        
        # Convertir l'intervalle en secondes en clé de dictionnaire
        interval_seconds = refresh_settings['refresh_interval']
        interval_key = None
        for key, value in REFRESH_INTERVALS.items():
            if value == interval_seconds:
                interval_key = key
                break
        
        # Si aucune correspondance trouvée, utiliser la valeur par défaut
        if interval_key is None:
            interval_key = "1m"  # 1 minute
        
        self.refresh_interval_var = tk.StringVar(value=interval_key)
        refresh_interval_combo = ttk.Combobox(refresh_frame, textvariable=self.refresh_interval_var,
                                             values=list(REFRESH_INTERVALS.keys()), width=10)
        refresh_interval_combo.grid(row=1, column=1, sticky=tk.W, padx=5)
        
        # Jours d'historique
        ttk.Label(refresh_frame, text="Jours d'historique à charger:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.history_days_var = tk.IntVar(value=refresh_settings['history_days'])
        history_days_entry = ttk.Entry(refresh_frame, textvariable=self.history_days_var, width=10)
        history_days_entry.grid(row=2, column=1, sticky=tk.W, padx=5)
    
    def create_ui_tab(self, parent):
        """
        Création de l'onglet d'interface utilisateur
        
        Args:
            parent: Widget parent pour cet onglet
        """
        # Frame pour les paramètres d'interface
        ui_frame = ttk.LabelFrame(parent, text="Paramètres d'interface", padding=10)
        ui_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Charger les paramètres actuels
        ui_settings = self.config_manager.get_ui_settings()
        
        # Thème
        ttk.Label(ui_frame, text="Thème:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.theme_var = tk.StringVar(value=ui_settings['theme'])
        theme_combo = ttk.Combobox(ui_frame, textvariable=self.theme_var,
                                  values=["default", "dark"], width=15)
        theme_combo.grid(row=0, column=1, sticky=tk.W, padx=5)
        
        # Style de graphique
        ttk.Label(ui_frame, text="Style de graphique:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.chart_style_var = tk.StringVar(value=ui_settings['chart_style'])
        chart_style_combo = ttk.Combobox(ui_frame, textvariable=self.chart_style_var,
                                       values=["default", "dark"], width=15)
        chart_style_combo.grid(row=1, column=1, sticky=tk.W, padx=5)
        
        # Langue
        ttk.Label(ui_frame, text="Langue:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.language_var = tk.StringVar(value=ui_settings['language'])
        language_combo = ttk.Combobox(ui_frame, textvariable=self.language_var,
                                     values=["fr", "en"], width=15)
        language_combo.grid(row=2, column=1, sticky=tk.W, padx=5)
        
        # Afficher l'écran de bienvenue
        self.show_welcome_var = tk.BooleanVar(value=ui_settings['show_welcome'])
        show_welcome_check = ttk.Checkbutton(ui_frame, text="Afficher l'écran de bienvenue au démarrage",
                                           variable=self.show_welcome_var)
        show_welcome_check.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=10)
    
    def create_email_tab(self, parent):
        """
        Création de l'onglet de notification par email
        
        Args:
            parent: Widget parent pour cet onglet
        """
        # Frame pour les paramètres de notification par email
        email_frame = ttk.LabelFrame(parent, text="Notifications par email", padding=10)
        email_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Charger les paramètres actuels
        email_settings = self.config_manager.get_email_settings()
        
        # Activer les notifications par email
        self.email_enabled_var = tk.BooleanVar(value=email_settings['enabled'])
        email_enabled_check = ttk.Checkbutton(email_frame, text="Activer les notifications par email",
                                             variable=self.email_enabled_var)
        email_enabled_check.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=10)
        
        # Serveur SMTP
        ttk.Label(email_frame, text="Serveur SMTP:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.smtp_server_var = tk.StringVar(value=email_settings['smtp_server'])
        smtp_server_entry = ttk.Entry(email_frame, textvariable=self.smtp_server_var, width=30)
        smtp_server_entry.grid(row=1, column=1, sticky=tk.W, padx=5)
        
        # Port SMTP
        ttk.Label(email_frame, text="Port SMTP:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.smtp_port_var = tk.IntVar(value=email_settings['smtp_port'])
        smtp_port_entry = ttk.Entry(email_frame, textvariable=self.smtp_port_var, width=10)
        smtp_port_entry.grid(row=2, column=1, sticky=tk.W, padx=5)
        
        # Nom d'utilisateur SMTP
        ttk.Label(email_frame, text="Nom d'utilisateur:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.smtp_username_var = tk.StringVar(value=email_settings['smtp_username'])
        smtp_username_entry = ttk.Entry(email_frame, textvariable=self.smtp_username_var, width=30)
        smtp_username_entry.grid(row=3, column=1, sticky=tk.W, padx=5)
        
        # Mot de passe SMTP
        ttk.Label(email_frame, text="Mot de passe:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.smtp_password_var = tk.StringVar(value=email_settings['smtp_password'])
        smtp_password_entry = ttk.Entry(email_frame, textvariable=self.smtp_password_var, width=30, show="*")
        smtp_password_entry.grid(row=4, column=1, sticky=tk.W,padx=5)

         # Destinataire
        ttk.Label(email_frame, text="Destinataire:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.recipient_var = tk.StringVar(value=email_settings['recipient'])
        recipient_entry = ttk.Entry(email_frame, textvariable=self.recipient_var, width=30)
        recipient_entry.grid(row=5, column=1, sticky=tk.W, padx=5)
        
        # Bouton pour tester la configuration
        test_button = ttk.Button(email_frame, text="Tester la configuration", command=self.test_email_config)
        test_button.grid(row=6, column=0, columnspan=2, pady=10)
    
    def test_email_config(self):
        """Teste la configuration email en envoyant un email de test"""
        # Cette méthode serait implémentée pour envoyer un email de test
        # Basée sur les paramètres actuels de l'interface
        # Pour l'instant, on affiche juste un message
        from tkinter import messagebox
        messagebox.showinfo("Test Email", "Fonctionnalité à implémenter dans une future version.")
    
    def save_settings(self):
        """Enregistre les paramètres"""
        try:
            # Enregistrer les seuils d'alerte
            alert_thresholds = {
                'margin_pct': self.alert_vars['margin_pct'].get(),
                'daily_loss': -self.alert_vars['daily_loss'].get(),  # Valeur négative
                'drawdown': -self.alert_vars['drawdown'].get(),      # Valeur négative
                'd_leverage': self.alert_vars['d_leverage'].get(),
                'var_monthly': self.alert_vars['var_monthly'].get(),
                'correlation': self.alert_vars['correlation'].get(),
                'sector_concentration': self.alert_vars['sector_concentration'].get()
            }
            self.config_manager.set_alert_thresholds(alert_thresholds)
            
            # Enregistrer les paramètres de rafraîchissement
            refresh_settings = {
                'auto_refresh': self.auto_refresh_var.get(),
                'refresh_interval': REFRESH_INTERVALS[self.refresh_interval_var.get()],
                'history_days': self.history_days_var.get()
            }
            self.config_manager.set_data_refresh_settings(refresh_settings)
            
            # Enregistrer les paramètres d'interface
            ui_settings = {
                'theme': self.theme_var.get(),
                'chart_style': self.chart_style_var.get(),
                'language': self.language_var.get(),
                'show_welcome': self.show_welcome_var.get()
            }
            self.config_manager.set_ui_settings(ui_settings)
            
            # Enregistrer les paramètres de notification par email
            email_settings = {
                'enabled': self.email_enabled_var.get(),
                'smtp_server': self.smtp_server_var.get(),
                'smtp_port': self.smtp_port_var.get(),
                'smtp_username': self.smtp_username_var.get(),
                'smtp_password': self.smtp_password_var.get(),
                'recipient': self.recipient_var.get()
            }
            self.config_manager.set_email_settings(email_settings)
            
            # Indiquer que les paramètres ont été enregistrés avec succès
            self.result = True
            
            # Fermer la boîte de dialogue
            self.dialog.destroy()
            
        except Exception as e:
            self.logger.exception("Erreur lors de l'enregistrement des paramètres")
            from tkinter import messagebox
            messagebox.showerror("Erreur", f"Erreur lors de l'enregistrement des paramètres: {str(e)}")