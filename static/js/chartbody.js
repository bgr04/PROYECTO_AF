// Pie Chart
new Chart(document.getElementById('chartPie'), {
    type: 'pie',
    data: {
      labels: ['Vehículos', 'Maquinaria', 'Equipos', 'Otros'],
      datasets: [{
        data: [30, 25, 20, 25],
        backgroundColor: ['#42a5f5','#66bb6a','#ffa726','#ef5350']
      }]
    }
});

// Bar Chart
new Chart(document.getElementById('chartBar'), {
  type: 'bar',
  data: {
    labels: ['Producción','Ventas','Administración','Logística'],
    datasets: [{
      label: 'Número de Activos',
      data: [12, 19, 7, 14],
      backgroundColor: '#42a5f5'
    }]
  },
  options: {
    scales: { y: { beginAtZero: true } }
  }
});