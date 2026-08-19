/**
 * SMART EXPENSE TRACKER - BUDGETS JS
 * Budget management, modal pre-fill, and preset quick selectors
 */

document.addEventListener('DOMContentLoaded', () => {
  initBudgetPresets();
  initEditBudgetButtons();
});

function initBudgetPresets() {
  const presetBtns = document.querySelectorAll('.budget-preset-btn');
  const amountInput = document.getElementById('budgetAmountInput');

  if (amountInput) {
    presetBtns.forEach((btn) => {
      btn.addEventListener('click', () => {
        amountInput.value = btn.dataset.amount;
      });
    });
  }
}

function initEditBudgetButtons() {
  const editBtns = document.querySelectorAll('.btn-edit-budget');
  const modal = document.getElementById('setBudgetModal');
  const catSelect = document.getElementById('budgetCategorySelect');
  const amountInput = document.getElementById('budgetAmountInput');

  if (editBtns && modal && catSelect && amountInput) {
    editBtns.forEach((btn) => {
      btn.addEventListener('click', () => {
        const cat = btn.dataset.category || 'overall';
        const amount = btn.dataset.amount || '';

        catSelect.value = cat;
        amountInput.value = amount;
        openModal('setBudgetModal');
      });
    });
  }
}
