import customtkinter as ctk
import json
import requests
import os
import base64
import queue
import tkinter as tk
import threading
from PIL import Image
import random
import sys

# Add the current directory to Python's path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Configure the appearance
ctk.set_appearance_mode("system")

# Custom color theme
ctk.set_default_color_theme("dark-blue")

# Define custom colors
ACTIVE_COLOR = "#1A1A1A"  # Almost black for active elements
BG_COLOR = "#2A2A2A"      # Dark gray background
TEXT_COLOR = "#FFFFFF"   # White text
BUTTON_COLOR = "#333333" # Slightly lighter gray for hover
INACTIVE_COLOR = "#404040" # Medium gray for inactive elements
HOVER_COLOR = "#333333"  # Dark gray for hover states

import webbrowser

class BacklinkManagerPro(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Initialize UI lock for thread-safe operations
        self.ui_lock = threading.Lock()

        # Initialize window
        self.title("Backlink Manager Pro")

        # Configure window
        self.title("Backlink Manager Pro")
        self.geometry("950x800")  # Increased width while maintaining height
        self.resizable(False, False)  # Prevent window resizing
        try:
            icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bm.ico")
            if os.path.exists(icon_path):
                self.iconbitmap(icon_path)
        except Exception as e:
            print(f"Warning: Could not load icon: {e}")
        self.configure(fg_color=BG_COLOR)
        
        # Load saved sites
        self.sites_file = "sites.json"
        self.backlinks_file = "backlinks.json"
        self.articles_file = "articles.json"
        
        # Initialize data storage
        self.sites = []
        self.backlinks = []
        self.articles = []
        
        # Load data from files
        self.load_sites()
        self.load_backlinks()
        self.load_articles()

        # Configure grid layout
        self.grid_columnconfigure(0, weight=1)  # Main content column
        self.grid_rowconfigure(0, weight=0)  # Top menu row
        self.grid_rowconfigure(1, weight=1)  # Main content row
        self.grid_rowconfigure(2, weight=0)  # Bottom branding row

        # Create top menu frame
        self.top_menu_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.top_menu_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.top_menu_frame.grid_columnconfigure((0,1,2,3,4), weight=1)

        # Create main frame
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_propagate(False)  # Prevent resizing

        # Create bottom branding frame
        self.bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.bottom_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        self.bottom_frame.grid_columnconfigure(0, weight=1)

        # Create frames for each section
        self.site_frame = ctk.CTkFrame(self.main_frame)
        self.backlink_frame = ctk.CTkFrame(self.main_frame)
        self.article_frame = ctk.CTkFrame(self.main_frame)
        self.process_frame = ctk.CTkFrame(self.main_frame)
        self.help_frame = None  # Initialize help_frame attribute

        # Configure all frames
        self.setup_site_frame()
        self.setup_backlink_frame()
        self.setup_article_frame()
        self.setup_process_frame()
        self.setup_help_frame()

        # Create menu buttons in top frame with icons
        self.site_menu_button = ctk.CTkButton(self.top_menu_frame, text="🌍 Site Yönetimi",
                                            command=self.show_site_frame,
                                            fg_color=ACTIVE_COLOR,
                                            hover_color=HOVER_COLOR,
                                            height=35, corner_radius=8,
                                            font=("Montserrat", 18),
                                            border_spacing=10)
        self.site_menu_button.grid(row=0, column=0, padx=5, pady=5)

        self.backlink_menu_button = ctk.CTkButton(self.top_menu_frame, text="🔗 Bağlantı Yönetimi",
                                                command=self.show_backlink_frame,
                                                fg_color=INACTIVE_COLOR,
                                                hover_color=HOVER_COLOR,
                                                height=35, corner_radius=8,
                                                font=("Montserrat", 18),
                                                border_spacing=10)
        self.backlink_menu_button.grid(row=0, column=1, padx=5, pady=5)

        self.article_menu_button = ctk.CTkButton(self.top_menu_frame, text="📝 Makale Ekle",
                                               command=self.show_article_frame,
                                               fg_color=INACTIVE_COLOR,
                                               hover_color=HOVER_COLOR,
                                               height=35, corner_radius=8,
                                               font=("Montserrat", 18),
                                               border_spacing=10)
        self.article_menu_button.grid(row=0, column=2, padx=5, pady=5)

        self.process_menu_button = ctk.CTkButton(self.top_menu_frame, text="🚀 Makale Gönder",
                                              command=self.show_process_frame,
                                              fg_color=INACTIVE_COLOR,
                                              hover_color=HOVER_COLOR,
                                              height=35, corner_radius=8,
                                              font=("Montserrat", 18),
                                              border_spacing=10)
        self.process_menu_button.grid(row=0, column=3, padx=5, pady=5)

        self.help_button = ctk.CTkButton(self.top_menu_frame, text="❓ Yardım ve Destek",
                                      command=self.show_help,
                                      fg_color=INACTIVE_COLOR,
                                      hover_color=HOVER_COLOR,
                                      height=35, corner_radius=8,
                                      font=("Montserrat", 18),
                                      border_spacing=10)
        self.help_button.grid(row=0, column=4, padx=5, pady=5)

        # Create company branding in bottom frame
        # Single line frame for all branding elements
        branding_frame = ctk.CTkFrame(self.bottom_frame, fg_color="transparent")
        branding_frame.pack(pady=5)

        # WebAdHere link
        company_link = ctk.CTkLabel(branding_frame, text="WebAdHere", text_color="#FFF", cursor="hand2")
        company_link.pack(side="left")
        company_link.bind("<Button-1>", lambda e: webbrowser.open("https://webadhere.com"))

        # Yazılım text
        yazilim_label = ctk.CTkLabel(branding_frame, text=" Yazılım ")
        yazilim_label.pack(side="left")

        # Product name
        product_label = ctk.CTkLabel(branding_frame, text="Backlink Manager Pro")
        product_label.pack(side="left")

        # Show site frame by default
        self.show_site_frame()
        
        # Initialize sites list with saved sites
        self.update_sites_list()

    def update_sites_list(self):
        # Clear existing widgets in sites frame
        for widget in self.sites_frame.winfo_children():
            widget.destroy()

        # Add sites
        for i, site in enumerate(self.sites):
            # Create frame for site row
            row_frame = ctk.CTkFrame(self.sites_frame, fg_color="transparent")
            row_frame.grid(row=i+1, column=0, columnspan=2, padx=10, pady=2, sticky="ew")
            row_frame.grid_columnconfigure(0, weight=3)
            row_frame.grid_columnconfigure(1, weight=1)

            # Show site URL
            url = site['url'][:50] + "..." if len(site['url']) > 50 else site['url']
            url_label = ctk.CTkLabel(row_frame, text=url, anchor="w")
            url_label.grid(row=0, column=0, padx=5, pady=2, sticky="w")

            # Delete button
            delete_button = ctk.CTkButton(row_frame, text="❌ Sil",
                                       command=lambda idx=i: self.delete_site(idx),
                                       fg_color=INACTIVE_COLOR, height=35, corner_radius=8,
                                       border_spacing=10)
            delete_button.grid(row=0, column=1, padx=5, pady=2, sticky="e")

    def load_sites(self):
        if not os.path.exists(self.sites_file):
            with open(self.sites_file, 'w') as f:
                json.dump([], f)
        try:
            with open(self.sites_file, 'r') as f:
                self.sites = json.load(f)
        except json.JSONDecodeError:
            self.sites = []
            self.save_sites()

    def load_backlinks(self):
        if not os.path.exists(self.backlinks_file):
            with open(self.backlinks_file, 'w') as f:
                json.dump([], f)
        try:
            with open(self.backlinks_file, 'r') as f:
                self.backlinks = json.load(f)
        except json.JSONDecodeError:
            self.backlinks = []
            self.save_backlinks()

    def load_articles(self):
        if not os.path.exists(self.articles_file):
            with open(self.articles_file, 'w') as f:
                json.dump([], f)
        try:
            with open(self.articles_file, 'r') as f:
                self.articles = json.load(f)
        except json.JSONDecodeError:
            self.articles = []
            self.save_articles()

    def save_sites(self):
        with open(self.sites_file, 'w') as f:
            json.dump(self.sites, f)

    def save_backlinks(self):
        with open(self.backlinks_file, 'w') as f:
            json.dump(self.backlinks, f)

    def save_articles(self):
        with open(self.articles_file, 'w') as f:
            json.dump(self.articles, f)

    def setup_backlink_frame(self):
        # Configure grid layout
        self.backlink_frame.grid_columnconfigure(0, weight=3)
        self.backlink_frame.grid_columnconfigure(1, weight=1)

        # Backlink frame title
        self.backlink_label = ctk.CTkLabel(self.backlink_frame, text="Bağlantı Yönetimi",
                                        font=ctk.CTkFont(size=16, weight="bold"))
        self.backlink_label.grid(row=0, column=0, columnspan=2, padx=10, pady=5)

        # Status message label for displaying errors and success messages
        self.backlink_status_label = ctk.CTkLabel(self.backlink_frame, text="",
                                        font=ctk.CTkFont(size=12),
                                        text_color="#FFFFFF",
                                        wraplength=600)
        self.backlink_status_label.grid(row=1, column=0, columnspan=2, padx=10, pady=5)

        # Input frame for URL and button
        input_frame = ctk.CTkFrame(self.backlink_frame, fg_color="transparent")
        input_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        input_frame.grid_columnconfigure(0, weight=3)
        input_frame.grid_columnconfigure(1, weight=1)

        # Backlink input field
        self.backlink_url_entry = ctk.CTkEntry(input_frame, placeholder_text="Site URL", 
                                            height=35, corner_radius=8)
        self.backlink_url_entry.grid(row=0, column=0, padx=(0,10), pady=5, sticky="ew")

        # Add backlink button
        self.add_backlink_button = ctk.CTkButton(input_frame, text="➕ Site Ekle", 
                                            command=self.add_backlink_url,
                                            fg_color=ACTIVE_COLOR, height=35, corner_radius=8,
                                            border_spacing=10)
        self.add_backlink_button.grid(row=0, column=1, pady=5, sticky="ew")

        # Backlinks list frame with scrolling
        self.backlinks_frame = ctk.CTkScrollableFrame(self.backlink_frame)
        self.backlinks_frame.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        self.backlinks_frame.grid_columnconfigure(0, weight=1)
        self.backlink_frame.grid_rowconfigure(3, weight=1)  # Make the list frame expand vertically

        # Update backlinks list
        self.update_backlinks_list()

    def setup_site_frame(self):
        # Configure grid layout for site frame
        self.site_frame.grid_columnconfigure(0, weight=1)  # Increased weight for URL column
        self.site_frame.grid_columnconfigure(1, weight=1)
        self.site_frame.grid_columnconfigure(2, weight=1)
        self.site_frame.grid_columnconfigure(3, weight=1)

        self.site_label = ctk.CTkLabel(self.site_frame, text="Site Yönetimi",
                                      font=ctk.CTkFont(size=16, weight="bold"))
        self.site_label.grid(row=0, column=0, columnspan=4, padx=10, pady=5, sticky="n")

        # Status message label for displaying errors and success messages
        self.status_label = ctk.CTkLabel(self.site_frame, text="",                                        font=ctk.CTkFont(size=12),
                                        text_color="#FFFFFF",
                                        wraplength=600)
        self.status_label.grid(row=1, column=0, columnspan=4, padx=10, pady=5)

        # Site input fields with enhanced styling
        self.site_url_entry = ctk.CTkEntry(self.site_frame, placeholder_text="Site URL", height=35, corner_radius=8, width=250)
        self.site_url_entry.grid(row=2, column=0, padx=10, pady=5, sticky="ew")

        self.username_entry = ctk.CTkEntry(self.site_frame, placeholder_text="Kullanıcı Adı", height=35, corner_radius=8, width=250)
        self.username_entry.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

        self.password_entry = ctk.CTkEntry(self.site_frame, placeholder_text="Şifre", show="*", height=35, corner_radius=8, width=250)
        self.password_entry.grid(row=2, column=2, padx=10, pady=5, sticky="ew")

        self.add_site_button = ctk.CTkButton(self.site_frame, text="➕ Site Ekle", command=self.add_site, 
                                    fg_color=ACTIVE_COLOR, height=35, corner_radius=8,
                                    border_spacing=10)
        self.add_site_button.grid(row=2, column=3, padx=10, pady=5)

        # Sites list frame with scrolling
        self.sites_frame = ctk.CTkScrollableFrame(self.site_frame)
        self.sites_frame.grid(row=3, column=0, columnspan=4, padx=10, pady=10, sticky="nsew")
        self.sites_frame.grid_columnconfigure(0, weight=1)
        self.site_frame.grid_rowconfigure(3, weight=1)  # Make the list frame expand vertically

    def add_site(self):
        # Get site details from entry fields
        url = self.site_url_entry.get().strip()
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        # Validate input fields
        if not url or not username or not password:
            self.status_label.configure(text="❌ Lütfen tüm alanları doldurun!", text_color="#FF0000")
            return

        # Ensure URL starts with http:// or https://
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url

        # Remove trailing slash if present
        url = url.rstrip('/')

        # Check if site already exists
        for site in self.sites:
            if site['url'] == url:
                self.status_label.configure(text="❌ Bu site zaten eklenmiş!", text_color="#FF0000")
                return

        try:
            import requests
            from urllib.parse import urlparse

            # First check if the domain is accessible
            parsed_url = urlparse(url)
            try:
                response = requests.get(f"{parsed_url.scheme}://{parsed_url.netloc}", timeout=10)
                response.raise_for_status()
            except requests.exceptions.Timeout:
                self.status_label.configure(text="❌ Site bağlantısı zaman aşımına uğradı! Lütfen internet bağlantınızı kontrol edin.", text_color="#FF0000")
                return
            except requests.exceptions.ConnectionError:
                self.status_label.configure(text="❌ Site bağlantısı başarısız! Lütfen internet bağlantınızı ve URL'yi kontrol edin.", text_color="#FF0000")
                return
            except requests.exceptions.RequestException as e:
                self.status_label.configure(text=f"❌ Site erişilebilir değil! Hata: {str(e)}", text_color="#FF0000")
                return

            # Check if the Backlink Manager API plugin is installed and working
            auth_url = f"{url}/wp-json/backlink-manager/v1/auth"
            try:
                # Update status to show progress
                self.status_label.configure(text="✓ Backlink Manager API kontrol ediliyor...", text_color="#00FF00")
                
                # Authenticate with the plugin
                auth_data = {
                    'username': username,
                    'password': password
                }
                
                auth_response = requests.post(auth_url, json=auth_data, timeout=10)
                auth_response.raise_for_status()
                
                # Get the authentication token
                auth_token = auth_response.json().get('token')
                if not auth_token:
                    raise ValueError("Authentication token not received")
                
                # Add new site with authentication token
                new_site = {
                    'url': url,
                    'username': username,
                    'auth_token': auth_token,
                    'api_type': 'backlink-manager'
                }

                self.sites.append(new_site)
                self.save_sites()
                self.update_sites_list()

                # Clear input fields
                self.site_url_entry.delete(0, 'end')
                self.username_entry.delete(0, 'end')
                self.password_entry.delete(0, 'end')

                # Show success message
                self.status_label.configure(text="✅ Site başarıyla eklendi! (Backlink Manager API)", text_color="#00FF00")
                
            except requests.exceptions.Timeout:
                self.status_label.configure(text="❌ API bağlantısı zaman aşımına uğradı!", text_color="#FF0000")
                return
            except requests.exceptions.ConnectionError:
                self.status_label.configure(text="❌ API bağlantısı başarısız! Backlink Manager API eklentisi kurulu değil.", text_color="#FF0000")
                return
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 401:
                    self.status_label.configure(text="❌ Kullanıcı adı veya şifre hatalı!", text_color="#FF0000")
                elif e.response.status_code == 403:
                    self.status_label.configure(text="❌ Bu işlem için yönetici yetkisi gereklidir!", text_color="#FF0000")
                else:
                    self.status_label.configure(text=f"❌ API hatası: {e.response.status_code}", text_color="#FF0000")
                return
            except ValueError as e:
                self.status_label.configure(text=f"❌ API yanıtı geçersiz: {str(e)}", text_color="#FF0000")
                return
            except Exception as e:
                self.status_label.configure(text=f"❌ Beklenmeyen bir hata oluştu: {str(e)}", text_color="#FF0000")
                return

        except Exception as e:
            self.status_label.configure(text=f"❌ Beklenmeyen bir hata oluştu: {str(e)}", text_color="#FF0000")
            # Clear input fields on error
            self.site_url_entry.delete(0, 'end')
            self.username_entry.delete(0, 'end')
            self.password_entry.delete(0, 'end')
            return

    def setup_article_frame(self):
        # Configure grid layout for article frame
        self.article_frame.grid_columnconfigure(0, weight=1)
        self.article_frame.grid_columnconfigure(1, weight=1)
        self.article_frame.grid_columnconfigure(2, weight=1)

        # Article frame title
        self.article_label = ctk.CTkLabel(self.article_frame, text="Makale Ekle",
                                      font=ctk.CTkFont(size=16, weight="bold"))
        self.article_label.grid(row=0, column=0, columnspan=3, padx=10, pady=5)

        # Status message label for displaying errors and success messages
        self.article_status_label = ctk.CTkLabel(self.article_frame, text="",
                                        font=ctk.CTkFont(size=12),
                                        text_color="#FFFFFF",
                                        wraplength=600)
        self.article_status_label.grid(row=1, column=0, columnspan=3, padx=10, pady=5)

        # Title input field
        self.title_label = ctk.CTkLabel(self.article_frame, text="Makale Başlığı (Spintax Olarak Girin)")
        self.title_label.grid(row=2, column=1, padx=10, pady=(10,0), sticky="w")
        
        self.title_entry = ctk.CTkTextbox(self.article_frame, height=60, width=800)
        self.title_entry.grid(row=3, column=1, padx=10, pady=(0,10), sticky="ew")

        # Content input field
        self.content_label = ctk.CTkLabel(self.article_frame, text="Makale İçeriği (Spintax Olarak Girin)")
        self.content_label.grid(row=4, column=1, padx=10, pady=(10,0), sticky="w")
        
        self.content_entry = ctk.CTkTextbox(self.article_frame, height=250, width=800)
        self.content_entry.grid(row=5, column=1, padx=10, pady=(0,10), sticky="ew")

        # Variation counter
        self.variation_label = ctk.CTkLabel(self.article_frame, 
                                        text="Maksimum Üretilebilir Makale: 0",
                                        font=ctk.CTkFont(size=12))
        self.variation_label.grid(row=6, column=1, padx=10, pady=5)

        # Button frame for preview and image URL input
        self.button_frame = ctk.CTkFrame(self.article_frame, fg_color="transparent")
        self.button_frame.grid(row=7, column=1, padx=10, pady=10)
        
        # Top row frame
        top_row_frame = ctk.CTkFrame(self.button_frame, fg_color="transparent")
        top_row_frame.grid(row=0, column=0, padx=5, pady=(0, 10))
        
        # Preview button
        self.preview_article_button = ctk.CTkButton(top_row_frame, text="Makale Önizle",
                                               command=self.preview_article,
                                               fg_color=ACTIVE_COLOR, height=35, corner_radius=8,
                                               border_spacing=10)
        self.preview_article_button.grid(row=0, column=0, padx=5)
        
        # Multi-image button
        self.multi_image_button = ctk.CTkButton(top_row_frame, text="Görsel Ekle",
                                            command=self.show_image_panel,
                                            fg_color=ACTIVE_COLOR, height=35, corner_radius=8,
                                            border_spacing=10)
        self.multi_image_button.grid(row=0, column=1, padx=5)

        # Initialize image URLs list
        self.image_urls = []

        # Image panel (initially hidden)
        self.image_panel = None

        # Bottom row frame
        bottom_row_frame = ctk.CTkFrame(self.button_frame, fg_color="transparent")
        bottom_row_frame.grid(row=1, column=0, padx=5)

        # Article count input frame
        article_count_frame = ctk.CTkFrame(bottom_row_frame, fg_color="transparent")
        article_count_frame.grid(row=0, column=0, padx=5)
        
        # Article count label
        article_count_label = ctk.CTkLabel(article_count_frame, text="Üretilecek Makale:")
        article_count_label.grid(row=0, column=0, padx=(0, 5))
        
        # Article count entry
        self.article_count_entry = ctk.CTkEntry(article_count_frame, width=60, height=35)
        self.article_count_entry.grid(row=0, column=1)

        # Backlink count frame
        backlink_count_frame = ctk.CTkFrame(bottom_row_frame, fg_color="transparent")
        backlink_count_frame.grid(row=0, column=1, padx=5)
        
        # Backlink count label
        backlink_count_label = ctk.CTkLabel(backlink_count_frame, text="Makale Başına Bağlantı:")
        backlink_count_label.grid(row=0, column=0, padx=(0, 5))
        
        # Backlink count entry
        self.backlink_per_content_entry = ctk.CTkEntry(backlink_count_frame, width=60, height=35)
        self.backlink_per_content_entry.grid(row=0, column=1)
        self.backlink_per_content_entry.insert(0, "1")  # Default value
        self.article_count_entry.insert(0, "5")  # Default value

        # Save button (renamed to Generate Article)
        self.save_article_button = ctk.CTkButton(bottom_row_frame, text="Makale Üret",
                                             command=self.generate_articles,
                                             fg_color=ACTIVE_COLOR, height=35, corner_radius=8,
                                             border_spacing=10)
        self.save_article_button.grid(row=0, column=2, padx=5)

        # Initialize current article index
        self.current_article_index = None

        # Set initial variation label text
        self.variation_label.configure(text="Maksimum Üretilebilir Makale: 0")

        # Bind text change events
        self.title_entry.bind("<<Modified>>", self.on_text_change)
        self.content_entry.bind("<<Modified>>", self.on_text_change)

    def calculate_spintax_variations(self, text):
        if not text:
            return 1
        
        import time
        import traceback
        
        # Start time to track processing duration
        start_time = time.time()
        
        # Remove hard limits but keep track of large numbers
        variations = 1
        stack = []
        current_options = 1
        
        try:
            for i in range(len(text)):
                # Add a small delay every 1000 characters to prevent freezing
                if i > 0 and i % 1000 == 0:
                    time.sleep(0.01)  # 10ms delay every 1000 characters
                
                if i >= len(text):
                    break
                    
                char = text[i]
                
                if char == '{':
                    stack.append(current_options)
                    current_options = 1
                elif char == '|':
                    current_options += 1
                elif char == '}':
                    if stack:
                        # Still prevent integer overflow but with a much higher limit
                        if variations > 1e15 / current_options:  # Use scientific notation for very large number
                            return 1e15  # Return a very large number instead of hard limit
                        variations *= current_options
                        current_options = stack.pop()
                
                # Still check for unbalanced brackets but with higher threshold
                if len(stack) > 200:  # Increased threshold for malformed spintax detection
                    print("Warning: Potentially malformed spintax detected (too many nested brackets)")
                    return 1e15  # Return a very large number
            
            # Add a small delay at the end based on how many variations we found
            if variations > 1000:
                time.sleep(0.05)  # 50ms delay for large variation counts
                
        except Exception as e:
            print(f"Error calculating spintax variations: {str(e)}")
            traceback.print_exc()
            return 1  # Return safe default on error
        
        # Handle unbalanced brackets
        if stack:
            print(f"Warning: Unbalanced brackets in spintax - {len(stack)} unclosed brackets")
        
        # Format large numbers for display
        processing_time = time.time() - start_time
        print(f"Calculated {self.format_number(variations)} variations in {processing_time:.2f} seconds")
        return variations

    def calculate_spintax_variations(self, text):
        # Count variations in spintax
        if not text:
            return 0

        stack = []
        variations = 1
        current_options = 1

        for char in text:
            if char == '{':
                stack.append(current_options)
                current_options = 1
            elif char == '|':
                current_options += 1
            elif char == '}':
                if stack:
                    variations *= current_options
                    current_options = stack.pop()

        return max(1, variations)

    def format_number(self, number):
        if number < 1000:
            return str(number)
        elif number < 1000000:
            return f"{number/1000:.0f} Bin"
        elif number < 1000000000:
            return f"{number/1000000:.1f} Milyon"
        elif number < 1000000000000:
            return f"{number/1000000000:.1f} Milyar"
        elif number < 1000000000000000:
            return f"{number/1000000000000:.1f} Trilyon"
        elif number < 1000000000000000000:
            return f"{number/1000000000000000:.1f} Katrilyon"
        elif number < 1000000000000000000000:
            return f"{number/1000000000000000000:.1f} Kentilyon"
        else:
            return f"{number/1000000000000000000000:.1f} Sekstilyon"

    def on_text_change(self, event=None):
        # Get current content
        title = self.title_entry.get("1.0", "end-1c")
        content = self.content_entry.get("1.0", "end-1c")
        
        # Calculate variations
        try:
            if title.strip() and content.strip():
                title_variations = self.calculate_spintax_variations(title)
                content_variations = self.calculate_spintax_variations(content)
                total_variations = title_variations * content_variations
                
                formatted_number = self.format_number(total_variations)
                self.variation_label.configure(text=f"Maksimum Üretilebilir Makale: {formatted_number}")
            else:
                self.variation_label.configure(text="Maksimum Üretilebilir Makale: 0")
        except Exception as e:
            print(f"Error updating variation count: {str(e)}")
            self.variation_label.configure(text="Maksimum Üretilebilir Makale: Hesaplanamadı")
            
        # Reset the modified flag
        if hasattr(event, 'widget'):
            event.widget.edit_modified(False)

    # Otomatik kaydetme sistemi kullanıldığı için bu fonksiyon artık kullanılmıyor

    def clear_article_inputs(self):
        self.title_entry.delete("1.0", "end")
        self.content_entry.delete("1.0", "end")
        self.variation_label.configure(text="Maksimum Üretilebilir Makale: 0")
        self.current_article_index = None  # Reset current article index

    def show_article_status(self, message, is_error=False):
        self.article_status_label.configure(text=message)
        if is_error:
            self.article_status_label.configure(text_color="#FF0000")
        else:
            self.article_status_label.configure(text_color="#00FF00")

    def process_spintax(self, text):
        if not text:
            return text
        
        import re
        import random
        import traceback
        import time
        
        # Start time to track processing duration
        start_time = time.time()
        
        # Improved pattern to handle nested spintax better
        pattern = r'\{([^{}]*)\}'
        
        def replace(match):
            try:
                options = match.group(1).split('|')
                if not options:
                    return ""
                return random.choice(options)
            except Exception as e:
                # Return empty string on error to prevent crashes
                print(f"Replace error: {str(e)}")
                return ""
        
        # Remove hard iteration limit but keep track of iterations
        iteration_count = 0
        last_text = None
        
        try:
            # Use cached regex object for more efficient processing
            pattern_compiled = re.compile(pattern)
            
            # Continue processing as long as there are matches
            while pattern_compiled.search(text):
                # Add small delay every 5 iterations to prevent freezing
                if iteration_count > 0 and iteration_count % 5 == 0:
                    time.sleep(0.01)  # 10ms delay every 5 iterations
                    
                # Store last text to detect if we're stuck
                last_text = text
                
                # Process one match at a time
                try:
                    text = pattern_compiled.sub(replace, text, count=1)
                except Exception as sub_error:
                    print(f"Regex substitution error: {str(sub_error)}")
                    break
                
                # Check if text changed, if not, we might be stuck
                if text == last_text:
                    print("Spintax processing stuck - text not changing")
                    break
                    
                iteration_count += 1
                
                # Add longer delay for very high iteration counts
                if iteration_count > 100:
                    time.sleep(0.05)  # 50ms delay after 100 iterations
            
            # Log the number of iterations for monitoring
            if iteration_count > 50:
                print(f"High number of iterations in spintax processing: {iteration_count}")
                
            # Sanitize output to remove any unprocessed spintax
            # This ensures we don't return malformed content
            if '{' in text and '}' in text:
                text = pattern_compiled.sub('', text)
                
            return text
        except Exception as e:
            # Catch any exceptions to prevent crashes
            print(f"Error in spintax processing: {str(e)}")
            traceback.print_exc()
            # Return sanitized text if processing fails
            return text.replace('{', '').replace('}', '').replace('|', ' ')
        

    def preview_article(self):
        title = self.title_entry.get("1.0", "end-1c").strip()
        content = self.content_entry.get("1.0", "end-1c").strip()

        if not title or not content:
            self.show_article_status("❌ Başlık ve içerik alanları boş olamaz!", True)
            return
            
        self._show_preview_window(title, content)
        
    def generate_limited_articles(self):
        title = self.title_entry.get("1.0", "end-1c").strip()
        content = self.content_entry.get("1.0", "end-1c").strip()

        if not title or not content:
            self.show_article_status("❌ Başlık ve içerik alanları boş olamaz!", True)
            return
            
        try:
            # Get the number of articles to generate from the entry field
            article_count = int(self.article_count_entry.get().strip())
            if article_count <= 0:
                self.show_article_status("❌ Makale sayısı 1 veya daha büyük olmalıdır!", True)
                return
                
            # Create a window to display generated articles
            articles_window = ctk.CTkToplevel(self)
            articles_window.title(f"{article_count} Makale Oluşturuldu")
            articles_window.geometry("800x600")
            
            # Create a notebook for tabbed interface
            notebook = ctk.CTkTabview(articles_window)
            notebook.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Generate the specified number of articles
            for i in range(article_count):
                # Create a new tab for each article
                tab_name = f"Makale {i+1}"
                notebook.add(tab_name)
                
                # Create a scrollable frame for the article content
                article_frame = ctk.CTkScrollableFrame(notebook.tab(tab_name))
                article_frame.pack(fill="both", expand=True, padx=5, pady=5)
                
                # Process the spintax to generate a unique variation
                processed_title = self.process_spintax(title)
                processed_content = self.process_spintax(content)
                
                # Title label
                title_label = ctk.CTkLabel(article_frame, text="Başlık:", font=ctk.CTkFont(size=14, weight="bold"))
                title_label.pack(anchor="w", pady=(0, 5))
                
                # Processed title
                article_title = ctk.CTkLabel(article_frame, text=processed_title,
                                        font=ctk.CTkFont(size=16), wraplength=700)
                article_title.pack(anchor="w", pady=(0, 15))
                
                # Content label
                content_label = ctk.CTkLabel(article_frame, text="Makale:", font=ctk.CTkFont(size=14, weight="bold"))
                content_label.pack(anchor="w", pady=(0, 5))
                
                # Processed content
                article_content = ctk.CTkLabel(article_frame, text=processed_content,
                                         font=ctk.CTkFont(size=12), wraplength=700, justify="left")
                article_content.pack(anchor="w", pady=(0, 15))
                
                # Save button for each article
                def save_article_factory(title, content):
                    def save_article():
                        new_article = {
                            'title': title,
                            'content': content,
                            'variations': self.calculate_spintax_variations(title) * self.calculate_spintax_variations(content)
                        }
                        self.articles.append(new_article)
                        self.save_articles()
                        self.show_article_status(f"✅ Makale başarıyla kaydedildi! (Makale {len(self.articles)})", False)
                    return save_article
                
                save_button = ctk.CTkButton(article_frame, text="Bu Makaleyi Kaydet",
                                         command=save_article_factory(processed_title, processed_content),
                                         fg_color=ACTIVE_COLOR, height=35, corner_radius=8)
                save_button.pack(pady=10)
                
            # Button to save all articles at once
            save_all_frame = ctk.CTkFrame(articles_window, fg_color="transparent")
            save_all_frame.pack(pady=10)
            
            def save_all_articles():
                saved_count = 0
                for i in range(article_count):
                    tab_name = f"Makale {i+1}"
                    # Get the title and content from the labels in each tab
                    tab = notebook.tab(tab_name)
                    # This is a simplified approach - in a real implementation you'd need to store the processed text
                    # Here we're just generating new variations
                    processed_title = self.process_spintax(title)
                    processed_content = self.process_spintax(content)
                    
                    new_article = {
                        'title': processed_title,
                        'content': processed_content,
                        'variations': self.calculate_spintax_variations(title) * self.calculate_spintax_variations(content)
                    }
                    self.articles.append(new_article)
                    saved_count += 1
                
                self.save_articles()
                # Clear input fields after saving all articles
                self.clear_article_inputs()
                self.show_article_status(f"✅ {saved_count} makale başarıyla kaydedildi!", False)
                articles_window.destroy()
            
            save_all_button = ctk.CTkButton(save_all_frame, text="Tüm Makaleleri Kaydet",
                                         command=save_all_articles,
                                         fg_color=ACTIVE_COLOR, height=35, corner_radius=8)
            save_all_button.pack()
            
        except ValueError:
            self.show_article_status("❌ Geçerli bir makale sayısı giriniz!", True)
        except Exception as e:
            self.show_article_status(f"❌ Bir hata oluştu: {str(e)}", True)

    def preview_saved_article(self, article):
        title = article['title']
        content = article['content']
        self._show_preview_window(title, content)

    def _show_preview_window(self, title, content):
        # Create preview window
        preview_window = ctk.CTkToplevel(self)
        preview_window.title("Makale Önizleme")
        preview_window.geometry("900x900")

        # Create scrollable frame
        preview_frame = ctk.CTkScrollableFrame(preview_window)
        preview_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Title label
        title_label = ctk.CTkLabel(preview_frame, text="Başlık:", font=ctk.CTkFont(size=14, weight="bold"))
        title_label.pack(anchor="w", pady=(0, 5))

        # Processed title
        processed_title = ctk.CTkLabel(preview_frame, text=self.process_spintax(title),
                                    font=ctk.CTkFont(size=16), wraplength=850)
        processed_title.pack(anchor="w", pady=(0, 15))

        # Content label
        content_label = ctk.CTkLabel(preview_frame, text="Makale:", font=ctk.CTkFont(size=14, weight="bold"))
        content_label.pack(anchor="w", pady=(0, 5))

        # Processed content
        processed_content = ctk.CTkLabel(preview_frame, text=self.process_spintax(content),
                                     font=ctk.CTkFont(size=12), wraplength=850, justify="left")
        processed_content.pack(anchor="w", pady=(0, 15))

        # Regenerate button
        def regenerate():
            processed_title.configure(text=self.process_spintax(title))
            processed_content.configure(text=self.process_spintax(content))

        regenerate_button = ctk.CTkButton(preview_frame, text="Tekrar Oluştur",
                                       command=regenerate,
                                       fg_color=ACTIVE_COLOR, height=35, corner_radius=8)
        self.start_button.grid(row=5, column=0, padx=10, pady=10)

        # Update article list
        self.update_article_list()
        regenerate_button.pack(pady=10)

    def setup_process_frame(self):
        # Configure grid layout
        self.process_frame.grid_columnconfigure(0, weight=1)
        self.process_frame.configure(fg_color=BG_COLOR)

        # Process frame title
        self.process_label = ctk.CTkLabel(self.process_frame, text="Üretilen Makaleleri Gönder",
                                      font=ctk.CTkFont(size=16, weight="bold"))
        self.process_label.grid(row=0, column=0, padx=10, pady=5)

        # Initialize selected article index
        self.selected_article_index = None

        # Settings buttons with dark theme
        self.settings_frame = ctk.CTkFrame(self.process_frame)
        self.settings_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

        # Example settings buttons
        self.backup_button = ctk.CTkButton(self.settings_frame, text="Yedekleme",
                                       fg_color=ACTIVE_COLOR,
                                       hover_color=HOVER_COLOR,
                                       height=35, corner_radius=8)
        self.backup_button.grid(row=0, column=0, padx=10, pady=5)

        self.restore_button = ctk.CTkButton(self.settings_frame, text="Geri Yükleme",
                                        fg_color=ACTIVE_COLOR,
                                        hover_color=HOVER_COLOR,
                                        height=35, corner_radius=8)
        self.restore_button.grid(row=1, column=0, padx=10, pady=5)

        self.settings_button = ctk.CTkButton(self.settings_frame, text="Genel Ayarlar",
                                         fg_color=ACTIVE_COLOR,
                                         hover_color=HOVER_COLOR,
                                         height=35, corner_radius=8)
        self.settings_button.grid(row=2, column=0, padx=10, pady=5)

        # Create saved articles frame
        saved_articles_frame = ctk.CTkFrame(self.process_frame)
        saved_articles_frame.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")
        saved_articles_frame.grid_columnconfigure(0, weight=1)
        self.process_frame.grid_rowconfigure(2, weight=3)  # Give more weight to the saved articles row

        # Add title for saved articles
        # Create a frame to hold the title and buttons
        title_frame = ctk.CTkFrame(saved_articles_frame, fg_color="transparent")
        title_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        title_frame.grid_columnconfigure(0, weight=1)  # Title takes most space
        title_frame.grid_columnconfigure(1, weight=0)  # Counter takes minimal space
        title_frame.grid_columnconfigure(2, weight=0)  # Button takes minimal space
        
        # Title label
        saved_articles_title = ctk.CTkLabel(title_frame, text="Üretilen Makaleler",
                                        font=ctk.CTkFont(size=14))
        saved_articles_title.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        # Article counter
        self.article_counter = ctk.CTkLabel(title_frame,
                                        text=f"{len(self.articles)}",
                                        font=ctk.CTkFont(size=14))
        self.article_counter.grid(row=0, column=1, padx=5, pady=5)
        
        # Delete all button
        delete_all_button = ctk.CTkButton(title_frame, text="❌ Hepsini Sil",
                                      command=self.delete_all_articles,
                                      fg_color=ACTIVE_COLOR, height=25, corner_radius=6,
                                      hover_color=HOVER_COLOR, width=80)
        delete_all_button.grid(row=0, column=2, padx=5, pady=5, sticky="e")

        # Create scrollable frame for articles with dark background
        self.saved_articles_scroll = ctk.CTkScrollableFrame(saved_articles_frame, fg_color="transparent", height=400)
        self.saved_articles_scroll.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        saved_articles_frame.grid_rowconfigure(1, weight=1)

        # Create settings frame
        settings_frame = ctk.CTkFrame(self.process_frame)
        settings_frame.grid(row=3, column=0, padx=10, pady=5, sticky="nsew")
        settings_frame.grid_columnconfigure(1, weight=1)

        # Fixed thread count (removed slider)

        # Content per site input and Backlinks per content input (side by side)
        content_settings_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        content_settings_frame.grid(row=1, column=0, columnspan=3, padx=10, pady=5, sticky="ew")
        content_settings_frame.grid_columnconfigure(1, weight=1)
        content_settings_frame.grid_columnconfigure(3, weight=1)
        content_settings_frame.grid_columnconfigure(5, weight=1)

        content_per_site_label = ctk.CTkLabel(content_settings_frame, text="Site Başına Makale Sayısı:", anchor="w")
        content_per_site_label.grid(row=0, column=0, padx=(0,10), pady=5, sticky="w")

        self.content_per_site_entry = ctk.CTkEntry(content_settings_frame, width=100)
        self.content_per_site_entry.grid(row=0, column=1, padx=(0,20), pady=5, sticky="w")
        self.content_per_site_entry.insert(0, "1")

        content_status_label = ctk.CTkLabel(content_settings_frame, text="Makale Durumu:", anchor="w")
        content_status_label.grid(row=0, column=2, padx=(0,10), pady=5, sticky="w")

        self.content_status_var = ctk.StringVar(value="publish")
        
        status_frame = ctk.CTkFrame(content_settings_frame, fg_color="transparent")
        status_frame.grid(row=0, column=3, padx=0, pady=5, sticky="w")
        
        publish_radio = ctk.CTkRadioButton(status_frame, text="Yayınla", variable=self.content_status_var, value="publish")
        publish_radio.grid(row=0, column=0, padx=(0, 10))
        
        draft_radio = ctk.CTkRadioButton(status_frame, text="Taslak", variable=self.content_status_var, value="draft")
        draft_radio.grid(row=0, column=1)

        # Create progress bar and status label but don't display them initially
        self.progress_bar = ctk.CTkProgressBar(self.process_frame)
        self.progress_bar.set(0)
        
        self.progress_label = ctk.CTkLabel(self.process_frame, text="")
        
        self.process_status_label = ctk.CTkLabel(self.process_frame, text="", wraplength=600)

        # Start button
        self.start_button = ctk.CTkButton(self.process_frame, text="Makale Göndermeyi Başlat",
                                      command=self.start_article_generation,
                                      fg_color=ACTIVE_COLOR, height=35, corner_radius=8,
                                      border_spacing=10)
        self.start_button.grid(row=8, column=0, padx=10, pady=10)

        # Update article list
        self.update_article_list()

    # Thread slider functionality removed

    def update_article_list(self):
        # Clear existing widgets in saved articles scroll frame
        for widget in self.saved_articles_scroll.winfo_children():
            widget.destroy()

        # Update article counter
        if hasattr(self, 'article_counter'):
            self.article_counter.configure(text=f"Listede {len(self.articles)} Makale Bulunuyor")

        # Initialize pagination variables if not exists
        if not hasattr(self, 'current_page'):
            self.current_page = 0
        if not hasattr(self, 'articles_per_page'):
            self.articles_per_page = 50

        # Calculate total pages
        total_pages = (len(self.articles) + self.articles_per_page - 1) // self.articles_per_page

        # Get current page articles
        start_idx = self.current_page * self.articles_per_page
        end_idx = min(start_idx + self.articles_per_page, len(self.articles))
        current_articles = self.articles[start_idx:end_idx]

        # Add articles for current page
        for i, article in enumerate(current_articles):
            # Create frame for article row with dark background
            row_frame = ctk.CTkFrame(self.saved_articles_scroll, fg_color="transparent")
            row_frame.grid(row=i, column=0, padx=5, pady=1, sticky="ew")
            row_frame.grid_columnconfigure(0, weight=1)
            row_frame.grid_columnconfigure(1, weight=0)

            # Show article title with reduced height - extended length
            title = article['title'][:150] + "..." if len(article['title']) > 150 else article['title']
            title_label = ctk.CTkLabel(row_frame, text=title, anchor="w", height=25)
            title_label.grid(row=0, column=0, padx=5, pady=1, sticky="w")

            # Create frame for buttons with transparent background
            button_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
            button_frame.grid(row=0, column=1, padx=(0, 10), pady=1, sticky="e")

            # Delete button with reduced height and padding
            delete_button = ctk.CTkButton(button_frame, text="❌ Sil",
                                       command=lambda idx=start_idx+i: self.delete_article(idx),
                                       fg_color=ACTIVE_COLOR, height=25, corner_radius=6,
                                       hover_color=HOVER_COLOR, width=50)
            delete_button.grid(row=0, column=1, padx=(0, 5), pady=1)

        # Add pagination controls if there are multiple pages
        if total_pages > 1:
            pagination_frame = ctk.CTkFrame(self.saved_articles_scroll, fg_color="transparent")
            pagination_frame.grid(row=len(current_articles), column=0, padx=5, pady=10, sticky="ew")
            pagination_frame.grid_columnconfigure((0,1,2), weight=1)

            # Previous page button
            prev_button = ctk.CTkButton(pagination_frame, text="←",
                                    command=lambda: self.change_page(-1),
                                    fg_color=ACTIVE_COLOR, height=25, corner_radius=6,
                                    hover_color=HOVER_COLOR, width=50,
                                    state="normal" if self.current_page > 0 else "disabled")
            prev_button.grid(row=0, column=0, padx=5, pady=5)

            # Page indicator
            page_label = ctk.CTkLabel(pagination_frame,
                                   text=f"Sayfa {self.current_page + 1}/{total_pages}")
            page_label.grid(row=0, column=1, padx=5, pady=5)

            # Next page button
            next_button = ctk.CTkButton(pagination_frame, text="→",
                                    command=lambda: self.change_page(1),
                                    fg_color=ACTIVE_COLOR, height=25, corner_radius=6,
                                    hover_color=HOVER_COLOR, width=50,
                                    state="normal" if self.current_page < total_pages - 1 else "disabled")
            next_button.grid(row=0, column=2, padx=5, pady=5)

    def generate_articles(self):
        # Prevent multiple generations
        if hasattr(self, 'generation_thread') and self.generation_thread.is_alive():
            self.article_status_label.configure(text="⚠️ Makale üretimi zaten devam ediyor!", text_color="#FFA500")
            return

        # Initialize message queue and thread control flag
        self.generation_queue = queue.Queue()
        self.is_generating = True

        # Disable UI elements during generation
        self.disable_ui_elements()
        
        try:
            # Start article generation in a separate thread with proper cleanup
            self.generation_thread = threading.Thread(target=self._generate_articles_worker)
            self.generation_thread.daemon = True
            self.generation_thread.start()
            
            # Start UI update loop with proper cleanup
            self.update_generation_ui()
        except Exception as e:
            self.article_status_label.configure(text=f"❌ Makale üretimi başlatılamadı: {str(e)}", text_color="#FF0000")
            self.enable_ui_elements()
            self.is_generating = False
            if hasattr(self, 'generation_queue'):
                del self.generation_queue

    def _generate_articles_worker(self):
        try:
            # Get article count and content within try block to handle UI access errors
            try:
                article_count = int(self.article_count_entry.get())
                title = self.title_entry.get("1.0", "end-1c")
                content = self.content_entry.get("1.0", "end-1c")
                backlinks_per_article = int(self.backlink_per_content_entry.get())
            except Exception as e:
                raise ValueError(f"UI erişim hatası: {str(e)}")

            # Validate inputs
            if not title or not content:
                raise ValueError("Başlık ve içerik alanları boş olamaz!")
            if article_count < 1:
                raise ValueError("Geçerli bir makale sayısı giriniz!")
            if backlinks_per_article < 0:
                raise ValueError("Geçerli bir bağlantı sayısı giriniz!")
            if backlinks_per_article > 0 and not self.backlinks:
                raise ValueError("Bağlantı eklemek için önce bağlantı listesine site eklemelisiniz!")

            # Generate articles with proper thread safety
            for i in range(article_count):
                if not self.is_generating:
                    break

                try:
                    # First process the spintax content
                    processed_content = self.process_spintax(content)
                    processed_title = self.process_spintax(title)
                    
                    # Add a single random image at the beginning of content if available
                    if self.image_urls:
                        # Select one random image URL from the pool
                        random_image_url = random.choice(self.image_urls)
                        # Generate image tag without alt attribute
                        image_tag = '<img src="{}" style="max-width:100%;height:auto;">'.format(random_image_url)
                        processed_content = image_tag + '\n\n' + processed_content
                    
                    # Process content and add backlinks if needed
                    if backlinks_per_article > 0 and self.backlinks:
                        # Split content into paragraphs
                        paragraphs = [p for p in processed_content.split('\n\n') if p.strip()]
                        
                        # Get random backlinks
                        selected_backlinks = random.sample(self.backlinks, min(backlinks_per_article, len(self.backlinks)))
                        
                        for backlink in selected_backlinks:
                            if not paragraphs:  # Skip if no valid paragraphs
                                continue
                                
                            # Select a random paragraph
                            paragraph_idx = random.randint(0, len(paragraphs) - 1)
                            paragraph = paragraphs[paragraph_idx]
                            
                            # Split into words and filter valid ones
                            words = paragraph.split()
                            valid_words = [i for i, word in enumerate(words) 
                                         if len(word) > 3 
                                         and word.isalnum() 
                                         and not any(tag in word for tag in ['<a', '</a>', '<img', '<p', '<div'])]
                            
                            if valid_words:  # Only proceed if we found valid words
                                # Select a random word
                                word_idx = random.choice(valid_words)
                                word = words[word_idx]
                                
                                # Create the hyperlink - handle both dictionary and string formats
                                if isinstance(backlink, dict) and 'url' in backlink:
                                    backlink_url = backlink['url']
                                else:
                                    backlink_url = str(backlink)
                                words[word_idx] = f'<a href="{backlink_url}" target="_blank" rel="nofollow">{word}</a>'
                                
                                # Update the paragraph
                                paragraphs[paragraph_idx] = ' '.join(words)
                        
                        # Rejoin the paragraphs
                        processed_content = '\n\n'.join(paragraphs)

                    # Create new article with processed content
                    new_article = {
                        'title': processed_title,
                        'content': processed_content,
                        'image_urls': self.image_urls.copy() if self.image_urls else []
                    }

                    # Add article and save with proper locking
                    with self.ui_lock:
                        if not self.is_generating:
                            break
                        self.articles.append(new_article)
                        self.save_articles()
                        # Update progress through queue
                        progress = f"✓ {i + 1}/{article_count} makale üretildi..."
                        self.generation_queue.put(("progress", progress))

                except Exception as e:
                    self.generation_queue.put(("error", f"Makale üretim hatası: {str(e)}"))
                    break

            # Clear input fields only if generation completed successfully
            if self.is_generating:
                self.generation_queue.put(("clear_inputs", None))
                self.generation_queue.put(("success", f"✅ {article_count} makale başarıyla üretildi!"))

        except ValueError as e:
            self.generation_queue.put(("error", str(e)))
        except Exception as e:
            self.generation_queue.put(("error", f"Beklenmeyen hata: {str(e)}"))
        finally:
            self.is_generating = False

    def update_generation_ui(self):
        if not self.is_generating:
            return

        try:
            # Process all available messages with proper error handling
            while True:
                try:
                    msg_type, msg_value = self.generation_queue.get_nowait()
                    
                    if msg_type == "error":
                        self.article_status_label.configure(text=f"❌ {msg_value}", text_color="#FF0000")
                        self.is_generating = False
                        self.enable_ui_elements()
                        return
                    elif msg_type == "progress":
                        self.article_status_label.configure(text=msg_value, text_color="#00FF00")
                    elif msg_type == "success":
                        self.article_status_label.configure(text=msg_value, text_color="#00FF00")
                        self.is_generating = False
                        self.enable_ui_elements()
                        return
                    elif msg_type == "clear_inputs":
                        self.title_entry.delete("1.0", "end")
                        self.content_entry.delete("1.0", "end")
                        self.image_urls = []
                        
                except queue.Empty:
                    break
                except Exception as e:
                    # Log UI update errors but continue processing
                    print(f"UI update error: {str(e)}")
                    continue

            # Schedule next update if still generating
            if self.is_generating:
                self.after(100, self.update_generation_ui)

        except Exception as e:
            self.article_status_label.configure(text=f"❌ UI güncelleme hatası: {str(e)}", text_color="#FF0000")
            self.is_generating = False
            self.enable_ui_elements()

    def disable_ui_elements(self):
        # Disable all interactive elements during article generation
        self.title_entry.configure(state="disabled")
        self.content_entry.configure(state="disabled")
        self.article_count_entry.configure(state="disabled")
        self.backlink_per_content_entry.configure(state="disabled")
        self.preview_article_button.configure(state="disabled")
        self.multi_image_button.configure(state="disabled")
        self.site_menu_button.configure(state="disabled")
        self.backlink_menu_button.configure(state="disabled")
        self.article_menu_button.configure(state="disabled")
        self.process_menu_button.configure(state="disabled")
        self.help_button.configure(state="disabled")

    def enable_ui_elements(self):
        # Re-enable all interactive elements after article generation
        self.title_entry.configure(state="normal")
        self.content_entry.configure(state="normal")
        self.article_count_entry.configure(state="normal")
        self.backlink_per_content_entry.configure(state="normal")
        self.preview_article_button.configure(state="normal")
        self.multi_image_button.configure(state="normal")
        self.site_menu_button.configure(state="normal")
        self.backlink_menu_button.configure(state="normal")
        self.article_menu_button.configure(state="normal")
        self.process_menu_button.configure(state="normal")
        self.help_button.configure(state="normal")

    def generate_articles(self):
        # Import required modules
        import threading
        import queue
        
        # Initialize generation queue for thread-safe communication
        self.generation_queue = queue.Queue()
        self.is_generating = True
        
        # Get article details
        title = self.title_entry.get("1.0", "end-1c").strip()
        content = self.content_entry.get("1.0", "end-1c").strip()

        # Validate input fields
        if not title or not content:
            self.article_status_label.configure(text="❌ Lütfen tüm alanları doldurun!", text_color="#FF0000")
            return

        # Disable UI elements during generation
        self.save_article_button.configure(state="disabled")
        self.article_status_label.configure(text="⏳ Makaleler üretiliyor...", text_color="#FFFFFF")

        # Start the worker thread
        worker_thread = threading.Thread(target=self._generate_articles_worker, daemon=True)
        worker_thread.start()

        # Update UI based on queue messages
        def update_ui():
            try:
                while True:
                    try:
                        msg_type, msg_value = self.generation_queue.get_nowait()
                        
                        if msg_type == "progress":
                            self.article_status_label.configure(text=msg_value, text_color="#00FF00")
                        elif msg_type == "error":
                            self.article_status_label.configure(text=msg_value, text_color="#FF0000")
                            self.save_article_button.configure(state="normal")
                            return
                        elif msg_type == "success":
                            self.article_status_label.configure(text=msg_value, text_color="#00FF00")
                            self.save_article_button.configure(state="normal")
                            return
                        elif msg_type == "clear_inputs":
                            self.title_entry.delete("1.0", "end")
                            self.content_entry.delete("1.0", "end")
                            self.image_urls = []
                            
                    except queue.Empty:
                        break
                        
                if self.is_generating:
                    self.after(100, update_ui)
                    
            except Exception as e:
                self.article_status_label.configure(
                    text=f"❌ UI güncelleme hatası: {str(e)}",
                    text_color="#FF0000"
                )
                self.save_article_button.configure(state="normal")
        
        # Start UI updates
        update_ui()

    def change_page(self, direction):
        # Update current page
        total_pages = (len(self.articles) + self.articles_per_page - 1) // self.articles_per_page
        new_page = self.current_page + direction
        
        # Ensure page is within valid range
        if 0 <= new_page < total_pages:
            self.current_page = new_page
            self.update_article_list()

    def delete_article(self, index):
        # Remove article from list
        self.articles.pop(index)
        self.save_articles()
        # Reset to first page when deleting
        self.current_page = 0
        self.update_article_list()
        
    def delete_all_articles(self):
        # Remove all articles
        self.articles = []
        self.save_articles()
        self.update_article_list()
        self.process_status_label.configure(text="✅ Tüm makaleler başarıyla silindi!", text_color="#00FF00")

    def start_article_generation(self):
        # Import required modules
        import queue
        import random
        import threading
        import time
        import requests

        # Get the number of articles to generate
        try:
            content_per_site = int(self.content_per_site_entry.get())
            if content_per_site < 1:
                self.process_status_label.configure(text="❌ Geçerli sayılar giriniz!", text_color="#FF0000")
                return
        except ValueError:
            self.process_status_label.configure(text="❌ Geçerli sayılar giriniz!", text_color="#FF0000")
            return

        if not self.articles:
            self.process_status_label.configure(text="❌ Önce içerik eklemelisiniz!", text_color="#FF0000")
            return

        if not self.sites:
            self.process_status_label.configure(text="❌ Önce site eklemelisiniz!", text_color="#FF0000")
            return

        # Check if already running
        if hasattr(self, 'is_generating') and self.is_generating:
            self.is_generating = False
            self.start_button.configure(text="Makale Göndermeyi Başlat", fg_color=ACTIVE_COLOR)
            self.process_status_label.configure(text="✓ Makale gönderme durduruldu", text_color="#00FF00")
            return

        # Validate inputs
        try:
            content_per_site = int(self.content_per_site_entry.get())
            if content_per_site < 1:
                raise ValueError
        except ValueError:
            self.process_status_label.configure(text="❌ Geçerli sayılar giriniz!", text_color="#FF0000")
            return

        if not self.articles:
            self.process_status_label.configure(text="❌ Önce içerik eklemelisiniz!", text_color="#FF0000")
            return

        if not self.sites:
            self.process_status_label.configure(text="❌ Önce site eklemelisiniz!", text_color="#FF0000")
            return

        # Initialize UI and processing state
        self.is_generating = True
        self.start_button.configure(text="Makale Göndermeyi Durdur", fg_color="#FF4444")
        message_queue = queue.Queue()
        
        # Show progress bar and label
        self.progress_bar.grid(row=6, column=0, padx=10, pady=5, sticky="ew")
        self.progress_label.grid(row=7, column=0, padx=10, pady=5)
        self.process_status_label.grid(row=5, column=0, padx=10, pady=5)
        
        # Calculate total articles to be posted
        total_articles = len(self.sites) * content_per_site
        self.progress_bar.set(0)
        self.progress_label.configure(text=f"Makaleler gönderiliyor... 0/{total_articles}")
        
        # Thread-safe resources
        articles_lock = threading.Lock()
        processed_articles = 0

        def post_article(site):
            nonlocal processed_articles
            if not self.is_generating:
                return False

            try:
                # Select random article
                with articles_lock:
                    if not self.articles:
                        raise ValueError("No articles available")
                    article = random.choice(self.articles)

                # Prepare article data
                post_data = {
                    'title': article['title'],
                    'content': article['content'],
                    'status': self.content_status_var.get()
                }

                # Send request to WordPress
                headers = {'Authorization': f'Bearer {site["auth_token"]}'}
                response = requests.post(
                    f"{site['url']}/wp-json/backlink-manager/v1/posts",
                    json=post_data,
                    headers=headers,
                    timeout=30
                )
                response.raise_for_status()

                # Update progress
                with articles_lock:
                    processed_articles += 1
                    progress = processed_articles / total_articles
                    message_queue.put(('progress', progress))
                    message_queue.put(('status', [f"✓ Makale gönderildi: {article['title'][:50]}...", "#00FF00"]))

                return True

            except Exception as e:
                message_queue.put(('status', [f"❌ {site['url']} için hata: {str(e)}", "#FF0000"]))
                return False

        def update_ui():
            try:
                if not self.is_generating:
                    return

                # Process all available messages
                while True:
                    try:
                        msg_type, msg_value = message_queue.get_nowait()
                        if msg_type == 'progress':
                            self.progress_bar.set(msg_value)
                            self.progress_label.configure(text=f"Makaleler gönderiliyor... {processed_articles}/{total_articles}")
                        elif msg_type == 'status':
                            self.process_status_label.configure(text=msg_value[0], text_color=msg_value[1])
                    except queue.Empty:
                        break

            except Exception as e:
                print(f"UI update error: {str(e)}")
            finally:
                if self.is_generating:
                    self.after(100, update_ui)
                else:
                    self.after(0, lambda: self.start_button.configure(text="Makale Göndermeyi Başlat", fg_color=ACTIVE_COLOR))

        # Start UI updates
        update_ui()

        # Create and start worker threads
        def worker_thread():
            try:
                for _ in range(content_per_site):
                    if not self.is_generating:
                        break
                    for site in self.sites:
                        if not self.is_generating:
                            break
                        try:
                            post_article(site)
                            time.sleep(0.5)  # Small delay between posts
                        except Exception as e:
                            message_queue.put(('status', [f"❌ Makale gönderme hatası: {str(e)}", "#FF0000"]))
                            continue
            except Exception as e:
                message_queue.put(('status', [f"❌ İşlem hatası: {str(e)}", "#FF0000"]))
            finally:
                self.is_generating = False
                message_queue.put(('status', [f"✅ İşlem tamamlandı! {processed_articles} makale gönderildi.", "#00FF00"]))

        # Start worker thread with proper exception handling
        try:
            self.worker_thread = threading.Thread(target=worker_thread)
            self.worker_thread.daemon = True
            self.worker_thread.start()
        except Exception as e:
            self.is_generating = False
            self.process_status_label.configure(text=f"❌ Thread başlatma hatası: {str(e)}", text_color="#FF0000")
            self.start_button.configure(text="Makale Göndermeyi Başlat", fg_color=ACTIVE_COLOR)

        # Calculate total work for posting phase
        start_time = time.time()

        # Thread-safe resources with improved management
        lock = threading.Lock()
        articles_lock = threading.Lock()
        backlinks_lock = threading.Lock()
        
        # Add a semaphore to limit concurrent API requests - use actual thread count
        request_semaphore = threading.Semaphore(max(1, thread_count))  # Use full thread count

        # Initialize the processed_articles counter
        processed_articles = 0

        def update_progress():
            nonlocal processed_articles
            try:
                with lock:
                    processed_articles += 1
                    progress = processed_articles / total_articles
                    if not self.is_generating:
                        return False

                    # Only queue updates, don't update UI directly from worker thread
                    message_queue.put(('progress', progress))
                    message_queue.put(('progress_label', f"İşleniyor... {processed_articles}/{total_articles}"))
                    return True
            except Exception as e:
                message_queue.put(('status', [f"❌ İlerleme güncellemesi hatası: {str(e)}", "#FF0000"]))
                return False

        def update_ui():
            if not self.is_generating:
                return
            try:
                # Process all available messages in the queue
                messages_processed = 0
                max_messages_per_update = 10  # Limit messages processed per update
                
                while messages_processed < max_messages_per_update:
                    try:
                        msg_type, msg_value = message_queue.get_nowait()
                        messages_processed += 1
                        
                        # Only process progress updates, ignore status messages
                        if msg_type == 'progress':
                            self.progress_bar.set(msg_value)
                        elif msg_type == 'progress_label':
                            # Process but don't display progress label updates
                            pass
                        elif msg_type == 'status':
                            # Ignore status messages
                            pass
                    except queue.Empty:
                        break
                    except Exception as e:
                        # Silently handle errors
                        continue
                
                # Batch update the UI
                self.update()
                
            except Exception as e:
                try:
                    self.process_status_label.configure(text=f"❌ UI Güncelleme Hatası: {str(e)}", text_color="#FF0000")
                    self.update()
                except:
                    pass
            finally:
                if self.is_generating:
                    # Schedule next update with shorter interval for smoother progress
                    self.after(10, update_ui)

        # Start UI updates
        update_ui()

        # Backlink insertion is now done during article generation in save_current_article

        def process_site(site):
            try:
                # Set timeout for entire process
                start_time = time.time()
                timeout = 30  # 30 second timeout
                
                # Get random article with proper error handling
                with articles_lock:
                    if time.time() - start_time > timeout:
                        raise TimeoutError("Article processing timeout")
                    if not self.articles:
                        raise ValueError("Makale bulunamadı")
                    article = random.choice(self.articles)

                # Get the already processed title and content (no spintax processing needed)
                try:
                    if time.time() - start_time > timeout:
                        raise TimeoutError("Article processing timeout")
                    
                    # Use the already processed title and content directly
                    title = article.get('title', '')
                    content = article.get('content', '')
                    
                    # Update UI to show current processing status
                    message_queue.put(('status', [f"✓ Makale gönderiliyor: {title[:50]}...", "#00FF00"]))
                    self.update_idletasks()
                    
                    # Validate content
                    if not title or len(title) < 5:
                        raise ValueError("Başlık hatası: Başlık çok kısa veya boş")
                    if not content or len(content) < 50:
                        raise ValueError("İçerik hatası: İçerik çok kısa veya boş")
                        
                except TimeoutError as e:
                    message_queue.put(('status', ["⚠️ Makale işleme zaman aşımı", "#FFA500"]))
                    raise
                except Exception as e:
                    raise ValueError(f"Makale işleme hatası: {str(e)}")

                # Backlinks are already added during article generation
                message_queue.put(('status', ["✓ Makale backlinkleri ile birlikte gönderiliyor", "#00FF00"]))
                self.update_idletasks()

                # Update progress after each major step
                if not update_progress():
                    return
                
                self.update_idletasks()
                return True

            except Exception as e:
                message_queue.put(('status', [f"❌ İşlem hatası: {str(e)}", "#FF0000"]))
                self.update_idletasks()
                return False

                # Handle image upload if available - using image path from article
                featured_image_id = None
                try:
                    # Get image path from article
                    image_path = article.get('featured_image_path')
                    if image_path:
                            # Import libraries at the beginning to avoid repeated imports
                            import base64, os
                            from PIL import Image
                            import io
                            
                            try:
                                # Optimize image before uploading
                                img = Image.open(image_path)
                                
                                # Resize large images to reduce upload size
                                max_size = (1200, 1200)  # Maximum dimensions
                                if img.width > max_size[0] or img.height > max_size[1]:
                                    img.thumbnail(max_size, Image.LANCZOS)
                                
                                # Convert to RGB if needed (in case of RGBA or other modes)
                                if img.mode != 'RGB':
                                    img = img.convert('RGB')
                                
                                # Save optimized image to memory buffer
                                buffer = io.BytesIO()
                                img.save(buffer, format='JPEG', quality=85, optimize=True)
                                buffer.seek(0)
                                img_data = buffer.read()
                                
                                # Convert image to base64
                                img_base64 = base64.b64encode(img_data).decode('utf-8')
                                
                                # Get image filename
                                img_name = os.path.basename(image_path)
                                
                                # Upload image to WordPress with semaphore to limit concurrent requests
                                with request_semaphore:
                                    headers = {'Authorization': f'Bearer {site["auth_token"]}'}                            
                                    image_data = {
                                        'image_data': f'data:image/jpeg;base64,{img_base64}',
                                        'image_name': img_name
                                    }
                                    
                                    # Send image upload request with reduced timeout
                                    upload_response = requests.post(
                                        f"{site['url']}/wp-json/backlink-manager/v1/upload-image",
                                        json=image_data,
                                        headers=headers,
                                        timeout=20  # Reduced timeout
                                    )
                                    upload_response.raise_for_status()
                                    
                                    # Get the uploaded image ID
                                    upload_result = upload_response.json()
                                    featured_image_id = upload_result.get('id')
                                    
                                    message_queue.put(('status', [f"✓ Görsel başarıyla yüklendi: {img_name}", "#00FF00"]))
                            except Exception as img_error:
                                message_queue.put(('status', [f"⚠️ Görsel işleme hatası: {str(img_error)}", "#FFA500"]))
                except Exception as e:
                    # Log error but continue without image rather than failing
                    message_queue.put(('status', [f"⚠️ Görsel yükleme uyarısı: {str(e)}", "#FFA500"]))
                
                # Create post data
                post_data = {
                    'title': title,
                    'content': content,
                    'status': self.content_status_var.get(),
                    'featured_image_id': featured_image_id
                }

                # Send request to WordPress using semaphore to limit concurrent requests
                try:
                    # Use semaphore to limit concurrent API requests
                    with request_semaphore:
                        headers = {'Authorization': f'Bearer {site["auth_token"]}'}
                        # Reduce timeout from 30 to 15 seconds to fail faster
                        # Create a session with retry capability
                        session = requests.Session()
                        from requests.adapters import HTTPAdapter
                        from urllib3.util.retry import Retry
                        
                        # Configure optimized retry strategy
                        retries = Retry(
                            total=3,  # Arttırılmış yeniden deneme sayısı
                            backoff_factor=1,  # Daha uzun bekleme süresi
                            status_forcelist=[429, 500, 502, 503, 504],  # 429 (rate limit) eklendi
                            allowed_methods=["POST"],  # Only retry POST requests
                            respect_retry_after_header=True  # Sunucunun retry-after başlığına uy
                        )
                        
                        # Apply retry strategy to session with optimized connection pool
                        adapter = HTTPAdapter(max_retries=retries, pool_connections=10, pool_maxsize=10)
                        session.mount('http://', adapter)
                        session.mount('https://', adapter)
                        
                        # Optimize request headers
                        headers['Connection'] = 'keep-alive'
                        headers['Accept'] = 'application/json'
                        headers['Content-Type'] = 'application/json'
                        
                        # Send request with retry capability and optimized timeout
                        response = session.post(
                            f"{site['url']}/wp-json/backlink-manager/v1/posts",
                            json=post_data,
                            headers=headers,
                            timeout=12  # Daha kısa zaman aşımı süresi
                        )
                        response.raise_for_status()
                        
                        # Dinamik bekleme süresi - sunucu yükü yüksekse daha uzun bekle
                        if response.status_code == 201 or response.status_code == 200:
                            # Başarılı yanıt - kısa bekleme
                            time.sleep(0.3)
                        else:
                            # Diğer başarılı yanıtlar - biraz daha uzun bekle
                            time.sleep(0.7)
                except requests.exceptions.Timeout:
                    raise ValueError("WordPress bağlantı zaman aşımı - sunucu yanıt vermiyor")
                except requests.exceptions.ConnectionError:
                    raise ValueError("WordPress bağlantı hatası - internet bağlantınızı kontrol edin")
                except requests.exceptions.HTTPError as e:
                    if hasattr(e, 'response') and e.response is not None:
                        status_code = e.response.status_code
                        if status_code == 401:
                            raise ValueError("WordPress API yetkilendirme hatası - token geçersiz")
                        elif status_code >= 500:
                            raise ValueError(f"WordPress sunucu hatası: {status_code}")
                        else:
                            raise ValueError(f"WordPress API hatası: {status_code}")
                    else:
                        raise ValueError(f"WordPress API hatası: {str(e)}")
                except requests.exceptions.RequestException as e:
                    raise ValueError(f"WordPress API hatası: {str(e)}")

                # Update progress
                if not update_progress():
                    return False

                return True

            except ValueError as e:
                message_queue.put(('status', [f"❌ {str(e)}", "#FF0000"]))
                return False
            except Exception as e:
                import traceback
                traceback.print_exc()
                message_queue.put(('status', [f"❌ Beklenmeyen hata: {str(e)}", "#FF0000"]))
                return False

        # Create thread pool with proper exception handling and resource management
        def process_with_timeout(site):
            try:
                # Add timeout to prevent hanging threads
                result = None
                import threading
                import time
                import ctypes
                import traceback
                import queue
                from contextlib import contextmanager
                
                @contextmanager
                def timeout_context(timeout):
                    # Use a proper approach for timeout that doesn't rely on thread.interrupt
                    timer = threading.Timer(timeout, lambda: None)  # Just a placeholder timer
                    timer.start()
                    try:
                        yield
                    finally:
                        timer.cancel()
                
                # Thread-local error queue with size limit
                error_queue = queue.Queue(maxsize=5)
                
                # Create thread with proper resource management
                def thread_target():
                    nonlocal result
                    try:
                        # Use a simpler approach without the problematic timeout_context
                        result = process_site(site)
                    except Exception as e:
                        error_message = str(e)
                        traceback.print_exc()
                        try:
                            error_queue.put_nowait(error_message)
                        except queue.Full:
                            pass
                        result = False
                    finally:
                        # Ensure resources are released
                        try:
                            with request_semaphore:
                                pass
                        except:
                            pass
                
                # Create and start thread with resource limits
                thread = threading.Thread(target=thread_target)
                thread.daemon = True
                
                start_time = time.time()
                thread.start()
                
                # Wait with timeout and proper cleanup
                thread.join(timeout=20)
                
                if thread.is_alive():
                    elapsed_time = time.time() - start_time
                    message_queue.put(('status', [f"⚠️ İşlem zaman aşımı ({elapsed_time:.1f}s)", "#FFA500"]))
                    return False
                
                # Check for errors with timeout
                try:
                    error_message = error_queue.get_nowait()
                    message_queue.put(('status', [f"⚠️ İşlem hatası: {error_message}", "#FFA500"]))
                    return False
                except queue.Empty:
                    pass
                    
                return result if result is not None else False
                
            except Exception as e:
                traceback.print_exc()
                message_queue.put(('status', [f"⚠️ Beklenmeyen hata: {str(e)}", "#FFA500"]))
                return False
                
        # Use a safer approach with ThreadPoolExecutor
        executor = None
        futures = []
        try:
            # Use the exact thread count specified by the user
            max_workers = thread_count
            executor = ThreadPoolExecutor(max_workers=max_workers)
            
            # Submit tasks for each site and content combination
            futures = []
            for site in self.sites:
                for _ in range(content_per_site):
                    if not self.is_generating:
                        break
                    futures.append(executor.submit(process_with_timeout, site))
                    
            # Update status to show that tasks have been submitted
            message_queue.put(('status', [f"✓ {len(futures)} makale oluşturma görevi başlatıldı ({max_workers} iş parçacığı ile)", "#00FF00"]))
            message_queue.put(('progress_label', f"İşleniyor... 0/{total_articles}"))
            self.update_idletasks()

            # Wait for all tasks to complete with timeout
            import concurrent.futures
            try:
                # Use as_completed with timeout to prevent hanging
                completed_count = 0
                total_count = len(futures)
                
                # Set a reasonable timeout based on the number of tasks
                overall_timeout = min(30 + (total_count * 10), 300)  # Between 30s and 5min
                
                # Update UI immediately to show we're starting to process
                message_queue.put(('progress', 0.01))  # Show a small progress to indicate start
                message_queue.put(('status', [f"✓ İşleniyor: 0/{total_count} tamamlandı", "#00FF00"]))
                self.update_idletasks()
                
                for future in concurrent.futures.as_completed(futures, timeout=overall_timeout):
                    try:
                        # Reduced individual timeout for better responsiveness
                        result = future.result(timeout=15)  
                        completed_count += 1
                        
                        # Update progress after each completion
                        progress = completed_count / total_count
                        message_queue.put(('progress', progress))
                        message_queue.put(('progress_label', f"İşleniyor... {completed_count}/{total_count}"))
                        
                        # Calculate elapsed time
                        elapsed_time = time.time() - start_time
                        
                        # Update status more frequently for better feedback
                        if completed_count % 1 == 0 or completed_count == total_count:  # Update every completion
                            message_queue.put(('status', [f"✓ İşleniyor: {completed_count}/{total_count} tamamlandı", "#00FF00"]))
                            
                        # Force UI update more frequently
                        if completed_count % 1 == 0:  # Update UI after each completion
                            self.update_idletasks()
                    except concurrent.futures.TimeoutError:
                        message_queue.put(('status', [f"⚠️ Bir işlem zaman aşımına uğradı, devam ediliyor", "#FFA500"]))
                        self.update_idletasks()
                    except Exception as e:
                        import traceback
                        traceback.print_exc()
                        message_queue.put(('status', [f"⚠️ Hata: {str(e)}, devam ediliyor", "#FFA500"]))
                        self.update_idletasks()
            except concurrent.futures.TimeoutError:
                message_queue.put(('status', [f"⚠️ İşlemler zaman aşımına uğradı, kalan işlemler iptal ediliyor", "#FFA500"]))
            except Exception as e:
                import traceback
                traceback.print_exc()
                message_queue.put(('status', [f"❌ Beklenmeyen hata: {str(e)}", "#FF0000"]))
        finally:
            # Ensure proper cleanup of executor and futures
            if futures:
                # Cancel any remaining futures
                for future in futures:
                    if not future.done():
                        future.cancel()
            
            # Shutdown executor properly
            if executor:
                try:
                    # Shutdown with a short timeout to prevent hanging
                    executor.shutdown(wait=True, cancel_futures=True)
                except Exception as e:
                    message_queue.put(('status', [f"⚠️ Executor kapatma hatası: {str(e)}", "#FFA500"]))

        # Calculate elapsed time and update final status
        elapsed_time = time.time() - start_time
        hours, remainder = divmod(elapsed_time, 3600)
        minutes, seconds = divmod(remainder, 60)

        if self.is_generating:
            message_queue.put(('status', [
                f"✅ İşlem tamamlandı!\nGönderilen Makale: {processed_posts}\nSüre: {int(hours)}s {int(minutes)}d {int(seconds)}s",
                "#00FF00"
            ]))
            message_queue.put(('progress', 1.0))  # Ensure progress bar shows 100%
            message_queue.put(('progress_label', f"Tamamlandı! {processed_posts}/{total_articles}"))
            
            # Force update UI
            self.update_idletasks()
            
        # Reset state
        self.is_generating = False
        self.start_button.configure(text="Makale Oluşturmayı Başlat", fg_color=ACTIVE_COLOR)
        self.update_idletasks()  # Force button update

    # Image handling is now done through URL input

    def add_backlink_url(self):
        # Get backlink URL from entry field
        url = self.backlink_url_entry.get().strip()

        # Validate input field
        if not url:
            self.backlink_status_label.configure(text="❌ Lütfen site URL'sini girin!", text_color="#FF0000")
            return

        # Ensure URL starts with http:// or https://
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url

        # Remove trailing slash if present
        url = url.rstrip('/')

        # Check if backlink already exists
        if url in self.backlinks:
            self.backlink_status_label.configure(text="❌ Bu site zaten eklenmiş!", text_color="#FF0000")
            return

        # Add new backlink as a dictionary with url key
        self.backlinks.append({'url': url})
        self.save_backlinks()
        self.update_backlinks_list()

        # Clear input field
        self.backlink_url_entry.delete(0, 'end')

        # Show success message
        self.backlink_status_label.configure(text="✅ Site başarıyla eklendi!", text_color="#00FF00")

    def setup_help_frame(self):
        # Define helper functions for buttons
        def open_email():
            webbrowser.open("mailto:info@webadhere.com")
            
        def open_whatsapp():
            webbrowser.open("https://wa.me/905411710315")

        def reset_all_data():
            self.sites = []
            self.backlinks = []
            self.articles = []
            self.save_sites()
            self.save_backlinks()
            self.save_articles()
            self.update_sites_list()
            self.update_backlinks_list()
            self.show_help()

        # Configure help frame
        self.help_frame = ctk.CTkFrame(self.main_frame)
        self.help_frame.grid(row=0, column=0, sticky="nsew")
        self.help_frame.grid_columnconfigure(0, weight=1)
        self.help_frame.grid_rowconfigure(1, weight=1)  # Make scrollable frame expand

        # Title
        title_label = ctk.CTkLabel(self.help_frame, text="Yardım ve Destek",
                                font=ctk.CTkFont(size=16, weight="bold"))
        title_label.grid(row=0, column=0, padx=10, pady=5)

        # Create scrollable frame for help content
        help_scroll = ctk.CTkScrollableFrame(self.help_frame)
        help_scroll.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        help_scroll.grid_columnconfigure(0, weight=1)

        # Button frame
        button_frame = ctk.CTkFrame(help_scroll, fg_color="transparent")
        button_frame.grid(row=1, column=0, padx=10, pady=10)

        # Reset button
        reset_button = ctk.CTkButton(button_frame, text="Programı Sıfırla",
                                  command=reset_all_data,
                                  fg_color="#750000", height=35, corner_radius=8)
        reset_button.grid(row=0, column=0, padx=5, pady=10)

        # Mail button
        mail_button = ctk.CTkButton(button_frame, text="Mail",
                                    command=open_email,
                                    fg_color="#2196F3", height=35, corner_radius=8)
        mail_button.grid(row=0, column=1, padx=5, pady=10)

        # WhatsApp button
        whatsapp_button = ctk.CTkButton(button_frame, text="WhatsApp",
                                    command=open_whatsapp,
                                    fg_color="#25D366", height=35, corner_radius=8)
        whatsapp_button.grid(row=0, column=2, padx=5, pady=10)

        # Help sections
        sections = [
                        ("Program Güvenliği ve Kullanımı", """
Program Güvenlik Özellikleri:
- Program verilerinizi dışarıya aktarmaz, veriler sadece kurulu olduğu bilgisayarda saklanır.
- Sadece Windows 10 ve 11 üzerinde, internet erişimi ile sağlıklı çalışır.

Dosya Yönetimi:
- Program dosyalarını (sites.json, backlinks.json, articles.json) silmeyin.
- En iyi performans için programı bir klasör içinde çalıştırın.
- Düzenli yedekleme yapmanız önerilir.

WordPress Güvenliği:
- Backlink Manager API eklentisini WordPress sitenize yükleyin ve etkinleştirin.
- Program üzerinden siteyi eklerken API eklentisini kullanarak bağlantıyı sağlayın.
- Site bağlantısını kaldırmak için program üzerinden silebilir ve 'Backlink Manager API' eklentisini devre dışı bırakabilirsiniz.
"""),    

            ("WordPress Site Ekleme", """
1. WordPress sitenizin yönetici paneline giriş yapın.
2. Eklentiler > Yeni Eklenti Ekle > Eklenti Yükle
3. Backlink Manager API eklentisini yükleyin.
4. Site URL'nizi, kullanıcı adınızı ve şifrenizi Backlink Manager Pro'da kullanın.
5. Birden fazla WordPress sitenizi ekleyebilirsiniz.
"""),

            ("Spintax Makale Oluşturma", """
1. Makaleniz yoksa ChatGPT veya Claude gibi bir yapay zeka aracını kullanarak makalenizi oluşturun.
2. Daha sonra yapay zeka aracına makaleniz için spintax formatı oluşturmasını isteyin.
             
    Yapay zekadan spintax makale oluşturma örneği:
    "Lütfen bu makaleyi spintax formatında yaz."

3. Makaleniz spintax formatında aşağıdaki gibi olacaktır:
             
   - Benzer anlamlı kelimeler {kelime1|kelime2|kelime3} şeklinde,
   - Farklı cümle yapıları {cümle1|cümle2|cümle3} şeklinde.
             
4. Her makale için saniyeler içerisinde trilyonlarca farklı varyasyon oluşturabilirsiniz.
5. Her varyasyon özgün ve benzersiz içerik sağlar.
6. Program her makaleye seçtiğiniz linkleri ve görselleri ekler.

Örnek:
{Merhaba|Selam|Hey}, {nasılsın|bugün nasıl gidiyor|nasıl gidiyor}?
"""),

            ("Maksimum Üretilebilir Makale", """
Maksimum üretilebilir makale sayısı, spintax içeriğinizdeki tüm olası kombinasyonların sayısıdır.

Hesaplama örneği:
{A|B|C} {D|E} = 3 x 2 = 6 farklı kombinasyon

Örnek makale:
{Merhaba|Selam} {dostlar|arkadaşlar} = 2 x 2 = 4 farklı kombinasyon
1. Merhaba dostlar
2. Merhaba arkadaşlar
3. Selam dostlar
4. Selam arkadaşlar

Not: Çok fazla spintax kullanımı milyonlarca farklı makale üretebilir!
Cihaz performansınız için bir anda çok fazla yazı üretmeyin.
             
Spintax İpuçları:
- Doğal görünüm için az sayıda alternatif kullanın.
- Dilbilgisi kurallarına dikkat edin.
- Her paragrafta en az bir spintax kullanın.
"""),

            ("Makale Ekle", """
1. Makale başlığınızı spintax formatında girin.
2. Makale içeriğinizi spintax formatında girin.
3. 'Makaleyi Önizle' butonu ile farklı varyasyonları test edin.
4. 'Görsel Ekle' butonu ile tüm makalelere görseller ekleyebilirsiniz.
             
    'WordPress sitenizde, Ortamlar kısmından sitenizdeki görsellere erişebilirsiniz. Görsele tıkladıktan sonra 'Adresi Panoya Kopyala' butonu ile görsel URL'nizi alabilirsiniz.'

5. 'Üretilecek Makale' sayısı, toplamda kaç makale üretileceğini belirler.
6. 'Makale Başına Bağlantı' sayısı, bir makalede kaç adet bağlantı olacağını belirler.
7. 'Makale Üret' butonu ile makalenizi üretin.
"""),

            ("Makale Gönder", """
1. 'Site Başına Makale Sayısı' butonu ile 'Site Yönetimi Sayfasında' eklediğiniz sitelere yüklenecek
makale sayısını girin.
             
    '100 makale ürettiniz, 2 siteniz var. Site başına 50 makale yazılmasını seçerseniz, toplamda 100 makale gönderilir.'

2. 'Makale Durumu' seçimi ile tüm WordPress sitelerinizde **Yayınla** veya **Taslak** seçeneklerini belirleyin.
3. 'Makale Göndermeyi Başlat' butonu ile sınırsız makale gönderimini başlatabilirsiniz.
4. Makale gönderilirken sabırlı olun. Sitelere belirli zaman aşımları uygulanarak gönderilir.
5. Çok fazla makale göndermek sunucunuzu yorabilir ve sitenizin çökmesine neden olabilir. 
Verimli kullanım için daha küçük sayılarda makale gönderimi yapmanız önerilir.
""")
        ]

        # Add help sections
        for i, (title, content) in enumerate(sections, start=3):
            # Section title
            section_label = ctk.CTkLabel(help_scroll, text=title,
                                      font=ctk.CTkFont(size=16, weight="bold"))
            section_label.grid(row=i*2, column=0, padx=10, pady=(20,5), sticky="w")
            
            # Section content
            content_label = ctk.CTkLabel(help_scroll, text=content,
                                      font=ctk.CTkFont(size=12),
                                      wraplength=700, justify="left")
            content_label.grid(row=i*2+1, column=0, padx=10, pady=5, sticky="w")

    def update_backlinks_list(self):
        # Clear existing widgets in backlinks frame
        for widget in self.backlinks_frame.winfo_children():
            widget.destroy()

        # Add backlinks
        for i, backlink in enumerate(self.backlinks):
            # Create frame for backlink row
            row_frame = ctk.CTkFrame(self.backlinks_frame, fg_color="transparent")
            row_frame.grid(row=i, column=0, columnspan=2, padx=10, pady=2, sticky="ew")
            row_frame.grid_columnconfigure(0, weight=3)
            row_frame.grid_columnconfigure(1, weight=0)

            # Extract URL from backlink (handle both string and dict formats)
            backlink_url = backlink['url'] if isinstance(backlink, dict) else backlink
            
            # Show URL without any formatting
            url_label = ctk.CTkLabel(row_frame, text=backlink_url, anchor="w")
            url_label.grid(row=0, column=0, padx=5, pady=2, sticky="w")

            # Delete button with system color scheme
            delete_button = ctk.CTkButton(row_frame, text="❌ Sil",
                                       command=lambda idx=i: self.delete_backlink(idx),
                                       fg_color=INACTIVE_COLOR, height=35, corner_radius=8,
                                       border_spacing=10)
            delete_button.grid(row=0, column=1, padx=5, pady=2, sticky="e")

    def delete_backlink(self, index):
        # Remove backlink from list
        del self.backlinks[index]
        self.save_backlinks()
        self.update_backlinks_list()
        self.backlink_status_label.configure(text="✅ Site başarıyla silindi!", text_color="#00FF00")

    def delete_site(self, index):
        # Remove the site from the list
        if 0 <= index < len(self.sites):
            del self.sites[index]
            self.save_sites()
            self.update_sites_list()
            self.status_label.configure(text="✅ Site başarıyla silindi!", text_color="#00FF00")
        else:
            self.status_label.configure(text="❌ Site silinirken bir hata oluştu!", text_color="#FF0000")

    def show_saved_articles_frame(self):
        self.saved_articles_frame.grid(row=0, column=0, sticky="nsew")
        self.site_frame.grid_forget()
        self.backlink_frame.grid_forget()
        self.article_frame.grid_forget()
        self.help_frame.grid_forget()
        self.process_frame.grid_forget()
        
        # Update menu button states
        self.site_menu_button.configure(fg_color=INACTIVE_COLOR)
        self.backlink_menu_button.configure(fg_color=INACTIVE_COLOR)
        self.article_menu_button.configure(fg_color=INACTIVE_COLOR)
        self.saved_articles_button.configure(fg_color=ACTIVE_COLOR)
        self.process_menu_button.configure(fg_color=INACTIVE_COLOR)
        self.help_button.configure(fg_color=INACTIVE_COLOR)

    def show_help(self):
        self.help_frame.grid(row=0, column=0, sticky="nsew")
        self.site_frame.grid_forget()
        self.backlink_frame.grid_forget()
        self.article_frame.grid_forget()
        self.process_frame.grid_forget()
        
        # Update menu button states
        self.site_menu_button.configure(fg_color=INACTIVE_COLOR)
        self.backlink_menu_button.configure(fg_color=INACTIVE_COLOR)
        self.article_menu_button.configure(fg_color=INACTIVE_COLOR)
        self.process_menu_button.configure(fg_color=INACTIVE_COLOR)
        self.help_button.configure(fg_color=ACTIVE_COLOR)

        button_frame = ctk.CTkFrame(help_scroll, fg_color="transparent")
        button_frame.grid(row=1, column=0, padx=10, pady=10)

        # Reset button
        reset_button = ctk.CTkButton(button_frame, text="Programı Sıfırla",
                                  command=reset_all_data,
                                  fg_color="#750000", height=35, corner_radius=8)
        reset_button.grid(row=0, column=0, padx=5, pady=10)

        # Mail button
        mail_button = ctk.CTkButton(button_frame, text="Mail",
                                    command=open_email,
                                    fg_color="#2196F3", height=35, corner_radius=8)
        mail_button.grid(row=0, column=1, padx=5, pady=10)

        # WhatsApp button
        whatsapp_button = ctk.CTkButton(button_frame, text="WhatsApp",
                                    command=open_whatsapp,
                                    fg_color="#25D366", height=35, corner_radius=8)
        whatsapp_button.grid(row=0, column=2, padx=5, pady=10)

        # Help sections
        sections = [
            ("Program Güvenliği ve Kullanımı", """
Program Güvenlik Özellikleri:
- Program verilerinizi dışarıya aktarmaz, veriler sadece kurulu olduğu bilgisayarda saklanır.
- Sadece Windows 10 ve 11 üzerinde, internet erişimi ile sağlıklı çalışır.

Dosya Yönetimi:
- Program dosyalarını (sites.json, backlinks.json, articles.json) silmeyin.
- En iyi performans için programı bir klasör içinde çalıştırın.
- Düzenli yedekleme yapmanız önerilir.

WordPress Güvenliği:
- Backlink Manager API eklentisini WordPress sitenize yükleyin ve etkinleştirin.
- Program üzerinden siteyi eklerken API eklentisini kullanarak bağlantıyı sağlayın.
- Site bağlantısını kaldırmak için program üzerinden silebilir ve 'Backlink Manager API' eklentisini devre dışı bırakabilirsiniz.
"""),    

            ("WordPress Site Ekleme", """
1. WordPress sitenizin yönetici paneline giriş yapın.
2. Eklentiler > Yeni Eklenti Ekle > Eklenti Yükle
3. Backlink Manager API eklentisini yükleyin.
4. Site URL'nizi, kullanıcı adınızı ve şifrenizi Backlink Manager Pro'da kullanın.
5. Birden fazla WordPress sitenizi ekleyebilirsiniz.
"""),

            ("Spintax Makale Oluşturma", """
1. Makaleniz yoksa ChatGPT veya Claude gibi bir yapay zeka aracını kullanarak makalenizi oluşturun.
2. Daha sonra yapay zeka aracına makaleniz için spintax formatı oluşturmasını isteyin.
             
    Yapay zekadan spintax makale oluşturma örneği:
    "Lütfen bu makaleyi spintax formatında yaz."

3. Makaleniz spintax formatında aşağıdaki gibi olacaktır:
             
   - Benzer anlamlı kelimeler {kelime1|kelime2|kelime3} şeklinde,
   - Farklı cümle yapıları {cümle1|cümle2|cümle3} şeklinde.
             
4. Her makale için saniyeler içerisinde trilyonlarca farklı varyasyon oluşturabilirsiniz.
5. Her varyasyon özgün ve benzersiz içerik sağlar.
6. Program her makaleye seçtiğiniz linkleri ve görselleri ekler.

Örnek:
{Merhaba|Selam|Hey}, {nasılsın|bugün nasıl gidiyor|nasıl gidiyor}?
"""),

            ("Maksimum Üretilebilir Makale", """
Maksimum üretilebilir makale sayısı, spintax içeriğinizdeki tüm olası kombinasyonların sayısıdır.

Hesaplama örneği:
{A|B|C} {D|E} = 3 x 2 = 6 farklı kombinasyon

Örnek makale:
{Merhaba|Selam} {dostlar|arkadaşlar} = 2 x 2 = 4 farklı kombinasyon
1. Merhaba dostlar
2. Merhaba arkadaşlar
3. Selam dostlar
4. Selam arkadaşlar

Not: Çok fazla spintax kullanımı milyonlarca farklı makale üretebilir!
Cihaz performansınız için bir anda çok fazla yazı üretmeyin.
             
Spintax İpuçları:
- Doğal görünüm için az sayıda alternatif kullanın.
- Dilbilgisi kurallarına dikkat edin.
- Her paragrafta en az bir spintax kullanın.
"""),

            ("Makale Ekle", """
1. Makale başlığınızı spintax formatında girin.
2. Makale içeriğinizi spintax formatında girin.
3. 'Makaleyi Önizle' butonu ile farklı varyasyonları test edin.
4. 'Görsel Ekle' butonu ile tüm makalelere görseller ekleyebilirsiniz.
             
    'WordPress sitenizde, Ortamlar kısmından sitenizdeki görsellere erişebilirsiniz. Görsele tıkladıktan sonra 'Adresi Panoya Kopyala' butonu ile görsel URL'nizi alabilirsiniz.'

5. 'Üretilecek Makale' sayısı, toplamda kaç makale üretileceğini belirler.
6. 'Makale Başına Bağlantı' sayısı, bir makalede kaç adet bağlantı olacağını belirler.
7. 'Makale Üret' butonu ile makalenizi üretin.
"""),

            ("Makale Gönder", """
1. 'Site Başına Makale Sayısı' butonu ile 'Site Yönetimi Sayfasında' eklediğiniz sitelere yüklenecek
makale sayısını girin.
             
    '100 makale ürettiniz, 2 siteniz var. Site başına 50 makale yazılmasını seçerseniz, toplamda 100 makale gönderilir.'

2. 'Makale Durumu' seçimi ile tüm WordPress sitelerinizde **Yayınla** veya **Taslak** seçeneklerini belirleyin.
3. 'Makale Göndermeyi Başlat' butonu ile sınırsız makale gönderimini başlatabilirsiniz.
4. Makale gönderilirken sabırlı olun. Sitelere belirli zaman aşımları uygulanarak gönderilir.
5. Çok fazla makale göndermek sunucunuzu yorabilir ve sitenizin çökmesine neden olabilir. 
Verimli kullanım için daha küçük sayılarda makale gönderimi yapmanız önerilir.
""")
        ]
        # Add help sections
        for i, (title, content) in enumerate(sections, start=3):
            # Section title
            section_label = ctk.CTkLabel(help_scroll, text=title,
                                      font=ctk.CTkFont(size=16, weight="bold"))
            section_label.grid(row=i*2, column=0, padx=10, pady=(20,5), sticky="w")
            
            # Section content
            content_label = ctk.CTkLabel(help_scroll, text=content,
                                      font=ctk.CTkFont(size=12),
                                      wraplength=700, justify="left")
            content_label.grid(row=i*2+1, column=0, padx=10, pady=5, sticky="w")

    def show_site_frame(self):
        self.site_frame.grid(row=0, column=0, sticky="nsew")
        self.backlink_frame.grid_forget()
        self.article_frame.grid_forget()
        self.process_frame.grid_forget()
        if self.help_frame:
            self.help_frame.grid_forget()
            
        # Update menu button states
        self.site_menu_button.configure(fg_color=ACTIVE_COLOR)
        self.backlink_menu_button.configure(fg_color=INACTIVE_COLOR)
        self.article_menu_button.configure(fg_color=INACTIVE_COLOR)
        self.process_menu_button.configure(fg_color=INACTIVE_COLOR)
        self.help_button.configure(fg_color=INACTIVE_COLOR)

    def show_backlink_frame(self):
        self.backlink_frame.grid(row=0, column=0, sticky="nsew")
        self.site_frame.grid_forget()
        self.article_frame.grid_forget()
        self.process_frame.grid_forget()
        if self.help_frame:
            self.help_frame.grid_forget()
            
        # Update menu button states
        self.site_menu_button.configure(fg_color=INACTIVE_COLOR)
        self.backlink_menu_button.configure(fg_color=ACTIVE_COLOR)
        self.article_menu_button.configure(fg_color=INACTIVE_COLOR)
        self.process_menu_button.configure(fg_color=INACTIVE_COLOR)
        self.help_button.configure(fg_color=INACTIVE_COLOR)

    def show_article_frame(self):
        self.article_frame.grid(row=0, column=0, sticky="nsew")
        self.site_frame.grid_forget()
        self.backlink_frame.grid_forget()
        self.process_frame.grid_forget()
        if self.help_frame:
            self.help_frame.grid_forget()
            
        # Update menu button states
        self.site_menu_button.configure(fg_color=INACTIVE_COLOR)
        self.backlink_menu_button.configure(fg_color=INACTIVE_COLOR)
        self.article_menu_button.configure(fg_color=ACTIVE_COLOR)
        self.process_menu_button.configure(fg_color=INACTIVE_COLOR)
        self.help_button.configure(fg_color=INACTIVE_COLOR)

    def show_process_frame(self):
        # Hide all frames
        self.site_frame.grid_forget()
        self.backlink_frame.grid_forget()
        self.article_frame.grid_forget()
        if self.help_frame:
            self.help_frame.grid_forget()

        # Show process frame
        self.process_frame.grid(row=0, column=0, sticky="nsew")

        # Update button colors
        self.site_menu_button.configure(fg_color=INACTIVE_COLOR)
        self.backlink_menu_button.configure(fg_color=INACTIVE_COLOR)
        self.article_menu_button.configure(fg_color=INACTIVE_COLOR)
        self.process_menu_button.configure(fg_color=ACTIVE_COLOR)
        self.help_button.configure(fg_color=INACTIVE_COLOR)

        # Update article list
        self.update_article_list()

    # Thread slider functionality removed

    def update_article_list(self):
        # Clear existing widgets in saved articles scroll frame
        for widget in self.saved_articles_scroll.winfo_children():
            widget.destroy()

        # Update article counter
        if hasattr(self, 'article_counter'):
            self.article_counter.configure(text=f"Listede {len(self.articles)} Makale Bulunuyor")

        # Initialize pagination variables if not exists
        if not hasattr(self, 'current_page'):
            self.current_page = 0
        if not hasattr(self, 'articles_per_page'):
            self.articles_per_page = 50

        # Calculate total pages
        total_pages = (len(self.articles) + self.articles_per_page - 1) // self.articles_per_page

        # Get current page articles
        start_idx = self.current_page * self.articles_per_page
        end_idx = min(start_idx + self.articles_per_page, len(self.articles))
        current_articles = self.articles[start_idx:end_idx]

        # Add articles for current page
        for i, article in enumerate(current_articles):
            # Create frame for article row with dark background
            row_frame = ctk.CTkFrame(self.saved_articles_scroll, fg_color="transparent")
            row_frame.grid(row=i, column=0, padx=5, pady=1, sticky="ew")
            row_frame.grid_columnconfigure(0, weight=1)
            row_frame.grid_columnconfigure(1, weight=0)

            # Show article title with reduced height - extended length
            title = article['title'][:150] + "..." if len(article['title']) > 150 else article['title']
            title_label = ctk.CTkLabel(row_frame, text=title, anchor="w", height=25)
            title_label.grid(row=0, column=0, padx=5, pady=1, sticky="w")

            # Create frame for buttons with transparent background
            button_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
            button_frame.grid(row=0, column=1, padx=(0, 10), pady=1, sticky="e")

            # Delete button with reduced height and padding
            delete_button = ctk.CTkButton(button_frame, text="❌ Sil",
                                       command=lambda idx=start_idx+i: self.delete_article(idx),
                                       fg_color=ACTIVE_COLOR, height=25, corner_radius=6,
                                       hover_color=HOVER_COLOR, width=50)
            delete_button.grid(row=0, column=1, padx=(0, 5), pady=1)

        # Add pagination controls if there are multiple pages
        if total_pages > 1:
            pagination_frame = ctk.CTkFrame(self.saved_articles_scroll, fg_color="transparent")
            pagination_frame.grid(row=len(current_articles), column=0, padx=5, pady=10, sticky="ew")
            pagination_frame.grid_columnconfigure((0,1,2), weight=1)

            # Previous page button
            prev_button = ctk.CTkButton(pagination_frame, text="←",
                                    command=lambda: self.change_page(-1),
                                    fg_color=ACTIVE_COLOR, height=25, corner_radius=6,
                                    hover_color=HOVER_COLOR, width=50,
                                    state="normal" if self.current_page > 0 else "disabled")
            prev_button.grid(row=0, column=0, padx=5, pady=5)

            # Page indicator
            page_label = ctk.CTkLabel(pagination_frame,
                                   text=f"Sayfa {self.current_page + 1}/{total_pages}")
            page_label.grid(row=0, column=1, padx=5, pady=5)

            # Next page button
            next_button = ctk.CTkButton(pagination_frame, text="→",
                                    command=lambda: self.change_page(1),
                                    fg_color=ACTIVE_COLOR, height=25, corner_radius=6,
                                    hover_color=HOVER_COLOR, width=50,
                                    state="normal" if self.current_page < total_pages - 1 else "disabled")
            next_button.grid(row=0, column=2, padx=5, pady=5)

    def generate_articles(self):
        # Prevent multiple generations
        if hasattr(self, 'generation_thread') and self.generation_thread.is_alive():
            self.article_status_label.configure(text="⚠️ Makale üretimi zaten devam ediyor!", text_color="#FFA500")
            return

        # Initialize message queue and thread control flag
        self.generation_queue = queue.Queue()
        self.is_generating = True

        # Disable UI elements during generation
        self.disable_ui_elements()
        
        try:
            # Start article generation in a separate thread with proper cleanup
            self.generation_thread = threading.Thread(target=self._generate_articles_worker)
            self.generation_thread.daemon = True
            self.generation_thread.start()
            
            # Start UI update loop with proper cleanup
            self.update_generation_ui()
        except Exception as e:
            self.article_status_label.configure(text=f"❌ Makale üretimi başlatılamadı: {str(e)}", text_color="#FF0000")
            self.enable_ui_elements()
            self.is_generating = False
            if hasattr(self, 'generation_queue'):
                del self.generation_queue

    def _generate_articles_worker(self):
        try:
            # Get article count and content within try block to handle UI access errors
            try:
                article_count = int(self.article_count_entry.get())
                title = self.title_entry.get("1.0", "end-1c")
                content = self.content_entry.get("1.0", "end-1c")
                backlinks_per_article = int(self.backlink_per_content_entry.get())
            except Exception as e:
                raise ValueError(f"UI erişim hatası: {str(e)}")

            # Validate inputs
            if not title or not content:
                raise ValueError("Başlık ve içerik alanları boş olamaz!")
            if article_count < 1:
                raise ValueError("Geçerli bir makale sayısı giriniz!")
            if backlinks_per_article < 0:
                raise ValueError("Geçerli bir bağlantı sayısı giriniz!")
            if backlinks_per_article > 0 and not self.backlinks:
                raise ValueError("Bağlantı eklemek için önce bağlantı listesine site eklemelisiniz!")

            # Generate articles with proper thread safety
            for i in range(article_count):
                if not self.is_generating:
                    break

                try:
                    # First process the spintax content
                    processed_content = self.process_spintax(content)
                    processed_title = self.process_spintax(title)
                    
                    # Add a single random image at the beginning of content if available
                    if self.image_urls:
                        # Select one random image URL from the pool
                        random_image_url = random.choice(self.image_urls)
                        # Generate image tag without alt attribute
                        image_tag = '<img src="{}" style="max-width:100%;height:auto;">'.format(random_image_url)
                        processed_content = image_tag + '\n\n' + processed_content
                    
                    # Process content and add backlinks if needed
                    if backlinks_per_article > 0 and self.backlinks:
                        # Split content into paragraphs
                        paragraphs = [p for p in processed_content.split('\n\n') if p.strip()]
                        
                        # Get random backlinks
                        selected_backlinks = random.sample(self.backlinks, min(backlinks_per_article, len(self.backlinks)))
                        
                        for backlink in selected_backlinks:
                            if not paragraphs:  # Skip if no valid paragraphs
                                continue
                                
                            # Select a random paragraph
                            paragraph_idx = random.randint(0, len(paragraphs) - 1)
                            paragraph = paragraphs[paragraph_idx]
                            
                            # Split into words and filter valid ones
                            words = paragraph.split()
                            valid_words = [i for i, word in enumerate(words) 
                                         if len(word) > 3 
                                         and word.isalnum() 
                                         and not any(tag in word for tag in ['<a', '</a>', '<img', '<p', '<div'])]
                            
                            if valid_words:  # Only proceed if we found valid words
                                # Select a random word
                                word_idx = random.choice(valid_words)
                                word = words[word_idx]
                                
                                # Create the hyperlink - handle both dictionary and string formats
                                if isinstance(backlink, dict) and 'url' in backlink:
                                    backlink_url = backlink['url']
                                else:
                                    backlink_url = str(backlink)
                                words[word_idx] = f'<a href="{backlink_url}" target="_blank" rel="nofollow">{word}</a>'
                                
                                # Update the paragraph
                                paragraphs[paragraph_idx] = ' '.join(words)
                        
                        # Rejoin the paragraphs
                        processed_content = '\n\n'.join(paragraphs)

                    # Create new article with processed content
                    new_article = {
                        'title': processed_title,
                        'content': processed_content,
                        'image_urls': self.image_urls.copy() if self.image_urls else []
                    }

                    # Add article and save with proper locking
                    with self.ui_lock:
                        if not self.is_generating:
                            break
                        self.articles.append(new_article)
                        self.save_articles()
                        # Update progress through queue
                        progress = f"✓ {i + 1}/{article_count} makale üretildi..."
                        self.generation_queue.put(("progress", progress))

                except Exception as e:
                    self.generation_queue.put(("error", f"Makale üretim hatası: {str(e)}"))
                    break

            # Clear input fields only if generation completed successfully
            if self.is_generating:
                self.generation_queue.put(("clear_inputs", None))
                self.generation_queue.put(("success", f"✅ {article_count} makale başarıyla üretildi!"))

        except ValueError as e:
            self.generation_queue.put(("error", str(e)))
        except Exception as e:
            self.generation_queue.put(("error", f"Beklenmeyen hata: {str(e)}"))
        finally:
            self.is_generating = False

    def update_generation_ui(self):
        if not self.is_generating:
            return

        try:
            # Process all available messages with proper error handling
            while True:
                try:
                    msg_type, msg_value = self.generation_queue.get_nowait()
                    
                    if msg_type == "error":
                        self.article_status_label.configure(text=f"❌ {msg_value}", text_color="#FF0000")
                        self.is_generating = False
                        self.enable_ui_elements()
                        return
                    elif msg_type == "progress":
                        self.article_status_label.configure(text=msg_value, text_color="#00FF00")
                    elif msg_type == "success":
                        self.article_status_label.configure(text=msg_value, text_color="#00FF00")
                        self.is_generating = False
                        self.enable_ui_elements()
                        return
                    elif msg_type == "clear_inputs":
                        self.title_entry.delete("1.0", "end")
                        self.content_entry.delete("1.0", "end")
                        self.image_urls = []
                        
                except queue.Empty:
                    break
                except Exception as e:
                    # Log UI update errors but continue processing
                    print(f"UI update error: {str(e)}")
                    continue

            # Schedule next update if still generating
            if self.is_generating:
                self.after(100, self.update_generation_ui)

        except Exception as e:
            self.article_status_label.configure(text=f"❌ UI güncelleme hatası: {str(e)}", text_color="#FF0000")
            self.is_generating = False
            self.enable_ui_elements()

    def disable_ui_elements(self):
        # Disable all interactive elements during article generation
        self.title_entry.configure(state="disabled")
        self.content_entry.configure(state="disabled")
        self.article_count_entry.configure(state="disabled")
        self.backlink_per_content_entry.configure(state="disabled")
        self.preview_article_button.configure(state="disabled")
        self.multi_image_button.configure(state="disabled")
        self.site_menu_button.configure(state="disabled")
        self.backlink_menu_button.configure(state="disabled")
        self.article_menu_button.configure(state="disabled")
        self.process_menu_button.configure(state="disabled")
        self.help_button.configure(state="disabled")

    def enable_ui_elements(self):
        # Re-enable all interactive elements after article generation
        self.title_entry.configure(state="normal")
        self.content_entry.configure(state="normal")
        self.article_count_entry.configure(state="normal")
        self.backlink_per_content_entry.configure(state="normal")
        self.preview_article_button.configure(state="normal")
        self.multi_image_button.configure(state="normal")
        self.site_menu_button.configure(state="normal")
        self.backlink_menu_button.configure(state="normal")
        self.article_menu_button.configure(state="normal")
        self.process_menu_button.configure(state="normal")
        self.help_button.configure(state="normal")

    def generate_articles(self):
        # Import required modules
        import threading
        import queue
        
        # Initialize generation queue for thread-safe communication
        self.generation_queue = queue.Queue()
        self.is_generating = True
        
        # Get article details
        title = self.title_entry.get("1.0", "end-1c").strip()
        content = self.content_entry.get("1.0", "end-1c").strip()

        # Validate input fields
        if not title or not content:
            self.article_status_label.configure(text="❌ Lütfen tüm alanları doldurun!", text_color="#FF0000")
            return

        # Disable UI elements during generation
        self.save_article_button.configure(state="disabled")
        self.article_status_label.configure(text="⏳ Makaleler üretiliyor...", text_color="#FFFFFF")

        # Start the worker thread
        worker_thread = threading.Thread(target=self._generate_articles_worker, daemon=True)
        worker_thread.start()

        # Update UI based on queue messages
        def update_ui():
            try:
                while True:
                    try:
                        msg_type, msg_value = self.generation_queue.get_nowait()
                        
                        if msg_type == "progress":
                            self.article_status_label.configure(text=msg_value, text_color="#00FF00")
                        elif msg_type == "error":
                            self.article_status_label.configure(text=msg_value, text_color="#FF0000")
                            self.save_article_button.configure(state="normal")
                            return
                        elif msg_type == "success":
                            self.article_status_label.configure(text=msg_value, text_color="#00FF00")
                            self.save_article_button.configure(state="normal")
                            return
                        elif msg_type == "clear_inputs":
                            self.title_entry.delete("1.0", "end")
                            self.content_entry.delete("1.0", "end")
                            self.image_urls = []
                            
                    except queue.Empty:
                        break
                        
                if self.is_generating:
                    self.after(100, update_ui)
                    
            except Exception as e:
                self.article_status_label.configure(
                    text=f"❌ UI güncelleme hatası: {str(e)}",
                    text_color="#FF0000"
                )
                self.save_article_button.configure(state="normal")
        
        # Start UI updates
        update_ui()

    def change_page(self, direction):
        # Update current page
        total_pages = (len(self.articles) + self.articles_per_page - 1) // self.articles_per_page
        new_page = self.current_page + direction
        
        # Ensure page is within valid range
        if 0 <= new_page < total_pages:
            self.current_page = new_page
            self.update_article_list()

    def delete_article(self, index):
        # Remove article from list
        self.articles.pop(index)
        self.save_articles()
        # Reset to first page when deleting
        self.current_page = 0
        self.update_article_list()
        
    def delete_all_articles(self):
        # Remove all articles
        self.articles = []
        self.save_articles()
        self.update_article_list()
        self.process_status_label.configure(text="✅ Tüm makaleler başarıyla silindi!", text_color="#00FF00")

    def start_article_generation(self):
        # Import required modules
        import queue
        import random
        import threading
        import time
        import requests

        # Get the number of articles to generate
        try:
            content_per_site = int(self.content_per_site_entry.get())
            if content_per_site < 1:
                self.process_status_label.configure(text="❌ Geçerli sayılar giriniz!", text_color="#FF0000")
                return
        except ValueError:
            self.process_status_label.configure(text="❌ Geçerli sayılar giriniz!", text_color="#FF0000")
            return

        if not self.articles:
            self.process_status_label.configure(text="❌ Önce içerik eklemelisiniz!", text_color="#FF0000")
            return

        if not self.sites:
            self.process_status_label.configure(text="❌ Önce site eklemelisiniz!", text_color="#FF0000")
            return

        # Check if already running
        if hasattr(self, 'is_generating') and self.is_generating:
            self.is_generating = False
            self.start_button.configure(text="Makale Göndermeyi Başlat", fg_color=ACTIVE_COLOR)
            self.process_status_label.configure(text="✓ Makale gönderme durduruldu", text_color="#00FF00")
            return

        # Validate inputs
        try:
            content_per_site = int(self.content_per_site_entry.get())
            if content_per_site < 1:
                raise ValueError
        except ValueError:
            self.process_status_label.configure(text="❌ Geçerli sayılar giriniz!", text_color="#FF0000")
            return

        if not self.articles:
            self.process_status_label.configure(text="❌ Önce içerik eklemelisiniz!", text_color="#FF0000")
            return

        if not self.sites:
            self.process_status_label.configure(text="❌ Önce site eklemelisiniz!", text_color="#FF0000")
            return

        # Initialize UI and processing state
        self.is_generating = True
        self.start_button.configure(text="Makale Göndermeyi Durdur", fg_color="#FF4444")
        message_queue = queue.Queue()
        
        # Show progress bar and label
        self.progress_bar.grid(row=6, column=0, padx=10, pady=5, sticky="ew")
        self.progress_label.grid(row=7, column=0, padx=10, pady=5)
        self.process_status_label.grid(row=5, column=0, padx=10, pady=5)
        
        # Calculate total articles to be posted
        total_articles = len(self.sites) * content_per_site
        self.progress_bar.set(0)
        self.progress_label.configure(text=f"Makaleler gönderiliyor... 0/{total_articles}")
        
        # Thread-safe resources
        articles_lock = threading.Lock()
        processed_articles = 0

        def post_article(site):
            nonlocal processed_articles
            if not self.is_generating:
                return False

            try:
                # Select random article
                with articles_lock:
                    if not self.articles:
                        raise ValueError("No articles available")
                    article = random.choice(self.articles)

                # Prepare article data
                post_data = {
                    'title': article['title'],
                    'content': article['content'],
                    'status': self.content_status_var.get()
                }

                # Send request to WordPress
                headers = {'Authorization': f'Bearer {site["auth_token"]}'}
                response = requests.post(
                    f"{site['url']}/wp-json/backlink-manager/v1/posts",
                    json=post_data,
                    headers=headers,
                    timeout=30
                )
                response.raise_for_status()

                # Update progress
                with articles_lock:
                    processed_articles += 1
                    progress = processed_articles / total_articles
                    message_queue.put(('progress', progress))
                    message_queue.put(('status', [f"✓ Makale gönderildi: {article['title'][:50]}...", "#00FF00"]))

                return True

            except Exception as e:
                message_queue.put(('status', [f"❌ {site['url']} için hata: {str(e)}", "#FF0000"]))
                return False

        def update_ui():
            try:
                if not self.is_generating:
                    return

                # Process all available messages
                while True:
                    try:
                        msg_type, msg_value = message_queue.get_nowait()
                        if msg_type == 'progress':
                            self.progress_bar.set(msg_value)
                            self.progress_label.configure(text=f"Makaleler gönderiliyor... {processed_articles}/{total_articles}")
                        elif msg_type == 'status':
                            self.process_status_label.configure(text=msg_value[0], text_color=msg_value[1])
                    except queue.Empty:
                        break

            except Exception as e:
                print(f"UI update error: {str(e)}")
            finally:
                if self.is_generating:
                    self.after(100, update_ui)
                else:
                    self.after(0, lambda: self.start_button.configure(text="Makale Göndermeyi Başlat", fg_color=ACTIVE_COLOR))

        # Start UI updates
        update_ui()

        # Create and start worker threads
        def worker_thread():
            try:
                for _ in range(content_per_site):
                    if not self.is_generating:
                        break
                    for site in self.sites:
                        if not self.is_generating:
                            break
                        try:
                            post_article(site)
                            time.sleep(0.5)  # Small delay between posts
                        except Exception as e:
                            message_queue.put(('status', [f"❌ Makale gönderme hatası: {str(e)}", "#FF0000"]))
                            continue
            except Exception as e:
                message_queue.put(('status', [f"❌ İşlem hatası: {str(e)}", "#FF0000"]))
            finally:
                self.is_generating = False
                message_queue.put(('status', [f"✅ İşlem tamamlandı! {processed_articles} makale gönderildi.", "#00FF00"]))

        # Start worker thread with proper exception handling
        try:
            self.worker_thread = threading.Thread(target=worker_thread)
            self.worker_thread.daemon = True
            self.worker_thread.start()
        except Exception as e:
            self.is_generating = False
            self.process_status_label.configure(text=f"❌ Thread başlatma hatası: {str(e)}", text_color="#FF0000")
            self.start_button.configure(text="Makale Göndermeyi Başlat", fg_color=ACTIVE_COLOR)

        # Calculate total work for posting phase
        start_time = time.time()

        # Thread-safe resources with improved management
        lock = threading.Lock()
        articles_lock = threading.Lock()
        backlinks_lock = threading.Lock()
        
        # Add a semaphore to limit concurrent API requests - use actual thread count
        request_semaphore = threading.Semaphore(max(1, thread_count))  # Use full thread count

        # Initialize the processed_articles counter
        processed_articles = 0

        def update_progress():
            nonlocal processed_articles
            try:
                with lock:
                    processed_articles += 1
                    progress = processed_articles / total_articles
                    if not self.is_generating:
                        return False

                    # Only queue updates, don't update UI directly from worker thread
                    message_queue.put(('progress', progress))
                    message_queue.put(('progress_label', f"İşleniyor... {processed_articles}/{total_articles}"))
                    return True
            except Exception as e:
                message_queue.put(('status', [f"❌ İlerleme güncellemesi hatası: {str(e)}", "#FF0000"]))
                return False

        def update_ui():
            if not self.is_generating:
                return
            try:
                # Process all available messages in the queue
                messages_processed = 0
                max_messages_per_update = 10  # Limit messages processed per update
                
                while messages_processed < max_messages_per_update:
                    try:
                        msg_type, msg_value = message_queue.get_nowait()
                        messages_processed += 1
                        
                        # Only process progress updates, ignore status messages
                        if msg_type == 'progress':
                            self.progress_bar.set(msg_value)
                        elif msg_type == 'progress_label':
                            # Process but don't display progress label updates
                            pass
                        elif msg_type == 'status':
                            # Ignore status messages
                            pass
                    except queue.Empty:
                        break
                    except Exception as e:
                        # Silently handle errors
                        continue
                
                # Batch update the UI
                self.update()
                
            except Exception as e:
                try:
                    self.process_status_label.configure(text=f"❌ UI Güncelleme Hatası: {str(e)}", text_color="#FF0000")
                    self.update()
                except:
                    pass
            finally:
                if self.is_generating:
                    # Schedule next update with shorter interval for smoother progress
                    self.after(10, update_ui)

        # Start UI updates
        update_ui()

        # Backlink insertion is now done during article generation in save_current_article

        def process_site(site):
            try:
                # Set timeout for entire process
                start_time = time.time()
                timeout = 30  # 30 second timeout
                
                # Get random article with proper error handling
                with articles_lock:
                    if time.time() - start_time > timeout:
                        raise TimeoutError("Article processing timeout")
                    if not self.articles:
                        raise ValueError("Makale bulunamadı")
                    article = random.choice(self.articles)

                # Get the already processed title and content (no spintax processing needed)
                try:
                    if time.time() - start_time > timeout:
                        raise TimeoutError("Article processing timeout")
                    
                    # Use the already processed title and content directly
                    title = article.get('title', '')
                    content = article.get('content', '')
                    
                    # Update UI to show current processing status
                    message_queue.put(('status', [f"✓ Makale gönderiliyor: {title[:50]}...", "#00FF00"]))
                    self.update_idletasks()
                    
                    # Validate content
                    if not title or len(title) < 5:
                        raise ValueError("Başlık hatası: Başlık çok kısa veya boş")
                    if not content or len(content) < 50:
                        raise ValueError("İçerik hatası: İçerik çok kısa veya boş")
                        
                except TimeoutError as e:
                    message_queue.put(('status', ["⚠️ Makale işleme zaman aşımı", "#FFA500"]))
                    raise
                except Exception as e:
                    raise ValueError(f"Makale işleme hatası: {str(e)}")

                # Backlinks are already added during article generation
                message_queue.put(('status', ["✓ Makale backlinkleri ile birlikte gönderiliyor", "#00FF00"]))
                self.update_idletasks()

                # Update progress after each major step
                if not update_progress():
                    return
                
                self.update_idletasks()
                return True

            except Exception as e:
                message_queue.put(('status', [f"❌ İşlem hatası: {str(e)}", "#FF0000"]))
                self.update_idletasks()
                return False

                # Handle image upload if available - using image path from article
                featured_image_id = None
                try:
                    # Get image path from article
                    image_path = article.get('featured_image_path')
                    if image_path:
                            # Import libraries at the beginning to avoid repeated imports
                            import base64, os
                            from PIL import Image
                            import io
                            
                            try:
                                # Optimize image before uploading
                                img = Image.open(image_path)
                                
                                # Resize large images to reduce upload size
                                max_size = (1200, 1200)  # Maximum dimensions
                                if img.width > max_size[0] or img.height > max_size[1]:
                                    img.thumbnail(max_size, Image.LANCZOS)
                                
                                # Convert to RGB if needed (in case of RGBA or other modes)
                                if img.mode != 'RGB':
                                    img = img.convert('RGB')
                                
                                # Save optimized image to memory buffer
                                buffer = io.BytesIO()
                                img.save(buffer, format='JPEG', quality=85, optimize=True)
                                buffer.seek(0)
                                img_data = buffer.read()
                                
                                # Convert image to base64
                                img_base64 = base64.b64encode(img_data).decode('utf-8')
                                
                                # Get image filename
                                img_name = os.path.basename(image_path)
                                
                                # Upload image to WordPress with semaphore to limit concurrent requests
                                with request_semaphore:
                                    headers = {'Authorization': f'Bearer {site["auth_token"]}'}                            
                                    image_data = {
                                        'image_data': f'data:image/jpeg;base64,{img_base64}',
                                        'image_name': img_name
                                    }
                                    
                                    # Send image upload request with reduced timeout
                                    upload_response = requests.post(
                                        f"{site['url']}/wp-json/backlink-manager/v1/upload-image",
                                        json=image_data,
                                        headers=headers,
                                        timeout=20  # Reduced timeout
                                    )
                                    upload_response.raise_for_status()
                                    
                                    # Get the uploaded image ID
                                    upload_result = upload_response.json()
                                    featured_image_id = upload_result.get('id')
                                    
                                    message_queue.put(('status', [f"✓ Görsel başarıyla yüklendi: {img_name}", "#00FF00"]))
                            except Exception as img_error:
                                message_queue.put(('status', [f"⚠️ Görsel işleme hatası: {str(img_error)}", "#FFA500"]))
                except Exception as e:
                    # Log error but continue without image rather than failing
                    message_queue.put(('status', [f"⚠️ Görsel yükleme uyarısı: {str(e)}", "#FFA500"]))
                
                # Create post data
                post_data = {
                    'title': title,
                    'content': content,
                    'status': self.content_status_var.get(),
                    'featured_image_id': featured_image_id
                }

                # Send request to WordPress using semaphore to limit concurrent requests
                try:
                    # Use semaphore to limit concurrent API requests
                    with request_semaphore:
                        headers = {'Authorization': f'Bearer {site["auth_token"]}'}
                        # Reduce timeout from 30 to 15 seconds to fail faster
                        # Create a session with retry capability
                        session = requests.Session()
                        from requests.adapters import HTTPAdapter
                        from urllib3.util.retry import Retry
                        
                        # Configure optimized retry strategy
                        retries = Retry(
                            total=3,  # Arttırılmış yeniden deneme sayısı
                            backoff_factor=1,  # Daha uzun bekleme süresi
                            status_forcelist=[429, 500, 502, 503, 504],  # 429 (rate limit) eklendi
                            allowed_methods=["POST"],  # Only retry POST requests
                            respect_retry_after_header=True  # Sunucunun retry-after başlığına uy
                        )
                        
                        # Apply retry strategy to session with optimized connection pool
                        adapter = HTTPAdapter(max_retries=retries, pool_connections=10, pool_maxsize=10)
                        session.mount('http://', adapter)
                        session.mount('https://', adapter)
                        
                        # Optimize request headers
                        headers['Connection'] = 'keep-alive'
                        headers['Accept'] = 'application/json'
                        headers['Content-Type'] = 'application/json'
                        
                        # Send request with retry capability and optimized timeout
                        response = session.post(
                            f"{site['url']}/wp-json/backlink-manager/v1/posts",
                            json=post_data,
                            headers=headers,
                            timeout=12  # Daha kısa zaman aşımı süresi
                        )
                        response.raise_for_status()
                        
                        # Dinamik bekleme süresi - sunucu yükü yüksekse daha uzun bekle
                        if response.status_code == 201 or response.status_code == 200:
                            # Başarılı yanıt - kısa bekleme
                            time.sleep(0.3)
                        else:
                            # Diğer başarılı yanıtlar - biraz daha uzun bekle
                            time.sleep(0.7)
                except requests.exceptions.Timeout:
                    raise ValueError("WordPress bağlantı zaman aşımı - sunucu yanıt vermiyor")
                except requests.exceptions.ConnectionError:
                    raise ValueError("WordPress bağlantı hatası - internet bağlantınızı kontrol edin")
                except requests.exceptions.HTTPError as e:
                    if hasattr(e, 'response') and e.response is not None:
                        status_code = e.response.status_code
                        if status_code == 401:
                            raise ValueError("WordPress API yetkilendirme hatası - token geçersiz")
                        elif status_code >= 500:
                            raise ValueError(f"WordPress sunucu hatası: {status_code}")
                        else:
                            raise ValueError(f"WordPress API hatası: {status_code}")
                    else:
                        raise ValueError(f"WordPress API hatası: {str(e)}")
                except requests.exceptions.RequestException as e:
                    raise ValueError(f"WordPress API hatası: {str(e)}")

                # Update progress
                if not update_progress():
                    return False

                return True

            except ValueError as e:
                message_queue.put(('status', [f"❌ {str(e)}", "#FF0000"]))
                return False
            except Exception as e:
                import traceback
                traceback.print_exc()
                message_queue.put(('status', [f"❌ Beklenmeyen hata: {str(e)}", "#FF0000"]))
                return False

        # Create thread pool with proper exception handling and resource management
        def process_with_timeout(site):
            try:
                # Add timeout to prevent hanging threads
                result = None
                import threading
                import time
                import ctypes
                import traceback
                import queue
                from contextlib import contextmanager
                
                @contextmanager
                def timeout_context(timeout):
                    # Use a proper approach for timeout that doesn't rely on thread.interrupt
                    timer = threading.Timer(timeout, lambda: None)  # Just a placeholder timer
                    timer.start()
                    try:
                        yield
                    finally:
                        timer.cancel()
                
                # Thread-local error queue with size limit
                error_queue = queue.Queue(maxsize=5)
                
                # Create thread with proper resource management
                def thread_target():
                    nonlocal result
                    try:
                        # Use a simpler approach without the problematic timeout_context
                        result = process_site(site)
                    except Exception as e:
                        error_message = str(e)
                        traceback.print_exc()
                        try:
                            error_queue.put_nowait(error_message)
                        except queue.Full:
                            pass
                        result = False
                    finally:
                        # Ensure resources are released
                        try:
                            with request_semaphore:
                                pass
                        except:
                            pass
                
                # Create and start thread with resource limits
                thread = threading.Thread(target=thread_target)
                thread.daemon = True
                
                start_time = time.time()
                thread.start()
                
                # Wait with timeout and proper cleanup
                thread.join(timeout=20)
                
                if thread.is_alive():
                    elapsed_time = time.time() - start_time
                    message_queue.put(('status', [f"⚠️ İşlem zaman aşımı ({elapsed_time:.1f}s)", "#FFA500"]))
                    return False
                
                # Check for errors with timeout
                try:
                    error_message = error_queue.get_nowait()
                    message_queue.put(('status', [f"⚠️ İşlem hatası: {error_message}", "#FFA500"]))
                    return False
                except queue.Empty:
                    pass
                    
                return result if result is not None else False
                
            except Exception as e:
                traceback.print_exc()
                message_queue.put(('status', [f"⚠️ Beklenmeyen hata: {str(e)}", "#FFA500"]))
                return False
                
        # Use a safer approach with ThreadPoolExecutor
        executor = None
        futures = []
        try:
            # Use the exact thread count specified by the user
            max_workers = thread_count
            executor = ThreadPoolExecutor(max_workers=max_workers)
            
            # Submit tasks for each site and content combination
            futures = []
            for site in self.sites:
                for _ in range(content_per_site):
                    if not self.is_generating:
                        break
                    futures.append(executor.submit(process_with_timeout, site))
                    
            # Update status to show that tasks have been submitted
            message_queue.put(('status', [f"✓ {len(futures)} makale oluşturma görevi başlatıldı ({max_workers} iş parçacığı ile)", "#00FF00"]))
            message_queue.put(('progress_label', f"İşleniyor... 0/{total_articles}"))
            self.update_idletasks()

            # Wait for all tasks to complete with timeout
            import concurrent.futures
            try:
                # Use as_completed with timeout to prevent hanging
                completed_count = 0
                total_count = len(futures)
                
                # Set a reasonable timeout based on the number of tasks
                overall_timeout = min(30 + (total_count * 10), 300)  # Between 30s and 5min
                
                # Update UI immediately to show we're starting to process
                message_queue.put(('progress', 0.01))  # Show a small progress to indicate start
                message_queue.put(('status', [f"✓ İşleniyor: 0/{total_count} tamamlandı", "#00FF00"]))
                self.update_idletasks()
                
                for future in concurrent.futures.as_completed(futures, timeout=overall_timeout):
                    try:
                        # Reduced individual timeout for better responsiveness
                        result = future.result(timeout=15)  
                        completed_count += 1
                        
                        # Update progress after each completion
                        progress = completed_count / total_count
                        message_queue.put(('progress', progress))
                        message_queue.put(('progress_label', f"İşleniyor... {completed_count}/{total_count}"))
                        
                        # Calculate elapsed time
                        elapsed_time = time.time() - start_time
                        
                        # Update status more frequently for better feedback
                        if completed_count % 1 == 0 or completed_count == total_count:  # Update every completion
                            message_queue.put(('status', [f"✓ İşleniyor: {completed_count}/{total_count} tamamlandı", "#00FF00"]))
                            
                        # Force UI update more frequently
                        if completed_count % 1 == 0:  # Update UI after each completion
                            self.update_idletasks()
                    except concurrent.futures.TimeoutError:
                        message_queue.put(('status', [f"⚠️ Bir işlem zaman aşımına uğradı, devam ediliyor", "#FFA500"]))
                        self.update_idletasks()
                    except Exception as e:
                        import traceback
                        traceback.print_exc()
                        message_queue.put(('status', [f"⚠️ Hata: {str(e)}, devam ediliyor", "#FFA500"]))
                        self.update_idletasks()
            except concurrent.futures.TimeoutError:
                message_queue.put(('status', [f"⚠️ İşlemler zaman aşımına uğradı, kalan işlemler iptal ediliyor", "#FFA500"]))
            except Exception as e:
                import traceback
                traceback.print_exc()
                message_queue.put(('status', [f"❌ Beklenmeyen hata: {str(e)}", "#FF0000"]))
        finally:
            # Ensure proper cleanup of executor and futures
            if futures:
                # Cancel any remaining futures
                for future in futures:
                    if not future.done():
                        future.cancel()
            
            # Shutdown executor properly
            if executor:
                try:
                    # Shutdown with a short timeout to prevent hanging
                    executor.shutdown(wait=True, cancel_futures=True)
                except Exception as e:
                    message_queue.put(('status', [f"⚠️ Executor kapatma hatası: {str(e)}", "#FFA500"]))

        # Calculate elapsed time and update final status
        elapsed_time = time.time() - start_time
        hours, remainder = divmod(elapsed_time, 3600)
        minutes, seconds = divmod(remainder, 60)

        if self.is_generating:
            message_queue.put(('status', [
                f"✅ İşlem tamamlandı!\nGönderilen Makale: {processed_posts}\nSüre: {int(hours)}s {int(minutes)}d {int(seconds)}s",
                "#00FF00"
            ]))
            message_queue.put(('progress', 1.0))  # Ensure progress bar shows 100%
            message_queue.put(('progress_label', f"Tamamlandı! {processed_posts}/{total_articles}"))
            
            # Force update UI
            self.update_idletasks()
            
        # Reset state
        self.is_generating = False
        self.start_button.configure(text="Makale Oluşturmayı Başlat", fg_color=ACTIVE_COLOR)
        self.update_idletasks()  # Force button update

    # Image handling is now done through URL input

    def add_backlink_url(self):
        # Get backlink URL from entry field
        url = self.backlink_url_entry.get().strip()

        # Validate input field
        if not url:
            self.backlink_status_label.configure(text="❌ Lütfen site URL'sini girin!", text_color="#FF0000")
            return

        # Ensure URL starts with http:// or https://
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url

        # Remove trailing slash if present
        url = url.rstrip('/')

        # Check if backlink already exists
        if url in self.backlinks:
            self.backlink_status_label.configure(text="❌ Bu site zaten eklenmiş!", text_color="#FF0000")
            return

        # Add new backlink as a dictionary with url key
        self.backlinks.append({'url': url})
        self.save_backlinks()
        self.update_backlinks_list()

        # Clear input field
        self.backlink_url_entry.delete(0, 'end')

        # Show success message
        self.backlink_status_label.configure(text="✅ Site başarıyla eklendi!", text_color="#00FF00")

    def setup_help_frame(self):
        # Define helper functions for buttons
        def open_email():
            webbrowser.open("mailto:info@webadhere.com")
            
        def open_whatsapp():
            webbrowser.open("https://wa.me/905411710315")

        def reset_all_data():
            self.sites = []
            self.backlinks = []
            self.articles = []
            self.save_sites()
            self.save_backlinks()
            self.save_articles()
            self.update_sites_list()
            self.update_backlinks_list()
            self.show_help()

        # Configure help frame
        self.help_frame = ctk.CTkFrame(self.main_frame)
        self.help_frame.grid(row=0, column=0, sticky="nsew")
        self.help_frame.grid_columnconfigure(0, weight=1)
        self.help_frame.grid_rowconfigure(1, weight=1)  # Make scrollable frame expand

        # Title
        title_label = ctk.CTkLabel(self.help_frame, text="Yardım ve Destek",
                                font=ctk.CTkFont(size=16, weight="bold"))
        title_label.grid(row=0, column=0, padx=10, pady=5)

        # Create scrollable frame for help content
        help_scroll = ctk.CTkScrollableFrame(self.help_frame)
        help_scroll.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        help_scroll.grid_columnconfigure(0, weight=1)

        # Button frame
        button_frame = ctk.CTkFrame(help_scroll, fg_color="transparent")
        button_frame.grid(row=1, column=0, padx=10, pady=10)

        # Reset button
        reset_button = ctk.CTkButton(button_frame, text="Programı Sıfırla",
                                  command=reset_all_data,
                                  fg_color="#750000", height=35, corner_radius=8)
        reset_button.grid(row=0, column=0, padx=5, pady=10)

        # Mail button
        mail_button = ctk.CTkButton(button_frame, text="Mail",
                                    command=open_email,
                                    fg_color="#2196F3", height=35, corner_radius=8)
        mail_button.grid(row=0, column=1, padx=5, pady=10)

        # WhatsApp button
        whatsapp_button = ctk.CTkButton(button_frame, text="WhatsApp",
                                    command=open_whatsapp,
                                    fg_color="#25D366", height=35, corner_radius=8)
        whatsapp_button.grid(row=0, column=2, padx=5, pady=10)

        # Help sections
        sections = [
            ("Program Güvenliği ve Kullanımı", """
Program Güvenlik Özellikleri:
- Program verilerinizi dışarıya aktarmaz, veriler sadece kurulu olduğu bilgisayarda saklanır.
- Sadece Windows 10 ve 11 üzerinde, internet erişimi ile sağlıklı çalışır.

Dosya Yönetimi:
- Program dosyalarını (sites.json, backlinks.json, articles.json) silmeyin.
- En iyi performans için programı bir klasör içinde çalıştırın.
- Düzenli yedekleme yapmanız önerilir.

WordPress Güvenliği:
- Backlink Manager API eklentisini WordPress sitenize yükleyin ve etkinleştirin.
- Program üzerinden siteyi eklerken API eklentisini kullanarak bağlantıyı sağlayın.
- Site bağlantısını kaldırmak için program üzerinden silebilir ve 'Backlink Manager API' eklentisini devre dışı bırakabilirsiniz.
"""),    

            ("WordPress Site Ekleme", """
1. WordPress sitenizin yönetici paneline giriş yapın.
2. Eklentiler > Yeni Eklenti Ekle > Eklenti Yükle
3. Backlink Manager API eklentisini yükleyin.
4. Site URL'nizi, kullanıcı adınızı ve şifrenizi Backlink Manager Pro'da kullanın.
5. Birden fazla WordPress sitenizi ekleyebilirsiniz.
"""),

            ("Spintax Makale Oluşturma", """
1. Makaleniz yoksa ChatGPT veya Claude gibi bir yapay zeka aracını kullanarak makalenizi oluşturun.
2. Daha sonra yapay zeka aracına makaleniz için spintax formatı oluşturmasını isteyin.
             
    Yapay zekadan spintax makale oluşturma örneği:
    "Lütfen bu makaleyi spintax formatında yaz."

3. Makaleniz spintax formatında aşağıdaki gibi olacaktır:
             
   - Benzer anlamlı kelimeler {kelime1|kelime2|kelime3} şeklinde,
   - Farklı cümle yapıları {cümle1|cümle2|cümle3} şeklinde.
             
4. Her makale için saniyeler içerisinde trilyonlarca farklı varyasyon oluşturabilirsiniz.
5. Her varyasyon özgün ve benzersiz içerik sağlar.
6. Program her makaleye seçtiğiniz linkleri ve görselleri ekler.

Örnek:
{Merhaba|Selam|Hey}, {nasılsın|bugün nasıl gidiyor|nasıl gidiyor}?
"""),

            ("Maksimum Üretilebilir Makale", """
Maksimum üretilebilir makale sayısı, spintax içeriğinizdeki tüm olası kombinasyonların sayısıdır.

Hesaplama örneği:
{A|B|C} {D|E} = 3 x 2 = 6 farklı kombinasyon

Örnek makale:
{Merhaba|Selam} {dostlar|arkadaşlar} = 2 x 2 = 4 farklı kombinasyon
1. Merhaba dostlar
2. Merhaba arkadaşlar
3. Selam dostlar
4. Selam arkadaşlar

Not: Çok fazla spintax kullanımı milyonlarca farklı makale üretebilir!
Cihaz performansınız için bir anda çok fazla yazı üretmeyin.
             
Spintax İpuçları:
- Doğal görünüm için az sayıda alternatif kullanın.
- Dilbilgisi kurallarına dikkat edin.
- Her paragrafta en az bir spintax kullanın.
"""),

            ("Makale Ekle", """
1. Makale başlığınızı spintax formatında girin.
2. Makale içeriğinizi spintax formatında girin.
3. 'Makaleyi Önizle' butonu ile farklı varyasyonları test edin.
4. 'Görsel Ekle' butonu ile tüm makalelere görseller ekleyebilirsiniz.
             
    'WordPress sitenizde, Ortamlar kısmından sitenizdeki görsellere erişebilirsiniz. Görsele tıkladıktan sonra 'Adresi Panoya Kopyala' butonu ile görsel URL'nizi alabilirsiniz.'

5. 'Üretilecek Makale' sayısı, toplamda kaç makale üretileceğini belirler.
6. 'Makale Başına Bağlantı' sayısı, bir makalede kaç adet bağlantı olacağını belirler.
7. 'Makale Üret' butonu ile makalenizi üretin.
"""),

            ("Makale Gönder", """
1. 'Site Başına Makale Sayısı' butonu ile 'Site Yönetimi Sayfasında' eklediğiniz sitelere yüklenecek
makale sayısını girin.
             
    '100 makale ürettiniz, 2 siteniz var. Site başına 50 makale yazılmasını seçerseniz, toplamda 100 makale gönderilir.'

2. 'Makale Durumu' seçimi ile tüm WordPress sitelerinizde **Yayınla** veya **Taslak** seçeneklerini belirleyin.
3. 'Makale Göndermeyi Başlat' butonu ile sınırsız makale gönderimini başlatabilirsiniz.
4. Makale gönderilirken sabırlı olun. Sitelere belirli zaman aşımları uygulanarak gönderilir.
5. Çok fazla makale göndermek sunucunuzu yorabilir ve sitenizin çökmesine neden olabilir. 
Verimli kullanım için daha küçük sayılarda makale gönderimi yapmanız önerilir.
""")
        ]

        # Add help sections
        for i, (title, content) in enumerate(sections, start=3):
            # Section title
            section_label = ctk.CTkLabel(help_scroll, text=title,
                                      font=ctk.CTkFont(size=16, weight="bold"))
            section_label.grid(row=i*2, column=0, padx=10, pady=(20,5), sticky="w")
            
            # Section content
            content_label = ctk.CTkLabel(help_scroll, text=content,
                                      font=ctk.CTkFont(size=12),
                                      wraplength=700, justify="left")
            content_label.grid(row=i*2+1, column=0, padx=10, pady=5, sticky="w")

    def update_backlinks_list(self):
        # Clear existing widgets in backlinks frame
        for widget in self.backlinks_frame.winfo_children():
            widget.destroy()

        # Add backlinks
        for i, backlink in enumerate(self.backlinks):
            # Create frame for backlink row
            row_frame = ctk.CTkFrame(self.backlinks_frame, fg_color="transparent")
            row_frame.grid(row=i, column=0, columnspan=2, padx=10, pady=2, sticky="ew")
            row_frame.grid_columnconfigure(0, weight=3)
            row_frame.grid_columnconfigure(1, weight=0)

            # Extract URL from backlink (handle both string and dict formats)
            backlink_url = backlink['url'] if isinstance(backlink, dict) else backlink
            
            # Show URL without any formatting
            url_label = ctk.CTkLabel(row_frame, text=backlink_url, anchor="w")
            url_label.grid(row=0, column=0, padx=5, pady=2, sticky="w")

            # Delete button with system color scheme
            delete_button = ctk.CTkButton(row_frame, text="❌ Sil",
                                       command=lambda idx=i: self.delete_backlink(idx),
                                       fg_color=INACTIVE_COLOR, height=35, corner_radius=8,
                                       border_spacing=10)
            delete_button.grid(row=0, column=1, padx=5, pady=2, sticky="e")

    def delete_backlink(self, index):
        # Remove backlink from list
        del self.backlinks[index]
        self.save_backlinks()
        self.update_backlinks_list()
        self.backlink_status_label.configure(text="✅ Site başarıyla silindi!", text_color="#00FF00")

    def delete_site(self, index):
        # Remove the site from the list
        if 0 <= index < len(self.sites):
            del self.sites[index]
            self.save_sites()
            self.update_sites_list()
            self.status_label.configure(text="✅ Site başarıyla silindi!", text_color="#00FF00")
        else:
            self.status_label.configure(text="❌ Site silinirken bir hata oluştu!", text_color="#FF0000")

    def show_saved_articles_frame(self):
        self.saved_articles_frame.grid(row=0, column=0, sticky="nsew")
        self.site_frame.grid_forget()
        self.backlink_frame.grid_forget()
        self.article_frame.grid_forget()
        self.help_frame.grid_forget()
        self.process_frame.grid_forget()
        
        # Update menu button states
        self.site_menu_button.configure(fg_color=INACTIVE_COLOR)
        self.backlink_menu_button.configure(fg_color=INACTIVE_COLOR)
        self.article_menu_button.configure(fg_color=INACTIVE_COLOR)
        self.saved_articles_button.configure(fg_color=ACTIVE_COLOR)
        self.process_menu_button.configure(fg_color=INACTIVE_COLOR)
        self.help_button.configure(fg_color=INACTIVE_COLOR)

    def show_help(self):
        self.help_frame.grid(row=0, column=0, sticky="nsew")
        self.site_frame.grid_forget()
        self.backlink_frame.grid_forget()
        self.article_frame.grid_forget()
        self.process_frame.grid_forget()
        
        # Update menu button states
        self.site_menu_button.configure(fg_color=INACTIVE_COLOR)
        self.backlink_menu_button.configure(fg_color=INACTIVE_COLOR)
        self.article_menu_button.configure(fg_color=INACTIVE_COLOR)
        self.process_menu_button.configure(fg_color=INACTIVE_COLOR)
        self.help_button.configure(fg_color=ACTIVE_COLOR)

    def show_saved_articles_frame(self):
        self.saved_articles_frame.grid(row=0, column=0, sticky="nsew")
        self.site_frame.grid_forget()
        self.backlink_frame.grid_forget()
        self.article_frame.grid_forget()
        self.process_frame.grid_forget()
        if self.help_frame:
            self.help_frame.grid_forget()
            
        # Update menu button states
        self.site_menu_button.configure(fg_color=INACTIVE_COLOR)
        self.backlink_menu_button.configure(fg_color=INACTIVE_COLOR)
        self.article_menu_button.configure(fg_color=INACTIVE_COLOR)
        self.process_menu_button.configure(fg_color=INACTIVE_COLOR)
        self.saved_articles_button.configure(fg_color=ACTIVE_COLOR)
        self.help_button.configure(fg_color=INACTIVE_COLOR)

        # Update article list
        self.update_article_list()
        
    def on_closing(self):
        if hasattr(self, 'image_url_entry'):
            self.image_url_entry = None
        if hasattr(self, 'image_panel_window') and self.image_panel_window is not None:
            self.image_panel_window.destroy()
            self.image_panel_window = None

    def show_image_panel(self):
        # Create a new window for image panel
        if hasattr(self, 'image_panel_window') and self.image_panel_window is not None:
            self.image_panel_window.focus()
            return

        self.image_panel_window = ctk.CTkToplevel(self)
        self.image_panel_window.title("Görsel Yönetimi")
        self.image_panel_window.geometry("600x400")
        self.image_panel_window.resizable(False, False)
        self.image_panel_window.transient(self)
        self.image_panel_window.grab_set()

        # Configure grid
        self.image_panel_window.grid_columnconfigure(0, weight=1)
        self.image_panel_window.grid_rowconfigure(2, weight=1)

        # Title
        title_label = ctk.CTkLabel(self.image_panel_window, 
                                  text="Görsel URL'leri",
                                  font=ctk.CTkFont(size=16, weight="bold"))
        title_label.grid(row=0, column=0, padx=10, pady=5)

        # Input frame
        input_frame = ctk.CTkFrame(self.image_panel_window, fg_color="transparent")
        input_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        input_frame.grid_columnconfigure(0, weight=1)

        # URL input
        self.image_url_entry = ctk.CTkEntry(input_frame, 
                                           placeholder_text="Görsel URL'si",
                                           height=35,
                                           width=400)
        self.image_url_entry.grid(row=0, column=0, padx=5)

        # Button frame
        button_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        button_frame.grid(row=0, column=1, padx=5)

        # Add button
        add_button = ctk.CTkButton(button_frame,
                                  text="Ekle",
                                  command=self.add_image_url,
                                  fg_color=ACTIVE_COLOR,
                                  height=35,
                                  width=100)
        add_button.grid(row=0, column=0, padx=2)

        # Save button
        save_button = ctk.CTkButton(button_frame,
                                  text="Kaydet",
                                  command=self.on_closing,
                                  fg_color=ACTIVE_COLOR,
                                  height=35,
                                  width=100)
        save_button.grid(row=0, column=1, padx=2)

        # URLs list frame
        self.urls_frame = ctk.CTkScrollableFrame(self.image_panel_window)
        self.urls_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

        # Update URLs list
        self.update_image_urls_list()

        # Set window protocol
        self.image_panel_window.protocol("WM_DELETE_WINDOW", self.on_closing)

    def add_image_url(self):
        url = self.image_url_entry.get().strip()
        if url:
            if url not in self.image_urls:
                self.image_urls.append(url)
                self.image_url_entry.delete(0, 'end')
                self.update_image_urls_list()

    def update_image_urls_list(self):
        # Clear existing widgets
        for widget in self.urls_frame.winfo_children():
            widget.destroy()

        # Add URLs
        for i, url in enumerate(self.image_urls):
            # Create frame for URL row
            row_frame = ctk.CTkFrame(self.urls_frame, fg_color="transparent")
            row_frame.grid(row=i, column=0, padx=5, pady=2, sticky="ew")
            row_frame.grid_columnconfigure(0, weight=1)

            # Show URL
            url_display = url[:50] + "..." if len(url) > 50 else url
            url_label = ctk.CTkLabel(row_frame, text=url_display, anchor="w")
            url_label.grid(row=0, column=0, padx=5, sticky="w")

            # Delete button
            delete_button = ctk.CTkButton(row_frame,
                                        text="❌ Sil",
                                        command=lambda idx=i: self.delete_image_url(idx),
                                        fg_color=INACTIVE_COLOR,
                                        height=35,
                                        width=60)
            delete_button.grid(row=0, column=1, padx=5)

    def delete_image_url(self, index):
        if 0 <= index < len(self.image_urls):
            self.image_urls.pop(index)
            self.update_image_urls_list()

if __name__ == "__main__":
    app = BacklinkManagerPro()
    app.mainloop()
