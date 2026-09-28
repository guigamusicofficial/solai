const messages = document.getElementById("messages");
const composer = document.getElementById("composer");
const input = document.getElementById("messageInput");

const labels = {
  sol: "Sol AI ♛",
  luna: "Luna ☾",
  maya: "Maya ☀",
  valentina: "Valentina ♥",
  jade: "Jade ♣"
};

let enviando = false;

function addMessage(text, role = "user") {
  const row = document.createElement("div");
  row.className = `msg ${role}`;

  if (role === "assistant") {
    row.innerHTML = `
      <img src="/web/assets/sol_thumb.png" alt="Sol">
      <div>
        <div class="bubble"></div>
        <time>agora</time>
      </div>
    `;
  } else {
    row.innerHTML = `
      <div>
        <div class="bubble"></div>
        <time>agora ✓✓</time>
      </div>
    `;
  }

  row.querySelector(".bubble").textContent = text;
  messages.appendChild(row);
  messages.scrollTop = messages.scrollHeight;

  return row;
}

function addTyping() {
  const row = document.createElement("div");
  row.className = "msg assistant typing-message";

  row.innerHTML = `
    <img src="/web/assets/sol_thumb.png" alt="Sol">
    <div>
      <div class="bubble">Sol está digitando...</div>
      <time>agora</time>
    </div>
  `;

  messages.appendChild(row);
  messages.scrollTop = messages.scrollHeight;

  return row;
}

async function sendMessage(text) {
  text = text.trim();

  if (!text || enviando) return;

  enviando = true;

  addMessage(text, "user");
  input.value = "";
  input.focus();

  const typing = addTyping();

  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        message: text
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const data = await response.json();

    typing.remove();

    if (data.resposta) {
      addMessage(data.resposta, "assistant");
    } else if (data.error) {
      addMessage(`Erro: ${data.error}`, "assistant");
    } else {
      addMessage("Estou aqui, Guiga.", "assistant");
    }

  } catch (erro) {
    typing.remove();

    console.error("Erro no chat:", erro);

    addMessage(
      "Não consegui falar com o servidor da Sol agora.",
      "assistant"
    );

  } finally {
    enviando = false;
    input.focus();
  }
}


/* =========================================================
   ENVIO DA MENSAGEM
   ========================================================= */

composer.addEventListener("submit", (event) => {
  event.preventDefault();
  sendMessage(input.value);
});


/* Enter envia a mensagem.
   Shift + Enter mantém o comportamento normal. */

input.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    composer.requestSubmit();
  }
});


/* =========================================================
   SELEÇÃO DAS PERSONAGENS
   ========================================================= */

document.querySelectorAll(".companion, .right-card").forEach(card => {

  card.addEventListener("click", () => {

    const name = card.dataset.character;

    document
      .querySelectorAll(".companion, .right-card")
      .forEach(item => item.classList.remove("active"));

    document
      .querySelectorAll(`[data-character="${name}"]`)
      .forEach(item => item.classList.add("active"));

    const chatName = document.getElementById("chatName");

    if (chatName) {
      chatName.textContent = labels[name] || name;
    }
  });

});


/* =========================================================
   NOVA CONVERSA
   ========================================================= */

const newChat = document.getElementById("newChat");

if (newChat) {

  newChat.addEventListener("click", () => {

    messages.innerHTML = "";

    addMessage(
      "Nova conversa iniciada. Estou aqui, Guiga.",
      "assistant"
    );

    input.focus();
  });

}


/* =========================================================
   MENU LATERAL
   ========================================================= */

document.querySelectorAll(".nav-item").forEach(item => {

  item.addEventListener("click", () => {

    document
      .querySelectorAll(".nav-item")
      .forEach(x => x.classList.remove("active"));

    item.classList.add("active");
  });

});


/* =========================================================
   FOCO AUTOMÁTICO
   ========================================================= */

window.addEventListener("load", () => {
  input.focus();
});
