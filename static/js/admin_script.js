document.addEventListener('DOMContentLoaded', () => {
  const equipTab = document.getElementById('equip-tab');
  const schedTab = document.getElementById('sched-tab');
  const bookingsTab = document.getElementById('bookings-tab');
  const exportBtn = document.getElementById('export-btn');

  const equipmentSection = document.getElementById('equipment-admin-section');
  const scheduleSection = document.getElementById('schedule-admin-section');
  const bookingsSection = document.getElementById('bookings-admin-section');

  equipTab.addEventListener('click', () => {
    equipmentSection.classList.remove('hidden');
    scheduleSection.classList.add('hidden');
    bookingsSection.classList.add('hidden');
  });
  schedTab.addEventListener('click', () => {
    equipmentSection.classList.add('hidden');
    scheduleSection.classList.remove('hidden');
    bookingsSection.classList.add('hidden');
  });
  bookingsTab.addEventListener('click', () => {
    equipmentSection.classList.add('hidden');
    scheduleSection.classList.add('hidden');
    bookingsSection.classList.remove('hidden');
  });
  exportBtn.addEventListener('click', () => {
    window.location.href = '/admin/export';
  });

  // Здесь можно добавить вызовы fetch для загрузки данных и заполнения таблиц.
});
