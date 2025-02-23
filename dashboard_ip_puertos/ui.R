library(shinydashboard)

dashboardPage(
  dashboardHeader(title = "OpUtils - Administración de IP y Puertos"),
  dashboardSidebar(
    # Menú lateral 
  ),
  dashboardBody(
    fluidRow(
      box(
        title = "Resumen general",
        width = 6,
        # Aquí irán los gráficos de resumen
      ),
      box(
        title = "Direcciones IP",
        width = 6,
        DT::dataTableOutput("tabla_ips")
      )
    ),
    fluidRow(
      box(
        title = "Puertos de switch",
        width = 6,
        DT::dataTableOutput("tabla_puertos")
      ),
      box(
        title = "Switches",
        width = 6,
        DT::dataTableOutput("tabla_switches")
      )
    )
  )
)