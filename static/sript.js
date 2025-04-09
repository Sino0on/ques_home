  const pageButtons = document.querySelectorAll(".page");
  const prev = document.getElementById("prev");
  const next = document.getElementById("next");

  function setActive(index) {
    pageButtons.forEach(btn => btn.classList.remove("active"));
    pageButtons[index].classList.add("active");
  }

  pageButtons.forEach((btn, index) => {
    btn.addEventListener("click", () => {
      setActive(index);
    });
  });

  prev.addEventListener("click", () => {
    let activeIndex = [...pageButtons].findIndex(btn => btn.classList.contains("active"));
    if (activeIndex > 0) setActive(activeIndex - 1);
  });

  next.addEventListener("click", () => {
    let activeIndex = [...pageButtons].findIndex(btn => btn.classList.contains("active"));
    if (activeIndex < pageButtons.length - 1) setActive(activeIndex + 1);
  });