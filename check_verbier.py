import os
import sys
import requests
from bs4 import BeautifulSoup

URL = "https://verbier4vallees.ch/en/online-shop/activities/opening-session-st.nicholas-express_activity_426820"
SOLD_OUT = "today's ski pass quota has been sold out"


def notify(message):
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    chat_id = os.environ["TELEGRAM_CHAT_ID"]
    resp = requests.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        json={"chat_id": chat_id, "text": message, "disable_web_page_preview": True},
        timeout=20,
    )
    resp.raise_for_status()
    print("Messaggio Telegram inviato.")


def main():
    if os.environ.get("TEST_NOTIFICATION") == "true":
        notify("✅ Test riuscito! Il monitor Verbier può inviarti messaggi.\n" + URL)
        return

    try:
        response = requests.get(
            URL,
            headers={"User-Agent": "Mozilla/5.0 (compatible; personal-availability-monitor/1.0)"},
            timeout=25,
        )
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        text = " ".join(soup.stripped_strings).casefold().replace("’", "'")
        if "st. nicholas express" not in text or "chf" not in text:
            print("Pagina inattesa: verifica manualmente; nessun allarme di disponibilità.")
            return
        if SOLD_OUT in text:
            print("Quota esaurita: nessun messaggio.")
            return
        print("Il messaggio 'quota esaurita' non è stato trovato.")
        notify("🎿 VERBIER CON TRENO: POSSIBILE DISPONIBILITÀ!\n"
               "Il messaggio 'quota esaurita' non compare più sulla pagina. "
               "Non è una conferma di 2 biglietti: controlla subito!\n" + URL)
    except requests.RequestException as exc:
        print(f"Errore rete/sito: {exc}. Nessun falso allarme.")
        sys.exit(1)


if __name__ == "__main__":
    main()
