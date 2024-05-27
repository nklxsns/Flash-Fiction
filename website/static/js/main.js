function for_span(fieldId, spanId) {
  var span = document.getElementById(spanId);
  console.log(this.className);
  var input = document.getElementById(fieldId);
  if (input.getAttribute("type") == "password") {
    input.setAttribute("type", "text");
    span.className = span.className.replace("fa-eye", "fa-eye-slash");
  } else {
    input.setAttribute("type", "password");
    span.className = span.className.replace("fa-eye-slash", "fa-eye");
  }
}

function checkPassword() {
  var pass1 = document.getElementById("password-field1").value;
  var pass2 = document.getElementById("password-field2").value;

  if (pass1 !== pass2) {
    alert("Passwords Do Not Match.");
    return false;
  }
  return true;
}

function copyToClipboard(text) {
  navigator.clipboard
    .writeText(text)
    .then(() => {
      alert("Link Copied");
    })
    .catch((error) => {
      console.error(`Could not copy text: ${error}`);
      alert(`Could not copy text: ${error}`);
    });
}

function viewContri(data) {
  document.getElementById("modal-closer").click();
  mutable_div = document.getElementById("editable");
  mutable_div.innerHTML = data;
  mutable_div.style.color = "rgb(150, 211, 219)";
  mutable_div.scrollIntoView();
}

function loadContri() {
  const urlParams = new URLSearchParams(window.location.search);
  if (urlParams.has("data")) {
    viewContri(urlParams.get("data"));
  }
}

function likeStory(storyId) {
  const likeCount = document.getElementById(`story-likes-count-${storyId}`);
  const likeButton = document.getElementById(`story-like-button-${storyId}`);

  fetch(`/like-story/${storyId}`, { method: "GET" })
    .then((res) => res.json())
    .then((data) => {
      likeCount.innerHTML = data["likes"];
      if (data["liked"]) {
        likeButton.checked = true;
      } else {
        likeButton.checked = false;
      }
    });
}

function likeContribution(contributionId) {
  const likeCount = document.getElementById(
    `contribution-likes-count-${contributionId}`
  );
  const likeButton = document.getElementById(
    `contribution-like-button-${contributionId}`
  );

  fetch(`/like-contribution/${contributionId}`, { method: "GET" })
    .then((res) => res.json())
    .then((data) => {
      likeCount.innerHTML = data["likes"];
      if (data["liked"]) {
        likeButton.checked = true;
      } else {
        likeButton.checked = false;
      }
    });
}

function deleteStory(storyId) {
  fetch(`/delete-story/${storyId}`, { method: "GET" })
    .then((res) => res.json())
    .then((data) => {
      document.location.reload();
    });
}

function deleteContribution(contributionId) {
  fetch(`/delete-contribution/${contributionId}`, { method: "GET" })
    .then((res) => res.json())
    .then((data) => {
      document.location.reload();
    });
}
