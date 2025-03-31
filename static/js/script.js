document.addEventListener('DOMContentLoaded', () => {
  // Определяем элементы шагов
  const step1 = document.getElementById('step1');
  const step2 = document.getElementById('step2');
  const step3 = document.getElementById('step3');
  const step4 = document.getElementById('step4');


  // Данные подкатегорий
  const subcatData = {
    "Катамарани": [
      { name: "2-місний", id: 1 },
      { name: "4-місний", id: 2 }
    ],
    "САП-дошки": [
      { name: "Спортивні", id: 3 },
      { name: "Туристичні", id: 4 },
      { name: "Дитячі", id: 5 }
    ],
    "Каяки": [
      { name: "Одномісний", id: 6 },
      { name: "Двомісний", id: 7 }
    ],
    "Аутрігери": [
      { name: "Одномісний", id: 8 },
      { name: "Двомісний", id: 9 }
    ]
  };

  // Пример временных слотов
  const availableTimes = ["09:00", "11:00", "13:00", "15:00", "17:00"];

  // Элементы для шага 1 (категории)
  const categoryBtns = document.querySelectorAll('.category-btn');
  // Элементы для шага 2 (подкатегории)
  const subcatContainer = document.getElementById('subcat-buttons');
  const backToStep1Btn = document.getElementById('backToStep1'); // кнопка "Назад" на шаге 2 (должна быть добавлена в HTML, если нужна)
  const toStep3Btn = document.getElementById('toStep3');
  let selectedCategory = null;
  let selectedSubcatId = null;

  // Элементы для шага 3 (дата)
  const dateInput = document.getElementById('datepicker');
  const toStep4Btn = document.getElementById('toStep4');
  const backToStep2Btn = document.getElementById('backToStep2'); // кнопка "Назад" на шаге 3

  // Элементы для шага 4 (время и форма)
  const timeSlotsContainer = document.getElementById('time-slots');
  const backToStep3Btn = document.getElementById('backToStep3');
  // Скрытые поля
  const selectedDateInput = document.getElementById('selected-date');
  const selectedHourInput = document.getElementById('selected-hour');
  const selectedEquipmentInput = document.getElementById('selected-equipment-id');

  // Шаг 1: выбор категории
  categoryBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      selectedCategory = btn.getAttribute('data-category');
      // Заполняем подкатегории для выбранной категории
      subcatContainer.innerHTML = "";
      if (subcatData[selectedCategory]) {
        subcatData[selectedCategory].forEach(item => {
          const subBtn = document.createElement('button');
          subBtn.textContent = item.name;
          subBtn.className = "btn btn-primary subcat-btn";
          subBtn.dataset.id = item.id;
          subBtn.addEventListener('click', () => {
            selectedSubcatId = item.id;
            toStep3Btn.disabled = false;
            document.querySelectorAll('.subcat-btn').forEach(b => b.classList.remove('active'));
            subBtn.classList.add('active');
          });
          subcatContainer.appendChild(subBtn);
        });
      }
      // Переход к шагу 2
      step1.classList.add('d-none');
      step2.classList.remove('d-none');
    });
  });

  // Обработчик кнопки "Назад" на шаге 2
  if(backToStep1Btn){
    backToStep1Btn.addEventListener('click', () => {
      step2.classList.add('d-none');
      step1.classList.remove('d-none');
    });
  }

  // Переход со шага 2 к шагу 3
  toStep3Btn.addEventListener('click', () => {
    if (!selectedSubcatId) return;
    selectedEquipmentInput.value = selectedSubcatId;
    step2.classList.add('d-none');
    step3.classList.remove('d-none');
    // Инициализация Litepicker (альтернативный календарь)
    const picker = new Litepicker({
      element: dateInput,
      format: 'YYYY-MM-DD',
      autoApply: true,
      singleMode: true,
      setup: (picker) => {
        picker.on('selected', (date) => {
          selectedDateInput.value = date.format('YYYY-MM-DD');
          toStep4Btn.disabled = false;
        });
      }
    });
  });

  // Обработчик кнопки "Назад" на шаге 3
  backToStep2Btn.addEventListener('click', () => {
    step3.classList.add('d-none');
    step2.classList.remove('d-none');
  });

  // Переход со шага 3 к шагу 4
  toStep4Btn.addEventListener('click', () => {
    if (!selectedDateInput.value) return;
    step3.classList.add('d-none');
    step4.classList.remove('d-none');
    populateTimeSlots();
  });

  // Функция заполнения временных слотов
  function populateTimeSlots() {
    timeSlotsContainer.innerHTML = "";
    availableTimes.forEach(time => {
      const timeBtn = document.createElement('button');
      timeBtn.textContent = time;
      timeBtn.className = "btn btn-outline-primary time-btn";
      timeBtn.addEventListener('click', () => {
        document.querySelectorAll('.time-btn').forEach(btn => {
          btn.classList.remove('active');
          btn.classList.remove('btn-primary');
          btn.classList.add('btn-outline-primary');
        });
        timeBtn.classList.add('active');
        timeBtn.classList.remove('btn-outline-primary');
        timeBtn.classList.add('btn-primary');
        selectedHourInput.value = time;
      });
      timeSlotsContainer.appendChild(timeBtn);
    });
  }

  // Обработчик кнопки "Назад" на шаге 4
  backToStep3Btn.addEventListener('click', () => {
    step4.classList.add('d-none');
    step3.classList.remove('d-none');
  });

  // Обработка отправки формы бронирования
const bookingForm = document.getElementById('booking-form');
const bookingMessage = document.getElementById('booking-message');

bookingForm.addEventListener('submit', (e) => {
  e.preventDefault();
  
  // Собираем данные формы
  const data = {
    name: document.getElementById('name').value,
    phone: document.getElementById('phone').value,
    email: document.getElementById('email').value,
    quantity: parseInt(document.getElementById('quantity').value) || 1,
    date: document.getElementById('selected-date').value,
    hour: document.getElementById('selected-hour').value,
    equipment_id: document.getElementById('selected-equipment-id').value
  };

  // Отправляем POST-запрос на сервер
  fetch('/api/book', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
  })
  .then(response => response.json())
  .then(result => {
    if (result.booking_id) {
      bookingMessage.textContent = "Дякуємо, бронювання оформлено!";
      bookingMessage.className = "alert alert-success";
      bookingForm.reset();
    } else if (result.error) {
      bookingMessage.textContent = result.error;
      bookingMessage.className = "alert alert-danger";
    }
  })
  .catch(error => {
    console.error("Error:", error);
    bookingMessage.textContent = "Сталася помилка при оформленні бронювання.";
    bookingMessage.className = "alert alert-danger";
  });
});

});
