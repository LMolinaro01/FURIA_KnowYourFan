document.addEventListener("DOMContentLoaded", () => {
  const cpfInput = document.getElementById("cpf");
  if (cpfInput) {
    cpfInput.addEventListener("input", function (e) {
      let cpf = e.target.value.replace(/\D/g, "");
      cpf = cpf.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, "$1.$2.$3-$4");
      e.target.value = cpf;
    });
  }

  function clearFieldErrors() {
    document.querySelectorAll(".error").forEach((el) => el.classList.remove("error"));
    document.querySelectorAll(".error-text").forEach((el) => el.remove());
  }

  function setFieldError(fieldId, message) {
    const input = document.getElementById(fieldId);
    if (!input) return;
    input.classList.add("error");
    const span = document.createElement("span");
    span.className = "error-text";
    span.style.color = "#ff4d4f";
    span.textContent = message;
    input.parentNode.appendChild(span);
  }

  function showToast(msg) {
    const alertEl = document.getElementById("alert");
    if (!alertEl) return;
    alertEl.textContent = msg;
    alertEl.classList.add("show");
    setTimeout(() => alertEl.classList.remove("show"), 3000);
  }

  function fileToBase64(file) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onerror = () => reject(reader.error);
      reader.onload = () => resolve(reader.result.split(",")[1]);
      reader.readAsDataURL(file);
    });
  }

  const formulario = document.getElementById("formulario");
  const alerta = document.getElementById("alert");

  if (!formulario) {
    console.error("Formulário não encontrado!");
    return;
  }

  formulario.addEventListener("submit", async function (e) {
    e.preventDefault();
    clearFieldErrors();

    alerta.innerText = "Enviando dados...";
    alerta.style.color = "black";

    const nomeInput = document.getElementById("nome");
    const nome = nomeInput ? nomeInput.value.trim() : "";
    const cpfElem = document.getElementById("cpf");
    const cpf = cpfElem ? cpfElem.value.trim() : "";
    const enderecoInput = document.getElementById("endereco");
    const endereco = enderecoInput ? enderecoInput.value.trim() : "";
    const twitterInput = document.getElementById("twitter");
    const twitter = twitterInput ? twitterInput.value.trim() : "";

    const jogosFuria = Array.from(
           document.querySelectorAll('input[name="jogos_furia[]"]:checked')
          ).map((c) => c.value);

    const produtos = Array.from(
      document.querySelectorAll('input[name="produtos_furia[]"]:checked')
    ).map((c) => c.value);

    const eventosElem = document.getElementById("eventos_furia");
    const eventos = eventosElem ? eventosElem.value : "";

    const rgFileInput = document.getElementById("rgImagem");
    const rgFile = rgFileInput ? rgFileInput.files[0] : null;
    const selfieFileInput = document.getElementById("selfieImagem");
    const selfieFile = selfieFileInput ? selfieFileInput.files[0] : null;

    let hasError = false;

    if (nomeInput && !nome) {
      setFieldError("nome", "Por favor informe seu nome.");
      hasError = true;
    }
    if (cpfElem && !/^\d{3}\.\d{3}\.\d{3}-\d{2}$/.test(cpf)) {
      setFieldError("cpf", "CPF inválido. Formato: 000.000.000-00");
      hasError = true;
    }
    if (enderecoInput && !endereco) {
      setFieldError("endereco", "Por favor informe o estado.");
      hasError = true;
    }

    if (jogosFuria.length === 0) {
      const jogosLabel = document.querySelector('label[for="jogos_furia"]');
      if (jogosLabel) {
        const span = document.createElement("span");
        span.className = "error-text";
        span.style.color = "#ff4d4f";
        span.textContent = "Selecione pelo menos um jogo.";
        jogosLabel.parentNode.insertBefore(span, jogosLabel.nextSibling);
      }
      hasError = true;
    }

    if (produtos.length === 0) {
      setFieldError("produtos_furia", "Selecione pelo menos um produto.");
      hasError = true;
    }

    if (eventosElem && !eventos) {
      setFieldError("eventos_furia", "Selecione uma opção de evento.");
      hasError = true;
    }

    if (!rgFile) {
      setFieldError("rgImagem", "Carregue a imagem do RG.");
      hasError = true;
    }

    if (!selfieFile) {
      setFieldError("selfieImagem", "Carregue a sua selfie.");
      hasError = true;
    }

    if (hasError) return;

    let rgBase64, selfieBase64;
    try {
      rgBase64 = await fileToBase64(rgFile);
      selfieBase64 = await fileToBase64(selfieFile);
    } catch (err) {
      showToast("Falha ao ler imagens.");
      console.error(err);
      return;
    }

    const dados = {
      nome,
      cpf,
      endereco,
      twitter,
      jogos_furia: jogosFuria,
      produtos_furia: produtos,
      eventos_furia: eventos,
      rgImagem_base64: rgBase64,
      selfieImagem_base64: selfieBase64,
    };

    fetch("/submit", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(dados),
    })
      .then((r) => r.json())
      .then((resp) => {
        showToast(resp.message);
        formulario.reset();
      })
      .catch((err) => {
        showToast("Erro ao enviar. Tente novamente.");
        console.error(err);
      });
  });
});
