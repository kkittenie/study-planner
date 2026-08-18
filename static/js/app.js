// Frontend Interactive Script for Study Planner
document.addEventListener('DOMContentLoaded', () => {
  // ============================================================
  // FLOATING TOAST NOTIFICATION AUTO-DISMISS SYSTEM
  // ============================================================
  const toasts = document.querySelectorAll('.toast-editorial');
  toasts.forEach(toast => {
    // Show toast with smooth entry animation
    setTimeout(() => {
      toast.classList.add('show');
    }, 50);

    const autoDismissMs = parseInt(toast.getAttribute('data-toast-auto-dismiss')) || 4000;
    const progressBar = toast.querySelector('.toast-progress-bar');
    
    if (progressBar) {
      progressBar.style.transitionDuration = `${autoDismissMs}ms`;
      setTimeout(() => {
        progressBar.style.width = '0%';
      }, 50);
    }

    const dismissToast = () => {
      toast.classList.remove('show');
      toast.classList.add('hiding');
      setTimeout(() => {
        toast.remove();
      }, 300);
    };

    const closeBtn = toast.querySelector('.toast-close');
    if (closeBtn) {
      closeBtn.addEventListener('click', dismissToast);
    }

    setTimeout(dismissToast, autoDismissMs);
  });

  // ============================================================
  // 1. CUSTOM CONFIRMATION ALERT MODAL SYSTEM
  // ============================================================
  let modalBackdrop = document.getElementById('custom-modal-backdrop');
  if (!modalBackdrop) {
    modalBackdrop = document.createElement('div');
    modalBackdrop.id = 'custom-modal-backdrop';
    modalBackdrop.className = 'custom-modal-backdrop';
    modalBackdrop.innerHTML = `
      <div class="custom-modal-card">
        <div class="custom-modal-icon">
          <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/><line x1="10" y1="11" x2="10" y2="17"/><line x1="14" y1="11" x2="14" y2="17"/></svg>
        </div>
        <h3 class="custom-modal-title" id="custom-modal-title">Konfirmasi Hapus</h3>
        <p class="custom-modal-message" id="custom-modal-message">Apakah kamu yakin ingin menghapus item ini?</p>
        <div class="custom-modal-actions">
          <button type="button" class="btn-editorial btn-editorial-teal" id="custom-modal-cancel">Batal</button>
          <button type="button" class="btn-editorial btn-editorial-coral" id="custom-modal-confirm">Ya, Hapus</button>
        </div>
      </div>
    `;
    document.body.appendChild(modalBackdrop);
  }

  const modalTitle = document.getElementById('custom-modal-title');
  const modalMessage = document.getElementById('custom-modal-message');
  const modalCancel = document.getElementById('custom-modal-cancel');
  const modalConfirm = document.getElementById('custom-modal-confirm');

  let pendingForm = null;

  const showConfirmModal = (message, form) => {
    pendingForm = form;
    modalTitle.textContent = "Konfirmasi Hapus";
    modalMessage.textContent = message || "Apakah kamu yakin ingin menghapus item ini?";
    modalBackdrop.classList.add('active');
  };

  const hideConfirmModal = () => {
    modalBackdrop.classList.remove('active');
    pendingForm = null;
  };

  if (modalCancel) modalCancel.addEventListener('click', hideConfirmModal);
  if (modalBackdrop) {
    modalBackdrop.addEventListener('click', (e) => {
      if (e.target === modalBackdrop) hideConfirmModal();
    });
  }

  if (modalConfirm) {
    modalConfirm.addEventListener('click', () => {
      if (pendingForm) {
        const formToSubmit = pendingForm;
        hideConfirmModal();
        formToSubmit.submit();
      }
    });
  }

  // Intercept all forms with onsubmit containing confirm(...) or data-confirm
  const confirmForms = document.querySelectorAll('form[onsubmit*="confirm"], form[data-confirm]');
  confirmForms.forEach(form => {
    const onsubmitAttr = form.getAttribute('onsubmit');
    let message = "Apakah kamu yakin ingin menghapus item ini?";

    if (onsubmitAttr) {
      const match = onsubmitAttr.match(/confirm\(['"](.+?)['"]\)/);
      if (match && match[1]) {
        message = match[1];
      }
      form.removeAttribute('onsubmit');
    } else if (form.hasAttribute('data-confirm')) {
      message = form.getAttribute('data-confirm');
    }

    form.addEventListener('submit', (e) => {
      e.preventDefault();
      showConfirmModal(message, form);
    });
  });

  // ============================================================
  // 2. CUSTOM SELECT DROPDOWN COMPONENT GENERATOR
  // ============================================================
  const nativeSelects = document.querySelectorAll('select.form-control');
  
  nativeSelects.forEach(select => {
    select.style.display = 'none';

    const wrapper = document.createElement('div');
    wrapper.className = 'custom-select-wrapper';

    const trigger = document.createElement('div');
    trigger.className = 'custom-select-trigger';

    const selectedOption = select.options[select.selectedIndex] || select.options[0];
    const triggerText = document.createElement('span');
    triggerText.textContent = selectedOption ? selectedOption.text : '';

    const triggerIcon = document.createElement('span');
    triggerIcon.className = 'chevron';
    triggerIcon.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"/></svg>`;

    trigger.appendChild(triggerText);
    trigger.appendChild(triggerIcon);
    wrapper.appendChild(trigger);

    const optionsContainer = document.createElement('div');
    optionsContainer.className = 'custom-select-options';

    Array.from(select.options).forEach(opt => {
      const optionDiv = document.createElement('div');
      optionDiv.className = 'custom-option' + (opt.selected ? ' selected' : '');
      optionDiv.dataset.value = opt.value;
      optionDiv.innerHTML = `<span>${opt.text}</span>` + (opt.selected ? `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--coral)" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>` : '');

      optionDiv.addEventListener('click', (e) => {
        e.stopPropagation();
        select.value = opt.value;
        triggerText.textContent = opt.text;

        optionsContainer.querySelectorAll('.custom-option').forEach(el => el.classList.remove('selected'));
        optionDiv.classList.add('selected');

        wrapper.classList.remove('open');

        // Dispatch change event on native select so filter forms trigger autoload!
        select.dispatchEvent(new Event('change', { bubbles: true }));
      });

      optionsContainer.appendChild(optionDiv);
    });

    wrapper.appendChild(optionsContainer);

    trigger.addEventListener('click', (e) => {
      e.stopPropagation();
      document.querySelectorAll('.custom-select-wrapper.open').forEach(w => {
        if (w !== wrapper) w.classList.remove('open');
      });
      wrapper.classList.toggle('open');
    });

    select.parentNode.insertBefore(wrapper, select);
    wrapper.appendChild(select);

    // Autoload listener on select change
    select.addEventListener('change', () => {
      const filterForm = select.closest('.tasks-filter-form');
      if (filterForm) {
        filterForm.submit();
      }
    });
  });

  // Autoload search input with debounce
  const searchInput = document.getElementById('q');
  if (searchInput) {
    let searchTimeout = null;
    searchInput.addEventListener('input', () => {
      clearTimeout(searchTimeout);
      searchTimeout = setTimeout(() => {
        const form = searchInput.closest('form');
        if (form) form.submit();
      }, 450);
    });
  }

  // Close custom select dropdowns when clicking outside
  document.addEventListener('click', () => {
    document.querySelectorAll('.custom-select-wrapper.open').forEach(w => {
      w.classList.remove('open');
    });
  });

  // ============================================================
  // 3. USER HEADER DROPDOWN MENU CONTROLLER
  // ============================================================
  const userMenuTrigger = document.getElementById('user-header-trigger');
  const userMenu = document.getElementById('user-header-menu');

  if (userMenuTrigger && userMenu) {
    userMenuTrigger.addEventListener('click', (e) => {
      e.stopPropagation();
      userMenu.classList.toggle('open');
    });

    document.addEventListener('click', () => {
      userMenu.classList.remove('open');
    });
  }

  // ============================================================
  // 4. POP-UP FORM MODAL CONTROLLER
  // ============================================================
  const modalTriggers = document.querySelectorAll('[data-open-modal]');
  modalTriggers.forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const targetId = btn.getAttribute('data-open-modal');
      const modal = document.querySelector(targetId);
      if (modal) {
        modal.classList.add('active');
      }
    });
  });

  const modalCloses = document.querySelectorAll('[data-close-modal]');
  modalCloses.forEach(btn => {
    btn.addEventListener('click', () => {
      const modal = btn.closest('.modal-form-backdrop');
      if (modal) {
        modal.classList.remove('active');
      }
    });
  });

  document.querySelectorAll('.modal-form-backdrop').forEach(backdrop => {
    backdrop.addEventListener('click', (e) => {
      if (e.target === backdrop) {
        backdrop.classList.remove('active');
      }
    });
  });

  // ============================================================
  // 5. PASSWORD EYE TOGGLE INITIALIZER SYSTEM
  // ============================================================
  const initPasswordToggles = () => {
    const passwordInputs = document.querySelectorAll('input[type="password"]');
    passwordInputs.forEach(input => {
      if (input.closest('.password-input-wrapper')) return;

      const wrapper = document.createElement('div');
      wrapper.className = 'password-input-wrapper';

      input.parentNode.insertBefore(wrapper, input);
      wrapper.appendChild(input);

      const toggleBtn = document.createElement('button');
      toggleBtn.type = 'button';
      toggleBtn.className = 'password-toggle-btn';
      toggleBtn.setAttribute('aria-label', 'Tampilkan Kata Sandi');
      toggleBtn.setAttribute('title', 'Tampilkan Kata Sandi');

      const eyeOpenSVG = `<svg class="eye-icon eye-open" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>`;
      const eyeClosedSVG = `<svg class="eye-icon eye-closed" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="display: none;"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>`;

      toggleBtn.innerHTML = eyeOpenSVG + eyeClosedSVG;
      wrapper.appendChild(toggleBtn);

      const eyeOpen = toggleBtn.querySelector('.eye-open');
      const eyeClosed = toggleBtn.querySelector('.eye-closed');

      toggleBtn.addEventListener('click', (e) => {
        e.preventDefault();
        const isPassword = input.type === 'password';
        input.type = isPassword ? 'text' : 'password';

        if (isPassword) {
          eyeOpen.style.display = 'none';
          eyeClosed.style.display = 'block';
          toggleBtn.setAttribute('title', 'Sembunyikan Kata Sandi');
          toggleBtn.setAttribute('aria-label', 'Sembunyikan Kata Sandi');
        } else {
          eyeOpen.style.display = 'block';
          eyeClosed.style.display = 'none';
          toggleBtn.setAttribute('title', 'Tampilkan Kata Sandi');
          toggleBtn.setAttribute('aria-label', 'Tampilkan Kata Sandi');
        }
      });
    });
  };

  initPasswordToggles();
});
