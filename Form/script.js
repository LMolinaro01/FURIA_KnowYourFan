
// formata CPF enquanto digita
document.getElementById("cpf").addEventListener("input", function (e) {
  let cpf = e.target.value.replace(/\D/g, "");
  cpf = cpf.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, "$1.$2.$3-$4");
  e.target.value = cpf;
});

function clearFieldErrors() {
  // remove classe de erro de tudo
  document
    .querySelectorAll(".error")
    .forEach((el) => el.classList.remove("error"));
  // remove todas as mensagens
  document.querySelectorAll(".error-text").forEach((el) => el.remove());
}

function setFieldError(fieldId, message) {
  const el = document.getElementById(fieldId);
  // marca o container (fieldset) com .error
  el.classList.add("error");
  // insere a mensagem abaixo do fieldset
  const span = document.createElement("span");
  span.className = "error-text";
  span.textContent = message;
  el.appendChild(span);
}

// valida e envia
document
  .getElementById("formulario")
  .addEventListener("submit", function (e) {
    e.preventDefault();
    clearFieldErrors();

    const nome = document.getElementById("nome").value.trim();
    const cpf = document.getElementById("cpf").value.trim();
    const endereco = document.getElementById("endereco").value.trim();
    //const email = document.getElementById("email").value.trim();
    const instagram = document.getElementById("instagram").value.trim();
    const twitter = document.getElementById("twitter").value.trim();
    const jogosFuria = Array.from(
      document.querySelectorAll('input[name="jogos_furia"]:checked')
    ).map((c) => c.value);
    const produtos = Array.from(
      document.querySelectorAll('input[name="produtos_furia"]:checked')
    ).map((c) => c.value);
    const eventos = document.getElementById("eventos_furia").value;

    let hasError = false;

    if (!nome) {
      setFieldError("nome", "Por favor informe seu nome.");
      hasError = true;
    }
    if (!/^\d{3}\.\d{3}\.\d{3}-\d{2}$/.test(cpf)) {
      setFieldError("cpf", "CPF inválido. Formato: 000.000.000-00");
      hasError = true;
    }
    if (!endereco) {
      setFieldError("endereco", "Por favor informe o estado.");
      hasError = true;
    }
    //if (!email) {
      //setFieldError("email", "Por favor informe seu e-mail.");
      //hasError = true;
    //}
    if (!instagram && !twitter) {
      setFieldError("instagram", "Informe o Instagram ou o Twitter.");
      setFieldError("twitter", "Informe o Instagram ou o Twitter.");
      hasError = true;
    }
    if (jogosFuria.length === 0) {
      setFieldError("jogos_furia", "Selecione pelo menos um jogo.");
      hasError = true;
    }
    if (produtos.length === 0) {
      setFieldError("produtos_furia", "Selecione pelo menos um produto.");
      hasError = true;
    }
    if (!eventos) {
      setFieldError("eventos_furia", "Selecione uma opção de evento.");
      hasError = true;
    }

    function clearFieldErrors() {
      document.querySelectorAll(".form-control.error").forEach((el) => {
        el.classList.remove("error");
        const msg = el.parentNode.querySelector(".error-text");
        if (msg) msg.remove();
      });
    }

    // marca um campo como inválido e exibe mensagem
    function setFieldError(fieldId, message) {
      const input = document.getElementById(fieldId);
      input.classList.add("error");
      const span = document.createElement("span");
      span.className = "error-text";
      span.style.color = "#ff4d4f";
      span.textContent = message;
      input.parentNode.appendChild(span);
    }

    // exibe um toast simples usando a div #alert
    function showToast(msg) {
      const alert = document.getElementById("alert");
      alert.textContent = msg;
      alert.classList.add("show");
      setTimeout(() => alert.classList.remove("show"), 3000);
    }

    if (hasError) return;

    const dados = {
      nome,
      cpf,
      endereco,
      //email,
      instagram,
      twitter,
      jogos_furia: jogosFuria,
      produtos_furia: produtos,
      eventos_furia: eventos,
    };

    fetch("http://localhost:8080/submit", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(dados),
    })
      .then((r) => r.json())
      .then((resp) => {
        showToast(resp.message);
      })
      .catch((err) => {
        showToast("Erro ao enviar. Tente novamente.");
        console.error(err);
      });
  });
