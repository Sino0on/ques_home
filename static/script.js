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

   function showSkeletons() {
     const container = document.getElementById("product-list");
     let skeletonHTML = '';
     for (let i = 0; i < 12; i++) {
       skeletonHTML += `
         <div class="product__cart skeleton">
           <div class="skeleton-box skeleton-img"></div>
           <div style="flex:1;">
             <div class="skeleton-box skeleton-text"></div>
             <div class="skeleton-box skeleton-text" style="width: 70%;"></div>
             <div class="skeleton-box skeleton-price"></div>
           </div>
         </div>
       `;
     }
     container.innerHTML = skeletonHTML;
   }

   function loadRealProducts() {
     const container = document.getElementById("product-list");
     const productHTML = `
       ${[...Array(12)].map(() => `
         <a href="/src/page/productDetail.html" class="product__cart">
           <img src="./src/assets/product/sonic.png" alt="#">
           <div class="product__info">
             <h5>Еще что то там</h5>
             <h4>Что то там...</h4>
             <p>999 KGS</p>
           </div>
         </a>
       `).join('')}
     `;
     container.innerHTML = productHTML;
   }

   document.addEventListener("DOMContentLoaded", function () {
     showSkeletons();
     setTimeout(loadRealProducts, 1000); // Задержка
   });