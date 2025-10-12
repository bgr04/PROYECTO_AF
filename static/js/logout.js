function salir() {
    Swal.fire({
        icon: 'info',
        title: 'Cerrando sesión...',
        timer: 1000,
        showConfirmButton: false,
        willClose: () => {
            window.location.href = "{{ url_for('login.logout') }}";
        }
    });
}