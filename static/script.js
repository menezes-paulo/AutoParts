const senha = document.getElementById("senha")
const mostrarSenha = document.getElementById("mostrar-senha")

mostrarSenha.addEventListener("change", function() {
    if (mostrarSenha.checked) {
        senha.type = "text";
    }
    else 
        senha.type = "password";


});