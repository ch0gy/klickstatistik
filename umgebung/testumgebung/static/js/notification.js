const closeButtons = document.querySelector('.notif__list__item__close-button');

for (const closeButton of closeButtons) {
  closeButton.addEventListener('click', () => {
    const notificationItem = closeButton.closest('.notif__list__item');

    notificationItem.remove();
  });
}


function removeNotificationAfterTimeout(seconds) {
  setTimeout(function () {
    var flash = document.getElementsByClassName('notif__list__item')[0];
    if (flash) {
      flash.style.visibility = 'hidden';
    }
  }, seconds * 1000);
}
