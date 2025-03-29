#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Boîte de dialogue À propos pour MT5 Trading Analyzer
"""

import tkinter as tk
from tkinter import ttk
import logging
from utils.constants import APP_NAME, APP_VERSION, APP_AUTHOR

class AboutDialog:
    """Boîte de dialogue affichant les informations sur l'application"""
    
    def __init__(self, parent):
        """
        Initialisation de la boîte de dialogue À propos
        
        Args:
            parent: Widget parent Tkinter
        """
        self.logger = logging.getLogger(__name__)
        
        # Création de la fenêtre de dialogue
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("À propos")
        self.dialog.geometry("400x300")
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
        # Frame principal
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Titre de l'application
        title_label = ttk.Label(main_frame, text=APP_NAME, font=("Helvetica", 14, "bold"))
        title_label.pack(pady=10)
        
        # Version
        version_label = ttk.Label(main_frame, text=f"Version {APP_VERSION}")
        version_label.pack()
        
        # Auteur/Copyright
        author_label = ttk.Label(main_frame, text=APP_AUTHOR)
        author_label.pack(pady=5)
        
        # Séparateur
        separator = ttk.Separator(main_frame, orient="horizontal")
        separator.pack(fill="x", pady=10)
        
        # Description
        description_text = (
            "Application de bureau pour surveiller et analyser vos activités de trading MT5.\n\n"
            "Fonctionnalités principales:\n"
            "- Suivi de l'équité et de la performance\n"
            "- Calcul des ratios (Sharpe, Sortino, Calmar)\n"
            "- Analyse du D-Leverage et de la VaR\n"
            "- Benchmarking avec les indices majeurs\n"
            "- Alertes et suggestions d'optimisation"
        )
        
        description_label = ttk.Label(main_frame, text=description_text, wraplength=350, justify="center")
        description_label.pack(pady=10)
        
        # Bouton Fermer
        close_button = ttk.Button(main_frame, text="Fermer", command=self.dialog.destroy)
        close_button.pack(pady=10)