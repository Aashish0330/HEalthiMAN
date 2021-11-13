const pusher = new Pusher("2ccb99d2c1a7248b0984", {
  cluster: "ap2",
  encrypted: true,
});

const channel = pusher.subscribe("blog");

channel.bind("post-added", (data) => {
  appendToList(data);
});

channel.bind("post-deleted", (data) => {
  const post = document.querySelector(`#${data.id}`);
  post.parentNode.removeChild(post);
});

channel.bind("post-deactivated", (data) => {
  const post = document.querySelector(`#${data.id}`);
  post.classList.add("deactivated");
});

const form = document.querySelector("#post-form");
form.onsubmit = (e) => {
  e.preventDefault();
  fetch("/post", {
    method: "POST",
    body: new FormData(form),
  }).then((r) => {
    form.reset();
  });
};

function deletePost(id) {
  fetch(`/post/${id}`, {
    method: "DELETE",
  });
}

function deactivatePost(id) {
  fetch(`/post/${id}`, {
    method: "PUT",
  });
}

function appendToList(data) {
  const html = `
      <div class="card" id="${data.id}">
        <header class="card-header">
          <p class="card-header-title">${data.title}</p>
        </header>
        <div class="card-content">
          <div class="content">
            <p>${data.content}</p>
          </div>
        </div>
        <footer class="card-footer">
          <a href="#myZone" onclick="deactivatePost('${data.id}')" class="card-footer-item">Mark completed</a>
          <a href="#myZone" onclick="deletePost('${data.id}')" class="card-footer-item">Delete Post</a>
        </footer>
      </div>`;
  let list = document.querySelector("#post-list");
  list.innerHTML += html;
}
