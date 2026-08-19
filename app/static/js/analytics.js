/**
 * SMART EXPENSE TRACKER - ANALYTICS CHARTS
 * Deep-dive visualizations for categories, cashflow comparisons, and cumulative velocity
 */

document.addEventListener('DOMContentLoaded', () => {
  initAnalyticsCharts();
});

function initAnalyticsCharts() {
  if (typeof Chart !== 'undefined') {
    Chart.defaults.color = '#94a3b8';
    Chart.defaults.font.family = "'Plus Jakarta Sans', 'Inter', sans-serif";
  }

  loadAnalyticsCategoryChart();
  loadAnalyticsCashflowChart();
  loadDailyVelocityChart();
}

/**
 * Category Breakdown Chart on Analytics page
 */
async function loadAnalyticsCategoryChart() {
  const canvas = document.getElementById('analyticsCategoryChart');
  if (!canvas) return;

  const month = canvas.dataset.month;
  const year = canvas.dataset.year;

  try {
    const res = await fetch(`/api/charts/category-expenses?month=${month}&year=${year}`);
    const data = await res.json();

    const emptyElem = document.getElementById('analyticsCatEmpty');

    if (!data.labels || data.labels.length === 0) {
      canvas.style.display = 'none';
      if (emptyElem) emptyElem.style.display = 'flex';
      return;
    }

    if (emptyElem) emptyElem.style.display = 'none';
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
          borderColor: '#1f2937'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '65%',
        plugins: {
          legend: {
            position: 'bottom',
            labels: {
              boxWidth: 12,
              padding: 12,
              font: { size: 12 }
            }
          },
          tooltip: {
            callbacks: {
              label: (ctx) => {
                const total = ctx.dataset.data.reduce((a, b) => a + b, 0);
                const pct = ((ctx.parsed / total) * 100).toFixed(1);
                return ` ${ctx.label}: ${sym}${ctx.parsed.toLocaleString(undefined, {minimumFractionDigits: 2})} (${pct}%)`;
              }
            }
          }
        }
      }
    });
  } catch (err) {
    console.error('Error loading analytics category chart:', err);
  }
}

/**
 * Monthly Cashflow Bar Chart on Analytics page
 */
async function loadAnalyticsCashflowChart() {
  const canvas = document.getElementById('analyticsCashflowChart');
  if (!canvas) return;

  const range = canvas.dataset.range || 6;

  try {
    const res = await fetch(`/api/charts/monthly-cashflow?range=${range}`);
    const data = await res.json();

    const emptyElem = document.getElementById('analyticsCashflowEmpty');

    if (!data.labels || data.labels.length === 0) {
      canvas.style.display = 'none';
      if (emptyElem) emptyElem.style.display = 'flex';
      return;
    }

    if (emptyElem) emptyElem.style.display = 'none';
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
          x: { grid: { color: 'rgba(255, 255, 255, 0.05)', drawBorder: false } },
          y: {
            grid: { color: 'rgba(255, 255, 255, 0.05)', drawBorder: false },
            ticks: { callback: (v) => `${sym}${v}` }
          }
        },
        plugins: {
          legend: { position: 'top', align: 'end' },
          tooltip: {
            callbacks: {
              label: (ctx) => ` ${ctx.dataset.label}: ${sym}${ctx.parsed.y.toLocaleString(undefined, {minimumFractionDigits: 2})}`
            }
          }
        }
      }
    });
  } catch (err) {
    console.error('Error loading analytics cashflow chart:', err);
  }
}

/**
 * Daily Spending Velocity Area Line Chart
 */
async function loadDailyVelocityChart() {
  const canvas = document.getElementById('dailyVelocityChart');
  if (!canvas) return;

  const month = canvas.dataset.month;
  const year = canvas.dataset.year;

  try {
    const res = await fetch(`/api/charts/daily-spending?month=${month}&year=${year}`);
    const data = await res.json();

    const emptyElem = document.getElementById('dailyVelocityEmpty');

    if (!data.labels || data.labels.length === 0) {
      canvas.style.display = 'none';
      if (emptyElem) emptyElem.style.display = 'flex';
      return;
    }

    if (emptyElem) emptyElem.style.display = 'none';
    canvas.style.display = 'block';

    const sym = data.currency_symbol || '$';
    const ctx = canvas.getContext('2d');
    
    // Gradient fill for area
    const gradient = ctx.createLinearGradient(0, 0, 0, 300);
    gradient.addColorStop(0, 'rgba(99, 102, 241, 0.4)');
    gradient.addColorStop(1, 'rgba(99, 102, 241, 0.0)');

    new Chart(ctx, {
      type: 'line',
      data: {
        labels: data.labels.map((d) => `Day ${d}`),
        datasets: [
          {
            label: 'Cumulative Spent',
            data: data.cumulative_values,
            borderColor: '#6366f1',
            backgroundColor: gradient,
            fill: true,
            tension: 0.35,
            borderWidth: 2.5,
            pointRadius: 2,
            pointHoverRadius: 5
          },
          {
            label: 'Daily Spent',
            data: data.daily_values,
            borderColor: '#f59e0b',
            borderWidth: 1.5,
            borderDash: [4, 4],
            fill: false,
            tension: 0.2,
            pointRadius: 0,
            pointHoverRadius: 4
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: { grid: { color: 'rgba(255, 255, 255, 0.05)', drawBorder: false } },
          y: {
            grid: { color: 'rgba(255, 255, 255, 0.05)', drawBorder: false },
            ticks: { callback: (v) => `${sym}${v}` }
          }
        },
        plugins: {
          legend: { position: 'top', align: 'end' },
          tooltip: {
            callbacks: {
              label: (ctx) => ` ${ctx.dataset.label}: ${sym}${ctx.parsed.y.toLocaleString(undefined, {minimumFractionDigits: 2})}`
            }
          }
        }
      }
    });
  } catch (err) {
    console.error('Error loading daily velocity chart:', err);
  }
}
