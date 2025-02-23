library(shiny)
library(dplyr)
library(ggplot2)
library(DT)

function(input, output) {
  # Datos de ejemplo (entonces se reemplaza con la lógica para obtener datos reales)
  datos_ip <- reactive({
    data.frame(
      estado = c("Utilizadas", "Disponibles", "Reservadas"),
      cantidad = c(sample(50:100, 1), sample(100:200, 1), sample(20:50, 1))
    )
  })

  datos_puertos <- reactive({
    data.frame(
      estado = c("Utilizados", "Libres", "Con problemas"),
      cantidad = c(sample(20:50, 1), sample(50:100, 1), sample(5:20, 1))
    )
  })

  datos_switches <- reactive({
    data.frame(
      nombre = c("Switch 1", "Switch 2", "Switch 3"),
      ip = c("192.168.1.1", "192.168.1.2", "192.168.1.3"),
      estado = c("En línea", "Fuera de línea", "En línea")
    )
  })

  # Gráficos (ejemplo con ggplot2)
  output$grafico_ip <- renderPlot({
    ggplot(datos_ip(), aes(x = estado, y = cantidad, fill = estado)) +
      geom_bar(stat = "identity") +
      labs(title = "Distribución de direcciones IP")
  })

  # Tablas (ejemplo con DT)
  output$tabla_ips <- DT::renderDataTable({
    datos_ip()
  })

  output$tabla_puertos <- DT::renderDataTable({
    datos_puertos()
  })

  output$tabla_switches <- DT::renderDataTable({
    datos_switches()
  })
}