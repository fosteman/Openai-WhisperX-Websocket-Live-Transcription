from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import whisper
import asyncio

app = FastAPI()

model = whisper.load_model("base")

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Streaming Whisper WebSocket Service</title>
    </head>
    <body>
        <h1>WebSocket Test</h1>
        <button onclick="startWebSocket()">Start WebSocket</button>
        <p id="transcript"></p>
        <script>
            let socket;
            function startWebSocket() {
                socket = new WebSocket("ws://localhost:8000/ws");
                socket.onmessage = function(event) {
                    document.getElementById("transcript").innerText += event.data + "\\n";
                };
                socket.onclose = function(event) {
                    console.log("WebSocket closed: ", event);
                };
                socket.onerror = function(error) {
                    console.log("WebSocket error: ", error);
                };
            }
        </script>
    </body>
</html>
"""

@app.get("/")
async def get():
    return HTMLResponse(html)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            result = model.transcribe(data, language='en')
            await websocket.send_text(result['text'])
    except Exception as e:
        await websocket.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

