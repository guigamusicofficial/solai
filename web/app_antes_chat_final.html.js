const messages = document.getElementById("messages");
const composer = document.getElementById("composer");
const input = document.getElementById("messageInput");

function addMessage(text, role="user"){
  const row = document.createElement("div");
  row.className = `msg ${role}`;
  if(role === "assistant"){
    row.innerHTML = `<img src="/web/assets/sol_thumb.png"><div><div class="bubble"></div><time>agora</time></div>`;
  }else{
    row.innerHTML = `<div><div class="bubble"></div><time>agora ✓✓</time></div>`;
  }
  row.querySelector(".bubble").textContent = text;
  messages.appendChild(row);
  messages.scrollTop = messages.scrollHeight;
}

async function sendMessage(text){
  if(!text.trim()) return;
  addMessage(text,"user");
  input.value="";
  try{
    const r = await fetch("/api/chat",{
      method:"POST",
      headers:{"Content-Type":"application/json"},
      body:JSON.stringify({message:text})
    });
    const data = await r.json();
    if(data.resposta) addMessage(data.resposta,"assistant");
    else addMessage("Estou aqui, Guiga.","assistant");
  }catch(e){
    addMessage("O servidor da Sol não respondeu agora.","assistant");
  }
}

composer.addEventListener("submit",e=>{
  e.preventDefault();
  sendMessage(input.value);
});

document.querySelectorAll(".companion,.right-card").forEach(card=>{
  card.addEventListener("click",()=>{
    const name = card.dataset.character;
    document.querySelectorAll(".companion,.right-card").forEach(x=>x.classList.remove("active"));
    document.querySelectorAll(`[data-character="${name}"]`).forEach(x=>x.classList.add("active"));
    const labels={sol:"Sol AI ♛",luna:"Luna ☾",maya:"Maya ☀",valentina:"Valentina ♥"};
    document.getElementById("chatName").textContent=labels[name];
  });
});

document.getElementById("newChat").addEventListener("click",()=>{
  messages.innerHTML="";
  addMessage("Nova conversa iniciada. Estou aqui, Guiga.","assistant");
});

document.querySelectorAll(".nav-item").forEach(item=>{
  item.addEventListener("click",()=>{
    document.querySelectorAll(".nav-item").forEach(x=>x.classList.remove("active"));
    item.classList.add("active");
  });
});
