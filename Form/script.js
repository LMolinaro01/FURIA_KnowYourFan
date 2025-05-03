// formata CPF enquanto digita
document.getElementById("cpf").addEventListener("input", function (e) {
  let cpf = e.target.value.replace(/\D/g, "");
  cpf = cpf.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, "$1.$2.$3-$4");
  e.target.value = cpf;
});

// remove todas as marcações de erro e textos
function clearFieldErrors() {
  document.querySelectorAll(".error").forEach((el) => {
    el.classList.remove("error");
    const msg = el.querySelector(".error-text");
    if (msg) msg.remove();
  });
}

// adiciona a classe de erro e insere uma mensagem
function setFieldError(fieldId, message) {
  const input = document.getElementById(fieldId);
  input.classList.add("error");
  const span = document.createElement("span");
  span.className = "error-text";
  span.style.color = "#ff4d4f";
  span.textContent = message;
  input.parentNode.appendChild(span);
}

// converte arquivo em Base64
function fileToBase64(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onerror = () => reject(reader.error);
    reader.onload = () => resolve(reader.result.split(",")[1]);
    reader.readAsDataURL(file);
  });
}

// exibe um toast na div #alert
function showToast(msg) {
  const alert = document.getElementById("alert");
  alert.textContent = msg;
  alert.classList.add("show");
  setTimeout(() => alert.classList.remove("show"), 3000);
}

// listener de envio do formulário
document.getElementById("formulario").addEventListener("submit", async function (e) {
  e.preventDefault();
  clearFieldErrors();
  console.log("Submit iniciado"); // para debug

  // captura dos campos
  const nome     = document.getElementById("nome").value.trim();
  const cpf      = document.getElementById("cpf").value.trim();
  const endereco = document.getElementById("endereco").value.trim();
  const twitter  = document.getElementById("twitter").value.trim();

  const jogosFuria = Array.from(
    document.querySelectorAll('input[name="jogos_furia"]:checked')
  ).map(c => c.value);
  const produtos = Array.from(
    document.querySelectorAll('input[name="produtos_furia"]:checked')
  ).map(c => c.value);
  const eventos = document.getElementById("eventos_furia").value;

  let hasError = false;

  // validações básicas
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
  if (!twitter) {
    setFieldError("twitter", "Por favor informe seu Twitter.");
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

  const rgFile     = document.getElementById("rgImagem").files[0];
  const selfieFile = document.getElementById("selfieImagem").files[0];
  if (!rgFile)     { setFieldError("rgImagem",     "Carregue a imagem do RG.");     hasError = true; }
  if (!selfieFile) { setFieldError("selfieImagem", "Carregue a sua selfie.");      hasError = true; }

  if (hasError) return;

  // converte imagens
  let rgBase64, selfieBase64;
  try {
    rgBase64     = await fileToBase64(rgFile);
    selfieBase64 = await fileToBase64(selfieFile);
  } catch (err) {
    showToast("Falha ao ler imagens.");
    console.error(err);
    return;
  }

  // monta o payload
  const dados = {
    nome,
    cpf,
    endereco,
    twitter,
    jogos_furia:    jogosFuria,
    produtos_furia: produtos,
    eventos_furia:  eventos,
    rgImagem_base64:     rgBase64,
    selfieImagem_base64: selfieBase64
  };

  // envia para o back-end
  try {
    const resp = await fetch("http://localhost:8080/submit", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(dados),
    }).then(r => r.json());
    showToast(resp.message);
  } catch (err) {
    showToast("Erro ao enviar. Tente novamente.");
    console.error(err);
  }
});
