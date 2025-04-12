import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
from tkinter import font as tkfont
import datetime
import os
import webbrowser
import json
from PIL import Image, ImageTk
import pandas as pd
from fpdf import FPDF
from geopy.distance import geodesic
import requests
from time import sleep

# Custom color scheme
BG_COLOR = "#f0f8ff"
PRIMARY_COLOR = "#4682b4"
SECONDARY_COLOR = "#87cefa"
ACCENT_COLOR = "#ff7f50"
TEXT_COLOR = "#2f4f4f"
EMERGENCY_COLOR = "#ff3333"
HIGHLIGHT_COLOR = "#ffd700"
DARK_ACCENT = "#e67300"
BUTTON_TEXT_COLOR = "#000000"  # Black text for buttons

class HealthAdvisorProPlus:
    def __init__(self, root):
        self.root = root
        self.root.title("Health Advisor Pro+")
        self.root.geometry("1400x900")
        self.root.configure(bg=BG_COLOR)
        
        # Track current step
        self.current_step = 0  # 0=Profile, 1=Metrics, 2=MainApp
        
        # User data
        self.user_profile = {
            'name': '', 'age': '', 'gender': '', 
            'location': '', 'medical_history': '',
            'medical_history_file': '', 'blood_type': '',
            'allergies': '', 'emergency_contact': ''
        }
        
        # Health metrics
        self.health_metrics = {
            'bp': '', 'bp_status': '', 'diabetes': '',
            'diabetes_status': '', 'weight': '', 'height': '',
            'bmi': '', 'risk_level': '', 'last_period': '',
            'cycle_length': '', 'next_period': ''
        }
        
        # Emergency contacts
        self.emergency_contacts = {
            'International': {'Emergency': '112'},
            'United States': {'Emergency': '911'},
            'India': {'Emergency': '112'},
            'United Kingdom': {'Emergency': '999'}
        }

        # Enhanced Medicine Database with more symptoms
        self.medicine_db = {
            'Fever': {
                'Medicines': [
                    'Paracetamol (Crocin/Panadol) - 500mg every 6 hours',
                    'Ibuprofen (Brufen) - 200-400mg every 6-8 hours'
                ],
                'Natural': [
                    'Basil leaf tea: Boil 10-15 leaves in water',
                    'Ginger-honey tea: Boil 1 inch ginger, add honey'
                ],
                'Lifestyle': [
                    'Stay hydrated with water/electrolytes',
                    'Use cool compresses on forehead'
                ],
                'Severity': {
                    'Low': 'Rest and monitor temperature',
                    'Medium': 'Take antipyretics if temperature > 100.4°F',
                    'High': 'Seek medical attention if temperature > 103°F'
                }
            },
            'Headache': {
                'Medicines': [
                    'Paracetamol (Crocin) - 500mg every 6 hours',
                    'Aspirin (Disprin) - 325-650mg every 4 hours',
                    'Ibuprofen (Advil) - 200-400mg every 6-8 hours'
                ],
                'Natural': [
                    'Peppermint oil: Apply on temples',
                    'Cold compress: On forehead for 15 mins',
                    'Ginger tea: Anti-inflammatory properties'
                ],
                'Lifestyle': [
                    'Rest in dark room',
                    'Reduce screen time',
                    'Maintain regular sleep schedule'
                ],
                'Severity': {
                    'Low': 'Try relaxation techniques',
                    'Medium': 'Use OTC pain relievers',
                    'High': 'Seek medical help for persistent headaches'
                }
            }
        }

        # Enhanced Hospital Data with Map Support
        self.hospitals = [
            {'name': 'City General Hospital', 'address': '123 Main St', 
             'city': 'Metropolis', 'location': (12.9716, 77.5946),
             'specialties': ['Emergency', 'Cardiology', 'Pediatrics'],
             'contact': '555-1234', 'rating': 4.5}
        ]

        # WHO links
        self.who_links = {
            "General Health": "https://www.who.int/health-topics",
            "Diabetes": "https://www.who.int/news-room/fact-sheets/detail/diabetes"
        }

        # Initialize directories
        self.reports_dir = "health_reports"
        self.profiles_dir = "user_profiles"
        self.medical_history_dir = "medical_history"
        os.makedirs(self.reports_dir, exist_ok=True)
        os.makedirs(self.profiles_dir, exist_ok=True)
        os.makedirs(self.medical_history_dir, exist_ok=True)

        # Load datasets
        self.health_data = self.load_health_dataset()
        self.hospitals_data = self.load_hospitals_dataset()
        self.symptoms_data = self.load_symptoms_data()

        # Setup UI
        self.create_styles()
        self.show_welcome_screen()

    def load_symptoms_data(self):
        """Load symptoms data from CSV file"""
        try:
            if os.path.exists("symptoms_data.csv"):
                df = pd.read_csv("symptoms_data.csv")
                # Convert empty strings to None for better handling
                df = df.replace('', None)
                return df
            return pd.DataFrame()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load symptoms data: {str(e)}")
            return pd.DataFrame()

    def create_styles(self):
        """Create custom widget styles"""
        self.style = ttk.Style()
        
        # Main style
        self.style.configure('.', background=BG_COLOR, foreground=TEXT_COLOR)
        
        # Notebook style
        self.style.configure('TNotebook', background=BG_COLOR)
        self.style.configure('TNotebook.Tab', 
                           background=SECONDARY_COLOR, 
                           foreground=TEXT_COLOR,
                           padding=[10, 5],
                           font=('Arial', 10, 'bold'))
        self.style.map('TNotebook.Tab', 
                     background=[('selected', PRIMARY_COLOR)],
                     foreground=[('selected', 'white')])
        
        # Button styles - updated to use black text
        self.style.configure('TButton', 
                           padding=6, 
                           font=('Arial', 10),
                           foreground=BUTTON_TEXT_COLOR)
        
        # Accent button style with black text
        self.style.configure('Accent.TButton', 
                           background=ACCENT_COLOR, 
                           foreground=BUTTON_TEXT_COLOR,
                           font=('Arial', 10, 'bold'))
        self.style.map('Accent.TButton',
                      background=[('active', DARK_ACCENT)],
                      foreground=[('active', BUTTON_TEXT_COLOR)],
                      font=[('active', ('Arial', 10, 'bold'))])
        
        # Emergency button style with black text
        self.style.configure('Emergency.TButton', 
                           background=EMERGENCY_COLOR, 
                           foreground=BUTTON_TEXT_COLOR,
                           font=('Arial', 12, 'bold'))
        self.style.map('Emergency.TButton',
                      background=[('active', '#cc0000')],
                      foreground=[('active', BUTTON_TEXT_COLOR)],
                      font=[('active', ('Arial', 12, 'bold'))])
        
        # LabelFrame style
        self.style.configure('TLabelframe', background=BG_COLOR)
        self.style.configure('TLabelframe.Label', 
                           background=BG_COLOR, 
                           foreground=PRIMARY_COLOR,
                           font=('Arial', 10, 'bold'))
        
        # Entry style
        self.style.configure('TEntry', fieldbackground='white', font=('Arial', 10))
        
        # Checkbutton style
        self.style.configure('Custom.TCheckbutton', background=BG_COLOR, font=('Arial', 10))
        
        # Treeview style
        self.style.configure('Treeview', 
                           background='white',
                           fieldbackground='white',
                           foreground=TEXT_COLOR,
                           font=('Arial', 10))
        self.style.configure('Treeview.Heading', 
                           background=PRIMARY_COLOR,
                           foreground='white',
                           font=('Arial', 10, 'bold'))
        self.style.map('Treeview', 
                      background=[('selected', SECONDARY_COLOR)])

    def analyze_symptoms(self):
        selected = [s for s, var in self.symptom_vars.items() if var.get()]
        severity = self.severity_var.get()
        
        if not selected:
            messagebox.showwarning("Warning", "Please select symptoms")
            return

        result = "=== HEALTH RECOMMENDATIONS ===\n\n"
        result += f"Analysis for: {', '.join(selected)}\n"
        result += f"Severity Level: {severity}\n\n"
        
        # First check the CSV data for symptoms
        csv_data_used = False
        for symptom in selected:
            if not self.symptoms_data.empty:
                csv_match = self.symptoms_data[self.symptoms_data['Symptom'].str.lower() == symptom.lower()]
                if not csv_match.empty:
                    csv_data_used = True
                    row = csv_match.iloc[0]
                    result += f"FOR {symptom.upper()} (from recorded data):\n"
                    if pd.notna(row['Condition']):
                        result += f"Possible Condition: {row['Condition']}\n"
                    if pd.notna(row['Severity']):
                        result += f"Recorded Severity: {row['Severity']}\n"
                    if pd.notna(row['Recommendation']):
                        result += f"Recommendation: {row['Recommendation']}\n"
                    if pd.notna(row['Notes']):
                        result += f"Notes: {row['Notes']}\n"
                    result += "\n"
        
        # Then add the standard recommendations
        for symptom in selected:
            data = self.medicine_db.get(symptom, {})
            
            # Only add header if we didn't already show CSV data for this symptom
            if not csv_data_used or symptom.lower() not in [s.lower() for s in self.symptoms_data['Symptom'].tolist()]:
                result += f"FOR {symptom.upper()}:\n"
            
            # Medicines
            if data.get('Medicines'):
                result += "💊 MEDICINES:\n"
                for med in data.get('Medicines', []):
                    result += f"- {med}\n"
            
            # Natural remedies
            if data.get('Natural'):
                result += "\n🌿 NATURAL REMEDIES:\n"
                for remedy in data.get('Natural', []):
                    result += f"- {remedy}\n"
            
            # Lifestyle
            if data.get('Lifestyle'):
                result += "\n🏡 LIFESTYLE TIPS:\n"
                for tip in data.get('Lifestyle', []):
                    result += f"- {tip}\n"
            
            # Severity specific advice
            if 'Severity' in data:
                result += f"\n⚠️ {severity.upper()} SEVERITY ADVICE:\n"
                result += f"- {data['Severity'].get(severity, 'Consult a doctor')}\n"
            
            result += "\n" + "="*50 + "\n\n"

        # Add WHO links for selected symptoms
        who_links = self.get_who_links(selected)
        if who_links:
            result += "🔗 RELEVANT WHO RESOURCES:\n"
            for title, link in who_links.items():
                result += f"- {title}: {link}\n"

        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, result)

    # [Rest of the methods remain unchanged...]

if __name__ == "__main__":
    root = tk.Tk()
    app = HealthAdvisorProPlus(root)
    
    # Center the window
    root.eval('tk::PlaceWindow . center')
    
    root.mainloop()
