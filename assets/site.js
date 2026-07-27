const projectsMenu = document.querySelector(".projects-menu");
const wechatDialog = document.getElementById("wechat-dialog");
const wechatOpen = document.getElementById("wechat-open");
const wechatClose = document.getElementById("wechat-close");

function initializeSiteFooter() {
  let footers = Array.from(document.querySelectorAll(".site-footer"));

  if (footers.length === 0) {
    const footer = document.createElement("footer");
    footer.className = "site-footer site-footer-global";
    (document.querySelector("main") || document.body).append(footer);
    footers = [footer];
  }

  footers.forEach((footer) => {
    if (footer.querySelector(".site-footer-legal")) {
      return;
    }

    const legal = document.createElement("span");
    legal.className = "site-footer-legal";
    legal.textContent = `© ${new Date().getFullYear()} YOYOworks. All rights reserved.`;
    footer.append(legal);
  });
}

initializeSiteFooter();

document.querySelectorAll("[data-quota-toggle]").forEach((button) => {
  button.addEventListener("click", () => {
    const details = document.getElementById(button.getAttribute("aria-controls"));
    if (!details) {
      return;
    }

    const willExpand = button.getAttribute("aria-expanded") !== "true";
    details.classList.toggle("is-expanded", willExpand);
    button.setAttribute("aria-expanded", String(willExpand));
    button.textContent = willExpand
      ? button.dataset.collapseLabel
      : button.dataset.expandLabel;
  });
});

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
