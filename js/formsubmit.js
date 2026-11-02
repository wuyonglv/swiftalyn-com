(() => {
  "use strict";

  const contactForm = document.querySelector('form[data-ux="Form"]');

  if (!contactForm) {
    throw new Error("Contact form was not found.");
  }

  contactForm.action = "https://formsubmit.co/service@swiftalyn.com";
  contactForm.method = "POST";

  const nameField = contactForm.querySelector('[data-aid="CONTACT_FORM_NAME"]');
  const emailField = contactForm.querySelector('[data-aid="CONTACT_FORM_EMAIL"]');
  const messageField = contactForm.querySelector('[data-aid="CONTACT_FORM_MESSAGE"]');
  const honeypotField = contactForm.querySelector('input[name="_app_id"]');

  if (!(nameField instanceof HTMLInputElement)
    || !(emailField instanceof HTMLInputElement)
    || !(messageField instanceof HTMLTextAreaElement)
    || !(honeypotField instanceof HTMLInputElement)) {
    throw new Error("Contact form fields are incomplete.");
  }

  nameField.name = "name";
  emailField.name = "email";
  emailField.type = "email";
  emailField.required = true;
  messageField.name = "message";
  honeypotField.name = "_honey";

  const subjectField = document.createElement("input");
  subjectField.type = "hidden";
  subjectField.name = "_subject";
  subjectField.value = "Swiftalyn website contact form";
  contactForm.append(subjectField);
})();
