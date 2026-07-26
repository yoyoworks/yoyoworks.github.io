const projectsMenu = document.querySelector(".projects-menu");
const wechatDialog = document.getElementById("wechat-dialog");
const wechatOpen = document.getElementById("wechat-open");
const wechatClose = document.getElementById("wechat-close");

document.addEventListener("click", (event) => {
  if (projectsMenu && !projectsMenu.contains(event.target)) {
    projectsMenu.removeAttribute("open");
  }
});

if (wechatDialog && wechatOpen && wechatClose) {
  wechatOpen.addEventListener("click", () => {
    if (typeof wechatDialog.showModal === "function") {
      wechatDialog.showModal();
    } else {
      wechatDialog.setAttribute("open", "");
    }
  });

  wechatClose.addEventListener("click", () => {
    wechatDialog.close();
  });

  wechatDialog.addEventListener("click", (event) => {
    const rect = wechatDialog.getBoundingClientRect();
    const inside =
      event.clientX >= rect.left &&
      event.clientX <= rect.right &&
      event.clientY >= rect.top &&
      event.clientY <= rect.bottom;

    if (!inside) {
      wechatDialog.close();
    }
  });
}
