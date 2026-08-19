/**
 * SMART EXPENSE TRACKER - TRANSACTIONS PAGE JS
 * Handles dynamic category switching, date filters, and delete actions
 */

document.addEventListener('DOMContentLoaded', () => {
  initTransactionTypeToggle();
  initTimeframeFilter();
  initDeleteButtons();
});

/* Toggle Categories when Type changes between Expense and Income */
function initTransactionTypeToggle() {
  const typeRadios = document.querySelectorAll('input[name="type"]');
  const categorySelect = document.getElementById('transactionCategory');

  const expenseCategories = ['Food', 'Travel', 'Shopping', 'Bills', 'Education', 'Entertainment', 'Health', 'Other'];
  const incomeCategories = ['Salary', 'Freelance', 'Investments', 'Gift', 'Allowance', 'Other'];

  if (!typeRadios.length || !categorySelect) return;

  function updateCategories(selectedType, selectedCategory = '') {
    categorySelect.innerHTML = '<option value="" disabled selected>Select category...</option>';
    const list = selectedType === 'income' ? incomeCategories : expenseCategories;
    
    list.forEach((cat) => {
      const opt = document.createElement('option');
      opt.value = cat;
      opt.textContent = cat;
      if (cat === selectedCategory) opt.selected = true;
      categorySelect.appendChild(opt);
    });
  }

  typeRadios.forEach((radio) => {
    radio.addEventListener('change', () => {
      // Update styling on radio wrapper pills
      document.querySelectorAll('.type-radio-label').forEach((label) => {
        label.classList.remove('active');
      });
      radio.closest('.type-radio-label').classList.add('active');
      updateCategories(radio.value);
    });
  });
}

/* Timeframe Filter custom date range toggle */
function initTimeframeFilter() {
  const timeframeSelect = document.getElementById('timeframeSelect');
  const customDateRow = document.getElementById('customDateRow');

  if (timeframeSelect && customDateRow) {
    timeframeSelect.addEventListener('change', () => {
      if (timeframeSelect.value === 'custom') {
        customDateRow.classList.remove('hidden');
      } else {
        customDateRow.classList.add('hidden');
      }
    });
  }
}

/* Handle Transaction Deletion with Confirmation */
function initDeleteButtons() {
  const deleteForms = document.querySelectorAll('.delete-transaction-form');

  deleteForms.forEach((form) => {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();

      if (!confirm('Are you sure you want to delete this transaction? This action cannot be undone.')) {
        return;
      }

      const row = form.closest('tr');
      const actionUrl = form.getAttribute('action');

      try {
        const response = await fetch(actionUrl, {
          method: 'POST',
          headers: {
            'X-Requested-With': 'XMLHttpRequest'
          }
        });

        const result = await response.json();

        if (response.ok && result.success) {
          showToast('Transaction deleted successfully', 'info');
          if (row) {
            row.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
            row.style.opacity = '0';
            row.style.transform = 'scale(0.95)';
            setTimeout(() => {
              row.remove();
              // If table empty, refresh to update pagination
              const remainingRows = document.querySelectorAll('.data-table tbody tr');
              if (remainingRows.length === 0) window.location.reload();
            }, 300);
          }
        } else {
          showToast('Failed to delete transaction.', 'danger');
        }
      } catch (err) {
        showToast('Network error while deleting.', 'danger');
      }
    });
  });
}
