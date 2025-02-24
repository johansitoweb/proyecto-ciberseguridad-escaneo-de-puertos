import flet as ft
import requests

def obtener_respuesta_api(pregunta):
    email = pregunta  
    url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}"

    try:
        respuesta = requests.get(url)
        respuesta.raise_for_status()  
        datos = respuesta.json()

        if datos:
            
            filtraciones = [f"  - {filtracion['Title']}" for filtracion in datos]
            return f"¡El email {email} fue encontrado en las siguientes filtraciones:\n" + "\n".join(filtraciones)
        else:
            return f"¡El email {email} no fue encontrado en ninguna filtración conocida!"

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return f"¡El email {email} no fue encontrado en ninguna filtración conocida!"
        else:
            return f"Error al contactar la API de HIBP: {e}"
    except Exception as e:
        return f"Error al procesar la respuesta de HIBP: {e}"

def main(page: ft.Page):
    page.title = "Chatbot de Ciberseguridad (HIBP)"

    chat_area = ft.Column()
    user_input = ft.TextField(hint_text="Ingresa el email a verificar...")

    def send_message(e):
        message = user_input.value
        chat_area.controls.append(ft.Text(f"Tú: {message}"))
        respuesta = obtener_respuesta_api(message)
        chat_area.controls.append(ft.Text(f"Chatbot: {respuesta}"))
        user_input.value = ""
        page.update()

    page.add(
        chat_area,
        ft.Row(
            [
                user_input,
                ft.ElevatedButton("Enviar", on_click=send_message),
            ]
        ),
    )

ft.app(target=main)