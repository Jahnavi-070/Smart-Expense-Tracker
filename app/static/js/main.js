/**
 * SMART EXPENSE TRACKER - MAIN JAVASCRIPT
 * Handles mobile sidebar, modals, toast alerts, and quick transaction form
 */

document.addEventListener('DOMContentLoaded', () => {
  initMobileSidebar();
  initToastAlerts();
  initModals();
  initQuickTransactionForm();
});

/* Mobile Sidebar Drawer */
function initMobileSidebar() {
  const toggleBtn = document.getElementById('mobileMenuBtn');
  const sidebar = document.querySelector('.app-sidebar');

  if (toggleBtn && sidebar) {
    toggleBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      sidebar.classList.toggle('open');
    });

    document.addEventListener('click', (e) => {
      if (sidebar.classList.contains('open') && !sidebar.contains(e.target) && e.target !== toggleBtn) {
        sidebar.classList.remove('open');
      }
    });
  }
}

/* Flash Toasts Auto Dismiss */
function initToastAlerts() {
  const toasts = document.querySelectorAll('.toast');
  toasts.forEach((toast) => {
    // Auto dismiss after 5 seconds
    setTimeout(() => {
      dismissToast(toast);
    }, 5000);

    const closeBtn = toast.querySelector('.toast-close');
    if (closeBtn) {
      closeBtn.addEventListener('click', () => {
        dismissToast(toast);
      });
    }
  });
}

function dismissToast(toast) {
  if (!toast) return;
  toast.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
  toast.style.opacity = '0';
  toast.style.transform = 'translateX(100%)';
  setTimeout(() => toast.remove(), 300);
}

function showToast(message, type = 'info') {
  let container = document.querySelector('.toast-container');
  if (!container) {
    container = document.createElement('div');
    container.className = 'toast-container';
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.innerHTML = `
    <span>${message}</span>
    <button class="toast-close" type="button">&times;</button>
  `;

  container.appendChild(toast);

  toast.querySelector('.toast-close').addEventListener('click', () => dismissToast(toast));
  setTimeout(() => dismissToast(toast), 5000);
}

/* Modals System */
function initModals() {
  const openButtons = document.querySelectorAll('[data-modal-target]');
  const closeButtons = document.querySelectorAll('[data-modal-close]');

  openButtons.forEach((btn) => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const targetId = btn.getAttribute('data-modal-target');
      openModal(targetId);
    });
  });

  closeButtons.forEach((btn) => {
    btn.addEventListener('click', () => {
      const modal = btn.closest('.modal-backdrop');
      if (modal) closeModal(modal.id);
    });
  });

  // Close on backdrop click
  document.querySelectorAll('.modal-backdrop').forEach((modal) => {
    modal.addEventListener('click', (e) => {
      if (e.target === modal) {
        closeModal(modal.id);
      }
    });
  });

  // Close on Escape key
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      const activeModal = document.querySelector('.modal-backdrop.active');
      if (activeModal) closeModal(activeModal.id);
    }
  });
}

function openModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.classList.add('active');
    document.body.style.overflow = 'hidden';
    const firstInput = modal.querySelector('input, select, textarea');
    if (firstInput) setTimeout(() => firstInput.focus(), 50);
  }
}

function closeModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.classList.remove('active');
    document.body.style.overflow = '';
  }
}

/* Quick Add Transaction Modal Logic */
function initQuickTransactionForm() {
  const form = document.getElementById('quickAddTransactionForm');
  if (!form) return;

  const typeRadios = form.querySelectorAll('input[name="type"]');
  const categorySelect = form.querySelector('#quickCategory');

  // Categories config
  const expenseCategories = ['Food', 'Travel', 'Shopping', 'Bills', 'Education', 'Entertainment', 'Health', 'Other'];
  const incomeCategories = ['Salary', 'Freelance', 'Investments', 'Gift', 'Allowance', 'Other'];

  function updateCategoryOptions(type) {
    if (!categorySelect) return;
    categorySelect.innerHTML = '<option value="" disabled selected>Select category...</option>';
    const list = type === 'income' ? incomeCategories : expenseCategories;
    list.forEach((cat) => {
      const opt = document.createElement('option');
      opt.value = cat;
      opt.textContent = cat;
      categorySelect.appendChild(opt);
    });
  }

  typeRadios.forEach((radio) => {
    radio.addEventListener('change', (e) => {
      const parentLabels = form.querySelectorAll('.type-radio-label');
      parentLabels.forEach((l) => l.classList.remove('active'));
      radio.closest('.type-radio-label').classList.add('active');
      updateCategoryOptions(radio.value);
    });
  });

  // Handle Form Submission via AJAX
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    submitBtn.disabled = true;
    submitBtn.innerHTML = 'Saving...';

    const formData = new FormData(form);
    const payload = Object.fromEntries(formData.entries());

    try {
      const response = await fetch('/transactions/add', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify(payload)
      });

      const result = await response.json();

      if (response.ok && result.success) {
        showToast(result.message, 'success');
        closeModal('quickAddModal');
        form.reset();
        // Reload dashboard/transactions after 600ms
        setTimeout(() => window.location.reload(), 600);
      } else {
        const errors = result.errors ? result.errors.join('<br>') : 'Error creating transaction.';
        showToast(errors, 'danger');
      }
    } catch (err) {
      showToast('Network error. Please try again.', 'danger');
    } finally {
      submitBtn.disabled = false;
      submitBtn.innerHTML = originalText;
    }
  });
}

/* Live Currency Calculator */
function initCurrencyCalculator() {
  const amountInput = document.getElementById('calcAmount');
  const fromSelect = document.getElementById('calcFrom');
  const toSelect = document.getElementById('calcTo');
  const resultValue = document.getElementById('calcResultValue');
  const rateValue = document.getElementById('calcRateValue');

  if (!amountInput || !fromSelect || !toSelect || !resultValue) return;

  async function updateConversion() {
    const amount = parseFloat(amountInput.value) || 0;
    const fromCurr = fromSelect.value;
    const toCurr = toSelect.value;

    try {
      const res = await fetch(`/api/currency/convert?amount=${amount}&from=${fromCurr}&to=${toCurr}`);
      const data = await res.json();

      if (data.success) {
        resultValue.textContent = data.formatted;
        if (rateValue) {
          rateValue.textContent = `1 ${fromCurr} = ${data.rate.toFixed(4)} ${toCurr}`;
        }
      }
    } catch (err) {
      console.error('Error calculating conversion:', err);
    }
  }

  amountInput.addEventListener('input', updateConversion);
  fromSelect.addEventListener('change', updateConversion);
  toSelect.addEventListener('change', updateConversion);
}

document.addEventListener('DOMContentLoaded', () => {
  initCurrencyCalculator();
});

