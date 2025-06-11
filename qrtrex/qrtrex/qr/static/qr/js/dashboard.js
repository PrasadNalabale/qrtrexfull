// function readUrl(input,previewId) {
//     if (input.files && input.files[0]) {
//         var reader = new FileReader();
//         reader.onload = function (e) {
//             preview = document.getElementById(previewId);
//             if (preview) {
//                 preview.src = e.target.result;
//             } else {
//                 console.log('Element with id "${previewId}" not found.');
//             }
//         };
//         reader.readAsDataURL(input.files[0]);
//     }
// }
    

// function removeImage(inputId, previewId, defaultImageUrl) {
//     const input = document.getElementById(inputId);
//     const preview = document.getElementById(previewId);

//     if (preview) preview.src = defaultImageUrl;
//     if (input) input.value = "";
// }


// setTimeout(function() {
//       const alerts = document.querySelectorAll('.alert');
//       alerts.forEach(alert => {
//         alert.classList.remove('show');  // fade out
//         alert.classList.add('fade');     // trigger Bootstrap fade animation
//         setTimeout(() => alert.remove(), 500); // remove from DOM after animation
//       });
//     }, 5000); // 5 seconds

// document.querySelectorAll('.offcanvas-close-link').forEach(link => {
//   link.addEventListener('click', function () {
//     if (window.innerWidth < 768) {
//       const sidebar = document.getElementById('sidebarMenu');
//       const offcanvas = bootstrap.Offcanvas.getInstance(sidebar) || new bootstrap.Offcanvas(sidebar);
//       offcanvas.hide();
//     }
//   });
// });


// function submitFormWithImage(formid,input,imagefieldname) {
//     const form = document.getElementById(formid);
//     const fileInput = document.getElementById(input);

//     const formData = new FormData(form);
//     if (fileInput && fileInput.files.length > 0) {
//         formData.append(imagefieldname, fileInput.files[0]);
//     }
//     else {
//         console.log("no files found")
//     }

//     fetch(form.action, {
//         method: 'POST',
//         headers: {
//         'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
//         },
//         body: formData
//     })
//     .then(response => {
//         if (response.ok) {
//         alert('Form submitted successfully!');
//         } else {
//         alert('Error submitting form.');
//         }
//     })
//     .catch(error => {
//         console.error('Submission error:', error);
//         alert('Network or server error.');
//     });
// }



function readUrl(input, previewId) {
  if (input.files && input.files[0]) {
    const reader = new FileReader();
    reader.onload = function (e) {
      const preview = document.getElementById(previewId);
      if (preview) {
        preview.src = e.target.result;
      } else {
        console.log(`Element with id "${previewId}" not found.`);
      }
    };
    reader.readAsDataURL(input.files[0]);
  }
}

function removeImage(inputId, previewId, defaultImageUrl) {
  const input = document.getElementById(inputId);
  const preview = document.getElementById(previewId);

  if (preview) preview.src = defaultImageUrl;
  if (input) input.value = "";
}

setTimeout(() => {
  const alerts = document.querySelectorAll('.alert');
  alerts.forEach(alert => {
    alert.classList.remove('show');  // fade out
    alert.classList.add('fade');     // trigger Bootstrap fade animation
    setTimeout(() => alert.remove(), 500); // remove from DOM after animation
  });
}, 5000); // 5 seconds

document.querySelectorAll('.offcanvas-close-link').forEach(link => {
  link.addEventListener('click', () => {
    if (window.innerWidth < 768) {
      const sidebar = document.getElementById('sidebarMenu');
      const offcanvasInstance = bootstrap.Offcanvas.getInstance(sidebar) || new bootstrap.Offcanvas(sidebar);
      offcanvasInstance.hide();
    }
  });
});

// function submitFormWithImage(formId, inputId, imageFieldName) {
//   const form = document.getElementById(formId);
//   const fileInput = document.getElementById(inputId);

//   if (!form) {
//     console.error(`Form with id "${formId}" not found.`);
//     return;
//   }

//   const formData = new FormData(form);

//   if (fileInput && fileInput.files.length > 0) {
//     formData.append(imageFieldName, fileInput.files[0]);
//   } else {
//     console.log("No files found");
//   }

//   fetch(form.action, {
//     method: 'POST',
//     headers: {
//       'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
//     },
//     body: formData
//   })
//     .then(response => {
//       if (response.ok) {
//         alert('Form submitted successfully!');
//       } else {
//         alert('Error submitting form.');
//       }
//     })
//     .catch(error => {
//       console.error('Submission error:', error);
//       alert('Network or server error.');
//     });
// }
