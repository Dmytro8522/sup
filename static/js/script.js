document.addEventListener("DOMContentLoaded", () => {
  const step1 = document.getElementById("step1");
  const step2 = document.getElementById("step2");
  const step3 = document.getElementById("step3");
  const step4 = document.getElementById("step4");

  const subcatButtons = document.getElementById("subcat-buttons");
  const selectedEquipmentIdInput = document.getElementById("selected-equipment-id");

  const toStep3 = document.getElementById("toStep3");
  const toStep4 = document.getElementById("toStep4");

  const backToStep1 = document.getElementById("backToStep1");
  const backToStep2 = document.getElementById("backToStep2");
  const backToStep3 = document.getElementById("backToStep3");

  const timeSlots = document.getElementById("time-slots");
  const selectedDateInput = document.getElementById("selected-date");
  const selectedHourInput = document.getElementById("selected-hour");

  let selectedCategory = null;
  let availableDates = [];

  // Категории
  document.querySelectorAll(".category-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      selectedCategory = btn.dataset.category;
      fetch("/admin/equipment")
        .then(res => res.json())
        .then(data => {
          subcatButtons.innerHTML = "";
          const filtered = data.filter(eq => eq.category === selectedCategory);
          filtered.forEach(eq => {
            const b = document.createElement("button");
            b.className = "btn btn-outline-primary subcategory-btn";
            b.dataset.id = eq.id;
            b.textContent = eq.subcategory;
            b.addEventListener("click", () => {
              selectedEquipmentIdInput.value = eq.id;
              document.querySelectorAll(".subcategory-btn").forEach(bb => bb.classList.remove("active"));
              b.classList.add("active");
              toStep3.disabled = false;
            });
            subcatButtons.appendChild(b);
          });

          step1.classList.add("d-none");
          step2.classList.remove("d-none");
        });
    });
  });

  // Переходы
  toStep3.addEventListener("click", () => {
    step2.classList.add("d-none");
    step3.classList.remove("d-none");
  });

  toStep4.addEventListener("click", () => {
    step3.classList.add("d-none");
    step4.classList.remove("d-none");
  });

  backToStep1.addEventListener("click", () => {
    step1.classList.remove("d-none");
    step2.classList.add("d-none");
  });

  backToStep2.addEventListener("click", () => {
    step2.classList.remove("d-none");
    step3.classList.add("d-none");
  });

  backToStep3.addEventListener("click", () => {
    step4.classList.add("d-none");
    step3.classList.remove("d-none");
  });

  // Litepicker
  const picker = new Litepicker({
    element: document.getElementById("datepicker"),
    format: "YYYY-MM-DD",
    lang: "uk-UA",
    lockDaysFilter: (date) => !availableDates.includes(date.format("YYYY-MM-DD")),
    setup: (picker) => {
      picker.on("selected", (date) => {
        const selectedDate = date.format("YYYY-MM-DD");
        selectedDateInput.value = selectedDate;
        loadHours(selectedDate);
        toStep4.disabled = false;
      });
    }
  });

  // Загрузка доступных дат
  fetch("/api/availability")
    .then(res => res.json())
    .then(data => {
      availableDates = data.dates;
      picker.setOptions({ lockDaysFilter: (d) => !availableDates.includes(d.format("YYYY-MM-DD")) });
    });

  // Загрузка времени
  function loadHours(date) {
    fetch("/api/availability?date=" + date)
      .then(res => res.json())
      .then(data => {
        timeSlots.innerHTML = "";

        if (data.hours.length === 0) {
          timeSlots.innerHTML = '<div class="text-danger">На цей день немає вільного спорядження або графіка.</div>';
          toStep4.disabled = true;
          return;
        } else {
          toStep4.disabled = false;
        }

        data.hours.forEach(h => {
          const btn = document.createElement("button");
          btn.className = "btn btn-outline-primary m-1";
          btn.textContent = h;
          btn.addEventListener("click", () => {
            selectedHourInput.value = h;
            document.querySelectorAll("#time-slots button").forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
          });
          timeSlots.appendChild(btn);
        });
      });
  }

  // Отправка формы
  const bookingForm = document.getElementById("booking-form");
  bookingForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    if (!selectedHourInput.value) {
      alert("Будь ласка, оберіть час.");
      return;
    }

    const payload = {
      name: document.getElementById("name").value,
      phone: document.getElementById("phone").value,
      email: document.getElementById("email").value,
      date: selectedDateInput.value,
      hour: selectedHourInput.value,
      items: [
        {
          equipment_id: selectedEquipmentIdInput.value,
          quantity: document.getElementById("quantity").value
        }
      ]
    };

    const res = await fetch("/api/book", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    const result = await res.json();
    if (res.ok) {
      document.getElementById("booking-message").innerHTML = '<div class="alert alert-success">Успішно заброньовано!</div>';
    } else {
      document.getElementById("booking-message").innerHTML = '<div class="alert alert-danger">' + (result.error || 'Помилка') + '</div>';
    }
  });
});
