from datetime import datetime
import os
from pathlib import Path
import time
import gradio as gr
import requests
from dotenv import load_dotenv
load_dotenv()

API_URL = os.getenv("API_URL", "http://api:8054/api")


def list_yml_files():
    data_folder = os.getenv("DATA_FOLDER")
    if not data_folder:
        return []

    p = Path(data_folder)
    if not p.exists() or not p.is_dir():
        return []

    # List all *.yml files (only filenames, or full paths if you prefer)
    files = [str(f) for f in p.glob("*.yml")] + [str(f) for f in p.glob("*.yaml")]
    return files

def start_bot_ui(config_path, secrets_path, resume_path):
    # Generate session_id based on current time, e.g. 20250615_153045
    session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    payload = {
        "session_id": session_id,
        "config_path": config_path,
        "secrets_path": secrets_path,
        "resume_path": resume_path or None
    }
    try:
        response = requests.post(f"{API_URL}/start", json=payload)
        return response.json(), f"✅ Bot {session_id} started."
    except Exception as e:
        return {}, f"❌ Error: {str(e)}"

def stop_bot_ui(session_id):
    try:
        response = requests.post(f"{API_URL}/stop", params={"session_id": session_id})
        return response.json(), f"🛑 Stopped {session_id}" if response.ok else "❌ Failed to stop session."
    except Exception as e:
        return {}, f"❌ Error: {str(e)}"

def list_sessions_ui():
    response = requests.get(f"{API_URL}/sessions/active")
    data = response.json()
    if not data["active_sessions"]:
        return "No active sessions."
    table = "### Active Sessions\n\n| Session ID | Jobs Applied | Start Time |\n|------------|--------------|------------|\n"
    for session in data["active_sessions"]:
        table += f"| {session['session_id']} | {session.get('jobs_applied', 'N/A')} | {session.get('start_time', 'N/A')} |\n"
    table += f"\n**Total Active Sessions**: {data['total_active_sessions']}"
    return table

def get_active_session_ids():
    try:
        response = requests.get(f"{API_URL}/sessions/active")
        data = response.json()
        return [session["session_id"] for session in data.get("active_sessions", [])]
    except Exception:
        return []

def clear_message():
    return gr.Textbox.update(value="", visible=False)




def build_gradio_interface():
    yml_files = list_yml_files()
    config_list = [f for f in yml_files if "config" in f.lower()]
    secrets_list = [f for f in yml_files if "secrets" in f.lower()]
    resume_list = [f for f in yml_files if "resume" in f.lower()]

    with gr.Blocks(title="LinkedIn Bot Control Panel", css=".section {border: 1px solid #e0e0e0; border-radius: 8px; padding: 15px; margin-bottom: 20px;}") as demo:
        gr.Markdown("# 🤖 LinkedIn Auto-Apply Bot Dashboard")

        # Start Bot Section
        with gr.Column(elem_classes=["section"]):
            gr.Markdown("## 🚀 Start New Bot Session")
            start_msg = gr.Textbox(visible=False, interactive=False, show_label=False)
            with gr.Row():
                config_path = gr.Dropdown(label="Config Path", choices=config_list, value=config_list[0] if config_list else None)
                secrets_path = gr.Dropdown(label="Secrets Path", choices=secrets_list, value=secrets_list[0] if secrets_list else None)
                resume_path = gr.Dropdown(label="Resume Path", choices=["None"] + resume_list, value=resume_list[0] if resume_list else None)
            with gr.Row():
                start_button = gr.Button("Start Bot", variant="primary")
            start_output = gr.JSON(label="Response", visible=False)

            start_button.click(
                fn=start_bot_ui,
                inputs=[config_path, secrets_path, resume_path],
                outputs=[start_output, start_msg]
            )

        # Stop Bot Section
        with gr.Column(elem_classes=["section"]):
            gr.Markdown("## 🛑 Stop Running Bot")
            stop_msg = gr.Textbox(visible=False, interactive=False, show_label=False)
            with gr.Row():
                stop_dropdown = gr.Dropdown(label="Active Sessions", choices=get_active_session_ids(), interactive=True, allow_custom_value=True)
                reload_dropdown_button = gr.Button("🔄 Refresh Session List")
            with gr.Row():
                stop_button = gr.Button("Stop Selected Bot", variant="stop")
            stop_output = gr.JSON(label="Response", visible=False)

            reload_dropdown_button.click(fn=get_active_session_ids, outputs=stop_dropdown)
            stop_button.click(fn=stop_bot_ui, inputs=stop_dropdown, outputs=[stop_output, stop_msg])

        # Active Sessions Section
        with gr.Column(elem_classes=["section"]):
            gr.Markdown("## 📋 Active Sessions")
            with gr.Row():
                refresh_button = gr.Button("🔄 Refresh Sessions")
            session_output = gr.Markdown()
            refresh_button.click(list_sessions_ui, outputs=session_output)
            
            # Initial load of sessions
            demo.load(fn=list_sessions_ui, outputs=session_output)

    return demo

gradio_app = build_gradio_interface().queue()
if __name__ == "__main__":
    gradio_app.launch(server_name="0.0.0.0", server_port=7860)
