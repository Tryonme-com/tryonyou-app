import os
from datetime import datetime

def set_launch_timer():
    print("--- ⏳ ACTIVANDO CUENTA ATRÁS: GALERIES LAFAYETTE ---")
    html_path = "index.html"
    
    timer_html = """
    <div id="launch-timer" style="margin-top:20px; color:#D4AF37; font-family:'Inter', sans-serif; font-size:1.2rem; letter-spacing:3px;">
        LANCEMENT OFFICIEL : MAI 2026 | <span id="days-count">--</span> JOURS RESTANTS
    </div>
    <script>
        const targetDate = new Date('May 1, 2026 00:00:00').getTime();
        function updateTimer() {
            const now = new Date().getTime();
            const distance = targetDate - now;
            const days = Math.floor(distance / (1000 * 60 * 60 * 24));
            document.getElementById('days-count').innerHTML = days;
        }
        setInterval(updateTimer, 1000);
        updateTimer();
    </script>
    """
    
    if os.path.exists(html_path):
        with open(html_path, "r") as f:
            content = f.read()
        
        if "launch-timer" not in content:
            # Lo inyectamos justo debajo del titular principal
            new_content = content.replace("</h1>", f"</h1>{timer_html}")
            with open(html_path, "w") as f:
                f.write(new_content)
            print("✅ Cuenta atrás inyectada correctamente.")
        else:
            print("⚠️ El contador ya está activo.")

if __name__ == "__main__":
    set_launch_timer()
