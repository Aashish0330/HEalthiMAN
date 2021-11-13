const pusher = new Pusher("2ccb99d2c1a7248b0984", {
  cluster: "ap2",
  encrypted: true,
});

const channel = pusher.subscribe("blog");
channel.bind("post-added", eventHandler);
channel.bind("post-deleted", eventHandler);
channel.bind("post-deactivated", eventHandler);

function eventHandler(data) {
  const html = `
        <div class="box">
          <article class="media">
            <div class="media-content">
              <div class="content">
                <p>
                  <strong>Post ${data.event_name}</strong>
                  <br>
                  Post with ID [<strong>${data.id}</strong>] has been ${data.event_name} <br> <strong> Post Title :<strong>  ${data.title} <br> 
                </p>
              </div>
            </div>
          </article>
        </div>`;
  let list = document.querySelector("#events");
  list.innerHTML += html;
}
