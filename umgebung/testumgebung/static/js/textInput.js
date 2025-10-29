function adjustFontSize() {
  const textInputs = document.querySelectorAll('.textInput');

  textInputs.forEach(textInput => {
    const container = textInput.closest('.subject_button');
    if (!container) return;

    const maxWidth = container.offsetWidth;
    const maxHeight = container.offsetHeight;

    let fontSize = 220; 

    // Reset line height to match font size
    textInput.style.lineHeight = '1';

    // Function to check if text fits
    const textFits = () => {
      const rect = textInput.getBoundingClientRect();
      return rect.width <= maxWidth * 0.9 && rect.height <= maxHeight * 0.6;
    };

    // Decrease font size until text fits with some padding
    while (!textFits() && fontSize > 10) {
      fontSize -= 2;
      textInput.style.fontSize = `${fontSize}px`;
    }
  });
}

window.addEventListener('load', adjustFontSize);
window.addEventListener('resize', adjustFontSize);

