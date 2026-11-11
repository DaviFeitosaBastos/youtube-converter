"use strict";

const $ = (id) => document.getElementById(id);
let api = null;
let busy = false;
let pending = false;
let pollInFlight = false;
let lastMessage = "";
let selectedFile = false;

function message(text, status = "idle") {
  $("activityCard").dataset.status = status;
  if (text !== lastMessage) {
    $("statusText").textContent = text;
    lastMessage = text;
  }
}

function controls() {
  document.querySelectorAll("[data-native]").forEach((button) => {
    button.disabled = !api || busy || pending;
  });
  document.querySelectorAll("form input, form select").forEach((input) => {
    input.disabled = busy || pending;
  });
  $("gifButton").disabled = !api || busy || pending || !selectedFile;
  $("activityCard").setAttribute("aria-busy", String(busy));
}

async function perform(action) {
  if (!api || busy || pending) return;
  pending = true;
  controls();
  try {
    const result = await action();
    if (!result.ok) message(result.message, "error");
    return result;
  } catch (_) {
    message("A comunicação com o aplicativo falhou. Feche e abra a janela novamente.", "error");
  } finally {
    pending = false;
    controls();
  }
}

function switchView(view) {
  const gif = view === "gif";
  $("downloadForm").hidden = gif;
  $("gifForm").hidden = !gif;
  $("metadataCard").hidden = true;
  $("pageEyebrow").textContent = gif ? "DO SEU VÍDEO PARA UM GIF" : "DO YOUTUBE PARA VOCÊ";
  $("pageTitle").textContent = gif ? "Um trecho que vale repetir." : "Um link. Seu próximo play.";
  $("pageSubtitle").textContent = gif
    ? "Recorte, ajuste e transforme seu MP4. Tudo acontece no seu computador."
    : "Vídeos e áudios, do jeito que você precisa. Salvos no seu computador.";
  document.querySelectorAll("[data-view]").forEach((button) => {
    const active = button.dataset.view === view;
    button.classList.toggle("active", active);
    if (active) button.setAttribute("aria-current", "page");
    else button.removeAttribute("aria-current");
  });
}

document.querySelectorAll("[data-view]").forEach((button) => {
  button.addEventListener("click", () => switchView(button.dataset.view));
});

document.querySelectorAll('input[name="format"]').forEach((radio) => {
  radio.addEventListener("change", () => {
    const audio = radio.value === "mp3" && radio.checked;
    $("qualityRow").hidden = audio;
    $("downloadButton").querySelector("span").textContent = audio ? "Baixar áudio" : "Baixar vídeo";
  });
});

async function start(action) {
  const response = await perform(action);
  if (response?.ok) {
    busy = true;
    $("resultPath").hidden = true;
    $("metadataCard").hidden = true;
    message("Preparando…", "running");
    controls();
    await poll();
  }
}

$("downloadForm").addEventListener("submit", (event) => {
  event.preventDefault();
  const format = document.querySelector('input[name="format"]:checked').value;
  start(() => api.start_download($("urlInput").value.trim(), format, $("qualityInput").value));
});
$("infoButton").addEventListener("click", () => start(() => api.start_info($("urlInput").value.trim())));
$("chooseFile").addEventListener("click", async () => {
  const response = await perform(() => api.choose_mp4());
  if (response?.ok && !response.cancelled) {
    selectedFile = true;
    $("fileName").textContent = response.name;
    message("MP4 selecionado. Escolha o trecho e crie seu GIF.");
    controls();
  }
});
$("gifForm").addEventListener("submit", (event) => {
  event.preventDefault();
  start(() => api.start_gif($("gifStart").value.trim(), $("gifEnd").value.trim(),
    Number($("gifFps").value), Number($("gifWidth").value)));
});
$("chooseOutput").addEventListener("click", async () => {
  const response = await perform(() => api.choose_output());
  if (response?.ok) $("outputPath").textContent = response.output_dir;
});
$("openOutput").addEventListener("click", () => perform(() => api.open_output()));
$("cancelButton").addEventListener("click", async () => {
  $("cancelButton").disabled = true;
  try {
    await api.cancel();
    message("Cancelamento solicitado. Aguardando a etapa atual…", "running");
  } catch (_) {
    message("Não foi possível solicitar o cancelamento. Aguarde a operação atual.", "error");
  }
});
$("privacyButton").addEventListener("click", () => $("privacyDialog").showModal());
$("closePrivacy").addEventListener("click", () => $("privacyDialog").close());

function duration(seconds) {
  const number = Math.max(0, Number(seconds) || 0);
  return `${Math.floor(number / 60)}:${String(Math.floor(number % 60)).padStart(2, "0")}`;
}

async function poll() {
  if (!api || pollInFlight || pending) return;
  pollInFlight = true;
  try {
    const state = await api.state();
    busy = state.status === "running";
    message(state.message, state.status);
    $("cancelButton").hidden = !busy;
    if (!busy) $("cancelButton").disabled = false;
    $("progressRow").hidden = !busy;
    if (state.percent === null) {
      $("progressBar").removeAttribute("value");
      $("progressLabel").textContent = "…";
    } else {
      $("progressBar").value = state.percent;
      $("progressLabel").textContent = `${Math.round(state.percent)}%`;
    }
    if (state.result?.kind === "file") {
      $("resultPath").textContent = state.result.path;
      $("resultPath").hidden = false;
    } else if (state.result?.kind === "info") {
      $("videoTitle").textContent = state.result.title;
      $("videoDetails").textContent = `${state.result.author} · ${duration(state.result.duration)} · ${Number(state.result.views || 0).toLocaleString("pt-BR")} visualizações`;
      $("videoDescription").textContent = state.result.description;
      $("metadataCard").hidden = false;
    }
    controls();
  } catch (_) {
    message("A conexão com a janela foi interrompida. Reabra o aplicativo.", "error");
  } finally {
    pollInFlight = false;
  }
}

async function connect() {
  if (api || !window.pywebview?.api) return;
  api = window.pywebview.api;
  try {
    const settings = await api.settings();
    $("outputPath").textContent = settings.output_dir;
    $("engineStatus").className = `engine-status ${settings.ffmpeg ? "ready" : "missing"}`;
    $("engineStatus").lastChild.textContent = settings.ffmpeg ? "Pronto para criar" : "FFmpeg não encontrado";
    if (!settings.ffmpeg) message("Instale o FFmpeg para baixar em alta qualidade, extrair MP3 ou criar GIFs.", "error");
    $("browserNotice").hidden = true;
    controls();
    window.setInterval(() => { if (busy) poll(); }, 500);
  } catch (_) {
    api = null;
    message("Não foi possível conectar à interface desktop. Reabra o aplicativo.", "error");
    controls();
  }
}
window.addEventListener("pywebviewready", connect);
connect();
controls();
