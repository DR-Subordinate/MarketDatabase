export function initMainPage() {
  toggleSeeMore();
}

interface ToggleElements {
  seeMoreText: HTMLElement;
  seeMoreIcon: HTMLElement;
  oldLinkList: HTMLElement;
}

function getToggleElements(): ToggleElements | null {
  const seeMoreText = document.getElementById("see_more");
  const seeMoreIcon = document.querySelector<HTMLElement>("#see_more > .text-blue-500");
  const oldLinkList = document.getElementById("old_link_list");

  if (!seeMoreText || !seeMoreIcon || !oldLinkList) {
    return null;
  }

  return { seeMoreText, seeMoreIcon, oldLinkList };
}

function toggleSeeMore(): void {
  const toggleElements = getToggleElements();

  if (!toggleElements) {
    return;
  }

  toggleElements.seeMoreText.addEventListener("click", () => {
    const isHidden = toggleElements.oldLinkList.classList.toggle("hidden");
    toggleElements.seeMoreIcon.textContent = isHidden ? "+" : "−";
  });
}
