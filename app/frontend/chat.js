const chatToggle = document.getElementById("chat-toggle")
const chatContainer = document.getElementById("chat-container")
const closeBtn = document.getElementById("close-btn")

const sendBtn = document.getElementById("send-btn")
const chatInput = document.getElementById("chat-input")
const chatMessages = document.getElementById("chat-messages")

const userIdKey = "chatUserId"


chatToggle.onclick = () => {

    chatContainer.style.display = "flex"

}

closeBtn.onclick = () => {

    chatContainer.style.display = "none"

}
function getUserId(){
    let id = localStorage.getItem(userIdKey)
    if(!id){
        id = crypto.randomUUID ? crypto.randomUUID() : Math.random().toString(36).slice(2)
        localStorage.setItem(userIdKey,id)
    }
    return id
}

function addMessage(text,className){

    const msg = document.createElement("div")

    msg.classList.add("message",className)

    msg.innerText = text

    chatMessages.appendChild(msg)

    chatMessages.scrollTop = chatMessages.scrollHeight

}
function showTyping() {

    const typing = document.createElement("div")

    typing.classList.add("message", "bot")

    typing.id = "typing"

    typing.innerText = "Bot is typing..."

    chatMessages.appendChild(typing)

    chatMessages.scrollTop = chatMessages.scrollHeight
}

function removeTyping() {

    const typing = document.getElementById("typing")

    if (typing) {
        typing.remove()
    }

}


async function loadHistory(){
    const userId = getUserId()
    try{
        const res = await fetch(`http://localhost:8000/history?user_id=${encodeURIComponent(userId)}`)
        const data = await res.json()
        if(Array.isArray(data.history)){
            data.history.forEach(entry => addMessage(entry.text, entry.role === "user" ? "user" : "bot"))
        }
    }catch(err){
        console.error("Failed to load history",err)
    }
}


async function sendMessage() {

    const query = chatInput.value

    if (!query) return

    addMessage(query, "user")

    chatInput.value = ""

    showTyping()
    const botMsg = document.createElement("div")

    botMsg.classList.add("message","bot")

    chatMessages.appendChild(botMsg)
    chatMessages.scrollTop = chatMessages.scrollHeight

    try{
    const response = await fetch("http://localhost:8000/ask", {

        method: "POST",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({
            query: query,
            user_id: getUserId()
        })

    })
const reader = response.body.getReader()

    const decoder = new TextDecoder()

    while(true){

        const {done,value} = await reader.read()

        if(done) break

        botMsg.innerText += decoder.decode(value)

        chatMessages.scrollTop = chatMessages.scrollHeight

    }
    }catch(err){
        botMsg.innerText = "Sorry, something went wrong."
        console.error(err)
    }finally{
        removeTyping()
    }

}


sendBtn.addEventListener("click", (e) => {
    e.preventDefault()
    sendMessage()
})


chatInput.addEventListener("keypress", function (e) {

    if (e.key === "Enter") {
        e.preventDefault()
        sendMessage()
    }

})
loadHistory()
