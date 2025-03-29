#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Widget de barre de statut pour MT5 Trading Analyzer
"""

import tkinter as tk
from tkinter import ttk
import logging
from datetime import datetime

class StatusBarWidget(ttk.LabelFrame):
    """Widget de barre de statut pour l'application"""
    
    def __init__(self, parent):
        """
        Initialisation de la barre de statut
        
        Args:
            parent: Widget parent Tkinter
        """
        super().__init__(parent, text="Statut", padding=5)
        self.logger = logging.getLogger(__name__)
        
        self.create_widgets()
    
    def create_widgets(self):
        """Création des widgets pour la barre de statut"""
        # Frame principale
        status_frame = ttk.Frame(self)
        status_frame.pack(fill=tk.X, expand=True)
        
        # Label principal pour le statut
        self.status_label = ttk.Label(status_frame, text="Prêt")
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        # Séparateur
        ttk.Separator(status_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=5)
        
        # Label pour l'horodatage
        self.timestamp_label = ttk.Label(status_frame, text=self.get_timestamp())
        self.timestamp_label.pack(side=tk.LEFT, padx=5)
    
    def set_status(self, message, status_type="info"):
        """
        Définit le message de statut
        
        Args:
            message (str): Message de statut
            status_type (str): Type de statut ("info", "success", "warning", "error")
        """
        try:
            # Mettre à jour le message
            self.status_label.config(text=message)
            
            # Appliquer un style en fonction du type de statut
            if status_type == "success":
                self.status_label.config(foreground="green")
            elif status_type == "warning":
                self.status_label.config(foreground="orange")
            elif status_type == "error":
                self.status_label.config(foreground="red")
            else:  # info
                self.status_label.config(foreground="black")
            
            # Mettre à jour l'horodatage
            self.timestamp_label.config(text=self.get_timestamp())
            
            # Forcer la mise à jour de l'affichage
            self.update_idletasks()
            
        except Exception as e:
            self.logger.exception("Erreur lors de la mise à jour du statut")
    
    def get_timestamp(self):
        """
        Obtient l'horodatage actuel formaté
        
        Returns:
            str: Horodatage formaté
        """
        return datetime.now().strftime("%H:%M:%S")