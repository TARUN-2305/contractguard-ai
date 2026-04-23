import os
import time
import subprocess
import traceback
from playwright.sync_api import sync_playwright

def generate_manual_screenshots():
    # Setup paths
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    assets_dir = os.path.join(base_dir, "docs", "assets")
    os.makedirs(assets_dir, exist_ok=True)
    log_path = os.path.join(base_dir, "AGENTS_LOG.md")
    
    # Boot Streamlit App
    app_path = os.path.join(base_dir, "app", "app.py")
    print(f"Booting Streamlit: {app_path}")
    process = subprocess.Popen(
        ["streamlit", "run", app_path, "--server.headless", "true"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for init
    print("Waiting 10 seconds for Streamlit server to initialize...")
    time.sleep(10)

    personas = ["Contract Manager", "Project Manager", "Site Engineer", "Auditor", "Contractor Rep"]
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            # Navigate to the app
            page.goto("http://localhost:8501")
            page.wait_for_load_state("networkidle")
            time.sleep(5)  # Let streamlit fully load its DOM

            for persona in personas:
                print(f"Capturing screenshot for: {persona}")
                
                # Click the radio button label matching the persona exact text
                page.get_by_text(persona, exact=True).click()
                
                # Wait for the page content to update
                page.wait_for_timeout(2000)
                
                # Take screenshot
                safe_name = persona.lower().replace(" ", "_")
                screenshot_path = os.path.join(assets_dir, f"screenshot_{safe_name}.png")
                page.screenshot(path=screenshot_path, full_page=True)
                
            browser.close()
            print("Capture sequence complete.")
            
    except Exception as e:
        error_msg = f"\n[ERROR] Playwright UI Navigation Failed:\n{traceback.format_exc()}\n"
        print(error_msg)
        with open(log_path, "a") as f:
            f.write(f"\n[2026-04-23] [Agent-Doc] [CRITICAL ERROR] - UI capture failed. {str(e)}\n")
        
        process.terminate()
        process.wait()
        raise e
        
    finally:
        # Cleanup Streamlit process
        print("Terminating Streamlit server...")
        process.terminate()
        process.wait()

if __name__ == "__main__":
    generate_manual_screenshots()
