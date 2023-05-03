function enviar_datos(url, datos, callback) {
  // obtener el token CSRF del input escondido de la pagina
  const csrfTokenInput = document.querySelector(
    'input[name="csrfmiddlewaretoken"]'
  );
  const csrftoken = csrfTokenInput.value;

  fetch(url, {
    method: "POST",
    body: JSON.stringify(datos), // Convierte los datos en JSON para poder procesarlos en la vista
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrftoken,
    },
  })
    .then((response) => response.json())
    .then((data) => {
      callback(data);
    })
    .catch((error) => {
      //****************** que hubo un error
      const Toast = Swal.mixin({
        toast: true,
        position: "top-end",
        showConfirmButton: false,
        timer: 4000,
        timerProgressBar: true,
        didOpen: (toast) => {
          toast.addEventListener("mouseenter", Swal.stopTimer);
          toast.addEventListener("mouseleave", Swal.resumeTimer);
        },
      });

      Toast.fire({
        icon: "error",
        title: `${error}`,
      });
      //*************
    });
}
