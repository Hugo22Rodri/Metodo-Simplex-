document.addEventListener("DOMContentLoaded", () => {
  // 1. Efecto máquina de escribir en el encabezado
  const titulo = document.querySelector(".cabecera h1");
  if (titulo) {
    const texto = titulo.innerText;
    titulo.innerText = "";
    let i = 0;
    const velocidad = 60;

    const escribir = () => {
      if (i < texto.length) {
        titulo.innerHTML += `<span style="color:#38bdf8;">${texto.charAt(i)}</span>`;
        i++;
        setTimeout(escribir, velocidad);
      }
    };
    escribir();
  }

  // 2. Animación por scroll con IntersectionObserver
  const elementosAnimados = document.querySelectorAll(".seccion, .tarjeta, .pasos-lista li");

  const observador = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add("visible");
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.2 });

  elementosAnimados.forEach(el => observador.observe(el));

  // 3. Iluminación de tarjetas con movimiento del mouse
  const tarjetas = document.querySelectorAll(".tarjeta");
  tarjetas.forEach(tarjeta => {
    tarjeta.addEventListener("mousemove", e => {
      const { left, top } = tarjeta.getBoundingClientRect();
      const x = e.clientX - left;
      const y = e.clientY - top;
      tarjeta.style.background = `radial-gradient(circle at ${x}px ${y}px, rgba(124, 58, 237, 0.2), transparent 60%)`;
    });
    tarjeta.addEventListener("mouseleave", () => {
      tarjeta.style.background = "";
    });
  });

  // 4. Toggle de modo claro/oscuro
  const toggle = document.getElementById("modo-toggle");
  if (toggle) {
    toggle.addEventListener("click", () => {
      document.body.classList.toggle("modo-claro");
      localStorage.setItem("modo", document.body.classList.contains("modo-claro") ? "claro" : "oscuro");
    });

    const modoGuardado = localStorage.getItem("modo");
    if (modoGuardado === "claro") {
      document.body.classList.add("modo-claro");
    }
  }

  // 5. Cursor intermitente como consola digital
  const subtitulo = document.querySelector(".subtitulo");
  if (subtitulo) {
    const parpadeo = document.createElement("span");
    parpadeo.innerText = " ▍";
    parpadeo.style.color = "#38bdf8";
    parpadeo.style.animation = "blink 1s steps(2, start) infinite";
    subtitulo.appendChild(parpadeo);
  }
});
