const chatToggle = document.getElementById("chat-toggle")
const chatContainer = document.getElementById("chat-container")
const closeBtn = document.getElementById("close-btn")

const sendBtn = document.getElementById("send-btn")
const chatInput = document.getElementById("chat-input")
const chatMessages = document.getElementById("chat-messages")


chatToggle.onclick = () => {

    chatContainer.style.display = "flex"

}

closeBtn.onclick = () => {

    chatContainer.style.display = "none"

}


function addMessage(text, className){

    const msg = document.createElement("div")

    msg.classList.add("message", className)

    msg.innerText = text

    chatMessages.appendChild(msg)

    chatMessages.scrollTop = chatMessages.scrollHeight

}


async function sendMessage(){

    const query = chatInput.value

    if(!query) return

    addMessage(query,"user")

    chatInput.value = ""

    const response = await fetch("http://localhost:8000/ask",{

        method:"POST",

        headers:{
            "Content-Type":"application/json"
        },

        body:JSON.stringify({
            query:query
        })

    })

    const data = await response.json()

    addMessage(data.answer,"bot")

}


sendBtn.onclick = sendMessage


chatInput.addEventListener("keypress",function(e){

    if(e.key === "Enter"){
        sendMessage()
    }

})