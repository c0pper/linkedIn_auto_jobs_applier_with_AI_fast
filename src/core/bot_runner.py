import os
from threading import Thread, Event
from pathlib import Path
import time
from typing import Optional
import yaml
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from src.core.original_files.main import FileManager, create_bot, run_bot
from src.core.original_files.utils import chromeBrowserOptions  # Import your existing function

class BotRunner:
    def __init__(self):
        self.stop_event = Event()
        self.thread = None
        self.driver = None
        self.start_time = None
        self.jobs_applied_count = 0 # WIP
        self.current_position = None # WIP
        self.current_company = None # WIP
        
    def run(self, config_path: Path, secrets_path: Path, resume_path: Optional[Path] = None):
        """Run the bot in a separate thread"""
        self.start_time = time.time()
        if self.thread and self.thread.is_alive():
            return {'status': 'error', 'message': 'Bot is already running'}
            
        self.stop_event.clear()
        
        # Load configuration
        with open(config_path, 'r') as f:
            parameters = yaml.safe_load(f)
        with open(secrets_path, 'r') as f:
            secrets = yaml.safe_load(f)
        

        parameters['uploads'] = FileManager.file_paths_to_dict(None, resume_path)
        parameters['outputFileDirectory'] = str(Path(os.getenv('DATA_FOLDER')) / "output")

        # Prepare args for original function
        args = {
            'email': secrets['email'],
            'password': secrets['password'],
            'parameters': parameters,
            'openai_api_key': secrets['openai_api_key']
        }
        
        def bot_wrapper():
            try:
                # Initialize browser with options that allow for remote control
                options = chromeBrowserOptions()
                service = ChromeService(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=options)
                # self.driver = webdriver.Remote(
                #     command_executor=os.getenv('SELENIUM_REMOTE_URL', 'http://localhost:4444'),
                #     options=options
                # )
                
                # Run the original bot logic
                bot = create_bot(driver=self.driver, **args)
                run_bot(bot)
                
            except Exception as e:
                print(f"Bot error: {str(e)}")
            finally:
                if self.driver:
                    self.driver.quit()
                    self.driver = None
        
        self.thread = Thread(target=bot_wrapper)
        self.thread.start()
        return {'status': 'success', 'message': 'Bot started'}
        
    def stop(self):
        """Returns dict with stop details including force flag"""
        was_running = self.thread and self.thread.is_alive()
        needed_force = False
        
        if was_running:
            self.stop_event.set()
            try:
                # Try graceful shutdown first
                self.thread.join(timeout=5)
                if self.thread.is_alive():
                    needed_force = True
                    if self.driver:
                        self.driver.quit()  # Force quit if not responding
            except Exception:
                needed_force = True
                
        return {
            'status': 'success' if was_running else 'error',
            'message': 'Force stopped' if needed_force else 'Gracefully stopped',
            'force_terminated': needed_force
        }
        
    def get_active_time(self) -> float:
        """Returns seconds since bot started"""
        return time.time() - self.start_time if self.start_time else 0
        
    # WIP
    def update_current_job(self, position: str, company: str):
        """Call this when starting a new job application"""
        self.current_position = position
        self.current_company = company
    
    @property
    def is_running(self):
        return self.thread and self.thread.is_alive()
