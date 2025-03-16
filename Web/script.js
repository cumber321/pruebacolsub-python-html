document.addEventListener("DOMContentLoaded", function() {
    const loading = document.getElementById("loading");
    loading.style.display = "block"; 

    fetch("/Web/resultados.json") // Ruta del json
        .then(response => {
            if (!response.ok) {
                throw new Error("No se pudo cargar el JSON");
            }
            return response.json();
        })
        .then(data => {
            loading.style.display = "Los resultados de la prueba";
            mostrarResultados(data);
        })
        .catch(error => {
            console.error("Error al cargar los datos:", error);
            let msg = document.getElementById("mensaje-error"); 
            if (msg) msg.innerText = "Error al cargar los datos.";
        });
        
});

function mostrarResultados(data) {
    actualizarSeccion("temporadas-venta-resultados", data.temporadasVenta);
    actualizarSeccion("consumo-por-ues-resultados", data.consumoPorUES);
    actualizarSeccion("participacion-consumo-resultados", data.participacionConsumo);
    actualizarSeccion("productos-mas-usados-resultados", data.productosMasUsados);
    actualizarSeccion("clientes-mayor-frecuencia-resultados", data.clientesMayorFrecuencia);
    actualizarSeccion("clientes-mayor-valor-resultados", data.clientesMayorValor);
    actualizarSeccion("penetracion-afiliados-resultados", data.penetracionAfiliados);
    actualizarSeccion("productos-segmento-resultados", data.productosSegmento);
    actualizarSeccion("mejores-empresas-resultados", data.mejoresEmpresas);
}

function actualizarSeccion(id, datos) {
    const contenedor = document.getElementById(id);
    if (datos && datos.length > 0) {
        contenedor.innerHTML = datos.map(item => `<p>${item}</p>`).join("");
    } else {
        contenedor.innerHTML = "No se tienen datos para mostar ";
    }
}
