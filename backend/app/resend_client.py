"""Client Resend API pour Proximeet"""
import json
import os
import urllib.error
import urllib.request
from typing import Optional, Tuple

RESEND_API_URL = "https://api.resend.com/emails"


def send_email_via_resend(
    to_email: str,
    subject: str,
    body_html: str,
    reply_to: Optional[str] = None,
    from_email: Optional[str] = None,
    api_key: Optional[str] = None,
) -> Tuple[bool, dict]:
    """
    Envoyer un email via Resend API.
    
    Args:
        to_email: Email du destinataire
        subject: Sujet de l'email
        body_html: Contenu HTML
        reply_to: Email de réponse (optionnel)
        from_email: Email expéditeur (défaut: on_reply@proximeet.resend.dev)
        api_key: Clé API Resend (depuis env ou paramètre)
    
    Returns:
        Tuple (succès, réponse_api)
    """
    api_key = api_key or os.getenv("RESEND_API_KEY", "")
    from_email = from_email or os.getenv("RESEND_FROM_EMAIL", "invitations@hrconseil.net")
    
    if not api_key:
        print("[RESEND] ❌ Clé API manquante (RESEND_API_KEY)")
        return False, {"error": "Clé API Resend manquante"}
    
    payload = {
        "from": f"Proximeet <{from_email}>",
        "to": [to_email],
        "subject": subject,
        "html": body_html,
    }
    
    if reply_to:
        payload["reply_to"] = reply_to
    
    data = json.dumps(payload).encode("utf-8")
    
    req = urllib.request.Request(
        RESEND_API_URL,
        data=data,
        method="POST",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        }
    )
    
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode("utf-8")
            response_data = json.loads(body)
            
            if resp.getcode() in (200, 202):
                print(f"[RESEND] ✅ Email envoyé avec succès à {to_email}")
                print(f"[RESEND]   ID: {response_data.get('id')}")
                return True, response_data
            else:
                print(f"[RESEND] ⚠️ Réponse HTTP {resp.getcode()}: {body}")
                return False, response_data
                
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8")
        print(f"[RESEND] ❌ Erreur HTTP {exc.code}: {body}")
        try:
            error_data = json.loads(body)
        except json.JSONDecodeError:
            error_data = {"raw_response": body}
        return False, error_data
        
    except Exception as e:
        print(f"[RESEND] ❌ Exception: {e}")
        return False, {"error": str(e)}
