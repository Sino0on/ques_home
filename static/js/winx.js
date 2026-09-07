(function () {
  "use strict";

  function getCsrfToken() {
    var el = document.querySelector("input[name=csrfmiddlewaretoken]");
    return el ? el.value : "";
  }

  function shuffle(array) {
    var arr = array.slice();
    for (var i = arr.length - 1; i > 0; i--) {
      var j = Math.floor(Math.random() * (i + 1));
      var tmp = arr[i];
      arr[i] = arr[j];
      arr[j] = tmp;
    }
    return arr;
  }

  var prefersReducedMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function celebrationBurst(originEl) {
    if (prefersReducedMotion || !originEl) return;
    var rect = originEl.getBoundingClientRect();
    var cx = rect.left + rect.width / 2;
    var cy = rect.top + rect.height / 2;
    var colors = ["#ff5fa8", "#4f6fee", "#2fc0e8", "#2ecb8a"];
    var count = 26;

    for (var i = 0; i < count; i++) {
      var el = document.createElement("span");
      el.className = "winx-burst";
      var angle = (Math.PI * 2 * i) / count + Math.random() * 0.4;
      var dist = 70 + Math.random() * 110;
      el.style.left = cx + "px";
      el.style.top = cy + "px";
      el.style.setProperty("--dx", Math.cos(angle) * dist + "px");
      el.style.setProperty("--dy", Math.sin(angle) * dist + "px");
      el.style.background = colors[i % colors.length];
      el.style.color = colors[i % colors.length];
      document.body.appendChild(el);
      (function (node) {
        setTimeout(function () { node.remove(); }, 950);
      })(el);
    }
  }

  function initParticles() {
    var layer = document.getElementById("winxParticles");
    if (!layer || prefersReducedMotion) return;

    var colors = ["pink", "blue", "cool", "green"];
    var total = window.innerWidth < 600 ? 34 : 60;

    for (var i = 0; i < total; i++) {
      var roll = i % 6;
      var isSpark = roll === 0 || roll === 3;
      var isFirefly = roll === 5;
      var el = document.createElement("span");
      var colorClass = colors[i % colors.length];
      var kind = isSpark ? "spark" : isFirefly ? "firefly" : "dot";
      el.className = "winx-particle " + kind + " " + colorClass;

      var size = isFirefly ? 4 + Math.random() * 3 : isSpark ? 5 + Math.random() * 4 : 1.5 + Math.random() * 1.5;
      var left = Math.random() * 100;
      var top = Math.random() * 100;
      var twinkleDuration = 2.5 + Math.random() * 3.5;
      var delay = Math.random() * -6;

      var secondDelay = Math.random() * -10;
      var secondDuration = isSpark ? 6 + Math.random() * 6 : 8 + Math.random() * 10;

      el.style.left = left + "%";
      el.style.top = top + "%";
      el.style.width = size + "px";
      el.style.height = size + "px";
      el.style.animationDelay = delay + "s, " + secondDelay + "s";
      el.style.animationDuration = twinkleDuration + "s, " + secondDuration + "s";

      layer.appendChild(el);
    }
  }

  function initReveal() {
    var items = document.querySelectorAll(".reveal-el");
    if (!items.length) return;

    if (prefersReducedMotion || !("IntersectionObserver" in window)) {
      items.forEach(function (el) { el.classList.add("is-visible"); });
      return;
    }

    var observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-visible");
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.2 }
    );

    items.forEach(function (el) { observer.observe(el); });
  }

  function initDotNav() {
    var dotsNav = document.getElementById("winxDots");
    var slides = document.querySelectorAll(".winx-slide");
    if (!dotsNav || !slides.length) return;

    var dots = Array.prototype.slice.call(dotsNav.querySelectorAll("button"));

    dots.forEach(function (dot) {
      dot.addEventListener("click", function () {
        var target = document.getElementById(dot.dataset.target);
        if (target) target.scrollIntoView({ behavior: "smooth" });
      });
    });

    if ("IntersectionObserver" in window) {
      var observer = new IntersectionObserver(
        function (entries) {
          entries.forEach(function (entry) {
            if (entry.isIntersecting) {
              dots.forEach(function (dot) {
                dot.classList.toggle("active", dot.dataset.target === entry.target.id);
              });
            }
          });
        },
        { threshold: 0.5 }
      );
      slides.forEach(function (slide) { observer.observe(slide); });
    }
  }

  function initSound() {
    var btn = document.getElementById("soundToggle");
    if (!btn) return;
    var onIcon = btn.querySelector(".winx-sound-toggle__on");
    var offIcon = btn.querySelector(".winx-sound-toggle__off");
    var soundOn = true;

    function playFairyChime() {
      try {
        var Ctx = window.AudioContext || window.webkitAudioContext;
        var ctx = new Ctx();
        var now = ctx.currentTime;
        var freqs = [1046.5, 1318.5, 1568.0, 2093.0];
        freqs.forEach(function (freq, i) {
          var osc = ctx.createOscillator();
          var gain = ctx.createGain();
          osc.type = "sine";
          osc.frequency.value = freq;
          var start = now + i * 0.09;
          gain.gain.setValueAtTime(0, start);
          gain.gain.linearRampToValueAtTime(0.15, start + 0.02);
          gain.gain.exponentialRampToValueAtTime(0.001, start + 0.35);
          osc.connect(gain).connect(ctx.destination);
          osc.start(start);
          osc.stop(start + 0.4);
        });
        setTimeout(function () { ctx.close(); }, 900);
      } catch (e) {
        /* WebAudio unsupported or blocked — silently ignore */
      }
    }

    btn.addEventListener("click", function () {
      soundOn = !soundOn;
      onIcon.hidden = !soundOn;
      offIcon.hidden = soundOn;
      btn.setAttribute("aria-label", soundOn ? "Выключить звук" : "Включить звук");
      if (soundOn) playFairyChime();
    });

    setTimeout(function () {
      if (soundOn) playFairyChime();
    }, 900);
  }

  function initHeroFlight() {
    var fairy = document.getElementById("heroFairy");
    var trailLayer = document.getElementById("heroTrail");
    if (!fairy || !trailLayer || prefersReducedMotion) return;

    var duration = 2100;
    var start = performance.now();

    var iv = setInterval(function () {
      var elapsed = performance.now() - start;
      if (elapsed > duration + 200) {
        clearInterval(iv);
        return;
      }
      var rect = fairy.getBoundingClientRect();
      var parentRect = trailLayer.getBoundingClientRect();
      var dot = document.createElement("span");
      dot.className = "winx-hero__dust";
      dot.style.left = rect.left + rect.width / 2 - parentRect.left + "px";
      dot.style.top = rect.top + rect.height / 2 - parentRect.top + "px";
      trailLayer.appendChild(dot);
      setTimeout(function () { dot.remove(); }, 900);
    }, 70);
  }

  function initBoxSpin() {
    var btn = document.getElementById("boxSpinBtn");
    var track = document.getElementById("carouselTrack");
    var resultEl = document.getElementById("boxSpinResult");
    var reel = document.getElementById("boxReel");
    var reelIcon = document.getElementById("boxReelIcon");
    var reelName = document.getElementById("boxReelName");
    if (!btn || !track || !resultEl || !reel) return;

    var cards = Array.prototype.slice.call(track.querySelectorAll(".winx-box__card"));
    var spinning = false;

    function renderTick(index) {
      var card = cards[index];
      var portrait = card.querySelector(".winx-box__card-portrait");
      var color = card.style.getPropertyValue("--card-color");
      var img = portrait.querySelector("img");
      reelIcon.style.boxShadow = "0 0 0 4px " + color;
      if (img) {
        reelIcon.style.backgroundImage = "url(" + img.getAttribute("src") + ")";
        reelIcon.textContent = "";
      } else {
        reelIcon.style.backgroundImage = "none";
        var iconSpan = portrait.querySelector("span");
        reelIcon.textContent = iconSpan ? iconSpan.textContent : "";
      }
      reelName.textContent = card.querySelector("h4").textContent;
    }

    btn.addEventListener("click", function () {
      if (spinning) return;
      spinning = true;
      btn.disabled = true;
      resultEl.textContent = "";
      reel.hidden = false;
      reel.classList.add("spinning");
      cards.forEach(function (c) { c.classList.remove("winx-box__card--picked"); });

      var winner = Math.floor(Math.random() * cards.length);
      var totalTicks = cards.length * 3 + winner + 1;
      var tick = 0;
      var delay = 80;

      function step() {
        var current = tick % cards.length;
        renderTick(current);
        tick++;
        if (tick >= totalTicks) {
          reel.classList.remove("spinning");
          var finalCard = cards[(totalTicks - 1) % cards.length];
          finalCard.classList.add("winx-box__card--picked");
          finalCard.scrollIntoView({ behavior: "smooth", inline: "center", block: "nearest" });
          celebrationBurst(reel);
          resultEl.textContent = "Магия выбрала тебе: " + finalCard.querySelector("h4").textContent;
          spinning = false;
          btn.disabled = false;
          return;
        }
        delay += 14;
        setTimeout(step, delay);
      }

      step();
    });
  }

  function initCarousel() {
    var track = document.getElementById("carouselTrack");
    if (!track) return;
    var prevBtn = document.querySelector(".winx-carousel__nav.prev");
    var nextBtn = document.querySelector(".winx-carousel__nav.next");
    var step = 250;

    if (prevBtn) prevBtn.addEventListener("click", function () { track.scrollBy({ left: -step, behavior: "smooth" }); });
    if (nextBtn) nextBtn.addEventListener("click", function () { track.scrollBy({ left: step, behavior: "smooth" }); });
  }

  function unlockOrderSlide() {
    var locked = document.getElementById("orderLocked");
    var formWrap = document.getElementById("orderFormWrap");
    if (locked) locked.hidden = true;
    if (formWrap) formWrap.hidden = false;
  }

  function initGoToPuzzle() {
    var btn = document.getElementById("goToPuzzleBtn");
    if (!btn) return;
    btn.addEventListener("click", function () {
      var target = document.getElementById("slide-5");
      if (target) target.scrollIntoView({ behavior: "smooth" });
    });
  }

  function initPuzzle() {
    var area = document.getElementById("puzzleArea");
    if (!area) return;

    var board = document.getElementById("puzzleBoard");
    var msg = document.getElementById("puzzleMsg");
    var toOrderBtn = document.getElementById("puzzleToOrder");
    var claimed = area.dataset.claimed === "1";
    var idx = parseInt(area.dataset.puzzleIndex, 10) || 0;
    var image = (window.WINX_PUZZLE_IMAGES || [])[idx];

    toOrderBtn.addEventListener("click", function () {
      var target = document.getElementById("slide-6");
      if (target) target.scrollIntoView({ behavior: "smooth" });
    });

    if (claimed) {
      msg.textContent = "Ты уже получил(а) свою магическую скидку ✨";
      board.hidden = true;
      toOrderBtn.hidden = false;
      unlockOrderSlide();
      return;
    }

    var SIZE = 3;
    var total = SIZE * SIZE;
    var order = [];
    for (var i = 0; i < total; i++) order.push(i);

    function isSolved(arr) {
      return arr.every(function (v, i) { return v === i; });
    }

    do {
      order = shuffle(order);
    } while (isSolved(order));

    var selected = null;
    var solved = false;

    function render() {
      board.innerHTML = "";
      order.forEach(function (tileValue, position) {
        var tile = document.createElement("button");
        tile.type = "button";
        tile.className = "winx-puzzle__tile" + (selected === position ? " selected" : "");
        var col = tileValue % SIZE;
        var row = Math.floor(tileValue / SIZE);
        tile.style.backgroundImage = "url(" + image + ")";
        tile.style.backgroundSize = SIZE * 100 + "% " + SIZE * 100 + "%";
        tile.style.backgroundPosition = (col * 100) / (SIZE - 1) + "% " + (row * 100) / (SIZE - 1) + "%";
        tile.addEventListener("click", function () { onTileClick(position); });
        board.appendChild(tile);
      });
    }

    function onTileClick(position) {
      if (solved) return;
      if (selected === null) {
        selected = position;
        render();
        return;
      }
      if (selected === position) {
        selected = null;
        render();
        return;
      }
      var tmp = order[selected];
      order[selected] = order[position];
      order[position] = tmp;
      selected = null;
      render();
      if (isSolved(order)) {
        solved = true;
        board.classList.add("solved");
        msg.textContent = "Поздравляем! Ты собрал(а) пазл и выиграл(а) 5% скидку на Secret Box.";
        celebrationBurst(board);
        claimDiscount();
      }
    }

    function claimDiscount() {
      fetch(window.WINX_URLS.claim, {
        method: "POST",
        headers: { "X-CSRFToken": getCsrfToken() },
      })
        .then(function () {
          toOrderBtn.hidden = false;
          unlockOrderSlide();
        })
        .catch(function () {
          toOrderBtn.hidden = false;
          unlockOrderSlide();
        });
    }

    render();
  }

  function initOrderForm() {
    var form = document.getElementById("orderForm");
    if (!form) return;

    var methodRadios = form.querySelectorAll("input[name=method]");
    var addressField = document.getElementById("addressField");
    var addressInput = addressField.querySelector("input");
    var errorEl = document.getElementById("orderError");
    var submitBtn = form.querySelector("button[type=submit]");

    function syncAddress() {
      var checked = form.querySelector("input[name=method]:checked");
      var isDelivery = checked && checked.value === "delivery";
      addressField.hidden = !isDelivery;
      addressInput.required = isDelivery;
    }

    methodRadios.forEach(function (radio) { radio.addEventListener("change", syncAddress); });
    syncAddress();

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      errorEl.hidden = true;
      submitBtn.disabled = true;
      submitBtn.textContent = "Отправляем...";

      fetch(window.WINX_URLS.order, {
        method: "POST",
        headers: { "X-CSRFToken": getCsrfToken() },
        body: new FormData(form),
      })
        .then(function (r) { return r.json().then(function (data) { return { ok: r.ok, data: data }; }); })
        .then(function (res) {
          if (res.ok && res.data.ok) {
            document.getElementById("qrModal").hidden = false;
            form.reset();
            syncAddress();
          } else {
            errorEl.textContent = (res.data && res.data.error) || "Что-то пошло не так, попробуй ещё раз";
            errorEl.hidden = false;
          }
        })
        .catch(function () {
          errorEl.textContent = "Не удалось отправить заказ. Проверь соединение и попробуй снова";
          errorEl.hidden = false;
        })
        .finally(function () {
          submitBtn.disabled = false;
          submitBtn.textContent = "Купить";
        });
    });
  }

  function initGamesHub() {
    var cards = document.querySelectorAll(".winx-games__card[data-target]");
    cards.forEach(function (card) {
      card.addEventListener("click", function () {
        var target = document.getElementById(card.dataset.target);
        if (target) target.scrollIntoView({ behavior: "smooth" });
      });
    });
  }

  var QUIZ_CHARACTERS = {
    bloom: {
      name: "Блум",
      monogram: "Б",
      color: "#ff5fa8",
      title: "Сердце, которое ведёт других",
      desc: "У тебя сильное чувство справедливости и удивительная способность не сдаваться. Люди тянутся к тебе и доверяют тебе — ты умеешь вдохновлять и объединять."
    },
    stella: {
      name: "Стелла",
      monogram: "С",
      color: "#ffd76a",
      title: "Солнце с железным характером",
      desc: "Ты лёгкая, яркая и любишь красивую жизнь. За этим сиянием скрывается харизма и уверенность — ты умеешь превращать обычный день в праздник."
    },
    flora: {
      name: "Флора",
      monogram: "Ф",
      color: "#4be3a0",
      title: "Сила через мягкость",
      desc: "Ты редко борешься криком — твоя сила в терпении, заботе и умении видеть хорошее даже в сложных ситуациях. Рядом с тобой людям спокойно."
    },
    musa: {
      name: "Муза",
      monogram: "М",
      color: "#a06bff",
      title: "Та, кто чувствует глубже остальных",
      desc: "Ты проживаешь эмоции очень интенсивно и умеешь превращать чувства в творчество. Искренность — твой самый сильный инструмент."
    },
    tecna: {
      name: "Текна",
      monogram: "Т",
      color: "#4fd3e8",
      title: "Разум, которому можно доверять",
      desc: "Ты редко решаешь импульсивно. Надёжность, логика и объективность делают тебя человеком, к которому идут за советом в любой ситуации."
    },
    aisha: {
      name: "Лейла",
      monogram: "Л",
      color: "#5b6ee8",
      title: "Свобода сильнее страха",
      desc: "Ты независимая и смелая — даже когда боишься, всё равно идёшь вперёд, потому что твоя жизнь принадлежит только тебе."
    }
  };

  var QUIZ_QUESTIONS = [
    {
      q: "Как ты проводишь свободное время?",
      options: [
        { text: "Помогаю близким или разруливаю чью-то ситуацию", c: "bloom" },
        { text: "Устраиваю что-то яркое и весёлое", c: "stella" },
        { text: "Гуляю на природе, ухаживаю за растениями", c: "flora" },
        { text: "Слушаю музыку, рисую или пишу", c: "musa" },
        { text: "Разбираюсь в гаджетах, читаю, планирую", c: "tecna" },
        { text: "Занимаюсь спортом или еду куда-то новое", c: "aisha" }
      ]
    },
    {
      q: "Что для тебя важнее всего?",
      options: [
        { text: "Справедливость и забота о других", c: "bloom" },
        { text: "Уверенность в себе", c: "stella" },
        { text: "Гармония и спокойствие", c: "flora" },
        { text: "Искренние чувства", c: "musa" },
        { text: "Знания и логика", c: "tecna" },
        { text: "Свобода и независимость", c: "aisha" }
      ]
    },
    {
      q: "Как ты ведёшь себя в компании друзей?",
      options: [
        { text: "Первая иду спасать, если что-то случилось", c: "bloom" },
        { text: "Душа компании, всех веселю", c: "stella" },
        { text: "Слушаю и тихо поддерживаю", c: "flora" },
        { text: "Делюсь тем, что чувствую по-настоящему", c: "musa" },
        { text: "Слежу, чтобы всё было по плану", c: "tecna" },
        { text: "Предлагаю самое смелое приключение", c: "aisha" }
      ]
    },
    {
      q: "Какой цвет тебе ближе?",
      options: [
        { text: "Розово-золотой", c: "bloom" },
        { text: "Солнечно-жёлтый", c: "stella" },
        { text: "Природно-зелёный", c: "flora" },
        { text: "Сиреневый", c: "musa" },
        { text: "Бирюзовый", c: "tecna" },
        { text: "Синий с серебром", c: "aisha" }
      ]
    },
    {
      q: "Твой идеальный выходной?",
      options: [
        { text: "Провести время с близкими", c: "bloom" },
        { text: "Шопинг и красивые фото", c: "stella" },
        { text: "Пикник на природе", c: "flora" },
        { text: "Концерт или творческий вечер", c: "musa" },
        { text: "Новый сериал или интересная лекция", c: "tecna" },
        { text: "Активный отдых, путешествие", c: "aisha" }
      ]
    },
    {
      q: "Как ты принимаешь решения?",
      options: [
        { text: "Сердцем", c: "bloom" },
        { text: "Интуицией и настроением", c: "stella" },
        { text: "Не тороплюсь, чувствую момент", c: "flora" },
        { text: "Прислушиваюсь к эмоциям", c: "musa" },
        { text: "Взвешиваю факты", c: "tecna" },
        { text: "Решаю мгновенно и иду вперёд", c: "aisha" }
      ]
    },
    {
      q: "Какая черта в тебе самая сильная?",
      options: [
        { text: "Смелость перед неизвестностью", c: "bloom" },
        { text: "Харизма", c: "stella" },
        { text: "Терпение и забота", c: "flora" },
        { text: "Чувствительность к людям", c: "musa" },
        { text: "Надёжность", c: "tecna" },
        { text: "Решительность", c: "aisha" }
      ]
    },
    {
      q: "Если подруга расстроена, ты…",
      options: [
        { text: "Сразу бегу на помощь", c: "bloom" },
        { text: "Отвлекаю и поднимаю настроение", c: "stella" },
        { text: "Молча обнимаю и просто рядом", c: "flora" },
        { text: "Слушаю и разделяю эмоции", c: "musa" },
        { text: "Помогаю разложить проблему по полочкам", c: "tecna" },
        { text: "Зову на что-то активное, чтобы отвлечься", c: "aisha" }
      ]
    },
    {
      q: "Какой подарок обрадует тебя сильнее всего?",
      options: [
        { text: "Что-то со смыслом, сделанное с душой", c: "bloom" },
        { text: "Яркий аксессуар или украшение", c: "stella" },
        { text: "Растение или что-то для дома", c: "flora" },
        { text: "Билет на концерт или мастер-класс", c: "musa" },
        { text: "Гаджет или интересная книга", c: "tecna" },
        { text: "Билет в путешествие", c: "aisha" }
      ]
    }
  ];

  function initQuiz() {
    var introEl = document.getElementById("quizIntro");
    var gameEl = document.getElementById("quizGame");
    var resultEl = document.getElementById("quizResult");
    if (!introEl || !gameEl || !resultEl) return;

    var startBtn = document.getElementById("quizStartBtn");
    var restartBtn = document.getElementById("quizRestartBtn");
    var questionEl = document.getElementById("quizQuestion");
    var optionsEl = document.getElementById("quizOptions");
    var progressBar = document.getElementById("quizProgressBar");
    var badgeEl = document.getElementById("quizResultBadge");
    var imgEl = document.getElementById("quizResultImg");
    var nameEl = document.getElementById("quizResultName");
    var textEl = document.getElementById("quizResultText");

    var order = ["bloom", "stella", "flora", "musa", "tecna", "aisha"];
    var current = 0;
    var scores = {};

    function renderQuestion() {
      var q = QUIZ_QUESTIONS[current];
      questionEl.textContent = current + 1 + ". " + q.q;
      progressBar.style.width = Math.round((current / QUIZ_QUESTIONS.length) * 100) + "%";
      optionsEl.innerHTML = "";
      q.options.forEach(function (opt) {
        var btn = document.createElement("button");
        btn.type = "button";
        btn.className = "winx-quiz__option";
        btn.textContent = opt.text;
        btn.addEventListener("click", function () { selectOption(opt.c); });
        optionsEl.appendChild(btn);
      });
    }

    function selectOption(characterId) {
      scores[characterId] = (scores[characterId] || 0) + 1;
      current++;
      if (current >= QUIZ_QUESTIONS.length) {
        showResult();
      } else {
        renderQuestion();
      }
    }

    function showResult() {
      progressBar.style.width = "100%";
      var winner = order[0];
      order.forEach(function (id) {
        if ((scores[id] || 0) > (scores[winner] || 0)) winner = id;
      });
      var character = QUIZ_CHARACTERS[winner];
      var imgSrc = (window.WINX_QUIZ_IMAGES || {})[winner];

      if (imgSrc) {
        imgEl.src = imgSrc;
        imgEl.alt = character.name;
        imgEl.hidden = false;
        badgeEl.hidden = true;
      } else {
        imgEl.hidden = true;
        badgeEl.hidden = false;
        badgeEl.textContent = character.monogram;
        badgeEl.style.setProperty("--card-color", character.color);
      }

      nameEl.textContent = "Ты — " + character.name;
      textEl.textContent = character.title + ". " + character.desc;
      gameEl.hidden = true;
      resultEl.hidden = false;
    }

    startBtn.addEventListener("click", function () {
      current = 0;
      scores = {};
      introEl.hidden = true;
      resultEl.hidden = true;
      gameEl.hidden = false;
      renderQuestion();
    });

    restartBtn.addEventListener("click", function () {
      resultEl.hidden = true;
      introEl.hidden = false;
    });
  }

  function initModal() {
    var modal = document.getElementById("qrModal");
    var closeBtn = document.getElementById("qrClose");
    if (!modal || !closeBtn) return;
    closeBtn.addEventListener("click", function () { modal.hidden = true; });
    modal.addEventListener("click", function (e) {
      if (e.target === modal) modal.hidden = true;
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    initParticles();
    initReveal();
    initDotNav();
    initSound();
    initHeroFlight();
    initCarousel();
    initBoxSpin();
    initPuzzle();
    initGoToPuzzle();
    initOrderForm();
    initGamesHub();
    initQuiz();
    initModal();
  });
})();
