/**
 * SMART EXPENSE TRACKER - DASHBOARD CHARTS
 * Renders Category Doughnut & Monthly Cashflow Charts with Chart.js
 */

document.addEventListener('DOMContentLoaded', () => {
  initDashboardCharts();
});

function initDashboardCharts() {
  // Global Chart.js Configuration
  if (typeof Chart !== 'undefined') {
    Chart.defaults.color = '#94a3b8';
    Chart.defaults.font.family = "'Plus Jakarta Sans', 'Inter', sans-serif";
    Chart.defaults.plugins.tooltip.backgroundColor = 'rgba(17, 24, 39, 0.95)';
    Chart.defaults.plugins.tooltip.titleColor = '#f8fafc';
    Chart.defaults.plugins.tooltip.bodyColor = '#cbd5e1';
    Chart.defaults.plugins.tooltip.borderColor = 'rgba(255, 255, 255, 0.1)';
    Chart.defaults.plugins.tooltip.borderWidth = 1;
    Chart.defaults.plugins.tooltip.padding = 10;
    Chart.defaults.plugins.tooltip.cornerRadius = 8;
  }

  loadCategoryExpensesChart();
  loadMonthlyCashflowChart();
}

/**
 * Loads Category Doughnut Chart
 */
async function loadCategoryExpensesChart() {
  const canvas = document.getElementById('categoryExpensesChart');
  if (!canvas) return;

  try {
    const res = await fetch('/api/charts/category-expenses');
    const data = await res.json();

    const emptyContainer = document.getElementById('categoryChartEmpty');

    if (!data.labels || data.labels.length === 0) {
      canvas.style.display = 'none';
      if (emptyContainer) emptyContainer.style.display = 'flex';
      return;
    }

    if (emptyContainer) emptyContainer.style.display = 'none';
    canvas.style.display = 'block';

    const sym = data.currency_symbol || '$';
    const ctx = canvas.getContext('2d');
    new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: data.labels,
        datasets: [{
          data: data.values,
          backgroundColor: data.colors,
          borderWidth: 2,
          borderColor: '#1f2937',
          hoverOffset: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '68%',
        plugins: {
          legend: {
            position: 'right',
            labels: {
              boxWidth: 12,
              padding: 14,
              font: { size: 12, weight: '500' }
            }
          },
          tooltip: {
            callbacks: {
              label: function (context) {
                const val = context.parsed || 0;
                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                const pct = total > 0 ? ((val / total) * 100).toFixed(1) : 0;
                return ` ${context.label}: ${sym}${val.toLocaleString(undefined, {minimumFractionDigits: 2})} (${pct}%)`;
              }
            }
          }
        }
      }
    });
  } catch (err) {
    console.error('Failed to load category chart:', err);
  }
}

/**
 * Loads Monthly Cashflow Grouped Bar Chart
 */
async function loadMonthlyCashflowChart() {
  const canvas = document.getElementById('monthlyCashflowChart');
  if (!canvas) return;

  try {
    const res = await fetch('/api/charts/monthly-cashflow?range=6');
    const data = await res.json();

    const emptyContainer = document.getElementById('cashflowChartEmpty');

    if (!data.labels || data.labels.length === 0) {
      canvas.style.display = 'none';
      if (emptyContainer) emptyContainer.style.display = 'flex';
      return;
    }

    if (emptyContainer) emptyContainer.style.display = 'none';
    canvas.style.display = 'block';

    const sym = data.currency_symbol || '$';
    const ctx = canvas.getContext('2d');
    new Chart(ctx, {
      type: 'bar',
      data: {
        labels: data.labels,
        datasets: [
          {
            label: 'Income',
            data: data.income,
            backgroundColor: '#10b981',
            borderRadius: 6,
            barPercentage: 0.6,
            categoryPercentage: 0.7
          },
          {
            label: 'Expenses',
            data: data.expenses,
            backgroundColor: '#f43f5e',
            borderRadius: 6,
            barPercentage: 0.6,
            categoryPercentage: 0.7
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: {
            grid: {
              color: 'rgba(255, 255, 255, 0.05)',
              drawBorder: false
            },
            ticks: { font: { size: 11 } }
          },
          y: {
            grid: {
              color: 'rgba(255, 255, 255, 0.05)',
              drawBorder: false
            },
            ticks: {
              font: { size: 11 },
              callback: (val) => `${sym}${val}`
            }
          }
        },
        plugins: {
          legend: {
            position: 'top',
            align: 'end',
            labels: {
              boxWidth: 12,
              padding: 10,
              font: { size: 12 }
            }
          },
          tooltip: {
            callbacks: {
              label: (ctx) => ` ${ctx.dataset.label}: ${sym}${ctx.parsed.y.toLocaleString(undefined, {minimumFractionDigits: 2})}`
            }
          }
        }
      }
    });
  } catch (err) {
    console.error('Failed to load cashflow chart:', err);
  }
}
