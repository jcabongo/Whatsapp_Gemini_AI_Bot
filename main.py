import google.generativeai as genai
from flask import Flask,request,jsonify
import requests
import os
import fitz

wa_token=os.environ.get("WA_TOKEN")
genai.configure(api_key=os.environ.get("GEN_API"))
phone_id=os.environ.get("PHONE_ID")
phone=os.environ.get("PHONE_NUMBER")
name="Três Seis Nove" #The bot will consider this person as its owner or creator
bot_name="Isabel" #This will be the name of your bot, eg: "Hello I am Astro Bot"
model_name="gemini-1.5-flash" #Switch to "gemini-1.0-pro" or any free model, if "gemini-1.5-flash" becomes paid in future.

app=Flask(__name__)

generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 0,
  "max_output_tokens":  6000,
}

safety_settings = [
  {"category": "HARM_CATEGORY_HARASSMENT","threshold": "BLOCK_MEDIUM_AND_ABOVE"},
  {"category": "HARM_CATEGORY_HATE_SPEECH","threshold": "BLOCK_MEDIUM_AND_ABOVE"},  
  {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT","threshold": "BLOCK_MEDIUM_AND_ABOVE"},
  {"category": "HARM_CATEGORY_DANGEROUS_CONTENT","threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]

model = genai.GenerativeModel(model_name=model_name,
                              generation_config=generation_config,
                              safety_settings=safety_settings)

convo = model.start_chat(history=[
])

convo.send_message(f'''

Regra

Regra para Respostas do Bot
Objetividade: Responde apenas ao que foi perguntado, sem informações extras desnecessárias.
Clareza: Usa frases curtas e linguagem fácil de entender.
Qualidade: Oferece uma resposta completa e útil, mesmo que breve.
Relevância: Foca no contexto da pergunta e evita divagações.
Tamanho Máximo: Mantém as respostas entre 1 a 3 frases sempre que possível.
Nao seja muito repetitivo

Formatação de texto: Usa sempre a formatação Justify para apresentar os texto, usa espaços entre os paragrafos, carrega os titlos, usa tambem um espaço pequeno entre titlo e informações do paragrafo, portugues Portugal.

O seu nome é Isabel, assistente virtual da Três Seis Nove , o teu objetivo é conversar com todos clientes que entrar em contacto, age sempre como um bom vendedor, usa tecnicas bem sucedidas de 
atendimento que vendedores de sucesso ja usaram, logo no contacto inicial convida o cliente a se sentir a vontade para conversar contigo, seja dinâmico, conversa de forma diferente com cada cliente, 
não podes usar a mesma abordagem para todos cliente, porque cada cliente é unico e nós temos que tratar ele como especial, procura conhecer também o cliente, isso vai fazer que o cliente se sinta mais valorizado.
Evita excesso de informação nos clientes e também não complica o cliente com perguntas desnessarios, seja proativo e simples.
                      
Sobre a Três Seis Nove automação: 
Usa as informações que estao no nosso website https://www.tresseisnove.online, apresenta uma breve introdução sobre a nós e nao enche o cliente com muita informação a princípio, foca-se na nossa missão, visão e valores

Nossos Serviços: 
Apresenta os nossos serviços no nosso website de forma proativa, pergunta ao cliente, faça perguntas ou gatilhos mentais para saber mais sobre o cliente. Saiba tambem que o teu foco não é só mostrar os nossos serviços mas sim as vantanges que o nossos serviços apresenta, por isso procura o máximo possível entender as nescessidades dos nossos clientes, saiba a dor dele, assim que descobrir onde esta a dor ou a ferida dele, toca mais nisso até lhe convencer que a Três Seis Nove é a melhor opção para ele.

Porque escolher-nos ou Nossos Direnciais: 
Apresenta ao cliente os pontos fortes que nós temos, convencendo ele a solicitar os nossos serviços.

Como Trabalhamos ou nossos Procesos: 
Apresenta ao cliente sobre a forma como trabalhamos apresentado nossso website, excrecça a ele os pontos para que ele compreenda os processos todos.

O teu foco é fechar a vendas dos nossos serviços no nosso website, só no final da conversa leva o cliente a agendar uma reunião ou demostração connosco ao clicar neste link: https://www.tresseisnove.online/#contact e tambem apresenta uma abordagem de ele continuar com a conversa sabendo mais.

Seja mais proativo, se um cliente fazer uma pergunta que não tem nada a ver com o que esta na nossa base de dados, agradeça a ele pela pergunta e responda de forma respeitosa que a nossa startup não oferece esse tipo de serviço por isso não tens  como responder mas entendes sim a situação dele e vás encaminhar a um gestor de vendas para que ele tome conta disso.

.''')


def send(answer):
    url=f"https://graph.facebook.com/v21.0/{phone_id}/messages"
    headers={
        'Authorization': f'Bearer {wa_token}',
        'Content-Type': 'application/json'
    }
    data={
          "messaging_product": "whatsapp", 
          "to": f"{phone}", 
          "type": "text",
          "text":{"body": f"{answer}"},
          }
    
    response=requests.post(url, headers=headers,json=data)
    return response

def remove(*file_paths):
    for file in file_paths:
        if os.path.exists(file):
            os.remove(file)
        else:pass

@app.route("/",methods=["GET","POST"])
def index():
    return "Bot"

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if mode == "subscribe" and token == "BOT":
            return challenge, 200
        else:
            return "Failed", 403
    elif request.method == "POST":
        try:
            data = request.get_json()["entry"][0]["changes"][0]["value"]["messages"][0]
            if data["type"] == "text":
                prompt = data["text"]["body"]
                convo.send_message(prompt)
                send(convo.last.text)
            else:
                media_url_endpoint = f'https://graph.facebook.com/v18.0/{data[data["type"]]["id"]}/'
                headers = {'Authorization': f'Bearer {wa_token}'}
                media_response = requests.get(media_url_endpoint, headers=headers)
                media_url = media_response.json()["url"]
                media_download_response = requests.get(media_url, headers=headers)
                if data["type"] == "audio":
                    filename = "/tmp/temp_audio.mp3"
                elif data["type"] == "image":
                    filename = "/tmp/temp_image.jpg"
                elif data["type"] == "document":
                    doc=fitz.open(stream=media_download_response.content,filetype="pdf")
                    for _,page in enumerate(doc):
                        destination="/tmp/temp_image.jpg"
                        pix = page.get_pixmap()
                        pix.save(destination)
                        file = genai.upload_file(path=destination,display_name="tempfile")
                        response = model.generate_content(["What is this",file])
                        answer=response._result.candidates[0].content.parts[0].text
                        convo.send_message(f"This message is created by an llm model based on the image prompt of user, reply to the user based on this: {answer}")
                        send(convo.last.text)
                        remove(destination)
                else:send("This format is not Supported by the bot ☹")
                with open(filename, "wb") as temp_media:
                    temp_media.write(media_download_response.content)
                file = genai.upload_file(path=filename,display_name="tempfile")
                response = model.generate_content(["What is this",file])
                answer=response._result.candidates[0].content.parts[0].text
                remove("/tmp/temp_image.jpg","/tmp/temp_audio.mp3")
                convo.send_message(f"This is an voice/image message from user transcribed by an llm model, reply to the user based on the transcription: {answer}")
                send(convo.last.text)
                files=genai.list_files()
                for file in files:
                    file.delete()
        except :pass
        return jsonify({"status": "ok"}), 200
if __name__ == "__main__":
    app.run(debug=True, port=8000)
