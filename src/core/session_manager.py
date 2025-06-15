from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
from src.core.bot_runner import BotRunner

class SessionManager:
    def __init__(self):
        self.active_sessions: Dict[str, BotRunner] = {}
        
    def start_bot(self, session_id: str, config_path: Path, secrets_path: Path, resume_path: Optional[Path] = None):
        if session_id in self.active_sessions:
            return {'status': 'error', 'message': 'Session already exists'}
            
        runner = BotRunner()
        result = runner.run(config_path, secrets_path, resume_path)
        
        if result['status'] == 'success':
            self.active_sessions[session_id] = runner
            
        return result
        
    def stop_bot(self, session_id: str) -> dict:
        """
        Stops a bot session and returns enhanced status information
        
        Returns:
            dict: {
                'status': 'success'|'error',
                'message': str,
                'force_terminated': bool (if had to force quit),
                'active_time': float (seconds bot was running),
                'jobs_applied': int (total applications sent)
            }
        """
        if session_id not in self.active_sessions:
            return {
                'status': 'error',
                'message': f'Session {session_id} not found',
                'force_terminated': False,
                'active_time': 0,
                'jobs_applied': 0
            }
            
        runner = self.active_sessions[session_id]
        
        # Get stats before stopping
        stats = {
            'active_time': runner.get_active_time(),
            'jobs_applied': runner.jobs_applied_count
        }
        
        result = runner.stop()  # This calls the stop() we added earlier
        
        if result['status'] == 'success':
            del self.active_sessions[session_id]
            return {
                'status': 'success',
                'message': f'Session {session_id} stopped. {stats["jobs_applied"]} jobs applied',
                'force_terminated': result.get('force_terminated', False),
                **stats
            }
            
        return {
            'status': 'error',
            'message': result['message'],
            'force_terminated': False,
            **stats
        }
        
    def get_status(self, session_id: str):
        runner = self.active_sessions.get(session_id)
        if not runner:
            return {'status': 'error', 'message': 'Session not found'}
            
        return {
            'status': 'success',
            'is_running': runner.is_running,
            'message': 'Bot is running' if runner.is_running else 'Bot is not running'
        }
    
    def get_active_sessions(self) -> dict:
        """Returns information about all active sessions"""
        sessions = []
        total_jobs = 0
        
        for session_id, runner in self.active_sessions.items():
            sessions.append({
                'session_id': session_id,
                'start_time': datetime.fromtimestamp(runner.start_time).isoformat(),
                # 'jobs_applied': runner.jobs_applied_count, # WIP
                # 'current_position': runner.current_position, # WIP
                # 'current_company': runner.current_company # WIP
            })
            # total_jobs += runner.jobs_applied_count
            
        return {
            'active_sessions': sessions,
            # 'total_jobs_applied': total_jobs,
            'total_active_sessions': len(sessions)
        }
