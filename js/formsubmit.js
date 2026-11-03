(() => {
  "use strict";

  const contactRoot = document.querySelector(".widget-contact");
  if (!contactRoot) return;

  function configure(contactForm) {
    const nameField = contactForm.querySelector('input[data-aid="CONTACT_FORM_NAME"]');
    const emailField = contactForm.querySelector('input[data-aid="CONTACT_FORM_EMAIL"]');
    const messageField = contactForm.querySelector('[data-aid="CONTACT_FORM_MESSAGE"]');
    const honeypotField = contactForm.querySelector('input[name="_app_id"], input[name="_honey"]');
    if (!(nameField instanceof HTMLInputElement)
      || !(emailField instanceof HTMLInputElement)
      || !(messageField instanceof HTMLTextAreaElement)
      || !(honeypotField instanceof HTMLInputElement)) return false;

    contactForm.action = "https://formsubmit.co/service@swiftalyn.com";
    contactForm.method = "POST";
    nameField.name = "name";
    emailField.name = "email";
    emailField.type = "email";
    emailField.required = true;
    messageField.name = "message";
    honeypotField.name = "_honey";

    let subjectField = contactForm.querySelector('input[name="_subject"]');
    if (!subjectField) {
      subjectField = document.createElement("input");
      subjectField.type = "hidden";
      subjectField.name = "_subject";
      contactForm.append(subjectField);
    }
    subjectField.value = "Swiftalyn website contact form";
    return true;
  }

  function configureForms() {
    contactRoot.querySelectorAll('form[data-ux="Form"]').forEach(configure);
  }
  configureForms();
  // The original widget replaces the form when opening or closing its mobile view.
  new MutationObserver(configureForms).observe(contactRoot, { childList: true, subtree: true });
  contactRoot.addEventListener("submit", event => {
    const form = event.target;
    if (!(form instanceof HTMLFormElement) || !form.matches('form[data-ux="Form"]') || !configure(form)) return;
    event.preventDefault();
    event.stopImmediatePropagation();
    if (!form.checkValidity()) {
      form.reportValidity();
      return;
    }
    HTMLFormElement.prototype.submit.call(form);
  }, true);
})();
