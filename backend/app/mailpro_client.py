"""Client Mailpro API v2 pour Proximeet"""
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from typing import Optional, Tuple

# API v2 endpoint for sending single email
SENDONE_URL = "https://api.mailpro.com/v2/send/sendone.json"


def send_email_via_mailpro(
    to_email: str,
    subject: str,
    body_html: str,
    reply_to: Optional[str] = None,
    id_client: Optional[str] = None,
    api_key: Optional[str] = None,
    id_email_exp: Optional[str] = None,
) -> Tuple[bool, dict]:
    """
    Envoyer un email via Mailpro API v2.
    
    Args:
        to_email: Email du destinataire
        subject: Sujet de l'email
        body_html: Contenu HTML
        reply_to: Email de réponse (optionnel)
        id_client: ID client Mailpro (depuis env ou paramètre)
        api_key: Clé API Mailpro (depuis env ou paramètre)
        id_email_exp: ID de l'email expéditeur (depuis env ou paramètre)
    
    Returns:
        Tuple (succès, réponse_api)
    """
    # Récupérer les credentials depuis les variables d'environnement si non fournis
    id_client = id_client or os.getenv("MAILPRO_IDCLIENT", "")
    api_key = api_key or os.getenv("MAILPRO_API_KEY", "")
    id_email_exp = id_email_exp or os.getenv("MAILPRO_SENDER_ID", "")
    
    # Vérifier que les credentials sont présents
    if not id_client or not api_key or not id_email_exp:
        print("[MAILPRO] ❌ Credentials manquants:")
        print(f"  MAILPRO_IDCLIENT: {'OK' if id_client else 'MANQUANT'}")
        print(f"  MAILPRO_API_KEY: {'OK' if api_key else 'MANQUANT'}")
        print(f"  MAILPRO_SENDER_ID: {'OK' if id_email_exp else 'MANQUANT'}")
        return False, {"error": "Credentials Mailpro manquants"}
    
    # EmailData format: email,field1,field2,...,field25 (25 champs vides)
    email_data = f"{to_email},,,,,,,,,,,,,,,,,,,,,,,,,"
    
    # Construire les données du formulaire
    form_data = {
        "IDClient": id_client,
        "ApiKey": api_key,
        "IDEmailExp": id_email_exp,
        "EmailData": email_data,
        "BodyHTML": body_html,
        "Subject": subject,
    }
    
    if reply_to:
        form_data["ReplyTo"] = reply_to
    
    encoded_data = urllib.parse.urlencode(form_data).encode("utf-8")
    
    # Créer la requête
    req = urllib.request.Request(
        SENDONE_URL,
        data=encoded_data,
        method="POST",
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.0.36",
            "Accept": "application/json",
        }
    )
    
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            response_data = json.loads(body)
            
            if resp.getcode() == 200:
                print(f"[MAILPRO] ✅ Email envoyé avec succès à {to_email}")
                return True, response_data
            else:
                print(f"[MAILPRO] ⚠️ Réponse HTTP {resp.getcode()}: {body}")
                return False, response_data
                
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        print(f"[MAILPRO] ❌ Erreur HTTP {exc.code}: {body}")
        try:
            error_data = json.loads(body)
        except json.JSONDecodeError:
            error_data = {"raw_response": body}
        return False, error_data
        
    except Exception as e:
        print(f"[MAILPRO] ❌ Exception: {e}")
        return False, {"error": str(e)}
