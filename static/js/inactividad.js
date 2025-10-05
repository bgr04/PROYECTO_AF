// $(document).ajaxError(function(event, jqxhr) {
//   if (jqxhr && jqxhr.status === 401) {
//     Swal.fire({
//       icon: 'warning',
//       title: 'Sesión expirada',
//       text: 'Tu sesión ha expirado por inactividad. Serás redirigido al inicio de sesión.',
//       confirmButtonText: 'Ir al login',
//       allowOutsideClick: false,
//       allowEscapeKey: false
//     }).then(() => {
//       // replace() evita que el usuario regrese con el botón Atrás
//       window.location.replace('/logout');
//     });
//   }
// });

// 2) Temporizador de inactividad en el cliente (solo UX, el servidor manda)
(function() {
  const LIMIT_MS = 10 * 60 * 1000; // 10 minutos
  let idleTimer = null;
  let shown = false;

  function resetIdle() {
    shown = false;
    if (idleTimer) clearTimeout(idleTimer);
    idleTimer = setTimeout(onIdleLimit, LIMIT_MS);
  }

  function onIdleLimit() {
    if (shown) return;
    shown = true;
    Swal.fire({
      icon: 'warning',
      title: 'Sesión expirada por inactividad',
      text: 'Has estado inactivo 10 minutos. Serás redirigido al inicio de sesión.',
      timer: 3000,
      showConfirmButton: false,
      allowOutsideClick: false,
      allowEscapeKey: false,
      timerProgressBar: true
    }).then(() => {
      window.location.href ='/logout';
    });
  }

  // Consideramos estas acciones como “actividad”
  ['mousemove','mousedown','keypress','touchstart','scroll'].forEach(ev => {
    window.addEventListener(ev, resetIdle, {passive:true});
  });

  resetIdle();
})();

// 3) Refuerzo contra el botón “Atrás”
window.history.replaceState(null, '', window.location.href);
window.addEventListener('popstate', function () {
  // Si intenta volver, recargamos la ruta actual; el servidor decidirá (y si expiró, lo saca)
  window.location.replace(window.location.href);
});