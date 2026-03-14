const chatToggle = document.getElementById("chat-toggle")
const chatContainer = document.getElementById("chat-container")
const closeBtn = document.getElementById("close-btn")

const sendBtn = document.getElementById("send-btn")
const chatInput = document.getElementById("chat-input")
const chatMessages = document.getElementById("chat-messages")

const userIdKey = "chatUserId"


function renderMarkdown(text) {
    const raw = text || ""
    // Sanitize rendered HTML to avoid XSS while preserving formatting
    return DOMPurify.sanitize(marked.parse(raw))
}

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

    msg.innerHTML = renderMarkdown(text)

    chatMessages.appendChild(msg)

    chatMessages.scrollTop = chatMessages.scrollHeight

}
function showTyping() {

    const typing = document.createElement("div")

    typing.classList.add("message", "bot")

    typing.id = "typing"

    typing.innerHTML = `Bot is typing<span class="blinking-cursor">|</span>`

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
    sendBtn.disabled = true

    showTyping()
    let botMsg = null
    
    let botText = ""
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

        botText += decoder.decode(value)

        if(!botMsg){
            botMsg = document.createElement("div")
            botMsg.classList.add("message","bot","streaming")
            chatMessages.appendChild(botMsg)
            removeTyping()
        }

        botMsg.innerHTML = renderMarkdown(botText)

        chatMessages.scrollTop = chatMessages.scrollHeight

    }
    }catch(err){
        if(!botMsg){
            botMsg = document.createElement("div")
            botMsg.classList.add("message","bot","streaming")
            chatMessages.appendChild(botMsg)
        }
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
