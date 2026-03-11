from typing import Optional

from .resend_client import send_email_via_resend


def send_invitation_email(
    to_email: str,
    organizer_name: str,
    restaurant_name: str,
    restaurant_address: Optional[str],
    restaurant_lat: Optional[float],
    restaurant_lng: Optional[float],
    scheduled_at: Optional[str],
    invitation_message: Optional[str],
    accept_url: str,
    decline_url: str,
    frontend_url: str = "https://proximeet.hrconseil.net",
) -> bool:
    """Envoyer une invitation par email via Resend API"""
    
    # Gérer les valeurs None
    safe_organizer = organizer_name or "Quelqu'un"
    safe_restaurant = restaurant_name or "un restaurant"
    safe_date = scheduled_at or "date à préciser"
    
    date_str = f" le {safe_date}" if scheduled_at else ""
    subject = f"🍽️ Invitation à déjeuner - {safe_restaurant}"
    
    # Construire le corps HTML de l'email
    html_body = _build_invitation_html(
        organizer_name=safe_organizer,
        restaurant_name=safe_restaurant,
        restaurant_address=restaurant_address,
        restaurant_lat=restaurant_lat,
        restaurant_lng=restaurant_lng,
        scheduled_at=safe_date,
        invitation_message=invitation_message,
        accept_url=accept_url,
        decline_url=decline_url,
        frontend_url=frontend_url,
    )
    
    # Envoyer via Resend
    success, response = send_email_via_resend(
        to_email=to_email,
        subject=subject,
        body_html=html_body,
    )
    
    if success:
        print(f"[EMAIL] ✅ Invitation envoyée via Resend à {to_email}")
    else:
        print(f"[EMAIL] ❌ Échec envoi Resend: {response}")
    
    return success


def _build_invitation_html(
    organizer_name: str,
    restaurant_name: str,
    restaurant_address: Optional[str],
    restaurant_lat: Optional[float],
    restaurant_lng: Optional[float],
    scheduled_at: Optional[str],
    invitation_message: Optional[str],
    accept_url: str,
    decline_url: str,
    frontend_url: str,
) -> str:
    """Construire le HTML de l'email d'invitation"""
    
    # Gérer les valeurs None
    safe_organizer = organizer_name or "Quelqu'un"
    safe_restaurant = restaurant_name or "un restaurant"
    safe_message = invitation_message or ""
    safe_frontend = frontend_url or "https://proximeet.hrconseil.net"
    
    date_str = f" le {scheduled_at}" if scheduled_at else ""
    
    # Construire le bloc message uniquement si présent
    message_block = f'<div class="message">💬 "{safe_message}"</div>' if safe_message else ''
    
    # Construire le bloc adresse si présent
    address_block = ""
    if restaurant_address:
        address_block = f'<p class="address">📍 {restaurant_address}</p>'
    
    # Construire le lien Google Maps si coordonnées disponibles
    map_link = ""
    if restaurant_lat and restaurant_lng:
        map_url = f"https://www.google.com/maps/search/?api=1&query={restaurant_lat},{restaurant_lng}"
        map_link = f'<p style="margin-top: 10px;"><a href="{map_url}" style="color: #56a3a6; text-decoration: none;">🗺️ Voir sur Google Maps</a></p>'
    
    html_body = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; background: #f5f5f5; }}
        .container {{ max-width: 600px; margin: 20px auto; padding: 30px; background: white; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }}
        .header {{ color: #56a3a6; margin-bottom: 20px; }}
        .btn-accept {{ background: #22c55e; color: white; padding: 12px 24px; text-decoration: none; border-radius: 8px; margin-right: 10px; display: inline-block; font-weight: bold; }}
        .btn-decline {{ background: #ef4444; color: white; padding: 12px 24px; text-decoration: none; border-radius: 8px; display: inline-block; font-weight: bold; }}
        .message {{ background: #f8fafc; padding: 15px; border-left: 4px solid #56a3a6; margin: 15px 0; font-style: italic; }}
        .address {{ background: #f0f9ff; padding: 12px; border-left: 4px solid #0284c7; margin: 15px 0; font-weight: 500; }}
        .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; color: #999; font-size: 0.85em; }}
    </style>
</head>
<body>
    <div class="container">
        <h2 class="header">🍽️ Nouvelle invitation</h2>
        
        <p>Bonjour,</p>
        
        <p><strong>{safe_organizer}</strong> vous invite à déjeuner au restaurant 
        <strong>"{safe_restaurant}"</strong>{date_str}.</p>
        
        {address_block}
        {map_link}
        
        {message_block}
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="{accept_url}" class="btn-accept">✅ Accepter</a>
            <a href="{decline_url}" class="btn-decline">❌ Refuser</a>
        </div>
        
        <p style="color: #666; font-size: 0.9em;">
            Ou connectez-vous sur <a href="{safe_frontend}" style="color: #56a3a6;">Proximeet</a> 
            pour gérer vos invitations.
        </p>
        
        <div class="footer">
            Cet email a été envoyé automatiquement par Proximeet.
        </div>
    </div>
</body>
</html>"""
    
    return html_body
