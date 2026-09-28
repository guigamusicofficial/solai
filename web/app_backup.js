const chat = document.getElementById("chat");
const input = document.getElementById("message");
const send = document.getElementById("send");

function adicionarMensagem(texto, tipo) {

    const welcome = document.querySelector(".welcome");

    if (welcome) {
        welcome.remove();
    }

    const wrapper = document.createElement("div");

    wrapper.className =
        "message " + tipo;

    const bubble =
        document.createElement("div");

    bubble.className = "bubble";

    bubble.textContent = texto;

    wrapper.appendChild(bubble);

    chat.appendChild(wrapper);

    chat.scrollTop = chat.scrollHeight;
}


function mostrarDigitando() {

    const wrapper =
        document.createElement("div");

    wrapper.className =
        "message sol";

    wrapper.id =
        "typing";

    const bubble =
        document.createElement("div");

    bubble.className =
        "bubble";

    bubble.textContent =
        "Sol está digitando...";

    wrapper.appendChild(bubble);

    chat.appendChild(wrapper);

    chat.scrollTop =
        chat.scrollHeight;
}


function removerDigitando() {

    const typing =
        document.getElementById("typing");

    if (typing) {
        typing.remove();
    }
}


async function enviarMensagem() {

    const texto =
        input.value.trim();

    if (!texto) {
        return;
    }

    adicionarMensagem(
        texto,
        "user"
    );

    input.value = "";

    input.style.height =
        "auto";

    mostrarDigitando();

    send.disabled = true;

    try {

        const resposta =
            await fetch(
                "/api/chat",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        mensagem: texto
                    })
                }
            );

        const dados =
            await resposta.json();

        removerDigitando();

        if (dados.resposta) {

            adicionarMensagem(
                dados.resposta,
                "sol"
            );

        } else {

            adicionarMensagem(
                "Não consegui processar a mensagem.",
                "sol"
            );
        }

    } catch (erro) {

        removerDigitando();

        adicionarMensagem(
            "Não consegui conectar ao servidor da Sol.",
            "sol"
        );

        console.error(erro);

    } finally {

        send.disabled = false;

        input.focus();
    }
}


send.addEventListener(
    "click",
    enviarMensagem
);


input.addEventListener(
    "keydown",
    function(event) {

        if (
            event.key === "Enter" &&
            !event.shiftKey
        ) {

            event.preventDefault();

            enviarMensagem();
        }
    }
);


input.addEventListener(
    "input",
    function() {

        this.style.height =
            "auto";

        this.style.height =
            Math.min(
                this.scrollHeight,
                130
            ) + "px";
    }
);
